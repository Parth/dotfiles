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

"""Test utilities for mocking out metadata_lib.Metadata."""




class MockMetadata(object):
  def __init__(self):
    self._is_present_calls = []
    self._is_present_return_values = []

    self._get_service_account_scopes_calls = []
    self._get_service_account_scopes_return_values = []

  def ExpectIsPresent(self, and_return):
    self._is_present_return_values.append(and_return)

  def ExpectGetServiceAccountScopes(self, and_return):
    self._get_service_account_scopes_return_values.append(and_return)

  def IsPresent(self):
    self._is_present_calls.append({})
    return self._is_present_return_values.pop(0)

  def GetServiceAccountScopes(self, service_account='default'):
    self._get_service_account_scopes_calls.append(
        {'service_account': service_account})
    return_value = self._get_service_account_scopes_return_values.pop(0)
    if isinstance(return_value, Exception):
      raise return_value
    return return_value

  def ExpectsMoreCalls(self):
    return sum(map(len, [self._is_present_return_values,
                         self._get_service_account_scopes_return_values])) > 0
