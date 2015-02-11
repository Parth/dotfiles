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

"""Unit tests for the move commands."""



import path_initializer
path_initializer.InitSysPath()

import copy
import json
import uuid

from google.apputils import app
import gflags as flags
import unittest

from gcutil_lib import command_base
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api
from gcutil_lib import mock_lists
from gcutil_lib import move_cmds
from gcutil_lib import old_mock_api


FLAGS = flags.FLAGS


class MoveInstancesTest(gcutil_unittest.GcutilTestCase):
  _SUPPORTED_API_VERSIONS = ('v1',)

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)

  def testMoveInstanceWithReservedIpAcrossRegions(self):
    expected_project = 'my-project'
    expected_source_zone = 'twilight-a'
    expected_dest_zone = 'danger-a'
    expected_reserved_ip = '1.2.3.4'
    expected_address_name = 'my-address'
    expected_source_region = 'twilight'
    expected_dest_region = 'danger'
    expected_source_region_url = (
        'https://www.googleapis.com/compute/version/projects/{0}/regions/{1}'
        .format(expected_project, expected_source_region))
    expected_dest_region_url = (
        'https://www.googleapis.com/compute/version/projects/{0}/regions/{1}'
        .format(expected_project, expected_dest_region))
    expected_instance = 'lana'
    expected_machine_type = 'machine_type_1'

    set_flags = {
        'project': expected_project,
        'source_zone': expected_source_zone,
        'destination_zone': expected_dest_zone
    }

    command = self._CreateAndInitializeCommand(
        move_cmds.MoveInstances, 'moveinstances', self.version, set_flags)

    src_zone_response = {
        'kind': 'compute#zone',
        'name': expected_source_zone,
        'region': expected_source_region_url,
        'status': 'UP',
    }
    dest_zone_response = {
        'kind': 'compute#zone',
        'name': expected_dest_zone,
        'region': expected_dest_region_url,
        'status': 'UP',
    }

    def FakeCheckDeprecatedResources(instances_to_move):
      return instances_to_move

    command._CheckDeprecatedResources = FakeCheckDeprecatedResources

    def FakeWriteLog(*unused_args):
      pass

    def FakeDeleteLog(*unused_args):
      pass

    command._WriteLog = FakeWriteLog
    command._DeleteLog = FakeDeleteLog

    project_call = self.mock.Respond(
        'compute.projects.get',
        {
            'kind': 'compute#project',
            'name': expected_project,
            'quotas': [{
                'limit': 8.0,
                'metric': 'CPUS',
                'usage': 3.0
            }, {
                'limit': 8.0,
                'metric': 'INSTANCES',
                'usage': 3.0
            }, {
                'limit': 1000.0,
                'metric': 'SNAPSHOTS',
                'usage': 42.0
            }]
        })

    address_list_call = self.mock.Respond(
        'compute.addresses.aggregatedList',
        {
            'kind': 'compute#addressAggregatedList',
            'items': {
                'regions/{0}'.format(expected_source_region): {
                    'addresses': [{
                        'kind': 'compute#address',
                        'name': expected_address_name,
                        'region': expected_source_region_url,
                        'address': expected_reserved_ip
                    }]
                }
            }
        })

    # Next, a call to instances.list happens for both the source and
    # destination zones, in that order.
    source_instance_to_move_list_call = mock_lists.GetSampleInstanceListCall(
        command,
        self.mock,
        1,
        [expected_instance],
        networkInterfaces=[[{
            'accessConfigs': [{
                'kind': 'compute#accessConfig',
                'natIP': expected_reserved_ip,
                'type': 'ONE_TO_ONE_NAT'
            }]
        }]],
        machineType=[command.NormalizeGlobalResourceName(
            expected_project, 'machineTypes', expected_machine_type)],
        zone=[expected_source_zone])

    destination_instance_list_call = mock_lists.GetSampleInstanceListCall(
        command, self.mock, 2)

    # Next, another call to instances.list happens in the source zone
    # to do a sanity check regarding disk moves.
    source_instance_no_move_list_call = mock_lists.GetSampleInstanceListCall(
        command, self.mock, 1, ['do-not-move'])

    # The zone is checked for validity.
    zone_check_call = self.mock.Respond(
        'compute.zones.get', dest_zone_response)

    # Next we do a call to zones API in the destination zone in order to check
    # quotas.
    destination_zone_quota_call = self.mock.Respond(
        'compute.zones.get', dest_zone_response)

    # Two calls to zones.get happen to get their respective regions.
    source_zone_quota_call = self.mock.Respond(
        'compute.zones.get', src_zone_response)

    region_quota_call = self.mock.Respond(
        'compute.regions.get',
        {
            'name': expected_dest_region,
            'kind': 'compute#region',
            'quotas': [{
                'limit': 8.0,
                'metric': 'CPUS',
                'usage': 2.0
            }, {
                'limit': 8.0,
                'metric': 'INSTANCES',
                'usage': 2.0
            }, {
                'limit': 1000.0,
                'metric': 'SNAPSHOTS',
                'usage': 42.0
            }]
        })

    # There is also a call to machine_types to find out how many CPUs
    # are in use.
    machine_type_call = mock_lists.GetSampleMachineTypeListCall(command,
                                                                self.mock)

    # Also to disks
    disks_call = mock_lists.GetSampleDiskListCall(command, self.mock, 0)

    # Next there are two calls to the zones API to check whether it is
    # plausible to preserve the reserved addresses.  It will be.
    source_zone_region_call = self.mock.Respond(
        'compute.zones.get', src_zone_response)

    destination_zone_region_call = self.mock.Respond(
        'compute.zones.get', dest_zone_response)

    # Next a call to DeleteInstances wipes out the instance to move
    # on the source zone.
    delete_call = self.mock.Respond(
        'compute.instances.delete',
        {
            'kind': 'compute#operation',
            'name': expected_instance,
            'operationType': 'delete',
            'status': 'DONE',
            'targetLink': command.NormalizeGlobalResourceName(
                expected_project,
                'instances',
                expected_instance),
            'zone': command.NormalizeGlobalResourceName(
                expected_project,
                'zones',
                expected_source_zone)
        })

    disks_call = mock_lists.GetSampleDiskListCall(command, self.mock, 0)

    # There are no disks to move, so finally a call to CreateInstances
    # recreates the instances in the destination zone.
    create_call = self.mock.Respond(
        'compute.instances.insert',
        {
            'kind': 'compute#operation',
            'name': expected_instance,
            'operationType': 'insert',
            'status': 'DONE',
            'targetLink': command.NormalizeGlobalResourceName(
                expected_project,
                'projects',
                expected_instance),
            'zone': command.NormalizeGlobalResourceName(
                expected_project,
                'zones',
                expected_source_zone)
        })

    with gcutil_unittest.CaptureStandardIO('y\n\r') as unused_stdio:
      command.Handle(expected_instance)

      request = project_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])

      request = address_list_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])

      request = source_instance_to_move_list_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_source_zone, parameters['zone'])

      request = destination_instance_list_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_dest_zone, parameters['zone'])

      request = source_instance_no_move_list_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_source_zone, parameters['zone'])

      request = zone_check_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_dest_zone, parameters['zone'])

      request = destination_zone_quota_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_dest_zone, parameters['zone'])

      request = source_zone_quota_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_source_zone, parameters['zone'])

      request = destination_zone_quota_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_dest_zone, parameters['zone'])

      request = region_quota_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_dest_region, parameters['region'])

      request = machine_type_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])

      request = disks_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_source_zone, parameters['zone'])

      request = source_zone_region_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_source_zone, parameters['zone'])

      request = destination_zone_region_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_dest_zone, parameters['zone'])

      request = delete_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_source_zone, parameters['zone'])
      self.assertEqual(expected_instance, parameters['instance'])

      request = create_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_dest_zone, parameters['zone'])
      body = json.loads(request.body)
      self.assertEqual(expected_instance, body['name'])
      self.assertEqual(expected_machine_type,
                       command.DenormalizeResourceName(body['machineType']))
      self.assertFalse('natIP' in
                       body['networkInterfaces'][0]['accessConfigs'][0])

  def testMoveInstanceWithReservedIpWithinRegion(self):
    expected_project = 'my-project'
    expected_source_zone = 'danger-a'
    expected_destination_zone = 'danger-b'
    expected_reserved_ip = '1.2.3.4'
    expected_address_name = 'my-address'
    expected_region = 'danger'
    expected_region_url = ('https://www.googleapis.com/compute/version/'
                           'projects/{0}/regions/{1}'.format(expected_project,
                                                             expected_region))
    expected_instance = 'lana'
    expected_machine_type = 'machine_type_1'

    set_flags = {
        'project': expected_project,
        'source_zone': expected_source_zone,
        'destination_zone': expected_destination_zone
    }

    command = self._CreateAndInitializeCommand(
        move_cmds.MoveInstances, 'moveinstances', self.version, set_flags)

    src_zone_response = {
        'kind': 'compute#zone',
        'name': expected_source_zone,
        'region': expected_region_url,
        'status': 'UP',
    }
    dest_zone_response = {
        'kind': 'compute#zone',
        'name': expected_destination_zone,
        'region': expected_region_url,
        'status': 'UP',
    }

    def FakeCheckDeprecatedResources(instances_to_move):
      return instances_to_move

    command._CheckDeprecatedResources = FakeCheckDeprecatedResources

    def FakeWriteLog(*unused_args):
      pass

    def FakeDeleteLog(*unused_args):
      pass

    command._WriteLog = FakeWriteLog
    command._DeleteLog = FakeDeleteLog

    project_call = self.mock.Respond(
        'compute.projects.get',
        {
            'kind': 'compute#project',
            'name': expected_project,
            'quotas': [{
                'limit': 8.0,
                'metric': 'CPUS',
                'usage': 3.0
            }, {
                'limit': 8.0,
                'metric': 'INSTANCES',
                'usage': 3.0
            }, {
                'limit': 1000.0,
                'metric': 'SNAPSHOTS',
                'usage': 42.0
            }]
        })

    address_list_call = self.mock.Respond(
        'compute.addresses.aggregatedList',
        {
            'kind': 'compute#addressAggregatedList',
            'items': {
                'regions/{0}'.format(expected_region): {
                    'addresses': [{
                        'kind': 'compute#address',
                        'name': expected_address_name,
                        'region': expected_region_url,
                        'address': expected_reserved_ip
                    }]
                }
            }
        })

    # Next, a call to instances.list happens for both the source and
    # destination zones, in that order.
    source_instance_to_move_list_call = mock_lists.GetSampleInstanceListCall(
        command,
        self.mock,
        1,
        [expected_instance],
        networkInterfaces=[[{
            'accessConfigs': [{
                'kind': 'compute#accessConfig',
                'natIP': expected_reserved_ip,
                'type': 'ONE_TO_ONE_NAT'
            }]
        }]],
        machineType=[command.NormalizeGlobalResourceName(
            expected_project, 'machineTypes', expected_machine_type)],
        zone=[expected_source_zone])

    destination_instance_list_call = mock_lists.GetSampleInstanceListCall(
        command, self.mock, 2)

    # Next, another call to instances.list happens in the source zone
    # to do a sanity check regarding disk moves.
    source_instance_no_move_list_call = mock_lists.GetSampleInstanceListCall(
        command, self.mock, 1, ['do-not-move'])

    # The zone is checked for validity.
    zone_check_call = self.mock.Respond(
        'compute.zones.get', dest_zone_response)

    # Next we do a call to zones API in the destination zone in order to check
    # quotas.
    destination_zone_quota_call = self.mock.Respond(
        'compute.zones.get', dest_zone_response)

    # Two calls to zones.get happen to get their respective regions.
    source_zone_quota_call = self.mock.Respond(
        'compute.zones.get', src_zone_response)

    region_quota_call = self.mock.Respond(
        'compute.regions.get',
        {
            'name': expected_region,
            'kind': 'compute#region',
            'quotas': [{
                'limit': 8.0,
                'metric': 'CPUS',
                'usage': 2.0
            }, {
                'limit': 8.0,
                'metric': 'INSTANCES',
                'usage': 2.0
            }, {
                'limit': 1000.0,
                'metric': 'SNAPSHOTS',
                'usage': 42.0
            }]
        })

    # There is also a call to machine_types to find out how many CPUs
    # are in use.
    machine_type_call = mock_lists.GetSampleMachineTypeListCall(command,
                                                                self.mock)

    # Also to disks
    disks_call = mock_lists.GetSampleDiskListCall(command, self.mock, 0)

    # Next there are two calls to the zones API to check whether it is
    # plausible to preserve the reserved addresses.  It will be.
    source_zone_region_call = self.mock.Respond(
        'compute.zones.get', src_zone_response)

    destination_zone_region_call = self.mock.Respond(
        'compute.zones.get', dest_zone_response)

    disks_call = mock_lists.GetSampleDiskListCall(command, self.mock, 0)

    # Next a call to DeleteInstances wipes out the instance to move
    # on the source zone.
    delete_call = self.mock.Respond(
        'compute.instances.delete',
        {
            'kind': 'compute#operation',
            'name': expected_instance,
            'operationType': 'delete',
            'status': 'DONE',
            'targetLink': command.NormalizeGlobalResourceName(
                expected_project,
                'instances',
                expected_instance),
            'zone': command.NormalizeGlobalResourceName(
                expected_project,
                'zones',
                expected_source_zone)
        })

    # There are no disks to move, so finally a call to CreateInstances
    # recreates the instances in the destination zone.
    create_call = self.mock.Respond(
        'compute.instances.insert',
        {
            'kind': 'compute#operation',
            'name': expected_instance,
            'operationType': 'insert',
            'status': 'DONE',
            'targetLink': command.NormalizeGlobalResourceName(
                expected_project,
                'projects',
                expected_instance),
            'zone': command.NormalizeGlobalResourceName(
                expected_project,
                'zones',
                expected_source_zone)
        })

    with gcutil_unittest.CaptureStandardIO('y\n\r') as unused_stdio:
      command.Handle(expected_instance)

      request = project_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])

      request = address_list_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])

      request = source_instance_to_move_list_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_source_zone, parameters['zone'])

      request = destination_instance_list_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_destination_zone, parameters['zone'])

      request = source_instance_no_move_list_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_source_zone, parameters['zone'])

      request = zone_check_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_destination_zone, parameters['zone'])

      request = destination_zone_quota_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_destination_zone, parameters['zone'])

      request = source_zone_quota_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_source_zone, parameters['zone'])

      request = destination_zone_quota_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_destination_zone, parameters['zone'])

      request = region_quota_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_region, parameters['region'])

      request = machine_type_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])

      request = disks_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_source_zone, parameters['zone'])

      request = source_zone_region_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_source_zone, parameters['zone'])

      request = destination_zone_region_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_destination_zone, parameters['zone'])

      request = delete_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_source_zone, parameters['zone'])
      self.assertEqual(expected_instance, parameters['instance'])

      request = create_call.GetRequest()
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_destination_zone, parameters['zone'])
      body = json.loads(request.body)
      self.assertEqual(expected_instance, body['name'])
      self.assertEqual(expected_machine_type,
                       command.DenormalizeResourceName(body['machineType']))
      self.assertEqual(
          expected_reserved_ip,
          body['networkInterfaces'][0]['accessConfigs'][0]['natIP'])


