"""Tests for mock_api_server."""

import path_initializer
path_initializer.InitSysPath()

import itertools
import json


from apiclient import discovery
import unittest
from gcutil_lib import mock_api_parser
from gcutil_lib import mock_api_server
from gcutil_lib import mock_api_types

SIMPLE_API = {
    'version': 'v1',
    'baseUrl': 'https://www.googleapis.com/compute/v1/projects/',
    'rootUrl': 'https://www.googleapis.com/',
    'servicePath': 'compute/v1/projects/',
    'parameters': {
        'alt': {
            'type': 'string',
            'enum': [
                'json'
            ],
            'location': 'query'
        },
    },
    'schemas': {
        'Network': {
            'id': 'Network',
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'range': {'type': 'string'}
            }
        },
        'Operation': {
            'id': 'Operation',
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'progress': {'type': 'integer', 'format': 'int32'},
                'errors': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'code': {'type': 'integer', 'format': 'int32'},
                            'message': {'type': 'string'},
                        }
                    }
                }
            }
        }
    },
    'resources': {
        'networks': {
            'methods': {
                'insert': {
                    'id': 'compute.networks.insert',
                    'path': '{project}/networks',
                    'httpMethod': 'POST',
                    'parameters': {
                        'project': {
                            'type': 'string',
                            'required': True,
                            'location': 'path'
                        }
                    },
                    'request': {'$ref': 'Network'},
                    'response': {'$ref': 'Operation'}
                },
                'update': {
                    'id': 'compute.networks.update',
                    'path': '{project}/networks/{network}',
                    'httpMethod': 'POST',
                    'parameters': {
                        'project': {
                            'type': 'string',
                            'required': True,
                            'location': 'path'
                        },
                        'network': {
                            'type': 'string',
                            'required': True,
                            'location': 'path'
                        }
                    },
                    'request': {'$ref': 'Network'},
                }
            }
        },
        'operations': {
            'methods': {
                'get': {
                    'id': 'compute.operations.get',
                    'path': '{project}/operations/{operation}',
                    'httpMethod': 'GET',
                    'parameters': {
                        'operation': {
                            'type': 'string',
                            'required': True,
                            'location': 'path'
                        },
                        'project': {
                            'type': 'string',
                            'required': True,
                            'location': 'path'
                        }
                    },
                    'response': {'$ref': 'Operation'}
                },
                'delete': {
                    'id': 'compute.operations.delete',
                    'path': '{project}/operations/{operation}',
                    'httpMethod': 'DELETE',
                    'parameters': {
                        'operation': {
                            'type': 'string',
                            'required': True,
                            'location': 'path'
                        },
                        'project': {
                            'type': 'string',
                            'required': True,
                            'location': 'path'
                        }
                    }
                },
                'list': {
                    'id': 'compute.operations.list',
                    'path': '{project}/operations',
                    'httpMethod': 'GET',
                    'parameters': {
                        'filter': {
                            'type': 'string',
                            'location': 'query'
                        },
                        'maxResults': {
                            'type': 'integer',
                            'format': 'uint32',
                            'minimum': '0',
                            'maximum': '100',
                            'location': 'query'
                        },
                        'pageToken': {
                            'type': 'number',
                            'format': 'double',
                            'location': 'query'
                        },
                        'project': {
                            'type': 'string',
                            'required': True,
                            'location': 'path',
                            'format': 'uint64'
                        },
                        'sort': {
                            'type': 'boolean',
                            'location': 'query'
                        }
                    }
                }
            }
        }
    }
}


