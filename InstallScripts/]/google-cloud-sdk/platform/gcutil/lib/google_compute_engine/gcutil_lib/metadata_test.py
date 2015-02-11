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

"""Unit tests for the metadata package."""


from __future__ import with_statement



import path_initializer
path_initializer.InitSysPath()

import copy
import os
import tempfile

from google.apputils import app
import gflags as flags
import unittest

from gcutil_lib import metadata


FLAGS = flags.FLAGS


class MetadataTest(unittest.TestCase):

  def testGatherMetadata(self):
    flag_values = copy.deepcopy(FLAGS)
    metadata_flags_processor = metadata.MetadataFlagsProcessor(flag_values)

    handle, path = tempfile.mkstemp()
    try:
      with os.fdopen(handle, 'w') as metadata_file:
        metadata_file.write('metadata file content')
        metadata_file.flush()

        flag_values.metadata = ['bar:baz']
        flag_values.metadata_from_file = ['bar_file:%s' % path]

        metadata_entries = metadata_flags_processor.GatherMetadata()

        self.assertEqual(len(metadata_entries), 2)
        self.assertEqual(metadata_entries[0]['key'], 'bar')
        self.assertEqual(metadata_entries[0]['value'], 'baz')
        self.assertEqual(metadata_entries[1]['key'], 'bar_file')
        self.assertEqual(metadata_entries[1]['value'],
                         'metadata file content')
    finally:
      os.remove(path)

  def testGatherMetadataWithDuplicateKeys(self):
    flag_values = copy.deepcopy(FLAGS)
    metadata_flags_processor = metadata.MetadataFlagsProcessor(flag_values)

    flag_values.metadata = ['bar:baz', 'bar:foo']
    self.assertRaises(app.UsageError, metadata_flags_processor.GatherMetadata)

    flag_values.metadata = ['bar:baz', 'bar:foo', 'foo:baz', 'foobar:val']
    self.assertRaises(app.UsageError, metadata_flags_processor.GatherMetadata)

    flag_values.metadata = ['foo:foo', 'bar:baz', 'bar:foo', 'foo:baz',
                            'foobar:val']
    self.assertRaises(app.UsageError, metadata_flags_processor.GatherMetadata)

    handle, path = tempfile.mkstemp()
    try:
      with os.fdopen(handle, 'w') as metadata_file:
        metadata_file.write('metadata file content')
        metadata_file.flush()
        flag_values.metadata = ['bar:baz']
        flag_values.metadata_from_file = ['bar:%s' % metadata_file.name]
        self.assertRaises(app.UsageError,
                          metadata_flags_processor.GatherMetadata)
    finally:
      os.remove(path)

  def testGatherMetadataWithBannedMetadata(self):
    flag_values = copy.deepcopy(FLAGS)
    metadata_flags_processor = metadata.MetadataFlagsProcessor(flag_values)

    flag_values.metadata = [
        metadata.INITIAL_WINDOWS_PASSWORD_METADATA_NAME + ':' + 'Pa$$0rd']
    self.assertRaises(app.UsageError, metadata_flags_processor.GatherMetadata)

if __name__ == '__main__':
  unittest.main()
