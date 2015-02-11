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

"""The Google API scopes used by Google Compute Engine."""



USER_INFO_SCOPE = 'https://www.googleapis.com/auth/userinfo.email'
COMPUTE_RW_SCOPE = 'https://www.googleapis.com/auth/compute'
COMPUTE_RO_SCOPE = 'https://www.googleapis.com/auth/compute.readonly'
DATASTORE = 'https://www.googleapis.com/auth/datastore'
STORAGE_R_SCOPE = 'https://www.googleapis.com/auth/devstorage.read_only'
STORAGE_W_SCOPE = 'https://www.googleapis.com/auth/devstorage.write_only'
STORAGE_RW_SCOPE = (
        'https://www.googleapis.com/auth/devstorage.read_write')
STORAGE_FULL_SCOPE = 'https://www.googleapis.com/auth/devstorage.full_control'
CLOUD_PLATFORM_SCOPE = 'https://www.googleapis.com/auth/cloud-platform'


# Historically we asked for these scopes, but not all are needed.  In order
# to simplify the 3LO scope authorization page, we no longer ask for all of
# them.
LEGACY_AUTH_SCOPES = [
    COMPUTE_RW_SCOPE, COMPUTE_RO_SCOPE,
    # USER_INFO_SCOPE allows seeing who user authenticated as, which helps
    # to debug auth issues.
    USER_INFO_SCOPE,
    # Image commands use STORAGE access.
    STORAGE_R_SCOPE, STORAGE_W_SCOPE, STORAGE_RW_SCOPE, STORAGE_FULL_SCOPE
    ]

# These are the set of scopes we ask for when running 'gcutil auth'.
DEFAULT_AUTH_SCOPES = [
    COMPUTE_RW_SCOPE,
    # USER_INFO_SCOPE allows seeing who user authenticated as, which helps
    # to debug auth issues.
    USER_INFO_SCOPE,
    # Image commands use STORAGE access.
    STORAGE_FULL_SCOPE
    ]

TASKQUEUE = 'https://www.googleapis.com/auth/taskqueue'
BIGQUERY = 'https://www.googleapis.com/auth/bigquery'
CLOUDSQL = 'https://www.googleapis.com/auth/sqlservice'

SCOPE_ALIASES = {
    'bigquery': BIGQUERY,
    'cloudsql': CLOUDSQL,
    'compute-ro': COMPUTE_RO_SCOPE,
    'compute-rw': COMPUTE_RW_SCOPE,
    'datastore': DATASTORE,
    'storage-full': STORAGE_FULL_SCOPE,
    'storage-ro': STORAGE_R_SCOPE,
    'storage-rw': STORAGE_RW_SCOPE,
    'storage-wo': STORAGE_W_SCOPE,
    'taskqueue': TASKQUEUE,
    'userinfo-email': USER_INFO_SCOPE,
    'cloud-platform': CLOUD_PLATFORM_SCOPE,
    }


def ExpandScopeAliases(scopes):
  """Expand a list of scope aliases if available.

  Args:
    scopes: a list of scopes and scope aliases

  Returns:
    a list of scopes
  """
  return [SCOPE_ALIASES.get(s, s) for s in scopes]