class UtilityClassTest(unittest.TestCase):
  def testMockServerCall(self):
    expected_response = {'kind': 'compute#operation'}

    def ResponseFunction(*unused_args, **unused_kwargs):
      return mock_api_server.MockServer.MOCK_RESPONSE(expected_response, True)

    server_call = mock_api_server.MockServer._MockServerCall(
        'compute.resource.method', ResponseFunction)

    self.assertEquals('compute.resource.method', server_call._method)
    self.assertTrue(ResponseFunction is server_call._response_function)
    self.assertEquals(len(server_call._requests), 0)

    # GetRequest fails - request hasn't been made.
    self.assertRaises(ValueError, server_call.GetRequest)

    # Simulate request
    parameters = {'project': 'my-project'}
    request = {'kind': 'compute#resource', 'name': 'test-resource'}
    response = server_call.ExecuteRequest(
        'https://www.googleapis.com/compute/v1/resource', 'POST',
        parameters, request)

    self.assertEquals(expected_response, response.response)
    self.assertTrue(response.exhausted)

    self.assertTrue(isinstance(server_call._requests[0],
                               mock_api_server._Request))
    self.assertEquals('https://www.googleapis.com/compute/v1/resource',
                      server_call._requests[0].uri)
    self.assertEquals('POST', server_call._requests[0].method)
    self.assertTrue(parameters is server_call._requests[0].parameters)
    self.assertTrue(request is server_call._requests[0].body)

  def testMockRequest(self):
    executed = [False]  # Method 'execute' below was not executed.
    def Execute(uri, http_method, http_body, rest_method):
      self.assertFalse(executed[0])  # Executed only once.
      executed[0] = True  # Now it was
      self.assertTrue(expected_uri is uri)
      self.assertTrue(expected_http_method is http_method)
      self.assertTrue(expected_http_body is http_body)
      self.assertTrue(expected_rest_method is rest_method)

    postproc = object()
    expected_uri = 'https://www.googleapis.com/compute/v1/collection/resource'
    expected_http_method = 'POST'
    expected_http_body = {'kind': 'compute#resource', 'name': 'my-resource'}
    expected_rest_method = 'compute.resource.custom'

    mock_request = mock_api_server.MockServer._MockRequest(
        Execute, postproc, expected_uri, expected_http_method,
        expected_http_body, expected_rest_method)

    self.assertTrue(Execute is mock_request._execute)
    self.assertTrue(postproc is mock_request._postproc)
    self.assertTrue(expected_uri is mock_request._uri)
    self.assertTrue(expected_http_method is mock_request._http_method)
    self.assertTrue(expected_http_body is mock_request._http_body)
    self.assertTrue(expected_rest_method is mock_request._rest_method)

    self.assertFalse(executed[0])
    mock_request.execute()
    self.assertTrue(executed[0])


