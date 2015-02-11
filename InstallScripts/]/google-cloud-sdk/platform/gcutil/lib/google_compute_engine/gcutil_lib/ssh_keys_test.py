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

"""Unit tests for the ssh key utility."""



import path_initializer
path_initializer.InitSysPath()

import base64

import gflags as flags
import unittest

from gcutil_lib import ssh_keys

FLAGS = flags.FLAGS


class SshKeyTest(unittest.TestCase):


  def testNoKeysProducesEmptyAuthorizedUserKeysString(self):
    authorized_user_keys = ssh_keys.SshKeys.GetAuthorizedUserKeys(
        use_compute_key=False,
        authorized_ssh_keys=[])

    self.assertEqual(authorized_user_keys, [])

  def testGetAuthorizedUserKeysFromMetadata(self):
    mock_ssh_keys = 'foo:bar\nbaz:bat'
    mock_metadata = [
        {'key': 'startup-script', 'value': 'echo "Hello, World!"'},
        {'key': 'sshKeys', 'value': mock_ssh_keys},
        {'key': 'key', 'value': 'value'}]
    authorized_user_keys = ssh_keys.SshKeys.GetAuthorizedUserKeysFromMetadata(
        mock_metadata)

    self.assertEqual(authorized_user_keys,
                     [{'user': 'foo', 'key': 'bar'},
                      {'user': 'baz', 'key': 'bat'}])

  def testGetAuthorizedUserKeysFromMetadataWithNoMetadata(self):
    authorized_user_keys = (
        ssh_keys.SshKeys.GetAuthorizedUserKeysFromMetadata([]))
    self.assertEqual(authorized_user_keys, [])

  def testGetAuthorizedUserKeysFromMetadataWithEmptySshKeys(self):
    authorized_user_keys = ssh_keys.SshKeys.GetAuthorizedUserKeysFromMetadata(
        [{'key': 'sshKeys', 'value': ''}])
    self.assertEqual(authorized_user_keys, [])

  def testGetAuthorizedUserKeysFromMetadataWithSpecialCharsInComment(self):
    comment = 'X' + ''.join([chr(i) for i in range(32, 128)]) + 'X'
    key = 'type content ' + comment
    authorized_user_keys = ssh_keys.SshKeys.GetAuthorizedUserKeysFromMetadata(
        [{'key': 'sshKeys', 'value': 'foo:' + key}])
    self.assertEqual(authorized_user_keys,
                     [{'user': 'foo', 'key': key}])

  def testSetAuthorizedUserKeysInMetadata(self):
    metadata = [{'key': 'key1', 'value': 'value1'},
                {'key': 'sshKeys', 'value': 'foo:bar\nbaz:bat'},
                {'key': 'key3', 'value': 'value3'}]
    ssh_keys.SshKeys.SetAuthorizedUserKeysInMetadata(
        metadata,
        [{'user': 'user1', 'key': 'key1'}, {'user': 'user2', 'key': 'key2'}])
    self.assertEqual(
        [{'key': 'key1', 'value': 'value1'},
         {'key': 'sshKeys', 'value': 'user1:key1\nuser2:key2'},
         {'key': 'key3', 'value': 'value3'}],
        metadata)

  def testValidateSshKey(self):
    key = ('ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCm60IMJ0qIzJB+K4AEpEhyvfEL0eX'
           '2WuQ2LpT51s5JE0UCIUqX7t7cYHwfFxqwx34ZGM5RqZbj2RFkeZfU7NwjAS1YMfjxkT'
           '0l/pGnsCPzCZhV5++U9+AZpnM+669fQiA9pRq9JlL4JJtmz0dZHbBSlOwe2ty6lSS5G'
           'xAcZ+g553dj5NLfTTAH+HRzA9AnySOEExUIJ1Vpix+NEyyRkMQbBHcJnWAnqd+yBe5d'
           'E0ojpO6ZZzciF4waBhmMK4T8kuuXII/bTqlZKGzl3qdzBIhFaMmXDXq+3bw9hRvPb+g'
           'ChIDYiPmx0HJyqtZ7OkRbh5MyR5W/Zu8cn4sjoiBWIfxJ')
    self.assertEqual(key, ssh_keys.SshKeys._ValidateSshKey(key, 'filename'))
    key_with_empty_comment = key + ' '
    self.assertEqual(key_with_empty_comment,
                     ssh_keys.SshKeys._ValidateSshKey(
                         key_with_empty_comment, 'filename'))
    key_with_comment = key + ' comment@comment.com'
    self.assertEqual(key_with_comment,
                     ssh_keys.SshKeys._ValidateSshKey(
                         key_with_comment, 'filename'))
    key_with_spaces_in_comment = key + ' comment comment com'
    self.assertEqual(key_with_spaces_in_comment,
                     ssh_keys.SshKeys._ValidateSshKey(
                         key_with_spaces_in_comment, 'filename'))

    # No key - exception
    self.assertRaises(ssh_keys.UserSetupError, ssh_keys.SshKeys._ValidateSshKey,
                      '', 'filename')

    def AssertUserSetupError(key, message):
      filename = '/the/file/path'
      try:
        ssh_keys.SshKeys._ValidateSshKey(key, filename)
      except ssh_keys.UserSetupError, e:
        self.assertIn(key, e.msg)
        self.assertIn(filename, e.msg)
        self.assertIn(message, e.msg)
      else:
        self.fail('Expected an UserSetupError exception')

    # Newline in the key
    AssertUserSetupError('\n'.join(key.split()), 'single line')
    # Fewer than 2 parts
    AssertUserSetupError(
        ' '.join(key.split()[0:1]),
        'must consist of at least two')
    # Base-64 cannot contain '_'
    AssertUserSetupError(key.replace('Q', '_'), 'is not a valid base64 encoded')
    # Malformed key - not enought data
    AssertUserSetupError(
        'ssh-rsa ' + base64.b64encode('\00\00\04') + ' comment',
        'The key has invalid length.')
    # Malformed key - not enough data for length + type
    AssertUserSetupError(
        'ssh-rsa ' + base64.b64encode('\00\00\00\07ssh-') + ' comment',
        'The key doesn\'t have a valid type.')
    # Malformed key - mismatched type
    AssertUserSetupError(
        ' '.join(['ssh-rsb'] + key.split()[1:]),
        'The decoded key type doesn\'t match.')

if __name__ == '__main__':
  unittest.main()
