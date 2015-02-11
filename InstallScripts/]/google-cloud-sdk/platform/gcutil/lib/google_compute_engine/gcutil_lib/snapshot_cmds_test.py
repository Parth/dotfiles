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

"""Unit tests for the persistent disk snapshot commands."""



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
from gcutil_lib import snapshot_cmds


FLAGS = flags.FLAGS


class SnapshotCmdsTest(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)

  def testAddSnapshotsWithFullyQualifiedPaths(self):
    project_flag = 'wrong-project'
    expected_project = 'right-project'
    expected_disk_zone = 'danger-a'
    expected_disk_name = 'deadly'
    expected_snapshot_name = 'snap'

    set_flags = {
        'project': project_flag,
        'wait_until_complete': True
    }

    # In order to get the correct fully qualified paths for the arguments,
    # the command must be initialized once.
    command = self._CreateAndInitializeCommand(
        snapshot_cmds.AddSnapshot, 'addsnapshot', self.version, set_flags)

    submitted_disk = command.NormalizePerZoneResourceName(
        expected_project,
        expected_disk_zone,
        'disks',
        expected_disk_name)

    submitted_snapshot = command.NormalizeGlobalResourceName(
        expected_project,
        'snapshots',
        expected_snapshot_name)

    set_flags['source_disk'] = submitted_disk

    # Now we initialize it again with the extra flag.
    command = self._CreateAndInitializeCommand(
        snapshot_cmds.AddSnapshot, 'addsnapshot', self.version, set_flags)

    snapshot_call = self.mock.Respond('compute.disks.createSnapshot', {})

    # While waiting for operation, we will do a snapshot get.
    self.mock.Respond(
        'compute.snapshots.get',
        {
            'kind': 'compute#snapshot',
            'status': 'READY',
        })

    command.Handle(submitted_snapshot)

    request = snapshot_call.GetRequest()

    parameters = request.parameters
    body = json.loads(request.body)

    self.assertEquals(expected_project, parameters['project'])
    self.assertEquals(expected_disk_zone, parameters['zone'])
    self.assertEquals(expected_disk_name, parameters['disk'])
    self.assertEquals(expected_snapshot_name, body['name'])


