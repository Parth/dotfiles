# Copyright 2013 Google Inc. All Rights Reserved.

"""A git credential helper that provides Google git repository passwords.

Reads a session from stdin that looks a lot like:
  protocol=https
  host=code.google.com
And writes out a session to stdout that looks a lot like:
  username=me
  password=secret

Errors will be reported on stderr.

Note that spaces may be part of key names so, for example, "protocol" must not
be proceeded by leading spaces.
"""
import os
import re
import subprocess
import sys
import textwrap

from oauth2client import client

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exc
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.credentials import store as c_store
from googlecloudsdk.core.util import platforms


_KEYVAL_RE = re.compile(r'(.+)=(.+)')
_BLANK_LINE_RE = re.compile(r'^ *$')


@base.Hidden
class GitHelper(base.Command):
  """A git credential helper to provide access to Google git repositories."""

  GET = 'get'
  STORE = 'store'
  METHODS = [GET, STORE]

  @staticmethod
  def Args(parser):
    parser.add_argument('method',
                        help='The git credential helper method.')
    parser.add_argument('--ignore-unknown',
                        action='store_true',
                        help=('Produce no output and exit with 0 when given '
                              'an unknown method (e.g. store) or host.'))

  @c_exc.RaiseToolExceptionInsteadOf(c_store.Error, client.Error)
  def Run(self, args):
    """Run the helper command."""

    if args.method not in GitHelper.METHODS:
      if args.ignore_unknown:
        return
      raise c_exc.ToolException(
          'Unexpected method [{meth}]. One of [{methods}] expected.'
          .format(meth=args.method, methods=', '.join(GitHelper.METHODS)))

    info = self._ParseInput()
    credentialed_domains = ['code.google.com', 'source.developers.google.com']
    extra = properties.VALUES.core.credentialed_hosted_repo_domains.Get()
    if extra:
      credentialed_domains.extend(extra.split(','))
    if info.get('host') not in credentialed_domains:
      if args.ignore_unknown:
        return
      raise c_exc.ToolException('Unknown host [{host}].'
                                .format(host=info.get('host')))

    if args.method == GitHelper.GET:
      account = properties.VALUES.core.account.Get()
      try:
        cred = c_store.Load(account)
        c_store.Refresh(cred)
        c_store.Store(cred, account)
      except c_store.Error as e:
        sys.stderr.write(textwrap.dedent("""\
            ERROR: {error}
            Run 'gcloud auth login' to log in.
            """.format(error=str(e))))
        return

      self._CheckNetrc()

      sys.stdout.write(textwrap.dedent("""\
          username={username}
          password={password}
          """).format(username=account, password=cred.access_token))
    elif args.method == GitHelper.STORE:
      # On OSX, there is an additional credential helper that gets called before
      # ours does.  When we return a token, it gets cached there.  Git continues
      # to get it from there first until it expires.  That command then fails,
      # and the token is deleted, but it does not retry the operation.  The next
      # command gets a new token from us and it starts working again, for an
      # hour.  This erases our credential from the other cache whenever 'store'
      # is called on us.  Because they are called first, the token will already
      # be stored there, and so we can successfully erase it to prevent caching.
      if (platforms.OperatingSystem.Current() ==
          platforms.OperatingSystem.MACOSX):
        log.debug('Clearing OSX credential cache.')
        try:
          input_string = 'protocol={protocol}\nhost={host}\n\n'.format(
              protocol=info.get('protocol'), host=info.get('host'))
          log.debug('Calling erase with input:\n%s', input_string)
          p = subprocess.Popen(['git-credential-osxkeychain', 'erase'],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
          (out, err) = p.communicate(input_string)
          if p.returncode:
            log.debug(
                'Failed to clear OSX keychain:\nstdout: {%s}\nstderr: {%s}',
                out, err)
        # pylint:disable=broad-except, This can fail and should only be done as
        # best effort.
        except Exception as e:
          log.debug('Failed to clear OSX keychain', exc_info=True)

  def _ParseInput(self):
    """Parse the fields from stdin.

    Returns:
      {str: str}, The parsed parameters given on stdin.
    """
    info = {}
    for line in sys.stdin:
      if _BLANK_LINE_RE.match(line):
        continue
      match = _KEYVAL_RE.match(line)
      if not match:
        raise c_exc.ToolException('Invalid input line format: [{format}].'
                                  .format(format=line.rstrip('\n')))
      key, val = match.groups()
      info[key] = val.strip()

    if 'protocol' not in info:
      raise c_exc.ToolException('Required key "protocol" missing.')

    if 'host' not in info:
      raise c_exc.ToolException('Required key "host" missing.')

    if info.get('protocol') != 'https':
      raise c_exc.ToolException('Invalid protocol [{p}].  "https" expected.'
                                .format(p=info.get('protocol')))
    return info

  def _CheckNetrc(self):
    """Warn on stderr if ~/.netrc contains redundant credentials."""

    def Check(p):
      if not os.path.exists(p):
        return
      try:
        with open(p) as f:
          data = f.read()
          if 'source.developers.google.com' in data:
            sys.stderr.write(textwrap.dedent("""\
You have credentials for your Google repository in [{path}]. This repository's
git credential helper is set correctly, so the credentials in [{path}] will not
be used, but you may want to remove them to avoid confusion.
""".format(path=p)))
      # pylint:disable=broad-except, If something went wrong, forget about it.
      except Exception:
        pass
    Check(os.path.expanduser(os.path.join('~', '.netrc')))
    Check(os.path.expanduser(os.path.join('~', '_netrc')))
