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

"""Unit tests for the region commands."""



import path_initializer
path_initializer.InitSysPath()

import gflags as flags
import unittest

from gcutil_lib import gcutil_unittest
from gcutil_lib import mock_api
from gcutil_lib import region_cmds

FLAGS = flags.FLAGS


class RegionCmdsTest(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)

  def testQualifiedRegionGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_region = 'twilight-region'

    set_flags = {
        'project': 'wrong-project',
    }

    command = self._CreateAndInitializeCommand(
        region_cmds.GetRegion, 'getregion', self.version, set_flags)

    region_call = self.mock.Respond('compute.regions.get', {})

    qualified_region = 'projects/%s/regions/%s' % (expected_project,
                                                   expected_region)

    command.Handle(qualified_region)

    request = region_call.GetRequest()

    self.assertEqual(expected_region, request.parameters['region'])
    self.assertEqual(expected_project, request.parameters['project'])

  def testGetRegionGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_region = 'twilight-region'

    set_flags = {
        'project': expected_project,
    }

    command = self._CreateAndInitializeCommand(
        region_cmds.GetRegion, 'getregion', self.version, set_flags)

    region_call = self.mock.Respond('compute.regions.get', {})

    command.Handle(expected_region)

    request = region_call.GetRequest()

    self.assertEqual(expected_region, request.parameters['region'])
    self.assertEqual(expected_project, request.parameters['project'])


if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
