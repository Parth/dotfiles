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

import re

__version__ = '1.16.5'

# Supported_api_versions must be maintained in chronological order
SUPPORTED_API_VERSIONS = ['v1']

DEFAULT_API_VERSION = 'v1'


# pylint: disable=protected-access
class _ApiVersion(object):
  __slots__ = ('_name', '_index', '_versions')

  def __init__(self, name, index, versions):
    self._name = name
    self._index = index
    self._versions = versions

  def __str__(self):
    return '<compute api %s>' % self._name

  def __eq__(self, other):
    other = self._versions.get(other)
    return (self is other or
            self._versions is other._versions and self._index == other._index)

  def __ne__(self, other):
    return not self.__eq__(other)

  def __lt__(self, other):
    other = self._versions.get(other)
    return (self is not other and
            self._versions is other._versions and self._index < other._index)

  def __gt__(self, other):
    other = self._versions.get(other)
    return (self is not other and
            self._versions is other._versions and self._index > other._index)

  def __le__(self, other):
    other = self._versions.get(other)
    return (self is other or
            self._versions is other._versions and self._index <= other._index)

  def __ge__(self, other):
    other = self._versions.get(other)
    return (self is other or
            self._versions is other._versions and self._index >= other._index)


class _ApiVersions(object):
  __slots__ = ('_versions')

  VERSION_RE = '^(?:[a-z]+_)?(?P<version>v[1-9][0-9]*(?:[a-z]+[1-9][0-9]*)?)$'

  def __init__(self, versions):
    api_versions = {}
    for version in versions:
      base_version = _ApiVersions._ExtractBaseVersion(version)
      if base_version not in api_versions:
        api_versions[base_version] = _ApiVersion(
            base_version, len(api_versions), self)
    self._versions = api_versions

  @staticmethod
  def _ExtractBaseVersion(version):
    match = re.match(_ApiVersions.VERSION_RE, version)
    if not match:
      raise ValueError('API version %s doesn\'t match regular expression %s' % (
          version, _ApiVersions.VERSION_RE))
    return match.group('version')

  def __getitem__(self, version):
    return self.get(version)

  def get(self, version):
    """Returns an object representing requested api version."""

    if isinstance(version, _ApiVersion):
      if version._versions is not self:
        raise TypeError('version %s doesn\'t belong to this group of versions')
      return version

    if not isinstance(version, basestring):
      raise TypeError('version argument value must be a string: %s (%s)' %
                      (version, type(version)))

    base_version = _ApiVersions._ExtractBaseVersion(version)
    api_version = self._versions.get(base_version)
    if api_version is None:
      raise ValueError('Unrecognized API version %s' % version)

    return api_version

  def iteritems(self):
    return self._versions.iteritems()


def _Export(versions):
  version_module_globals = globals()
  for name, version in versions.iteritems():
    if name not in version_module_globals:
      version_module_globals[name] = version
  return versions


_API_VERSIONS = _Export(_ApiVersions(SUPPORTED_API_VERSIONS))


def get(version):
  return _API_VERSIONS.get(version)
