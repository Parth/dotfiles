# Copyright 2014 Google Inc. All Rights Reserved.
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

"""Unit tests for the disk type commands."""



import path_initializer
path_initializer.InitSysPath()

import unittest

from gcutil_lib import disk_type_cmds
from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api
from gcutil_lib import mock_lists


class DiskTypeCmdsTest(gcutil_unittest.GcutilTestCase):

  _SUPPORTED_API_VERSIONS = ('v1',)

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)
    self.expected_zone = 'test-zone'
    self.expected_project = 'test-project'
    self.expected_disk_type = 'test-disk-type'

  def testGetDiskTypeGeneratesCorrectRequest(self):
    set_flags = {
        'project': self.expected_project,
        'zone': self.expected_zone
    }

    command = self._CreateAndInitializeCommand(
        disk_type_cmds.GetDiskType,
        'getdisktype',
        self.version,
        set_flags)

    get_call = self.mock.Respond('compute.diskTypes.get', {
        'kind': 'compute#diskType',
        'zone': self.expected_zone,
        'name': self.expected_disk_type,
        })

    self.mock.Respond('compute.zones.get', {
        'kind': 'compute#zone',
        'name': self.expected_zone,
        })

    command.Handle(self.expected_disk_type)

    requests = get_call.GetAllRequests()
    self.assertEquals(1, len(requests))
    request = requests[0]

    self.assertEqual(self.expected_disk_type, request.parameters['diskType'])
    self.assertEqual(self.expected_zone, request.parameters['zone'])

  def testGetDiskTypePromptsForZone(self):
    set_flags = {
        'project': self.expected_project,
    }

    command = self._CreateAndInitializeCommand(
        disk_type_cmds.GetDiskType,
        'getdisktype',
        self.version,
        set_flags)

    get_call = self.mock.Respond('compute.diskTypes.get', {
        'kind': 'compute#diskType',
        'zone': self.expected_zone,
        'name': self.expected_disk_type,
        })

    mock_lists.GetSampleZoneListCall(
        command, self.mock, 1, name=[self.expected_zone])

    command.Handle(self.expected_disk_type)

    requests = get_call.GetAllRequests()
    self.assertEquals(1, len(requests))
    request = requests[0]

    self.assertEqual(self.expected_disk_type, request.parameters['diskType'])
    self.assertEqual(self.expected_zone, request.parameters['zone'])

  def testGetDiskTypeWithFullyQualifiedPaths(self):
    set_flags = {
        'project': 'wrong-project',
        'zone': 'wrong-zone',
    }

    command = self._CreateAndInitializeCommand(
        disk_type_cmds.GetDiskType,
        'getdisktype',
        self.version,
        set_flags)

    qualified_path = command.NormalizeResourceName(
        self.expected_project,
        'zones/%s' % self.expected_zone,
        'diskTypes',
        self.expected_disk_type)

    get_call = self.mock.Respond('compute.diskTypes.get', {
        'kind': 'compute#diskType',
        'zone': self.expected_zone,
        'name': self.expected_disk_type,
        })

    self.mock.Respond('compute.zones.get', {
        'kind': 'compute#zone',
        'name': self.expected_zone,
        })

    command.Handle(qualified_path)

    requests = get_call.GetAllRequests()
    self.assertEquals(1, len(requests))
    request = requests[0]

    self.assertEqual(self.expected_project, request.parameters['project'])
    self.assertEqual(self.expected_disk_type, request.parameters['diskType'])
    self.assertEqual(self.expected_zone, request.parameters['zone'])

  def testListDiskTypes(self):
    command = self._CreateAndInitializeCommand(
        disk_type_cmds.ListDiskTypes, 'listdisktypes', self.version)

    set_flags = {
        'project': self.expected_project,
        'zone': self.expected_zone,
        }

    command = self._CreateAndInitializeCommand(
        disk_type_cmds.ListDiskTypes,
        'listdisktypes',
        self.version,
        set_flags)

    list_call = mock_lists.GetSampleDiskTypeListCall(command, self.mock)

    command.Handle()

    requests = list_call.GetAllRequests()
    self.assertEquals(len(requests), 1)
    request = requests[0]

    self.assertEquals(self.expected_project, request.parameters['project'])
    self.assertEquals(self.expected_zone, request.parameters['zone'])

if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
