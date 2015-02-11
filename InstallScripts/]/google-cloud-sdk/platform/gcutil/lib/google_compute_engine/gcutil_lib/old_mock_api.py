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

"""Mock Google Compute Engine API used for unit tests."""





import inspect

from gcutil_lib import gce_api
from gcutil_lib import version


class CommandExecutor(object):
  """An object to represent an apiclient endpoint with a fixed response."""

  def __init__(self, response):
    """Create a new CommandExecutor to return response for each API call."""
    self._response = response

  def __call__(self, **unused_kw):
    """Handle calling this object (part 1 of making an apiclient call)."""
    self._parameters = unused_kw
    return self

  def execute(self):
    """Return the stored results for this API call (part 2 of apiclient)."""
    return self._response


class MockRequest(object):
  """Mock request type for use with the MockApi class."""

  def __init__(self, payload, method_name=None):
    self.request_payload = payload
    # For now we return the request as a response.
    self.result_payload = payload
    self.method_name = method_name

  def execute(self, http=None):  # pylint: disable=unused-argument
    return self.result_payload


class MockApiBase(object):
  """Base class for all mock APIs."""

  def __init__(self):
    self.requests = []

  def RegisterRequest(self, request_data, **kwargs):
    if kwargs:
      request_data = dict(request_data.items() + kwargs.items())
    request = MockRequest(request_data, inspect.stack()[1][3])
    self.requests.append(request)
    return request


class MockAddressesApi(MockApiBase):
  """Mock return result of the MockApi.addresses() method."""

  def get(self, project='wrong_project', address='wrong_address', **kwargs):
    return self.RegisterRequest({'project': project, 'address': address},
                                **kwargs)

  def insert(self, project='wrong_project', body='wrong_address_resource',
             **kwargs):
    return self.RegisterRequest({'project': project, 'body': body}, **kwargs)

  def delete(self, project='wrong_project', address='wrong_address', **kwargs):
    return self.RegisterRequest({'project': project, 'address': address},
                                **kwargs)

  def list(self, project='wrong_project', region='wrong_region', **kwargs):
    return self.RegisterRequest({'project': project, 'region': region},
                                **kwargs)

  def aggregatedList(self, project='wrong_project', **kwargs):
    return self.RegisterRequest({'project': project}, **kwargs)


class MockDisksApi(MockApiBase):
  """Mock return result of the MockApi.disks() method."""

  def get(self, project='wrong_project', disk='wrong_disk', **kwargs):
    return self.RegisterRequest({'project': project, 'disk': disk}, **kwargs)

  def insert(self, project='wrong_project', body='wrong_disk_resource',
             sourceImage='wrong_source_image', **kwargs):
    return self.RegisterRequest({'project': project, 'body': body,
                                 'sourceImage': sourceImage}, **kwargs)

  def delete(self, project='wrong_project', disk='wrong_disk', **kwargs):
    return self.RegisterRequest({'project': project, 'disk': disk}, **kwargs)

  def list(self, project='wrong_project', zone='wrong_zone', **kwargs):
    return self.RegisterRequest({'project': project, 'zone': zone}, **kwargs)

  def createSnapshot(self, project='wrong_project', disk='wrong_disk',
                     zone='wrong_zone', body='wrong snapshot resource',
                     **kwargs):
    return self.RegisterRequest({'project': project, 'disk': disk, 'zone': zone,
                                 'body': body}, **kwargs)


class MockFirewallsApi(MockApiBase):
  """Mock return result of the MockApi.firewalls() method."""

  def get(self, project='wrong_project', firewall='wrong_firewall'):
    return self.RegisterRequest({'project': project, 'firewall': firewall})

  def insert(self, project='wrong_project', body='wrong_firewall_resource'):
    return self.RegisterRequest({'project': project, 'body': body})

  def delete(self, project='wrong_project', firewall='wrong_firewall'):
    return self.RegisterRequest({'project': project, 'firewall': firewall})

  def list(self, project='wrong_project'):
    return self.RegisterRequest({'project': project})


class MockNetworksApi(MockApiBase):
  """Mock return result of the MockApi.networks() method."""

  def get(self, project='wrong_project', network='wrong_network'):
    return self.RegisterRequest({'project': project, 'network': network})

  def insert(self, project='wrong_project', body='wrong_network_resource'):
    return self.RegisterRequest({'project': project, 'body': body})

  def delete(self, project='wrong_project', network='wrong_network'):
    return self.RegisterRequest({'project': project, 'network': network})

  def list(self, project='wrong_project'):
    return self.RegisterRequest({'project': project})


