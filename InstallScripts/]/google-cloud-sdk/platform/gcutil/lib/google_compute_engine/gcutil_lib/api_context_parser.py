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

"""Context management class for gcutil."""



import re


import gflags as flags

from gcutil_lib import gcutil_logging
from gcutil_lib import version

FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER

CURRENT_VERSION = version.DEFAULT_API_VERSION
SUPPORTED_VERSIONS = version.SUPPORTED_API_VERSIONS


class ApiContextParser(object):
  """Class to parse context from fully-qualified paths.

  A context is simply the set of parameters necessary to specify a cloud object
  in a fully-qualified path. For instance, a disk has a fully-qualified path:
    '{project}/zones/{zone}/disks/{disk}'

  The context is then:
    {
        'project': ...,
        'zone': ...,
        'disk': ...
    }

  Since each of these are required to fully specify which disk the user wishes
  to talk about
  """

  def __init__(self, service_version='', api_host=''):
    self._service_version = service_version
    self._api_host = api_host
    self.context_prompt_fxns = {}
    self._context_priority = ['project', 'region', 'zone']
    if service_version:
      self._api_context = self._GetApiContext()

  def _GetApiContext(self):
    """Get the API context for the specified service version.

    Returns:
      A dict containing each type of object and the requisite context.
    """

    api_context_by_service_version = {
        'v1': {
            'addresses': '{project}/regions/{region}/addresses/{address}',
            'disks': '{project}/zones/{zone}/disks/{disk}',
            'diskTypes': '{project}/zones/{zone}/diskTypes/{diskType}',
            'firewalls': '{project}/global/firewalls/{firewall}',
            'forwardingRules': (
                '{project}/regions/{region}/forwardingRules/{forwardingRule}'),
            'gateways': '{project}/global/gateways/default-internet-gateway',
            'globalOperations': '{project}/global/operations/{operation}',
            'httpHealthChecks': (
                '{project}/global/httpHealthChecks/{httpHealthCheck}'),
            'images': '{project}/global/images/{image}',
            'instances': '{project}/zones/{zone}/instances/{instance}',
            'licenses': '{project}/global/licenses/{license}',
            'machineTypes': '{project}/zones/{zone}/machineTypes/{machineType}',
            'networks': '{project}/global/networks/{network}',
            'projects': '{project}',
            'regionOperations': (
                '{project}/regions/{region}/operations/{operation}'),
            'regions': '{project}/regions/{region}',
            'routes': '{project}/global/routes/{route}',
            'snapshots': '{project}/global/snapshots/{snapshot}',
            'targetInstances': (
                '{project}/zones/{zone}/targetInstances/{targetInstance}'),
            'targetPools': (
                '{project}/regions/{region}/targetPools/{targetPool}'),
            'zoneOperations': '{project}/zones/{zone}/operations/{operation}',
            'zones': '{project}/zones/{zone}'
        },
        'v2beta1': {
            'addresses': '{project}/regions/{region}/addresses/{address}',
            'disks': '{project}/zones/{zone}/disks/{disk}',
            'diskTypes': '{project}/zones/{zone}/diskTypes/{diskType}',
            'firewalls': '{project}/global/firewalls/{firewall}',
            'forwardingRules': (
                '{project}/regions/{region}/forwardingRules/{forwardingRule}'),
            'gateways': '{project}/global/gateways/default-internet-gateway',
            'globalOperations': '{project}/global/operations/{operation}',
            'httpHealthChecks': (
                '{project}/global/httpHealthChecks/{httpHealthCheck}'),
            'images': '{project}/global/images/{image}',
            'instances': '{project}/zones/{zone}/instances/{instance}',
            'licenses': '{project}/global/licenses/{license}',
            'machineTypes': '{project}/zones/{zone}/machineTypes/{machineType}',
            'networks': '{project}/global/networks/{network}',
            'projects': '{project}',
            'regionOperations': (
                '{project}/regions/{region}/operations/{operation}'),
            'regions': '{project}/regions/{region}',
            'routes': '{project}/global/routes/{route}',
            'snapshots': '{project}/global/snapshots/{snapshot}',
            'targetInstances': (
                '{project}/zones/{zone}/targetInstances/{targetInstance}'),
            'targetPools': (
                '{project}/regions/{region}/targetPools/{targetPool}'),
            'zoneOperations': '{project}/zones/{zone}/operations/{operation}',
            'zones': '{project}/zones/{zone}'
        },
    }


    return api_context_by_service_version[self._service_version]

  def _GetRequiredContext(self, object_type):
    """Parse the required context for this object type.

    Args:
      object_type: The type of object. Must be a valid compute object type.

    Returns:
      A dict with all necessary context for this kind of object.
    """
    context = {}
    for item in re.findall(r'\{[a-zA-Z0-9]+\}',
                           self._api_context[object_type]):
      context[item[1:-1]] = None

    return context

  def _IsContext(self, path_part):
    return re.match(r'\{[a-zA-Z0-9]+\}', path_part)

  def _GetContextFromPath(self, object_type, path):
    """Get all of the context out of the path proper.

    Args:
      object_type: The type of object. Must be a valid compute object type.
      path: The path to parse.
    Returns:
      A dict with the parsed context. If a context could not be parsed,
      then None acts as a placeholder.

    Raises:
      ValueError: The path was invalid for this object type.
    """
    # Get all required context.
    context = self._GetRequiredContext(object_type)

    user_path_components = path.split('/')
    full_path_components = (
        self._GetFullPathTo(self._api_context[object_type]).split('/'))

    if len(user_path_components) > len(full_path_components):
      raise ValueError('Invalid path: {0}'.format(path))

    # Get all context from the path.
    for user, full in zip(reversed(user_path_components),
                          reversed(full_path_components)):
      if full and not user:
        raise ValueError('Invalid path: {0}'.format(path))

      if self._IsContext(full):
        # This should be mapped to a context.
        context[full[1:-1]] = user
      else:
        # User path should match this exactly.
        if user != full:
          raise ValueError('Invalid path: {0}'.format(path))

    return context

  def IdentifyObjectTypeFromPath(self, path):
    """If possible, identify the object type from the path.

    Args:
      path: Fully- or partially-qualified path to the object.

    Returns:
      The corresponding object_type if it is uniquely identifiable
      from the path. Otherwise, None.
    """
    possible_types = []

    for object_type in self._api_context:
      try:
        self._GetContextFromPath(object_type, path)
        possible_types.append(object_type)
      except ValueError:
        pass

    if len(possible_types) == 1:
      return possible_types[0]
    return None

  def _PromptForContextOrFail(self, context, object_type, path):
    """Get the default or user prompted context for missing parts, or fail.

    Args:
      context: The known context.
      object_type: The type of object to prompt for context for.
      path: The path that generated them.

    Returns:
      The parsed context.

    Raises:
      ValueError: No means of getting the context for this kind of object was
        available, and it was not specified in the path.
    """
    def _GetContextForItem(item, context, object_type):
      if item in self.context_prompt_fxns:
        context[item] = self.context_prompt_fxns[item](object_type,
                                                       context)
      else:
        raise ValueError(
            'Cannot get missing context {0} from path {1}'.format(context,
                                                                  path))

    for item in self._context_priority:
      if item in context and context[item] is None:
        _GetContextForItem(item, context, object_type)

    for item in context:
      if context[item] is None:
        _GetContextForItem(item, context, object_type)

    return context

  def ParseContextOrPrompt(self, object_type, path):
    """Either get the context for the object from the path, or fail.

    ParseContextOrPrompt will parse a (relative or fully-qualified) path
    to a compute object and return a dict with the context and object name,
    either as specified by the user in a prompt, from the flags, or in the
    path.

    For instance, suppose the user wants the context for a disk object.
    If the user specifies a path:
      'my-project/zones/some-zone/disks/my-disk',
    then the context returned will be a dict with:
      {
          project: 'my-project',
          zone: 'some-zone',
          disk: 'my-disk'
      }

    On the other hand, if the zone was not specified and the user used a less
    specific path:
      'disks/my-disk'
    depending on the callback specified in context_prompt_fxns, the user may
    be requested to specifiy the zone or it may be automatically detected,
    or perhaps it will be taken from flags.

    Args:
      object_type:  The type of object. Must be a valid compute object type.
      path:  A relative or absolute path to the object.

    Returns:
      A dict with all necessary context path parsed out, or alternatively the
      context from flags.
    """

    # Get all context from the path.
    context = self._GetContextFromPath(object_type, path)

    # For each context that could not be taken from the path, prompt for it
    # or get it from flags.
    context = self._PromptForContextOrFail(context, object_type, path)

    return context

  def NormalizeOrPrompt(self, object_type, path):
    """Either get the normalized for the object from the path, or fail.

    NormalizeOrPrompt will parse a (relative or fully-qualified) path
    to a compute object and return a dict with the context and object name,
    either as specified by the user in a prompt, from the flags, or in the
    path.

    Args:
      object_type: The type of object. Must be a valid compute object type.
      path: A relative or absolute path to the object.

    Returns:
      A string which equals the normalized path.
    """
    if path is None:
      return

    context = self.ParseContextOrPrompt(object_type, path)

    return self.NormalizeWithContext(object_type, context)

  def _GetFullPathTo(self, relative_path):
    """Retrieve the full path given a relative path.

    Args:
      relative_path: The relative path.

    Returns:
      The full path.
    """
    return '%s/compute/%s/projects/%s' % (self._api_host.rstrip('/'),
                                          self._service_version,
                                          relative_path)

  def NormalizeWithContext(self, object_type, context):
    """Given some context, produce a normalized path.

    Args:
      object_type: The type of object. Must be a valid compute object type.
      context: A dictionary of context to use.

    Returns:
      A string which equals the normalized path.
    """

    relative_path = self._api_context[object_type].format(**context)

    full_path = self._GetFullPathTo(relative_path)

    return full_path
