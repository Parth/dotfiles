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

"""Unit tests for the firewall commands."""



import path_initializer
path_initializer.InitSysPath()

import json
import unittest

import gflags as flags

from gcutil_lib import firewall_cmds
from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api

FLAGS = flags.FLAGS


class FirewallRulesTest(gcutil_unittest.GcutilTestCase):
  def testParsePortSpecs(self):
    parse_port_specs = firewall_cmds.FirewallRules.ParsePortSpecs
    self.assertRaises(ValueError, parse_port_specs, [''])
    self.assertRaises(ValueError, parse_port_specs, ['foo'])
    self.assertRaises(ValueError, parse_port_specs, ['foo:'])
    self.assertRaises(ValueError, parse_port_specs, ['tcp:foo-bar'])
    self.assertRaises(ValueError, parse_port_specs, ['tcp:http:https'])

    self.assertEqual(parse_port_specs([]), [])
    self.assertEqual(parse_port_specs(['tcp']),
                     [{'IPProtocol': '6'}])
    self.assertEqual(parse_port_specs(['6']),
                     [{'IPProtocol': '6'}])
    self.assertEqual(parse_port_specs(['tcp:80', 'tcp', 'tcp:ssh']),
                     [{'IPProtocol': '6'}])
    self.assertEqual(parse_port_specs(['tcp:ssh']),
                     [{'IPProtocol': '6',
                       'ports': ['22']}])
    self.assertEqual(parse_port_specs([':ssh']),
                     [{'IPProtocol': '17',
                       'ports': ['22']},
                      {'IPProtocol': '6',
                       'ports': ['22']}])
    self.assertEqual(parse_port_specs([':ssh']),
                     parse_port_specs(['udp:ssh', 'tcp:ssh']))
    self.assertEqual(parse_port_specs([':ssh', 'tcp:80']),
                     [{'IPProtocol': '17',
                       'ports': ['22']},
                      {'IPProtocol': '6',
                       'ports': ['22', '80']}])


