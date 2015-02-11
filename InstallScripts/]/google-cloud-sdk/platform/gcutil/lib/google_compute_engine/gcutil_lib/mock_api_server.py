# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Support for mocking Google Compute Engine API method calls."""

import collections
import threading

from gcutil_lib import gcutil_logging

LOGGER = gcutil_logging.LOGGER

_ServerMethod = collections.namedtuple('ServerMethod', ('method', 'calls'))
_Request = collections.namedtuple('Request',
                                  ('uri', 'method', 'parameters', 'body'))


class MockServer(object):
  """Class for tracking individual API calls, their requests and responses.

  The MockServer instance (or more precisely, bound BuildRequest method) is
  passed to discovery document as a way to create API call requests.
  Using the Respond method test can program responses to requests the tested
  code is sending.
  """
  __slots__ = ('_methods', '_lock')

  MOCK_RESPONSE = collections.namedtuple('MockResponse',
                                         ['response', 'exhausted'])

  class _MockServerCall(object):
    __slots__ = ('_method', '_requests', '_response_function')

    def __init__(self, method, response_function):
      self._method = method
      self._requests = []
      self._response_function = response_function

    def GetRequest(self, index=0):
      if not self._requests:
        raise ValueError('No request was captured.')
      return self._requests[index]

    def GetAllRequests(self):
      return self._requests

    def ExecuteRequest(self, uri, http_method, parameters, body):
      """Logs a request and sends the specified response.

      Args:
        uri:  The uri for the request.
        http_method:  The http_method for the request.
        parameters:  Parameters for the request.
        body:  JSON body for the request.

      Returns:
        A mocked server response.
      """

      self._requests.append(_Request(uri, http_method, parameters, body))
      return self._response_function(uri, http_method, parameters, body)

  class _MockRequest(object):
    __slots__ = ('_execute', '_postproc', '_uri', '_http_method',
                 '_http_body', '_rest_method')

    def __init__(self, execute, postproc, uri, http_method, http_body,
                 rest_method):
      self._execute = execute
      self._postproc = postproc
      self._uri = uri
      self._http_method = http_method
      self._http_body = http_body
      self._rest_method = rest_method

    # pylint: disable=g-bad-name,unused-argument
    def execute(self, http=None):
      return self._execute(self._uri, self._http_method, self._http_body,
                           self._rest_method)

  def __init__(self, methods):
    self._methods = dict((method_name, _ServerMethod(method, []))
                         for method_name, method in methods.iteritems())
    self._lock = threading.Lock()

  # The signature of this method must match what google-api-python-client
  # library expects.
  # pylint: disable=unused-argument,g-bad-name
  def BuildRequest(self, http, postproc, uri, method='GET', body=None,
                   headers=None, methodId=None, resumable=None):
    """HTTP request builder, passed to discovery to create mock requests."""
    with self._lock:
      server_method = self._methods.get(methodId)

    if server_method is None:
      raise ValueError('Unrecognized method {method}'.format(method=methodId))

    return self._MockRequest(
        self._ExecuteRequest, postproc, uri, method, body, methodId)

  def _ExecuteRequest(self, uri, http_method, body, rest_method):
    with self._lock:
      server_method = self._methods.get(rest_method)
      if server_method is None:
        raise ValueError('Unrecognized method {method}'.format(
            method=rest_method))
      if not server_method.calls:
        raise ValueError('No responses available for method {method}'.format(
            method=rest_method))

      parameters = server_method.method.ValidateRequest(uri, body)
      server_call = server_method.calls[0]

      response, exhausted = server_call.ExecuteRequest(uri, http_method,
                                                       parameters, body)
      if exhausted:
        server_method.calls.pop(0)

      return response

  def Respond(self, method, response):
    """Responds to a call to method with a specified response, one time.

    Args:
      method:  The method (from the discovery doc) to respond to.
      response:  The response to return to the caller.

    Returns:
      A mock server call object which can be used to retrieve the request
      sent to the server.
    """
    return self.RespondN(method, response, 1)

  def RespondForever(self, method, response):
    """Responds to a call to method with a specified response forever.

    Args:
      method:  The method (from the discovery doc) to respond to.
      response:  The response to return to the caller.

    Returns:
      A mock server call object which can be used to retrieve the request
      sent to the server.
    """
    def ResponseFunction(*unused_args, **unused_kwargs):
      return response, False

    return self.RespondF(method, ResponseFunction)

  def RespondN(self, method, response, times):
    """Responds to a call to method with a specified response several times.

    Args:
      method:  The method (from the discovery doc) to respond to.
      response:  The response to return to the caller.
      times:  Number of times to return the response.  Must be an integer
        greater than zero.

    Returns:
      A mock server call object which can be used to retrieve the request
      sent to the server.

    Raises:
      ValueError:  times was not valid.
    """
    if not isinstance(times, int) and not isinstance(times, long):
      raise ValueError('Must respond an integer number of times.')

    if times <= 0:
      raise ValueError('Must respond at least 1 time.')

    # calls_left is a single-element array being used for closure with
    # ResponseFunction, since I need to know how many times it was called.
    calls_left = [times]

    def ResponseFunction(*unused_args, **unused_kwargs):
      calls_left[0] -= 1
      return MockServer.MOCK_RESPONSE(response, calls_left[0] == 0)

    return self.RespondF(method, ResponseFunction)

  def RespondF(self, method, response_function):
    """Responds to a call to method with a generated response.

    Args:
      method:  The method (from the discovery doc) to respond to.
      response_function:  The response to return to the caller based
        on the request.  Takes arguments uri, http_method, parameters, body.

    Returns:
      A mock server call object which can be used to retrieve the request(s)
      sent to the server.

    Raises:
      ValueError:  The specified method was not in the discovery doc.
    """
    with self._lock:
      server_method = self._methods.get(method)
      if server_method is None:
        raise ValueError('Invalid method {method}'.format(method=method))

      server_call = self._MockServerCall(method, response_function)
      server_method.calls.append(server_call)
      return server_call