class MockGlobalOperationsApi(MockApiBase):
  """Mock return result of the MockApi.globalOperations() method."""

  def get(self, project='wrong_project', operation='wrong_operation', **kwargs):
    return self.RegisterRequest({'project': project, 'operation': operation},
                                **kwargs)

  def delete(self, project='wrong_project', operation='wrong_operation'):
    return self.RegisterRequest({'project': project, 'operation': operation})

  def list(self, project='wrong_project'):
    return self.RegisterRequest({'project': project})


class MockZoneOperationsApi(MockApiBase):
  """Mock return result of the MockApi.zoneOperations() method."""

  def get(self, project='wrong_project', operation='wrong_operation',
          zone='wrong_zone'):
    return self.RegisterRequest({'project': project,
                                 'operation': operation,
                                 'zone': zone})

  def delete(self, project='wrong_project', operation='wrong_operation',
             zone='wrong_zone'):
    return self.RegisterRequest({'project': project,
                                 'operation': operation,
                                 'zone': zone})

  def list(self, project='wrong_project', zone='wrong_zone'):
    return self.RegisterRequest({'project': project, 'zone': zone})


class MockRegionOperationsApi(MockApiBase):
  """Mock return result of the MockApi.zoneOperations() method."""

  def get(self, project='wrong_project', operation='wrong_operation',
          region='wrong_region'):
    return self.RegisterRequest({'project': project,
                                 'operation': operation,
                                 'region': region})

  def delete(self, project='wrong_project', operation='wrong_operation',
             region='wrong_region'):
    return self.RegisterRequest({'project': project,
                                 'operation': operation,
                                 'region': region})

  def list(self, project='wrong_project', region='wrong_region'):
    return self.RegisterRequest({'project': project, 'region': region})


class MockImagesApi(MockApiBase):
  """Mock return result of the MockApi.images() method."""

  def get(self, project='wrong_project', image='wrong_image'):
    return self.RegisterRequest({'project': project, 'image': image})

  def insert(self, project='wrong_project', body='wrong_image_resource'):
    return self.RegisterRequest({'project': project, 'body': body})

  def delete(self, project='wrong_project', image='wrong_image'):
    return self.RegisterRequest({'project': project, 'image': image})

  def list(self, project='wrong_project', **unused_kwargs):
    return self.RegisterRequest({'project': project})

  def deprecate(self, project='wrong_project', image='wrong_image',
                body='wrong_deprecation_resource'):
    return self.RegisterRequest({'project': project, 'image': image,
                                 'body': body})


class MockInstancesApi(MockApiBase):
  """Mock return result of the MockApi.instances() method."""

  def get(self, project='wrong_project', instance='wrong_instance', **kwargs):
    return self.RegisterRequest({'project': project, 'instance': instance},
                                **kwargs)

  def insert(self, project='wrong_project', body='wrong_instance_resource',
             **kwargs):
    return self.RegisterRequest({'project': project, 'body': body}, **kwargs)

  def delete(self, project='wrong_project', instance='wrong_instance',
             **kwargs):
    return self.RegisterRequest({'project': project, 'instance': instance},
                                **kwargs)

  def list(self, project='wrong_project', zone='wrong_zone', **unused_kwargs):
    return self.RegisterRequest({'project': project, 'zone': zone})

  def addAccessConfig(self, project='wrong_project', instance='wrong_instance',
                      network_interface='wrong_network_interface',
                      body='wrong_instance_resource', **kwargs):
    return self.RegisterRequest({'project': project, 'instance': instance,
                                 'network_interface': network_interface,
                                 'body': body}, **kwargs)

  def deleteAccessConfig(self, project='wrong_project',
                         instance='wrong_instance',
                         networkInterface='wrong_network_interface',
                         accessConfig='wrong_access_config',
                         **kwargs):
    return self.RegisterRequest({'project': project, 'instance': instance,
                                 'networkInterface': networkInterface,
                                 'accessConfig': accessConfig}, **kwargs)

  def reset(self, project='wrong_project', instance='wrong_instance',
            zone='wrong_zone'):
    return self.RegisterRequest({'project': project, 'instance': instance,
                                 'zone': zone})

  def setMetadata(self, project='wrong_project', instance='wrong_instance',
                  body='wrong_metadata', zone='wrong_zone'):
    return self.RegisterRequest({'project': project, 'instance': instance,
                                 'body': body, 'zone': zone})

  def setTags(self, project='wrong_project', instance='wrong_instance',
              body='wrong_tags', zone='wrong_zone'):
    return self.RegisterRequest({'project': project, 'instance': instance,
                                 'body': body, 'zone': zone})

  def attachDisk(self, project='wrong_project', instance='wrong_instance',
                 body='wrong_disk_body', zone='wrong_zone'):
    return self.RegisterRequest({'project': project, 'instance': instance,
                                 'body': body, 'zone': zone})

  def detachDisk(self, project='wrong_project', instance='wrong_instance',
                 deviceName='wrong_disk_name', zone='wrong_zone'):
    return self.RegisterRequest({'project': project, 'instance': instance,
                                 'deviceName': deviceName, 'zone': zone})


