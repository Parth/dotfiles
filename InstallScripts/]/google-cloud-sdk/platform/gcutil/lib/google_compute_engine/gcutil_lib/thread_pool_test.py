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

"""Tests for thread_pool."""



import path_initializer
path_initializer.InitSysPath()

import time

import unittest
from gcutil_lib import thread_pool


class TestOperation(thread_pool.Operation):
  def __init__(self, raise_exception=False, sleep_time=0):
    thread_pool.Operation.__init__(self)
    self.raise_exception = raise_exception
    self.sleep_time = sleep_time

  def Run(self):
    if self.sleep_time:
      time.sleep(self.sleep_time)
    if self.raise_exception:
      raise Exception('Exception!')
    return 42


class ThreadPoolTest(unittest.TestCase):
  def testBasic(self):
    """Test basic start up and shutdown."""
    tp = thread_pool.ThreadPool(3, 0.2)
    tp.WaitShutdown()

  def testSubmit(self):
    tp = thread_pool.ThreadPool(3, 0.2)

    ops = []
    for _ in xrange(20):
      op = TestOperation()
      ops.append(op)
      tp.Add(op)
    tp.WaitShutdown()
    for op in ops:
      self.assertEqual(op.Result(), 42)
      self.assertFalse(op.RaisedException())

  def testLongOps(self):
    tp = thread_pool.ThreadPool(3, 0.2)

    ops = []
    for _ in xrange(10):
      op = TestOperation(sleep_time=0.1)
      ops.append(op)
      tp.Add(op)
    tp.WaitShutdown()
    for op in ops:
      self.assertEqual(op.Result(), 42)
      self.assertFalse(op.RaisedException())

  def testExceptionOps(self):
    tp = thread_pool.ThreadPool(3, 0.2)

    ops = []
    for _ in xrange(20):
      op = TestOperation(raise_exception=0.1)
      ops.append(op)
      tp.Add(op)
    tp.WaitShutdown()
    for op in ops:
      self.assertEqual(str(op.Result()), 'Exception!')
      self.assertTrue(op.RaisedException())

if __name__ == '__main__':
  unittest.main()
