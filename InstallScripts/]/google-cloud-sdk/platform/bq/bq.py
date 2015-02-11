#!/usr/bin/env python
#
# Copyright 2012 Google Inc. All Rights Reserved.

"""Python script for interacting with BigQuery."""



import cmd
import codecs
import datetime
import httplib
import json
import os
import pdb
import pipes
import platform
import shlex
import sys
import time
import traceback
import types


import apiclient
import httplib2
import oauth2client
import oauth2client.client
import oauth2client.file
import oauth2client.gce
import oauth2client.tools
import yaml

from google.apputils import app
from google.apputils import appcommands
import gflags as flags

import table_formatter
import bigquery_client
# pylint: disable=unused-import
import bq_flags
# pylint: enable=unused-import


FLAGS = flags.FLAGS
# These are long names.
# pylint: disable=g-bad-name
JobReference = bigquery_client.ApiClientHelper.JobReference
ProjectReference = bigquery_client.ApiClientHelper.ProjectReference
DatasetReference = bigquery_client.ApiClientHelper.DatasetReference
TableReference = bigquery_client.ApiClientHelper.TableReference
BigqueryClient = bigquery_client.BigqueryClient
JobIdGeneratorIncrementing = bigquery_client.JobIdGeneratorIncrementing
JobIdGeneratorRandom = bigquery_client.JobIdGeneratorRandom
JobIdGeneratorFingerprint = bigquery_client.JobIdGeneratorFingerprint
# pylint: enable=g-bad-name


_VERSION_NUMBER = '2.0.22'
_CLIENT_USER_AGENT = 'Cloud SDK Command Line Tool' + _VERSION_NUMBER
_CLIENT_SCOPE = [
    'https://www.googleapis.com/auth/bigquery',
]
_CLIENT_ID = '32555940559.apps.googleusercontent.com'
_CLIENT_INFO = {
    'client_id': _CLIENT_ID,
    'client_secret': 'ZmssLNjJy2998hD4CTg2ejr2',
    'scope': _CLIENT_SCOPE,
    'user_agent': _CLIENT_USER_AGENT,
    }
_BIGQUERY_TOS_MESSAGE = (
    'In order to get started, please visit the Google APIs Console to '
    'create a project and agree to our Terms of Service:\n'
    '\thttp://code.google.com/apis/console\n\n'
    'For detailed sign-up instructions, please see our Getting Started '
    'Guide:\n'
    '\thttps://developers.google.com/bigquery/docs/getting-started\n\n'
    'Once you have completed the sign-up process, please try your command '
    'again.')
_DELIMITER_MAP = {
    'tab': '\t',
    '\\t': '\t',
    }

# These aren't relevant for user-facing docstrings:
# pylint: disable=g-doc-return-or-yield
# pylint: disable=g-doc-args
# TODO(user): Write some explanation of the structure of this file.

####################
# flags processing
####################


def _ValidateGlobalFlags():
  """Validate combinations of global flag values."""
  if FLAGS.service_account and FLAGS.use_gce_service_account:
    raise app.UsageError(
        'Cannot specify both --service_account and --use_gce_service_account.')


def ValidateAtMostOneSelected(*args):
  """Validates that at most one of the argument flags is selected.

  Returns:
    True if more than 1 flag was selected, False if 1 or 0 were selected.
  """
  count = 0
  for arg in args:
    if arg:
      count += 1
  return count > 1


def _GetBigqueryRcFilename():
  """Return the name of the bigqueryrc file to use.

  In order, we look for a flag the user specified, an environment
  variable, and finally the default value for the flag.

  Returns:
    bigqueryrc filename as a string.
  """
  return ((FLAGS['bigqueryrc'].present and FLAGS.bigqueryrc) or
          os.environ.get('BIGQUERYRC') or
          FLAGS.bigqueryrc)


def _ProcessBigqueryrc():
  """Updates FLAGS with values found in the bigqueryrc file."""
  bigqueryrc = _GetBigqueryRcFilename()
  if not os.path.exists(bigqueryrc):
    return
  with open(bigqueryrc) as rcfile:
    for line in rcfile:
      if line.lstrip().startswith('#') or not line.strip():
        continue
      elif line.lstrip().startswith('['):
        # TODO(user): Support command-specific flag sections.
        continue
      flag, equalsign, value = line.partition('=')
      # if no value given, assume stringified boolean true
      if not equalsign:
        value = 'true'
      flag = flag.strip()
      value = value.strip()
      while flag.startswith('-'):
        flag = flag[1:]
      # We want flags specified at the command line to override
      # those in the flagfile.
      if flag not in FLAGS:
        raise app.UsageError(
            'Unknown flag %s found in bigqueryrc file' % (flag,))
      if not FLAGS[flag].present:
        FLAGS[flag].Parse(value)
      elif FLAGS[flag].Type().startswith('multi'):
        old_value = getattr(FLAGS, flag)
        FLAGS[flag].Parse(value)
        setattr(FLAGS, flag, old_value + getattr(FLAGS, flag))


def _ResolveApiInfoFromFlags():
  """Determine an api and api_version."""
  api_version = FLAGS.api_version
  api = FLAGS.api
  return {'api': api, 'api_version': api_version}




def _UseServiceAccount():
  return bool(FLAGS.use_gce_service_account or FLAGS.service_account)


def _GetServiceAccountCredentialsFromFlags(storage):  # pylint: disable=unused-argument
  client_scope = _CLIENT_SCOPE

  if FLAGS.use_gce_service_account:
    return oauth2client.gce.AppAssertionCredentials(client_scope)

  if not oauth2client.client.HAS_OPENSSL:
    raise app.UsageError(
        'BigQuery requires OpenSSL to be installed in order to use '
        'service account credentials. Please install OpenSSL '
        'and the Python OpenSSL package.')

  if FLAGS.service_account_private_key_file:
    try:
      with file(FLAGS.service_account_private_key_file, 'rb') as f:
        key = f.read()
    except IOError as e:
      raise app.UsageError(
          'Service account specified, but private key in file "%s" '
          'cannot be read:\n%s' % (FLAGS.service_account_private_key_file, e))
  else:
    raise app.UsageError(
        'Service account authorization requires the '
        'service_account_private_key_file flag to be set.')

  return oauth2client.client.SignedJwtAssertionCredentials(
      FLAGS.service_account, key, client_scope,
      private_key_password=FLAGS.service_account_private_key_password,
      user_agent=_CLIENT_USER_AGENT)


def _GetCredentialsFromOAuthFlow(storage):
  print
  print '******************************************************************'
  print '** No OAuth2 credentials found, beginning authorization process **'
  print '******************************************************************'
  print
  if FLAGS.headless:
    print 'Running in headless mode, exiting.'
    sys.exit(1)
  client_info = _CLIENT_INFO.copy()
  while True:
    # If authorization fails, we want to retry, rather than let this
    # cascade up and get caught elsewhere. If users want out of the
    # retry loop, they can ^C.
    try:
      flow = oauth2client.client.OAuth2WebServerFlow(**client_info)
      credentials = oauth2client.tools.run(flow, storage)
      break
    except (oauth2client.client.FlowExchangeError, SystemExit) as e:
      # Here SystemExit is "no credential at all", and the
      # FlowExchangeError is "invalid" -- usually because you reused
      # a token.
      print 'Invalid authorization: %s' % (e,)
      print
    except httplib2.HttpLib2Error as e:
      print 'Error communicating with server. Please check your internet '
      print 'connection and try again.'
      print
      print 'Error is: %s' % (e,)
      sys.exit(1)
  print
  print '************************************************'
  print '** Continuing execution of BigQuery operation **'
  print '************************************************'
  print
  return credentials


def _GetCredentialsFromFlags():
  # In the case of a GCE service account, we can skip the entire
  # process of loading from storage.
  if FLAGS.use_gce_service_account:
    return _GetServiceAccountCredentialsFromFlags(None)


  if FLAGS.service_account:
    credentials_getter = _GetServiceAccountCredentialsFromFlags
    credential_file = FLAGS.service_account_credential_file
    if not credential_file:
      raise app.UsageError(
          'The flag --service_account_credential_file must be specified '
          'if --service_account is used.')
  else:
    credentials_getter = _GetCredentialsFromOAuthFlow
    credential_file = FLAGS.credential_file

  try:
    # Note that oauth2client.file ensures the file is created with
    # the correct permissions.
    storage = oauth2client.file.Storage(credential_file)
  except OSError as e:
    raise bigquery_client.BigqueryError(
        'Cannot create credential file %s: %s' % (FLAGS.credential_file, e))
  try:
    credentials = storage.get()
  except BaseException as e:
    BigqueryCmd.ProcessError(
        e, name='GetCredentialsFromFlags',
        message_prefix=(
            'Credentials appear corrupt. Please delete the credential file '
            'and try your command again. You can delete your credential '
            'file using "bq init --delete_credentials".\n\nIf that does '
            'not work, you may have encountered a bug in the BigQuery CLI.'))
    sys.exit(1)

  if credentials is None or credentials.invalid:
    credentials = credentials_getter(storage)
    credentials.set_store(storage)
  return credentials


def _GetFormatterFromFlags(secondary_format='sparse'):
  if FLAGS['format'].present:
    return table_formatter.GetFormatter(FLAGS.format)
  else:
    return table_formatter.GetFormatter(secondary_format)


def _ExpandForPrinting(fields, rows, formatter):
  """Expand entries that require special bq-specific formatting."""
  return [_ExpandRowForPrinting(fields, row, formatter) for row in rows]


