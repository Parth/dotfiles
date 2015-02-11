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

"""Commands for interacting with Google Compute Engine availability zones."""



import iso8601

from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base


FLAGS = flags.FLAGS


class ZoneCommand(command_base.GoogleComputeCommand):
  """Base command for working with the zones collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'status', 'next-maintenance'],
      field_mappings=(
          ('name', 'name'),
          ('description', 'description'),
          ('status', 'status'),
          ('deprecation', 'deprecated.state'),
          ('next-maintenance', 'next_maintenance_window'),
          ('instances', 'instances'),
          ('cpus', 'cpus'),
          ('disks', 'disks'),
          ('disks-total-gb', 'disks_total_gb')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('status', 'status'),
          ('deprecation', 'deprecated.state'),
          ('replacement', 'deprecated.replacement')),
      sort_by='name')


class GetZone(ZoneCommand):
  """Get a zone."""

  positional_args = '<zone-name>'

  def GetDetailRow(self, result):
    """Returns an associative list of items for display in a detail table.

    Args:
      result: A dict returned by the server.

    Returns:
      A list.
    """
    data = []
    # Add machine types
    for (i, m) in enumerate(result.get('availableMachineType', [])):
      key = ''
      if i == 0:
        key = 'machine types'
      data.append((key, self._presenter.PresentElement(m)))

    # Add the maintenance windows
    for window in result.get('maintenanceWindows', []):
      maintenance_info = []
      maintenance_info.append(('name', window['name']))
      maintenance_info.append(('description', window['description']))
      maintenance_info.append(('begin-time', window['beginTime']))
      maintenance_info.append(('end-time', window['endTime']))
      data.append(('maintenance-window', maintenance_info))

    return data

  def Handle(self, zone_name):
    """Get the specified zone.

    Args:
      zone_name: Path of the zone to get.

    Returns:
      The result of getting the zone.
    """
    zone_context = self._context_parser.ParseContextOrPrompt('zones',
                                                             zone_name)

    request = self.api.zones.get(project=zone_context['project'],
                                 zone=zone_context['zone'])
    return request.execute()


class ListZones(ZoneCommand, command_base.GoogleComputeListCommand):
  """List the zones for a project."""

  def ListFunc(self):
    return self.api.zones.list

  def Handle(self):
    """List the project's zones."""
    result = super(ListZones, self).Handle()
    items = result.get('items', [])

    # Add the next maintenance window start time to each entry.
    for zone in items:
      next_iso = None
      next_str = 'None scheduled'

      for window in zone.get('maintenanceWindows', []):
        begin_str = window['beginTime']
        begin_iso = iso8601.parse_date(begin_str)
        if next_iso is None or begin_iso < next_iso:
          next_iso = begin_iso
          next_str = begin_str

      zone['next_maintenance_window'] = next_str

      for quota in zone.get('quotas', []):
        column_name = quota['metric'].lower()
        zone[column_name] = (
            '%s/%s' % (str(quota['usage']), str(quota['limit'])))

    return result


def AddCommands():
  appcommands.AddCmd('getzone', GetZone)
  appcommands.AddCmd('listzones', ListZones)
