# Copyright 2013 Google Inc. All Rights Reserved.
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

"""Unit testing support for tests that run across all supported api versions."""

import copy
import logging
import StringIO
import sys
import unittest

import gflags as flags

from gcutil_lib import gcutil_logging
from gcutil_lib import mock_api
from gcutil_lib import mock_timer
from gcutil_lib import version


FLAGS = flags.FLAGS
flags.DEFINE_string('test_api_version', None, 'The version of API to test.')


class GcutilTestCase(unittest.TestCase):
  _SUPPORTED_API_VERSIONS = version.SUPPORTED_API_VERSIONS

  def __init__(self, methodName, apiVersion=None):
    # Standard test case constructor has only two parameters: self and
    # methodName. Making additional parameters (apiVersion) optional to conform
    # to the standard signature allows us to run a single test method, which
    # helps debugging during development.
    super(GcutilTestCase, self).__init__(methodName)
    if not apiVersion:
      if not FLAGS.test_api_version:
        self.fail('When apiVersion is not passed in as function parameter, '
                  'it must be specified on command line as flag, '
                  'for example, --test_api_version=v1')
      self.version = FLAGS.test_api_version
    else:
      self.version = apiVersion

  def __str__(self):
    return '{method} [version={version}] ({type})'.format(
        method=self._testMethodName, version=self.version,
        type=self.__class__.__name__)

  def _CreateAndInitializeCommand(self, command_class, name,
                                  service_version=None, set_flags=None):
    """Initialize a command for testing with specified flags.

    Args:
      command_class:  A command object inheriting from
                      command_base.GoogleComputeCommand, e.g.
                      disk_cmds.AddDisk
      name:  Desired name for the command object.
      service_version:  Optional.  Service version to set.
      set_flags:  Optional.  Flags to set.

    Returns:
      An instance of command, initialized with the desired flags.
    """
    flag_values = copy.deepcopy(FLAGS)
    command_with_flags = command_class(name, flag_values)

    if service_version:
      flag_values.service_version = service_version

    flag_values.require_tty = False

    command_with_flags._timer = mock_timer.MockTimer()
    command_with_flags.THREAD_POOL_WAIT_TIME = 0

    if set_flags:
      for flag in set_flags:
        if set_flags[flag] is not None:
          flag_values[flag].present = True
          flag_values[flag].value = set_flags[flag]

    command_with_flags.SetFlags(flag_values)
    command_with_flags.SetApi(self.api)
    command_with_flags._InitializeContextParser()
    command_with_flags._credential = mock_api.MockCredential()

    return command_with_flags


class GcutilLoader(unittest.TestLoader):
  def loadTestsFromTestCase(self, testCaseClass):
    test_cases = []
    for method_name in self.getTestCaseNames(testCaseClass):
      if issubclass(testCaseClass, GcutilTestCase):
        for api_version in testCaseClass._SUPPORTED_API_VERSIONS:
          test_cases.append(testCaseClass(method_name, api_version))
      else:
        test_cases.append(testCaseClass(method_name))
    return self.suiteClass(test_cases)


class CaptureStandardIO(object):
  """Captures stderr/stdout and provides the given text to stdin.

  For example:

  def testMyTest(self):
    with CaptureStandardIO('line1\nline2\n') as stdio:
      runTest()
      self.assertEquals('expectedoutput\n', stdio.stdout.getvalue())
      self.assertEquals('expectederror\n', stdio.stderr.getvalue())

  Args:
    stdin: The input to pass to stdin.
  """

  class MockOutput(object):
    def __init__(self):
      self.real_stdout = sys.stdout
      self.real_stderr = sys.stderr
      self.stdout = StringIO.StringIO()
      self.stderr = StringIO.StringIO()

  def __init__(self, stdin=''):
    self._input_string = stdin
    self.handler = None

  def __enter__(self):
    self._stdout = sys.stdout
    self._stderr = sys.stderr
    self._stdin = sys.stdin
    mock_output = CaptureStandardIO.MockOutput()

    logger = logging.getLogger(gcutil_logging._LOG_ROOT)
    self.handler = logging.StreamHandler(mock_output.stderr)
    logger.addHandler(self.handler)

    sys.stdout = mock_output.stdout
    sys.stderr = mock_output.stderr
    sys.stdin = StringIO.StringIO(self._input_string)
    return mock_output

  def __exit__(self, the_type, value, traceback):
    sys.stdout = self._stdout
    sys.stderr = self._stderr
    sys.stdin = self._stdin

    logger = logging.getLogger(gcutil_logging._LOG_ROOT)
    logger.removeHandler(self.handler)


def SelectTemplateForVersion(template_dict, apiversion):
  """Selects the most recent item from a dict compatible with apiversion.

  Args:
    template_dict:  A dict of things to select from, usually templates in a
      unit test.
    apiversion:  The API version to select for.

  Returns:
    An value from template_dict.
  """
  selected_version = ''

  # By default, selected version will be the smallest in the dict.
  # This takes care of the edge case where the api version is smaller than
  # everything in the dict.
  for template in template_dict:
    if not selected_version or template < version.get(selected_version):
      selected_version = template

  # Now, we select the largest compatible version.
  for template in template_dict:
    if template <= apiversion and template > version.get(selected_version):
      selected_version = template

  return template_dict[selected_version]