class OldMoveInstancesBaseTestCase(unittest.TestCase):

  def setUp(self):
    self.flag_values = copy.deepcopy(FLAGS)
    self.flag_values.project = 'myproject'
    self.command = self._CreateCommand()
    self.api = old_mock_api.CreateMockApi('v1')
    self.command.SetFlags(self.flag_values)
    self.command.SetApi(self.api)

  def _CreateCommand(self):
    return move_cmds.MoveInstances('basemoveinstances', self.flag_values)


class OldMoveInstancesBaseTest(OldMoveInstancesBaseTestCase):

  cmd_name = 'moveinstancesbase'

  def testExtractAvailableQuota(self):
    project_quota = [
        {'metric': 'INSTANCES',
         'usage': 5.0,
         'limit': 10.0},
        {'metric': 'CPUS',
         'usage': 40.0,
         'limit': 0},  # Quota was changed after resource-creation.
        {'metric': 'EPHEMERAL_ADDRESSES',
         'usage': 5.0,
         'limit': 10.0},
        {'metric': 'DISKS',
         'usage': 7.0,
         'limit': 10.0},
        {'metric': 'DISKS_TOTAL_GB',
         'usage': 40.0,
         'limit': 100.0},
        {'metric': 'SNAPSHOTS',
         'usage': 3.0,
         'limit': 100.0},
        {'metric': 'NETWORKS',
         'usage': 2.0,
         'limit': 10.0},
        {'metric': 'FIREWALLS',
         'usage': 3.0,
         'limit': 10.0},
        {'metric': 'IMAGES',
         'usage': 9.0,
         'limit': 10.0}]

    zone_quota = [
        {'metric': 'INSTANCES',
         'usage': 3.0,
         'limit': 10.0},
        {'metric': 'CPUS',
         'usage': 3.0,
         'limit': 10.0},
        {'metric': 'DISKS',
         'usage': 2.0,
         'limit': 10.0},
        {'metric': 'DISKS_TOTAL_GB',
         'usage': 22.0,
         'limit': 25.0}]

    requirements = {
        'INSTANCES': 2.0,
        'CPUS': 2.0,
        'DISKS_TOTAL_GB': 32.0,
        'SNAPSHOTS': 3.0,
        'DISKS': 3.0}

    expected = {
        'INSTANCES': 7.0,
        'CPUS': -38.0,
        'DISKS_TOTAL_GB': 3.0,
        'SNAPSHOTS': 97.0,
        'DISKS': 6.0}

    self.assertEqual(self.command._ExtractAvailableQuota(
        project_quota, zone_quota, requirements), expected)


