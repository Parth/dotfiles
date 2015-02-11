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

"""Commands for interacting with Google Compute Engine target instances."""



from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_flags
from gcutil_lib import version


FLAGS = flags.FLAGS


class TargetInstanceCommand(command_base.GoogleComputeCommand):
  """Base command for working with the target instance collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'instance'],
      field_mappings=(
          ('name', 'name'),
          ('description', 'description'),
          ('zone', 'zone'),
          ('nat-policy', 'natPolicy'),
          ('instance', 'instance')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('nat-policy', 'natPolicy'),
          ('instance', 'instance'),
          ),
      sort_by='name')

  resource_collection_name = 'targetInstances'

  DEFAULT_NAT_POLICY = 'NO_NAT'

  def __init__(self, name, flag_values):
    super(TargetInstanceCommand, self).__init__(name, flag_values)
    flags.DEFINE_string('zone',
                        None,
                        '[Required] The zone for this request.',
                        flag_values=flag_values)

  def _PrepareRequestArgs(self, target_instance_context):
    """Gets the dictionary of API method keyword arguments.

    Args:
      target_instance_context: A context dict for this target instance.

    Returns:
      Dictionary of keyword arguments that should be passed in the API call.
    """

    kwargs = {
        'project': target_instance_context['project'],
        'targetInstance': target_instance_context['targetInstance'],
        'zone': target_instance_context['zone']
    }

    return kwargs

  def _AutoDetectZone(self):
    """Instruct this command to auto detect zone instead of prompting."""
    def _GetZoneContext(object_type, context):
      if self._flags.zone:
        return self.DenormalizeResourceName(self._flags.zone)

      if object_type == 'targetInstances':
        return self.GetZoneForResource(self.api.target_instances,
                                       context['targetInstance'])

    self._context_parser.context_prompt_fxns['zone'] = _GetZoneContext

  def _GetZoneOrPrompt(self):
    """Instruct this command to get the zone from flag or by prompting."""
    if self._flags.zone is None:
      self._flags.zone = self._presenter.PromptForZone(self.api.zones)['name']
    return self.DenormalizeResourceName(self._flags.zone)


class AddTargetInstance(TargetInstanceCommand):
  """Create a new target instance to handle network load balancing."""

  positional_args = '<target-instance-name>'

  def __init__(self, name, flag_values):
    super(AddTargetInstance, self).__init__(name, flag_values)
    flags.DEFINE_string('description',
                        '',
                        'An optional Target Instance description',
                        flag_values=flag_values)
    flags.DEFINE_string('instance',
                        None,
                        'The name of the instance resource to serve this '
                        'target. The instance does not have to be created '
                        'already, but must be in the same zone as this '
                        'TargetInstance resource.',
                        flag_values=flag_values)
    gcutil_flags.DEFINE_case_insensitive_enum(
        'nat_policy',
        self.DEFAULT_NAT_POLICY,
        ['NO_NAT'],
        'NAT policy options controlling how the IP should be '
        'NAT\'ed to the VM.',
        flag_values=flag_values)

  def Handle(self, target_instance_name):
    """Add the specified target instance.

    Args:
      target_instance_name: The name of the target instance to add.

    Returns:
      The result of inserting the target instance.
    """
    if self.api.version < version.get('v1'):
      raise gcutil_errors.UnsupportedCommand(
          'This command is not supported in service version %s.' %
          self.api.version)

    self._GetZoneOrPrompt()
    target_instance_context = self._context_parser.ParseContextOrPrompt(
        'targetInstances', target_instance_name)

    target_instance_resource = {
        'kind': self._GetResourceApiKind('targetInstance'),
        'name': target_instance_context['targetInstance'],
        'description': self._flags.description,
        'natPolicy': self._flags.nat_policy,
        'instance': self._context_parser.NormalizeOrPrompt(
            'instances', self._flags.instance)
        }

    kwargs = {'zone': target_instance_context['zone']}

    target_instance_request = (self.api.target_instances.insert(
        project=target_instance_context['project'],
        body=target_instance_resource, **kwargs))
    return target_instance_request.execute()


class GetTargetInstance(TargetInstanceCommand):
  """Get a target instance."""

  positional_args = '<target-instance-name>'

  def __init__(self, name, flag_values):
    super(GetTargetInstance, self).__init__(name, flag_values)

  def Handle(self, target_instance_name):
    """Get the specified target instance.

    Args:
      target_instance_name: The name of the target instance to get.

    Returns:
      The result of getting the target instance.
    """
    if self.api.version < version.get('v1'):
      raise gcutil_errors.UnsupportedCommand(
          'This command is not supported in service version %s.' %
          self.api.version)

    self._AutoDetectZone()

    target_instance_context = self._context_parser.ParseContextOrPrompt(
        'targetInstances', target_instance_name)

    target_instance_request = self.api.target_instances.get(
        **self._PrepareRequestArgs(target_instance_context))

    return target_instance_request.execute()


class DeleteTargetInstance(TargetInstanceCommand):
  """Delete one or more target instances.

  If multiple target instance names are specified, the target instance
  will be deleted in parallel.
  """

  positional_args = '<target-instance-name-1> ... <target-instance-name-n>'
  safety_prompt = 'Delete target instance'

  def __init__(self, name, flag_values):
    super(DeleteTargetInstance, self).__init__(name, flag_values)

  def Handle(self, *target_instance_names):
    """Delete the specified target instances.

    Args:
      *target_instance_names: The names of the target instances to delete.

    Returns:
      Tuple (results, exceptions) - results of deleting the target instances.
    """
    if self.api.version < version.get('v1'):
      raise gcutil_errors.UnsupportedCommand(
          'This command is not supported in service version %s.' %
          self.api.version)

    self._AutoDetectZone()

    requests = []
    for name in target_instance_names:
      target_instance_context = self._context_parser.ParseContextOrPrompt(
          'targetInstances', name)
      requests.append(self.api.target_instances.delete(
          **self._PrepareRequestArgs(target_instance_context)))
    results, exceptions = self.ExecuteRequests(requests)
    return (self.MakeListResult(results, 'operationList'), exceptions)


class ListTargetInstances(TargetInstanceCommand,
                          command_base.GoogleComputeListCommand):
  """List the target instances for a project."""

  def IsZoneLevelCollection(self):
    return True

  def IsRegionLevelCollection(self):
    return False

  def IsGlobalLevelCollection(self):
    return False

  def __init__(self, name, flag_values):
    super(ListTargetInstances, self).__init__(name, flag_values)

  def ListFunc(self):
    """Returns the function for listing target instances."""
    return None

  def ListZoneFunc(self):
    """Returns the function for listing target instances in a zone."""
    if self.api.version < version.get('v1'):
      raise gcutil_errors.UnsupportedCommand(
          'This command is not supported in service version %s.' %
          self.api.version)
    else:
      return self.api.target_instances.list

  def ListAggregatedFunc(self):
    """Returns the function for listing target instances across all zones."""
    if self.api.version < version.get('v1'):
      raise gcutil_errors.UnsupportedCommand(
          'This command is not supported in service version %s.' %
          self.api.version)
    else:
      return self.api.target_instances.aggregatedList


def AddCommands():
  """Add all of the target instance related commands."""

  appcommands.AddCmd('addtargetinstance', AddTargetInstance)
  appcommands.AddCmd('gettargetinstance', GetTargetInstance)
  appcommands.AddCmd('deletetargetinstance', DeleteTargetInstance)
  appcommands.AddCmd('listtargetinstances', ListTargetInstances)
