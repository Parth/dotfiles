# Copyright 2014 Google Inc. All Rights Reserved.
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

"""Commands for interacting with Google Compute Engine disk types."""




from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base


FLAGS = flags.FLAGS



class DiskTypeCommand(command_base.GoogleComputeCommand):
  """Base command for working with the disk types collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'zone'],
      field_mappings=(
          ('name', 'name'),
          ('description', 'description'),
          ('valid-disk-size', 'validDiskSize'),
          ('zone', 'zone'),
          ('deprecation', 'deprecated.state')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('valid-disk-size', 'validDiskSize'),
          ('zone', 'zone'),
          ('creation-time', 'creationTimestamp'),
          ('deprecation', 'deprecated.state'),
          ('replacement', 'deprecated.replacement')),
      sort_by='name')

  resource_collection_name = 'diskTypes'

  def __init__(self, name, flag_values):
    super(DiskTypeCommand, self).__init__(name, flag_values)
    flags.DEFINE_string('zone',
                        None,
                        'The zone for this request.',
                        flag_values=flag_values)

  def _PrepareRequestArgs(self, disk_type_context, **other_args):
    """Gets the dictionary of API method keyword arguments.

    Args:
      disk_type_context: A context dict for the desired disk type.
      **other_args: Keyword arguments that should be included in the request.

    Returns:
      Dictionary of keyword arguments that should be passed in the API call,
      includes all keyword arguments passed in 'other_args' plus common keys
      such as the name of the resource and the project.
    """
    kwargs = {
        'project': disk_type_context['project'],
        'diskType': disk_type_context['diskType']
    }
    if disk_type_context['zone']:
      kwargs['zone'] = disk_type_context['zone']
    for key, value in other_args.items():
      kwargs[key] = value
    return kwargs


class GetDiskType(DiskTypeCommand):
  """Get a disk type."""

  def __init__(self, name, flag_values):
    super(GetDiskType, self).__init__(name, flag_values)

  def Handle(self, disk_type_name):
    """Get the specified disk type.

    Args:
      disk_type_name: Name of the disk type to get.

    Returns:
      The result of getting the disk type.
    """
    disk_type_context = self._context_parser.ParseContextOrPrompt(
        'diskTypes', disk_type_name)

    disk_type_request = self.api.disk_types.get(
        **self._PrepareRequestArgs(disk_type_context))

    return disk_type_request.execute()


class ListDiskTypes(DiskTypeCommand,
                    command_base.GoogleComputeListCommand):
  """List the disk types for a project in a given zone."""

  def IsZoneLevelCollection(self):
    return True

  def IsGlobalLevelCollection(self):
    return False

  def __init__(self, name, flag_values):
    super(ListDiskTypes, self).__init__(name, flag_values)

  def ListFunc(self):
    """Returns the function for listing disk types."""
    return self.api.disk_types.list

  def ListZoneFunc(self):
    """Returns the function for listing disk types in a zone."""
    return self.api.disk_types.list

  def ListAggregatedFunc(self):
    """Returns the function for listing disk types across all zones."""
    return self.api.disk_types.aggregatedList


def AddCommands():
  appcommands.AddCmd('getdisktype', GetDiskType)
  appcommands.AddCmd('listdisktypes', ListDiskTypes)
