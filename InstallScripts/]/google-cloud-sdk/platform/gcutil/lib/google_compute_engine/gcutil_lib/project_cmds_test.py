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

"""Unit tests for the project commands."""



import path_initializer
path_initializer.InitSysPath()

import base64
import copy
import json
import os
import tempfile


from google.apputils import app
import gflags as flags
import unittest

from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api
from gcutil_lib import old_mock_api
from gcutil_lib import project_cmds

FLAGS = flags.FLAGS


class ProjectCmdsTest(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)

  def testGetProjectWithFullyQualifiedPathGeneratesCorrectRequest(self):
    project = 'cool-project'

    command = self._CreateAndInitializeCommand(project_cmds.GetProject,
                                               'getproject',
                                               self.version)

    qualified_project = 'projects/%s' % project

    project_call = self.mock.Respond('compute.projects.get', {})
    command.Handle(qualified_project)

    request = project_call.GetRequest()

    self.assertEquals(project, request.parameters['project'])

  def testSetCommonInstanceMetadataNoFingerprintGeneratesCorrectRequest(self):
    set_flags = {'project': 'swordfish', 'metadata': ['foo:bar']}

    command = self._CreateAndInitializeCommand(
        project_cmds.SetCommonInstanceMetadata,
        'setcommoninstancemetadata',
        self.version,
        set_flags)

    self.mock.Respond('compute.projects.get', {})
    project_call = self.mock.Respond(
        'compute.projects.setCommonInstanceMetadata',
        {})
    command.Handle()

    request = project_call.GetRequest()

    self.assertEquals(set_flags['project'], request.parameters['project'])

    expected = {'kind': 'compute#metadata',
                'items': [{'key': 'foo', 'value': 'bar'}]}
    self.assertEquals(expected, json.loads(request.body))

  def testSetCommonInstanceMetadataWithFingerprintGeneratesCorrectRequest(self):
    fingerprint = base64.b64encode('apple', '-_')
    set_flags = {'project': 'swordfish',
                 'fingerprint': fingerprint,
                 'metadata': ['foo:bar']}

    command = self._CreateAndInitializeCommand(
        project_cmds.SetCommonInstanceMetadata,
        'setcommoninstancemetadata',
        self.version,
        set_flags)

    self.mock.Respond('compute.projects.get', {})
    project_call = self.mock.Respond(
        'compute.projects.setCommonInstanceMetadata',
        {})
    command.Handle()

    request = project_call.GetRequest()

    self.assertEquals(set_flags['project'], request.parameters['project'])
    expected = {'kind': 'compute#metadata',
                'fingerprint': fingerprint,
                'items': [{'key': 'foo', 'value': 'bar'}]}
    self.assertEquals(expected, json.loads(request.body))


class OldProjectCmdsTest(unittest.TestCase):
  def testGetProjectGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)

    command = project_cmds.GetProject('getproject', flag_values)

    expected_project = 'test_project'
    flag_values.project = expected_project

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()

    result = command.Handle()

    self.assertEqual(result['project'], expected_project)

  def testSetCommonInstanceMetadataGeneratesCorrectRequest(self):

    class SetCommonInstanceMetadata(object):

      def __call__(self, project, body):
        self._project = project
        self._body = body
        return self

      def execute(self):
        return {'project': self._project, 'body': self._body}

    flag_values = copy.deepcopy(FLAGS)
    command = project_cmds.SetCommonInstanceMetadata(
        'setcommoninstancemetadata', flag_values)

    expected_project = 'test_project'
    flag_values.project = expected_project
    flag_values.service_version = 'v1'
    handle, path = tempfile.mkstemp()
    try:
      with os.fdopen(handle, 'w') as metadata_file:
        metadata_file.write('foo:bar')
        metadata_file.flush()

        flag_values.metadata_from_file = ['sshKeys:%s' % path]

        command.SetFlags(flag_values)
        command.SetApi(old_mock_api.CreateMockApi())
        command._InitializeContextParser()
        command.api.projects.get = old_mock_api.CommandExecutor(
            {'commonInstanceMetadata': [{'key': 'sshKeys', 'value': ''}]})
        command.api.projects.setCommonInstanceMetadata = (
            SetCommonInstanceMetadata())

        result = command.Handle()
        self.assertEquals(expected_project, result['project'])
        self.assertEquals(
            {'kind': 'compute#metadata',
             'items': [{'key': 'sshKeys', 'value': 'foo:bar'}]},
            result['body'])
    finally:
      os.remove(path)

  def testSetCommonInstanceMetadataChecksForOverwrites(self):
    flag_values = copy.deepcopy(FLAGS)
    command = project_cmds.SetCommonInstanceMetadata(
        'setcommoninstancemetadata', flag_values)

    expected_project = 'test_project'
    flag_values.project = expected_project
    flag_values.service_version = 'v1'
    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    command.api.projects.get = old_mock_api.CommandExecutor(
        {'commonInstanceMetadata': [{'key': 'sshKeys', 'value': 'foo:bar'}]})

    self.assertRaises(gcutil_errors.CommandError, command.Handle)

  class SetUsageExportBucket(object):

    def __call__(self, project, body):
      self._project = project
      self._body = body
      return self

    # The methods generated by the apiclient library violate the naming
    # rule for methods, so to mock them out here we have to disable the
    # corresponding pylint message.
    # pylint: disable=g-bad-name
    def execute(self):
      return {'project': self._project, 'body': self._body}

  def testSetUsageExportBucketGeneratesCorrectRequest(self):
    expected_project = 'test_project'
    bucket = 'my_bucket'
    report_name_prefix = 'some/interesting/prefix/here'

    flag_values = copy.deepcopy(FLAGS)
    command = project_cmds.SetUsageExportBucket(
        'setusagebucket', flag_values)

    flag_values.project = expected_project
    # Parse is required to set .present to true
    flag_values['bucket'].Parse(bucket)
    flag_values['prefix'].Parse(report_name_prefix)

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    command.api.projects.setUsageExportBucket = (
        OldProjectCmdsTest.SetUsageExportBucket())

    result = command.Handle()
    self.assertEquals(expected_project, result['project'])
    self.assertEquals(
        {'kind': 'compute#usageExportLocation',
         'bucketName': bucket,
         'reportNamePrefix': report_name_prefix},
        result['body'])

  def testSetUsageExportBucketErrorWhenNoBucket(self):
    expected_project = 'test_project'

    flag_values = copy.deepcopy(FLAGS)
    command = project_cmds.SetUsageExportBucket(
        'setusagebucket', flag_values)

    flag_values.project = expected_project

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    command.api.projects.setUsageExportBucket = (
        OldProjectCmdsTest.SetUsageExportBucket())

    self.assertRaises(app.UsageError, command.Handle)

  def testClearUsageExportGeneratesCorrectRequest(self):

    expected_project = 'test_project'

    flag_values = copy.deepcopy(FLAGS)
    command = project_cmds.ClearUsageExportBucket(
        'clearusagebucket', flag_values)

    flag_values.project = expected_project

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()
    command.api.projects.setUsageExportBucket = (
        OldProjectCmdsTest.SetUsageExportBucket())

    result = command.Handle()
    self.assertEquals(expected_project, result['project'])
    self.assertEquals(
        {'kind': 'compute#usageExportLocation'},
        result['body'])


if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
