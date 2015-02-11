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

"""Unit tests for the persistent disk commands."""



import path_initializer
path_initializer.InitSysPath()

import json
import StringIO
import sys
import unittest

from google.apputils import app

from gcutil_lib import disk_cmds
from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api
from gcutil_lib import mock_lists
from gcutil_lib import version


class DiskCmdsTest(gcutil_unittest.GcutilTestCase):

  # The number of disks used in the tests.
  NUMBER_OF_DISKS = 30

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)

  def _DoTestAddDisks(self, service_version, disks,
                      source_snapshot=None, size=None,
                      source_image=None, wait_until_complete=None):
    expected_kind = 'compute#disk'
    expected_project = 'test_project'
    expected_description = 'test disk'
    expected_zone = 'copernicus-moon-base'
    provisioning_calls = 1

    set_flags = {
        'zone': expected_zone,
        'project': expected_project,
        'size_gb': size,
        'source_image': source_image,
        'description': expected_description,
        'wait_until_complete': wait_until_complete,
        'sleep_between_polls': 0.1,
        'source_snapshot': source_snapshot
        }
    expected_disk_type = 'pd-ssd'
    set_flags['disk_type'] = expected_disk_type

    command = self._CreateAndInitializeCommand(
        disk_cmds.AddDisk, 'adddisk', service_version, set_flags)

    # If an image is specified, we will simply fall through the image resolver.
    if source_image:
      mock_lists.MockImageListForCustomerAndStandardProjects(command, self.mock)

    if wait_until_complete:
      # Spend some queries in provisioning state.
      provisioning = [provisioning_calls]

      def GetResponse(unused_uri, unused_http_method, parameters, unused_body):
        if provisioning[0]:
          status = 'PROVISIONING'
          provisioning[0] -= 1
        else:
          status = 'READY'

        return self.mock.MOCK_RESPONSE(
            {
                'kind': 'compute#disk',
                'name': parameters['disk'],
                'zone': command.NormalizeGlobalResourceName(expected_project,
                                                            'zones',
                                                            parameters['zone']),
                'status': status
            },
            False)

      getcall = self.mock.RespondF('compute.disks.get', GetResponse)

    def DiskResponse(unused_uri, unused_http_method, parameters, body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#disk',
              'name': json.loads(body)['name'],
              'zone': command.NormalizeGlobalResourceName(expected_project,
                                                          'zones',
                                                          parameters['zone']),
              'selfLink': command.NormalizePerZoneResourceName(
                  expected_project,
                  parameters['zone'],
                  'disks',
                  json.loads(body)['name']),
              'status': 'PROVISIONING'
          },
          False)

    diskcall = self.mock.RespondF('compute.disks.insert', DiskResponse)

    # Make the call and ensure that nothing went wrong.
    results, exceptions = command.Handle(*disks)
    self.assertEqual([], exceptions)
    results = results['items']
    self.assertEqual(len(results), len(disks))

    # If we waited for completion, validate the "get" calls.
    if wait_until_complete:
      get_requests = getcall.GetAllRequests()
      self.assertEqual(provisioning_calls + len(disks), len(get_requests))
      for request in get_requests:
        self.assertEqual(expected_zone, request.parameters['zone'])
        self.assertTrue(request.parameters['disk'] in disks)

    # Validate the "insert" calls.
    remaining_disks = disks

    for request in diskcall.GetAllRequests():
      parameters = request.parameters
      body = json.loads(request.body)

      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_kind, body['kind'])
      self.assertEqual(expected_description, body['description'])
      if self.version >= version.get('v1'):
        expected_normalized_disk_type = command.NormalizePerZoneResourceName(
            expected_project,
            expected_zone,
            'diskTypes',
            expected_disk_type)
        self.assertEqual(expected_normalized_disk_type, body['type'])
      self.assertEqual(expected_zone, parameters['zone'])
      self.assertFalse('zone' in body)

      if size:
        self.assertEqual(size, body['sizeGb'])

      if source_snapshot:
        self.assertTrue(body['sourceSnapshot'].endswith(source_snapshot))
      elif source_image:
        self.assertTrue(parameters['sourceImage'].endswith(source_image))
      elif not size:
        self.assertEqual('100', body['sizeGb'])

      self.assertTrue(body['name'] in remaining_disks)
      remaining_disks = [disk for disk in remaining_disks
                         if disk != body['name']]

  def testAddDiskAndWaitUntilCompletion(self):
    self._DoTestAddDisks(self.version, disks=['test_disk'],
                         size='12', wait_until_complete=True)

  def testAddMultipleDisks(self):
    self._DoTestAddDisks(
        self.version, size='12',
        disks=['test-disk-%02d' % i
               for i in xrange(self.NUMBER_OF_DISKS)])

  def testAddDiskFromSnapshotGeneratesCorrectRequest(self):
    self._DoTestAddDisks(self.version, disks=['test_disk'],
                         source_snapshot='snap')

  def testAddDiskFromSnapshotWithSizeSpecified(self):
    self._DoTestAddDisks(self.version, disks=['test_disk'],
                         source_snapshot='snap', size='100')

  def testAddDiskDefaultSizeGb(self):
    self._DoTestAddDisks(self.version, disks=['test_disk'])

  def testAddDiskFromImageDoesNotPassSizeGbUnlessExplicitlySet(self):
    self._DoTestAddDisks(self.version, disks=['test_disk'],
                         source_image='images/image1')

  def testAddDiskFromImageGeneratesCorrectRequest(self):
    self._DoTestAddDisks(self.version, disks=['test_disk'],
                         size='12', source_image='image1')

  def testAddWithNoDisk(self):
    command = self._CreateAndInitializeCommand(disk_cmds.AddDisk, 'adddisk')
    self.assertRaises(app.UsageError, command.Handle)

  def testAddWithIncompatibleFlagsFails(self):
    set_flags = {
        'source_image': 'image',
        'source_snapshot': 'snap'
        }
    command = self._CreateAndInitializeCommand(
        disk_cmds.AddDisk, 'adddisk', set_flags=set_flags)
    self.assertRaises(app.UsageError, command.Handle)

  def testAddDiskRequiresZone(self):
    expected_project = 'test_project'
    expected_disk = 'test_disk'
    expected_description = 'test disk'
    expected_size = '20'
    selected_zone = 2

    set_flags = {
        'project': expected_project,
        'size_gb': expected_size,
        'description': expected_description
        }

    command = self._CreateAndInitializeCommand(
        disk_cmds.AddDisk, 'adddisk', self.version, set_flags=set_flags)

    self.mock.Respond('compute.zones.list',
                      {
                          'items': [{'name': 'us-east-a'},
                                    {'name': 'us-east-b'},
                                    {'name': 'us-east-c'},
                                    {'name': 'us-west-a'}]
                      })

    def ZoneResponse(unused_uri, unused_http_method, parameters, unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#zone',
              'name': parameters['zone'],
          },
          False)

    self.mock.RespondF('compute.zones.get', ZoneResponse)

    def DiskResponse(unused_uri, unused_http_method, parameters, body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#disk',
              'name': json.loads(body)['name'],
              'zone': command.NormalizeGlobalResourceName(expected_project,
                                                          'zones',
                                                          parameters['zone'])
          },
          False)

    diskcall = self.mock.RespondF('compute.disks.insert', DiskResponse)

    oldin = sys.stdin
    sys.stdin = StringIO.StringIO('%d\n\r' % selected_zone)
    oldout = sys.stdout
    sys.stdout = StringIO.StringIO()

    unused_results, exceptions = command.Handle(expected_disk)
    self.assertEqual(exceptions, [])

    requests = diskcall.GetAllRequests()
    self.assertEquals(len(requests), 1)
    request = requests[0]

    self.assertEqual('us-east-b', request.parameters['zone'])

    sys.stdin = oldin
    sys.stdout = oldout

  def _DoTestGetDiskGeneratesCorrectRequest(self, service_version):
    expected_project = 'test_project'
    expected_disk = 'test_disk'
    expected_zone = 'copernicus-moon-base'

    set_flags = {
        'zone': expected_zone,
        'project': expected_project,
        }

    command = self._CreateAndInitializeCommand(
        disk_cmds.GetDisk, 'getdisk', service_version, set_flags)

    def DiskResponse(unused_uri, unused_http_method, parameters, unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#disk',
              'name': parameters['disk'],
              'project': parameters['project'],
              'zone': command.NormalizeGlobalResourceName(expected_project,
                                                          'zones',
                                                          parameters['zone'])
          },
          True)

    getcall = self.mock.RespondF('compute.disks.get', DiskResponse)

    unused_result = command.Handle(expected_disk)

    requests = getcall.GetAllRequests()
    self.assertEquals(len(requests), 1)
    request = requests[0]

    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_disk, request.parameters['disk'])
    self.assertEqual(expected_zone, request.parameters['zone'])

  def testGetDiskGeneratesCorrectRequest(self):
    self._DoTestGetDiskGeneratesCorrectRequest(self.version)

  def _DoTestDeleteDisks(self, service_version, disks):
    expected_zone = 'zone-a'
    expected_project = 'test_project'

    set_flags = {
        'zone': expected_zone,
        'project': expected_project,
        }

    command = self._CreateAndInitializeCommand(
        disk_cmds.DeleteDisk, 'deletedisk', service_version, set_flags)

    def DeleteResponse(unused_uri, unused_http_method, parameters,
                       unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'name': parameters['disk'],
              'operationType': 'delete',
              'project': parameters['project'],
              'status': 'DONE',
              'targetLink': command.NormalizeGlobalResourceName(
                  expected_project,
                  'projects',
                  parameters['disk']),
              'zone': command.NormalizeGlobalResourceName(expected_project,
                                                          'zones',
                                                          parameters['zone'])
          },
          False)

    deletecall = self.mock.RespondF('compute.disks.delete', DeleteResponse)

    results, exceptions = command.Handle(*disks)
    self.assertEqual(len(results['items']), len(disks))
    self.assertEqual(exceptions, [])

    for request in deletecall.GetAllRequests():
      parameters = request.parameters

      self.assertEqual(parameters['project'], expected_project)
      self.assertEqual(parameters['zone'], expected_zone)

      self.assertTrue(parameters['disk'] in disks)
      disks = [disk for disk in disks
               if disk != parameters['disk']]

  def testAddDisksWithFullyQualifiedPaths(self):
    disks = ['test_disk1',
             'disks/test_disk2',
             'danger-a/disks/test_disk3',
             'zones/danger-a/disks/test_disk4',
             'other_project/zones/danger-a/disks/test_disk5']

    flag_project = 'test_project'
    flag_zone = 'copernicus-moon-base'

    expected = {
        'test_disk1': {
            'zone': flag_zone,
            'project': flag_project
        },
        'test_disk2': {
            'zone': flag_zone,
            'project': flag_project
        },
        'test_disk3': {
            'zone': 'danger-a',
            'project': flag_project
        },
        'test_disk4': {
            'zone': 'danger-a',
            'project': flag_project
        },
        'test_disk5': {
            'zone': 'danger-a',
            'project': 'other_project'
        }
    }

    set_flags = {
        'zone': flag_zone,
        'project': flag_project,
        }

    command = self._CreateAndInitializeCommand(
        disk_cmds.AddDisk, 'adddisk', self.version, set_flags)

    def DiskResponse(unused_uri, unused_http_method, parameters, body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#disk',
              'name': json.loads(body)['name'],
              'zone': command.NormalizeGlobalResourceName(parameters['project'],
                                                          'zones',
                                                          parameters['zone']),
              'status': 'PROVISIONING'
          },
          False)

    diskcall = self.mock.RespondF('compute.disks.insert', DiskResponse)

    def ZoneResponse(unused_uri, unused_http_method, parameters, unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#zone',
              'name': parameters['zone'],
          },
          False)

    unused_zonecall = self.mock.RespondF('compute.zones.get', ZoneResponse)

    unused_result = command.Handle(*disks)

    requests = diskcall.GetAllRequests()
    self.assertEqual(len(disks), len(requests))

    for request in requests:
      parameters = request.parameters
      body = json.loads(request.body)
      self.assertTrue(body['name'] in expected)

      expected_request = expected[body['name']]
      self.assertEqual(expected_request['zone'], parameters['zone'])
      self.assertEqual(expected_request['project'], parameters['project'])

  def testDeleteDiskGeneratesCorrectRequest(self):
    self._DoTestDeleteDisks(self.version, disks=['test_disk'])

  def testDeleteMultipleDisks(self):
    self._DoTestDeleteDisks(self.version,
                            disks=['test-disk-%02d' % x for x in
                                   xrange(self.NUMBER_OF_DISKS)])

  def testListDisks(self):
    expected_zone = 'the-danger-zone'
    expected_project = 'test_project'

    set_flags = {
        'zone': expected_zone,
        'project': expected_project,
        }

    command = self._CreateAndInitializeCommand(
        disk_cmds.ListDisks, 'listdisks', self.version, set_flags)

    listcall = mock_lists.GetSampleDiskListCall(command, self.mock)

    command.Handle()
    requests = listcall.GetAllRequests()

    self.assertEquals(len(requests), 1)

    request = requests[0]

    self.assertEquals(expected_zone, request.parameters['zone'])
    self.assertEquals(expected_project, request.parameters['project'])

if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