def _ExpandRowForPrinting(fields, row, formatter):
  """Expand entries in a single row with bq-specific formatting."""
  def NormalizeTimestamp(entry, field):  # pylint: disable=unused-argument
    try:
      date = datetime.datetime.utcfromtimestamp(float(entry))
      return date.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
      return '<date out of range for display>'

  def NormalizeRecord(entry, field):
    if isinstance(formatter, table_formatter.JsonFormatter):
      subfields = field.get('fields', [])
      subresults = _ExpandRowForPrinting(subfields, entry, formatter)
      subfield_names = [subfield.get('name', '') for subfield in subfields]
      result = {}
      for subfield_name, subfield_data in zip(subfield_names, subresults):
        result[subfield_name] = subfield_data
      return result
    else:
      return entry

  def NormalizeRepeatedRecord(entry, field):
    if isinstance(formatter, table_formatter.JsonFormatter):
      return [NormalizeRecord(record, field) for record in entry]
    else:
      return entry

  column_normalizers = {}
  for i, field in enumerate(fields):
    if field['type'].upper() == 'TIMESTAMP':
      column_normalizers[i] = NormalizeTimestamp
    elif field['type'].upper() == 'RECORD':
      if field['mode'].upper() == 'REPEATED':
        column_normalizers[i] = NormalizeRepeatedRecord
      else:
        column_normalizers[i] = NormalizeRecord

  def NormalizeNone():
    if isinstance(formatter, table_formatter.JsonFormatter):
      return None
    elif isinstance(formatter, table_formatter.CsvFormatter):
      return ''
    else:
      return 'NULL'

  def NormalizeEntry(i, entry):
    if entry is None:
      return NormalizeNone()
    elif i in column_normalizers:
      return column_normalizers[i](entry, fields[i])
    return entry

  return [NormalizeEntry(i, e) for i, e in enumerate(row)]


def _PrintDryRunInfo(job):
  num_bytes = job['statistics']['query']['totalBytesProcessed']
  if FLAGS.format in ['prettyjson', 'json']:
    _PrintFormattedJsonObject(job)
  elif FLAGS.format == 'csv':
    print num_bytes
  else:
    print (
        'Query successfully validated. Assuming the tables are not modified, '
        'running this query will process %s bytes of data.' % (num_bytes,))


def _PrintFormattedJsonObject(obj):
  if FLAGS.format == 'prettyjson':
    print json.dumps(obj, sort_keys=True, indent=2)
  else:
    print json.dumps(obj, separators=(',', ':'))


def _GetJobIdFromFlags():
  """Returns the job id or job generator from the flags."""
  if FLAGS.fingerprint_job_id and FLAGS.job_id:
    raise app.UsageError(
        'The fingerprint_job_id flag cannot be specified with the job_id '
        'flag.')
  if FLAGS.fingerprint_job_id:
    return JobIdGeneratorFingerprint()
  elif FLAGS.job_id is None:
    return JobIdGeneratorIncrementing(JobIdGeneratorRandom())
  elif FLAGS.job_id:
    return FLAGS.job_id
  else:
    # User specified a job id, but it was empty. Let the
    # server come up with a job id.
    return None


def _GetWaitPrinterFactoryFromFlags():
  """Returns the default wait_printer_factory to use while waiting for jobs."""
  if FLAGS.quiet:
    return BigqueryClient.QuietWaitPrinter
  if FLAGS.headless:
    return BigqueryClient.TransitionWaitPrinter
  return BigqueryClient.VerboseWaitPrinter


def _PromptWithDefault(message):
  """Prompts user with message, return key pressed or '' on enter."""
  if FLAGS.headless:
    print 'Running --headless, accepting default for prompt: %s' % (message,)
    return ''
  return raw_input(message).lower()


def _PromptYN(message):
  """Prompts user with message, returning the key 'y', 'n', or '' on enter."""
  response = None
  while response not in ['y', 'n', '']:
    response = _PromptWithDefault(message)
  return response


def _NormalizeFieldDelimiter(field_delimiter):
  """Validates and returns the correct field_delimiter."""
  # The only non-string delimiter we allow is None, which represents
  # no field delimiter specified by the user.
  if field_delimiter is None:
    return field_delimiter
  try:
    # We check the field delimiter flag specifically, since a
    # mis-entered Thorn character generates a difficult to
    # understand error during request serialization time.
    _ = field_delimiter.decode(sys.stdin.encoding or 'utf8')
  except UnicodeDecodeError:
    raise app.UsageError(
        'The field delimiter flag is not valid. Flags must be '
        'specified in your default locale. For example, '
        'the Latin 1 representation of Thorn is byte code FE, '
        'which in the UTF-8 locale would be expressed as C3 BE.')

  # Allow TAB and \\t substitution.
  key = field_delimiter.lower()
  return _DELIMITER_MAP.get(key, field_delimiter)




class TablePrinter(object):
  """Base class for printing a table, with a default implementation."""

  def __init__(self, **kwds):
    super(TablePrinter, self).__init__()
    # Most extended classes will require state.
    for key, value in kwds.iteritems():
      setattr(self, key, value)

  def PrintTable(self, fields, rows):
    formatter = _GetFormatterFromFlags(secondary_format='pretty')
    formatter.AddFields(fields)
    rows = _ExpandForPrinting(fields, rows, formatter)
    formatter.AddRows(rows)
    formatter.Print()


class Factory(object):
  """Class encapsulating factory creation of BigqueryClient."""
  _BIGQUERY_CLIENT_FACTORY = None

  class ClientTablePrinter(object):
    _TABLE_PRINTER = None

    @classmethod
    def GetTablePrinter(cls):
      if cls._TABLE_PRINTER is None:
        cls._TABLE_PRINTER = TablePrinter()
      return cls._TABLE_PRINTER

    @classmethod
    def SetTablePrinter(cls, printer):
      if not isinstance(printer, TablePrinter):
        raise TypeError('Printer must be an instance of TablePrinter.')
      cls._TABLE_PRINTER = printer

  @classmethod
  def GetBigqueryClientFactory(cls):
    if cls._BIGQUERY_CLIENT_FACTORY is None:
      cls._BIGQUERY_CLIENT_FACTORY = bigquery_client.BigqueryClient
    return cls._BIGQUERY_CLIENT_FACTORY

  @classmethod
  def SetBigqueryClientFactory(cls, factory):
    if not issubclass(factory, bigquery_client.BigqueryClient):
      raise TypeError('Factory must be subclass of BigqueryClient.')
    cls._BIGQUERY_CLIENT_FACTORY = factory


class Client(object):
  """Class wrapping a singleton bigquery_client.BigqueryClient."""
  client = None

  @staticmethod
  def Create(**kwds):
    """Build a new BigqueryClient configured from kwds and FLAGS."""

    def KwdsOrFlags(name):
      return kwds[name] if name in kwds else getattr(FLAGS, name)

    # Note that we need to handle possible initialization tasks
    # for the case of being loaded as a library.
    _ProcessBigqueryrc()
    bigquery_client.ConfigurePythonLogger(FLAGS.apilog)
    credentials = _GetCredentialsFromFlags()
    assert credentials is not None
    client_args = {}
    global_args = ('credential_file', 'job_property',
                   'project_id', 'dataset_id', 'trace', 'sync',
                   'api', 'api_version')
    for name in global_args:
      client_args[name] = KwdsOrFlags(name)
    client_args['wait_printer_factory'] = _GetWaitPrinterFactoryFromFlags()
    if FLAGS.discovery_file:
      with open(FLAGS.discovery_file) as f:
        client_args['discovery_document'] = f.read()
    bigquery_client_factory = Factory.GetBigqueryClientFactory()
    return bigquery_client_factory(credentials=credentials, **client_args)

  @classmethod
  def Get(cls):
    """Return a BigqueryClient initialized from flags."""
    if cls.client is None:
      try:
        cls.client = Client.Create()
      except ValueError as e:
        # Convert constructor parameter errors into flag usage errors.
        raise app.UsageError(e)
    return cls.client

  @classmethod
  def Delete(cls):
    """Delete the existing client.

    This is needed when flags have changed, and we need to force
    client recreation to reflect new flag values.
    """
    cls.client = None


def _Typecheck(obj, types, message=None):  # pylint: disable=redefined-outer-name
  """Raises a user error if obj is not an instance of types."""
  if not isinstance(obj, types):
    message = message or 'Type of %s is not one of %s' % (obj, types)
    raise app.UsageError(message)


