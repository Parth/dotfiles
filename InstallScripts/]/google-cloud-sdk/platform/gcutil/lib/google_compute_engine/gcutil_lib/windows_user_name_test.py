# Copyright 2014 Google Inc. All Rights Reserved.
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

"""Unit tests for the windows_user_name module."""

import path_initializer
path_initializer.InitSysPath()

import re

import unittest

from gcutil_lib import gcutil_errors
from gcutil_lib import mock_api
from gcutil_lib import windows_user_name


class WindowsUserNameTest(unittest.TestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi('v1')

  def testValidateUserName(self):
    def _AssertErrorMessageMatchesPattern(user_name, error_message_pattern):
      try:
        windows_user_name.ValidateUserName(user_name)
        self.fail('No exception thrown')
      except gcutil_errors.CommandError as e:
        self.assertFalse(re.search(error_message_pattern, e.message) is None)

    # Test invalid user names.
    regexp = 'The user name is missing.'
    _AssertErrorMessageMatchesPattern('', regexp)

    regexp = r'length must not exceed \d+ characters'
    _AssertErrorMessageMatchesPattern('123456789012345678901', regexp)

    regexp = 'contains invalid characters'
    _AssertErrorMessageMatchesPattern('user=', regexp)
    _AssertErrorMessageMatchesPattern('u:ser', regexp)

    regexp = 'cannot consist solely of periods or spaces'
    _AssertErrorMessageMatchesPattern('. . .', regexp)

    regexp = '"administrator" as initial user name is not allowed'
    _AssertErrorMessageMatchesPattern('Administrator', regexp)

    # Test a few valid names.
    windows_user_name.ValidateUserName('a')
    windows_user_name.ValidateUserName('12345678901234567890')
    windows_user_name.ValidateUserName('a.b.c  d')

  def testGenerateLocalUserNameBasedOnProjectWithProjectId(self):
    def _AssertErrorMessageMatchesPattern(project_id, error_message_pattern):
      try:
        windows_user_name.GenerateLocalUserNameBasedOnProject(
            project_id, self.api)
        self.fail('No exception thrown')
      except gcutil_errors.CommandError as e:
        self.assertFalse(re.search(error_message_pattern, e.message) is None)

    self.assertEqual(
        'abcd',
        windows_user_name.GenerateLocalUserNameBasedOnProject(
            'abcd', self.api))

    self.assertEqual(
        'abcd1234567890123456',
        windows_user_name.GenerateLocalUserNameBasedOnProject(
            'abcd1234567890123456', self.api))

    self.assertEqual(
        'abcd1234567890123456',
        windows_user_name.GenerateLocalUserNameBasedOnProject(
            'abcd12345678901234567890', self.api))

    # Project ID contains invalid chars.
    _AssertErrorMessageMatchesPattern('abc===', 'The user name .* is invalid')

  def testGenerateLocalUserNameBasedOnProjectWithProjectNumber(self):
    def _MockGetProjectResponse(project_id):
      self.mock.Respond(
          'compute.projects.get',
          {
              'kind': 'compute#project',
              'name': project_id,
              'description': 'project description',
              'selfLink': 'https://www.googleapis.com/compute/v1/projects/%s'
                          % project_id
          })

    _MockGetProjectResponse('u1234')
    self.assertEqual(
        'u1234',
        windows_user_name.GenerateLocalUserNameBasedOnProject(
            '384738', self.api))

    _MockGetProjectResponse('abcd12345678901234567890')
    self.assertEqual(
        'abcd1234567890123456',
        windows_user_name.GenerateLocalUserNameBasedOnProject(
            '384738', self.api))

if __name__ == '__main__':
  unittest.main()
