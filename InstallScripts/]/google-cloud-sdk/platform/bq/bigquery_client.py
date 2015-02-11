#!/usr/bin/env python
# Copyright 2012 Google Inc. All Rights Reserved.

"""Bigquery Client library for Python."""



import abc
import collections
import datetime
import hashlib
import itertools
import json
import logging
import os
import pkgutil
import random
import re
import string
import sys
import textwrap
import time
import traceback


import apiclient
from apiclient import discovery
from apiclient import http as http_request
from apiclient import model
import httplib2


# To configure apiclient logging.
import gflags as flags


# A unique non-None default, for use in kwargs that need to
# distinguish default from None.
_DEFAULT = object()

# Maximum number of jobs that can be retrieved by ListJobs (sanity limit).
_MAX_RESULTS = 100000


def _Typecheck(obj, types, message=None, method=None):
  if not isinstance(obj, types):
    if not message:
      if method:
        message = 'Invalid reference for %s: %r' % (method, obj)
      else:
        message = 'Type of %r is not one of %s' % (obj, types)
    raise TypeError(message)


def _ToLowerCamel(name):
  """Convert a name with underscores to camelcase."""
  return re.sub('_[a-z]', lambda match: match.group(0)[1].upper(), name)


def _ToFilename(url):
  """Converts a url to a filename."""
  return ''.join([c for c in url if c in string.ascii_lowercase])


def _ApplyParameters(config, **kwds):
  """Adds all kwds to config dict, adjusting keys to camelcase.

  Note this does not remove entries that are set to None, however.

  kwds: A dict of keys and values to set in the config.

  Args:
    config: A configuration dict.
  """
  config.update((_ToLowerCamel(k), v) for k, v in kwds.iteritems()
                if v is not None)


def ConfigurePythonLogger(apilog=None):
  """Sets up Python logger, which BigqueryClient logs with.

  Applications can configure logging however they want, but this
  captures one pattern of logging which seems useful when dealing with
  a single command line option for determining logging.

  Args:
    apilog: To log to sys.stdout, specify '', '-', '1', 'true', or
      'stdout'. To log to sys.stderr, specify 'stderr'. To log to a
      file, specify the file path. Specify None to disable logging.
  """
  if apilog is None:
    # Effectively turn off logging.
    logging.disable(logging.CRITICAL)
  else:
    if apilog in ('', '-', '1', 'true', 'stdout'):
      logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    elif apilog == 'stderr':
      logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    elif apilog:
      logging.basicConfig(filename=apilog, level=logging.INFO)
    else:
      logging.basicConfig(level=logging.INFO)
    # Turn on apiclient logging of http requests and responses. (Here
    # we handle both the flags interface from apiclient < 1.2 and the
    # module global in apiclient >= 1.2.)
    if hasattr(flags.FLAGS, 'dump_request_response'):
      flags.FLAGS.dump_request_response = True
    else:
      model.dump_request_response = True


InsertEntry = collections.namedtuple('InsertEntry',
                                     ['insert_id', 'record'])


def JsonToInsertEntry(insert_id, json_string):
  """Parses a JSON encoded record and returns an InsertEntry.

  Arguments:
    insert_id: Id for the insert, can be None.
    json_string: The JSON encoded data to be converted.
  Returns:
    InsertEntry object for adding to a table.
  """
  try:
    row = json.loads(json_string)
    if not isinstance(row, dict):
      raise BigqueryClientError('Value is not a JSON object')
    return InsertEntry(insert_id, row)
  except ValueError, e:
    raise BigqueryClientError('Could not parse object: %s' % (str(e),))


class BigqueryError(Exception):

  @staticmethod
  def Create(error, server_error, error_ls, job_ref=None):
    """Returns a BigqueryError for json error embedded in server_error.

    If error_ls contains any errors other than the given one, those
    are also included in the returned message.

    Args:
      error: The primary error to convert.
      server_error: The error returned by the server. (This is only used
        in the case that error is malformed.)
      error_ls: Additional errors to include in the error message.
      job_ref: JobReference, if this is an error associated with a job.

    Returns:
      BigqueryError representing error.
    """
    reason = error.get('reason')
    if job_ref:
      message = 'Error processing %r: %s' % (job_ref, error.get('message'))
    else:
      message = error.get('message')
    # We don't want to repeat the "main" error message.
    new_errors = [err for err in error_ls if err != error]
    if new_errors:
      message += '\nFailure details:\n'
      message += '\n'.join(
          textwrap.fill(
              ': '.join(filter(None, [
                  err.get('location', None), err.get('message', '')])),
              initial_indent=' - ',
              subsequent_indent='   ')
          for err in new_errors)
    if not reason or not message:
      return BigqueryInterfaceError(
          'Error reported by server with missing error fields. '
          'Server returned: %s' % (str(server_error),))
    if reason == 'notFound':
      return BigqueryNotFoundError(message, error, error_ls, job_ref=job_ref)
    if reason == 'duplicate':
      return BigqueryDuplicateError(message, error, error_ls, job_ref=job_ref)
    if reason == 'accessDenied':
      return BigqueryAccessDeniedError(
          message, error, error_ls, job_ref=job_ref)
    if reason == 'invalidQuery':
      return BigqueryInvalidQueryError(
          message, error, error_ls, job_ref=job_ref)
    if reason == 'termsOfServiceNotAccepted':
      return BigqueryTermsOfServiceError(
          message, error, error_ls, job_ref=job_ref)
    if reason == 'backendError':
      return BigqueryBackendError(
          message, error, error_ls, job_ref=job_ref)
    # We map the less interesting errors to BigqueryServiceError.
    return BigqueryServiceError(message, error, error_ls, job_ref=job_ref)


class BigqueryCommunicationError(BigqueryError):
  """Error communicating with the server."""
  pass


class BigqueryInterfaceError(BigqueryError):
  """Response from server missing required fields."""
  pass


class BigqueryServiceError(BigqueryError):
  """Base class of Bigquery-specific error responses.

  The BigQuery server received request and returned an error.
  """

  def __init__(self, message, error, error_list, job_ref=None,
               *args, **kwds):
    """Initializes a BigqueryServiceError.

    Args:
      message: A user-facing error message.
      error: The error dictionary, code may inspect the 'reason' key.
      error_list: A list of additional entries, for example a load job
        may contain multiple errors here for each error encountered
        during processing.
      job_ref: Optional JobReference, if this error was encountered
        while processing a job.
    """
    super(BigqueryServiceError, self).__init__(message, *args, **kwds)
    self.error = error
    self.error_list = error_list
    self.job_ref = job_ref

  def __repr__(self):
    return '%s: error=%s, error_list=%s, job_ref=%s' % (
        self.__class__.__name__, self.error, self.error_list, self.job_ref)


class BigqueryNotFoundError(BigqueryServiceError):
  """The requested resource or identifier was not found."""
  pass


class BigqueryDuplicateError(BigqueryServiceError):
  """The requested resource or identifier already exists."""
  pass


class BigqueryAccessDeniedError(BigqueryServiceError):
  """The user does not have access to the requested resource."""
  pass


class BigqueryInvalidQueryError(BigqueryServiceError):
  """The SQL statement is invalid."""
  pass


class BigqueryTermsOfServiceError(BigqueryAccessDeniedError):
  """User has not ACK'd ToS."""
  pass


class BigqueryBackendError(BigqueryServiceError):
  """A backend error typically corresponding to retriable HTTP 503 failures."""
  pass


class BigqueryClientError(BigqueryError):
  """Invalid use of BigqueryClient."""
  pass


class BigqueryClientConfigurationError(BigqueryClientError):
  """Invalid configuration of BigqueryClient."""
  pass


class BigquerySchemaError(BigqueryClientError):
  """Error in locating or parsing the schema."""
  pass


class BigqueryModel(model.JsonModel):
  """Adds optional global parameters to all requests."""

  def __init__(self, trace=None, **kwds):
    super(BigqueryModel, self).__init__(**kwds)
    self.trace = trace

  # pylint: disable=g-bad-name
  def request(self, headers, path_params, query_params, body_value):
    """Updates outgoing request."""
    if 'trace' not in query_params and self.trace:
      query_params['trace'] = self.trace
    return super(BigqueryModel, self).request(
        headers, path_params, query_params, body_value)
  # pylint: enable=g-bad-name

  # pylint: disable=g-bad-name
  def response(self, resp, content):
    """Convert the response wire format into a Python object."""
    return super(BigqueryModel, self).response(
        resp, content)
  # pylint: enable=g-bad-name


class BigqueryHttp(http_request.HttpRequest):
  """Converts errors into Bigquery errors."""

  def __init__(self, bigquery_model, *args, **kwds):
    super(BigqueryHttp, self).__init__(*args, **kwds)
    self._model = bigquery_model

  @staticmethod
  def Factory(bigquery_model):
    """Returns a function that creates a BigqueryHttp with the given model."""

    def _Construct(*args, **kwds):
      captured_model = bigquery_model
      return BigqueryHttp(captured_model, *args, **kwds)
    return _Construct

  def execute(self, **kwds):  # pylint: disable=g-bad-name
    try:
      return super(BigqueryHttp, self).execute(**kwds)
    except apiclient.errors.HttpError, e:
      # TODO(user): Remove this when apiclient supports logging
      # of error responses.
      self._model._log_response(e.resp, e.content)  # pylint: disable=protected-access
      if e.resp.get('content-type', '').startswith('application/json'):
        BigqueryClient.RaiseError(json.loads(e.content))
      else:
        raise BigqueryCommunicationError(
            ('Could not connect with BigQuery server.\n'
             'Http response status: %s\n'
             'Http response content:\n%s') % (
                 e.resp.get('status', '(unexpected)'), e.content))
    except (httplib2.HttpLib2Error, IOError), e:
      raise BigqueryCommunicationError(
          'Could not connect with BigQuery server due to: %r' % (e,))


