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

"""Unit tests for the version_checker module."""



import path_initializer
path_initializer.InitSysPath()

import json
import os
import tempfile

import httplib2

import unittest
from gcutil_lib import version_checker


class VersionCheckerTests(unittest.TestCase):

  class MockHttp(httplib2.Http):
    """A mock for httplib2.Http that always times out on requests."""

    def request(self, *unused_args, **unused_kwargs):
      return (httplib2.Response({
          'status': '200',
          'content-length': '81',
          'last-modified': 'Thu, 28 Jun 2012 21:35:00 GMT',
          'date': 'Fri, 14 Sep 2012 21:59:51 GMT',
          'content-type': 'application/json'}), (
              '{\n "version": "1.3.0",\n "package_name": "gcutil-1.3.0",'
              '\n "tar": "download/gcutil-1.3.0.tar.gz",'
              '\n "zip": "download/gcutil-1.3.0.zip"\n}\n'))

  def testReadCacheWithNonExistentCacheFile(self):
    vc = version_checker.VersionChecker(cache_path='non-existent-file')
    self.assertEqual(vc._ReadCache(), {})

  def testReadCacheWithMalformedJson(self):
    malformed_caches = (
        'MALFORMED JSON',
        '{ "last_checked_version": "1.2", "last_check": 3000.0, }',
        '{ "last_checked_version": "1.2", "last_check": 3000.0 }}',
        '{ "last_checked_version": "1.2", "last_check": 3000.0 }bad characters')

    for malformed_cache in malformed_caches:
      handle, bad_cache_file = tempfile.mkstemp()
      try:
        with os.fdopen(handle, 'w') as f:
          f.write(malformed_cache)

        vc = version_checker.VersionChecker(cache_path=bad_cache_file)
        self.assertEqual(vc._ReadCache(), {})
      finally:
        os.remove(bad_cache_file)

  def testReadCacheWithGoodCache(self):
    handle, cache_file = tempfile.mkstemp()
    try:
      with os.fdopen(handle, 'w') as f:
        f.write('{ "last_checked_version": "1.2", "last_check": 3000.0, '
                ' "last_tar_url": "download/gcutil-1.2.tar.gz", '
                ' "last_zip_url": "download/gcutil-1.2.zip" }')

      vc = version_checker.VersionChecker(cache_path=cache_file)
      self.assertEqual(
          vc._ReadCache(),
          {'last_checked_version': '1.2', 'last_check': 3000,
           'last_tar_url': 'download/gcutil-1.2.tar.gz',
           'last_zip_url': 'download/gcutil-1.2.zip'})
    finally:
      os.remove(cache_file)

  def testWriteToCache(self):
    handle, cache_file = tempfile.mkstemp()
    try:
      cache = {'last_checked_version': '1.2', 'last_check': 3000,
               'last_tar_url': 'download/gcutil-1.2.tar.gz',
               'last_zip_url': 'download/gcutil-1.2.zip'}
      vc = version_checker.VersionChecker(cache_path=cache_file)
      vc._WriteToCache(cache)

      with os.fdopen(handle) as f:
        self.assertEqual(json.load(f), cache)
    finally:
      os.remove(cache_file)

  def testUpdateCache(self):
    vc = version_checker.VersionChecker(
        cache_ttl_sec=20, current_version='1.2.0')
    cache = {}
    vc._UpdateCache(
        cache, http=VersionCheckerTests.MockHttp(), current_time=123456.7)
    self.assertEqual(cache['current_version'], '1.2.0')
    self.assertEqual(cache['last_checked_version'], '1.3.0')
    self.assertEqual(cache['last_tar_url'], 'download/gcutil-1.3.0.tar.gz')
    self.assertEqual(cache['last_zip_url'], 'download/gcutil-1.3.0.zip')
    self.assertEqual(cache['last_check'], 123456.7)

  def testIsCacheMalformed(self):
    malformed_caches = (
        {},
        {'last_checked_version': 'x', 'last_check': 3000.0,
         'current_version': 'y'},
        {'last_checked_version': '1...2', 'last_check': 3000.0,
         'current_version': '1.2'},
        {'last_checked_version': '1.2', 'last_check': 3000,
         'current_version': '1.2.0'},
        {'last_checked_version': '1.2', 'current_version': '1.2.0'},
        {'last_checked_version': '1.2.x', 'last_check': 3000,
         'current_version': '1.2.0'})
    for cache in malformed_caches:
      self.assertTrue(version_checker.VersionChecker._IsCacheMalformed(cache))

    good_caches = (
        {'last_checked_version': '1.3.0', 'last_check': 3000.0,
         'current_version': '1.2.0'},
        {'last_checked_version': '1.3.0', 'last_check': 3000.0,
         'current_version': '1.2.0',
         'last_check_time': '2012-09-17T18:03:48.792579+00:00',
         'latest_version': '1.1.20120628.1214',
         'last_tar_url': 'download/gcutil-1.2.tar.gz',
         'last_zip_url': 'download/gcutil-1.2.zip'})
    for cache in good_caches:
      self.assertFalse(version_checker.VersionChecker._IsCacheMalformed(cache))

  def testIsCacheStale(self):
    vc = version_checker.VersionChecker(
        cache_ttl_sec=20, current_version='1.2.0')
    cache = {'last_checked_version': '1.2', 'last_check': 3000.0,
             'current_version': '1.2.0'}

    self.assertTrue(vc._IsCacheStale(cache, current_time=1))
    self.assertTrue(vc._IsCacheStale(cache, current_time=2000))
    self.assertTrue(vc._IsCacheStale(cache, current_time=2999))
    self.assertFalse(vc._IsCacheStale(cache, current_time=3000))
    self.assertFalse(vc._IsCacheStale(cache, current_time=3005))
    self.assertFalse(vc._IsCacheStale(cache, current_time=3010))
    self.assertFalse(vc._IsCacheStale(cache, current_time=3019))
    self.assertTrue(vc._IsCacheStale(cache, current_time=3020))
    self.assertTrue(vc._IsCacheStale(cache, current_time=3021))
    self.assertTrue(vc._IsCacheStale(cache, current_time=4000))
    self.assertTrue(vc._IsCacheStale(cache, current_time=398457398))

    self.assertTrue(vc._IsCacheStale({}, current_time=1))
    self.assertTrue(vc._IsCacheStale({}, current_time=2000))
    self.assertTrue(vc._IsCacheStale({}, current_time=2999))
    self.assertTrue(vc._IsCacheStale({}, current_time=3000))
    self.assertTrue(vc._IsCacheStale({}, current_time=3005))
    self.assertTrue(vc._IsCacheStale({}, current_time=3010))
    self.assertTrue(vc._IsCacheStale({}, current_time=3019))
    self.assertTrue(vc._IsCacheStale({}, current_time=3020))
    self.assertTrue(vc._IsCacheStale({}, current_time=3021))
    self.assertTrue(vc._IsCacheStale({}, current_time=4000))
    self.assertTrue(vc._IsCacheStale({}, current_time=398457398))

  def testIsCacheStaleWithMalformedCache(self):
    vc = version_checker.VersionChecker(
        cache_ttl_sec=20, current_version='1.2.0')
    malformed_caches = (
        {'last_checked_version': '1.2', 'last_check': 3000,
         'current_version': '1.2.0'},
        {'last_checked_version': '1.2', 'current_version': '1.2.0'},
        {'last_checked_version': '1.2.x', 'last_check': 3000,
         'current_version': '1.2.0'})

    for cache in malformed_caches:
      self.assertTrue(vc._IsCacheStale(cache, current_time=1))
      self.assertTrue(vc._IsCacheStale(cache, current_time=2000))
      self.assertTrue(vc._IsCacheStale(cache, current_time=2999))
      self.assertTrue(vc._IsCacheStale(cache, current_time=3000))
      self.assertTrue(vc._IsCacheStale(cache, current_time=3005))
      self.assertTrue(vc._IsCacheStale(cache, current_time=3010))
      self.assertTrue(vc._IsCacheStale(cache, current_time=3019))
      self.assertTrue(vc._IsCacheStale(cache, current_time=3020))
      self.assertTrue(vc._IsCacheStale(cache, current_time=3021))
      self.assertTrue(vc._IsCacheStale(cache, current_time=4000))
      self.assertTrue(vc._IsCacheStale(cache, current_time=398457398))

  def testIsCacheStaleWithUpgradedVersion(self):
    vc = version_checker.VersionChecker(
        cache_ttl_sec=20, current_version='1.3.0')
    cache = {'last_checked_version': '1.3.0', 'last_check': 3000.0,
             'current_version': '1.2.0'}

    self.assertTrue(vc._IsCacheStale(cache, current_time=1))
    self.assertTrue(vc._IsCacheStale(cache, current_time=2000))
    self.assertTrue(vc._IsCacheStale(cache, current_time=2999))
    self.assertTrue(vc._IsCacheStale(cache, current_time=3000))
    self.assertTrue(vc._IsCacheStale(cache, current_time=3005))
    self.assertTrue(vc._IsCacheStale(cache, current_time=3010))
    self.assertTrue(vc._IsCacheStale(cache, current_time=3019))
    self.assertTrue(vc._IsCacheStale(cache, current_time=3020))
    self.assertTrue(vc._IsCacheStale(cache, current_time=3021))
    self.assertTrue(vc._IsCacheStale(cache, current_time=4000))
    self.assertTrue(vc._IsCacheStale(cache, current_time=398457398))

  def testParseVersionString(self):
    parse_fn = version_checker.VersionChecker._ParseVersionString
    self.assertEqual(parse_fn('1'), (1,))
    self.assertEqual(parse_fn('1.2'), (1, 2))
    self.assertEqual(parse_fn('1.2.0'), (1, 2, 0))
    self.assertEqual(parse_fn('0.1.0'), (0, 1, 0))
    self.assertEqual(parse_fn('12.13.14'), (12, 13, 14))

  def testCompareVersions(self):
    compare_fn = version_checker.VersionChecker._CompareVersions
    self.assertTrue(compare_fn('0', '1.2'))
    self.assertTrue(compare_fn('1.2', '1.3'))
    self.assertTrue(compare_fn('1.2', '1.2.1'))
    self.assertTrue(compare_fn('1.2.0', '1.2.1'))
    self.assertTrue(compare_fn('1.2.0', '1.2.13'))
    self.assertTrue(compare_fn('1.2.0', '1.3'))
    self.assertFalse(compare_fn('1.3', '1.3'))
    self.assertFalse(compare_fn('1.2.2', '1.2.0'))
    self.assertFalse(compare_fn('1.1', '1.0'))

  def testNewVersionExistsWithNonStaleCache(self):

    def MockReadCache():
      return {'last_checked_version': '1.3.0', 'last_check': 3000.0,
              'current_version': '1.2.0',
              'last_tar_url': 'download/gcutil-1.3.0.tar.gz',
              'last_zip_url': 'download/gcutil-1.3.0.zip'}

    def MockIsCacheStale(cache):
      return False

    vc = version_checker.VersionChecker(current_version='1.2.0')
    vc._ReadCache = MockReadCache
    vc._IsCacheStale = MockIsCacheStale
    available, _, _ = vc._NewVersionExists()
    self.assertTrue(available)

    vc = version_checker.VersionChecker(current_version='1.3.0')
    vc._ReadCache = MockReadCache
    vc._IsCacheStale = MockIsCacheStale
    available, _, _ = vc._NewVersionExists()
    self.assertFalse(available)

  def testNewVersionExistsWithStaleCache(self):

    def MockIsCacheStale(cache):
      return True

    def MockUpdateCache(cache):
      cache['last_checked_version'] = '1.3.0'
      cache['last_tar_url'] = 'download/gcutil-1.3.0.tar.gz'
      cache['last_zip_url'] = 'download/gcutil-1.3.0.zip'

    handle, cache_file = tempfile.mkstemp()
    try:
      with os.fdopen(handle, 'w') as f:
        f.write('{ "last_checked_version": "1.2.0", "last_check": 3000.0,'
                '   "current_version": "1.2.0",'
                '   "last_tar_url": "download/gcutil-1.2.0.tar.gz",'
                '   "last_zip_url": "download/gcutil-1.2.0.zip"}')

        vc = version_checker.VersionChecker(cache_path=cache_file,
                                            current_version='1.2.0')
        vc._IsCacheStale = MockIsCacheStale
        vc._UpdateCache = MockUpdateCache
        available, _, _ = vc._NewVersionExists()
        self.assertTrue(available)
        self.assertEqual(vc._ReadCache()['last_checked_version'], '1.3.0')

        def MockUpdateCache2(cache):
          cache['last_checked_version'] = '1.2.0'

        vc._UpdateCache = MockUpdateCache2
        available, _, _ = vc._NewVersionExists()
        self.assertFalse(available)
        self.assertEqual(vc._ReadCache()['last_checked_version'], '1.2.0')
    finally:
      os.remove(cache_file)

  def testGetDownloadLink(self):

    def MockGetSystemWindows():
      return 'Windows'

    vc = version_checker.VersionChecker()
    vc._GetSystem = MockGetSystemWindows
    cache = {'last_checked_version': '1.3.0', 'last_check': 3000.0,
             'current_version': '1.2.0'}
    self.assertEqual(vc._GetDownloadLink(cache), None)

    cache = {'last_checked_version': '1.3.0', 'last_check': 3000.0,
             'current_version': '1.2.0',
             'last_tar_url': 'download/gcutil-1.3.0.tar.gz',
             'last_zip_url': 'download/gcutil-1.3.0.zip'}
    self.assertEqual(vc._GetDownloadLink(cache), 'download/gcutil-1.3.0.zip')

    def MockGetSystemLinux():
      return 'Linux'

    vc._GetSystem = MockGetSystemLinux
    self.assertEqual(vc._GetDownloadLink(cache),
                     'download/gcutil-1.3.0.tar.gz')


if __name__ == '__main__':
  unittest.main()
