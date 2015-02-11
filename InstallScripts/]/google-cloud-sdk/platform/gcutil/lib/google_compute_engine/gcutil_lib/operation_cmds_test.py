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

"""Unit tests for the asynchronous operations commands."""



import path_initializer
path_initializer.InitSysPath()

import copy

import gflags as flags
import unittest

from gcutil_lib import command_base
from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api
from gcutil_lib import old_mock_api
from gcutil_lib import operation_cmds

FLAGS = flags.FLAGS


class OperationCmdsTest(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)

  def testFullyQualifiedDeleteOperation(self):
    project_flag = 'wrong-project'
    global_op_name = 'global-op'
    region_op_name = 'region-op'
    zone_op_name = 'zone-op'
    project_name = 'right-project'
    region_name = 'region-of-danger'
    zone_name = 'danger-zone'

    set_flags = {
        'project': project_flag,
    }

    command = self._CreateAndInitializeCommand(operation_cmds.DeleteOperation,
                                               'deleteoperation',
                                               self.version,
                                               set_flags)

    global_operation = command.NormalizeGlobalResourceName(project_name,
                                                           'operations',
                                                           global_op_name)

    region_operation = command.NormalizePerRegionResourceName(project_name,
                                                              region_name,
                                                              'operations',
                                                              region_op_name)

    zone_operation = command.NormalizePerZoneResourceName(project_name,
                                                          zone_name,
                                                          'operations',
                                                          zone_op_name)

    global_call = self.mock.Respond('compute.globalOperations.delete', {})
    region_call = self.mock.Respond('compute.regionOperations.delete', {})
    zone_call = self.mock.Respond('compute.zoneOperations.delete', {})

    command.Handle(global_operation, region_operation, zone_operation)

    global_request = global_call.GetRequest()
    parameters = global_request.parameters
    self.assertEquals(project_name, parameters['project'])
    self.assertEquals(global_op_name, parameters['operation'])

    region_request = region_call.GetRequest()
    parameters = region_request.parameters
    self.assertEquals(project_name, parameters['project'])
    self.assertEquals(region_op_name, parameters['operation'])
    self.assertEquals(region_name, parameters['region'])

    zone_request = zone_call.GetRequest()
    parameters = zone_request.parameters
    self.assertEquals(project_name, parameters['project'])
    self.assertEquals(zone_op_name, parameters['operation'])
    self.assertEquals(zone_name, parameters['zone'])

  def testDeleteMultipleOperations(self):
    project_flag = 'right-project'

    set_flags = {
        'project': project_flag,
    }

    command = self._CreateAndInitializeCommand(operation_cmds.DeleteOperation,
                                               'deleteoperation',
                                               self.version,
                                               set_flags)

    expected_operations = ['test-operation-%02d' % x for x in xrange(100)]

    self.mock.RespondN('compute.globalOperations.aggregatedList', {}, 100)
    self.mock.RespondN('compute.globalOperations.delete', {}, 100)

    results, exceptions = command.Handle(*expected_operations)

    self.assertEqual(exceptions, [])
    self.assertEqual(results, '')

  def testDeleteGlobalOperation(self):
    project_flag = 'right-project'
    expected_operation = 'global-op'

    set_flags = {
        'project': project_flag,
    }

    command = self._CreateAndInitializeCommand(operation_cmds.DeleteOperation,
                                               'deleteoperation',
                                               self.version,
                                               set_flags)

    self.mock.Respond(
        'compute.globalOperations.aggregatedList',
        {
            'items': {
                'global': {'operations': [{'name': expected_operation}]},
                'zone/danger-a': {'warning': 'No results'},
                'region/danger': {'warning': 'No results'},
            }
        })
    self.mock.Respond('compute.globalOperations.delete', {})

    results, exceptions = command.Handle(expected_operation)

    self.assertEqual(exceptions, [])
    self.assertEqual(results, '')

  def testDeleteRegionalOperation(self):
    project_flag = 'right-project'
    expected_operation = 'regional-op'

    set_flags = {
        'project': project_flag,
    }

    command = self._CreateAndInitializeCommand(operation_cmds.DeleteOperation,
                                               'deleteoperation',
                                               self.version,
                                               set_flags)

    self.mock.RespondN(
        'compute.globalOperations.aggregatedList',
        {
            'items': {
                'region/danger': {'operations': [{'name': expected_operation}]},
                'zone/danger-a': {'warning': 'No results'},
                'global': {'warning': 'No results'},
            }
        }, 2)
    self.mock.Respond('compute.globalOperations.delete', {})

    results, exceptions = command.Handle(expected_operation)

    self.assertEqual(exceptions, [])
    self.assertEqual(results, '')

  def testDeleteZonalOperation(self):
    project_flag = 'right-project'
    expected_operation = 'zonal-op'

    set_flags = {
        'project': project_flag,
    }

    command = self._CreateAndInitializeCommand(operation_cmds.DeleteOperation,
                                               'deleteoperation',
                                               self.version,
                                               set_flags)

    self.mock.RespondN(
        'compute.globalOperations.aggregatedList',
        {
            'items': {
                'zone/danger-a': {'operations': [{'name': expected_operation}]},
                'region/danger': {'warning': 'No results'},
                'global': {'warning': 'No results'},
            }
        }, 2)
    self.mock.Respond('compute.globalOperations.delete', {})

    results, exceptions = command.Handle(expected_operation)

    self.assertEqual(exceptions, [])
    self.assertEqual(results, '')