class JobIdGenerator(object):
  """Base class for job id generators."""
  __metaclass__ = abc.ABCMeta

  @abc.abstractmethod
  def Generate(self, job_configuration):
    """Generates a job_id to use for job_configuration."""


class JobIdGeneratorNone(JobIdGenerator):
  """Job id generator that returns None, letting the server pick the job id."""

  def Generate(self, unused_config):
    return None


class JobIdGeneratorRandom(JobIdGenerator):
  """Generates random job ids."""

  def Generate(self, unused_config):
    return 'bqjob_r%08x_%016x' % (random.SystemRandom().randint(0, sys.maxint),
                                  int(time.time() * 1000))


class JobIdGeneratorFingerprint(JobIdGenerator):
  """Generates job ids that uniquely match the job config."""

  def _Hash(self, config, sha1):
    """Computes the sha1 hash of a dict."""
    keys = config.keys()
    # Python dict enumeration ordering is random. Sort the keys
    # so that we will visit them in a stable order.
    keys.sort()
    for key in keys:
      sha1.update('%s' % (key,))
      v = config[key]
      if isinstance(v, dict):
        logging.info('Hashing: %s...', key)
        self._Hash(v, sha1)
      elif isinstance(v, list):
        logging.info('Hashing: %s ...', key)
        for inner_v in v:
          self._Hash(inner_v, sha1)
      else:
        logging.info('Hashing: %s:%s', key, v)
        sha1.update('%s' % (v,))

  def Generate(self, config):
    s1 = hashlib.sha1()
    self._Hash(config, s1)
    job_id = 'bqjob_c%s' % (s1.hexdigest(),)
    logging.info('Fingerprinting: %s:\n%s', config, job_id)
    return job_id


class JobIdGeneratorIncrementing(JobIdGenerator):
  """Generates job ids that increment each time we're asked."""

  def __init__(self, inner):
    self._inner = inner
    self._retry = 0

  def Generate(self, config):
    self._retry += 1
    return '%s_%d' % (self._inner.Generate(config), self._retry)


