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

"""Unit tests for address collection commands."""



import path_initializer
path_initializer.InitSysPath()

import json
import unittest

import gflags as flags
from gcutil_lib import address_cmds
from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api
from gcutil_lib import mock_lists

FLAGS = flags.FLAGS


class AddressCmdsTest(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)


  def testReserveAddressPromptsForRegion(self):
    expected_project = 'test_project'
    expected_address = 'test_address'
    expected_description = 'test address'
    expected_region = 'test-region'
    expected_source_address = '123.123.123.1'

    set_flags = {
        'project': expected_project,
        'description': expected_description,
        'source_address': expected_source_address,
    }
    command = self._CreateAndInitializeCommand(
        address_cmds.ReserveAddress, 'reserveaddress', set_flags=set_flags)

    mock_lists.GetSampleRegionListCall(
        command, self.mock, num_responses=1, name=[expected_region])

    call = self.mock.Respond('compute.addresses.insert', {})
    command.Handle(expected_address)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEquals(expected_region, request.parameters['region'])

    body = json.loads(request.body)
    self.assertEqual(body['name'], expected_address)
    self.assertEqual(body['description'], expected_description)
    self.assertEquals(body['address'], expected_source_address)

  def testReserveAddressGeneratesCorrectRequest(self):
    expected_project = 'test_project'
    expected_address = 'test_address'
    expected_description = 'test address'
    submitted_region = 'test-region'
    expected_source_address = '123.123.123.1'

    set_flags = {
        'project': expected_project,
        'description': expected_description,
        'region': submitted_region,
        'source_address': expected_source_address,
    }
    command = self._CreateAndInitializeCommand(
        address_cmds.ReserveAddress, 'reserveaddress', set_flags=set_flags)

    call = self.mock.Respond('compute.addresses.insert', {})
    command.Handle(expected_address)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEquals(submitted_region, request.parameters['region'])

    body = json.loads(request.body)
    self.assertEqual(body['name'], expected_address)
    self.assertEqual(body['description'], expected_description)
    self.assertEquals(body['address'], expected_source_address)

  def testGetAddressGeneratesCorrectRequest(self):
    expected_project = 'test_project'
    expected_address = 'test_address'
    submitted_region = 'test-region'

    set_flags = {
        'project': expected_project,
        'region': submitted_region,
        }
    command = self._CreateAndInitializeCommand(
        address_cmds.GetAddress, 'getaddress', set_flags=set_flags)

    call = self.mock.Respond('compute.addresses.get', {})
    command.Handle(expected_address)
    request = call.GetRequest()

    self.assertEqual('GET', request.method)
    self.assertEqual(None, request.body)

    parameters = request.parameters

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(parameters['region'], submitted_region)
    self.assertEqual(parameters['address'], expected_address)

  def testGetAddressPrintNonEmptyUsers(self):
    expected_project = 'test_project'
    submitted_region = 'test-region'

    set_flags = {
        'project': expected_project,
        'region': submitted_region,
        }
    command = self._CreateAndInitializeCommand(
        address_cmds.GetAddress, 'getaddress', set_flags=set_flags)

    data = command.GetDetailRow({'users': ['fr-1', 'fr-2']})

    expected_data = {
        'v1': [
            ('users', ['fr-1', 'fr-2'])
            ],
        }
    self.assertEquals(
        gcutil_unittest.SelectTemplateForVersion(
            expected_data, command.api.version),
        data)

  def testGetAddressPrintEmptyUsers(self):
    expected_project = 'test_project'
    submitted_region = 'test-region'

    set_flags = {
        'project': expected_project,
        'region': submitted_region,
        }
    command = self._CreateAndInitializeCommand(
        address_cmds.GetAddress, 'getaddress', set_flags=set_flags)

    data = command.GetDetailRow({'users': []})

    expected_data = {
        'v1': [
            ('users', [])
            ],
        }
    self.assertEquals(
        gcutil_unittest.SelectTemplateForVersion(
            expected_data, command.api.version),
        data)

  def testReleaseAddressGeneratesCorrectRequest(self):
    expected_project = 'test_project'
    expected_address = 'test_address'
    submitted_region = 'test-region'
    set_flags = {
        'project': expected_project,
        'region': submitted_region,
        }

    command = self._CreateAndInitializeCommand(
        address_cmds.ReleaseAddress, 'releaseaddress', set_flags=set_flags)

    call = self.mock.Respond('compute.addresses.delete', {})
    command.Handle(expected_address)
    request = call.GetRequest()

    self.assertEqual('DELETE', request.method)
    self.assertEqual(None, request.body)

    parameters = request.parameters

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(parameters['region'], submitted_region)
    self.assertEqual(parameters['address'], expected_address)

  def testReleaseAddressWithoutRegionFlag(self):
    expected_project = 'test_project'
    expected_region = 'test-region'
    expected_address = 'test_address'
    address = ('projects/%s/regions/%s/addresses/%s' %
               (expected_project, expected_region, expected_address))
    set_flags = {
        'project': 'incorrect_project',
        }

    command = self._CreateAndInitializeCommand(
        address_cmds.ReleaseAddress, 'releaseaddress', set_flags=set_flags)

    call = self.mock.Respond('compute.addresses.delete', {})
    command.Handle(address)
    request = call.GetRequest()

    self.assertEqual('DELETE', request.method)
    self.assertEqual(None, request.body)

    parameters = request.parameters

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(parameters['region'], expected_region)
    self.assertEqual(parameters['address'], expected_address)

  def testReleaseMultipleAddresses(self):
    expected_project = 'test_project'
    expected_addresses = [
        'test-addresses-%02d' % x for x in xrange(100)]

    set_flags = {
        'project': expected_project,
        'region': 'region-a',
        }

    command = self._CreateAndInitializeCommand(
        address_cmds.ReleaseAddress, 'releaseaddress', set_flags=set_flags)

    calls = [self.mock.Respond('compute.addresses.delete', {})
             for x in xrange(len(expected_addresses))]

    _, exceptions = command.Handle(*expected_addresses)
    self.assertEqual(0, len(exceptions))

    sorted_calls = sorted([call.GetRequest().parameters['address'] for
                           call in calls])

    self.assertEqual(expected_addresses, sorted_calls)

if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
