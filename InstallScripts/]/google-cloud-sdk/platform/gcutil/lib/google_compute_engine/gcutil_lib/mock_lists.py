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

"""List result generators for gcutil unit tests."""


import datetime

from gcutil_lib import command_base
from gcutil_lib import gcutil_unittest


def GetSampleDiskListCall(command, mock_server, num_responses=2):
  """Registers a sample disk list call on the mock server.

  Args:
    command: The gcutil command that this call is based on.
    mock_server:  The mock server to register the list call on.
    num_responses:  The size of the desired call.

  Returns:
    The created server call object.
  """
  def ListResponse(unused_uri, unused_http_method, parameters, unused_body):
    return mock_server.MOCK_RESPONSE(
        {
            'kind': 'compute#diskList',
            'items': [{
                'kind': 'compute#disk',
                'name': 'test_disk_%d' % x,
                'project': parameters['project'],
                'zone': command.NormalizeGlobalResourceName(
                    parameters['project'],
                    'zones',
                    parameters['zone'])
                } for x in xrange(num_responses)]
        },
        True)

  return mock_server.RespondF('compute.disks.list', ListResponse)


def GetSampleImageListCall(command, mock_server, num_responses=2, name=None):
  """Registers a sample image list call on the mock server.

  Args:
    command: The gcutil command that this call is based on.
    mock_server:  The mock server to register the list call on.
    num_responses:  The size of the desired call.
    name:  Optional list of names for the instances.

  Returns:
    The created server call object.
  """
  indices = xrange(num_responses)

  if not name:
    name = ['image_%d' % x for x in indices]

  def ListResponse(unused_uri, unused_http_method, parameters, unused_body):
    return mock_server.MOCK_RESPONSE(
        {
            'kind': 'compute#imageList',
            'items': [{
                'kind': 'compute#image',
                'name': name[x],
                'selfLink': command.NormalizeGlobalResourceName(
                    parameters['project'],
                    'images',
                    name[x]),
                } for x in indices]
        },
        True)

  return mock_server.RespondF('compute.images.list', ListResponse)


def MockImageListForCustomerAndStandardProjects(
    command, mock_server, names=None):
  """Register the calls needed to list all images.

  It calls GetSampleImageListCall for the customer project as well as
  each of the standard projects.

  Args:
    command: The gcutil command that this call is based on.
    mock_server:  The mock server to register the list call on.
    names: A collection of collections of image names. Each collection
      corresponds to the names to be returned by one call.  If names is None,
      or the number of collections is less than required, default
      parameters for GetSampleImageListCall will be used.
  """
  for i in range(len(command_base.STANDARD_IMAGE_PROJECTS) + 1):
    if not names or i >= len(names) or names[i] is None:
      GetSampleImageListCall(command, mock_server)
    else:
      name = names[i]
      GetSampleImageListCall(command, mock_server, len(name), name)


def GetSampleInstanceListCall(command, mock_server, num_responses=2,
                              name=None, description=None, disks=None,
                              networkInterfaces=None, machineType=None,
                              zone=None, project=None):
  """Registers a sample instance list call on the mock server.

  Args:
    command: The gcutil command that this call is based on.
    mock_server:  The mock server to register the list call on.
    num_responses:  The size of the desired call.
    name:  Optional list of names for the instances.
    description:  Optional list of descriptions for the instances.
    disks:  Optional list of disks for the instances.
    networkInterfaces:  Optional list of networkInterfaces for the instances.
    machineType:  Optional list of machine types for the instances.
    zone:  Optional list of zones for the instances.
    project:  Optional project for the instances.

  Returns:
    The created server call object.
  """
  indices = xrange(num_responses)

  # If entries are not specified, generate some.
  if not name:
    name = ['test-instance-%d' % x for x in indices]

  if not description:
    description = ['description-%d' % x for x in indices]

  if not disks:
    disks = [[] for x in indices]

  if not networkInterfaces:
    networkInterfaces = [[] for x in indices]

  if not machineType:
    machineType = ['n1-standard-1' for x in indices]

  if not zone:
    zone = ['danger-zone' for x in indices]

  if not project:
    project = ['sample-project' for x in indices]

  def ListResponse(unused_uri, unused_http_method, unused_parameters,
                   unused_body):
    return mock_server.MOCK_RESPONSE(
        {
            'kind': 'compute#instanceList',
            'items': [{
                'disks': disks[x],
                'kind': 'compute#instance',
                'name': name[x],
                'description': description[x],
                'networkInterfaces': networkInterfaces[x],
                'machineType': machineType[x],
                'zone': zone[x],
                'selfLink': command.NormalizePerZoneResourceName(
                    project[x], zone[x], 'instances', name[x]),
                } for x in indices]
        },
        True)

  return mock_server.RespondF('compute.instances.list', ListResponse)


