# Copyright 2013 Google Inc. All Rights Reserved.

"""The auth command gets tokens via oauth2."""


from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exc
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.credentials import store as c_store
from googlecloudsdk.core.util import console_io


class ActivateRefreshToken(base.Command):
  """Get credentials via an existing refresh token.

  Use an oauth2 refresh token to manufacture credentials for Google APIs. This
  token must have been acquired via some legitimate means to work. The account
  provided is only used locally to help the Cloud SDK keep track of the new
  credentials, so you can activate, list, and revoke the credentials in the
  future.
  """

  @staticmethod
  def Args(parser):
    """Set args for gcloud auth activate-refresh-token."""
    parser.add_argument(
        'account',
        help='The account to associate with the refresh token.')
    parser.add_argument(
        'token', nargs='?',
        help=('OAuth2 refresh token. If blank, prompt for value.'))

  def Run(self, args):
    """Run the authentication command."""

    token = args.token or console_io.PromptResponse('Refresh token: ')
    if not token:
      raise c_exc.InvalidArgumentException('token', 'No value provided.')

    creds = c_store.AcquireFromToken(token)
    account = args.account

    c_store.Refresh(creds)

    c_store.Store(creds, account)

    properties.PersistProperty(properties.VALUES.core.account, account)

    project = args.project
    if project:
      properties.PersistProperty(properties.VALUES.core.project, project)

    return creds

  def Display(self, args, result):
    if result:
      log.Print('Activated refresh token credentials for %s.' % args.account)
