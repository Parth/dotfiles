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


"""Support for mocking Google Compute Engine API method calls."""

import json
import os


from apiclient import discovery



from gcutil_lib import gce_api
from gcutil_lib import mock_api_parser
from gcutil_lib import mock_api_server
from gcutil_lib import version


def CreateApi(api_version):
  """Creates mock API for a given Google Compute Engine API version.

  Args:
    api_version: Version of the API demanded. For example: 'v1'.

  Returns:
    Tuple (mock, api). mock is an instance of MockServer which can be used to
    program responses for specific requests, api is an instance of Google
    Compute Engine API (google-api-python-client).
  """
  discovery_path = os.path.join(
      os.path.dirname(__file__),
      'compute',
      '{version}.json'.format(version=api_version))

  with open(discovery_path) as discovery_file:
    discovery_document = discovery_file.read()

  discovery_json = json.loads(discovery_document)

  parser = mock_api_parser.Parser(discovery_json)
  methods = parser.Parse()

  mock = mock_api_server.MockServer(methods)
  api = discovery.build_from_document(
      discovery_document, requestBuilder=mock.BuildRequest)
  return mock, gce_api.ComputeApi(api,
                                  version.get(discovery_json.get('version')),
                                  gce_api.GetSetOfApiMethods(discovery_json))


class MockCredential(object):
  """A mock credential that does nothing."""

  def authorize(self, http):
    return http