class OldOperationCmdsTest(unittest.TestCase):

  def _DoTestGetOperationGeneratesCorrectRequest(self, service_version):
    flag_values = copy.deepcopy(FLAGS)

    command = operation_cmds.GetOperation('getoperation', flag_values)

    expected_project = 'test_project'
    expected_operation = 'test_operation'
    flag_values.project = expected_project
    flag_values.service_version = service_version

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    submitted_zone = 'myzone'
    flag_values.zone = submitted_zone

    result = command.Handle(expected_operation)

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['operation'], expected_operation)

    api = command.api.global_operations
    api = command.api.zone_operations

    self.assertEquals(1, len(api.requests))
    request = api.requests[0]
    self.assertEqual(submitted_zone, request.request_payload['zone'])
    self.assertEqual(expected_project, request.request_payload['project'])
    self.assertEqual(expected_operation, request.request_payload['operation'])

  def testGetOperationGeneratesCorrectRequest(self):
    for version in command_base.SUPPORTED_VERSIONS:
      self._DoTestGetOperationGeneratesCorrectRequest(version)

  def _DoTestDeleteOperationGeneratesCorrectRequest(self, service_version):
    flag_values = copy.deepcopy(FLAGS)

    command = operation_cmds.DeleteOperation('deleteoperation', flag_values)

    expected_project = 'test_project'
    expected_operation = 'test_operation'
    flag_values.project = expected_project
    flag_values.service_version = service_version

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    command._credential = old_mock_api.MockCredential()
    submitted_zone = 'myzone'
    flag_values.zone = submitted_zone

    results, exceptions = command.Handle(expected_operation)
    self.assertEqual(exceptions, [])
    self.assertEqual(results, '')

    # Verify the request
    api = command.api.zone_operations

    self.assertEquals(1, len(api.requests))
    request = api.requests[0]
    self.assertEqual(submitted_zone, request.request_payload['zone'])
    self.assertEqual(expected_project, request.request_payload['project'])
    self.assertEqual(expected_operation, request.request_payload['operation'])

  def testDeleteOperationGeneratesCorrectRequest(self):
    for version in command_base.SUPPORTED_VERSIONS:
      self._DoTestDeleteOperationGeneratesCorrectRequest(version)

  def _DoTestGetGlobalOperationGeneratesCorrectRequest(self, service_version):
    flag_values = copy.deepcopy(FLAGS)

    command = operation_cmds.GetOperation('getoperation', flag_values)

    expected_project = 'test_project'
    expected_operation = 'test_operation'
    flag_values.project = expected_project
    flag_values.service_version = service_version
    flag_values.zone = command_base.GLOBAL_SCOPE_NAME

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    command._credential = old_mock_api.MockCredential()

    command.Handle(expected_operation)

    # Verify the request
    self.assertEquals(1, len(command.api.global_operations.requests))
    request = command.api.global_operations.requests[0]
    self.assertEqual('get', request.method_name)
    self.assertEqual(expected_project, request.request_payload['project'])
    self.assertEqual(expected_operation, request.request_payload['operation'])

  def testGetGlobalOperationGeneratesCorrectRequest(self):
    for version in command_base.SUPPORTED_VERSIONS:
      self._DoTestGetGlobalOperationGeneratesCorrectRequest(version)

  def _DoTestDeleteGlobalOperationGeneratesCorrectRequest(self,
                                                          service_version):
    flag_values = copy.deepcopy(FLAGS)

    command = operation_cmds.DeleteOperation('deleteoperation', flag_values)

    expected_project = 'test_project'
    expected_operation = 'test_operation'
    flag_values.project = expected_project
    flag_values.service_version = service_version
    flag_values.zone = command_base.GLOBAL_SCOPE_NAME

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    command._credential = old_mock_api.MockCredential()

    results, exceptions = command.Handle(expected_operation)
    self.assertEqual(exceptions, [])
    self.assertEqual(results, '')

    # Verify the request
    self.assertEquals(1, len(command.api.global_operations.requests))
    request = command.api.global_operations.requests[0]
    self.assertEqual('delete', request.method_name)
    self.assertEqual(expected_project, request.request_payload['project'])
    self.assertEqual(expected_operation, request.request_payload['operation'])

  def testDeleteGlobalOperationGeneratesCorrectRequest(self):
    for version in command_base.SUPPORTED_VERSIONS:
      self._DoTestDeleteGlobalOperationGeneratesCorrectRequest(version)

  def _DoTestGetRegionOperation(self, flag_values):
    command = operation_cmds.GetOperation('getoperation', flag_values)

    expected_project = 'region-test-project'
    expected_operation = 'region-test-operation'

    submitted_region = 'my-test-region'

    flag_values.project = expected_project
    flag_values.region = submitted_region

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    command._credential = old_mock_api.MockCredential()

    result = command.Handle(expected_operation)

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['operation'], expected_operation)

    api = command.api.region_operations

    self.assertEquals(1, len(api.requests))
    request = api.requests[0]
    self.assertEqual(submitted_region, request.request_payload['region'])

    self.assertEqual(expected_project, request.request_payload['project'])
    self.assertEqual(expected_operation, request.request_payload['operation'])

  def testGetRegionOperation(self):
    for version in command_base.SUPPORTED_VERSIONS:
      flag_values = copy.deepcopy(FLAGS)
      flag_values.service_version = version
      self._DoTestGetRegionOperation(flag_values)

  def _DoTestDeleteRegionOperation(self, flag_values):
    command = operation_cmds.DeleteOperation('deleteoperation', flag_values)

    expected_project = 'region-test-project'
    expected_operation = 'region-test-operation'

    submitted_region = 'my-test-region'

    flag_values.project = expected_project
    flag_values.region = submitted_region

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    command._credential = old_mock_api.MockCredential()

    results, exceptions = command.Handle(expected_operation)
    self.assertEqual(exceptions, [])
    self.assertEqual(results, '')

    api = command.api.region_operations

    self.assertEquals(1, len(api.requests))
    request = api.requests[0]
    self.assertEqual(submitted_region, request.request_payload['region'])

    self.assertEqual(expected_project, request.request_payload['project'])
    self.assertEqual(expected_operation, request.request_payload['operation'])

  def testDeleteRegionOperation(self):
    for version in command_base.SUPPORTED_VERSIONS:
      flag_values = copy.deepcopy(FLAGS)
      flag_values.service_version = version
      self._DoTestDeleteRegionOperation(flag_values)


if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