def GetSampleMachineTypeListCall(command, mock_server, num_responses=2):
  """Registers a sample machine type list call on the mock server.

  Args:
    command: The gcutil command that this call is based on.
    mock_server:  The mock server to register the list call on.
    num_responses:  The size of the desired call.

  Returns:
    The created server call object.
  """
  def ListResponse(unused_uri, unused_http_method, parameters, unused_body):
    return mock_server.MOCK_RESPONSE(
        {
            'kind': 'compute#machineTypeList',
            'items': [{
                'description': 'Machine type description %d' % x,
                'kind': 'compute#machineType',
                'name': 'machine_type_%d' % x,
                'guestCpus': 1,
                'selfLink': command.NormalizeGlobalResourceName(
                    parameters['project'],
                    'machineTypes',
                    'machine_type_%d' % x),
                'zone': command.NormalizeGlobalResourceName(
                    parameters['project'],
                    'zones',
                    parameters['zone'] if 'zone' in parameters else 'default')
                } for x in xrange(num_responses)]
        },
        True)

  return mock_server.RespondF('compute.machineTypes.list', ListResponse)


def GetSampleNetworkListCall(unused_command, mock_server, num_responses=2,
                             name=None, description=None):
  """Registers a sample network list call on the mock server.

  Args:
    unused_command: The gcutil command that this call is based on.  Unused.
    mock_server:  The mock server to register the list call on.
    num_responses:  The size of the desired call.
    name:  Optional list of names for the networks.
    description:  Optional list of descriptions for the networks.

  Returns:
    The created server call object.
  """
  indices = xrange(num_responses)

  # If entries are not specified, generate some.
  if not name:
    name = ['test-network-%d' % x for x in indices]

  if not description:
    description = ['description-%d' % x for x in indices]

  def ListResponse(unused_uri, unused_http_method, unused_parameters,
                   unused_body):
    return mock_server.MOCK_RESPONSE(
        {
            'kind': 'compute#networkList',
            'items': [{
                'kind': 'compute#network',
                'name': name[x],
                'description': description[x]
                } for x in indices]
        },
        True)

  return mock_server.RespondF('compute.networks.list', ListResponse)


def GetSampleMaintenanceWindows(
    num_windows=1, ref_time=datetime.datetime(2013, 1, 1, 12, 0, 0)):
  """Gets a sample list of maintenance windows.

  Args:
    num_windows:  The number of windows to generate.
    ref_time:  The time for the first window.

  Returns:
    The created server call object.
  """

  maintenance_windows = []
  for window in xrange(num_windows):
    begin_time = ref_time + datetime.timedelta(days=window)
    end_time = begin_time + datetime.timedelta(hours=1)
    maintenance_windows.append({
        'name': 'name-%d' % window,
        'description': 'description-%d' % window,
        'beginTime': begin_time.isoformat(),
        'endTime': end_time.isoformat()
        })
  return maintenance_windows