# TODO(user): This code uses more than the average amount of
# Python magic. Explain what the heck is going on throughout.
class NewCmd(appcommands.Cmd):
  """Featureful extension of appcommands.Cmd."""

  def __init__(self, name, flag_values):
    super(NewCmd, self).__init__(name, flag_values)
    run_with_args = getattr(self, 'RunWithArgs', None)
    self._new_style = isinstance(run_with_args, types.MethodType)
    if self._new_style:
      func = run_with_args.im_func
      code = func.func_code  # pylint: disable=redefined-outer-name
      self._full_arg_list = list(code.co_varnames[:code.co_argcount])
      # TODO(user): There might be some corner case where this
      # is *not* the right way to determine bound vs. unbound method.
      if isinstance(run_with_args.im_self, run_with_args.im_class):
        self._full_arg_list.pop(0)
      self._max_args = len(self._full_arg_list)
      self._min_args = self._max_args - len(func.func_defaults or [])
      self._star_args = bool(code.co_flags & 0x04)
      self._star_kwds = bool(code.co_flags & 0x08)
      if self._star_args:
        self._max_args = sys.maxint
      self._debug_mode = FLAGS.debug_mode
      self.surface_in_shell = True
      self.__doc__ = self.RunWithArgs.__doc__
    elif self.Run.im_func is NewCmd.Run.im_func:
      raise appcommands.AppCommandsError(
          'Subclasses of NewCmd must override Run or RunWithArgs')

  def __getattr__(self, name):
    if name in self._command_flags:
      return self._command_flags[name].value
    return super(NewCmd, self).__getattribute__(name)

  def _GetFlag(self, flagname):
    if flagname in self._command_flags:
      return self._command_flags[flagname]
    else:
      return None

  def Run(self, argv):
    """Run this command.

    If self is a new-style command, we set up arguments and call
    self.RunWithArgs, gracefully handling exceptions. If not, we
    simply call self.Run(argv).

    Args:
      argv: List of arguments as strings.

    Returns:
      0 on success, nonzero on failure.
    """
    if not self._new_style:
      return super(NewCmd, self).Run(argv)

    original_values = self._command_flags.FlagValuesDict()
    try:
      args = self._command_flags(argv)[1:]
      for flag, value in self._command_flags.FlagValuesDict().iteritems():
        setattr(self, flag, value)
        if value == original_values[flag]:
          original_values.pop(flag)
      new_args = []
      for argname in self._full_arg_list[:self._min_args]:
        flag = self._GetFlag(argname)
        if flag is not None and flag.present:
          new_args.append(flag.value)
        elif args:
          new_args.append(args.pop(0))
        else:
          print 'Not enough positional args, still looking for %s' % (argname,)
          if self.usage:
            print 'Usage: %s' % (self.usage,)
          return 1

      new_kwds = {}
      for argname in self._full_arg_list[self._min_args:]:
        flag = self._GetFlag(argname)
        if flag is not None and flag.present:
          new_kwds[argname] = flag.value
        elif args:
          new_kwds[argname] = args.pop(0)

      if args and not self._star_args:
        print 'Too many positional args, still have %s' % (args,)
        return 1
      new_args.extend(args)

      if self._debug_mode:
        return self.RunDebug(new_args, new_kwds)
      else:
        return self.RunSafely(new_args, new_kwds)
    finally:
      for flag, value in original_values.iteritems():
        setattr(self, flag, value)
        self._command_flags[flag].Parse(value)

  def RunCmdLoop(self, argv):
    """Hook for use in cmd.Cmd-based command shells."""
    try:
      args = shlex.split(argv)
    except ValueError as e:
      raise SyntaxError(BigqueryCmd.EncodeForPrinting(e))
    return self.Run([self._command_name] + args)

  def _HandleError(self, e):
    message = str(e)
    if isinstance(e, bigquery_client.BigqueryClientConfigurationError):
      message += ' Try running "bq init".'
    print 'Exception raised in %s operation: %s' % (self._command_name, message)
    return 1

  def RunDebug(self, args, kwds):
    """Run this command in debug mode."""
    try:
      return_value = self.RunWithArgs(*args, **kwds)
    except BaseException as e:
      # Don't break into the debugger for expected exceptions.
      if isinstance(e, app.UsageError) or (
          isinstance(e, bigquery_client.BigqueryError) and
          not isinstance(e, bigquery_client.BigqueryInterfaceError)):
        return self._HandleError(e)
      print
      print '****************************************************'
      print '**  Unexpected Exception raised in bq execution!  **'
      if FLAGS.headless:
        print '**  --headless mode enabled, exiting.             **'
        print '**  See STDERR for traceback.                     **'
      else:
        print '**  --debug_mode enabled, starting pdb.           **'
      print '****************************************************'
      print
      traceback.print_exc()
      print
      if not FLAGS.headless:
        pdb.post_mortem()
      return 1
    return return_value

  def RunSafely(self, args, kwds):
    """Run this command, turning exceptions into print statements."""
    try:
      return_value = self.RunWithArgs(*args, **kwds)
    except BaseException as e:
      return self._HandleError(e)
    return return_value


class BigqueryCmd(NewCmd):
  """Bigquery-specific NewCmd wrapper."""

  def _NeedsInit(self):
    """Returns true if this command requires the init command before running.

    Subclasses will override for any exceptional cases.
    """
    return not _UseServiceAccount() and not (
        os.path.exists(_GetBigqueryRcFilename()) or os.path.exists(
            FLAGS.credential_file))

  def Run(self, argv):
    """Bigquery commands run `init` before themselves if needed."""
    if self._NeedsInit():
      appcommands.GetCommandByName('init').Run([])
    return super(BigqueryCmd, self).Run(argv)

  def RunSafely(self, args, kwds):
    """Run this command, printing information about any exceptions raised."""
    try:
      return_value = self.RunWithArgs(*args, **kwds)
    except BaseException as e:
      return BigqueryCmd.ProcessError(e, name=self._command_name)
    return return_value

  @staticmethod
  def EncodeForPrinting(s):
    """Safely encode a string as the encoding for sys.stdout."""
    encoding = sys.stdout.encoding or 'ascii'
    return unicode(s).encode(encoding, 'backslashreplace')

  @staticmethod
  def ProcessError(
      e, name='unknown',
      message_prefix='You have encountered a bug in the BigQuery CLI.'):
    """Translate an error message into some printing and a return code."""
    response = []
    retcode = 1

    contact_us_msg = (
        'Please file a bug report in our public issue tracker:\n'
        '  https://code.google.com/p/google-bigquery/issues/list\n'
        'Please include a brief description of the steps that led to this '
        'issue, as well as the following information: \n\n')
    error_details = (
        '========================================\n'
        '== Platform ==\n'
        '  %s\n'
        '== bq version ==\n'
        '  %s\n'
        '== Command line ==\n'
        '  %s\n'
        '== UTC timestamp ==\n'
        '  %s\n'
        '== Error trace ==\n'
        '%s'
        '========================================\n') % (
            ':'.join([
                platform.python_implementation(),
                platform.python_version(),
                platform.platform()]),
            _VERSION_NUMBER,
            sys.argv,
            time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            ''.join(traceback.format_tb(sys.exc_info()[2]))
            )

    codecs.register_error('strict', codecs.replace_errors)
    message = BigqueryCmd.EncodeForPrinting(e)
    if isinstance(e, (bigquery_client.BigqueryNotFoundError,
                      bigquery_client.BigqueryDuplicateError)):
      response.append('BigQuery error in %s operation: %s' % (name, message))
      retcode = 2
    elif isinstance(e, bigquery_client.BigqueryTermsOfServiceError):
      response.append(str(e) + '\n')
      response.append(_BIGQUERY_TOS_MESSAGE)
    elif isinstance(e, bigquery_client.BigqueryInvalidQueryError):
      response.append('Error in query string: %s' % (message,))
    elif (isinstance(e, bigquery_client.BigqueryError)
          and not isinstance(e, bigquery_client.BigqueryInterfaceError)):
      response.append('BigQuery error in %s operation: %s' % (name, message))
    elif isinstance(e, (app.UsageError, TypeError)):
      response.append(message)
    elif (isinstance(e, SyntaxError) or
          isinstance(e, bigquery_client.BigquerySchemaError)):
      response.append('Invalid input: %s' % (message,))
    elif isinstance(e, flags.FlagsError):
      response.append('Error parsing command: %s' % (message,))
    elif isinstance(e, KeyboardInterrupt):
      response.append('')
    else:  # pylint: disable=broad-except
      # Errors with traceback information are printed here.
      # The traceback module has nicely formatted the error trace
      # for us, so we don't want to undo that via TextWrap.
      if isinstance(e, bigquery_client.BigqueryInterfaceError):
        message_prefix = (
            'Bigquery service returned an invalid reply in %s operation: %s.'
            '\n\n'
            'Please make sure you are using the latest version '
            'of the bq tool and try again. '
            'If this problem persists, you may have encountered a bug in the '
            'bigquery client.' % (name, message))
      elif isinstance(e, oauth2client.client.Error):
        message_prefix = (
            'Authorization error. This may be a network connection problem, '
            'so please try again. If this problem persists, the credentials '
            'may be corrupt. Try deleting and re-creating your credentials. '
            'You can delete your credentials using '
            '"bq init --delete_credentials".'
            '\n\n'
            'If this problem still occurs, you may have encountered a bug '
            'in the bigquery client.')
      elif (isinstance(e, httplib.HTTPException)
            or isinstance(e, apiclient.errors.Error)
            or isinstance(e, httplib2.HttpLib2Error)):
        message_prefix = (
            'Network connection problem encountered, please try again.'
            '\n\n'
            'If this problem persists, you may have encountered a bug in the '
            'bigquery client.')

      print flags.TextWrap(message_prefix + ' ' + contact_us_msg)
      print error_details
      response.append('Unexpected exception in %s operation: %s' % (
          name, message))

    print flags.TextWrap('\n'.join(response))
    return retcode

  def PrintJobStartInfo(self, job):
    """Print a simple status line."""
    reference = BigqueryClient.ConstructObjectReference(job)
    print 'Successfully started %s %s' % (self._command_name, reference)