class OldSnapshotCmdsTest(unittest.TestCase):

  def _DoTestAddSnapshotGeneratesCorrectRequest(self, service_version):
    flag_values = copy.deepcopy(FLAGS)

    command = snapshot_cmds.AddSnapshot('addsnapshot', flag_values)

    expected_project = 'test_project'
    expected_snapshot = 'test_snapshot'
    expected_description = 'test snapshot'
    submitted_source_disk = 'disk1'
    submitted_zone = 'myzone'
    flag_values.service_version = service_version
    flag_values.source_disk = submitted_source_disk
    flag_values.project = expected_project
    flag_values.description = expected_description

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()

    flag_values.zone = submitted_zone

    expected_source_disk = command.NormalizePerZoneResourceName(
        expected_project,
        submitted_zone,
        'disks',
        submitted_source_disk)

    result = command.Handle(expected_snapshot)

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['body']['name'], expected_snapshot)
    self.assertEqual(result['body']['description'], expected_description)

    self.assertEqual(result['disk'], submitted_source_disk)
    self.assertEqual(result['zone'], submitted_zone)
    expected_source_disk = None
    if expected_source_disk:
      self.assertEqual(result['body']['sourceDisk'], expected_source_disk)

  def testAddSnapshotGeneratesCorrectRequest(self):
    for version in command_base.SUPPORTED_VERSIONS:
      self._DoTestAddSnapshotGeneratesCorrectRequest(version)

  def _DoTestAddSnapshotWithoutZoneGeneratesCorrectRequest(self,
                                                           service_version):
    flag_values = copy.deepcopy(FLAGS)

    command = snapshot_cmds.AddSnapshot('addsnapshot', flag_values)

    expected_project = 'test_project'
    expected_snapshot = 'test_snapshot'
    expected_description = 'test snapshot'
    submitted_source_disk = 'disk1'
    disk_zone = 'us-east-a'
    api_base = 'https://www.googleapis.com/compute/%s' % service_version
    disk_self_link = '%s/projects/%s/zones/%s/disks/%s' % (
        api_base, expected_project, disk_zone, submitted_source_disk)

    flag_values.service_version = service_version
    flag_values.source_disk = submitted_source_disk
    flag_values.project = expected_project
    flag_values.description = expected_description

    disks = {
        'items': {
            ('zones/%s' % disk_zone): {
                'disks': [{
                    'name': 'disk1',
                    'selfLink': disk_self_link
                    }]
            }
        }
    }

    class MockDisksApi(old_mock_api.MockDisksApi):
      def aggregatedList(self, **unused_kwargs):
        return old_mock_api.MockRequest(disks)

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()

    command.api.disks = MockDisksApi()

    expected_source_disk = command.NormalizePerZoneResourceName(
        expected_project,
        disk_zone,
        'disks',
        submitted_source_disk)

    result = command.Handle(expected_snapshot)

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['body']['name'], expected_snapshot)
    self.assertEqual(result['body']['description'], expected_description)

    self.assertEqual(result['disk'], submitted_source_disk)
    self.assertEqual(result['zone'], disk_zone)
    expected_source_disk = None
    if expected_source_disk:
      self.assertEqual(result['body']['sourceDisk'], expected_source_disk)

  def testAddSnapshotWithoutZoneGeneratesCorrectRequest(self):
    for version in command_base.SUPPORTED_VERSIONS:
      self._DoTestAddSnapshotWithoutZoneGeneratesCorrectRequest(version)

  def _DoTestAddSnapshotRequiresSourceDisk(self, version):
    flag_values = copy.deepcopy(FLAGS)

    command = snapshot_cmds.AddSnapshot('addsnapshot', flag_values)

    expected_project = 'test_project'
    expected_snapshot = 'test_snapshot'
    expected_description = 'test snapshot'
    submitted_source_disk = 'disk1'

    flag_values.service_version = version
    flag_values.project = expected_project
    flag_values.description = expected_description
    flag_values.require_tty = False

    command.SetFlags(flag_values)

    def GetDiskPath(disk_name):
      return 'projects/test_project/zones/zone-a/disks/%s' % (disk_name)

    disks = {
        'items': [
            {'name': GetDiskPath('disk1'), 'selfLink': GetDiskPath('disk1')},
            {'name': GetDiskPath('disk2'), 'selfLink': GetDiskPath('disk2')},
            {'name': GetDiskPath('disk3'), 'selfLink': GetDiskPath('disk3')}]}

    class MockDisksApi(old_mock_api.MockDisksApi):
      def list(self, **unused_kwargs):
        return old_mock_api.MockRequest(disks)

    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()

    command.api.disks = MockDisksApi()

    with gcutil_unittest.CaptureStandardIO('1\n\r'):

      result = command.Handle(expected_snapshot)
      self.assertEqual(result['disk'],
                       submitted_source_disk)

  def testAddSnapshotRequiresSourceDisk(self):
    for version in command_base.SUPPORTED_VERSIONS:
      self._DoTestAddSnapshotRequiresSourceDisk(version)

  def _DoTestGetSnapshotGeneratesCorrectRequest(self, service_version):
    flag_values = copy.deepcopy(FLAGS)

    command = snapshot_cmds.GetSnapshot('getsnapshot', flag_values)

    expected_project = 'test_project'
    expected_snapshot = 'test_snapshot'
    flag_values.project = expected_project
    flag_values.service_version = service_version

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()

    result = command.Handle(expected_snapshot)

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['snapshot'], expected_snapshot)

  def testGetSnapshotGeneratesCorrectRequest(self):
    for version in command_base.SUPPORTED_VERSIONS:
      self._DoTestGetSnapshotGeneratesCorrectRequest(version)

  def _DoTestDeleteSnapshotGeneratesCorrectRequest(self, service_version):
    flag_values = copy.deepcopy(FLAGS)

    command = snapshot_cmds.DeleteSnapshot('deletesnapshot', flag_values)

    expected_project = 'test_project'
    expected_snapshot = 'test_snapshot'
    flag_values.project = expected_project

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    command._credential = old_mock_api.MockCredential()
    flag_values.service_version = service_version

    results, exceptions = command.Handle(expected_snapshot)
    self.assertEquals(exceptions, [])
    self.assertEquals(len(results['items']), 1)
    result = results['items'][0]

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['snapshot'], expected_snapshot)

  def testDeleteSnapshotGeneratesCorrectRequest(self):
    for version in command_base.SUPPORTED_VERSIONS:
      self._DoTestDeleteSnapshotGeneratesCorrectRequest(version)

  def testDeleteMultipleSnapshots(self):
    flag_values = copy.deepcopy(FLAGS)
    command = snapshot_cmds.DeleteSnapshot('deletesnapshot', flag_values)

    expected_project = 'test_project'
    expected_snapshots = ['test-snapshot-%02d' % x for x in xrange(100)]
    flag_values.project = expected_project

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    command._credential = old_mock_api.MockCredential()

    results, exceptions = command.Handle(*expected_snapshots)
    self.assertEqual(exceptions, [])
    results = results['items']
    self.assertEqual(len(results), len(expected_snapshots))

    for expected_snapshot, result in zip(expected_snapshots, results):
      self.assertEqual(result['project'], expected_project)
      self.assertEqual(result['snapshot'], expected_snapshot)


if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