class MockMachineSpecsApi(MockApiBase):
  """Mock return result of the MockApi.machineSpecs() method."""

  def get(self, machineSpec='wrong_machine_type'):
    return self.RegisterRequest({'machineSpec': machineSpec})

  def list(self):
    return self.RegisterRequest('empty_result')


class MockMachineTypesApi(MockApiBase):
  """Mock return result of the MockApi.machineTypes() method."""

  def get(self, machineType='wrong_machine_type', zone='wrong_zone',
          **unused_kwargs):
    return self.RegisterRequest({'machineType': machineType, 'zone': zone})

  def list(self, **unused_kwargs):
    return self.RegisterRequest('empty_result')


class MockProjectsApi(MockApiBase):
  """Mock return result of the MockApi.projects() method."""

  def get(self, project='wrong_project'):
    return self.RegisterRequest({'project': project})

  def setCommonInstanceMetadata(self, project='wrong_project', body=None):
    return self.RegisterRequest({'project': project,
                                 'commonInstanceMetadata': body})


class MockRegionsApi(MockApiBase):
  """Mock return result of the MockApi.regions() method."""

  def get(self, region='wrong_region', **unused_kwargs):
    return self.RegisterRequest({'region': region})

  def list(self, **unused_kwargs):
    return self.RegisterRequest('empty_result')


class MockRoutesApi(MockApiBase):
  """Mock return result of the MockApi.routes() method."""

  def get(self, project='wrong_project', route='wrong_route'):
    return self.RegisterRequest({'project': project, 'route': route})

  def insert(self, project='wrong_project', body='wrong_route_resource'):
    return self.RegisterRequest({'project': project, 'body': body})

  def delete(self, project='wrong_project', route='wrong_route'):
    return self.RegisterRequest({'project': project, 'route': route})

  def list(self, project='wrong_project'):
    return self.RegisterRequest({'project': project})


class MockSnapshotsApi(MockApiBase):
  """Mock return result of the MockApi.snapshots() method."""

  def get(self, project='wrong_project', snapshot='wrong_snapshot', **kwargs):
    return self.RegisterRequest({'project': project, 'snapshot': snapshot},
                                **kwargs)

  def insert(self, project='wrong_project', body='wrong_snapshot_resource',
             **kwargs):
    return self.RegisterRequest({'project': project, 'body': body}, **kwargs)

  def delete(self, project='wrong_project', snapshot='wrong_snapshot',
             **kwargs):
    return self.RegisterRequest({'project': project, 'snapshot': snapshot},
                                **kwargs)

  def list(self, project='wrong_project', **kwargs):
    return self.RegisterRequest({'project': project}, **kwargs)


class MockZonesApi(MockApiBase):
  """Mock return result of the MockApi.zones() method."""

  def get(self, zone='wrong_zone', **unused_kwargs):
    return self.RegisterRequest({'zone': zone})

  def list(self, **unused_kwargs):
    return self.RegisterRequest('empty_result')


class MockApi(object):
  """Mock of the Google Compute Engine API returned by the discovery client."""

  def addresses(self):
    return MockAddressesApi()

  def disks(self):
    return MockDisksApi()

  def firewalls(self):
    return MockFirewallsApi()

  def forwardingRules(self):
    return None

  def httpHealthChecks(self):
    return None

  def networks(self):
    return MockNetworksApi()

  def images(self):
    return MockImagesApi()

  def instances(self):
    return MockInstancesApi()

  def machineSpecs(self):
    return MockMachineSpecsApi()

  def machineTypes(self):
    return MockMachineTypesApi()

  def projects(self):
    return MockProjectsApi()

  def operations(self):
    return MockGlobalOperationsApi()

  def regionOperations(self):
    return MockRegionOperationsApi()

  def zoneOperations(self):
    return MockZoneOperationsApi()

  def globalOperations(self):
    return MockGlobalOperationsApi()

  def routes(self):
    return MockRoutesApi()

  def regions(self):
    return MockRegionsApi()

  def snapshots(self):
    return MockSnapshotsApi()

  def targetPools(self):
    return None

  def zones(self):
    return MockZonesApi()


class MockCredential(object):
  """A mock credential that does nothing."""

  def authorize(self, http):
    return http


def CreateMockApi(service_version='v1'):
  return gce_api.ComputeApi(MockApi(), version.get(service_version), None)
