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

"""Unit tests for the route commands."""



import path_initializer
path_initializer.InitSysPath()

import copy
import json

import gflags as flags
import unittest

from gcutil_lib import command_base
from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api
from gcutil_lib import old_mock_api
from gcutil_lib import route_cmds

FLAGS = flags.FLAGS

EXPECTED_PROJECT = 'test_project'


class RouteCmdsTest(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)

  def testAddRouteWithFullyQualifiedPath(self):
    project_flag = 'wrong-project'
    expected_project = 'right-project'
    expected_zone = 'passing-zone'
    expected_instance = 'four'
    expected_route = 'sixty-six'
    expected_range = '10.0.0.0/8'

    set_flags = {
        'project': project_flag,
    }

    # In order to get the correct fully qualified paths for the arguments,
    # the command must be initialized early.
    command = self._CreateAndInitializeCommand(
        route_cmds.AddRoute, 'addroute', self.version, set_flags)

    submitted_route = command.NormalizeGlobalResourceName(
        expected_project, 'routes', expected_route)

    submitted_instance = command.NormalizePerZoneResourceName(
        expected_project, expected_zone, 'instances', expected_instance)

    set_flags['next_hop_instance'] = submitted_instance

    # Initialize the command for real this time.
    command = self._CreateAndInitializeCommand(
        route_cmds.AddRoute, 'addroute', self.version, set_flags)

    route_call = self.mock.Respond('compute.routes.insert', {})

    command.Handle(submitted_route, expected_range)

    request = route_call.GetRequest()
    parameters = request.parameters
    body = json.loads(request.body)

    self.assertEqual(parameters['project'], expected_project)

    self.assertEqual(body['name'], expected_route)
    self.assertEqual(body['nextHopInstance'], submitted_instance)
    self.assertEqual(body['destRange'], expected_range)


class OldRouteCmdsTest(unittest.TestCase):

  def _DoAddRouteGeneratesCorrectRequest(self, service_version, dest_range,
                                         next_hop_flag_name, next_hop_str_val):
    flag_values = copy.deepcopy(FLAGS)

    command = route_cmds.AddRoute('addroute', flag_values)

    expected_route = 'test_route'
    submitted_network = 'test_network'
    expected_description = 'test route'
    expected_tags = ['a', 'b']
    expected_priority = 7
    flag_values.service_version = service_version
    flag_values.project = EXPECTED_PROJECT
    flag_values.description = expected_description
    flag_values.network = submitted_network
    flag_values.priority = expected_priority
    flag_values.tags = expected_tags
    flag_values[next_hop_flag_name].Parse(next_hop_str_val)

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()

    expected_network = command.NormalizeGlobalResourceName(EXPECTED_PROJECT,
                                                           'networks',
                                                           submitted_network)

    result = command.Handle(expected_route, dest_range)

    self.assertEqual(result['project'], EXPECTED_PROJECT)

    response_body = result['body']
    self.assertEqual(response_body['name'], expected_route)
    self.assertEqual(response_body['network'], expected_network)
    self.assertEqual(response_body['description'], expected_description)
    self.assertEqual(response_body['priority'], expected_priority)
    self.assertEqual(response_body['tags'], expected_tags)

    return command, response_body

  def testAddRouteGeneratesCorrectRequest(self):
    for version in command_base.SUPPORTED_VERSIONS:
      command, response_body = self._DoAddRouteGeneratesCorrectRequest(
          version, '10.0.0.0/8', 'next_hop_ip', '1.1.1.1')
      self.assertEqual(response_body['nextHopIp'], '1.1.1.1')

      next_hop_instance_url = command.NormalizePerZoneResourceName(
          EXPECTED_PROJECT, 'zone-1', 'instances', 'my-instance')
      command, response_body = self._DoAddRouteGeneratesCorrectRequest(
          version, '10.0.0.0/8', 'next_hop_instance', next_hop_instance_url)
      self.assertEqual(response_body['nextHopInstance'], next_hop_instance_url)

      command, response_body = self._DoAddRouteGeneratesCorrectRequest(
          version, '10.0.0.0/8', 'next_hop_gateway',
          'default-internet-gateway')
      self.assertEqual(
          response_body['nextHopGateway'],
          command.NormalizeGlobalResourceName(
              EXPECTED_PROJECT, 'gateways', 'default-internet-gateway'))

  def testGetRouteGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)

    command = route_cmds.GetRoute('getroute', flag_values)

    expected_route = 'test_route'
    flag_values.project = EXPECTED_PROJECT

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()

    result = command.Handle(expected_route)

    self.assertEqual(result['project'], EXPECTED_PROJECT)
    self.assertEqual(result['route'], expected_route)

  def testDeleteRouteGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)

    command = route_cmds.DeleteRoute('deleteroute', flag_values)

    expected_route = 'test_route'
    flag_values.project = EXPECTED_PROJECT

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    command._credential = old_mock_api.MockCredential()

    results, exceptions = command.Handle(expected_route)
    self.assertEqual(exceptions, [])
    self.assertEqual(len(results['items']), 1)
    result = results['items'][0]

    self.assertEqual(result['project'], EXPECTED_PROJECT)
    self.assertEqual(result['route'], expected_route)

  def testDeleteMultipleRoutes(self):
    flag_values = copy.deepcopy(FLAGS)
    command = route_cmds.DeleteRoute('deleteroute', flag_values)

    expected_routes = ['test-routes-%02d' % x for x in xrange(100)]
    flag_values.project = EXPECTED_PROJECT

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    command._credential = old_mock_api.MockCredential()

    results, exceptions = command.Handle(*expected_routes)
    self.assertEqual(exceptions, [])
    results = results['items']
    self.assertEqual(len(results), len(expected_routes))

    for expected_route, result in zip(expected_routes, results):
      self.assertEqual(result['project'], EXPECTED_PROJECT)
      self.assertEqual(result['route'], expected_route)


if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
