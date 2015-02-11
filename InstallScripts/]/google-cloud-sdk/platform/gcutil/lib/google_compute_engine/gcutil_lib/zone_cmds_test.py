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

"""Unit tests for the zone commands."""

import path_initializer
path_initializer.InitSysPath()

import datetime
import unittest

from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api
from gcutil_lib import mock_lists
from gcutil_lib import zone_cmds


class ZoneCmdsTest(gcutil_unittest.GcutilTestCase):
  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)

  def testGetZoneRequest(self):
    set_flags = {
        'project': 'my-project',
        }

    command = self._CreateAndInitializeCommand(
        zone_cmds.GetZone, 'getzone', self.version, set_flags)

    call = self.mock.Respond(
        'compute.zones.get',
        {
            'kind': 'compute#zone',
            'name': 'us-west-a'
        })

    command.Handle('us-west1-a')
    request = call.GetRequest()

    self.assertEquals('GET', request.method)
    self.assertEquals(None, request.body)

    parameters = request.parameters
    self.assertTrue('project' in parameters)
    self.assertEquals('my-project', parameters['project'])
    self.assertTrue('zone' in parameters)
    self.assertEquals('us-west1-a', parameters['zone'])

  def testGetZoneWithFullyQualifiedPathRequest(self):
    set_flags = {
        'project': 'wrong-project',
        }

    command = self._CreateAndInitializeCommand(
        zone_cmds.GetZone, 'getzone', self.version, set_flags)

    call = self.mock.Respond(
        'compute.zones.get',
        {
            'kind': 'compute#zone',
            'name': 'danger-zone',
        })

    command.Handle('right-project/zones/danger-zone')
    request = call.GetRequest()

    self.assertEquals('GET', request.method)

    parameters = request.parameters
    self.assertEquals('right-project', parameters['project'])
    self.assertEquals('danger-zone', parameters['zone'])

  def testListZones(self):
    expected_project = 'neat-project'

    set_flags = {
        'project': expected_project
        }

    command = self._CreateAndInitializeCommand(
        zone_cmds.ListZones, 'listzones', self.version, set_flags)

    listcall = mock_lists.GetSampleZoneListCall(command, self.mock, 3)

    results = command.Handle()
    requests = listcall.GetAllRequests()

    self.assertEquals(1, len(requests))

    request = requests[0]
    self.assertEquals(expected_project, request.parameters['project'])

    # The handler does some additional processing.  Make sure the result
    # is correct.
    for result in results['items']:
      self.assertTrue('next_maintenance_window' in result)

    # By design, the next maintenance window of the first entry should be
    # unspecified.  The other two should be the same.
    self.assertEquals('None scheduled',
                      results['items'][0]['next_maintenance_window'])
    self.assertEquals(datetime.datetime(2013, 1, 1, 12, 0, 0).isoformat(),
                      results['items'][1]['next_maintenance_window'])
    self.assertEquals(datetime.datetime(2013, 1, 1, 12, 0, 0).isoformat(),
                      results['items'][2]['next_maintenance_window'])

    # Test pretty printing on one of the results.
    command = self._CreateAndInitializeCommand(
        zone_cmds.GetZone, 'getzone', self.version, set_flags)

    data = command.GetDetailRow(results['items'][2])

    expected_data = {
        'v1': [
            ('maintenance-window',
             [('name', 'name-1'),
              ('description', 'description-1'),
              ('begin-time', '2013-01-02T12:00:00'),
              ('end-time', '2013-01-02T13:00:00')]),
            ('maintenance-window',
             [('name', 'name-0'),
              ('description', 'description-0'),
              ('begin-time', '2013-01-01T12:00:00'),
              ('end-time', '2013-01-01T13:00:00')])],
    }

    self.assertEquals(
        gcutil_unittest.SelectTemplateForVersion(
            expected_data, command.api.version),
        data)


if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