class _Load(BigqueryCmd):
  usage = """load <destination_table> <source> <schema>"""

  def __init__(self, name, fv):
    super(_Load, self).__init__(name, fv)
    flags.DEFINE_string(
        'field_delimiter', None,
        'The character that indicates the boundary between columns in the '
        'input file. "\\t" and "tab" are accepted names for tab.',
        short_name='F', flag_values=fv)
    flags.DEFINE_enum(
        'encoding', None,
        ['UTF-8', 'ISO-8859-1'],
        'The character encoding used by the input file.  Options include:'
        '\n ISO-8859-1 (also known as Latin-1)'
        '\n UTF-8',
        short_name='E', flag_values=fv)
    flags.DEFINE_integer(
        'skip_leading_rows', None,
        'The number of rows at the beginning of the source file to skip.',
        flag_values=fv)
    flags.DEFINE_string(
        'schema', None,
        'Either a filename or a comma-separated list of fields in the form '
        'name[:type].',
        flag_values=fv)
    flags.DEFINE_boolean(
        'replace', False,
        'If true erase existing contents before loading new data.',
        flag_values=fv)
    flags.DEFINE_string(
        'quote', None,
        'Quote character to use to enclose records. Default is ". '
        'To indicate no quote character at all, use an empty string.',
        flag_values=fv)
    flags.DEFINE_integer(
        'max_bad_records', 0,
        'Maximum number of bad records allowed before the entire job fails.',
        flag_values=fv)
    flags.DEFINE_boolean(
        'allow_quoted_newlines', None,
        'Whether to allow quoted newlines in CSV import data.',
        flag_values=fv)
    flags.DEFINE_boolean(
        'allow_jagged_rows', None,
        'Whether to allow missing trailing optional columns '
        'in CSV import data.',
        flag_values=fv)
    flags.DEFINE_boolean(
        'ignore_unknown_values', None,
        'Whether to allow and ignore extra, unrecognized values in CSV or JSON '
        'import data.',
        flag_values=fv)
    flags.DEFINE_enum(
        'source_format', None,
        ['CSV',
         'NEWLINE_DELIMITED_JSON',
         'DATASTORE_BACKUP'],
        'Format of source data. Options include:'
        '\n CSV'
        '\n NEWLINE_DELIMITED_JSON'
        '\n DATASTORE_BACKUP',
        flag_values=fv)

  def RunWithArgs(self, destination_table, source, schema=None):
    """Perform a load operation of source into destination_table.

    Usage:
      load <destination_table> <source> [<schema>]

    The <destination_table> is the fully-qualified table name of table to
    create, or append to if the table already exists.

    The <source> argument can be a path to a single local file, or a
    comma-separated list of URIs.

    The <schema> argument should be either the name of a JSON file or a text
    schema. This schema should be omitted if the table already has one.

    In the case that the schema is provided in text form, it should be a
    comma-separated list of entries of the form name[:type], where type will
    default to string if not specified.

    In the case that <schema> is a filename, it should contain a
    single array object, each entry of which should be an object with
    properties 'name', 'type', and (optionally) 'mode'. See the online
    documentation for more detail:
      https://developers.google.com/bigquery/preparing-data-for-bigquery

    Note: the case of a single-entry schema with no type specified is
    ambiguous; one can use name:string to force interpretation as a
    text schema.

    Examples:
      bq load ds.new_tbl ./info.csv ./info_schema.json
      bq load ds.new_tbl gs://mybucket/info.csv ./info_schema.json
      bq load ds.small gs://mybucket/small.csv name:integer,value:string
      bq load ds.small gs://mybucket/small.csv field1,field2,field3

    Arguments:
      destination_table: Destination table name.
      source: Name of local file to import, or a comma-separated list of
        URI paths to data to import.
      schema: Either a text schema or JSON file, as above.
    """
    client = Client.Get()
    table_reference = client.GetTableReference(destination_table)
    opts = {
        'encoding': self.encoding,
        'skip_leading_rows': self.skip_leading_rows,
        'max_bad_records': self.max_bad_records,
        'allow_quoted_newlines': self.allow_quoted_newlines,
        'job_id': _GetJobIdFromFlags(),
        'source_format': self.source_format,
        }
    if self.replace:
      opts['write_disposition'] = 'WRITE_TRUNCATE'
    if self.field_delimiter:
      opts['field_delimiter'] = _NormalizeFieldDelimiter(self.field_delimiter)
    if self.quote is not None:
      opts['quote'] = _NormalizeFieldDelimiter(self.quote)
    if self.allow_jagged_rows is not None:
      opts['allow_jagged_rows'] = self.allow_jagged_rows
    if self.ignore_unknown_values is not None:
      opts['ignore_unknown_values'] = self.ignore_unknown_values
    job = client.Load(table_reference, source, schema=schema, **opts)
    if not FLAGS.sync:
      self.PrintJobStartInfo(job)


class _Query(BigqueryCmd):
  usage = """query <sql>"""

  def __init__(self, name, fv):
    super(_Query, self).__init__(name, fv)
    flags.DEFINE_string(
        'destination_table', '',
        'Name of destination table for query results.',
        flag_values=fv)
    flags.DEFINE_integer(
        'start_row', 0,
        'First row to return in the result.',
        short_name='s', flag_values=fv)
    flags.DEFINE_integer(
        'max_rows', 100,
        'How many rows to return in the result.',
        short_name='n', flag_values=fv)
    flags.DEFINE_boolean(
        'batch', False,
        'Whether to run the query in batch mode.',
        flag_values=fv)
    flags.DEFINE_boolean(
        'append_table', False,
        'When a destination table is specified, whether or not to append.',
        flag_values=fv)
    flags.DEFINE_boolean(
        'rpc', False,
        'If true, use rpc-style query API instead of jobs.insert().',
        flag_values=fv)
    flags.DEFINE_boolean(
        'replace', False,
        'If true, erase existing contents before loading new data.',
        flag_values=fv)
    flags.DEFINE_boolean(
        'allow_large_results', None,
        'Enables larger destination table sizes.',
        flag_values=fv)
    flags.DEFINE_boolean(
        'dry_run', None,
        'Whether the query should be validated without executing.',
        flag_values=fv)
    flags.DEFINE_boolean(
        'require_cache', None,
        'Whether to only run the query if it is already cached.',
        flag_values=fv)
    flags.DEFINE_boolean(
        'use_cache', None,
        'Whether to use the query cache to avoid rerunning cached queries.',
        flag_values=fv)
    flags.DEFINE_float(
        'min_completion_ratio', None,
        '[Experimental] The minimum fraction of data that must be scanned '
        'before a query returns. If not set, the default server value (1.0) '
        'will be used.',
        lower_bound=0, upper_bound=1.0,
        flag_values=fv)
    flags.DEFINE_boolean(
        'flatten_results', None,
        'Whether to flatten nested and repeated fields in the result schema. '
        'If not set, the default behavior is to flatten.',
        flag_values=fv)

  def RunWithArgs(self, *args):
    # pylint: disable=g-doc-exception
    """Execute a query.

    Examples:
      bq query 'select count(*) from publicdata:samples.shakespeare'

    Usage:
      query <sql_query>
    """
    # Set up the params that are the same for rpc-style and jobs.insert()-style
    # queries.
    kwds = {
        'dry_run': self.dry_run,
        'use_cache': self.use_cache,
        'min_completion_ratio': self.min_completion_ratio,
        }
    query = ' '.join(args)
    client = Client.Get()
    if self.rpc:
      if self.allow_large_results:
        raise app.UsageError(
            'allow_large_results cannot be specified in rpc mode.')
      if self.destination_table:
        raise app.UsageError(
            'destination_table cannot be specified in rpc mode.')
      if FLAGS.job_id or FLAGS.fingerprint_job_id:
        raise app.UsageError(
            'job_id and fingerprint_job_id cannot be specified in rpc mode.')
      if self.batch:
        raise app.UsageError(
            'batch cannot be specified in rpc mode.')
      if self.flatten_results:
        raise app.UsageError(
            'flatten_results cannot be specified in rpc mode.')
      kwds['max_results'] = self.max_rows
      fields, rows = client.RunQueryRpc(query, **kwds)
      Factory.ClientTablePrinter.GetTablePrinter().PrintTable(fields, rows)
    else:
      if self.destination_table and self.append_table:
        kwds['write_disposition'] = 'WRITE_APPEND'
      if self.destination_table and self.replace:
        kwds['write_disposition'] = 'WRITE_TRUNCATE'
      if self.require_cache:
        kwds['create_disposition'] = 'CREATE_NEVER'
      if self.batch:
        kwds['priority'] = 'BATCH'

      kwds['destination_table'] = self.destination_table
      kwds['allow_large_results'] = self.allow_large_results
      kwds['flatten_results'] = self.flatten_results
      kwds['job_id'] = _GetJobIdFromFlags()
      job = client.Query(query, **kwds)
      if self.dry_run:
        _PrintDryRunInfo(job)
      elif not FLAGS.sync:
        self.PrintJobStartInfo(job)
      else:
        fields, rows = client.ReadSchemaAndJobRows(job['jobReference'],
                                                   start_row=self.start_row,
                                                   max_rows=self.max_rows)
        Factory.ClientTablePrinter.GetTablePrinter().PrintTable(fields, rows)


class _Extract(BigqueryCmd):
  usage = """extract <source_table> <destination_uris>"""

  def __init__(self, name, fv):
    super(_Extract, self).__init__(name, fv)
    flags.DEFINE_string(
        'field_delimiter', None,
        'The character that indicates the boundary between columns in the '
        'output file. "\\t" and "tab" are accepted names for tab.',
        short_name='F', flag_values=fv)
    flags.DEFINE_enum(
        'destination_format', None,
        ['CSV', 'NEWLINE_DELIMITED_JSON', 'AVRO'],
        'The format with which to write the extracted data. Tables with '
        'nested or repeated fields cannot be extracted to CSV.',
        flag_values=fv)
    flags.DEFINE_enum(
        'compression', 'NONE',
        ['GZIP', 'NONE'],
        'The compression type to use for exported files. Possible values '
        'include GZIP and NONE. The default value is NONE.',
        flag_values=fv)
    flags.DEFINE_boolean(
        'print_header', None, 'Whether to print header rows for formats that '
        'have headers. Prints headers by default.',
        flag_values=fv)

  def RunWithArgs(self, source_table, destination_uris):
    """Perform an extract operation of source_table into destination_uris.

    Usage:
      extract <source_table> <destination_uris>

    Examples:
      bq extract ds.summary gs://mybucket/summary.csv

    Arguments:
      source_table: Source table to extract.
      destination_uris: One or more Google Storage URIs, separated by commas.
    """
    client = Client.Get()
    kwds = {
        'job_id': _GetJobIdFromFlags(),
        }
    table_reference = client.GetTableReference(source_table)
    job = client.Extract(
        table_reference, destination_uris,
        print_header=self.print_header,
        field_delimiter=_NormalizeFieldDelimiter(self.field_delimiter),
        destination_format=self.destination_format,
        compression=self.compression, **kwds)
    if not FLAGS.sync:
      self.PrintJobStartInfo(job)