class BigqueryClient(object):
  """Class encapsulating interaction with the BigQuery service."""

  def __init__(self, **kwds):
    """Initializes BigqueryClient.

    Required keywords:
      api: the api to connect to, for example "bigquery".
      api_version: the version of the api to connect to, for example "v2".

    Optional keywords:
      project_id: a default project id to use. While not required for
        initialization, a project_id is required when calling any
        method that creates a job on the server. Methods that have
        this requirement pass through **kwds, and will raise
        BigqueryClientConfigurationError if no project_id can be
        found.
      dataset_id: a default dataset id to use.
      discovery_document: the discovery document to use. If None, one
        will be retrieved from the discovery api. If not specified,
        the built-in discovery document will be used.
      job_property: a list of "key=value" strings defining properties
        to apply to all job operations.
      trace: a tracing header to inclue in all bigquery api requests.
      sync: boolean, when inserting jobs, whether to wait for them to
        complete before returning from the insert request.
      wait_printer_factory: a function that returns a WaitPrinter.
        This will be called for each job that we wait on. See WaitJob().

    Raises:
      ValueError: if keywords are missing or incorrectly specified.
    """
    super(BigqueryClient, self).__init__()
    for key, value in kwds.iteritems():
      setattr(self, key, value)
    self._apiclient = None
    for required_flag in ('api', 'api_version'):
      if required_flag not in kwds:
        raise ValueError('Missing required flag: %s' % (required_flag,))
    default_flag_values = {
        'project_id': '',
        'dataset_id': '',
        'discovery_document': _DEFAULT,
        'job_property': '',
        'trace': None,
        'sync': True,
        'wait_printer_factory': BigqueryClient.TransitionWaitPrinter,
        'job_id_generator': JobIdGeneratorIncrementing(JobIdGeneratorRandom()),
        'max_rows_per_request': None,
        }
    for flagname, default in default_flag_values.iteritems():
      if not hasattr(self, flagname):
        setattr(self, flagname, default)
    if self.dataset_id and not self.project_id:
      raise ValueError('Cannot set dataset_id without project_id')

  def GetHttp(self):
    """Returns the httplib2 Http to use."""
    http = httplib2.Http()
    return http

  def GetDiscoveryUrl(self):
    """Returns the url to the discovery document for bigquery."""
    discovery_url = self.api + '/discovery/v1/apis/{api}/{apiVersion}/rest'
    return discovery_url

  @property
  def apiclient(self):
    """Return the apiclient attached to self."""
    if self._apiclient is None:
      http = self.credentials.authorize(self.GetHttp())
      bigquery_model = BigqueryModel(
          trace=self.trace)
      bigquery_http = BigqueryHttp.Factory(
          bigquery_model)
      discovery_document = self.discovery_document
      if discovery_document == _DEFAULT:
        # Use the api description packed with this client, if one exists.
        try:
          discovery_document = pkgutil.get_data(
              'bigquery_client', 'discovery/%s.bigquery.%s.rest.json'
              % (_ToFilename(self.api), self.api_version))
        except IOError:
          discovery_document = None
      if discovery_document is None:
        try:
          self._apiclient = discovery.build(
              'bigquery', self.api_version, http=http,
              discoveryServiceUrl=self.GetDiscoveryUrl(),
              model=bigquery_model,
              requestBuilder=bigquery_http)
        except (httplib2.HttpLib2Error, apiclient.errors.HttpError), e:
          # We can't find the specified server. This can be thrown for
          # multiple reasons, so inspect the error.
          if hasattr(e, 'content'):
            raise BigqueryCommunicationError(
                'Cannot contact server. Please try again.\nError: %r'
                '\nContent: %s' % (e, e.content))
          else:
            raise BigqueryCommunicationError(
                'Cannot contact server. Please try again.\n'
                'Traceback: %s' % (traceback.format_exc(),))
        except IOError, e:
          raise BigqueryCommunicationError(
              'Cannot contact server. Please try again.\nError: %r' % (e,))
        except apiclient.errors.UnknownApiNameOrVersion, e:
          # We can't resolve the discovery url for the given server.
          raise BigqueryCommunicationError(
              'Invalid API name or version: %s' % (str(e),))
      else:
        self._apiclient = discovery.build_from_document(
            discovery_document, http=http,
            model=bigquery_model,
            requestBuilder=bigquery_http)
    return self._apiclient

  #################################
  ## Utility methods
  #################################

  @staticmethod
  def FormatTime(secs):
    return time.strftime('%d %b %H:%M:%S', time.localtime(secs))

  @staticmethod
  def FormatAcl(acl):
    """Format a server-returned ACL for printing."""
    acl_entries = {
        'OWNER': [],
        'WRITER': [],
        'READER': [],
        'VIEW': [],
        }
    for entry in acl:
      entry = entry.copy()
      view = entry.pop('view', None)
      if view:
        acl_entries['VIEW'].append('%s:%s.%s' % (view.get('projectId'),
                                                 view.get('datasetId'),
                                                 view.get('tableId')))
      else:
        role = entry.pop('role', None)
        if not role or len(entry.values()) != 1:
          raise BigqueryServiceError(
              'Invalid ACL returned by server: %s' % (acl,))
        for _, value in entry.iteritems():
          acl_entries[role].append(value)
    result_lines = []
    if acl_entries['OWNER']:
      result_lines.extend([
          'Owners:', ',\n'.join('  %s' % (o,) for o in acl_entries['OWNER'])])
    if acl_entries['WRITER']:
      result_lines.extend([
          'Writers:', ',\n'.join('  %s' % (o,) for o in acl_entries['WRITER'])])
    if acl_entries['READER']:
      result_lines.extend([
          'Readers:', ',\n'.join('  %s' % (o,) for o in acl_entries['READER'])])
    if acl_entries['VIEW']:
      result_lines.extend([
          'Authorized Views:', ',\n'.join('  %s' % (o,) for o in
                                          acl_entries['VIEW'])])
    return '\n'.join(result_lines)

  @staticmethod
  def FormatSchema(schema):
    """Format a schema for printing."""

    def PrintFields(fields, indent=0):
      """Print all fields in a schema, recurring as necessary."""
      lines = []
      for field in fields:
        prefix = '|  ' * indent
        junction = '|' if field.get('type', 'STRING') != 'RECORD' else '+'
        entry = '%s- %s: %s' % (
            junction, field['name'], field.get('type', 'STRING').lower())
        if field.get('mode', 'NULLABLE') != 'NULLABLE':
          entry += ' (%s)' % (field['mode'].lower(),)
        lines.append(prefix + entry)
        if 'fields' in field:
          lines.extend(PrintFields(field['fields'], indent + 1))
      return lines

    return '\n'.join(PrintFields(schema.get('fields', [])))

  @staticmethod
  def NormalizeWait(wait):
    try:
      return int(wait)
    except ValueError:
      raise ValueError('Invalid value for wait: %s' % (wait,))

  @staticmethod
  def ValidatePrintFormat(print_format):
    if print_format not in ['show', 'list', 'view']:
      raise ValueError('Unknown format: %s' % (print_format,))

  @staticmethod
  def _ParseIdentifier(identifier):
    """Parses identifier into a tuple of (possibly empty) identifiers.

    This will parse the identifier into a tuple of the form
    (project_id, dataset_id, table_id) without doing any validation on
    the resulting names; missing names are returned as ''. The
    interpretation of these identifiers depends on the context of the
    caller. For example, if you know the identifier must be a job_id,
    then you can assume dataset_id is the job_id.

    Args:
      identifier: string, identifier to parse

    Returns:
      project_id, dataset_id, table_id: (string, string, string)
    """
    # We need to handle the case of a lone project identifier of the
    # form domain.com:proj separately.
    if re.search(r'^\w[\w.]*\.[\w.]+:\w[\w\d_-]*:?$', identifier):
      return identifier, '', ''
    project_id, _, dataset_and_table_id = identifier.rpartition(':')

    if '.' in dataset_and_table_id:
      dataset_id, _, table_id = dataset_and_table_id.rpartition('.')
    elif project_id:
      # Identifier was a project : <something without dots>.
      # We must have a dataset id because there was a project
      dataset_id = dataset_and_table_id
      table_id = ''
    else:
      # Identifier was just a bare id with no dots or colons.
      # Return this as a table_id.
      dataset_id = ''
      table_id = dataset_and_table_id

    return project_id, dataset_id, table_id

  def GetProjectReference(self, identifier=''):
    """Determine a project reference from an identifier and self."""
    project_id, dataset_id, table_id = BigqueryClient._ParseIdentifier(
        identifier)
    try:
      # ParseIdentifier('foo') is just a table_id, but we want to read
      # it as a project_id.
      project_id = project_id or table_id or self.project_id
      if not dataset_id and project_id:
        return ApiClientHelper.ProjectReference.Create(projectId=project_id)
    except ValueError:
      pass
    raise BigqueryClientError('Cannot determine project described by %s' % (
        identifier,))

  def GetDatasetReference(self, identifier=''):
    """Determine a DatasetReference from an identifier and self."""
    project_id, dataset_id, table_id = BigqueryClient._ParseIdentifier(
        identifier)
    if table_id and not project_id and not dataset_id:
      # identifier is 'foo'
      project_id = self.project_id
      dataset_id = table_id
    elif project_id and dataset_id and table_id:
      # Identifier was foo::bar.baz.qux.
      dataset_id = dataset_id + '.' + table_id
    elif project_id and dataset_id and not table_id:
      # identifier is 'foo:bar'
      pass
    elif not identifier:
      # identifier is ''
      project_id = self.project_id
      dataset_id = self.dataset_id
    else:
      raise BigqueryError('Cannot determine dataset described by %s' % (
          identifier,))

    try:
      return ApiClientHelper.DatasetReference.Create(
          projectId=project_id, datasetId=dataset_id)
    except ValueError:
      raise BigqueryError('Cannot determine dataset described by %s' % (
          identifier,))

  def GetTableReference(self, identifier=''):
    """Determine a TableReference from an identifier and self."""
    project_id, dataset_id, table_id = BigqueryClient._ParseIdentifier(
        identifier)
    try:
      return ApiClientHelper.TableReference.Create(
          projectId=project_id or self.project_id,
          datasetId=dataset_id or self.dataset_id,
          tableId=table_id,
          )
    except ValueError:
      raise BigqueryError('Cannot determine table described by %s' % (
          identifier,))


  def GetReference(self, identifier=''):
    """Try to deduce a project/dataset/table reference from a string.

    If the identifier is not compound, treat it as the most specific
    identifier we don't have as a flag, or as the table_id. If it is
    compound, fill in any unspecified part.

    Args:
      identifier: string, Identifier to create a reference for.

    Returns:
      A valid ProjectReference, DatasetReference, or TableReference.

    Raises:
      BigqueryError: if no valid reference can be determined.
    """
    try:
      return self.GetTableReference(identifier)
    except BigqueryError:
      pass
    try:
      return self.GetDatasetReference(identifier)
    except BigqueryError:
      pass
    try:
      return self.GetProjectReference(identifier)
    except BigqueryError:
      pass
    raise BigqueryError('Cannot determine reference for "%s"' % (identifier,))

  # TODO(user): consider introducing job-specific and possibly
  # dataset- and project-specific parsers for the case of knowing what
  # type we are looking for. Reinterpreting "dataset_id" as "job_id"
  # is rather confusing.
  def GetJobReference(self, identifier=''):
    """Determine a JobReference from an identifier and self."""
    project_id, dataset_id, table_id = BigqueryClient._ParseIdentifier(
        identifier)
    if table_id and not project_id and not dataset_id:
      # identifier is 'foo'
      project_id = self.project_id
      job_id = table_id
    elif project_id and dataset_id and not table_id:
      # identifier is 'foo:bar'
      job_id = dataset_id
    else:
      job_id = None
    if job_id:
      try:
        return ApiClientHelper.JobReference.Create(
            projectId=project_id, jobId=job_id)
      except ValueError:
        pass
    raise BigqueryError('Cannot determine job described by %s' % (
        identifier,))

  def GetObjectInfo(self, reference):
    """Get all data returned by the server about a specific object."""
    # Projects are handled separately, because we only have
    # bigquery.projects.list.
    if isinstance(reference, ApiClientHelper.ProjectReference):
      projects = self.ListProjects()
      for project in projects:
        if BigqueryClient.ConstructObjectReference(project) == reference:
          project['kind'] = 'bigquery#project'
          return project
      raise BigqueryNotFoundError('Unknown %r' % (reference,))

    if isinstance(reference, ApiClientHelper.JobReference):
      return self.apiclient.jobs().get(**dict(reference)).execute()
    elif isinstance(reference, ApiClientHelper.DatasetReference):
      return self.apiclient.datasets().get(**dict(reference)).execute()
    elif isinstance(reference, ApiClientHelper.TableReference):
      return self.apiclient.tables().get(**dict(reference)).execute()
    else:
      raise TypeError('Type of reference must be one of: ProjectReference, '
                      'JobReference, DatasetReference, or TableReference')

  def GetTableSchema(self, table_dict):
    table_info = self.apiclient.tables().get(**table_dict).execute()
    return table_info.get('schema', {})

  def InsertTableRows(self, table_dict, inserts):
    """Insert rows into a table.

    Arguments:
      table_dict: table reference into which rows are to be inserted.
      inserts: array of InsertEntry tuples where insert_id can be None.

    Returns:
      result of the operation.
    """
    def _EncodeInsert(insert):
      encoded = dict(json=insert.record)
      if insert.insert_id:
        encoded['insertId'] = insert.insert_id
      return encoded
    op = self.apiclient.tabledata().insertAll(
        body=dict(rows=map(_EncodeInsert, inserts)),
        **table_dict)
    return op.execute()

  def ReadSchemaAndRows(self, table_dict, start_row=None, max_rows=None):
    """Convenience method to get the schema and rows from a table.

    Arguments:
      table_dict: table reference dictionary.
      start_row: first row to read.
      max_rows: number of rows to read.

    Returns:
      A tuple where the first item is the list of fields and the
      second item a list of rows.

    Raises:
      ValueError: will be raised if start_row is not explicitly provided.
      ValueError: will be raised if max_rows is not explicitly provided.
    """
    if start_row is None:
      raise ValueError('start_row is required')
    if max_rows is None:
      raise ValueError('max_rows is required')
    table_ref = ApiClientHelper.TableReference.Create(**table_dict)
    return _TableTableReader(self.apiclient, self.max_rows_per_request,
                             table_ref).ReadSchemaAndRows(start_row,
                                                          max_rows)

  def ReadSchemaAndJobRows(self, job_dict, start_row=None, max_rows=None):
    """Convenience method to get the schema and rows from job query result.

    Arguments:
      job_dict: job reference dictionary.
      start_row: first row to read.
      max_rows: number of rows to read.

    Returns:
      A tuple where the first item is the list of fields and the
      second item a list of rows.
    Raises:
      ValueError: will be raised if start_row is not explicitly provided.
      ValueError: will be raised if max_rows is not explicitly provided.
    """
    if start_row is None:
      raise ValueError('start_row is required')
    if max_rows is None:
      raise ValueError('max_rows is required')
    job_ref = ApiClientHelper.JobReference.Create(**job_dict)
    reader = _JobTableReader(self.apiclient, self.max_rows_per_request,
                             job_ref)
    return reader.ReadSchemaAndRows(start_row, max_rows)

  @staticmethod
  def ConfigureFormatter(formatter, reference_type, print_format='list'):
    """Configure a formatter for a given reference type.

    If print_format is 'show', configures the formatter with several
    additional fields (useful for printing a single record).

    Arguments:
      formatter: TableFormatter object to configure.
      reference_type: Type of object this formatter will be used with.
      print_format: Either 'show' or 'list' to control what fields are
        included.

    Raises:
      ValueError: If reference_type or format is unknown.
    """
    BigqueryClient.ValidatePrintFormat(print_format)
    if reference_type == ApiClientHelper.JobReference:
      if print_format == 'list':
        formatter.AddColumns(('jobId',))
      formatter.AddColumns(
          ('Job Type', 'State', 'Start Time', 'Duration',))
      if print_format == 'show':
        formatter.AddColumns(('Bytes Processed',))
    elif reference_type == ApiClientHelper.ProjectReference:
      if print_format == 'list':
        formatter.AddColumns(('projectId',))
      formatter.AddColumns(('friendlyName',))
    elif reference_type == ApiClientHelper.DatasetReference:
      if print_format == 'list':
        formatter.AddColumns(('datasetId',))
      if print_format == 'show':
        formatter.AddColumns(('Last modified', 'ACLs',))
    elif reference_type == ApiClientHelper.TableReference:
      if print_format == 'list':
        formatter.AddColumns(('tableId', 'Type',))
      if print_format == 'show':
        formatter.AddColumns(('Last modified', 'Schema',
                              'Total Rows', 'Total Bytes',
                              'Expiration'))
      if print_format == 'view':
        formatter.AddColumns(('Query',))
    else:
      raise ValueError('Unknown reference type: %s' % (
          reference_type.__name__,))

  @staticmethod
  def RaiseError(result):
    """Raises an appropriate BigQuery error given the json error result."""
    error = result.get('error', {}).get('errors', [{}])[0]
    raise BigqueryError.Create(error, result, [])

  @staticmethod
  def IsFailedJob(job):
    """Predicate to determine whether or not a job failed."""
    return 'errorResult' in job.get('status', {})

  @staticmethod
  def RaiseIfJobError(job):
    """Raises a BigQueryError if the job is in an error state.

    Args:
      job: a Job resource.

    Returns:
      job, if it is not in an error state.

    Raises:
      BigqueryError: A BigqueryError instance based on the job's error
      description.
    """
    if BigqueryClient.IsFailedJob(job):
      error = job['status']['errorResult']
      error_ls = job['status'].get('errors', [])
      raise BigqueryError.Create(
          error, error, error_ls,
          job_ref=BigqueryClient.ConstructObjectReference(job))
    return job

  @staticmethod
  def GetJobTypeName(job_info):
    """Helper for job printing code."""
    job_names = set(('extract', 'load', 'query', 'copy'))
    try:
      return set(job_info.get('configuration', {}).keys()).intersection(
          job_names).pop()
    except KeyError:
      return None

  @staticmethod
  def ProcessSources(source_string):
    """Take a source string and return a list of URIs.

    The list will consist of either a single local filename, which
    we check exists and is a file, or a list of gs:// uris.

    Args:
      source_string: A comma-separated list of URIs.

    Returns:
      List of one or more valid URIs, as strings.

    Raises:
      BigqueryClientError: if no valid list of sources can be determined.
    """
    sources = [source.strip() for source in source_string.split(',')]
    gs_uris = [source for source in sources if source.startswith('gs://')]
    if not sources:
      raise BigqueryClientError('No sources specified')
    if gs_uris:
      if len(gs_uris) != len(sources):
        raise BigqueryClientError('All URIs must begin with "gs://" if any do.')
      return sources
    else:
      source = sources[0]
      if len(sources) > 1:
        raise BigqueryClientError(
            'Local upload currently supports only one file, found %d' % (
                len(sources),))
      if not os.path.exists(source):
        raise BigqueryClientError('Source file not found: %s' % (source,))
      if not os.path.isfile(source):
        raise BigqueryClientError('Source path is not a file: %s' % (source,))
    return sources

  @staticmethod
  def ReadSchema(schema):
    """Create a schema from a string or a filename.

    If schema does not contain ':' and is the name of an existing
    file, read it as a JSON schema. If not, it must be a
    comma-separated list of fields in the form name:type.

    Args:
      schema: A filename or schema.

    Returns:
      The new schema (as a dict).

    Raises:
      BigquerySchemaError: If the schema is invalid or the filename does
          not exist.
    """

    def NewField(entry):
      name, _, field_type = entry.partition(':')
      if entry.count(':') > 1 or not name.strip():
        raise BigquerySchemaError('Invalid schema entry: %s' % (entry,))
      return {
          'name': name.strip(),
          'type': field_type.strip().upper() or 'STRING',
          }

    if not schema:
      raise BigquerySchemaError('Schema cannot be empty')
    elif os.path.exists(schema):
      with open(schema) as f:
        try:
          return json.load(f)
        except ValueError, e:
          raise BigquerySchemaError(
              ('Error decoding JSON schema from file %s: %s\n'
               'To specify a one-column schema, use "name:string".') % (
                   schema, e))
    elif re.match(r'[./\\]', schema) is not None:
      # We have something that looks like a filename, but we didn't
      # find it. Tell the user about the problem now, rather than wait
      # for a round-trip to the server.
      raise BigquerySchemaError(
          ('Error reading schema: "%s" looks like a filename, '
           'but was not found.') % (schema,))
    else:
      return [NewField(entry) for entry in schema.split(',')]

  @staticmethod
  def _KindToName(kind):
    """Convert a kind to just a type name."""
    return kind.partition('#')[2]

  @staticmethod
  def FormatInfoByKind(object_info):
    """Format a single object_info (based on its 'kind' attribute)."""
    kind = BigqueryClient._KindToName(object_info.get('kind'))
    if kind == 'job':
      return BigqueryClient.FormatJobInfo(object_info)
    elif kind == 'project':
      return BigqueryClient.FormatProjectInfo(object_info)
    elif kind == 'dataset':
      return BigqueryClient.FormatDatasetInfo(object_info)
    elif kind == 'table':
      return BigqueryClient.FormatTableInfo(object_info)
    else:
      raise ValueError('Unknown object type: %s' % (kind,))

  @staticmethod
  def FormatJobInfo(job_info):
    """Prepare a job_info for printing.

    Arguments:
      job_info: Job dict to format.

    Returns:
      The new job_info.
    """
    result = job_info.copy()
    reference = BigqueryClient.ConstructObjectReference(result)
    result.update(dict(reference))
    if 'startTime' in result.get('statistics', {}):
      start = int(result['statistics']['startTime']) / 1000
      if 'endTime' in result['statistics']:
        duration_seconds = int(result['statistics']['endTime']) / 1000 - start
        result['Duration'] = str(datetime.timedelta(seconds=duration_seconds))
      result['Start Time'] = BigqueryClient.FormatTime(start)
    result['Job Type'] = BigqueryClient.GetJobTypeName(result)
    result['State'] = result['status']['state']
    if result['State'] == 'DONE':
      try:
        BigqueryClient.RaiseIfJobError(result)
        result['State'] = 'SUCCESS'
      except BigqueryError:
        result['State'] = 'FAILURE'
    if 'totalBytesProcessed' in result.get('statistics', {}):
      result['Bytes Processed'] = result['statistics']['totalBytesProcessed']
    return result

  @staticmethod
  def FormatProjectInfo(project_info):
    """Prepare a project_info for printing.

    Arguments:
      project_info: Project dict to format.

    Returns:
      The new project_info.
    """
    result = project_info.copy()
    reference = BigqueryClient.ConstructObjectReference(result)
    result.update(dict(reference))
    return result

  @staticmethod
  def FormatDatasetInfo(dataset_info):
    """Prepare a dataset_info for printing.

    Arguments:
      dataset_info: Dataset dict to format.

    Returns:
      The new dataset_info.
    """
    result = dataset_info.copy()
    reference = BigqueryClient.ConstructObjectReference(result)
    result.update(dict(reference))
    if 'lastModifiedTime' in result:
      result['Last modified'] = BigqueryClient.FormatTime(
          int(result['lastModifiedTime']) / 1000)
    if 'access' in result:
      result['ACLs'] = BigqueryClient.FormatAcl(result['access'])
    return result

  @staticmethod
  def FormatTableInfo(table_info):
    """Prepare a table_info for printing.

    Arguments:
      table_info: Table dict to format.

    Returns:
      The new table_info.
    """
    result = table_info.copy()
    reference = BigqueryClient.ConstructObjectReference(result)
    result.update(dict(reference))
    if 'lastModifiedTime' in result:
      result['Last modified'] = BigqueryClient.FormatTime(
          int(result['lastModifiedTime']) / 1000)
    if 'schema' in result:
      result['Schema'] = BigqueryClient.FormatSchema(result['schema'])
    if 'numBytes' in result:
      result['Total Bytes'] = result['numBytes']
    if 'numRows' in result:
      result['Total Rows'] = result['numRows']
    if 'expirationTime' in result:
      result['Expiration'] = BigqueryClient.FormatTime(
          int(result['expirationTime']) / 1000)
    if 'type' in result:
      result['Type'] = result['type']
      if result['type'] == 'VIEW':
        result['Total Bytes'] = '(view)'
        result['Total Rows'] = '(view)'
      if 'view' in result:
        result['Query'] = result['view']['query']
    return result


  @staticmethod
  def ConstructObjectReference(object_info):
    """Construct a Reference from a server response."""
    if 'kind' in object_info:
      typename = BigqueryClient._KindToName(object_info['kind'])
      lower_camel = typename + 'Reference'
      if lower_camel not in object_info:
        raise ValueError('Cannot find %s in object of type %s: %s' % (
            lower_camel, typename, object_info))
    else:
      keys = [k for k in object_info if k.endswith('Reference')]
      if len(keys) != 1:
        raise ValueError('Expected one Reference, found %s: %s' % (
            len(keys), keys))
      lower_camel = keys[0]
    upper_camel = lower_camel[0].upper() + lower_camel[1:]
    reference_type = getattr(ApiClientHelper, upper_camel, None)
    if reference_type is None:
      raise ValueError('Unknown reference type: %s' % (typename,))
    return reference_type.Create(**object_info[lower_camel])

  @staticmethod
  def ConstructObjectInfo(reference):
    """Construct an Object from an ObjectReference."""
    typename = reference.__class__.__name__
    lower_camel = typename[0].lower() + typename[1:]
    return {lower_camel: dict(reference)}

  def _PrepareListRequest(self, reference, max_results=None, page_token=None):
    request = dict(reference)
    if max_results is not None:
      request['maxResults'] = max_results
    if page_token is not None:
      request['pageToken'] = page_token
    return request

  def _NormalizeProjectReference(self, reference):
    if reference is None:
      try:
        return self.GetProjectReference()
      except BigqueryClientError:
        raise BigqueryClientError(
            'Project reference or a default project is required')
    return reference

  def ListJobRefs(self, **kwds):
    return map(  # pylint: disable=g-long-lambda
        BigqueryClient.ConstructObjectReference, self.ListJobs(**kwds))

  def ListJobs(self, reference=None,
               max_results=None, page_token=None,
               state_filter=None, all_users=None):
    """Return a list of jobs.

    Args:
      reference: The ProjectReference to list jobs for.
      max_results: The maximum number of jobs to return.
      page_token: Current page token (optional).
      state_filter: A single state filter or a list of filters to
        apply. If not specified, no filtering is applied.
      all_users: Whether to list jobs for all users of the project. Requesting
        user must be an owner of the project to list all jobs.

    Returns:
      A list of jobs.
    """
    reference = self._NormalizeProjectReference(reference)
    _Typecheck(reference, ApiClientHelper.ProjectReference, method='ListJobs')
    if max_results > _MAX_RESULTS:
      max_results = _MAX_RESULTS
    request = self._PrepareListRequest(reference, max_results, page_token)
    if state_filter is not None:
      # The apiclient wants enum values as lowercase strings.
      if isinstance(state_filter, basestring):
        state_filter = state_filter.lower()
      else:
        state_filter = [s.lower() for s in state_filter]
    _ApplyParameters(request, projection='full',
                     state_filter=state_filter, all_users=all_users)
    result = self.apiclient.jobs().list(**request).execute()
    results = result.get('jobs', [])
    if max_results is not None:
      while 'nextPageToken' in result and len(results) < max_results:
        request = self._PrepareListRequest(
            reference, max_results - len(results), result['nextPageToken'])
        _ApplyParameters(request, projection='full',
                         state_filter=state_filter, all_users=all_users)
        result = self.apiclient.jobs().list(**request).execute()
        results.extend(result.get('jobs', []))
    return results

  def ListProjectRefs(self, **kwds):
    """List the project references this user has access to."""
    return map(  # pylint: disable=g-long-lambda
        BigqueryClient.ConstructObjectReference, self.ListProjects(**kwds))

  def ListProjects(self, max_results=None, page_token=None):
    """List the projects this user has access to."""
    request = self._PrepareListRequest({}, max_results, page_token)
    result = self.apiclient.projects().list(**request).execute()
    return result.get('projects', [])

  def ListDatasetRefs(self, **kwds):
    return map(  # pylint: disable=g-long-lambda
        BigqueryClient.ConstructObjectReference, self.ListDatasets(**kwds))

  def ListDatasets(self, reference=None, max_results=None, page_token=None,
                   list_all=None):
    """List the datasets associated with this reference."""
    reference = self._NormalizeProjectReference(reference)
    _Typecheck(reference, ApiClientHelper.ProjectReference,
               method='ListDatasets')
    request = self._PrepareListRequest(reference, max_results, page_token)
    if list_all is not None:
      request['all'] = list_all
    result = self.apiclient.datasets().list(**request).execute()
    results = result.get('datasets', [])
    if max_results is not None:
      while 'nextPageToken' in result and len(results) < max_results:
        request = self._PrepareListRequest(
            reference, max_results - len(results), result['nextPageToken'])
        if list_all is not None:
          request['all'] = list_all
        result = self.apiclient.datasets().list(**request).execute()
        results.extend(result.get('datasets', []))
    return results

  def ListTableRefs(self, **kwds):
    return map(  # pylint: disable=g-long-lambda
        BigqueryClient.ConstructObjectReference, self.ListTables(**kwds))

  def ListTables(self, reference, max_results=None, page_token=None):
    """List the tables associated with this reference."""
    _Typecheck(reference, ApiClientHelper.DatasetReference,
               method='ListTables')
    request = self._PrepareListRequest(reference, max_results, page_token)
    result = self.apiclient.tables().list(**request).execute()
    results = result.get('tables', [])
    if max_results is not None:
      while 'nextPageToken' in result and len(results) < max_results:
        request = self._PrepareListRequest(
            reference, max_results - len(results), result['nextPageToken'])
        result = self.apiclient.tables().list(**request).execute()
        results.extend(result.get('tables', []))
    return results


  #################################
  ## Table and dataset management
  #################################

  def CopyTable(self, source_references, dest_reference,
                create_disposition=None, write_disposition=None,
                ignore_already_exists=False, **kwds):
    """Copies a table.

    Args:
      source_references: TableReferences of source tables.
      dest_reference: TableReference of destination table.
      create_disposition: Optional. Specifies the create_disposition for
          the dest_reference.
      write_disposition: Optional. Specifies the write_disposition for
          the dest_reference.
      ignore_already_exists: Whether to ignore "already exists" errors.
      **kwds: Passed on to ExecuteJob.

    Returns:
      The job description, or None for ignored errors.

    Raises:
      BigqueryDuplicateError: when write_disposition 'WRITE_EMPTY' is
        specified and the dest_reference table already exists.
    """
    for src_ref in source_references:
      _Typecheck(src_ref, ApiClientHelper.TableReference,
                 method='CopyTable')
    _Typecheck(dest_reference, ApiClientHelper.TableReference,
               method='CopyTable')
    copy_config = {
        'destinationTable': dict(dest_reference),
        'sourceTables': [dict(src_ref) for src_ref in source_references],
        }
    _ApplyParameters(copy_config, create_disposition=create_disposition,
                     write_disposition=write_disposition)
    try:
      return self.ExecuteJob({'copy': copy_config}, **kwds)
    except BigqueryDuplicateError, e:
      if ignore_already_exists:
        return None
      raise e

  def DatasetExists(self, reference):
    _Typecheck(reference, ApiClientHelper.DatasetReference,
               method='DatasetExists')
    try:
      self.apiclient.datasets().get(**dict(reference)).execute()
      return True
    except BigqueryNotFoundError:
      return False

  def TableExists(self, reference):
    _Typecheck(reference, ApiClientHelper.TableReference, method='TableExists')
    try:
      self.apiclient.tables().get(**dict(reference)).execute()
      return True
    except BigqueryNotFoundError:
      return False


  def CreateDataset(self, reference, ignore_existing=False, description=None,
                    friendly_name=None, acl=None):
    """Create a dataset corresponding to DatasetReference.

    Args:
      reference: the DatasetReference to create.
      ignore_existing: (boolean, default False) If False, raise
        an exception if the dataset already exists.
      description: an optional dataset description.
      friendly_name: an optional friendly name for the dataset.
      acl: an optional ACL for the dataset, as a list of dicts.

    Raises:
      TypeError: if reference is not a DatasetReference.
      BigqueryDuplicateError: if reference exists and ignore_existing
         is False.
    """
    _Typecheck(reference, ApiClientHelper.DatasetReference,
               method='CreateDataset')

    body = BigqueryClient.ConstructObjectInfo(reference)
    if friendly_name is not None:
      body['friendlyName'] = friendly_name
    if description is not None:
      body['description'] = description
    if acl is not None:
      body['access'] = acl
    try:
      self.apiclient.datasets().insert(
          body=body,
          **dict(reference.GetProjectReference())).execute()
    except BigqueryDuplicateError:
      if not ignore_existing:
        raise

  def CreateTable(self, reference, ignore_existing=False, schema=None,
                  description=None, friendly_name=None, expiration=None,
                  view_query=None):
    """Create a table corresponding to TableReference.

    Args:
      reference: the TableReference to create.
      ignore_existing: (boolean, default False) If False, raise
        an exception if the dataset already exists.
      schema: an optional schema for tables.
      description: an optional description for tables or views.
      friendly_name: an optional friendly name for the table.
      expiration: optional expiration time in milliseconds since the epoch for
        tables or views.
      view_query: an optional Sql query for views.

    Raises:
      TypeError: if reference is not a TableReference.
      BigqueryDuplicateError: if reference exists and ignore_existing
        is False.
    """
    _Typecheck(reference, ApiClientHelper.TableReference, method='CreateTable')

    try:
      body = BigqueryClient.ConstructObjectInfo(reference)
      if schema:
        body['schema'] = {'fields': schema}
      if friendly_name is not None:
        body['friendlyName'] = friendly_name
      if description is not None:
        body['description'] = description
      if expiration is not None:
        body['expirationTime'] = expiration
      if view_query is not None:
        body['view'] = {'query': view_query}
      self.apiclient.tables().insert(
          body=body,
          **dict(reference.GetDatasetReference())).execute()
    except BigqueryDuplicateError:
      if not ignore_existing:
        raise


  def UpdateTable(self, reference, schema=None,
                  description=None, friendly_name=None, expiration=None,
                  view_query=None):
    """Updates a table.

    Args:
      reference: the TableReference to update.
      schema: an optional schema for tables.
      description: an optional description for tables or views.
      friendly_name: an optional friendly name for the table.
      expiration: optional expiration time in milliseconds since the epoch for
        tables or views.
      view_query: an optional Sql query to update a view.

    Raises:
      TypeError: if reference is not a TableReference.
    """
    _Typecheck(reference, ApiClientHelper.TableReference, method='UpdateTable')

    body = BigqueryClient.ConstructObjectInfo(reference)
    if schema:
      body['schema'] = {'fields': schema}
    if friendly_name is not None:
      body['friendlyName'] = friendly_name
    if description is not None:
      body['description'] = description
    if expiration is not None:
      body['expirationTime'] = expiration
    if view_query is not None:
      body['view'] = {'query': view_query}

    self.apiclient.tables().patch(body=body, **dict(reference)).execute()

  def UpdateDataset(self, reference,
                    description=None, friendly_name=None, acl=None):
    """Updates a dataset.

    Args:
      reference: the DatasetReference to update.
      description: an optional dataset description.
      friendly_name: an optional friendly name for the dataset.
      acl: an optional ACL for the dataset, as a list of dicts.

    Raises:
      TypeError: if reference is not a DatasetReference.
    """
    _Typecheck(reference, ApiClientHelper.DatasetReference,
               method='UpdateDataset')

    body = BigqueryClient.ConstructObjectInfo(reference)
    if friendly_name is not None:
      body['friendlyName'] = friendly_name
    if description is not None:
      body['description'] = description
    if acl is not None:
      body['access'] = acl

    self.apiclient.datasets().patch(body=body, **dict(reference)).execute()

  def DeleteDataset(self, reference, ignore_not_found=False,
                    delete_contents=None):
    """Deletes DatasetReference reference.

    Args:
      reference: the DatasetReference to delete.
      ignore_not_found: Whether to ignore "not found" errors.
      delete_contents: [Boolean] Whether to delete the contents of
        non-empty datasets. If not specified and the dataset has
        tables in it, the delete will fail. If not specified,
        the server default applies.

    Raises:
      TypeError: if reference is not a DatasetReference.
      BigqueryNotFoundError: if reference does not exist and
        ignore_not_found is False.
    """
    _Typecheck(reference, ApiClientHelper.DatasetReference,
               method='DeleteDataset')

    args = dict(reference)
    if delete_contents is not None:
      args['deleteContents'] = delete_contents
    try:
      self.apiclient.datasets().delete(**args).execute()
    except BigqueryNotFoundError:
      if not ignore_not_found:
        raise

  def DeleteTable(self, reference, ignore_not_found=False):
    """Deletes TableReference reference.

    Args:
      reference: the TableReference to delete.
      ignore_not_found: Whether to ignore "not found" errors.

    Raises:
      TypeError: if reference is not a TableReference.
      BigqueryNotFoundError: if reference does not exist and
        ignore_not_found is False.
    """
    _Typecheck(reference, ApiClientHelper.TableReference, method='DeleteTable')
    try:
      self.apiclient.tables().delete(**dict(reference)).execute()
    except BigqueryNotFoundError:
      if not ignore_not_found:
        raise


  #################################
  ## Job control
  #################################

  def StartJob(self, configuration,
               project_id=None, upload_file=None, job_id=None):
    """Start a job with the given configuration.

    Args:
      configuration: The configuration for a job.
      project_id: The project_id to run the job under. If None,
        self.project_id is used.
      upload_file: A file to include as a media upload to this request.
        Only valid on job requests that expect a media upload file.
      job_id: A unique job_id to use for this job. If a
        JobIdGenerator, a job id will be generated from the job configuration.
        If None, a unique job_id will be created for this request.

    Returns:
      The job resource returned from the insert job request. If there is an
      error, the jobReference field will still be filled out with the job
      reference used in the request.

    Raises:
      BigqueryClientConfigurationError: if project_id and
        self.project_id are None.
    """
    project_id = project_id or self.project_id
    if not project_id:
      raise BigqueryClientConfigurationError(
          'Cannot start a job without a project id.')
    configuration = configuration.copy()
    if self.job_property:
      configuration['properties'] = dict(
          prop.partition('=')[0::2] for prop in self.job_property)
    job_request = {'configuration': configuration}

    # Use the default job id generator if no job id was supplied.
    job_id = job_id or self.job_id_generator

    if isinstance(job_id, JobIdGenerator):
      job_id = job_id.Generate(configuration)

    if job_id is not None:
      job_reference = {'jobId': job_id, 'projectId': project_id}
      job_request['jobReference'] = job_reference
    media_upload = ''
    if upload_file:
      resumable = True
      media_upload = http_request.MediaFileUpload(
          filename=upload_file, mimetype='application/octet-stream',
          resumable=resumable)
    result = self.apiclient.jobs().insert(
        body=job_request, media_body=media_upload,
        projectId=project_id).execute()
    return result

  def _StartQueryRpc(self,
                     query,
                     dry_run=None,
                     use_cache=None,
                     preserve_nulls=None,
                     max_results=None,
                     timeout_ms=None,
                     min_completion_ratio=None,
                     project_id=None,
                     **kwds):
    """Executes the given query using the rpc-style query api.

    Args:
      query: Query to execute.
      dry_run: Optional. Indicates whether the query will only be validated and
          return processing statistics instead of actually running.
      use_cache: Optional. Whether to use the query cache.
          Caching is best-effort only and you should not make
          assumptions about whether or how long a query result will be cached.
      preserve_nulls: Optional. Indicates whether to preserve nulls in input
          data. Temporary flag; will be removed in a future version.
      max_results: Maximum number of results to return.
      timeout_ms: Timeout, in milliseconds, for the call to query().
      min_completion_ratio: Optional. Specifies the the minimum fraction of
          data that must be scanned before a query returns. This value should be
          between 0.0 and 1.0 inclusive.
      project_id: Project id to use.
      **kwds: Extra keyword arguments passed directly to jobs.Query().

    Returns:
      The query response.

    Raises:
      BigqueryClientConfigurationError: if project_id and
        self.project_id are None.
    """
    project_id = project_id or self.project_id
    if not project_id:
      raise BigqueryClientConfigurationError(
          'Cannot run a query without a project id.')
    request = {'query': query}
    if self.dataset_id:
      request['defaultDataset'] = dict(self.GetDatasetReference())
    _ApplyParameters(
        request,
        preserve_nulls=preserve_nulls,
        use_query_cache=use_cache,
        timeout_ms=timeout_ms,
        max_results=max_results,
        min_completion_ratio=min_completion_ratio)
    _ApplyParameters(request, dry_run=dry_run)
    return self.apiclient.jobs().query(
        body=request, projectId=project_id, **kwds).execute()

  def GetQueryResults(self, job_id=None, project_id=None,
                      max_results=None, timeout_ms=None):
    """Waits for a query to complete, once.

    Args:
      job_id: The job id of the query job that we are waiting to complete.
      project_id: The project id of the query job.
      max_results: The maximum number of results.
      timeout_ms: The number of milliseconds to wait for the query to complete.

    Returns:
      The getQueryResults() result.

    Raises:
      BigqueryClientConfigurationError: if project_id and
        self.project_id are None.
    """
    project_id = project_id or self.project_id
    if not project_id:
      raise BigqueryClientConfigurationError(
          'Cannot get query results without a project id.')
    kwds = {}
    _ApplyParameters(kwds,
                     job_id=job_id,
                     project_id=project_id,
                     timeout_ms=timeout_ms,
                     max_results=max_results)
    return self.apiclient.jobs().getQueryResults(**kwds).execute()

  def RunJobSynchronously(self, configuration, project_id=None,
                          upload_file=None, job_id=None):
    result = self.StartJob(configuration, project_id=project_id,
                           upload_file=upload_file, job_id=job_id)
    if result['status']['state'] != 'DONE':
      job_reference = BigqueryClient.ConstructObjectReference(result)
      result = self.WaitJob(job_reference)
    return self.RaiseIfJobError(result)

  def ExecuteJob(self, configuration, sync=None,
                 project_id=None, upload_file=None, job_id=None):
    """Execute a job, possibly waiting for results."""
    if sync is None:
      sync = self.sync

    if sync:
      job = self.RunJobSynchronously(
          configuration, project_id=project_id, upload_file=upload_file,
          job_id=job_id)
    else:
      job = self.StartJob(
          configuration, project_id=project_id, upload_file=upload_file,
          job_id=job_id)
      self.RaiseIfJobError(job)
    return job

  class WaitPrinter(object):
    """Base class that defines the WaitPrinter interface."""

    def Print(self, job_id, wait_time, status):
      """Prints status for the current job we are waiting on.

      Args:
        job_id: the identifier for this job.
        wait_time: the number of seconds we have been waiting so far.
        status: the status of the job we are waiting for.
      """
      raise NotImplementedError('Subclass must implement Print')

    def Done(self):
      """Waiting is done and no more Print calls will be made.

      This function should handle the case of Print not being called.
      """
      raise NotImplementedError('Subclass must implement Done')

  class WaitPrinterHelper(WaitPrinter):
    """A Done implementation that prints based off a property."""

    print_on_done = False

    def Done(self):
      if self.print_on_done:
        print

  class QuietWaitPrinter(WaitPrinterHelper):
    """A WaitPrinter that prints nothing."""

    def Print(self, unused_job_id, unused_wait_time, unused_status):
      pass

  class VerboseWaitPrinter(WaitPrinterHelper):
    """A WaitPrinter that prints every update."""

    def Print(self, job_id, wait_time, status):
      self.print_on_done = True
      print '\rWaiting on %s ... (%ds) Current status: %-7s' % (
          job_id, wait_time, status),
      sys.stderr.flush()

  class TransitionWaitPrinter(VerboseWaitPrinter):
    """A WaitPrinter that only prints status change updates."""

    _previous_status = None

    def Print(self, job_id, wait_time, status):
      if status != self._previous_status:
        self._previous_status = status
        super(BigqueryClient.TransitionWaitPrinter, self).Print(
            job_id, wait_time, status)

  def WaitJob(self, job_reference, status='DONE',
              wait=sys.maxint, wait_printer_factory=None):
    """Poll for a job to run until it reaches the requested status.

    Arguments:
      job_reference: JobReference to poll.
      status: (optional, default 'DONE') Desired job status.
      wait: (optional, default maxint) Max wait time.
      wait_printer_factory: (optional, defaults to
        self.wait_printer_factory) Returns a subclass of WaitPrinter
        that will be called after each job poll.

    Returns:
      The job object returned by the final status call.

    Raises:
      StopIteration: If polling does not reach the desired state before
        timing out.
      ValueError: If given an invalid wait value.
    """
    _Typecheck(job_reference, ApiClientHelper.JobReference, method='WaitJob')
    start_time = time.time()
    job = None
    if wait_printer_factory:
      printer = wait_printer_factory()
    else:
      printer = self.wait_printer_factory()

    # This is a first pass at wait logic: we ping at 1s intervals a few
    # times, then increase to max(3, max_wait), and then keep waiting
    # that long until we've run out of time.
    waits = itertools.chain(
        itertools.repeat(1, 8),
        xrange(2, 30, 3),
        itertools.repeat(30))
    current_wait = 0
    current_status = 'UNKNOWN'
    while current_wait <= wait:
      try:
        done, job = self.PollJob(job_reference, status=status, wait=wait)
        current_status = job['status']['state']
        if done:
          printer.Print(job_reference.jobId, current_wait, current_status)
          break
      except BigqueryCommunicationError, e:
        # Communication errors while waiting on a job are okay.
        logging.warning('Transient error during job status check: %s', e)
      except BigqueryBackendError, e:
        # Temporary server errors while waiting on a job are okay.
        logging.warning('Transient error during job status check: %s', e)
      for _ in xrange(waits.next()):
        current_wait = time.time() - start_time
        printer.Print(job_reference.jobId, current_wait, current_status)
        time.sleep(1)
    else:
      raise StopIteration(
          'Wait timed out. Operation not finished, in state %s' % (
              current_status,))
    printer.Done()
    return job

  def PollJob(self, job_reference, status='DONE', wait=0):
    """Poll a job once for a specific status.

    Arguments:
      job_reference: JobReference to poll.
      status: (optional, default 'DONE') Desired job status.
      wait: (optional, default 0) Max server-side wait time for one poll call.

    Returns:
      Tuple (in_state, job) where in_state is True if job is
      in the desired state.

    Raises:
      ValueError: If given an invalid wait value.
    """
    _Typecheck(job_reference, ApiClientHelper.JobReference, method='PollJob')
    wait = BigqueryClient.NormalizeWait(wait)
    job = self.apiclient.jobs().get(**dict(job_reference)).execute()
    current = job['status']['state']
    return (current == status, job)

  #################################
  ## Wrappers for job types
  #################################

  def RunQuery(self, **kwds):
    """Run a query job synchronously, and return the result.

    Args:
      **kwds: Passed on to self.Query.

    Returns:
      A tuple where the first item is the list of fields and the
      second item a list of rows.
    """
    new_kwds = dict(kwds)
    new_kwds['sync'] = True
    job = self.Query(**new_kwds)

    return self.ReadSchemaAndJobRows(job['jobReference'])

  def RunQueryRpc(self,
                  query,
                  dry_run=None,
                  use_cache=None,
                  preserve_nulls=None,
                  max_results=None,
                  wait=sys.maxint,
                  min_completion_ratio=None,
                  wait_printer_factory=None,
                  max_single_wait=None,
                  **kwds):
    """Executes the given query using the rpc-style query api.

    Args:
      query: Query to execute.
      dry_run: Optional. Indicates whether the query will only be validated and
          return processing statistics instead of actually running.
      use_cache: Optional. Whether to use the query cache.
          Caching is best-effort only and you should not make
          assumptions about whether or how long a query result will be cached.
      preserve_nulls: Optional. Indicates whether to preserve nulls in input
          data. Temporary flag; will be removed in a future version.
      max_results: Optional. Maximum number of results to return.
      wait: (optional, default maxint) Max wait time in seconds.
      min_completion_ratio: Optional. Specifies the the minimum fraction of
          data that must be scanned before a query returns. This value should be
          between 0.0 and 1.0 inclusive.
      wait_printer_factory: (optional, defaults to
          self.wait_printer_factory) Returns a subclass of WaitPrinter
          that will be called after each job poll.
      max_single_wait: Optional. Maximum number of seconds to wait for each call
          to query() / getQueryResults().
      **kwds: Passed directly to self.ExecuteSyncQuery.

    Raises:
      BigqueryClientError: if no query is provided.
      StopIteration: if the query does not complete within wait seconds.

    Returns:
      The a tuple containing the schema fields and list of results of the query.
    """
    if not self.sync:
      raise BigqueryClientError('Running RPC-style query asynchronously is '
                                'not supported')
    if not query:
      raise BigqueryClientError('No query string provided')

    if wait_printer_factory:
      printer = wait_printer_factory()
    else:
      printer = self.wait_printer_factory()

    start_time = time.time()
    elapsed_time = 0
    job_reference = None
    current_wait_ms = None
    while True:
      try:
        elapsed_time = 0 if job_reference is None else time.time() - start_time
        remaining_time = wait - elapsed_time
        if max_single_wait is not None:
          # Compute the current wait, being careful about overflow, since
          # remaining_time may be counting down from sys.maxint.
          current_wait_ms = int(min(remaining_time, max_single_wait) * 1000)
          if current_wait_ms < 0:
            current_wait_ms = sys.maxint
        if remaining_time < 0:
          raise StopIteration('Wait timed out. Query not finished.')
        if job_reference is None:
          # We haven't yet run a successful Query(), so we don't
          # have a job id to check on.
          result = self._StartQueryRpc(
              query=query,
              preserve_nulls=preserve_nulls,
              use_cache=use_cache,
              dry_run=dry_run,
              min_completion_ratio=min_completion_ratio,
              timeout_ms=current_wait_ms,
              max_results=0,
              **kwds)
          job_reference = ApiClientHelper.JobReference.Create(
              **result['jobReference'])
        else:
          # The query/getQueryResults methods do not return the job state,
          # so we just print 'RUNNING' while we are actively waiting.
          printer.Print(job_reference.jobId, elapsed_time, 'RUNNING')
          result = self.GetQueryResults(
              job_reference.jobId,
              max_results=0,
              timeout_ms=current_wait_ms)
        if result['jobComplete']:
          return self.ReadSchemaAndJobRows(dict(job_reference),
                                           start_row=0,
                                           max_rows=max_results)
      except BigqueryCommunicationError, e:
        # Communication errors while waiting on a job are okay.
        logging.warning('Transient error during query: %s', e)
      except BigqueryBackendError, e:
        # Temporary server errors while waiting on a job are okay.
        logging.warning('Transient error during query: %s', e)

  def Query(self, query,
            destination_table=None,
            create_disposition=None,
            write_disposition=None,
            priority=None,
            preserve_nulls=None,
            allow_large_results=None,
            dry_run=None,
            use_cache=None,
            min_completion_ratio=None,
            flatten_results=None,
            **kwds):
    # pylint: disable=g-doc-args
    """Execute the given query, returning the created job.

    The job will execute synchronously if sync=True is provided as an
    argument or if self.sync is true.

    Args:
      query: Query to execute.
      destination_table: (default None) If provided, send the results to the
          given table.
      create_disposition: Optional. Specifies the create_disposition for
          the destination_table.
      write_disposition: Optional. Specifies the write_disposition for
          the destination_table.
      priority: Optional. Priority to run the query with. Either
          'INTERACTIVE' (default) or 'BATCH'.
      preserve_nulls: Optional. Indicates whether to preserve nulls in input
          data. Temporary flag; will be removed in a future version.
      allow_large_results: Enables larger destination table sizes.
      dry_run: Optional. Indicates whether the query will only be validated and
          return processing statistics instead of actually running.
      use_cache: Optional. Whether to use the query cache. If create_disposition
          is CREATE_NEVER, will only run the query if the result is already
          cached. Caching is best-effort only and you should not make
          assumptions about whether or how long a query result will be cached.
      min_completion_ratio: Optional. Specifies the the minimum fraction of
          data that must be scanned before a query returns. This value should be
          between 0.0 and 1.0 inclusive.
      flatten_results: Whether to flatten nested and repeated fields in the
        result schema. If not set, the default behavior is to flatten.
      **kwds: Passed on to self.ExecuteJob.

    Raises:
      BigqueryClientError: if no query is provided.

    Returns:
      The resulting job info.
    """
    if not query:
      raise BigqueryClientError('No query string provided')
    query_config = {'query': query}
    if self.dataset_id:
      query_config['defaultDataset'] = dict(self.GetDatasetReference())
    if destination_table:
      try:
        reference = self.GetTableReference(destination_table)
      except BigqueryError, e:
        raise BigqueryError('Invalid value %s for destination_table: %s' % (
            destination_table, e))
      query_config['destinationTable'] = dict(reference)
    _ApplyParameters(
        query_config,
        allow_large_results=allow_large_results,
        create_disposition=create_disposition,
        preserve_nulls=preserve_nulls,
        priority=priority,
        write_disposition=write_disposition,
        use_query_cache=use_cache,
        flatten_results=flatten_results,
        min_completion_ratio=min_completion_ratio)
    request = {'query': query_config}
    _ApplyParameters(request, dry_run=dry_run)
    return self.ExecuteJob(request, **kwds)

  def Load(self, destination_table_reference, source,
           schema=None, create_disposition=None, write_disposition=None,
           field_delimiter=None, skip_leading_rows=None, encoding=None,
           quote=None, max_bad_records=None, allow_quoted_newlines=None,
           source_format=None, allow_jagged_rows=None,
           ignore_unknown_values=None,
           **kwds):
    """Load the given data into BigQuery.

    The job will execute synchronously if sync=True is provided as an
    argument or if self.sync is true.

    Args:
      destination_table_reference: TableReference to load data into.
      source: String specifying source data to load.
      schema: (default None) Schema of the created table. (Can be left blank
          for append operations.)
      create_disposition: Optional. Specifies the create_disposition for
          the destination_table_reference.
      write_disposition: Optional. Specifies the write_disposition for
          the destination_table_reference.
      field_delimiter: Optional. Specifies the single byte field delimiter.
      skip_leading_rows: Optional. Number of rows of initial data to skip.
      encoding: Optional. Specifies character encoding of the input data.
          May be "UTF-8" or "ISO-8859-1". Defaults to UTF-8 if not specified.
      quote: Optional. Quote character to use. Default is '"'. Note that
          quoting is done on the raw binary data before encoding is applied.
      max_bad_records: Optional. Maximum number of bad records that should
          be ignored before the entire job is aborted.
      allow_quoted_newlines: Optional. Whether to allow quoted newlines in CSV
          import data.
      source_format: Optional. Format of source data. May be "CSV",
          "DATASTORE_BACKUP", or "NEWLINE_DELIMITED_JSON".
      allow_jagged_rows: Optional. Whether to allow missing trailing optional
          columns in CSV import data.
      ignore_unknown_values: Optional. Whether to allow extra, unrecognized
          values in CSV or JSON data.
      **kwds: Passed on to self.ExecuteJob.

    Returns:
      The resulting job info.
    """
    _Typecheck(destination_table_reference, ApiClientHelper.TableReference)
    load_config = {'destinationTable': dict(destination_table_reference)}
    sources = BigqueryClient.ProcessSources(source)
    if sources[0].startswith('gs://'):
      load_config['sourceUris'] = sources
      upload_file = None
    else:
      upload_file = sources[0]
    if schema is not None:
      load_config['schema'] = {'fields': BigqueryClient.ReadSchema(schema)}
    _ApplyParameters(
        load_config, create_disposition=create_disposition,
        write_disposition=write_disposition, field_delimiter=field_delimiter,
        skip_leading_rows=skip_leading_rows, encoding=encoding,
        quote=quote, max_bad_records=max_bad_records,
        source_format=source_format,
        allow_quoted_newlines=allow_quoted_newlines,
        allow_jagged_rows=allow_jagged_rows,
        ignore_unknown_values=ignore_unknown_values)
    return self.ExecuteJob(configuration={'load': load_config},
                           upload_file=upload_file, **kwds)

  def Extract(self, source_table, destination_uris,
              print_header=None, field_delimiter=None,
              destination_format=None, compression=None,
              **kwds):
    """Extract the given table from BigQuery.

    The job will execute synchronously if sync=True is provided as an
    argument or if self.sync is true.

    Args:
      source_table: TableReference to read data from.
      destination_uris: String specifying one or more destination locations,
         separated by commas.
      print_header: Optional. Whether to print out a header row in the results.
      field_delimiter: Optional. Specifies the single byte field delimiter.
      destination_format: Optional. Format to extract table to. May be "CSV",
         "AVRO", or "NEWLINE_DELIMITED_JSON".
      compression: Optional. The compression type to use for exported files.
        Possible values include "GZIP" and "NONE". The default value is NONE.
      **kwds: Passed on to self.ExecuteJob.

    Returns:
      The resulting job info.

    Raises:
      BigqueryClientError: if required parameters are invalid.
    """
    _Typecheck(source_table, ApiClientHelper.TableReference)
    uris = destination_uris.split(',')
    for uri in uris:
      if not uri.startswith('gs://'):
        raise BigqueryClientError(
            'Illegal URI: {}. Extract URI must start with "gs://".'.format(uri))
    extract_config = {'sourceTable': dict(source_table)}
    _ApplyParameters(
        extract_config, destination_uris=uris,
        destination_format=destination_format,
        print_header=print_header, field_delimiter=field_delimiter,
        compression=compression)
    return self.ExecuteJob(configuration={'extract': extract_config}, **kwds)


