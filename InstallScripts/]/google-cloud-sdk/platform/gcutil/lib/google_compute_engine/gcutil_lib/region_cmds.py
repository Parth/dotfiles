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

"""Commands for interacting with Google Compute Engine availability regions."""



from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base


FLAGS = flags.FLAGS


class RegionCommand(command_base.GoogleComputeCommand):
  """Base command for working with the regions collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'status', 'cpus', 'disks-total-gb', 'static-addresses'],
      field_mappings=(
          ('name', 'name'),
          ('description', 'description'),
          ('status', 'status'),
          ('deprecation', 'deprecated.state'),
          ('cpus', 'cpus'),
          ('disks-total-gb', 'disks_total_gb'),
          ('in-use-addresses', 'in_use_addresses'),
          ('static-addresses', 'static_addresses')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('status', 'status'),
          ('zones', 'zones'),
          ('deprecation', 'deprecated.state'),
          ('replacement', 'deprecated.replacement')),
      sort_by='name')


class GetRegion(RegionCommand):
  """Get a region."""

  positional_args = '<region-name>'

  def GetDetailRow(self, result):
    """Returns an associative list of items for display in a detail table.

    Args:
      result: A dict returned by the server.

    Returns:
      A list.
    """
    # Add the region quotas
    usage_info = []
    for quota in result.get('quotas', []):
      usage_info.append((quota['metric'].lower().replace('_', '-'),
                         '%s/%s' % (str(quota['usage']), str(quota['limit']))))
    if usage_info:
      return [('usage', usage_info)]
    else:
      return []

  def Handle(self, region_name):
    """Get the specified region.

    Args:
      region_name: Path of the region to get.

    Returns:
      The result of getting the region.
    """
    region_context = self._context_parser.ParseContextOrPrompt('regions',
                                                               region_name)

    request = self.api.regions.get(project=region_context['project'],
                                   region=region_context['region'])
    return request.execute()


class ListRegions(RegionCommand, command_base.GoogleComputeListCommand):
  """List the regions for a project."""

  def ListFunc(self):
    return self.api.regions.list

  def Handle(self):
    """List the project's regions."""
    result = super(ListRegions, self).Handle()
    items = result.get('items', [])

    for region in items:
      for quota in region.get('quotas', []):
        column_name = quota['metric'].lower()
        region[column_name] = (
            '%s/%s' % (str(quota['usage']), str(quota['limit'])))

    return result


def AddCommands():
  appcommands.AddCmd('getregion', GetRegion)
  appcommands.AddCmd('listregions', ListRegions)
