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

"""Unit tests for the target pool commands."""



import path_initializer
path_initializer.InitSysPath()

import copy
import json
import unittest

import gflags as flags
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api
from gcutil_lib import target_pool_cmds
from gcutil_lib import version

FLAGS = flags.FLAGS


class TargetPoolCmdsTests(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)


  def testLegacyRemoveTargetPoolInstanceGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'
    expected_instances = ['zone1/instance1', 'zone2/instance2']

    set_flags = {
        'project': expected_project,
        'region': expected_region,
        'instances': expected_instances,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.RemoveTargetPoolInstance, 'removetargetpoolinstance',
        set_flags=set_flags)

    calls = []
    calls.append(self.mock.Respond('compute.targetPools.removeInstance', {}))

    command.Handle(expected_target_pool)

    actual_instances = []
    request = calls[0].GetRequest()
    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_region, request.parameters['region'])
    body = json.loads(request.body)
    for instance in body['instances']:
      instance_url = instance['instance']
      actual_instances.append(instance_url)

    # Sort request instances, since there is no guaranteed order of execution.
    expected_instance_urls = []
    for expected_instance in expected_instances:
      zone, instance = expected_instance.split('/')
      expected_instance_urls.append(unicode(
          command.NormalizePerZoneResourceName(
              command._project, zone, 'instances', instance)))
    self.assertEqual(sorted(actual_instances), sorted(expected_instance_urls))

  def testLegacyAddTargetPoolInstanceGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'
    expected_instances = ['zone1/instance1', 'zone2/instance2']

    set_flags = {
        'project': expected_project,
        'region': expected_region,
        'instances': expected_instances,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.AddTargetPoolInstance, 'addtargetpoolinstance',
        set_flags=set_flags)

    calls = []
    calls.append(self.mock.Respond('compute.targetPools.addInstance', {}))

    command.Handle(expected_target_pool)

    actual_instances = []
    request = calls[0].GetRequest()
    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_region, request.parameters['region'])
    body = json.loads(request.body)
    for instance in body['instances']:
      instance_url = instance['instance']
      actual_instances.append(instance_url)

    # Sort request instances, since there is no guarranteed order of execution.
    expected_instance_urls = []
    for expected_instance in expected_instances:
      zone, instance = expected_instance.split('/')
      expected_instance_urls.append(unicode(
          command.NormalizePerZoneResourceName(
              command._project, zone, 'instances', instance)))
    self.assertEqual(sorted(actual_instances), sorted(expected_instance_urls))

  def testAddTargetPoolGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'
    expected_description = 'test fowarding pool'
    expected_health_checks = ['health-check1']
    # This is what the user actually sends.
    specified_instances = ['instance1', 'zone2/instances/instance2']
    # Ensure that the calls indicate that instance1 is in zone 1
    expected_instances = ['zone1/instances/instance1',
                          'zone2/instances/instance2']
    expected_session_affinity = 'CLIENT_IP'
    expected_failover_ratio = 0.45
    expected_backup_pool = 'backup-target-pool'

    set_flags = {
        'project': expected_project,
        'description': expected_description,
        'region': expected_region,
        'health_checks': expected_health_checks,
        'instances': specified_instances,
        'session_affinity': expected_session_affinity,
        'failover_ratio': expected_failover_ratio,
        'backup_pool': expected_backup_pool,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.AddTargetPool, 'addtargetpool', set_flags=set_flags)

    # A call will go out to determine what zones there are.
    aggregated_list_response = {
        'items': {
            'zones/zone1': {
                'instances': [{
                    'kind': 'compute#instance',
                    'name': 'instance1',
                    'description': '',
                    'selfLink': 'https://www.googleapis.com/compute/v1/'
                                'projects/test-project/zones/zone1/instances/'
                                'instance1'
                    }],
            },
            'zones/zone2': {
                'warning': {
                    'code': 'NO_RESULTS_ON_PAGE',
                    'data': [{
                        'key': 'scope',
                        'value': 'zones/zone1',
                    }],
                    'message': ('There are no results for scope '
                                '\'zones/zone1\' on this page.')
                }
            }
        },
    }

    self.mock.Respond('compute.instances.aggregatedList',
                      aggregated_list_response)

    call = self.mock.Respond('compute.targetPools.insert', {})
    command.Handle(expected_target_pool)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_region, request.parameters['region'])

    body = json.loads(request.body)
    self.assertEqual(body['name'], expected_target_pool)
    self.assertEqual(body['description'], expected_description)
    # URLs will have an http/path prefix attached.
    self.assertEqual(len(body['healthChecks']), len(expected_health_checks))
    for expected_hc, actual_hc in zip(expected_health_checks,
                                      body['healthChecks']):
      self.assertTrue(actual_hc.endswith('global/httpHealthChecks/' +
                                         expected_hc))

    self.assertEqual(len(body['instances']), len(expected_instances))
    for expected_instance, actual_instance in zip(expected_instances,
                                                  body['instances']):
      zone, _, inst = expected_instance.split('/')
      full_expected_instance = zone + '/instances/' + inst
      self.assertTrue(actual_instance.endswith(full_expected_instance))

  def testAddTargetPoolWithInvalidInstanceGeneratesValueError(self):
    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'
    expected_instance = 'this/will/fail'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
        'instances': expected_instance,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.AddTargetPoolInstance, 'addtargetpoolinstance',
        set_flags=set_flags)

    self.mock.Respond('compute.targetPools.addInstance', {})
    self.assertRaises(ValueError, command.Handle, expected_target_pool)

  def testAddTargetPoolWithFailoverRatioButNotBackupPool(self):
    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
        'failover_ratio': 0.45,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.AddTargetPool, 'addtargetpool', set_flags=set_flags)

    self.mock.Respond('compute.targetPools.insert', {})
    self.assertRaises(gcutil_errors.CommandError, command.Handle,
                      expected_target_pool)

  def testAddTargetPoolWithBackupPoolButNotFailoverRatio(self):
    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
        'backup_pool': 'backup-target-pool',
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.AddTargetPool, 'addtargetpool', set_flags=set_flags)

    self.mock.Respond('compute.targetPools.insert', {})
    self.assertRaises(gcutil_errors.CommandError, command.Handle,
                      expected_target_pool)

  def testAddTargetPoolInstanceGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'
    expected_instances = ['zone1/instances/instance1',
                          'zone2/instances/instance2']

    set_flags = {
        'project': expected_project,
        'region': expected_region,
        'instances': expected_instances,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.AddTargetPoolInstance, 'addtargetpoolinstance',
        set_flags=set_flags)

    calls = []
    calls.append(self.mock.Respond('compute.targetPools.addInstance', {}))

    command.Handle(expected_target_pool)

    actual_instances = []
    request = calls[0].GetRequest()
    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_region, request.parameters['region'])
    body = json.loads(request.body)
    for instance in body['instances']:
      instance_url = instance['instance']
      actual_instances.append(instance_url)

    # Sort request instances, since there is no guarranteed order of execution.
    expected_instance_urls = []
    for expected_instance in expected_instances:
      zone, _, instance = expected_instance.split('/')
      expected_instance_urls.append(unicode(
          command.NormalizePerZoneResourceName(
              command._project, zone, 'instances', instance)))
    self.assertEqual(sorted(actual_instances), sorted(expected_instance_urls))

  def testGetTargetPoolPrintsInstances(self):
    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.GetTargetPool, 'gettargetpool', set_flags=set_flags)

    url_prefix = ('https://www.googleapis.com/compute/v1/projects/' +
                  expected_project + '/zones/us-west1-a/instances')

    self.mock.Respond('compute.targetPools.get', {
        'instances': [url_prefix + '/www1',
                      url_prefix + '/www2',
                      url_prefix + '/www3'],
        })
    result = command.Handle(expected_target_pool)
    command.PrintResult(result)

  def testLegacyAddTargetPoolGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'
    expected_description = 'test fowarding pool'
    expected_health_checks = ['health-check1']
    # This is what the user actually sends.
    specified_instances = ['instance1', 'zone2/instance2']
    # Ensure that the calls indicate that instance1 is in zone 1
    expected_instances = ['zone1/instance1', 'zone2/instance2']
    expected_session_affinity = 'CLIENT_IP'
    expected_failover_ratio = 0.45
    expected_backup_pool = 'backup-target-pool'

    set_flags = {
        'project': expected_project,
        'description': expected_description,
        'region': expected_region,
        'health_checks': expected_health_checks,
        'instances': specified_instances,
        'session_affinity': expected_session_affinity,
        'failover_ratio': expected_failover_ratio,
        'backup_pool': expected_backup_pool,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.AddTargetPool, 'addtargetpool', set_flags=set_flags)

    aggregated_list_response = {
        'items': {
            'zones/zone1': {
                'instances': [{
                    'kind': 'compute#instance',
                    'name': 'instance1',
                    'description': '',
                    'selfLink': 'https://www.googleapis.com/compute/v1/'
                                'projects/test-project/zones/zone1/instances/'
                                'instance1'
                    }],
            },
            'zones/zone2': {
                'warning': {
                    'code': 'NO_RESULTS_ON_PAGE',
                    'data': [{
                        'key': 'scope',
                        'value': 'zones/zone1',
                    }],
                    'message': ('There are no results for scope '
                                '\'zones/zone1\' on this page.')
                }
            }
        },
    }

    self.mock.Respond('compute.instances.aggregatedList',
                      aggregated_list_response)

    call = self.mock.Respond('compute.targetPools.insert', {})
    command.Handle(expected_target_pool)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_region, request.parameters['region'])

    body = json.loads(request.body)
    self.assertEqual(body['name'], expected_target_pool)
    self.assertEqual(body['description'], expected_description)
    # URLs will have an http/path prefix attached.
    self.assertEqual(len(body['healthChecks']), len(expected_health_checks))
    for expected_hc, actual_hc in zip(expected_health_checks,
                                      body['healthChecks']):
      self.assertTrue(actual_hc.endswith('global/httpHealthChecks/' +
                                         expected_hc))

    self.assertEqual(len(body['instances']), len(expected_instances))
    for expected_instance, actual_instance in zip(expected_instances,
                                                  body['instances']):
      zone, inst = expected_instance.split('/')
      full_expected_instance = zone + '/instances/' + inst
      self.assertTrue(actual_instance.endswith(full_expected_instance))

  def testAddTargetPoolHealthCheckGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'
    expected_health_check = 'health-check1'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
        'health_check': expected_health_check,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.AddTargetPoolHealthCheck, 'addtargetpoolhealthcheck',
        set_flags=set_flags)

    call = self.mock.Respond('compute.targetPools.addHealthCheck', {})
    command.Handle(expected_target_pool)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_region, request.parameters['region'])

    body = json.loads(request.body)
    # URLs will have an http/path prefix attached.
    health_checks = body['healthChecks']
    self.assertEqual(len(health_checks), 1)
    self.assertTrue(health_checks[0]['healthCheck'].endswith(
        'global/httpHealthChecks/' + expected_health_check))

  def testGetTargetPoolGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.GetTargetPool, 'gettargetpool', set_flags=set_flags)

    call = self.mock.Respond('compute.targetPools.get', {})
    command.Handle(expected_target_pool)
    request = call.GetRequest()

    self.assertEqual('GET', request.method)
    self.assertEqual(None, request.body)

    parameters = request.parameters

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(parameters['region'], expected_region)
    self.assertEqual(parameters['targetPool'], expected_target_pool)

  def testGetTargetPoolHealthGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'
    expected_instance = 'zone1/instances/instance1'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
        'instances': [expected_instance],
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.GetTargetPoolHealth, 'gettargetpoolhealth',
        set_flags=set_flags)

    call = self.mock.Respond('compute.targetPools.getHealth', {})
    command.Handle(expected_target_pool)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_region, request.parameters['region'])

    body = json.loads(request.body)
    # URLs will have an http/path prefix attached.
    zone, _, inst = expected_instance.split('/')
    full_expected_instance = zone + '/instances/' + inst
    self.assertTrue(body['instance'].endswith(full_expected_instance))

  def testGetTargetPoolHealthFanout(self):
    flag_values = copy.deepcopy(FLAGS)

    command = target_pool_cmds.GetTargetPoolHealth(
        'gettargetpoolhealth', flag_values)

    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'
    expected_instances = ['thezone/instances/one',
                          'thezone/instances/two']

    set_flags = {
        'project': expected_project,
        'region': expected_region,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.GetTargetPoolHealth, 'gettargetpoolhealth',
        set_flags=set_flags)

    # Command will fetch the target pool first, then query for each instance.
    tp_call = self.mock.Respond('compute.targetPools.get',
                                {'instances': expected_instances})
    health_calls = []
    for inst in expected_instances:
      health_status_response = {
          'healthStatus': [{
              'instance': inst,
              'ipAddress': '1.2.3.4',
              'healthState': 'SO-SO'}]
          }
      health_calls.append(self.mock.Respond(
          'compute.targetPools.getHealth', health_status_response))

    results, exceptions = command.Handle(expected_target_pool)
    self.assertEqual(len(results), len(expected_instances))
    self.assertEqual([], exceptions)
    command.PrintResult({'items': results})

    # Check the targetPool.get request
    tp_request = tp_call.GetRequest()
    self.assertEqual('GET', tp_request.method)
    self.assertEqual(None, tp_request.body)
    tp_parameters = tp_request.parameters
    self.assertEqual(tp_parameters['project'], expected_project)
    self.assertEqual(tp_parameters['region'], expected_region)
    self.assertEqual(tp_parameters['targetPool'], expected_target_pool)

    # Health results and calls return in random (identical) order
    # that can differ from expected_instances order. We'll ensure
    # we hit all the expected ones, but not enforce the order.

    # Check each of the health requests.
    for hc, status_result in zip(health_calls, results):
      request = hc.GetRequest()
      self.assertEqual('POST', request.method)
      self.assertEqual(expected_project, request.parameters['project'])
      self.assertEqual(expected_region, request.parameters['region'])

      body = json.loads(request.body)
      inst = body['instance']
      self.assertEqual(status_result['healthStatus'][0]['instance'], inst)
      expected_instances.remove(inst)  # will throw if not present

    # None shall remain.
    self.assertEqual([], expected_instances)

  def testDeleteTargetPoolGeneratesCorrectRequest(self):
    expected_project = 'test_project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test_target_pool'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.DeleteTargetPool, 'deletetargetpool',
        set_flags=set_flags)

    call = self.mock.Respond('compute.targetPools.delete', {})
    command.Handle(expected_target_pool)
    request = call.GetRequest()

    self.assertEqual('DELETE', request.method)
    self.assertEqual(None, request.body)

    parameters = request.parameters

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(parameters['region'], expected_region)
    self.assertEqual(parameters['targetPool'], expected_target_pool)

  def testDeleteMultipleTargetPools(self):
    expected_project = 'test_project'
    expected_region = 'us-north1.a'
    expected_target_pools = [
        'test-target-pools-%02d' % x for x in xrange(5)]

    set_flags = {
        'project': expected_project,
        'region': expected_region,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.DeleteTargetPool, 'deletetargetpool',
        set_flags=set_flags)

    calls = [self.mock.Respond('compute.targetPools.delete', {})
             for x in xrange(len(expected_target_pools))]

    _, exceptions = command.Handle(*expected_target_pools)
    self.assertEqual(0, len(exceptions))

    sorted_calls = sorted([call.GetRequest().parameters['targetPool'] for
                           call in calls])
    self.assertEqual(expected_target_pools, sorted_calls)

  def testRemoveTargetPoolInstanceGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_region = 'us-north1.a'
    expected_target_pool = 'test-target-pool'
    expected_instances = ['zone1/instances/instance1',
                          'zone2/instances/instance2']

    set_flags = {
        'project': expected_project,
        'region': expected_region,
        'instances': expected_instances,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.RemoveTargetPoolInstance, 'removetargetpoolinstance',
        set_flags=set_flags)

    calls = []
    calls.append(self.mock.Respond('compute.targetPools.removeInstance', {}))

    command.Handle(expected_target_pool)

    actual_instances = []
    request = calls[0].GetRequest()
    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_region, request.parameters['region'])
    body = json.loads(request.body)
    for instance in body['instances']:
      instance_url = instance['instance']
      actual_instances.append(instance_url)

    # Sort request instances, since there is no guarranteed order of execution.
    expected_instance_urls = []
    for expected_instance in expected_instances:
      zone, _, instance = expected_instance.split('/')
      expected_instance_urls.append(unicode(
          command.NormalizePerZoneResourceName(
              command._project, zone, 'instances', instance)))
    self.assertEqual(sorted(actual_instances), sorted(expected_instance_urls))

  def testRemoveTargetPoolHealthCheckGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_target_pool = 'test-target-pool'
    expected_health_check = 'health-check1'
    expected_region = 'us-north1.a'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
        'health_check': expected_health_check,
    }
    command = self._CreateAndInitializeCommand(
        target_pool_cmds.RemoveTargetPoolHealthCheck,
        'removetargetpoolhealthcheck',
        set_flags=set_flags)

    call = self.mock.Respond('compute.targetPools.removeHealthCheck', {})
    command.Handle(expected_target_pool)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_region, request.parameters['region'])

    body = json.loads(request.body)
    # URLs will have an http/path prefix attached.
    health_checks = body['healthChecks']
    self.assertEqual(len(health_checks), 1)
    self.assertTrue(health_checks[0]['healthCheck'].endswith(
        'global/httpHealthChecks/' + expected_health_check))

  def testSetTargetPoolBackupGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_target_pool = 'test-target-pool'
    expected_region = 'us-east1'
    expected_backup_pool = 'backup-target-pool'
    expected_failover_ratio = '0.45'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
        'failover_ratio': expected_failover_ratio,
        'backup_pool': expected_backup_pool,
    }

    command = self._CreateAndInitializeCommand(
        target_pool_cmds.SetTargetPoolBackup, 'settargetpoolbackup',
        self.version, set_flags)

    call = self.mock.Respond('compute.targetPools.setBackup', {})
    command.Handle(expected_target_pool)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_region, request.parameters['region'])
    self.assertEqual(expected_failover_ratio,
                     request.parameters['failoverRatio'])

    body = json.loads(request.body)

    # URL will have an http/path prefix attached.
    self.assertTrue(body['target'].endswith(expected_backup_pool))


if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
