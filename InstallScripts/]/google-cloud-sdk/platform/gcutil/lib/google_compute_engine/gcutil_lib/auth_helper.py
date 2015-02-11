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

"""Google Compute Engine specific helpers to use the common auth library."""



import json
import os
import sys
import textwrap

import httplib2

import oauth2client.client as oauth2_client
import oauth2client.gce as oauth2_gce_client
import oauth2client.multistore_file as oauth2_multistore_file
import oauth2client.tools as oauth2_tools

import gflags as flags

from gcutil_lib import metadata_lib
from gcutil_lib import scopes
from gcutil_lib import utils

FLAGS = flags.FLAGS

# These identifieres are required as part of the OAuth2 spec but have
# limited utility with a command line tool.  Note that the secret
# isn't really secret here.  These are copied from the Identity tab on
# the Google APIs Console <http://code.google.com/apis/console>
OAUTH2_CLIENT_ID = '32555940559.apps.googleusercontent.com'
OAUTH2_CLIENT_SECRET = 'ZmssLNjJy2998hD4CTg2ejr2'
USER_AGENT = 'Cloud SDK Command Line Tool'



flags.DEFINE_string(
    'credentials_file',
    '~/.gcutil_auth',
    'File where user authorization credentials are stored.')

flags.DEFINE_string(
    'auth_service_account',
    'default',
    'Service account to use for automatic authorization. '
    'Empty string disables automatic authorization.')

flags.DEFINE_string(
    'authorization_uri_base',
    'https://accounts.google.com/o/oauth2',
    'The base URI for authorization requests')


# pylint: disable-msg=unused-argument
def GetCredentialFromStore(desired_scopes,
                           ask_user=True,
                           force_reauth=False,
                           credentials_file=None,
                           authorization_uri_base=None,
                           client_id=OAUTH2_CLIENT_ID,
                           client_secret=OAUTH2_CLIENT_SECRET,
                           user_agent=USER_AGENT,
                           metadata=metadata_lib.Metadata(),
                           oauth2_gce=oauth2_gce_client,
                           logger=None):
  """Get OAuth2 credentials for a specific scope.

  Args:
    desired_scopes: A list of OAuth2 scopes to request.
    ask_user: If True, prompt the user to authenticate.
    force_reauth: If True, force users to reauth
    credentials_file: The file to use to get/store credentials. If left at None
      FLAGS.credentials_file will be used.
    authorization_uri_base: The base URI for auth requests. If left at None
      FLAGS.authorization_uri_base will be used.
    client_id: The OAuth2 client id
    client_secret: The OAuth2 client secret
    user_agent: The user agent for requests

  Returns:
    An OAuth2Credentials object or None
  """
  if not credentials_file:
    credentials_file = FLAGS.credentials_file
  if not authorization_uri_base:
    authorization_uri_base = FLAGS.authorization_uri_base

  credentials_file = os.path.realpath(os.path.expanduser(credentials_file))

  # Ensure that the directory to contain the credentials file exists.
  credentials_dir = os.path.expanduser(os.path.dirname(credentials_file))
  if not os.path.exists(credentials_dir):
    os.makedirs(credentials_dir)


  desired_scopes = ['https://www.googleapis.com/auth/appengine.admin', 'https://www.googleapis.com/auth/bigquery', 'https://www.googleapis.com/auth/compute', 'https://www.googleapis.com/auth/devstorage.full_control', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/ndev.cloudman', 'https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/sqlservice.admin', 'https://www.googleapis.com/auth/prediction', 'https://www.googleapis.com/auth/projecthosting']
  desired_scopes_str = ' '.join(desired_scopes)

  metadata_present = False
  if FLAGS.auth_service_account:
    metadata_present = metadata.IsPresent()

  storage = oauth2_multistore_file.get_credential_storage(
      credentials_file, client_id, user_agent, desired_scopes_str)

  if FLAGS.auth_service_account and metadata_present:
    try:
      vm_scopes = metadata.GetServiceAccountScopes()
      # Only use gce auth if there is a compute scope in there.
      if (scopes.COMPUTE_RW_SCOPE in vm_scopes or
          scopes.COMPUTE_RO_SCOPE in vm_scopes or
          scopes.CLOUD_PLATFORM_SCOPE in vm_scopes):
        try:
          credentials = oauth2_gce.AppAssertionCredentials([])
          credentials.refresh(utils.GetHttp())
          http = credentials.authorize(utils.GetHttp())
          resp, content = http.request(
              'https://www.googleapis.com/userinfo/v2/me')
          if resp.status == 200:
            userinfo = json.loads(content)
            credentials.token_id = userinfo
          storage.put(credentials)
          return credentials
        except httplib2.ServerNotFoundError:
          # We are not running on a VM.
          pass
        except oauth2_client.AccessTokenRefreshError:
          # We are probably not running on a VM.
          pass
    except metadata_lib.MetadataError:
      # We don't seem to have any scopes.
      pass

  credentials = storage.get()

  if not credentials or credentials.invalid:
    # Look for the legacy auth scopes, in case they're present, we can use
    # them instead.
    legacy_desired_scopes_str = ' '.join(sorted(scopes.LEGACY_AUTH_SCOPES))
    legacy_storage = oauth2_multistore_file.get_credential_storage(
        credentials_file, client_id, user_agent, legacy_desired_scopes_str)
    credentials = legacy_storage.get()

  if force_reauth and credentials:
    credentials.invalid = True

  if (not credentials or credentials.invalid == True) and ask_user:
    if FLAGS.auth_service_account and metadata_present:
      print ('Service account scopes are not enabled for %s on this instance. '
             'Using manual authentication.') % (FLAGS.auth_service_account)

    # If gcutil is being run from within the Cloud SDK, do not do the web flow.
    # Instead, print out a message indicating that the user must log in via
    # "gcloud auth login".
    if os.environ.get('CLOUDSDK_WRAPPER', '0') == '1':
      msg = textwrap.dedent("""\
      You are not currently logged in. To authenticate, run
       $ gcloud auth login
      """)
      sys.stderr.write(msg)
      sys.exit(1)

    flow = oauth2_client.OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope=desired_scopes_str,
        user_agent=user_agent,
        auth_uri=authorization_uri_base + '/auth',
        token_uri=authorization_uri_base + '/token')
    credentials = oauth2_tools.run(flow, storage, http=utils.GetHttp())
  return credentials