class MockServerTest(unittest.TestCase):
  def setUp(self):
    parser = mock_api_parser.Parser(SIMPLE_API)
    methods = parser.Parse()
    self._server = mock_api_server.MockServer(methods)
    self._api = discovery.build_from_document(
        SIMPLE_API, requestBuilder=self._server.BuildRequest)
    self._networks = self._api.networks()
    self._operations = self._api.operations()

    # Basic sanity checks.
    self.assertEquals(['Network', 'Operation'], sorted(parser._parsed_schemas))
    self.assertTrue(isinstance(parser._parsed_schemas['Network'],
                               mock_api_types.ObjectType))
    self.assertTrue(isinstance(parser._parsed_schemas['Operation'],
                               mock_api_types.ObjectType))
    self.assertEquals(
        ['compute.networks.insert',
         'compute.networks.update',
         'compute.operations.delete',
         'compute.operations.get',
         'compute.operations.list'],
        sorted(methods))

  def testBuildRequest(self):
    expected_postproc = object()
    expected_uri = 'https://www.googleapis.com/compute/v1/collection/resource'
    expected_method = 'POST'
    expected_body = {'kind': 'compute#resource'}
    expected_rest_method = 'compute.operations.get'

    request = self._server.BuildRequest(
        http=None,
        postproc=expected_postproc,
        uri=expected_uri,
        method=expected_method,
        body=expected_body,
        methodId=expected_rest_method)

    self.assertTrue(isinstance(request,
                               mock_api_server.MockServer._MockRequest))
    self.assertTrue(expected_postproc is request._postproc)
    self.assertTrue(expected_uri is request._uri)
    self.assertTrue(expected_method is request._http_method)
    self.assertTrue(expected_body is request._http_body)
    self.assertTrue(expected_rest_method is request._rest_method)

    # Invalid method.

    self.assertRaises(
        ValueError, self._server.BuildRequest,
        http=None,
        postproc=expected_postproc,
        uri=expected_uri,
        method=expected_method,
        body=expected_body,
        methodId='compute.invalid.invalid')

  def testExecuteRequestInvalidMethod(self):
    self.assertRaises(
        ValueError, self._server._ExecuteRequest,
        uri='https://www.googleapis.com/compute/v1/collection/resource',
        http_method='POST',
        body={'kind': 'compute#resource'},
        rest_method='invalid.invalid.invalid')

  def testExecuteRequestNoResponses(self):
    rest_method = 'compute.networks.update'
    self.assertRaises(
        ValueError, self._server._ExecuteRequest,
        uri=('https://www.googleapis.com/compute/v1/projects/'
             'my-project/networks/my-network'),
        http_method='POST',
        body={'kind': 'compute#resource'},
        rest_method=rest_method)

    # Run again with a response prepared. Will succeed now.
    expected_response = None
    self._server.Respond(rest_method, expected_response)

    response = self._server._ExecuteRequest(
        uri=('https://www.googleapis.com/compute/v1/projects/'
             'my-project/networks/my-network'),
        http_method='POST',
        body={'name': 'my-network'},
        rest_method=rest_method)
    self.assertTrue(expected_response is response)

  def testExecuteMultipleRequests(self):
    expected_uri = ('https://www.googleapis.com/compute/v1/projects/'
                    'my-project/networks')
    expected_method = 'GET'
    expected_bodies = [{'name': 'my-network-1', 'range': '10.0.0.0/16'},
                       {'name': 'my-network-2', 'range': '10.0.0.0/16'}]
    expected_rest_method = 'compute.networks.insert'

    expected_response = {'progress': 30}

    # Program the responses.
    server_call = self._server.RespondN(expected_rest_method,
                                        expected_response, 2)

    # Execute both requests.
    for body in expected_bodies:
      response = self._server._ExecuteRequest(
          uri=expected_uri,
          http_method=expected_method,
          body=body,
          rest_method=expected_rest_method)

      # Validate the request that arrived on the 'server'.
      self.assertTrue(
          isinstance(server_call, mock_api_server.MockServer._MockServerCall))
      self.assertEquals(expected_response, response)

    # Get the requests back.
    requests = server_call.GetAllRequests()

    # There were as many requests as bodies.
    self.assertEquals(len(expected_bodies), len(requests))

    # Ensure that the requests are what I expect them to be.
    for (body, request) in itertools.izip(expected_bodies, requests):
      self.assertEquals(expected_uri, request.uri)
      self.assertEquals(expected_method, request.method)
      self.assertEquals(body, request.body)
      self.assertEquals({'project': 'my-project'}, request.parameters)

    # Any additional call will kill it.
    self.assertRaises(ValueError,
                      self._server._ExecuteRequest,
                      uri=expected_uri,
                      http_method=expected_method,
                      body=expected_bodies[0],
                      rest_method=expected_rest_method)

  def testRespondForever(self):
    expected_uri = ('https://www.googleapis.com/compute/v1/projects/'
                    'my-project/networks')
    expected_method = 'GET'
    expected_body = {'name': 'my-network', 'range': '10.0.0.0/16'}
    expected_rest_method = 'compute.networks.insert'

    expected_response = {'progress': 30}

    # Program the responses.
    server_call = self._server.RespondForever(expected_rest_method,
                                              expected_response)

    # Execute 10 requests.
    for _ in xrange(0, 10):
      response = self._server._ExecuteRequest(
          uri=expected_uri,
          http_method=expected_method,
          body=expected_body,
          rest_method=expected_rest_method)

      # Validate the request that arrived on the 'server'.
      self.assertTrue(
          isinstance(server_call, mock_api_server.MockServer._MockServerCall))
      self.assertEquals(expected_response, response)

    # Get the requests back.
    requests = server_call.GetAllRequests()

    # There were 10 requests.
    self.assertEquals(10, len(requests))

    # Ensure that the requests are what I expect them to be.
    for request in requests:
      self.assertEquals(expected_uri, request.uri)
      self.assertEquals(expected_method, request.method)
      self.assertEquals(expected_body, request.body)
      self.assertEquals({'project': 'my-project'}, request.parameters)

  def testExecuteRequest(self):
    expected_uri = ('https://www.googleapis.com/compute/v1/projects/'
                    'my-project/networks')
    expected_method = 'GET'
    expected_body = {'name': 'my-network', 'range': '10.0.0.0/16'}
    expected_rest_method = 'compute.networks.insert'

    # Program the response.
    expected_response = {'name': 'my-operation', 'progress': 30}
    server_call = self._server.Respond(expected_rest_method, expected_response)

    # Execute the request.
    response = self._server._ExecuteRequest(
        uri=expected_uri,
        http_method=expected_method,
        body=expected_body,
        rest_method=expected_rest_method)
    self.assertTrue(expected_response is response)

    # Validate the request that arrived on the 'server'.
    self.assertTrue(
        isinstance(server_call, mock_api_server.MockServer._MockServerCall))
    self.assertEquals(expected_response, response)

  def testSimpleApiCalls(self):
    network = {
        'name': 'my-network',
        'range': '10.0.0.0/8'
    }

    request = self._networks.insert(project='my-project', body=network)
    # No response available, return error.
    self.assertRaises(ValueError, request.execute)

    operation = {
        'name': 'my-operation',
        'progress': 30
    }
    server_call = self._server.Respond('compute.networks.insert', operation)

    response = request.execute()
    self.assertEquals(network, json.loads(server_call.GetRequest().body))
    self.assertTrue(operation is response)

    # Get the operation just for good measure.
    request = self._operations.get(
        project='my-project', operation='my-operation')
    server_call = self._server.Respond('compute.operations.get', operation)
    response = request.execute()
    self.assertEquals(
        ('https://www.googleapis.com/compute/v1/projects/my-project/'
         'operations/my-operation?alt=json'),
        server_call.GetRequest().uri)
    self.assertTrue(operation is response)

  def testApiCallWithParameters(self):
    server_call = self._server.Respond('compute.operations.list', None)
    self._operations.list(
        project=1234567890,
        filter='filter-expression',
        maxResults=17,
        pageToken=3.14,
        sort=True).execute()
    request = server_call.GetRequest()
    self.assertTrue(
        request.uri.startswith('https://www.googleapis.com/compute/v1/'
                               'projects/1234567890/operations?'))

    self.assertEquals('17', request.parameters['maxResults'])
    self.assertEquals('filter-expression', request.parameters['filter'])
    self.assertEquals('3.14', request.parameters['pageToken'])
    self.assertEquals('true', request.parameters['sort'])

  def testNoneMethodCalls(self):
    response = {'name': 'bogus-operation'}

    self.assertRaises(ValueError, self._server.RespondForever, None,
                      response)

    self.assertRaises(ValueError, self._server.Respond, None,
                      response)

  def testInvalidNumberOfResponses(self):
    response = {'name': 'bogus-operation'}
    rest_method = 'compute.networks.insert'

    self.assertRaises(ValueError,
                      self._server.RespondN, rest_method, response, 0)

    self.assertRaises(ValueError,
                      self._server.RespondN, rest_method, response, -1)

    self.assertRaises(ValueError,
                      self._server.RespondN, rest_method, response, 1.5)

if __name__ == '__main__':
  unittest.main()
