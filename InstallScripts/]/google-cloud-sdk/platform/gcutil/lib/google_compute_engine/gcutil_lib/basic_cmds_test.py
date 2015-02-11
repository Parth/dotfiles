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

"""Unit tests for the compute commands."""



import path_initializer
path_initializer.InitSysPath()

import copy


import gflags as flags
import unittest

from gcutil_lib import auth_helper
from gcutil_lib import basic_cmds
from gcutil_lib import flags_cache

FLAGS = flags.FLAGS


class ComputeCmdsTest(unittest.TestCase):
  def testAuthDoesNotBuildApi(self):
    class MockFlagsCache(object):
      """Mock FlagsCache for testing."""

      def SynchronizeFlags(self):
        """Mock SynchronizeFlags method that does nothing."""
        pass

    class MockCredential(object):
      """Mock OAuth2 Credential."""

      def authorize(self, http):
        """Authorize an http2.Http instance with this credential.

        Args:
          http: httplib2.http to append authorization to.

        Returns:
          An httplib2.http compatible object.
        """
        return http

    def MockGetCredentialFromStore(scopes,
                                   ask_user,
                                   force_reauth):
      """Returns a mock cred.

      Args:
        scopes: Scopes for which auth is being requested.
        ask_user: Should the user be asked to auth?
        force_reauth: Force user to reauth.

      Returns:
        A credentials object.
      """
      force_reauth = force_reauth  # silence lint
      ask_user = ask_user
      scopes = scopes
      return MockCredential()

    flag_values = copy.deepcopy(FLAGS)
    flags_cache.FlagsCache = MockFlagsCache
    auth_helper.GetCredentialFromStore = MockGetCredentialFromStore

    command = basic_cmds.AuthCommand('auth', flag_values)

    flag_values.fetch_discovery = False
    flag_values.api_host = None
    flag_values.service_version = None
    flag_values.project = None
    flag_values.force_reauth = True
    flag_values.confirm_email = False

    command.SetFlags(flag_values)
    result = command.RunWithFlagsAndPositionalArgs(flag_values,
                                                   ['path/to/gcutil'])
    self.assertEqual(result, (None, []))

  def testGetVersionGeneratesCorrectResponse(self):
    flag_values = copy.deepcopy(FLAGS)
    command = basic_cmds.GetVersion('version', flag_values)
    result = command.Run([])

    self.assertEqual(result, 0)
    self.assertEqual(
        basic_cmds.version.__version__, '1.16.5')


if __name__ == '__main__':
  unittest.main()
