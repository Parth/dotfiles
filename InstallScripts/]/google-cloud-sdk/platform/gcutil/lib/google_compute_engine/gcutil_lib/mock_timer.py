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

"""Mock timer for gcutil unit tests."""


class MockTimer(object):
  """Mock timer for testing."""

  def __init__(self):
    self._current_time = 0

  def time(self):
    return self._current_time

  def sleep(self, time_to_sleep):
    self._current_time += time_to_sleep
    return self._current_time
