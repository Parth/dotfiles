# Copyright 2013 Google Inc. All Rights Reserved.

"""Run a web flow for oauth2.

"""

import os

from oauth2client import client
from oauth2client import tools

from googlecloudsdk.core import config
from googlecloudsdk.core import log

try:
  # pylint:disable=g-import-not-at-top
  from urlparse import parse_qsl
except ImportError:
  # pylint:disable=g-import-not-at-top
  from cgi import parse_qsl


class Error(Exception):
  """Exceptions for the flow module."""


class AuthRequestRejectedException(Error):
  """Exception for when the authentication request was rejected."""


class AuthRequestFailedException(Error):
  """Exception for when the authentication request was rejected."""


class ClientRedirectHandler(tools.ClientRedirectHandler):
  """A handler for OAuth 2.0 redirects back to localhost.

  Waits for a single request and parses the query parameters
  into the servers query_params and then stops serving.
  """

  # pylint:disable=invalid-name, This method is overriden from the base class.
  def do_GET(self):
    """Handle a GET request.

    Parses the query parameters and prints a message
    if the flow has completed. Note that we can't detect
    if an error occurred.
    """
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    query = self.path.split('?', 1)[-1]
    query = dict(parse_qsl(query))
    self.server.query_params = query

    if 'code' in query:
      page = 'oauth2_landing.html'
    else:
      page = 'oauth2_landing_error.html'

    html_path = os.path.join(
        config.GoogleCloudSDKPackageRoot(), 'core', 'credentials', page)
    with open(html_path) as html_file:
      self.wfile.write(html_file.read())


def Run(flow, launch_browser=True, http=None,
        auth_host_name='localhost', auth_host_port_start=8085):
  """Run a web flow to get oauth2 credentials.

  Args:
    flow: oauth2client.OAuth2WebServerFlow, A flow that is ready to run.
    launch_browser: bool, If False, give the user a URL to copy into
        a browser. Requires that they paste the refresh token back into the
        terminal. If True, opens a web browser in a new window.
    http: httplib2.Http, The http transport to use for authentication.
    auth_host_name: str, Host name for the redirect server.
    auth_host_port_start: int, First port to try for serving the redirect. If
        this port is taken, it will keep trying incrementing ports until 100
        have been tried, then fail.

  Returns:
    oauth2client.Credential, A ready-to-go credential that has already been
    put in the storage.

  Raises:
    AuthRequestRejectedException: If the request was rejected.
    AuthRequestFailedException: If the request fails.
  """

  if launch_browser:
    # pylint:disable=g-import-not-at-top, Import when needed for performance.
    import socket
    import webbrowser

    success = False
    port_number = auth_host_port_start

    while True:
      try:
        httpd = tools.ClientRedirectServer((auth_host_name, port_number),
                                           ClientRedirectHandler)
      except socket.error, e:
        if port_number > auth_host_port_start + 100:
          success = False
          break
        port_number += 1
      else:
        success = True
        break

    if success:
      flow.redirect_uri = ('http://%s:%s/' % (auth_host_name, port_number))

      authorize_url = flow.step1_get_authorize_url()

      webbrowser.open(authorize_url, new=1, autoraise=True)
      message = 'Your browser has been opened to visit:'
      log.err.Print('{message}\n\n    {url}\n\n'.format(
          message=message,
          url=authorize_url,
      ))

      httpd.handle_request()
      if 'error' in httpd.query_params:
        raise AuthRequestRejectedException('Unable to authenticate.')
      if 'code' in httpd.query_params:
        code = httpd.query_params['code']
      else:
        raise AuthRequestFailedException(
            'Failed to find "code" in the query parameters of the redirect.')
    else:
      message = ('Failed to start a local webserver listening on any port '
                 'between {start_port} and {end_port}. Please check your '
                 'firewall settings or locally running programs that may be '
                 'blocking or using those ports.')
      log.warn(message.format(
          start_port=auth_host_port_start,
          end_port=port_number,
      ))

      launch_browser = False
      log.warn('Defaulting to URL copy/paste mode.')

  if not launch_browser:
    flow.redirect_uri = client.OOB_CALLBACK_URN
    authorize_url = flow.step1_get_authorize_url()
    message = 'Go to the following link in your browser:'
    log.err.Print('{message}\n\n    {url}\n\n'.format(
        message=message,
        url=authorize_url,
    ))
    code = raw_input('Enter verification code: ').strip()

  try:
    credential = flow.step2_exchange(code, http=http)
  except client.FlowExchangeError, e:
    raise AuthRequestFailedException(e)

  return credential
