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

"""Unit tests for the target instance commands."""



import path_initializer
path_initializer.InitSysPath()

import json
import unittest

import gflags as flags
from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api
from gcutil_lib import target_instance_cmds

FLAGS = flags.FLAGS


class TargetInstanceCmdsTests(gcutil_unittest.GcutilTestCase):
  _SUPPORTED_API_VERSIONS = ('v1',)

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)


  def testAddTargetInstanceGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_zone = 'us-north1-a'
    expected_target_instance = 'test-target-instance'
    expected_description = 'test target instance'
    # This is what the user actually sends.
    specified_instance = 'instance1'

    set_flags = {
        'project': expected_project,
        'description': expected_description,
        'zone': expected_zone,
        'instance': specified_instance,
    }
    command = self._CreateAndInitializeCommand(
        target_instance_cmds.AddTargetInstance,
        'addtargetinstance',
        self.version,
        set_flags=set_flags)

    self.mock.Respond(
        'compute.zones.list',
        {
            'kind': 'compute#zoneList',
            'items': [{
                'name': expected_zone,
                }],
        })

    self_link_format = (
        'https://www.googleapis.com/compute/%s/projects/%s/'
        'zones/%s/targetInstances/%s')

    self.mock.Respond(
        'compute.targetInstances.list',
        {
            'kind': 'compute#targetInstanceList',
            'items': [{
                'name': expected_target_instance,
                'zone': expected_zone,
                'selfLink': self_link_format % (self.version,
                                                expected_project,
                                                expected_zone,
                                                expected_target_instance)
            }]
        })

    call = self.mock.Respond('compute.targetInstances.insert', {})
    command.Handle(expected_target_instance)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_zone, request.parameters['zone'])

    body = json.loads(request.body)
    self.assertEqual(body['name'], expected_target_instance)
    self.assertEqual(body['description'], expected_description)

    self.assertTrue(body['instance'].endswith(
        expected_zone + '/instances/' + specified_instance))

  def testGetTargetInstanceGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_zone = 'us-north1-a'
    expected_target_instance = 'test-target-instance'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
    }
    command = self._CreateAndInitializeCommand(
        target_instance_cmds.GetTargetInstance,
        'gettargetinstance',
        self.version,
        set_flags=set_flags)

    call = self.mock.Respond('compute.targetInstances.get', {})
    command.Handle(expected_target_instance)
    request = call.GetRequest()

    self.assertEqual('GET', request.method)
    self.assertEqual(None, request.body)

    parameters = request.parameters

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(parameters['zone'], expected_zone)
    self.assertEqual(parameters['targetInstance'], expected_target_instance)

  def testDeleteTargetInstanceGeneratesCorrectRequest(self):
    expected_project = 'test_project'
    expected_zone = 'us-north1-a'
    expected_target_instance = 'test_target_instance'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
    }
    command = self._CreateAndInitializeCommand(
        target_instance_cmds.DeleteTargetInstance,
        'deletetargetinstance',
        self.version,
        set_flags=set_flags)

    call = self.mock.Respond('compute.targetInstances.delete', {})
    command.Handle(expected_target_instance)
    request = call.GetRequest()

    self.assertEqual('DELETE', request.method)
    self.assertEqual(None, request.body)

    parameters = request.parameters

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(parameters['zone'], expected_zone)
    self.assertEqual(parameters['targetInstance'], expected_target_instance)

  def testDeleteMultipleTargetInstances(self):
    expected_project = 'test_project'
    expected_zone = 'us-north1-a'
    expected_target_instances = [
        'test-target-instances-%02d' % x for x in xrange(5)]

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
    }
    command = self._CreateAndInitializeCommand(
        target_instance_cmds.DeleteTargetInstance,
        'deletetargetinstance',
        self.version,
        set_flags=set_flags)

    calls = [self.mock.Respond('compute.targetInstances.delete', {})
             for x in xrange(len(expected_target_instances))]

    _, exceptions = command.Handle(*expected_target_instances)
    self.assertEqual(0, len(exceptions))

    sorted_calls = sorted([call.GetRequest().parameters['targetInstance'] for
                           call in calls])
    self.assertEqual(expected_target_instances, sorted_calls)


if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())