class _TableReader(object):
  """Base class that defines the TableReader interface.

  _TableReaders provide a way to read paginated rows and schemas from a table.
  """

  def ReadRows(self, start_row=0, max_rows=None):
    """Read ad most max_rows rows from a table.

    Args:
      start_row: first row to return.
      max_rows: maximum number of rows to return.

    Raises:
      BigqueryInterfaceError: when bigquery returns something unexpected.

    Returns:
      list of rows, each of which is a list of field values.
    """
    (_, rows) = self.ReadSchemaAndRows(start_row=start_row, max_rows=max_rows)
    return rows

  def ReadSchemaAndRows(self, start_row, max_rows):
    """Read at most max_rows rows from a table and the schema.

    Args:
      start_row: first row to read.
      max_rows: maximum number of rows to return.

    Raises:
      BigqueryInterfaceError: when bigquery returns something unexpected.
      ValueError: when start_row is None.
      ValueError: when max_rows is None.

    Returns:
      A tuple where the first item is the list of fields and the
      second item a list of rows.
    """
    if start_row is None:
      raise ValueError('start_row is required')
    if max_rows is None:
      raise ValueError('max_rows is required')
    page_token = None
    rows = []
    schema = {}
    while len(rows) < max_rows:
      rows_to_read = max_rows - len(rows)
      if self.max_rows_per_request:
        rows_to_read = min(self.max_rows_per_request, rows_to_read)
      (more_rows, page_token, current_schema) = self._ReadOnePage(
          None if page_token else start_row,
          max_rows=None if page_token else rows_to_read,
          page_token=page_token)
      if not schema and current_schema:
        schema = current_schema.get('fields', [])
      for row in more_rows:
        rows.append(self._ConvertFromFV(schema, row))
        start_row += 1
      if not page_token or not more_rows:
        break
    return (schema, rows)

  def _ConvertFromFV(self, schema, row):
    """Converts from FV format to possibly nested lists of values."""
    if not row:
      return None
    values = [entry.get('v', '') for entry in row.get('f', [])]
    result = []
    for field, v in zip(schema, values):
      if field['type'].upper() == 'RECORD':
        # Nested field.
        subfields = field.get('fields', [])
        if field.get('mode', 'NULLABLE').upper() == 'REPEATED':
          # Repeated and nested. Convert the array of v's of FV's.
          result.append([self._ConvertFromFV(
              subfields, subvalue.get('v', '')) for subvalue in v])
        else:
          # Nested non-repeated field. Convert the nested f from FV.
          result.append(self._ConvertFromFV(subfields, v))
      elif field.get('mode', 'NULLABLE').upper() == 'REPEATED':
        # Repeated but not nested: an array of v's.
        result.append([subvalue.get('v', '') for subvalue in v])
      else:
        # Normal flat field.
        result.append(v)
    return result

  def __str__(self):
    return self._GetPrintContext()

  def __repr__(self):
    return self._GetPrintContext()

  def _GetPrintContext(self):
    """Returns context for what is being read."""
    raise NotImplementedError('Subclass must implement GetPrintContext')

  def _ReadOnePage(self, start_row, max_rows, page_token=None):
    """Read one page of data, up to max_rows rows.

    Assumes that the table is ready for reading. Will signal an error otherwise.

    Args:
      start_row: first row to read.
      max_rows: maximum number of rows to return.
      page_token: Optional. current page token.

    Returns:
      tuple of:
      rows: the actual rows of the table, in f,v format.
      page_token: the page token of the next page of results.
      schema: the schema of the table.
    """
    raise NotImplementedError('Subclass must implement _ReadOnePage')