class _List(BigqueryCmd):
  usage = """ls [-j|-p|-d][-a] [-n <number>] [<id>]"""  # pylint: disable=g-line-too-long

  def __init__(self, name, fv):
    super(_List, self).__init__(name, fv)
    flags.DEFINE_boolean(
        'all', None,
        'Show all results. For jobs, will show jobs from all users. For '
        'datasets, will list hidden datasets.',
        short_name='a', flag_values=fv)
    flags.DEFINE_boolean(
        'all_jobs', None,
        'DEPRECATED. Use --all instead',
        flag_values=fv)
    flags.DEFINE_boolean(
        'jobs', False,
        'Show jobs described by this identifier.',
        short_name='j', flag_values=fv)
    flags.DEFINE_integer(
        'max_results', None,
        'Maximum number to list.',
        short_name='n', flag_values=fv)
    flags.DEFINE_boolean(
        'projects', False,
        'Show all projects.',
        short_name='p', flag_values=fv)
    flags.DEFINE_boolean(
        'datasets', False,
        'Show datasets described by this identifier.',
        short_name='d', flag_values=fv)

  def RunWithArgs(self, identifier=''):
    """List the objects contained in the named collection.

    List the objects in the named project or dataset. A trailing : or
    . can be used to signify a project or dataset.
     * With -j, show the jobs in the named project.
     * With -p, show all projects.

    Examples:
      bq ls
      bq ls -j proj
      bq ls -p -n 1000
      bq ls mydataset
      bq ls -a
    """

    # pylint: disable=g-doc-exception
    if ValidateAtMostOneSelected(self.j, self.p, self.d):
      raise app.UsageError('Cannot specify more than one of -j, -p, or -d.')
    if self.j and self.p:
      raise app.UsageError(
          'Cannot specify more than one of -j and -p.')
    if self.p and identifier:
      raise app.UsageError('Cannot specify an identifier with -p')

    # Copy deprecated flag specifying 'all' to current one.
    if self.all_jobs is not None:
      self.a = self.all_jobs

    client = Client.Get()
    formatter = _GetFormatterFromFlags()
    if identifier:
      reference = client.GetReference(identifier)
    else:
      try:
        reference = client.GetReference(identifier)
      except bigquery_client.BigqueryError:
        # We want to let through the case of no identifier, which
        # will fall through to the second case below.
        reference = None
    # If we got a TableReference, we might be able to make sense
    # of it as a DatasetReference, as in 'ls foo' with dataset_id
    # set.
    if isinstance(reference, TableReference):
      try:
        reference = client.GetDatasetReference(identifier)
      except bigquery_client.BigqueryError:
        pass
    _Typecheck(reference, (types.NoneType, ProjectReference, DatasetReference),
               ('Invalid identifier "%s" for ls, cannot call list on object '
                'of type %s') % (identifier, type(reference).__name__))

    if self.d and isinstance(reference, DatasetReference):
      reference = reference.GetProjectReference()

    if self.j:
      reference = client.GetProjectReference(identifier)
      _Typecheck(reference, ProjectReference,
                 'Cannot determine job(s) associated with "%s"' % (identifier,))
      project_reference = client.GetProjectReference(identifier)
      BigqueryClient.ConfigureFormatter(formatter, JobReference)
      results = map(  # pylint: disable=g-long-lambda
          client.FormatJobInfo,
          client.ListJobs(reference=project_reference,
                          max_results=self.max_results,
                          all_users=self.a))
    elif self.p or reference is None:
      BigqueryClient.ConfigureFormatter(formatter, ProjectReference)
      results = map(  # pylint: disable=g-long-lambda
          client.FormatProjectInfo,
          client.ListProjects(max_results=self.max_results))
    elif isinstance(reference, ProjectReference):
      BigqueryClient.ConfigureFormatter(formatter, DatasetReference)
      results = map(  # pylint: disable=g-long-lambda
          client.FormatDatasetInfo,
          client.ListDatasets(reference, max_results=self.max_results,
                              list_all=self.a))
    else:  # isinstance(reference, DatasetReference):
      BigqueryClient.ConfigureFormatter(formatter, TableReference)
      results = map(  # pylint: disable=g-long-lambda
          client.FormatTableInfo,
          client.ListTables(reference, max_results=self.max_results))

    for result in results:
      formatter.AddDict(result)
    formatter.Print()


class _Delete(BigqueryCmd):
  usage = """rm [-f] [-r] [(-d|-t)] <identifier>"""

  def __init__(self, name, fv):
    super(_Delete, self).__init__(name, fv)
    flags.DEFINE_boolean(
        'dataset', False,
        'Remove dataset described by this identifier.',
        short_name='d', flag_values=fv)
    flags.DEFINE_boolean(
        'table', False,
        'Remove table described by this identifier.',
        short_name='t', flag_values=fv)
    flags.DEFINE_boolean(
        'force', False,
        "Ignore existing tables and datasets, don't prompt.",
        short_name='f', flag_values=fv)
    flags.DEFINE_boolean(
        'recursive', False,
        'Remove dataset and any tables it may contain.',
        short_name='r', flag_values=fv)

  def RunWithArgs(self, identifier):
    """Delete the dataset or table described by identifier.

    Always requires an identifier, unlike the show and ls commands.
    By default, also requires confirmation before deleting. Supports
    the -d -t flags to signify that the identifier is a dataset
    or table.
     * With -f, don't ask for confirmation before deleting.
     * With -r, remove all tables in the named dataset.

    Examples:
      bq rm ds.table
      bq rm -r -f old_dataset
    """

    client = Client.Get()

    # pylint: disable=g-doc-exception
    if self.d and self.t:
      raise app.UsageError('Cannot specify more than one of -d and -t.')
    if not identifier:
      raise app.UsageError('Must provide an identifier for rm.')

    if self.t:
      reference = client.GetTableReference(identifier)
    elif self.d:
      reference = client.GetDatasetReference(identifier)
    else:
      reference = client.GetReference(identifier)
      _Typecheck(reference, (DatasetReference, TableReference),
                 'Invalid identifier "%s" for rm.' % (identifier,))

    if isinstance(reference, TableReference) and self.r:
      raise app.UsageError(
          'Cannot specify -r with %r' % (reference,))

    if not self.force:
      if ((isinstance(reference, DatasetReference) and
           client.DatasetExists(reference)) or
          (isinstance(reference, TableReference)
           and client.TableExists(reference))):
        if 'y' != _PromptYN('rm: remove %r? (y/N) ' % (reference,)):
          print 'NOT deleting %r, exiting.' % (reference,)
          return 0

    if isinstance(reference, DatasetReference):
      client.DeleteDataset(reference,
                           ignore_not_found=self.force,
                           delete_contents=self.recursive)
    elif isinstance(reference, TableReference):
      client.DeleteTable(reference,
                         ignore_not_found=self.force)


class _Copy(BigqueryCmd):
  usage = """cp [-n] <source_table>[,<source_table>]* <dest_table>"""

  def __init__(self, name, fv):
    super(_Copy, self).__init__(name, fv)
    flags.DEFINE_boolean(
        'no_clobber', False,
        'Do not overwrite an existing table.',
        short_name='n', flag_values=fv)
    flags.DEFINE_boolean(
        'force', False,
        "Ignore existing destination tables, don't prompt.",
        short_name='f', flag_values=fv)
    flags.DEFINE_boolean(
        'append_table', False,
        'Append to an existing table.',
        short_name='a', flag_values=fv)

  def RunWithArgs(self, source_tables, dest_table):
    """Copies one table to another.

    Examples:
      bq cp dataset.old_table dataset2.new_table
    """
    client = Client.Get()
    source_references = [
        client.GetTableReference(src) for src in source_tables.split(',')]
    source_references_str = ', '.join(str(src) for src in source_references)
    dest_reference = client.GetTableReference(dest_table)

    if self.append_table:
      write_disposition = 'WRITE_APPEND'
      ignore_already_exists = True
    elif self.no_clobber:
      write_disposition = 'WRITE_EMPTY'
      ignore_already_exists = True
    else:
      write_disposition = 'WRITE_TRUNCATE'
      ignore_already_exists = False
      if not self.force:
        if client.TableExists(dest_reference):
          if 'y' != _PromptYN('cp: replace %s? (y/N) ' % (dest_reference,)):
            print 'NOT copying %s, exiting.' % (source_references_str,)
            return 0
    kwds = {
        'write_disposition': write_disposition,
        'ignore_already_exists': ignore_already_exists,
        'job_id': _GetJobIdFromFlags(),
        }
    job = client.CopyTable(source_references, dest_reference, **kwds)
    if job is None:
      print "Table '%s' already exists, skipping" % (dest_reference,)
    elif not FLAGS.sync:
      self.PrintJobStartInfo(job)
    else:
      print "Tables '%s' successfully copied to '%s'" % (
          source_references_str, dest_reference)