class FirewallCmdsTest(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)

  def _doAddFirewallGeneratesCorrectRequest(self, allowed_ip_sources):
    expected_project = 'test_project'
    expected_firewall = 'test_firewall'
    submitted_network = 'test_network'
    expected_description = 'test firewall'

    set_flags = {
        'project': expected_project,
        'description': expected_description,
        'network': submitted_network,
        'allowed': [':22'],
    }

    if allowed_ip_sources:
      set_flags['allowed_ip_sources'] = allowed_ip_sources

    command = self._CreateAndInitializeCommand(
        firewall_cmds.AddFirewall, 'addfirewall', self.version, set_flags)

    expected_network = command.NormalizeGlobalResourceName(expected_project,
                                                           'networks',
                                                           submitted_network)

    firewalls_call = self.mock.Respond(
        'compute.firewalls.insert',
        {
            'kind': 'compute#operation',
            'status': 'RUNNING'
        })

    unused_result = command.Handle(expected_firewall)

    request = firewalls_call.GetRequest()

    parameters = request.parameters
    body = json.loads(request.body)

    self.assertEqual(parameters['project'], expected_project)

    self.assertEqual(body['name'], expected_firewall)
    self.assertEqual(body['network'], expected_network)
    self.assertEqual(body['description'], expected_description)

    self.assertEqual(body['sourceRanges'],
                     allowed_ip_sources or ['0.0.0.0/0'])
    allowed = body['allowed']

    self.assertEqual(len(allowed), 2)
    used_protocols = set([x['IPProtocol'] for x in allowed])
    self.assertEqual(used_protocols, set(['6', '17']))
    self.assertEqual(allowed[0]['ports'], allowed[1]['ports'])
    self.assertFalse('sourceTags' in body)
    self.assertFalse('targetTags' in body)

  def testAddFirewallGeneratesCorrectRequest(self):
    self._doAddFirewallGeneratesCorrectRequest(['10.10.10.10/0'])

  def testAddFirewallGeneratesCorrectRequestWithNoAllowedIpSource(self):
    self._doAddFirewallGeneratesCorrectRequest([])

  def testGetFirewallGeneratesCorrectRequest(self):
    expected_project = 'test_project'
    expected_firewall = 'test_firewall'

    set_flags = {
        'project': expected_project,
    }

    command = self._CreateAndInitializeCommand(
        firewall_cmds.GetFirewall, 'getfirewall', self.version, set_flags)

    firewalls_call = self.mock.Respond(
        'compute.firewalls.get',
        {
            'kind': 'compute#firewall',
            'firewall': expected_firewall
        })

    unused_result = command.Handle(expected_firewall)

    request = firewalls_call.GetRequest()

    parameters = request.parameters

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(parameters['firewall'], expected_firewall)

  def _doDeleteFirewallsGeneratesCorrectRequest(self, firewalls):
    expected_project = 'text_project'

    set_flags = {
        'project': expected_project,
    }

    command = self._CreateAndInitializeCommand(
        firewall_cmds.DeleteFirewall, 'deletefirewall', self.version, set_flags)

    def DeleteResponse(
        unused_uri, unused_http_method, unused_parameters, unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'status': 'DONE',
              'operationType': 'delete',
              'targetLink': 'http://example.com/link/to/the/operation'
          }, False)

    firewalls_call = self.mock.RespondF(
        'compute.firewalls.delete', DeleteResponse)

    results, exceptions = command.Handle(*firewalls)
    self.assertEqual(exceptions, [])
    results = results['items']
    self.assertEqual(len(results), len(firewalls))

    requests = firewalls_call.GetAllRequests()

    for request in requests:
      parameters = request.parameters
      self.assertEqual(parameters['project'], expected_project)
      firewalls.remove(parameters['firewall'])

  def testDeleteFirewallGeneratesCorrectRequest(self):
    self._doDeleteFirewallsGeneratesCorrectRequest(['test_firewall'])

  def testDeleteMultipleFirewalls(self):
    self._doDeleteFirewallsGeneratesCorrectRequest(
        ['test-firewalls-%02d' % x for x in xrange(100)])

  def testDeleteFirewallsWithFullyQualifiedPath(self):
    project_flag = 'wrong_project'

    set_flags = {
        'project': project_flag,
    }

    command = self._CreateAndInitializeCommand(
        firewall_cmds.DeleteFirewall, 'deletefirewall', self.version, set_flags)

    firewalls_call = self.mock.Respond(
        'compute.firewalls.delete',
        {
            'kind': 'compute#operation',
            'status': 'DONE',
            'operationType': 'delete',
            'targetLink': 'http://example.com/link/to/the/operation'
        })

    _, exceptions = command.Handle(
        'right_project/global/firewalls/my_firewall')
    self.assertEqual(exceptions, [])

    request = firewalls_call.GetRequest()

    parameters = request.parameters
    self.assertEqual('right_project', parameters['project'])
    self.assertEqual('my_firewall', parameters['firewall'])

  def testAddFirewallsWithTagsGeneratesCorrectRequest(self):
    expected_project = 'test_project'
    expected_firewall = 'test_firewall'
    submitted_network = 'test_network'
    expected_description = 'test firewall'
    expected_source_tags = ['a', 'b']
    expected_target_tags = ['c', 'd']

    set_flags = {
        'project': expected_project,
        'description': expected_description,
        'network': submitted_network,
        'allowed': [':22'],
        'allowed_tag_sources': expected_source_tags,
        'target_tags': expected_target_tags * 2
    }

    command = self._CreateAndInitializeCommand(
        firewall_cmds.AddFirewall, 'addfirewall', self.version, set_flags)

    expected_network = command.NormalizeGlobalResourceName(expected_project,
                                                           'networks',
                                                           submitted_network)

    firewalls_call = self.mock.Respond(
        'compute.firewalls.insert',
        {
            'kind': 'compute#operation',
            'status': 'RUNNING'
        })

    unused_result = command.Handle(expected_firewall)

    request = firewalls_call.GetRequest()

    parameters = request.parameters
    body = json.loads(request.body)

    self.assertEqual(parameters['project'], expected_project)

    self.assertEqual(body['name'], expected_firewall)
    self.assertEqual(body['network'], expected_network)
    self.assertEqual(body['description'], expected_description)

    allowed = body['allowed']

    self.assertEqual(len(allowed), 2)
    used_protocols = set([x['IPProtocol'] for x in allowed])
    self.assertEqual(used_protocols, set(['6', '17']))
    self.assertEqual(allowed[0]['ports'], allowed[1]['ports'])
    self.assertEqual(allowed[0]['ports'], ['22'])
    self.assertTrue('sourceTags' in body)
    self.assertTrue('targetTags' in body)
    self.assertEqual(body['sourceTags'], expected_source_tags)
    self.assertEqual(body['targetTags'], expected_target_tags)

if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