class OldMoveInstancesTest(OldMoveInstancesBaseTestCase):

  def _CreateCommand(self):
    return move_cmds.MoveInstances('moveinstances', self.flag_values)

  def testFlagValidationWithNoSourceZone(self):
    self.flag_values.destination_zone = 'dest-zone'
    self.assertRaises(app.UsageError, self.command.Handle, ['.*'])

  def testFlagValidationWithNoDestinationZone(self):
    self.flag_values.source_zone = 'src-zone'
    self.assertRaises(app.UsageError, self.command.Handle, ['.*'])

  def testFlagValidationWithNoSameSrcAndDest(self):
    self.flag_values.source_zone = 'my-zone'
    self.flag_values.destination_zone = 'my-zone'
    self.assertRaises(app.UsageError, self.command.Handle, ['.*'])

  def testGenerateSnapshotNames(self):
    test_cases = (
        [],
        ['disk-0'],
        ['disk-1', 'disk2', 'disk3'])

    for arg in test_cases:
      res = self.command._GenerateSnapshotNames(arg)
      self.assertEqual(len(res), len(arg))
      self.assertEqual(sorted(res.keys()), sorted(arg))
      for val in res.values():
        self.assertTrue(isinstance(val, basestring))
        self.assertTrue(val.startswith('snapshot-'))
        try:
          uuid.UUID(val[len('snapshot-'):])
        except ValueError:
          self.fail('Value generated does not include valid UUID.')

  def _GenerateInstanceResources(self, num, prefix='instance'):
    template = {
        'status': 'RUNNING',
        'kind': 'compute#instance',
        'machineType': 'https://googleapis.com/compute/.../n1-standard-1',
        'zone': 'https://googleapis.com/compute/.../zones/my-zone',
        'tags': [],
        'image': 'https://googleapis.com/compute/.../images/gcel',
        'disks': [
            {
                'index': 0,
                'kind': 'compute#instanceDisk',
                'type': 'EPHEMERAL',
                'mode': 'READ_WRITE'
                },
            {
                'index': 1,
                'kind': 'compute#attachedDisk',
                'mode': 'READ_ONLY',
                'type': 'PERSISTENT'
                }
            ],
        'networkInterfaces': [
            {
                'networkIP': '10.211.197.175',
                'kind': 'compute#instanceNetworkInterface',
                'accessConfigs': [
                    {
                        'type': 'ONE_TO_ONE_NAT',
                        'name': 'External NAT',
                        'natIP': '173.255.120.98'
                        }
                    ],
                'name': 'nic0',
                'network': 'https://googleapis.com/compute/.../networks/default'
                }
            ],
        'id': '12884714477555140369'}

    res = []
    for i in xrange(num):
      instance = copy.deepcopy(template)
      instance['name'] = '%s-%s' % (prefix, i)
      instance['selfLink'] = (
          'https://googleapis.com/compute/.../instances/%s' % instance['name'])
      instance['disks'][1]['deviceName'] = instance['name']
      instance['disks'][1]['source'] = (
          'https://www.googleapis.com/compute/.../disks/%s' % instance['name'])
      res.append(instance)
    return res

  def testCheckInstancePreconditionsWithNoMatchingInstances(self):
    self.assertRaises(gcutil_errors.CommandError,
                      self.command._CheckInstancePreconditions,
                      [], [])

  def testCheckInstancePreconditionsWithTooManyInstances(self):
    for num_instances_to_mv in (101, 120, 200):
      for num_instances_in_dest in (0, 10, 100, 101, 200):
        instances_to_mv = self._GenerateInstanceResources(
            num_instances_to_mv, prefix='i')
        instances_in_dest = self._GenerateInstanceResources(
            num_instances_in_dest, prefix='x')
        self.assertRaises(
            gcutil_errors.CommandError,
            self.command._CheckInstancePreconditions,
            instances_to_mv,
            instances_in_dest)

  def testCheckInstancePreconditionsWithNameCollisions(self):
    # Tests with lots of collisions.
    for num_instances in (1, 2, 10):
      instances = self._GenerateInstanceResources(num_instances)
      self.assertRaises(gcutil_errors.CommandError,
                        self.command._CheckInstancePreconditions,
                        instances, instances)

    # Tests with only a single collision.
    for num_instances in (1, 2, 10):
      instances_to_mv = self._GenerateInstanceResources(
          num_instances, prefix='i')
      instances_in_dest = self._GenerateInstanceResources(
          num_instances, prefix='x')
      instances_in_dest.extend(self._GenerateInstanceResources(1, prefix='i'))
      self.assertRaises(
          gcutil_errors.CommandError,
          self.command._CheckInstancePreconditions,
          instances_to_mv,
          instances_in_dest)

  def testCheckInstancePreconditionsUnderNormalConditions(self):
    for num_instances_to_mv in (1, 2, 10):
      for num_instances_in_dest in (0, 2, 10):
        instances_to_mv = self._GenerateInstanceResources(
            num_instances_to_mv, prefix='i')
        instances_in_dest = self._GenerateInstanceResources(
            num_instances_in_dest, prefix='x')
        self.command._CheckInstancePreconditions(
            instances_to_mv, instances_in_dest)

  def testCheckDiskPreconditionsWithTooManyDisks(self):
    for num_disks in (101, 120, 200):
      disk_names = ['disk-%s' % i for i in xrange(num_disks)]
      self.assertRaises(
          gcutil_errors.CommandError,
          self.command._CheckDiskPreconditions,
          [],
          disk_names)

  def testCheckDiskPreconditionsWithPoorDiskAttachment(self):
    for num_instances in (1, 2, 10):
      for num_disks in xrange(1, num_instances + 1):
        self.assertRaises(
            gcutil_errors.CommandError,
            self.command._CheckDiskPreconditions,
            self._GenerateInstanceResources(num_instances, prefix='i'),
            ['i-%s' % i for i in xrange(num_disks)])

  def testGetFlagValue(self):
    def Set(name, value):
      self.flag_values[name].present = 1
      self.flag_values[name].value = value

    # Before explicitly set by the user
    self.assertFalse(self.flag_values.keep_snapshots)
    self.assertTrue(self.command._GetFlagValue('keep_snapshots', True))

    # User set the value explicitly to False
    Set('keep_snapshots', False)
    self.assertFalse(self.command._GetFlagValue('keep_snapshots', True))

    # User didn't set max_wait_time
    self.assertEquals(0, self.flag_values['max_wait_time'].present)
    self.assertEquals(self.flag_values.max_wait_time,
                      self.flag_values['max_wait_time'].default)

    # Nor sleep_between_polls
    self.assertEquals(0, self.flag_values['sleep_between_polls'].present)
    self.assertEquals(self.flag_values.sleep_between_polls,
                      self.flag_values['sleep_between_polls'].default)

    # Get default sleep_between_polls.
    self.assertEquals(move_cmds.DEFAULT_SLEEP_BETWEEN_POLLS,
                      self.command._GetSleepBetweenPollsSeconds())

    # User sets the value explicitly.
    Set('sleep_between_polls', 17)
    self.assertEquals(17, self.command._GetSleepBetweenPollsSeconds())

    # Get default max_wait_time.
    self.assertEquals(move_cmds.DEFAULT_OPERATION_TIMEOUT,
                      self.command._GetTimeoutSeconds())

    # User sets the value explicitly.
    Set('max_wait_time', 10000)
    self.assertEquals(10000, self.command._GetTimeoutSeconds())

  def testForFailedOperation(self):
    # Successful operation, no error property.
    op = {
        'kind': 'compute#operation',
        'name': 'my-operation',
        }
    # Expect success.
    self.assertEquals(None, self.command._CheckForFailedOperation(op))

    # 'error' present but empty (for multiple definitions of 'empty').
    for error in (None, '', {}):
      op = {
          'kind': 'compute#operation',
          'name': 'my-operation',
          'error': error,
          }
      self.assertEquals(None, self.command._CheckForFailedOperation(op))

    # 'error.errors' present but empty (for multiple definitions of 'empty').
    for errors in (None, '', [], tuple()):
      op = {
          'kind': 'compute#operation',
          'name': 'my-operation',
          'error': {'errors': errors},
          }
      self.assertEquals(None, self.command._CheckForFailedOperation(op))

    # 'error.errors' present and non-empty but with bad contents.
    # This is interpreted as error.
    for error in (None, '', {}):
      op = {
          'kind': 'compute#operation',
          'name': 'my-operation',
          'error': {'errors': [error]},
          }
      self.assertEquals(
          ['Operation my-operation failed, server returned no error'],
          self.command._CheckForFailedOperation(op))

    # 'error.errors' present and non-empty but with bad contents.
    # This time, not even operation name is present.
    # This is interpreted as error.
    for error in (None, '', {}):
      op = {
          'kind': 'compute#operation',
          'error': {'errors': [error]},
          }
      self.assertEquals(
          ['Operation <unknown name> failed, server returned no error'],
          self.command._CheckForFailedOperation(op))

    # Failure with a message. This is the common case of well-behaving server.
    # Message takes precedence over error code.
    op = {
        'kind': 'compute#operation',
        'name': 'my-operation',
        'error': {'errors': [
            {
                'message': 'Something went wrong.',
                'code': 'SOMETHING_WENT_WRONG'
            }
        ]}
    }
    self.assertEquals(
        ['Something went wrong.'], self.command._CheckForFailedOperation(op))

    # Failure without a message but with error code.
    op = {
        'kind': 'compute#operation',
        'name': 'my-operation',
        'error': {'errors': [
            {
                'code': 'SOMETHING_WENT_WRONG'
            }
        ]}
    }
    self.assertEquals(
        ['Operation failed with code SOMETHING_WENT_WRONG.'],
        self.command._CheckForFailedOperation(op))

    # Multiple errors.
    op = {
        'kind': 'compute#operation',
        'name': 'my-operation',
        'error': {'errors': [
            {
                'code': 'SOMETHING_WENT_WRONG'
            },
            {
                'message': 'Something went wrong.'
            },
            {
                # Nothing here.
            }
        ]}
    }
    self.assertEquals(
        ['Operation failed with code SOMETHING_WENT_WRONG.',
         'Something went wrong.',
         'Operation my-operation failed, server returned no error'],
        self.command._CheckForFailedOperation(op))

  def testCheckForUnfinishedOperation(self):
    # No status at all. Considered unfinished.
    op = {
        'kind': 'compute#operation',
    }
    self.assertEquals(
        'Operation <unknown name> did not complete. Its status is unknown.',
        self.command._CheckForUnfinishedOperation(op))

    # Status other than 'DONE'. Considered unfinished.
    op = {
        'kind': 'compute#operation',
        'status': 'RUNNING'
    }
    self.assertEquals(
        'Operation <unknown name> did not complete. Its status is RUNNING.',
        self.command._CheckForUnfinishedOperation(op))

    # No status at all, but have operation name. Considered unfinished.
    op = {
        'kind': 'compute#operation',
        'name': 'my-operation'
    }
    self.assertEquals(
        'Operation my-operation did not complete. Its status is unknown.',
        self.command._CheckForUnfinishedOperation(op))

    # Status other than 'DONE'. Considered unfinished.
    op = {
        'kind': 'compute#operation',
        'status': 'PENDING',
        'name': 'my-operation'
    }
    self.assertEquals(
        'Operation my-operation did not complete. Its status is PENDING.',
        self.command._CheckForUnfinishedOperation(op))

  def testVerifyOperations(self):

    # Empty results -> Success.
    results = {'items': []}
    self.assertEquals(None, self.command._VerifyOperations(results))

    # No operation in the mix. Success.
    results = {'items': [
        {
            'kind': 'compute#instance'
        }
    ]}
    self.assertEquals(None, self.command._VerifyOperations(results))

    # Unfinished operation. Raise CommandError
    results = {'items': [
        {
            'kind': 'compute#operation',
        }
    ]}
    self.assertRaises(gcutil_errors.CommandError,
                      self.command._VerifyOperations, results)

    # Finished operation and a resource. Success.
    results = {'items': [
        {
            'kind': 'compute#operation',
            'status': 'DONE'
        },
        {
            'kind': 'compute#instance'
        }
    ]}
    self.assertEquals(None, self.command._VerifyOperations(results))


class OldResumeMoveTest(OldMoveInstancesBaseTestCase):

  def _CreateCommand(self):
    return move_cmds.ResumeMove('resumemove', self.flag_values)

  def testGetKeyWithGoodKeys(self):
    test_cases = (
        ({'key1': []}, 'key1', []),
        ({'key1': [1, 2, 3]}, 'key1', [1, 2, 3]),
        ({'key1': [1, 2, 3], 'key2': 5}, 'key2', 5))
    for log, key, expected in test_cases:
      self.assertEqual(self.command._GetKey(log, key), expected)

  def testGetKeyWithBadKeys(self):
    test_cases = (
        {},
        {'key1': []},
        {'key1': [1, 2, 3]},
        {'key1': [1, 2, 3], 'key2': 5})
    for log in test_cases:
      self.assertRaises(gcutil_errors.CommandError,
                        self.command._GetKey, log, 'nonexistent')

if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