class _TableTableReader(_TableReader):
  """A TableReader that reads from a table."""

  def __init__(self, local_apiclient, max_rows_per_request, table_ref):
    self.table_ref = table_ref
    self.max_rows_per_request = max_rows_per_request
    self._apiclient = local_apiclient

  def _GetPrintContext(self):
    return '%r' % (self.table_ref,)

  def _ReadOnePage(self, start_row, max_rows, page_token=None):
    kwds = dict(self.table_ref)
    kwds['maxResults'] = max_rows
    if page_token:
      kwds['pageToken'] = page_token
    else:
      kwds['startIndex'] = start_row
    data = self._apiclient.tabledata().list(**kwds).execute()
    page_token = data.get('pageToken', None)
    rows = data.get('rows', [])

    kwds = dict(self.table_ref)
    table_info = self._apiclient.tables().get(**kwds).execute()
    schema = table_info.get('schema', {})

    return (rows, page_token, schema)


class _JobTableReader(_TableReader):
  """A TableReader that reads from a completed job."""

  def __init__(self, local_apiclient, max_rows_per_request, job_ref):
    self.job_ref = job_ref
    self.max_rows_per_request = max_rows_per_request
    self._apiclient = local_apiclient

  def _GetPrintContext(self):
    return '%r' % (self.job_ref,)

  def _ReadOnePage(self, start_row, max_rows, page_token=None):
    kwds = dict(self.job_ref)
    kwds['maxResults'] = max_rows
    # Sets the timeout to 0 because we assume the table is already ready.
    kwds['timeoutMs'] = 0
    if page_token:
      kwds['pageToken'] = page_token
    else:
      kwds['startIndex'] = start_row
    data = self._apiclient.jobs().getQueryResults(**kwds).execute()
    if not data['jobComplete']:
      raise BigqueryError('Job %s is not done' % (self,))
    page_token = data.get('pageToken', None)
    schema = data.get('schema', None)
    rows = data.get('rows', [])
    return (rows, page_token, schema)


