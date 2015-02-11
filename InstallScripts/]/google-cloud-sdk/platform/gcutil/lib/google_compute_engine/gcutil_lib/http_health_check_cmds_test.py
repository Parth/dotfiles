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

from gcutil_lib import gcutil_unittest
from gcutil_lib import http_health_check_cmds
from gcutil_lib import mock_api

FLAGS = flags.FLAGS


class HttpHealthCheckCmdsTest(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)


  def testAddHttpHealthCheckGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_http_health_check = 'test-http-health-check'
    expected_description = 'test http health check'
    expected_host = 'www.mydomain.com'
    expected_request_path = '/healthz?'
    expected_port = 8080
    expected_check_interval_sec = 7
    expected_check_timeout_sec = 6
    expected_unhealthy_threshold = 5
    expected_healthy_threshold = 3

    set_flags = {
        'project': expected_project,
        'description': expected_description,
        'host': expected_host,
        'request_path': expected_request_path,
        'port': expected_port,
        'check_interval_sec': expected_check_interval_sec,
        'check_timeout_sec': expected_check_timeout_sec,
        'unhealthy_threshold': expected_unhealthy_threshold,
        'healthy_threshold': expected_healthy_threshold,
    }

    command = self._CreateAndInitializeCommand(
        http_health_check_cmds.AddHttpHealthCheck, 'addhttphealthcheck',
        self.version, set_flags)

    call = self.mock.Respond('compute.httpHealthChecks.insert', {})
    command.Handle(expected_http_health_check)
    request = call.GetRequest()

    self.assertEqual('POST', request.method)
    self.assertEqual(expected_project, request.parameters['project'])

    body = eval(request.body)
    self.assertEqual(body['name'], expected_http_health_check)
    self.assertEqual(body['description'], expected_description)
    self.assertEqual(body['host'], expected_host)
    self.assertEqual(body['requestPath'], expected_request_path)
    self.assertEqual(body['port'], expected_port)
    self.assertEqual(body['checkIntervalSec'],
                     expected_check_interval_sec)
    self.assertEqual(body['timeoutSec'],
                     expected_check_timeout_sec)
    self.assertEqual(
        body['unhealthyThreshold'], expected_unhealthy_threshold)
    self.assertEqual(
        body['healthyThreshold'], expected_healthy_threshold)

  def testUpdateHttpHealthCheckGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_http_health_check = 'test-http-health-check'
    expected_description = 'test http health check'
    expected_host = 'www.mydomain.com'
    expected_request_path = '/healthz?'
    expected_port = 8080
    expected_check_interval_sec = 7
    expected_check_timeout_sec = 6
    expected_unhealthy_threshold = 5
    expected_healthy_threshold = 3

    set_flags = {
        'project': expected_project,
        'description': expected_description,
        'host': expected_host,
        'request_path': expected_request_path,
        'port': expected_port,
        'check_interval_sec': expected_check_interval_sec,
        'check_timeout_sec': expected_check_timeout_sec,
        'unhealthy_threshold': expected_unhealthy_threshold,
        'healthy_threshold': expected_healthy_threshold,
    }

    command = self._CreateAndInitializeCommand(
        http_health_check_cmds.UpdateHttpHealthCheck, 'updatehttphealthcheck',
        self.version, set_flags)

    call = self.mock.Respond('compute.httpHealthChecks.patch', {})
    command.Handle(expected_http_health_check)
    request = call.GetRequest()

    self.assertEqual('PATCH', request.method)
    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_http_health_check,
                     request.parameters['httpHealthCheck'])

    body = eval(request.body)
    self.assertEqual(body['description'], expected_description)
    self.assertEqual(body['host'], expected_host)
    self.assertEqual(body['requestPath'], expected_request_path)
    self.assertEqual(body['port'], expected_port)
    self.assertEqual(body['checkIntervalSec'],
                     expected_check_interval_sec)
    self.assertEqual(body['timeoutSec'],
                     expected_check_timeout_sec)
    self.assertEqual(
        body['unhealthyThreshold'], expected_unhealthy_threshold)
    self.assertEqual(
        body['healthyThreshold'], expected_healthy_threshold)

  def testGetHttpHealthCheckGeneratesCorrectRequest(self):
    expected_project = 'test_project'
    expected_http_health_check = 'test_http_health_check'

    set_flags = {
        'project': expected_project,
    }

    command = self._CreateAndInitializeCommand(
        http_health_check_cmds.GetHttpHealthCheck, 'gethttphealthcheck',
        self.version, set_flags)

    call = self.mock.Respond('compute.httpHealthChecks.get', {})
    command.Handle(expected_http_health_check)
    request = call.GetRequest()

    self.assertEqual('GET', request.method)
    self.assertEqual(None, request.body)

    parameters = request.parameters

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(parameters['httpHealthCheck'], expected_http_health_check)

  def testDeleteHttpHealthCheckGeneratesCorrectRequest(self):
    expected_project = 'test_project'
    expected_http_health_check = 'test_http_health_check'

    set_flags = {
        'project': expected_project,
    }

    command = self._CreateAndInitializeCommand(
        http_health_check_cmds.DeleteHttpHealthCheck, 'deletehttphealthcheck',
        self.version, set_flags)

    call = self.mock.Respond('compute.httpHealthChecks.delete', {})
    command.Handle(expected_http_health_check)
    request = call.GetRequest()

    self.assertEqual('DELETE', request.method)
    self.assertEqual(None, request.body)

    parameters = request.parameters

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(parameters['httpHealthCheck'], expected_http_health_check)

  def testDeleteHttpHealthCheckWithFullyQualifiedPath(self):
    flag_project = 'wrong-project'
    requested_http_health_check = (
        'right-project/global/httpHealthChecks/test_http_health_check')

    set_flags = {
        'project': flag_project,
    }

    command = self._CreateAndInitializeCommand(
        http_health_check_cmds.DeleteHttpHealthCheck, 'deletehttphealthcheck',
        self.version, set_flags)

    call = self.mock.Respond('compute.httpHealthChecks.delete', {})
    command.Handle(requested_http_health_check)
    request = call.GetRequest()

    self.assertEqual('DELETE', request.method)
    self.assertEqual(None, request.body)

    parameters = request.parameters

    self.assertEqual('right-project', parameters['project'])
    self.assertEqual('test_http_health_check', parameters['httpHealthCheck'])

  def testDeleteMultipleHttpHealthChecks(self):
    set_flags = {
        'project': 'test_project',
    }

    command = self._CreateAndInitializeCommand(
        http_health_check_cmds.DeleteHttpHealthCheck, 'deletehttphealthcheck',
        self.version, set_flags)

    expected_http_health_checks = [
        'test-http-health-checks-%02d' % x for x in xrange(5)]

    calls = [self.mock.Respond('compute.httpHealthChecks.delete', {})
             for x in xrange(len(expected_http_health_checks))]

    _, exceptions = command.Handle(*expected_http_health_checks)
    self.assertEqual(0, len(exceptions))

    sorted_calls = sorted([call.GetRequest().parameters['httpHealthCheck'] for
                           call in calls])
    self.assertEqual(expected_http_health_checks, sorted_calls)


if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