class _Make(BigqueryCmd):
  usage = """mk [-d] <identifier>  OR  mk [-t] <identifier> [<schema>]"""

  def __init__(self, name, fv):
    super(_Make, self).__init__(name, fv)
    flags.DEFINE_boolean(
        'force', False,
        'Ignore errors reporting that the object already exists.',
        short_name='f', flag_values=fv)
    flags.DEFINE_boolean(
        'dataset', False,
        'Create dataset with this name.',
        short_name='d', flag_values=fv)
    flags.DEFINE_boolean(
        'table', False,
        'Create table with this name.',
        short_name='t', flag_values=fv)
    flags.DEFINE_string(
        'schema', '',
        'Either a filename or a comma-separated list of fields in the form '
        'name[:type].',
        flag_values=fv)
    flags.DEFINE_string(
        'description', None,
        'Description of the dataset or table.',
        flag_values=fv)
    flags.DEFINE_integer(
        'expiration', None,
        'Expiration time, in seconds from now, of a table.',
        flag_values=fv)
    flags.DEFINE_string(
        'view', '',
        'Create view with this SQL query.',
        flag_values=fv)

  def RunWithArgs(self, identifier='', schema=''):
    # pylint: disable=g-doc-exception
    """Create a dataset, table or view with this name.

    See 'bq help load' for more information on specifying the schema.

    Examples:
      bq mk new_dataset
      bq mk new_dataset.new_table
      bq --dataset_id=new_dataset mk table
      bq mk -t new_dataset.newtable name:integer,value:string
      bq mk --view='select 1 as num' new_dataset.newview

    """

    client = Client.Get()

    if self.d and self.t:
      raise app.UsageError('Cannot specify both -d and -t.')
    if ValidateAtMostOneSelected(self.schema, self.view):
      raise app.UsageError('Cannot specify more than one of'
                           ' --schema or --view.')

    if self.t:
      reference = client.GetTableReference(identifier)
    elif self.view:
      reference = client.GetTableReference(identifier)
    elif self.d or not identifier:
      reference = client.GetDatasetReference(identifier)
    else:
      reference = client.GetReference(identifier)
      _Typecheck(reference, (DatasetReference, TableReference),
                 "Invalid identifier '%s' for mk." % (identifier,))
    if isinstance(reference, DatasetReference):
      if self.schema:
        raise app.UsageError('Cannot specify schema with a dataset.')
      if self.expiration:
        raise app.UsageError('Cannot specify an expiration for a dataset.')
      if client.DatasetExists(reference):
        message = "Dataset '%s' already exists." % (reference,)
        if not self.f:
          raise bigquery_client.BigqueryError(message)
        else:
          print message
          return
      client.CreateDataset(reference, ignore_existing=True,
                           description=self.description)
      print "Dataset '%s' successfully created." % (reference,)
    elif isinstance(reference, TableReference):
      object_name = 'Table'
      if self.view:
        object_name = 'View'
      if client.TableExists(reference):
        message = ("%s '%s' could not be created; a table with this name "
                   "already exists.") % (object_name, reference,)
        if not self.f:
          raise bigquery_client.BigqueryError(message)
        else:
          print message
          return
      if schema:
        schema = bigquery_client.BigqueryClient.ReadSchema(schema)
      else:
        schema = None
      expiration = None
      if self.expiration:
        expiration = int(self.expiration + time.time()) * 1000
      query_arg = self.view or None
      client.CreateTable(reference, ignore_existing=True, schema=schema,
                         description=self.description,
                         expiration=expiration,
                         view_query=query_arg)
      print "%s '%s' successfully created." % (object_name, reference,)


class _Update(BigqueryCmd):
  usage = """update [-d] [-t] <identifier> [<schema>]"""

  def __init__(self, name, fv):
    super(_Update, self).__init__(name, fv)
    flags.DEFINE_boolean(
        'dataset', False,
        'Updates a dataset with this name.',
        short_name='d', flag_values=fv)
    flags.DEFINE_boolean(
        'table', False,
        'Updates a table with this name.',
        short_name='t', flag_values=fv)
    flags.DEFINE_string(
        'schema', '',
        'Either a filename or a comma-separated list of fields in the form '
        'name[:type].',
        flag_values=fv)
    flags.DEFINE_string(
        'description', None,
        'Description of the dataset, table or view.',
        flag_values=fv)
    flags.DEFINE_integer(
        'expiration', None,
        'Expiration time, in seconds from now, of a table or view.',
        flag_values=fv)
    flags.DEFINE_string(
        'source', None,
        'Path to file with JSON payload for an update',
        flag_values=fv)
    flags.DEFINE_string(
        'view', '',
        'SQL query of a view.',
        flag_values=fv)

  def RunWithArgs(self, identifier='', schema=''):
    # pylint: disable=g-doc-exception
    """Updates a dataset, table or view with this name.

    See 'bq help load' for more information on specifying the schema.

    Examples:
      bq update --description "Dataset description" existing_dataset
      bq update --description "My table" existing_dataset.existing_table
      bq update -t existing_dataset.existing_table name:integer,value:string
      bq update --view='select 1 as num' existing_dataset.existing_view
    """
    client = Client.Get()

    if self.d and self.t:
      raise app.UsageError('Cannot specify both -d and -t.')
    if ValidateAtMostOneSelected(self.schema, self.view):
      raise app.UsageError('Cannot specify more than one of'
                           ' --schema or --view.')

    if self.t:
      reference = client.GetTableReference(identifier)
    elif self.view:
      reference = client.GetTableReference(identifier)
    elif self.d or not identifier:
      reference = client.GetDatasetReference(identifier)
    else:
      reference = client.GetReference(identifier)
      _Typecheck(reference, (DatasetReference, TableReference),
                 "Invalid identifier '%s' for update." % (identifier,))
    if isinstance(reference, DatasetReference):
      if self.schema:
        raise app.UsageError('Cannot specify schema with a dataset.')
      if self.view:
        raise app.UsageError('Cannot specify view with a dataset.')
      if self.expiration:
        raise app.UsageError('Cannot specify an expiration for a dataset.')
      if self.source and self.description:
        raise app.UsageError('Cannot specify description with a source.')
      _UpdateDataset(client, reference, self.description, self.source)
      print "Dataset '%s' successfully updated." % (reference,)
    elif isinstance(reference, TableReference):
      object_name = 'Table'
      if self.view:
        object_name = 'View'
      if self.source:
        raise app.UsageError('%s update does not support --source.' %
                             object_name)
      if schema:
        schema = bigquery_client.BigqueryClient.ReadSchema(schema)
      else:
        schema = None
      expiration = None
      if self.expiration:
        expiration = int(self.expiration + time.time()) * 1000
      query_arg = self.view or None
      client.UpdateTable(reference, schema=schema,
                         description=self.description,
                         expiration=expiration,
                         view_query=query_arg)
      print "%s '%s' successfully updated." % (object_name, reference,)


def _UpdateDataset(client, reference, description, source):
  """Updates a dataset.

  Reads JSON file if specified and loads updated values, before calling bigquery
  dataset update.

  Args:
    client: the BigQuery client.
    reference: the DatasetReference to update.
    description: an optional dataset description.
    source: an optional filename containing the JSON payload.

  Raises:
    UsageError: when incorrect usage or invalid args are used.
  """
  acl = None
  if source is not None:
    if not os.path.exists(source):
      raise app.UsageError('Source file not found: %s' % (source,))
    if not os.path.isfile(source):
      raise app.UsageError('Source path is not a file: %s' % (source,))
    with open(source) as f:
      try:
        payload = json.load(f)
        if payload.__contains__('description'):
          description = payload['description']
        if payload.__contains__('access'):
          acl = payload['access']
      except ValueError as e:
        raise app.UsageError('Error decoding JSON schema from file %s: %s'
                             % (source, e))
  client.UpdateDataset(reference, description=description, acl=acl)


class _Show(BigqueryCmd):
  usage = """show [<identifier>]"""

  def __init__(self, name, fv):
    super(_Show, self).__init__(name, fv)
    flags.DEFINE_boolean(
        'job', False,
        'If true, interpret this identifier as a job id.',
        short_name='j', flag_values=fv)
    flags.DEFINE_boolean(
        'dataset', False,
        'Show dataset with this name.',
        short_name='d', flag_values=fv)
    flags.DEFINE_boolean(
        'view', False,
        'Show view specific details instead of general table details.',
        flag_values=fv)

  def RunWithArgs(self, identifier=''):
    """Show all information about an object.

    Examples:
      bq show -j <job_id>
      bq show dataset
      bq show dataset.table
      bq show [--view] dataset.view
    """
    # pylint: disable=g-doc-exception
    client = Client.Get()
    custom_format = 'show'
    if self.j:
      reference = client.GetJobReference(identifier)
    elif self.d:
      reference = client.GetDatasetReference(identifier)
    elif self.view:
      reference = client.GetTableReference(identifier)
      custom_format = 'view'
    else:
      reference = client.GetReference(identifier)
    if reference is None:
      raise app.UsageError('Must provide an identifier for show.')

    object_info = client.GetObjectInfo(reference)
    _PrintObjectInfo(object_info, reference, custom_format=custom_format)


def _PrintObjectInfo(object_info, reference, custom_format):
  # The JSON formats are handled separately so that they don't print
  # the record as a list of one record.
  if FLAGS.format in ['prettyjson', 'json']:
    _PrintFormattedJsonObject(object_info)
  elif FLAGS.format in [None, 'sparse', 'pretty']:
    formatter = _GetFormatterFromFlags()
    BigqueryClient.ConfigureFormatter(
        formatter, type(reference), print_format=custom_format)
    object_info = BigqueryClient.FormatInfoByKind(object_info)
    formatter.AddDict(object_info)
    print '%s %s\n' % (reference.typename.capitalize(), reference)
    formatter.Print()
    print
    if (isinstance(reference, JobReference) and
        object_info['State'] == 'FAILURE'):
      error_result = object_info['status']['errorResult']
      error_ls = object_info['status'].get('errors', [])
      error = bigquery_client.BigqueryError.Create(
          error_result, error_result, error_ls)
      print 'Errors encountered during job execution. %s\n' % (error,)
  else:
    formatter = _GetFormatterFromFlags()
    formatter.AddColumns(object_info.keys())
    formatter.AddDict(object_info)
    formatter.Print()


