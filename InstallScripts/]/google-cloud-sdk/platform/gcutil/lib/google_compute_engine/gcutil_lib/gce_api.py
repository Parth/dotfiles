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

"""Representation and analysis of Google Compute Engine API."""

import inspect
import json
import os


from apiclient import discovery
from apiclient import errors
from apiclient import model

import gflags as flags
from gcutil_lib import gcutil_errors
from gcutil_lib import version

FLAGS = flags.FLAGS



class ComputeApi(object):
  """Wraps Google Compute Engine API."""

  __slots__ = ('version', 'methods',
               # All collections
               'addresses',
               'disks',
               'disk_types',
               'firewalls',
               'forwarding_rules',
               'global_operations',
               'http_health_checks',
               'images',
               'instances',
               'machine_types',
               'networks',
               'projects',
               'region_operations',
               'regions',
               'routes',
               'snapshots',
               'target_pools',
               'target_instances',
               'zone_operations',
               'zones')

  def __init__(self, api, api_version, methods):
    self.version = api_version
    self.methods = methods

    def GetCollectionOrNone(api, name):
      return getattr(api, name)() if hasattr(api, name) else None

    self.addresses = GetCollectionOrNone(api, 'addresses')
    self.disks = api.disks()
    self.disk_types = GetCollectionOrNone(api, 'diskTypes')
    self.firewalls = api.firewalls()
    self.forwarding_rules = GetCollectionOrNone(api, 'forwardingRules')
    self.global_operations = api.globalOperations()
    self.http_health_checks = GetCollectionOrNone(api, 'httpHealthChecks')
    self.images = api.images()
    self.instances = api.instances()
    self.machine_types = api.machineTypes()
    self.networks = api.networks()
    self.projects = api.projects()
    self.region_operations = GetCollectionOrNone(api, 'regionOperations')
    self.regions = GetCollectionOrNone(api, 'regions')
    self.routes = api.routes()
    self.snapshots = api.snapshots()
    self.target_pools = GetCollectionOrNone(api, 'targetPools')
    self.target_instances = GetCollectionOrNone(api, 'targetInstances')
    self.zone_operations = api.zoneOperations()
    self.zones = api.zones()

  def __contains__(self, item):
    return item in self.methods


def _ParseMethods(methods, discovery_methods):
  for _, discovery_method in discovery_methods.iteritems():
    method_id = discovery_method.get('id')
    if method_id:
      methods.add(method_id)


def _ParseResource(methods, discovery_resource):
  discovery_methods = discovery_resource.get('methods')
  if discovery_methods:
    _ParseMethods(methods, discovery_methods)
  discovery_resources = discovery_resource.get('resources')
  if discovery_resources:
    _ParseResources(methods, discovery_resources)


def _ParseResources(methods, discovery_resources):
  for _, discovery_resource in discovery_resources.iteritems():
    _ParseResource(methods, discovery_resource)


def GetSetOfApiMethods(discovery_document):
  methods = set()
  _ParseResources(methods, discovery_document.get('resources'))
  return frozenset(methods)


def CreateComputeApi(
    http,
    api_version,
    download=False,
    server=None):
  """Builds the Google Compute Engine API to use.

  Args:
    http: a httplib2.Http like object for communication.
    api_version: the version of the API to create.
    download: bool. Download the discovery document from the discovery service.
    server: URL of the API service host.

  Returns:
    The ComputeApi object to use.

  Raises:
    gcutil_errors.CommandError: If loading the discovery doc fails.
  """
  # Use default server if none provided.
  default_server = 'https://www.googleapis.com/'
  server = server or default_server

  # Load the discovery document.
  discovery_document = None

  # Try to download the discovery document
  if download or server != default_server:
    url = '{server}/discovery/v1/apis/compute/{version}/rest'.format(
        server=server.rstrip('/'),
        version=api_version)
    response, content = http.request(url)

    if response.status == 200:
      discovery_document = content
    else:
      raise gcutil_errors.CommandError(
          'Could not load discovery document from %s:\n%s' % (
              url, content))
  else:
    # Try to load locally
    discovery_path = os.path.join(
        os.path.dirname(__file__), 'compute', '%s.json' % api_version)
    try:
      with open(discovery_path) as discovery_file:
        discovery_document = discovery_file.read()
    except IOError as err:
      raise gcutil_errors.CommandError(
          'Could not load discovery document from %s:\n%s' % (
              discovery_path, err))

  try:
    discovery_document = json.loads(discovery_document)
  except ValueError:
    raise errors.InvalidJsonError()

  api = discovery.build_from_document(
      discovery_document,
      http=http,
      model=model.JsonModel())
  api = WrapApiIfNeeded(api)

  return ComputeApi(
      api,
      version.get(discovery_document.get('version')),
      GetSetOfApiMethods(discovery_document))


# A wrapper around an Api that adds a trace keyword to the Api.
class TracedApi(object):
  """Wrap an Api to add a trace keyword argument."""

  def __init__(self, obj, trace_token):
    def Wrap(func):
      def _Wrapped(*args, **kwargs):
        # Add a trace= URL parameter to the method call.
        if trace_token:
          kwargs['trace'] = trace_token
        return func(*args, **kwargs)
      return _Wrapped

    # Find all public methods and interpose them.
    for method in inspect.getmembers(obj, (inspect.ismethod)):
      if not method[0].startswith('__'):
        setattr(self, method[0], Wrap(method[1]))


class TracedComputeApi(object):
  """Wrap a ComputeApi object to return TracedApis."""

  def __init__(self, obj, trace_token):
    def Wrap(func):
      def _Wrapped(*args, **kwargs):
        ret = func(*args, **kwargs)
        if ret:
          ret = TracedApi(ret, trace_token)
        return ret
      return _Wrapped

    # Find all our public methods and interpose them.
    for method in inspect.getmembers(obj, (inspect.ismethod)):
      if not method[0].startswith('__'):
        setattr(self, method[0], Wrap(method[1]))


def WrapApiIfNeeded(api):
  """Wraps the API to enable logging or tracing."""
  if FLAGS.trace_token:
    return TracedComputeApi(api, 'token:%s' % (FLAGS.trace_token))
  return api
