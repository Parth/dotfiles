# Copyright 2013 Google Inc. All Rights Reserved.

"""A module to make it easy to set up and run CLIs in the Cloud SDK."""

import urllib
import urlparse
import uuid

from oauth2client import client

from googlecloudsdk.core import config
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core.credentials import store as c_store


__all__ = ['Credentials', 'Http']


class Error(exceptions.Error):
  """Exceptions for the cli module."""


class CannotRefreshAuthTokenError(Error, client.AccessTokenRefreshError):
  """An exception raised when the auth tokens fail to refresh."""

  def __init__(self, msg):
    auth_command = '$ gcloud auth login'
    message = ('There was a problem refreshing your current auth tokens: '
               '{0}.  Please run\n  {1}.'.format(msg, auth_command))
    super(CannotRefreshAuthTokenError, self).__init__(message)


def Credentials():
  """Get the currently active credentials.

  This function loads account credentials via core.account property
  of core.properties module.

  These credentials will be refreshed before being returned, so it makes sense
  to cache the value returned for short-lived programs.

  Returns:
    An active, valid credentials object.

  Raises:
    c_store.Error: If an error loading the credentials occurs.
  """
  return c_store.Load()


def Http(cmd_path=None, trace_token=None,
         auth=True, creds=None, timeout=None):
  """Get an httplib2.Http object for working with the Google API.

  Args:
    cmd_path: str, Path of command that will use the httplib2.Http object.
    trace_token: str, Token to be used to route service request traces.
    auth: bool, True if the http object returned should be authorized.
    creds: oauth2client.client.Credentials, If auth is True and creds is not
        None, use those credentials to authorize the httplib2.Http object.
    timeout: double, The timeout in seconds to pass to httplib2.  This is the
        socket level timeout.  If timeout is None, timeout is infinite.

  Returns:
    An authorized httplib2.Http object, or a regular httplib2.Http object if no
    credentials are available.
  """

  # TODO(user): Have retry-once-if-denied logic, to allow client tools to not
  # worry about refreshing credentials.

  http = c_store._Http(timeout=timeout)  # pylint:disable=protected-access

  # Wrap the request method to put in our own user-agent, and trace reporting.
  gcloud_ua = 'gcloud/{0} command/{1} invocation-id/{2}'.format(
      config.CLOUD_SDK_VERSION,
      cmd_path,
      uuid.uuid4().hex)
  http = _WrapRequestForUserAgentAndTracing(http, trace_token,
                                            gcloud_ua)
  if auth:
    if not creds:
      creds = Credentials()
    http = creds.authorize(http)
    # Wrap the request method to put in our own error handling.
    http = _WrapRequestForAuthErrHandling(http)
  return http


def _WrapRequestForUserAgentAndTracing(http, trace_token,
                                       gcloud_ua):
  """Wrap request with user-agent, and trace reporting.

  Args:
    http: The original http object.
    trace_token: str, Token to be used to route service request traces.
    gcloud_ua: str, User agent string to be included in the request.

  Returns:
    http, The same http object but with the request method wrapped.
  """
  orig_request = http.request

  def RequestWithUserAgentAndTracing(*args, **kwargs):
    """Wrap request with user-agent, and trace reporting.

    Args:
      *args: Positional arguments.
      **kwargs: Keyword arguments.

    Returns:
      Wrapped request method with user-agent and trace reporting.
    """
    modified_args = list(args)

    # Use gcloud specific user-agent with command path and invocation-id.
    # Pass in the user-agent through kwargs or args.
    def UserAgent(current=''):
      user_agent = '{0} {1}'.format(current, gcloud_ua)
      return user_agent.strip()
    if 'headers' in kwargs:
      cur_ua = kwargs['headers'].get('user-agent', '')
      kwargs['headers']['user-agent'] = UserAgent(cur_ua)
    elif len(args) > 3:
      cur_ua = modified_args[3].get('user-agent', '')
      modified_args[3]['user-agent'] = UserAgent(cur_ua)
    else:
      kwargs['headers'] = {'user-agent': UserAgent()}

    # Modify request url to enable requested tracing.
    url_parts = urlparse.urlsplit(args[0])
    query_params = urlparse.parse_qs(url_parts.query)
    if trace_token:
      query_params['trace'] = 'token:{0}'.format(trace_token)

    # Replace the request url in the args
    modified_url_parts = list(url_parts)
    modified_url_parts[3] = urllib.urlencode(query_params, doseq=True)
    modified_args[0] = urlparse.urlunsplit(modified_url_parts)

    return orig_request(*modified_args, **kwargs)

  http.request = RequestWithUserAgentAndTracing

  # apitools needs this attribute to do credential refreshes during batch API
  # requests.
  if hasattr(orig_request, 'credentials'):
    setattr(http.request, 'credentials', orig_request.credentials)

  return http


def _WrapRequestForAuthErrHandling(http):
  """Wrap request with exception handling for auth.

  We need to wrap exception handling because oauth2client does similar wrapping
  when you authorize the http object.  Because of this, a credential refresh
  error can get raised wherever someone makes an http request.  With no common
  place to handle this exception, we do more wrapping here so we can convert it
  to one of our typed exceptions.

  Args:
    http: The original http object.

  Returns:
    http, The same http object but with the request method wrapped.
  """
  orig_request = http.request

  def RequestWithErrHandling(*args, **kwargs):
    try:
      return orig_request(*args, **kwargs)
    except client.AccessTokenRefreshError as e:
      log.debug('Exception caught during HTTP request: %s', e.message,
                exc_info=True)
      raise CannotRefreshAuthTokenError(e.message)

  http.request = RequestWithErrHandling

  # apitools needs this attribute to do credential refreshes during batch API
  # requests.
  if hasattr(orig_request, 'credentials'):
    setattr(http.request, 'credentials', orig_request.credentials)

  return http