class _Head(BigqueryCmd):
  usage = """head [-n <max rows>] [-j] [-t] <identifier>"""

  def __init__(self, name, fv):
    super(_Head, self).__init__(name, fv)
    flags.DEFINE_boolean(
        'job', False,
        'Reads the results of a query job.',
        short_name='j', flag_values=fv)
    flags.DEFINE_boolean(
        'table', False,
        'Reads rows from a table.',
        short_name='t', flag_values=fv)
    flags.DEFINE_integer(
        'start_row', 0,
        'The number of rows to skip before showing table data.',
        short_name='s', flag_values=fv)
    flags.DEFINE_integer(
        'max_rows', 100,
        'The number of rows to print when showing table data.',
        short_name='n', flag_values=fv)

  def RunWithArgs(self, identifier=''):
    # pylint: disable=g-doc-exception
    """Displays rows in a table.

    Examples:
      bq head dataset.table
      bq head -j job
      bq head -n 10 dataset.table
      bq head -s 5 -n 10 dataset.table
    """
    client = Client.Get()
    if self.j and self.t:
      raise app.UsageError('Cannot specify both -j and -t.')

    if self.j:
      reference = client.GetJobReference(identifier)
    else:
      reference = client.GetTableReference(identifier)

    if isinstance(reference, JobReference):
      fields, rows = client.ReadSchemaAndJobRows(dict(reference),
                                                 start_row=self.s,
                                                 max_rows=self.n)
    elif isinstance(reference, TableReference):
      fields, rows = client.ReadSchemaAndRows(dict(reference),
                                              start_row=self.s,
                                              max_rows=self.n)
    else:
      raise app.UsageError("Invalid identifier '%s' for head." % (identifier,))

    Factory.ClientTablePrinter.GetTablePrinter().PrintTable(fields, rows)


class _Insert(BigqueryCmd):
  usage = """insert <table identifier> [file]"""

  def __init__(self, name, fv):
    super(_Insert, self).__init__(name, fv)

  def RunWithArgs(self, identifier='', filename=None):
    """Inserts rows in a table.

    Inserts the records formatted as newline delimited JSON from file
    into the specified table. If file is not specified, reads from stdin.
    If there were any insert errors it prints the errors to stdout.

    Examples:
      bq insert dataset.table /tmp/mydata.json
      echo '{"a":1, "b":2}' | bq insert dataset.table
    """
    if filename:
      with open(filename, 'r') as json_file:
        return self._DoInsert(identifier, json_file)
    else:
      return self._DoInsert(identifier, sys.stdin)

  def _DoInsert(self, identifier, json_file):
    """Insert the contents of the file into a table."""
    client = Client.Get()
    reference = client.GetReference(identifier)
    _Typecheck(reference, (TableReference,),
               'Must provide a table identifier for insert.')
    reference = dict(reference)
    batch = []
    def Flush():
      result = client.InsertTableRows(reference, batch)
      del batch[:]
      return result, result.get('insertErrors', None)
    result = {}
    errors = None
    lineno = 1
    for line in json_file:
      try:
        batch.append(bigquery_client.JsonToInsertEntry(None, line))
        lineno += 1
      except bigquery_client.BigqueryClientError as e:
        raise app.UsageError('Line %d: %s' % (lineno, str(e)))
      if (FLAGS.max_rows_per_request and
          len(batch) == FLAGS.max_rows_per_request):
        result, errors = Flush()
      if errors: break
    if batch and errors is None:
      result, errors = Flush()

    if FLAGS.format in ['prettyjson', 'json']:
      _PrintFormattedJsonObject(result)
    elif FLAGS.format in [None, 'sparse', 'pretty']:
      if errors:
        for entry in result['insertErrors']:
          entry_errors = entry['errors']
          sys.stdout.write('record %d errors: ' % (entry['index'],))
          for error in entry_errors:
            print '\t%s: %s' % (error['reason'], error['message'])
    return 1 if errors else 0


class _Wait(BigqueryCmd):
  usage = """wait [<job_id>] [<secs>]"""

  def __init__(self, name, fv):
    super(_Wait, self).__init__(name, fv)
    flags.DEFINE_boolean(
        'fail_on_error', True,
        'When done waiting for the job, exit the process with an error '
        'if the job is still running, or ended with a failure.',
        flag_values=fv)

  def RunWithArgs(self, job_id='', secs=sys.maxint):
    # pylint: disable=g-doc-exception
    """Wait some number of seconds for a job to finish.

    Poll job_id until either (1) the job is DONE or (2) the
    specified number of seconds have elapsed. Waits forever
    if unspecified. If no job_id is specified, and there is
    only one running job, we poll that job.

    Examples:
      bq wait # Waits forever for the currently running job.
      bq wait job_id  # Waits forever
      bq wait job_id 100  # Waits 100 seconds
      bq wait job_id 0  # Polls if a job is done, then returns immediately.
      # These may exit with a non-zero status code to indicate "failure":
      bq wait --fail_on_error job_id  # Succeeds if job succeeds.
      bq wait --fail_on_error job_id 100  # Succeeds if job succeeds in 100 sec.

    Arguments:
      job_id: Job ID to wait on.
      secs: Number of seconds to wait (must be >= 0).
    """
    try:
      secs = BigqueryClient.NormalizeWait(secs)
    except ValueError:
      raise app.UsageError('Invalid wait time: %s' % (secs,))

    client = Client.Get()
    if not job_id:
      running_jobs = client.ListJobRefs(state_filter=['PENDING', 'RUNNING'])
      if len(running_jobs) != 1:
        raise bigquery_client.BigqueryError(
            'No job_id provided, found %d running jobs' % (len(running_jobs),))
      job_reference = running_jobs.pop()
    else:
      job_reference = client.GetJobReference(job_id)

    try:
      job = client.WaitJob(job_reference=job_reference, wait=secs)
      _PrintObjectInfo(job, JobReference.Create(**job['jobReference']),
                       custom_format='show')
      return 1 if self.fail_on_error and BigqueryClient.IsFailedJob(job) else 0
    except StopIteration as e:
      print '\n'
      print e
    # If we reach this point, we have not seen the job succeed.
    return 1 if self.fail_on_error else 0


# pylint: disable=g-bad-name
class CommandLoop(cmd.Cmd):
  """Instance of cmd.Cmd built to work with NewCmd."""

  class TerminateSignal(Exception):
    """Exception type used for signaling loop completion."""
    pass

  def __init__(self, commands, prompt=None):
    cmd.Cmd.__init__(self)
    self._commands = {'help': commands['help']}
    self._special_command_names = ['help', 'repl', 'EOF']
    for name, command in commands.iteritems():
      if (name not in self._special_command_names and
          isinstance(command, NewCmd) and
          command.surface_in_shell):
        self._commands[name] = command
        setattr(self, 'do_%s' % (name,), command.RunCmdLoop)
    self._default_prompt = prompt or 'BigQuery> '
    self._set_prompt()
    self._last_return_code = 0

  @property
  def last_return_code(self):
    return self._last_return_code

  def _set_prompt(self):
    client = Client().Get()
    if client.project_id:
      path = str(client.GetReference())
      self.prompt = '%s> ' % (path,)
    else:
      self.prompt = self._default_prompt

  def do_EOF(self, *unused_args):
    """Terminate the running command loop.

    This function raises an exception to avoid the need to do
    potentially-error-prone string parsing inside onecmd.

    Returns:
      Never returns.

    Raises:
      CommandLoop.TerminateSignal: always.
    """
    raise CommandLoop.TerminateSignal()

  def postloop(self):
    print 'Goodbye.'

  def completedefault(self, unused_text, line, unused_begidx, unused_endidx):
    if not line:
      return []
    else:
      command_name = line.partition(' ')[0].lower()
      usage = ''
      if command_name in self._commands:
        usage = self._commands[command_name].usage
      elif command_name == 'set':
        usage = 'set (project_id|dataset_id) <name>'
      elif command_name == 'unset':
        usage = 'unset (project_id|dataset_id)'
      if usage:
        print
        print usage
        print '%s%s' % (self.prompt, line),
      return []

  def emptyline(self):
    print 'Available commands:',
    print ' '.join(list(self._commands))

  def precmd(self, line):
    """Preprocess the shell input."""
    if line == 'EOF':
      return line
    if line.startswith('exit') or line.startswith('quit'):
      return 'EOF'
    words = line.strip().split()
    if len(words) > 1 and words[0].lower() == 'select':
      return 'query %s' % (pipes.quote(line),)
    if len(words) == 1 and words[0] not in ['help', 'ls', 'version']:
      return 'help %s' % (line.strip(),)
    return line

  def onecmd(self, line):
    """Process a single command.

    Runs a single command, and stores the return code in
    self._last_return_code. Always returns False unless the command
    was EOF.

    Args:
      line: (str) Command line to process.

    Returns:
      A bool signaling whether or not the command loop should terminate.
    """
    try:
      self._last_return_code = cmd.Cmd.onecmd(self, line)
    except CommandLoop.TerminateSignal:
      return True
    except BaseException as e:
      name = line.split(' ')[0]
      BigqueryCmd.ProcessError(e, name=name)
      self._last_return_code = 1
    return False

  def get_names(self):
    names = dir(self)
    commands = (name for name in self._commands
                if name not in self._special_command_names)
    names.extend('do_%s' % (name,) for name in commands)
    names.append('do_select')
    names.remove('do_EOF')
    return names

  def do_set(self, line):
    """Set the value of the project_id or dataset_id flag."""
    client = Client().Get()
    name, value = (line.split(' ') + ['', ''])[:2]
    if (name not in ('project_id', 'dataset_id') or
        not 1 <= len(line.split(' ')) <= 2):
      print 'set (project_id|dataset_id) <name>'
    elif name == 'dataset_id' and not client.project_id:
      print 'Cannot set dataset_id with project_id unset'
    else:
      setattr(client, name, value)
      self._set_prompt()
    return 0

  def do_unset(self, line):
    """Unset the value of the project_id or dataset_id flag."""
    name = line.strip()
    client = Client.Get()
    if name not in ('project_id', 'dataset_id'):
      print 'unset (project_id|dataset_id)'
    else:
      setattr(client, name, '')
      if name == 'project_id':
        client.dataset_id = ''
      self._set_prompt()
    return 0

  def do_help(self, command_name):
    """Print the help for command_name (if present) or general help."""

    # TODO(user): Add command-specific flags.
    def FormatOneCmd(name, command, command_names):
      indent_size = appcommands.GetMaxCommandLength() + 3
      if len(command_names) > 1:
        indent = ' ' * indent_size
        command_help = flags.TextWrap(
            command.CommandGetHelp('', cmd_names=command_names),
            indent=indent,
            firstline_indent='')
        first_help_line, _, rest = command_help.partition('\n')
        first_line = '%-*s%s' % (indent_size, name + ':', first_help_line)
        return '\n'.join((first_line, rest))
      else:
        default_indent = '  '
        return '\n' + flags.TextWrap(
            command.CommandGetHelp('', cmd_names=command_names),
            indent=default_indent,
            firstline_indent=default_indent) + '\n'

    if not command_name:
      print '\nHelp for Bigquery commands:\n'
      command_names = list(self._commands)
      print '\n\n'.join(
          FormatOneCmd(name, command, command_names)
          for name, command in self._commands.iteritems()
          if name not in self._special_command_names)
      print
    elif command_name in self._commands:
      print FormatOneCmd(command_name, self._commands[command_name],
                         command_names=[command_name])
    return 0

  def postcmd(self, stop, line):
    return bool(stop) or line == 'EOF'
