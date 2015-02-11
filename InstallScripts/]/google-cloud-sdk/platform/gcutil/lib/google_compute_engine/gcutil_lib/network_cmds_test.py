#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
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

"""Unit tests for the network commands."""

import path_initializer
path_initializer.InitSysPath()

import json
import unittest

from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api
from gcutil_lib import mock_lists
from gcutil_lib import network_cmds


class NetworkCmdsTest(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)

  def testAddNetworkWithDefaultsGeneratesCorrectRequest(self):
    set_flags = {
        'project': 'my-project',
        }
    command = self._CreateAndInitializeCommand(
        network_cmds.AddNetwork, 'addnetwork', self.version, set_flags)

    call = self.mock.Respond(
        'compute.networks.insert',
        {
            'kind': 'compute#operation',
            'name': 'my-network'
        })

    command.Handle('my-network')
    request = call.GetRequest()

    self.assertEquals('POST', request.method)

    parameters = request.parameters
    self.assertEquals('my-project', parameters['project'])

    body = json.loads(request.body)
    self.assertEquals('my-network', body['name'])
    self.assertEquals('10.0.0.0/8', body['IPv4Range'])
    self.assertTrue('gatewayIPv4' not in body)

  def testAddNetworkGeneratesCorrectRequest(self):
    set_flags = {
        'project': 'my-project',
        'range': '192.168.0.0/16',
        'description': 'my network',
        'gateway': '192.168.0.1'
        }
    command = self._CreateAndInitializeCommand(
        network_cmds.AddNetwork, 'addnetwork', self.version, set_flags)

    call = self.mock.Respond(
        'compute.networks.insert',
        {
            'kind': 'compute#operation',
            'name': 'my-network'
        })

    command.Handle('my-network')
    request = call.GetRequest()

    self.assertEquals('POST', request.method)

    parameters = request.parameters
    self.assertEquals('my-project', parameters['project'])

    body = json.loads(request.body)
    self.assertEquals('my-network', body['name'])
    self.assertEquals('192.168.0.0/16', body['IPv4Range'])
    self.assertEquals('my network', body['description'])
    self.assertEquals('192.168.0.1', body['gatewayIPv4'])

  def testAddNetworkWithFullyQualifiedPathGeneratesCorrectRequest(self):
    set_flags = {
        'project': 'wrong-project',
        'range': '192.168.0.0/16',
        'description': 'my network',
        'gateway': '192.168.0.1',
        }

    command = self._CreateAndInitializeCommand(
        network_cmds.AddNetwork, 'addnetwork', self.version, set_flags)

    call = self.mock.Respond(
        'compute.networks.insert',
        {
            'kind': 'compute#operation',
            'name': 'my-network',
        })

    command.Handle('right-project/global/networks/my-network')
    request = call.GetRequest()

    self.assertEquals('POST', request.method)

    parameters = request.parameters
    self.assertEquals('right-project', parameters['project'])

    body = json.loads(request.body)
    self.assertEquals('my-network', body['name'])
    self.assertEquals('192.168.0.0/16', body['IPv4Range'])
    self.assertEquals('my network', body['description'])
    self.assertEquals('192.168.0.1', body['gatewayIPv4'])

  def testGetNetworkGeneratesCorrectRequest(self):
    set_flags = {
        'project': 'my-project',
        }
    command = self._CreateAndInitializeCommand(
        network_cmds.GetNetwork, 'getnetwork', self.version, set_flags)

    call = self.mock.Respond(
        'compute.networks.get',
        {
            'kind': 'compute#network',
            'name': 'my-network'
        })

    command.Handle('my-network')
    request = call.GetRequest()

    self.assertEquals('GET', request.method)
    self.assertEquals(request.body, None)

    parameters = request.parameters
    self.assertEquals('my-project', parameters['project'])
    self.assertEquals('my-network', parameters['network'])

  def testDeleteNetworkGeneratesCorrectRequest(self):
    set_flags = {
        'project': 'my-project',
        }
    command = self._CreateAndInitializeCommand(
        network_cmds.DeleteNetwork, 'deletenetwork', self.version, set_flags)

    call = self.mock.Respond(
        'compute.networks.delete',
        {
            'kind': 'compute#operation',
            'name': 'my-network',
            'operationType': 'delete',
            'targetLink':
            'https://www.googleapis.com/compute/v1/projects/'
            'my-project/global/networks/my-network',
            'status': 'DONE'
        })

    unused_results, exceptions = command.Handle('my-network')

    self.assertEquals([], exceptions)

    request = call.GetRequest()

    self.assertEquals('DELETE', request.method)
    self.assertEquals(request.body, None)

    parameters = request.parameters
    self.assertEquals('my-project', parameters['project'])
    self.assertEquals('my-network', parameters['network'])

  def testDeleteMultipleNetworks(self):
    set_flags = {
        'project': 'my-project',
        }
    command = self._CreateAndInitializeCommand(
        network_cmds.DeleteNetwork, 'deletenetwork', self.version, set_flags)

    expected_networks = ['my-network-%02d' % x for x in xrange(2)]

    # Program the responses
    response_count = [len(expected_networks)]

    def ResponseFunction(unused_uri, unused_http_method, parameters,
                         unused_body):
      response_count[0] -= 1
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'name': parameters['network'],
              'operationType': 'delete',
              'targetLink':
              'https://www.googleapis.com/compute/v1/projects/'
              'my-project/global/networks/my-network',
              'status': 'DONE'
          },
          response_count[0] == 0)

    call = self.mock.RespondF('compute.networks.delete', ResponseFunction)

    # Perform the request
    results, exceptions = command.Handle(*expected_networks)

    # Nothing should go wrong.
    self.assertEquals([], exceptions)

    # All of the requests should have been received.
    requests = call.GetAllRequests()
    self.assertEquals(len(requests), len(results['items']))

    # The requests all arrive, but may be totally mixed up in order.
    for request in requests:
      self.assertEquals('DELETE', request.method)
      self.assertEquals(request.body, None)

      # Check that the network returned matches the parameters sent.
      parameters = request.parameters

      self.assertEquals('my-project', parameters['project'])

      # Ensure that each network name in the list was sent exactly once.
      # Assert that the expected networks containsthis network, then remove
      # this network.
      self.assertTrue(parameters['network'] in expected_networks)
      expected_networks = [network for network in expected_networks
                           if network != parameters['network']]

  def testListNetworks(self):
    expected_project = 'test_project'

    set_flags = {
        'project': expected_project
        }

    command = self._CreateAndInitializeCommand(
        network_cmds.ListNetworks, 'listnetworks', self.version, set_flags)

    listcall = mock_lists.GetSampleNetworkListCall(command, self.mock)

    command.Handle()
    requests = listcall.GetAllRequests()

    self.assertEquals(len(requests), 1)

    request = requests[0]

    self.assertEquals(expected_project, request.parameters['project'])

if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
