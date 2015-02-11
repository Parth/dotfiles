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

"""Unit tests for the HTTP health check commands."""



import path_initializer
path_initializer.InitSysPath()

import unittest

import gflags as flags
from gcutil_lib import forwarding_rule_cmds
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api

FLAGS = flags.FLAGS


class ForwardingRuleCmdsTests(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)


  def testAddForwardingRulePromptsForRegion(self):
    expected_project = 'test-project'
    expected_forwarding_rule = 'test-fowarding-rule'
    expected_description = 'test fowarding rule'
    expected_ip = '1.2.3.4'
    expected_protocol = 'UDP'
    expected_port_range = '7000-8000'
    expected_target = 'test-target-name'
    expected_region = 'region-of-terror'

    set_flags = {
        'project': expected_project,
        'description': expected_description,
        'ip': expected_ip,
        'protocol': expected_protocol,
        'port_range': expected_port_range,
        'target_pool': expected_target
    }

    command = self._CreateAndInitializeCommand(
        forwarding_rule_cmds.AddForwardingRule, 'addforwardingrule',
        self.version, set_flags)

    # First, we must find the (only) valid region for the new rule.
    self.mock.Respond(
        'compute.regions.list',
        {
            'kind': 'compute#regionList',
            'items': [{
                'name': expected_region,
                }],
        })

    # Next, we auto-detect the region for test target.
    self.mock.Respond(
        'compute.regions.list',
        {
            'kind': 'compute#regionList',
            'items': [{
                'name': expected_region,
                }],
        })

    self_link_format = (
        'https://www.googleapis.com/compute/%s/projects/%s/'
        'regions/%s/targetPools/%s')

    self.mock.Respond(
        'compute.targetPools.aggregatedList',
        {
            'items': {
                ('regions/%s' % expected_region): {
                    'forwardingRules': [{
                        'name': expected_target,
                        'region': expected_region,
                        'selfLink': self_link_format % (self.version,
                                                        expected_project,
                                                        expected_region,
                                                        expected_target)
                    }]
                }
            }
        })

    # The insert goes off without a hitch.
    call = self.mock.Respond('compute.forwardingRules.insert', {})
    command.Handle(expected_forwarding_rule)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_region, request.parameters['region'])

    body = eval(request.body)
    self.assertEqual(body['name'], expected_forwarding_rule)
    self.assertEqual(body['description'], expected_description)
    self.assertEqual(body['IPAddress'], expected_ip)
    self.assertEqual(body['IPProtocol'], expected_protocol)
    self.assertEqual(body['portRange'], expected_port_range)

    # URL will have an http/path prefix attached.
    self.assertTrue(body['target'].endswith(expected_target))

  def testAddForwardingRuleWithFullyQualifiedPathGeneratesCorrectRequest(self):
    # This call to the backend would actually fail.  However, it should be
    # passed along by gcutil just the same, as gcutil is not an arbiter of
    # correctness.
    expected_project = 'test-project'
    fully_qualified_forwarding_rule = (
        'regions/us-east1/forwardingRules/test-forwarding-rule')
    expected_description = 'test fowarding rule'
    flag_region = 'us-west1'
    expected_ip = '1.2.3.4'
    expected_protocol = 'UDP'
    expected_port_range = '7000-8000'
    expected_target = 'test-target-name'

    set_flags = {
        'project': expected_project,
        'description': expected_description,
        'region': flag_region,
        'ip': expected_ip,
        'protocol': expected_protocol,
        'port_range': expected_port_range,
        'target': expected_target
    }

    command = self._CreateAndInitializeCommand(
        forwarding_rule_cmds.AddForwardingRule, 'addforwardingrule',
        self.version, set_flags)

    call = self.mock.Respond('compute.forwardingRules.insert', {})
    command.Handle(fully_qualified_forwarding_rule)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual('us-east1', request.parameters['region'])

    body = eval(request.body)
    self.assertEqual('test-forwarding-rule', body['name'])
    self.assertEqual(body['description'], expected_description)
    self.assertEqual(body['IPAddress'], expected_ip)
    self.assertEqual(body['IPProtocol'], expected_protocol)
    self.assertEqual(body['portRange'], expected_port_range)

    # URL will have an http/path prefix attached.
    self.assertTrue(body['target'].endswith(expected_target))
    # It is actually going to be in flag_region.  This makes this request
    # invalid on the backend.
    self.assertTrue(flag_region in body['target'])
    self.assertTrue(expected_project in body['target'])

  def testAddForwardingRuleGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_forwarding_rule = 'test-fowarding-rule'
    expected_description = 'test fowarding rule'
    expected_region = 'us-east1'
    expected_ip = '1.2.3.4'
    expected_protocol = 'UDP'
    expected_port_range = '7000-8000'
    expected_target = 'test-target-name'

    set_flags = {
        'project': expected_project,
        'description': expected_description,
        'region': expected_region,
        'ip': expected_ip,
        'protocol': expected_protocol,
        'port_range': expected_port_range,
        'target_pool': expected_target
    }

    command = self._CreateAndInitializeCommand(
        forwarding_rule_cmds.AddForwardingRule, 'addforwardingrule',
        self.version, set_flags)

    call = self.mock.Respond('compute.forwardingRules.insert', {})
    command.Handle(expected_forwarding_rule)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_region, request.parameters['region'])

    body = eval(request.body)
    self.assertEqual(body['name'], expected_forwarding_rule)
    self.assertEqual(body['description'], expected_description)
    self.assertEqual(body['IPAddress'], expected_ip)
    self.assertEqual(body['IPProtocol'], expected_protocol)
    self.assertEqual(body['portRange'], expected_port_range)

    # URL will have an http/path prefix attached.
    self.assertTrue(body['target'].endswith(expected_target))

  def testAddForwardingRuleWithTargetInstanceGeneratesCorrectRequest(self):
    if self.api.version >= 'v1':
      expected_project = 'test-project'
      expected_forwarding_rule = 'test-fowarding-rule'
      expected_description = 'test fowarding rule'
      expected_region = 'us-east1'
      expected_ip = '1.2.3.4'
      expected_protocol = 'UDP'
      expected_port_range = '7000-8000'
      specified_target_instance = 'test-target-name'
      expected_target_instance_suffix = (
          'zones/test-zone/targetInstances/test-target-name')

      set_flags = {
          'project': expected_project,
          'description': expected_description,
          'region': expected_region,
          'ip': expected_ip,
          'protocol': expected_protocol,
          'port_range': expected_port_range,
          'target_instance': specified_target_instance,
      }

      command = self._CreateAndInitializeCommand(
          forwarding_rule_cmds.AddForwardingRule, 'addforwardingrule',
          self.version, set_flags)

      # A call will go out to determine what zones there are.
      aggregated_list_response = {
          'items': {
              'zones/test-zone': {
                  'targetInstances': [{
                      'kind': 'compute#targetInstance',
                      'name': 'test-target-name',
                      'description': '',
                      'selfLink': 'https://www.googleapis.com/compute/v1/'
                                  'projects/test-project/zones/test-zone/'
                                  'targetInstances/test-target-name'
                      }],
              },
              'zones/empty-zone': {
                  'warning': {
                      'code': 'NO_RESULTS_ON_PAGE',
                      'data': [{
                          'key': 'scope',
                          'value': 'zones/zone1',
                      }],
                      'message': ('There are no results for scope '
                                  '\'zones/empty-zone\' on this page.')
                  }
              }
          },
      }

      self.mock.Respond('compute.targetInstances.aggregatedList',
                        aggregated_list_response)

      call = self.mock.Respond('compute.forwardingRules.insert', {})
      command.Handle(expected_forwarding_rule)
      request = call.GetRequest()

      self.assertEqual('POST', request.method)
      self.assertEqual(expected_project, request.parameters['project'])
      self.assertEqual(expected_region, request.parameters['region'])

      body = eval(request.body)
      self.assertEqual(body['name'], expected_forwarding_rule)
      self.assertEqual(body['description'], expected_description)
      self.assertEqual(body['IPAddress'], expected_ip)
      self.assertEqual(body['IPProtocol'], expected_protocol)
      self.assertEqual(body['portRange'], expected_port_range)

      # URL will have an http/path prefix attached.
      self.assertTrue(body['target'].endswith(expected_target_instance_suffix))

  def testAddForwardingRuleWithNoTargetRaisesError(self):
    if self.api.version >= 'v1':
      expected_project = 'test-project'
      expected_forwarding_rule = 'test-fowarding-rule'
      expected_description = 'test fowarding rule'
      expected_region = 'us-east1'
      expected_ip = '1.2.3.4'
      expected_protocol = 'UDP'
      expected_port_range = '7000-8000'

      set_flags = {
          'project': expected_project,
          'description': expected_description,
          'region': expected_region,
          'ip': expected_ip,
          'protocol': expected_protocol,
          'port_range': expected_port_range,
      }

      command = self._CreateAndInitializeCommand(
          forwarding_rule_cmds.AddForwardingRule, 'addforwardingrule',
          self.version, set_flags)

      self.assertRaises(gcutil_errors.CommandError, command.Handle,
                        expected_forwarding_rule)

  def testSetForwardingRuleTargetPoolGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_forwarding_rule = 'test-fowarding-rule'
    expected_region = 'us-east1'
    expected_target = 'test-target-name'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
        'target_pool': expected_target,
    }

    command = self._CreateAndInitializeCommand(
        forwarding_rule_cmds.SetForwardingRuleTarget, 'addforwardingrule',
        self.version, set_flags)

    call = self.mock.Respond('compute.forwardingRules.setTarget', {})
    command.Handle(expected_forwarding_rule)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_region, request.parameters['region'])

    body = eval(request.body)

    # URL will have an http/path prefix attached.
    self.assertTrue(body['target'].endswith(expected_target))

  def testSetForwardingRuleTargetInstanceGeneratesCorrectRequest(self):
    if self.api.version >= 'v1':
      expected_project = 'test-project'
      expected_forwarding_rule = 'test-fowarding-rule'
      expected_region = 'us-east1'
      specified_target_instance = 'test-target-name'
      expected_target_instance_suffix = (
          'zones/test-zone/targetInstances/test-target-name')

      set_flags = {
          'project': expected_project,
          'region': expected_region,
          'target_instance': specified_target_instance,
      }

      command = self._CreateAndInitializeCommand(
          forwarding_rule_cmds.SetForwardingRuleTarget, 'addforwardingrule',
          self.version, set_flags)

      # A call will go out to determine what zones there are.
      aggregated_list_response = {
          'items': {
              'zones/test-zone': {
                  'targetInstances': [{
                      'kind': 'compute#targetInstance',
                      'name': 'test-target-name',
                      'description': '',
                      'selfLink': 'https://www.googleapis.com/compute/v1/'
                                  'projects/test-project/zones/test-zone/'
                                  'targetInstances/test-target-name'
                      }],
              },
              'zones/empty-zone': {
                  'warning': {
                      'code': 'NO_RESULTS_ON_PAGE',
                      'data': [{
                          'key': 'scope',
                          'value': 'zones/empty-zone',
                      }],
                      'message': ('There are no results for scope '
                                  '\'zones/empty-zone\' on this page.')
                  }
              }
          },
      }

      self.mock.Respond('compute.targetInstances.aggregatedList',
                        aggregated_list_response)

      call = self.mock.Respond('compute.forwardingRules.setTarget', {})
      command.Handle(expected_forwarding_rule)
      request = call.GetRequest()

      self.assertEqual('POST', request.method)
      self.assertEqual(expected_project, request.parameters['project'])
      self.assertEqual(expected_region, request.parameters['region'])

      body = eval(request.body)

      # URL will have an http/path prefix attached.
      self.assertTrue(body['target'].endswith(expected_target_instance_suffix))

  def testSetForwardingRuleTargetWithoutTargetRaisesError(self):
    if self.api.version >= 'v1':
      expected_project = 'test-project'
      expected_forwarding_rule = 'test-fowarding-rule'
      expected_region = 'us-east1'

      set_flags = {
          'project': expected_project,
          'region': expected_region,
      }

      command = self._CreateAndInitializeCommand(
          forwarding_rule_cmds.SetForwardingRuleTarget, 'addforwardingrule',
          self.version, set_flags)

      self.assertRaises(gcutil_errors.CommandError, command.Handle,
                        expected_forwarding_rule)

  def testGetForwardingRuleGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_forwarding_rule = 'test-forwarding-rule'
    expected_region = 'us-north1.a'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
    }

    command = self._CreateAndInitializeCommand(
        forwarding_rule_cmds.GetForwardingRule, 'getforwardingrule',
        self.version, set_flags)

    call = self.mock.Respond('compute.forwardingRules.get', {})
    command.Handle(expected_forwarding_rule)
    request = call.GetRequest()

    self.assertEqual('GET', request.method)
    self.assertEqual(None, request.body)

    parameters = request.parameters

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(parameters['region'], expected_region)
    self.assertEqual(parameters['forwardingRule'], expected_forwarding_rule)

  def testDeleteForwardingRuleDoesNotPrompt(self):
    expected_project = 'my_project'
    expected_forwarding_rule = 'test_forwarding_rule'
    expected_region = 'us-north1.a'

    set_flags = {
        'project': expected_project
    }

    command = self._CreateAndInitializeCommand(
        forwarding_rule_cmds.DeleteForwardingRule, 'deleteforwardingrule',
        self.version, set_flags)

    self_link_format = (
        'https://www.googleapis.com/compute/%s/projects/%s/'
        'regions/%s/forwardingRules/%s')

    self.mock.Respond(
        'compute.forwardingRules.aggregatedList',
        {
            'items': {
                ('regions/%s' % expected_region): {
                    'forwardingRules': [{
                        'name': expected_forwarding_rule,
                        'region': expected_region,
                        'selfLink': self_link_format % (
                            self.version, expected_project,
                            expected_region, expected_forwarding_rule)
                    }]
                }
            }
        })

    call = self.mock.Respond('compute.forwardingRules.delete', {})
    command.Handle(expected_forwarding_rule)
    request = call.GetRequest()

    self.assertEqual('DELETE', request.method)
    self.assertEqual(None, request.body)

    parameters = request.parameters

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(parameters['region'], expected_region)
    self.assertEqual(parameters['forwardingRule'], expected_forwarding_rule)

  def testDeleteForwardingRuleGeneratesCorrectRequest(self):
    expected_project = 'test_project'
    expected_forwarding_rule = 'test_forwarding_rule'
    expected_region = 'us-north1.a'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
    }

    command = self._CreateAndInitializeCommand(
        forwarding_rule_cmds.DeleteForwardingRule, 'deleteforwardingrule',
        self.version, set_flags)

    call = self.mock.Respond('compute.forwardingRules.delete', {})
    command.Handle(expected_forwarding_rule)
    request = call.GetRequest()

    self.assertEqual('DELETE', request.method)
    self.assertEqual(None, request.body)

    parameters = request.parameters

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(parameters['region'], expected_region)
    self.assertEqual(parameters['forwardingRule'], expected_forwarding_rule)

  def testDeleteMultipleForwardingRules(self):
    expected_project = 'test_project'
    expected_region = 'us-north1'

    set_flags = {
        'project': expected_project,
        'region': expected_region,
    }

    command = self._CreateAndInitializeCommand(
        forwarding_rule_cmds.DeleteForwardingRule, 'deleteforwardingrule',
        self.version, set_flags)

    expected_forwarding_rules = [
        'test-forwarding-rules-%02d' % x for x in xrange(5)]

    calls = [self.mock.Respond('compute.forwardingRules.delete', {})
             for x in xrange(len(expected_forwarding_rules))]

    _, exceptions = command.Handle(*expected_forwarding_rules)
    self.assertEqual(0, len(exceptions))

    sorted_calls = sorted([call.GetRequest().parameters['forwardingRule'] for
                           call in calls])
    self.assertEqual(expected_forwarding_rules, sorted_calls)


if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
