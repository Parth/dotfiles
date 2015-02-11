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

"""Tests for auth_helper."""



import path_initializer
path_initializer.InitSysPath()

import os


import apiclient
import httplib2
import oauth2client.client as oauth2_client
import oauth2client.multistore_file as oauth2_multistore_file
import oauth2client.tools as oauth2_tools

import gflags as flags
import unittest
from gcutil_lib import auth_helper
from gcutil_lib import gcutil_unittest
from gcutil_lib import metadata_lib
from gcutil_lib import mock_metadata
from gcutil_lib import scopes


FLAGS = flags.FLAGS

CREDS_FILENAME = './unused_filename'


class MockFunctionCall(object):
  """Simple mock function implementation."""

  def __init__(self, return_values=None):
    self.num_calls = 0
    self.calls = []
    self.return_values = return_values

  def __call__(self, *args, **kwargs):
    self.num_calls += 1
    self.calls.append((args, kwargs))
    if self.return_values is None:
      return None
    return self.return_values.pop()


class AuthHelperTest(unittest.TestCase):

  class MockCred(object):
    def __init__(self, result=None):
      self.result = result
      self.calls = 0

    # pylint: disable-msg=g-bad-name
    def authorize(self, http):
      return http

    # pylint: disable-msg=g-bad-name
    def refresh(self, unused_request):
      self.calls += 1
      if isinstance(self.result, Exception):
        # pylint: disable-msg=raising-bad-type
        raise self.result
      if self.result is None:
        raise Exception(
            'MockCredential being called without a programmed result')
      return self.result

  class MockOauth2ClientGce(object):
    def __init__(self, credentials):
      self.credentials = credentials

    def AppAssertionCredentials(self, unused_scope):
      return self.credentials

  class MockCredStorage(object):
    def __init__(self, cred):
      self.cred = cred

    def get(self):
      return self.cred

    def put(self, credentials):
      pass

  @staticmethod
  def MockGetCredentialStorageNoCredentials(unused_credentials_file,
                                            unused_client_id,
                                            unused_user_agent,
                                            unused_desired_scopes):
    return AuthHelperTest.MockCredStorage(None)

  @staticmethod
  def MockGetCredentialStorage(credentials_file,
                               client_id,
                               user_agent,
                               desired_scopes):
    cred = AuthHelperTest.MockCred()
    storage = AuthHelperTest.MockCredStorage(cred)
    cred.credentials_file = credentials_file
    cred.client_id = client_id
    cred.user_agent = user_agent
    cred.scopes = desired_scopes
    cred.invalid = False
    return storage

  @staticmethod
  def MockGetCredentialStorageWithLegacyScopes(credentials_file,
                                               client_id,
                                               user_agent,
                                               desired_scopes):
    if desired_scopes == ' '.join(sorted(scopes.LEGACY_AUTH_SCOPES)):
      cred = AuthHelperTest.MockCred()
      storage = AuthHelperTest.MockCredStorage(cred)
      cred.credentials_file = credentials_file
      cred.client_id = client_id
      cred.user_agent = user_agent
      cred.scopes = desired_scopes
      cred.invalid = False
      return storage
    return AuthHelperTest.MockCredStorage(None)

  @staticmethod
  def CreateMockOAuthFlowRun():
    cred = AuthHelperTest.MockCred()

    def MockOAuthFlowRun(flow, unused_storage, http=None):  # pylint: disable=unused-argument
      if flow:
        cred.client_id = flow.client_id
        cred.client_secret = flow.client_secret
        cred.scopes = flow.scope
        cred.user_agent = flow.user_agent
      return cred

    return (cred, MockOAuthFlowRun)

  def setUp(self):
    FLAGS.credentials_file = CREDS_FILENAME
    # These tests modify functions in other modules.  We need to clean up
    # afterwards.
    self.old_credential_storage = oauth2_multistore_file.get_credential_storage
    self.old_oauth2_tools_run = oauth2_tools.run
    self.old_web_server_flow = oauth2_client.OAuth2WebServerFlow

  def tearDown(self):
    # Replace overridden module functions.
    oauth2_multistore_file.get_credential_storage = self.old_credential_storage
    oauth2_tools.run = self.old_oauth2_tools_run
    oauth2_client.OAuth2WebServerFlow = self.old_web_server_flow

  def testGetValidCred(self):
    oauth2_multistore_file.get_credential_storage = (
        self.MockGetCredentialStorage)
    cred = auth_helper.GetCredentialFromStore(['a', 'b'])
    self.assertEqual(cred.credentials_file, os.path.realpath(CREDS_FILENAME))
    self.assertEqual(cred.client_id, auth_helper.OAUTH2_CLIENT_ID)
    self.assertEqual(cred.user_agent, auth_helper.USER_AGENT)
    self.assertEqual(cred.scopes, 'a b')
    self.assertEqual(cred.invalid, False)

  def testSortScopes(self):
    oauth2_multistore_file.get_credential_storage = (
        self.MockGetCredentialStorage)
    cred = auth_helper.GetCredentialFromStore(['b', 'a'])
    self.assertEqual(cred.credentials_file, os.path.realpath(CREDS_FILENAME))
    self.assertEqual(cred.client_id, auth_helper.OAUTH2_CLIENT_ID)
    self.assertEqual(cred.user_agent, auth_helper.USER_AGENT)
    self.assertEqual(cred.scopes, 'a b')
    self.assertEqual(cred.invalid, False)

  def testNoAskuser(self):
    oauth2_multistore_file.get_credential_storage = (
        self.MockGetCredentialStorage)
    cred = auth_helper.GetCredentialFromStore(['b', 'a'],
                                              force_reauth=True,
                                              ask_user=False)
    self.assertEqual(cred.credentials_file, os.path.realpath(CREDS_FILENAME))
    self.assertEqual(cred.client_id, auth_helper.OAUTH2_CLIENT_ID)
    self.assertEqual(cred.user_agent, auth_helper.USER_AGENT)
    self.assertEqual(cred.scopes, 'a b')
    self.assertEqual(cred.invalid, True)

  def testLegacyScopes(self):
    oauth2_multistore_file.get_credential_storage = (
        self.MockGetCredentialStorageWithLegacyScopes)
    cred = auth_helper.GetCredentialFromStore(
        scopes.DEFAULT_AUTH_SCOPES)
    self.assertEqual(cred.credentials_file, os.path.realpath(CREDS_FILENAME))
    self.assertEqual(cred.client_id, auth_helper.OAUTH2_CLIENT_ID)
    self.assertEqual(cred.user_agent, auth_helper.USER_AGENT)
    self.assertEqual(cred.scopes, ' '.join(sorted(scopes.LEGACY_AUTH_SCOPES)))
    self.assertEqual(cred.invalid, False)

  def testReauthFlow(self):
    oauth2_multistore_file.get_credential_storage = (
        self.MockGetCredentialStorage)

    (mock_cred, oauth2_tools.run) = self.CreateMockOAuthFlowRun()
    cred = auth_helper.GetCredentialFromStore(['b', 'a'],
                                              force_reauth=True,
                                              ask_user=True)
    self.assertEqual(mock_cred, cred)
    self.assertEqual(cred.client_id, auth_helper.OAUTH2_CLIENT_ID)
    self.assertEqual(cred.client_secret, auth_helper.OAUTH2_CLIENT_SECRET)
    self.assertEqual(cred.user_agent, auth_helper.USER_AGENT)
    self.assertEqual(cred.scopes, 'a b')

  def testAuthWithMetadataServer(self):
    desired_scopes = [
        'https://www.googleapis.com/auth/compute',
        'https://www.googleapis.com/auth/devstorage.full_control',
        ]
    metadata = mock_metadata.MockMetadata()
    metadata.ExpectIsPresent(True)
    metadata.ExpectGetServiceAccountScopes(desired_scopes)
    oauth2_multistore_file.get_credential_storage = (
        self.MockGetCredentialStorage)
    gce_cred = AuthHelperTest.MockCred('accesstoken')
    cred = auth_helper.GetCredentialFromStore(
        desired_scopes,
        metadata=metadata,
        oauth2_gce=AuthHelperTest.MockOauth2ClientGce(gce_cred))
    self.assertEquals(gce_cred, cred)
    self.assertEquals(1, cred.calls)

  def testAuthWithMetadataServerNoServiceAccountsNoAuth(self):
    desired_scopes = [
        'https://www.googleapis.com/auth/compute',
        'https://www.googleapis.com/auth/devstorage.full_control',
        ]
    metadata = mock_metadata.MockMetadata()
    metadata.ExpectIsPresent(True)
    metadata.ExpectGetServiceAccountScopes(
        metadata_lib.MetadataError('No service accounts man'))
    oauth2_multistore_file.get_credential_storage = (
        self.MockGetCredentialStorageNoCredentials)
    oauth2_client.OAuth2WebServerFlow = MockFunctionCall()
    (mock_cred, oauth2_tools.run) = self.CreateMockOAuthFlowRun()

    with gcutil_unittest.CaptureStandardIO('verificationcode\n') as stdio:
      cred = auth_helper.GetCredentialFromStore(
          desired_scopes,
          metadata=metadata,
          oauth2_gce=AuthHelperTest.MockOauth2ClientGce(None))
      self.assertEquals(mock_cred, cred)
      self.assertEquals(1, oauth2_client.OAuth2WebServerFlow.num_calls)
      stdout_lines = stdio.stdout.getvalue().split('\n')
      self.assertTrue('Service account scopes are not enabled' in
                      stdout_lines[0])

  def testAuthNoMetadataServer(self):
    desired_scopes = [
        'https://www.googleapis.com/auth/compute',
        'https://www.googleapis.com/auth/devstorage.full_control',
        ]
    metadata = mock_metadata.MockMetadata()
    metadata.ExpectIsPresent(False)
    oauth2_multistore_file.get_credential_storage = (
        self.MockGetCredentialStorage)

    gce_cred = AuthHelperTest.MockCred(
        httplib2.ServerNotFoundError('metadata server not found'))

    cred = auth_helper.GetCredentialFromStore(
        desired_scopes,
        metadata=metadata,
        oauth2_gce=AuthHelperTest.MockOauth2ClientGce(gce_cred))
    self.assertNotEquals(gce_cred, cred)
    self.assertEquals(0, cred.calls)


if __name__ == '__main__':
  unittest.main()
