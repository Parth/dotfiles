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

"""Helper module for fetching metadata variables."""



import json
import urllib2


class MetadataError(Exception):
  """Base class for metadata errors."""
  pass


class NoMetadataServerError(MetadataError):
  """Metadata server is not responding."""
  pass


class MetadataNotFoundError(MetadataError):
  """Metadata not present."""
  pass


class Metadata(object):
  """Client API for the metadata server."""

  METADATA_BASE = 'http://metadata.google.internal'

  def __init__(self, server_address=METADATA_BASE,
               urllib2_module=urllib2):
    """Construct a Metadata client.

    Args:
      server_address: The address of the metadata server.
      urllib2_module: An injectable module for urllib2.
    """
    self._server_address = server_address
    self._urllib2 = urllib2_module

  def IsPresent(self):
    """Return whether the metadata server is ready and available."""
    try:
      self.GetProjectId(timeout=1)
      return True
    except MetadataError:
      return False

  def GetValue(self, path, timeout=None):
    """Return a string value from the metadata server.

    Args:
      path: The path of the variable.
      timeout: Optional timeout on the request.

    Returns:
      The metadata value.

    Raises:
      MetadataError on failure.
      MetadataNotFoundError if the metadata path is not present.
      NoMetadataServerError if the metadata server does not seem to be present.
    """
    url = '%s/%s' % (self._server_address, path)
    req = self._urllib2.Request(url)
    try:
      return self._DoHttpRequestRead(req, timeout=timeout)
    except self._urllib2.HTTPError as e:
      if e.code == 404:
        raise MetadataNotFoundError('Metadata not found: %s' % (path))
      raise MetadataError(
          'Failed to get value %s: %s %s' % (path, e.code, e.reason))
    except self._urllib2.URLError as e:
      try:
        if e.reason.errno == 111:
          raise NoMetadataServerError('Metadata server not responding')
        if e.reason.errno == -2:
          raise NoMetadataServerError('Metadata server not resolving')
      except AttributeError:
        pass

      raise MetadataError('URLError %s: %s' % (url, e))

  def GetJsonValue(self, path, timeout=None):
    """Return a decoded JSON value from the metadata server.

    Args:
      path: The path of the variable.
      timeout: An optional timeout on the request.

    Returns:
      A json-decoded object.

    Raises:
      MetadataError on failure.
      MetadataNotFoundError if the metadata path is not present.
      NoMetadataServerError if the metadata server does not seem to be present.
    """
    try:
      return json.loads(self.GetValue(path + '?alt=json', timeout=timeout))
    except ValueError as e:
      raise MetadataError('Failed to parse JSON: %s', e)

  def GetServiceAccountScopes(self, service_account='default'):
    """Return the service account scopes for the given service account.

    Args:
      service_account: The service account to use.

    Returns:
      A list of oauth2 scopes.

    Raises:
      MetadataError on failure.
    """
    return self.GetJsonValue(
        'computeMetadata/v1beta1/instance/service-accounts/%s/scopes' % (
            service_account))

  def GetProjectId(self, timeout=None):
    """Return the unique name of the project for this VM.

    Args:
      timeout: An optional timeout on the request.

    Returns:
      The unique name of the project for this VM.

    Raises:
      MetadataError on failure.
    """
    return self.GetValue('computeMetadata/v1beta1/project/project-id')

  def _DoHttpRequestRead(self, request, timeout):
    """Open and return contents of an http request."""
    if timeout is None:
      return self._urllib2.urlopen(request).read()
    else:
      return self._urllib2.urlopen(request, timeout=timeout).read()
