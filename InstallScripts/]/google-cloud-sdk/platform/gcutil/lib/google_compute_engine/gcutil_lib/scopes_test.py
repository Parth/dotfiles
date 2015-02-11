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

"""Tests for scopes module."""



import path_initializer
path_initializer.InitSysPath()

import unittest
from gcutil_lib import scopes


class ScopesTest(unittest.TestCase):
  def testExpandPassthrough(self):
    scopes_in = ['foo', 'bar', scopes.TASKQUEUE]
    scopes_out = scopes.ExpandScopeAliases(scopes_in)
    self.assertEqual(scopes_out, scopes_in)

  def testExpandEmpty(self):
    scopes_in = []
    scopes_out = scopes.ExpandScopeAliases(scopes_in)
    self.assertEqual(scopes_out, scopes_in)

  def testExpandSingle(self):
    scopes_in = ['compute-rw']
    scopes_out = scopes.ExpandScopeAliases(scopes_in)
    self.assertEqual(scopes_out, [scopes.COMPUTE_RW_SCOPE])

  def testExpandMixed(self):
    scopes_in = ['compute-rw', scopes.TASKQUEUE]
    scopes_out = scopes.ExpandScopeAliases(scopes_in)
    self.assertEqual(scopes_out, [scopes.COMPUTE_RW_SCOPE, scopes.TASKQUEUE])

if __name__ == '__main__':
  unittest.main()