class ApiClientHelper(object):
  """Static helper methods and classes not provided by the discovery client."""

  def __init__(self, *unused_args, **unused_kwds):
    raise NotImplementedError('Cannot instantiate static class ApiClientHelper')

  class Reference(object):
    """Base class for Reference objects returned by apiclient."""
    _required_fields = set()
    _format_str = ''

    def __init__(self, **kwds):
      if type(self) == ApiClientHelper.Reference:
        raise NotImplementedError(
            'Cannot instantiate abstract class ApiClientHelper.Reference')
      for name in self._required_fields:
        if not kwds.get(name, ''):
          raise ValueError('Missing required argument %s to %s' % (
              name, self.__class__.__name__))
        setattr(self, name, kwds[name])

    @classmethod
    def Create(cls, **kwds):
      """Factory method for this class."""
      args = dict((k, v) for k, v in kwds.iteritems()
                  if k in cls._required_fields)
      return cls(**args)

    def __iter__(self):
      return ((name, getattr(self, name)) for name in self._required_fields)

    def __str__(self):
      return self._format_str % dict(self)

    def __repr__(self):
      return "%s '%s'" % (self.typename, self)

    def __eq__(self, other):
      d = dict(other)
      return all(getattr(self, name) == d.get(name, '')
                 for name in self._required_fields)

  class JobReference(Reference):
    _required_fields = set(('projectId', 'jobId'))
    _format_str = '%(projectId)s:%(jobId)s'
    typename = 'job'

  class ProjectReference(Reference):
    _required_fields = set(('projectId',))
    _format_str = '%(projectId)s'
    typename = 'project'

  class DatasetReference(Reference):
    _required_fields = set(('projectId', 'datasetId'))
    _format_str = '%(projectId)s:%(datasetId)s'
    typename = 'dataset'

    def GetProjectReference(self):
      return ApiClientHelper.ProjectReference.Create(
          projectId=self.projectId)

  class TableReference(Reference):
    _required_fields = set(('projectId', 'datasetId', 'tableId'))
    _format_str = '%(projectId)s:%(datasetId)s.%(tableId)s'
    typename = 'table'

    def GetDatasetReference(self):
      return ApiClientHelper.DatasetReference.Create(
          projectId=self.projectId, datasetId=self.datasetId)

    def GetProjectReference(self):
      return ApiClientHelper.ProjectReference.Create(
          projectId=self.projectId)

