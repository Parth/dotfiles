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

"""Unit tests for the machine type commands."""



import path_initializer
path_initializer.InitSysPath()

import unittest

from gcutil_lib import gcutil_unittest
from gcutil_lib import machine_type_cmds
from gcutil_lib import mock_api
from gcutil_lib import mock_lists


class MachineTypeCmdsTest(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)

  def testGetMachineTypeGeneratesCorrectRequest(self):
    expected_zone = 'test-zone'
    expected_project = 'test-project'
    expected_machine_type = 't1000'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone
    }

    command = self._CreateAndInitializeCommand(
        machine_type_cmds.GetMachineType, 'getmachinetype',
        self.version, set_flags)

    machinecall = self.mock.Respond('compute.machineTypes.get', {
        'kind': 'compute#machineType',
        'zone': expected_zone,
        'name': expected_machine_type,
        })

    self.mock.Respond('compute.zones.get', {
        'kind': 'compute#zone',
        'name': expected_zone,
        })

    command.Handle(expected_machine_type)

    requests = machinecall.GetAllRequests()
    self.assertEquals(1, len(requests))
    request = requests[0]

    self.assertEqual(expected_machine_type, request.parameters['machineType'])
    self.assertEqual(expected_zone, request.parameters['zone'])

  def testGetMachineTypePromptsForZone(self):
    expected_project = 'test-project'
    expected_machine_type = 'party-machine'
    expected_zone = 'danger-a'

    set_flags = {
        'project': expected_project,
    }

    command = self._CreateAndInitializeCommand(
        machine_type_cmds.GetMachineType, 'getmachinetype',
        self.version, set_flags)

    machinecall = self.mock.Respond('compute.machineTypes.get', {
        'kind': 'compute#machineType',
        'zone': expected_zone,
        'name': expected_machine_type,
        })

    mock_lists.GetSampleZoneListCall(
        command, self.mock, 1, name=[expected_zone])

    command.Handle(expected_machine_type)

    requests = machinecall.GetAllRequests()
    self.assertEquals(1, len(requests))
    request = requests[0]

    self.assertEqual(expected_machine_type, request.parameters['machineType'])
    self.assertEqual(expected_zone, request.parameters['zone'])

  def testGetMachineTypeWithFullyQualifiedPaths(self):
    expected_zone = 'test-zone'
    expected_project = 'test-project'
    expected_machine_type = 't1000'

    set_flags = {
        'project': 'wrong-project',
        'zone': 'wrong-zone',
    }

    command = self._CreateAndInitializeCommand(
        machine_type_cmds.GetMachineType, 'getmachinetype',
        self.version, set_flags)

    qualified_path = command.NormalizeResourceName(expected_project,
                                                   'zones/%s' % expected_zone,
                                                   'machineTypes',
                                                   expected_machine_type)

    machinecall = self.mock.Respond('compute.machineTypes.get', {
        'kind': 'compute#machineType',
        'zone': expected_zone,
        'name': expected_machine_type,
        })

    self.mock.Respond('compute.zones.get', {
        'kind': 'compute#zone',
        'name': expected_zone,
        })

    command.Handle(qualified_path)

    requests = machinecall.GetAllRequests()
    self.assertEquals(1, len(requests))
    request = requests[0]

    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_machine_type, request.parameters['machineType'])
    self.assertEqual(expected_zone, request.parameters['zone'])

  def testListMachineTypes(self):
    expected_zone = 'the-twilight-zone'
    expected_project = 'test-project'

    command = self._CreateAndInitializeCommand(
        machine_type_cmds.ListMachineTypes, 'listmachinetypes', self.version)

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        }

    command = self._CreateAndInitializeCommand(
        machine_type_cmds.ListMachineTypes, 'listmachinetypes',
        self.version, set_flags)

    listcall = mock_lists.GetSampleMachineTypeListCall(command, self.mock)

    command.Handle()
    requests = listcall.GetAllRequests()

    self.assertEquals(len(requests), 1)

    request = requests[0]

    self.assertEquals(expected_project, request.parameters['project'])
    self.assertEquals(expected_zone, request.parameters['zone'])

if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