# pylint: enable=g-bad-name


class _Repl(BigqueryCmd):
  """Start an interactive bq session."""

  def __init__(self, name, fv):
    super(_Repl, self).__init__(name, fv)
    self.surface_in_shell = False
    flags.DEFINE_string(
        'prompt', '',
        'Prompt to use for BigQuery shell.',
        flag_values=fv)

  def RunWithArgs(self):
    """Start an interactive bq session."""
    repl = CommandLoop(appcommands.GetCommandList(), prompt=self.prompt)
    print 'Welcome to BigQuery! (Type help for more information.)'
    while True:
      try:
        repl.cmdloop()
        break
      except KeyboardInterrupt:
        print
    return repl.last_return_code


class _Init(BigqueryCmd):
  """Create a .bigqueryrc file and set up OAuth credentials."""

  def __init__(self, name, fv):
    super(_Init, self).__init__(name, fv)
    self.surface_in_shell = False
    flags.DEFINE_boolean(
        'delete_credentials', None,
        'If specified, the credentials file associated with this .bigqueryrc '
        'file is deleted.',
        flag_values=fv)

  def _NeedsInit(self):
    """Init never needs to call itself before running."""
    return False

  def DeleteCredentials(self):
    """Deletes this user's credential file."""
    _ProcessBigqueryrc()
    filename = FLAGS.service_account_credential_file or FLAGS.credential_file
    if not os.path.exists(filename):
      print 'Credential file %s does not exist.' % (filename,)
      return 0
    try:
      if 'y' != _PromptYN('Delete credential file %s? (y/N) ' % (filename,)):
        print 'NOT deleting %s, exiting.' % (filename,)
        return 0
      os.remove(filename)
    except OSError as e:
      print 'Error removing %s: %s' % (filename, e)
      return 1

  def RunWithArgs(self):
    """Authenticate and create a default .bigqueryrc file."""
    _ProcessBigqueryrc()
    bigquery_client.ConfigurePythonLogger(FLAGS.apilog)
    if self.delete_credentials:
      return self.DeleteCredentials()
    bigqueryrc = _GetBigqueryRcFilename()
    # Delete the old one, if it exists.
    print
    print 'Welcome to BigQuery! This script will walk you through the '
    print 'process of initializing your .bigqueryrc configuration file.'
    print
    if os.path.exists(bigqueryrc):
      print ' **** NOTE! ****'
      print 'An existing .bigqueryrc file was found at %s.' % (bigqueryrc,)
      print 'Are you sure you want to continue and overwrite your existing '
      print 'configuration?'
      print

      if 'y' != _PromptYN('Overwrite %s? (y/N) ' % (bigqueryrc,)):
        print 'NOT overwriting %s, exiting.' % (bigqueryrc,)
        return 0
      print
      try:
        os.remove(bigqueryrc)
      except OSError as e:
        print 'Error removing %s: %s' % (bigqueryrc, e)
        return 1

    print 'First, we need to set up your credentials if they do not '
    print 'already exist.'
    print

    client = Client.Get()
    entries = {'credential_file': FLAGS.credential_file}
    projects = client.ListProjects()
    print 'Credential creation complete. Now we will select a default project.'
    print
    if not projects:
      print 'No projects found for this user. Please go to '
      print '  https://code.google.com/apis/console'
      print 'and create a project.'
      print
    else:
      print 'List of projects:'
      formatter = _GetFormatterFromFlags()
      formatter.AddColumn('#')
      BigqueryClient.ConfigureFormatter(formatter, ProjectReference)
      for index, project in enumerate(projects):
        result = BigqueryClient.FormatProjectInfo(project)
        result.update({'#': index + 1})
        formatter.AddDict(result)
      formatter.Print()

      if len(projects) == 1:
        project_reference = BigqueryClient.ConstructObjectReference(
            projects[0])
        print 'Found only one project, setting %s as the default.' % (
            project_reference,)
        print
        entries['project_id'] = project_reference.projectId
      else:
        print 'Found multiple projects. Please enter a selection for '
        print 'which should be the default, or leave blank to not '
        print 'set a default.'
        print

        response = None
        while not isinstance(response, int):
          response = _PromptWithDefault(
              'Enter a selection (1 - %s): ' % (len(projects),))
          try:
            if not response or 1 <= int(response) <= len(projects):
              response = int(response or 0)
          except ValueError:
            pass
        print
        if response:
          project_reference = BigqueryClient.ConstructObjectReference(
              projects[response - 1])
          entries['project_id'] = project_reference.projectId

    try:
      with open(bigqueryrc, 'w') as rcfile:
        for flag, value in entries.iteritems():
          print >>rcfile, '%s = %s' % (flag, value)
    except IOError as e:
      print 'Error writing %s: %s' % (bigqueryrc, e)
      return 1

    print 'BigQuery configuration complete! Type "bq" to get started.'
    print
    _ProcessBigqueryrc()
    # Destroy the client we created, so that any new client will
    # pick up new flag values.
    Client.Delete()
    return 0


class _Version(BigqueryCmd):
  usage = """version"""

  def _NeedsInit(self):
    """If just printing the version, don't run `init` first."""
    return False

  def RunWithArgs(self):
    """Return the version of bq."""
    print 'This is BigQuery CLI %s' % (_VERSION_NUMBER,)


def main(unused_argv):
  # Avoid using global flags in main(). In this command line:
  # bq <global flags> <command> <global and local flags> <command args>,
  # only "<global flags>" will parse before main, not "<global and local flags>"
  try:
    FLAGS.auth_local_webserver = False
    _ValidateGlobalFlags()

    bq_commands = {
        # Keep the commands alphabetical.
        'cp': _Copy,
        'extract': _Extract,
        'head': _Head,
        'init': _Init,
        'insert': _Insert,
        'load': _Load,
        'ls': _List,
        'mk': _Make,
        'query': _Query,
        'rm': _Delete,
        'shell': _Repl,
        'show': _Show,
        'update': _Update,
        'version': _Version,
        'wait': _Wait,
    }

    for command, function in bq_commands.iteritems():
      if command not in appcommands.GetCommandList():
        appcommands.AddCmd(command, function)

  except KeyboardInterrupt as e:
    print 'Control-C pressed, exiting.'
    sys.exit(1)
  except BaseException as e:  # pylint: disable=broad-except
    print 'Error initializing bq client: %s' % (e,)
    # Use global flags if they're available, but we're exitting so we can't
    # count on global flag parsing anyways.
    if FLAGS.debug_mode or FLAGS.headless:
      traceback.print_exc()
      if not FLAGS.headless:
        pdb.post_mortem()
    sys.exit(1)




# pylint: disable=g-bad-name
def run_main():
  """Function to be used as setuptools script entry point.

  Appcommands assumes that it always runs as __main__, but launching
  via a setuptools-generated entry_point breaks this rule. We do some
  trickery here to make sure that appcommands and flags find their
  state where they expect to by faking ourselves as __main__.
  """

  # Put the flags for this module somewhere the flags module will look
  # for them.
  # pylint: disable=protected-access
  new_name = flags._GetMainModule()
  sys.modules[new_name] = sys.modules['__main__']
  for flag in FLAGS.FlagsByModuleDict().get(__name__, []):
    FLAGS._RegisterFlagByModule(new_name, flag)
    for key_flag in FLAGS.KeyFlagsByModuleDict().get(__name__, []):
      FLAGS._RegisterKeyFlagForModule(new_name, key_flag)
  # pylint: enable=protected-access

  # Now set __main__ appropriately so that appcommands will be
  # happy.
  sys.modules['__main__'] = sys.modules[__name__]
  appcommands.Run()
  sys.modules['__main__'] = sys.modules.pop(new_name)


if __name__ == '__main__':
  appcommands.Run()
