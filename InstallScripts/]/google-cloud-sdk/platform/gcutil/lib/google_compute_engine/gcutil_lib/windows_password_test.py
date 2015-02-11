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

"""Unit tests for the windows_password module."""

import path_initializer
path_initializer.InitSysPath()

import random
import re

import unittest

from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_logging
from gcutil_lib import windows_password

LOGGER = gcutil_logging.LOGGER


class WindowsPasswordTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls):
    gcutil_logging.SetupLogging()

  def testValidateStrongPasswordRequirement(self):
    user_name = 'windows_user'
    def _AssertErrorMessageMatchesPattern(password, error_message_pattern):
      try:
        windows_password.ValidateStrongPasswordRequirement(
            password, user_name)
        self.fail('No exception thrown')
      except gcutil_errors.CommandError as e:
        self.assertFalse(re.search(error_message_pattern, e.message) is None)

    # Password too short.
    regexp = r'must be at least \d+ characters long'
    _AssertErrorMessageMatchesPattern('!Ab1234', regexp)

    # Password does not contain enough categories of chars.
    regexp = 'must contain at least 3 types of characters'
    _AssertErrorMessageMatchesPattern('a1234567', regexp)
    _AssertErrorMessageMatchesPattern('Aabcdefg', regexp)
    _AssertErrorMessageMatchesPattern('!abcdefg', regexp)
    _AssertErrorMessageMatchesPattern('!1234567', regexp)

    # Password containing user account name not allowed.
    regexp = 'cannot contain the user account name'
    _AssertErrorMessageMatchesPattern(
        'Ab1G%s!' % user_name, regexp)

    # It is ok for password to contain user account name if the account
    # name is less than 3 characters.
    windows_password.ValidateStrongPasswordRequirement('ab123ABC', 'ab')

  def testGeneratePassword(self):
    class _MockRandom(object):

      def __init__(self, seed):
        self._seed = seed

      def GetRandomGenerator(self):
        return random.Random(self._seed)

    # Use fixed seed for random number generator to make the test
    # deterministic as per CR feedback.
    seed = 1
    LOGGER.info('testGeneratePassword: Seeding mock random with %d.' % seed)
    original_system_random = random.SystemRandom
    random.SystemRandom = _MockRandom(seed).GetRandomGenerator
    try:
      user_name = 'windows_user'

      # Make sure that the generated password meets strong password
      # requirement.
      password = windows_password.GeneratePassword(user_name)
      LOGGER.info('testGeneratePassword: Generated password: %s' % password)
      windows_password.ValidateStrongPasswordRequirement(password, user_name)
    finally:
      random.SystemRandom = original_system_random

if __name__ == '__main__':
  unittest.main()