def GetSampleZoneListCall(command, mock_server, num_responses=2,
                          name=None, description=None,
                          maintenanceWindows=None, quotas=None,
                          availableMachineType=None):
  """Registers a sample zone list call on the mock server.

  Args:
    command:  The gcutil command that this call is based on.
    mock_server:  The mock server to register the list call on.
    num_responses:  The size of the desired call.
    name:  Optional list of names for the zones.
    description:  Optional list of descriptions for the zones.
    maintenanceWindows:  Optional list of maintenance windows for zones.
    quotas:  Optional list of quotas for the zones.
    availableMachineType:  Optional list of machine types for the zones.

  Returns:
    The created server call object.
  """
  indices = xrange(num_responses)

  # If entries are not specified, generate some.
  if not name:
    name = ['test-zone-%d' % x for x in indices]

  if not description:
    description = ['description-%d' % x for x in indices]

  if not maintenanceWindows:
    # Zone 1 will have 0 windows, 2 will have 1, 3 will have 2, etc.
    maintenanceWindows = []
    for x in indices:
      # Reverse the order of maintenance windows so they're no longer in
      # ascending chronological order.
      maintenanceWindows.append(list(reversed(GetSampleMaintenanceWindows(x))))

  if not quotas:
    quotas = [[{'limit': 2, 'metric': 'CPUs', 'usage': 1}] for x in indices]

  if not availableMachineType:
    availableMachineType = [['party-machine', 't1000'] for x in indices]

  list_response_templates = {
      'v1': (
          lambda unused_uri, unused_http_method,
          unused_parameters, unused_body:
          mock_server.MOCK_RESPONSE(
              {
                  'kind': 'compute#zoneList',
                  'items': [{
                      'kind': 'compute#zone',
                      'name': name[x],
                      'description': description[x],
                      'maintenanceWindows': maintenanceWindows[x],
                      } for x in indices]
              },
              True)),
  }

  return mock_server.RespondF(
      'compute.zones.list', gcutil_unittest.SelectTemplateForVersion(
          list_response_templates, command.api.version))


def GetSampleRegionListCall(unused_command, mock_server, num_responses=2,
                            name=None, description=None, quotas=None):
  """Registers a sample region list call on the mock server.

  Args:
    unused_command:  The gcutil command that this call is based on.
    mock_server:  The mock server to register the list call on.
    num_responses:  The size of the desired call.
    name:  Optional list of names for the regions.
    description:  Optional list of descriptions for the regions.
    quotas:  Optional list of quotas for the regions.

  Returns:
    The created server call object.
  """
  indices = xrange(num_responses)

  # If entries are not specified, generate some.
  if not name:
    name = ['test-region-%d' % x for x in indices]

  if not description:
    description = ['description-%d' % x for x in indices]

  if not quotas:
    quotas = [[{'limit': 2, 'metric': 'CPUs', 'usage': 1}] for x in indices]

  def ListResponse(unused_uri, unused_http_method, unused_parameters,
                   unused_body):
    return mock_server.MOCK_RESPONSE(
        {
            'kind': 'compute#regionList',
            'items': [{
                'kind': 'compute#region',
                'name': name[x],
                'description': description[x],
                'quotas': quotas[x],
                } for x in indices]
        },
        True)

  return mock_server.RespondF('compute.regions.list', ListResponse)


def GetSampleDiskTypeListCall(command, mock_server, num_responses=2):
  """Registers a sample disk type list call on the mock server.

  Args:
    command: The gcutil command that this call is based on.
    mock_server:  The mock server to register the list call on.
    num_responses:  The size of the desired call.

  Returns:
    The created server call object.
  """
  def ListResponse(unused_uri, unused_http_method, parameters, unused_body):
    return mock_server.MOCK_RESPONSE(
        {
            'kind': 'compute#diskTypeList',
            'items': [{
                'description': 'Disk type description %d' % x,
                'kind': 'compute#diskType',
                'name': 'disk_type_%d' % x,
                'validDiskSize': '10GB-10TB',
                'selfLink': command.NormalizeGlobalResourceName(
                    parameters['project'],
                    'diskTypes',
                    'disk_type_%d' % x),
                'zone': command.NormalizeGlobalResourceName(
                    parameters['project'],
                    'zones',
                    parameters['zone'] if 'zone' in parameters else 'default')
                } for x in xrange(num_responses)]
        },
        True)

  return mock_server.RespondF('compute.diskTypes.list', ListResponse)
