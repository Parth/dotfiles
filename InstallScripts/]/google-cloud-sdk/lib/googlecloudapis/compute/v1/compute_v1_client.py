"""Generated client library for compute version v1."""

from googlecloudapis.apitools.base.py import base_api
from googlecloudapis.compute.v1 import compute_v1_messages as messages


class ComputeV1(base_api.BaseApiClient):
  """Generated client library for service compute version v1."""

  MESSAGES_MODULE = messages

  _PACKAGE = u'compute'
  _SCOPES = [u'https://www.googleapis.com/auth/compute', u'https://www.googleapis.com/auth/compute.readonly', u'https://www.googleapis.com/auth/devstorage.full_control', u'https://www.googleapis.com/auth/devstorage.read_only', u'https://www.googleapis.com/auth/devstorage.read_write']
  _VERSION = u'v1'
  _CLIENT_ID = ''
  _CLIENT_SECRET = ''
  _USER_AGENT = ''
  _CLIENT_CLASS_NAME = u'ComputeV1'
  _URL_VERSION = u'v1'

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new compute handle."""
    url = url or u'https://www.googleapis.com/compute/v1/'
    super(ComputeV1, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.addresses = self.AddressesService(self)
    self.backendServices = self.BackendServicesService(self)
    self.diskTypes = self.DiskTypesService(self)
    self.disks = self.DisksService(self)
    self.firewalls = self.FirewallsService(self)
    self.forwardingRules = self.ForwardingRulesService(self)
    self.globalAddresses = self.GlobalAddressesService(self)
    self.globalForwardingRules = self.GlobalForwardingRulesService(self)
    self.globalOperations = self.GlobalOperationsService(self)
    self.httpHealthChecks = self.HttpHealthChecksService(self)
    self.images = self.ImagesService(self)
    self.instanceTemplates = self.InstanceTemplatesService(self)
    self.instances = self.InstancesService(self)
    self.licenses = self.LicensesService(self)
    self.machineTypes = self.MachineTypesService(self)
    self.networks = self.NetworksService(self)
    self.projects = self.ProjectsService(self)
    self.regionOperations = self.RegionOperationsService(self)
    self.regions = self.RegionsService(self)
    self.routes = self.RoutesService(self)
    self.snapshots = self.SnapshotsService(self)
    self.targetHttpProxies = self.TargetHttpProxiesService(self)
    self.targetInstances = self.TargetInstancesService(self)
    self.targetPools = self.TargetPoolsService(self)
    self.urlMaps = self.UrlMapsService(self)
    self.zoneOperations = self.ZoneOperationsService(self)
    self.zones = self.ZonesService(self)

  class AddressesService(base_api.BaseApiService):
    """Service class for the addresses resource."""

    _NAME = u'addresses'

    def __init__(self, client):
      super(ComputeV1.AddressesService, self).__init__(client)
      self._method_configs = {
          'AggregatedList': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.addresses.aggregatedList',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/aggregated/addresses',
              request_field='',
              request_type_name=u'ComputeAddressesAggregatedListRequest',
              response_type_name=u'AddressAggregatedList',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.addresses.delete',
              ordered_params=[u'project', u'region', u'address'],
              path_params=[u'address', u'project', u'region'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/addresses/{address}',
              request_field='',
              request_type_name=u'ComputeAddressesDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.addresses.get',
              ordered_params=[u'project', u'region', u'address'],
              path_params=[u'address', u'project', u'region'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/addresses/{address}',
              request_field='',
              request_type_name=u'ComputeAddressesGetRequest',
              response_type_name=u'Address',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.addresses.insert',
              ordered_params=[u'project', u'region'],
              path_params=[u'project', u'region'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/addresses',
              request_field=u'address',
              request_type_name=u'ComputeAddressesInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.addresses.list',
              ordered_params=[u'project', u'region'],
              path_params=[u'project', u'region'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/regions/{region}/addresses',
              request_field='',
              request_type_name=u'ComputeAddressesListRequest',
              response_type_name=u'AddressList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def AggregatedList(self, request, global_params=None):
      """Retrieves the list of addresses grouped by scope.

      Args:
        request: (ComputeAddressesAggregatedListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (AddressAggregatedList) The response message.
      """
      config = self.GetMethodConfig('AggregatedList')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Deletes the specified address resource.

      Args:
        request: (ComputeAddressesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified address resource.

      Args:
        request: (ComputeAddressesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Address) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates an address resource in the specified project using the data included in the request.

      Args:
        request: (ComputeAddressesInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of address resources contained within the specified region.

      Args:
        request: (ComputeAddressesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (AddressList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class BackendServicesService(base_api.BaseApiService):
    """Service class for the backendServices resource."""

    _NAME = u'backendServices'

    def __init__(self, client):
      super(ComputeV1.BackendServicesService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.backendServices.delete',
              ordered_params=[u'project', u'backendService'],
              path_params=[u'backendService', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/backendServices/{backendService}',
              request_field='',
              request_type_name=u'ComputeBackendServicesDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.backendServices.get',
              ordered_params=[u'project', u'backendService'],
              path_params=[u'backendService', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/backendServices/{backendService}',
              request_field='',
              request_type_name=u'ComputeBackendServicesGetRequest',
              response_type_name=u'BackendService',
              supports_download=False,
          ),
          'GetHealth': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.backendServices.getHealth',
              ordered_params=[u'project', u'backendService'],
              path_params=[u'backendService', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/backendServices/{backendService}/getHealth',
              request_field=u'resourceGroupReference',
              request_type_name=u'ComputeBackendServicesGetHealthRequest',
              response_type_name=u'BackendServiceGroupHealth',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.backendServices.insert',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/backendServices',
              request_field=u'backendService',
              request_type_name=u'ComputeBackendServicesInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.backendServices.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/global/backendServices',
              request_field='',
              request_type_name=u'ComputeBackendServicesListRequest',
              response_type_name=u'BackendServiceList',
              supports_download=False,
          ),
          'Patch': base_api.ApiMethodInfo(
              http_method=u'PATCH',
              method_id=u'compute.backendServices.patch',
              ordered_params=[u'project', u'backendService'],
              path_params=[u'backendService', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/backendServices/{backendService}',
              request_field=u'backendServiceResource',
              request_type_name=u'ComputeBackendServicesPatchRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Update': base_api.ApiMethodInfo(
              http_method=u'PUT',
              method_id=u'compute.backendServices.update',
              ordered_params=[u'project', u'backendService'],
              path_params=[u'backendService', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/backendServices/{backendService}',
              request_field=u'backendServiceResource',
              request_type_name=u'ComputeBackendServicesUpdateRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified BackendService resource.

      Args:
        request: (ComputeBackendServicesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified BackendService resource.

      Args:
        request: (ComputeBackendServicesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (BackendService) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def GetHealth(self, request, global_params=None):
      """Gets the most recent health check results for this BackendService.

      Args:
        request: (ComputeBackendServicesGetHealthRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (BackendServiceGroupHealth) The response message.
      """
      config = self.GetMethodConfig('GetHealth')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates a BackendService resource in the specified project using the data included in the request.

      Args:
        request: (ComputeBackendServicesInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of BackendService resources available to the specified project.

      Args:
        request: (ComputeBackendServicesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (BackendServiceList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Patch(self, request, global_params=None):
      """Update the entire content of the BackendService resource. This method supports patch semantics.

      Args:
        request: (ComputeBackendServicesPatchRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Patch')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Update(self, request, global_params=None):
      """Update the entire content of the BackendService resource.

      Args:
        request: (ComputeBackendServicesUpdateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Update')
      return self._RunMethod(
          config, request, global_params=global_params)

  class DiskTypesService(base_api.BaseApiService):
    """Service class for the diskTypes resource."""

    _NAME = u'diskTypes'

    def __init__(self, client):
      super(ComputeV1.DiskTypesService, self).__init__(client)
      self._method_configs = {
          'AggregatedList': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.diskTypes.aggregatedList',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/aggregated/diskTypes',
              request_field='',
              request_type_name=u'ComputeDiskTypesAggregatedListRequest',
              response_type_name=u'DiskTypeAggregatedList',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.diskTypes.get',
              ordered_params=[u'project', u'zone', u'diskType'],
              path_params=[u'diskType', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/diskTypes/{diskType}',
              request_field='',
              request_type_name=u'ComputeDiskTypesGetRequest',
              response_type_name=u'DiskType',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.diskTypes.list',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/zones/{zone}/diskTypes',
              request_field='',
              request_type_name=u'ComputeDiskTypesListRequest',
              response_type_name=u'DiskTypeList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def AggregatedList(self, request, global_params=None):
      """Retrieves the list of disk type resources grouped by scope.

      Args:
        request: (ComputeDiskTypesAggregatedListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (DiskTypeAggregatedList) The response message.
      """
      config = self.GetMethodConfig('AggregatedList')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified disk type resource.

      Args:
        request: (ComputeDiskTypesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (DiskType) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of disk type resources available to the specified project.

      Args:
        request: (ComputeDiskTypesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (DiskTypeList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class DisksService(base_api.BaseApiService):
    """Service class for the disks resource."""

    _NAME = u'disks'

    def __init__(self, client):
      super(ComputeV1.DisksService, self).__init__(client)
      self._method_configs = {
          'AggregatedList': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.disks.aggregatedList',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/aggregated/disks',
              request_field='',
              request_type_name=u'ComputeDisksAggregatedListRequest',
              response_type_name=u'DiskAggregatedList',
              supports_download=False,
          ),
          'CreateSnapshot': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.disks.createSnapshot',
              ordered_params=[u'project', u'zone', u'disk'],
              path_params=[u'disk', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/disks/{disk}/createSnapshot',
              request_field=u'snapshot',
              request_type_name=u'ComputeDisksCreateSnapshotRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.disks.delete',
              ordered_params=[u'project', u'zone', u'disk'],
              path_params=[u'disk', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/disks/{disk}',
              request_field='',
              request_type_name=u'ComputeDisksDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.disks.get',
              ordered_params=[u'project', u'zone', u'disk'],
              path_params=[u'disk', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/disks/{disk}',
              request_field='',
              request_type_name=u'ComputeDisksGetRequest',
              response_type_name=u'Disk',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.disks.insert',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[u'sourceImage'],
              relative_path=u'projects/{project}/zones/{zone}/disks',
              request_field=u'disk',
              request_type_name=u'ComputeDisksInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.disks.list',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/zones/{zone}/disks',
              request_field='',
              request_type_name=u'ComputeDisksListRequest',
              response_type_name=u'DiskList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def AggregatedList(self, request, global_params=None):
      """Retrieves the list of disks grouped by scope.

      Args:
        request: (ComputeDisksAggregatedListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (DiskAggregatedList) The response message.
      """
      config = self.GetMethodConfig('AggregatedList')
      return self._RunMethod(
          config, request, global_params=global_params)

    def CreateSnapshot(self, request, global_params=None):
      """CreateSnapshot method for the disks service.

      Args:
        request: (ComputeDisksCreateSnapshotRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('CreateSnapshot')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Deletes the specified persistent disk resource.

      Args:
        request: (ComputeDisksDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified persistent disk resource.

      Args:
        request: (ComputeDisksGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Disk) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates a persistent disk resource in the specified project using the data included in the request.

      Args:
        request: (ComputeDisksInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of persistent disk resources contained within the specified zone.

      Args:
        request: (ComputeDisksListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (DiskList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class FirewallsService(base_api.BaseApiService):
    """Service class for the firewalls resource."""

    _NAME = u'firewalls'

    def __init__(self, client):
      super(ComputeV1.FirewallsService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.firewalls.delete',
              ordered_params=[u'project', u'firewall'],
              path_params=[u'firewall', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/firewalls/{firewall}',
              request_field='',
              request_type_name=u'ComputeFirewallsDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.firewalls.get',
              ordered_params=[u'project', u'firewall'],
              path_params=[u'firewall', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/firewalls/{firewall}',
              request_field='',
              request_type_name=u'ComputeFirewallsGetRequest',
              response_type_name=u'Firewall',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.firewalls.insert',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/firewalls',
              request_field=u'firewall',
              request_type_name=u'ComputeFirewallsInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.firewalls.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/global/firewalls',
              request_field='',
              request_type_name=u'ComputeFirewallsListRequest',
              response_type_name=u'FirewallList',
              supports_download=False,
          ),
          'Patch': base_api.ApiMethodInfo(
              http_method=u'PATCH',
              method_id=u'compute.firewalls.patch',
              ordered_params=[u'project', u'firewall'],
              path_params=[u'firewall', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/firewalls/{firewall}',
              request_field=u'firewallResource',
              request_type_name=u'ComputeFirewallsPatchRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Update': base_api.ApiMethodInfo(
              http_method=u'PUT',
              method_id=u'compute.firewalls.update',
              ordered_params=[u'project', u'firewall'],
              path_params=[u'firewall', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/firewalls/{firewall}',
              request_field=u'firewallResource',
              request_type_name=u'ComputeFirewallsUpdateRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified firewall resource.

      Args:
        request: (ComputeFirewallsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified firewall resource.

      Args:
        request: (ComputeFirewallsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Firewall) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates a firewall resource in the specified project using the data included in the request.

      Args:
        request: (ComputeFirewallsInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of firewall resources available to the specified project.

      Args:
        request: (ComputeFirewallsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (FirewallList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Patch(self, request, global_params=None):
      """Updates the specified firewall resource with the data included in the request. This method supports patch semantics.

      Args:
        request: (ComputeFirewallsPatchRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Patch')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Update(self, request, global_params=None):
      """Updates the specified firewall resource with the data included in the request.

      Args:
        request: (ComputeFirewallsUpdateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Update')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ForwardingRulesService(base_api.BaseApiService):
    """Service class for the forwardingRules resource."""

    _NAME = u'forwardingRules'

    def __init__(self, client):
      super(ComputeV1.ForwardingRulesService, self).__init__(client)
      self._method_configs = {
          'AggregatedList': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.forwardingRules.aggregatedList',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/aggregated/forwardingRules',
              request_field='',
              request_type_name=u'ComputeForwardingRulesAggregatedListRequest',
              response_type_name=u'ForwardingRuleAggregatedList',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.forwardingRules.delete',
              ordered_params=[u'project', u'region', u'forwardingRule'],
              path_params=[u'forwardingRule', u'project', u'region'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/forwardingRules/{forwardingRule}',
              request_field='',
              request_type_name=u'ComputeForwardingRulesDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.forwardingRules.get',
              ordered_params=[u'project', u'region', u'forwardingRule'],
              path_params=[u'forwardingRule', u'project', u'region'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/forwardingRules/{forwardingRule}',
              request_field='',
              request_type_name=u'ComputeForwardingRulesGetRequest',
              response_type_name=u'ForwardingRule',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.forwardingRules.insert',
              ordered_params=[u'project', u'region'],
              path_params=[u'project', u'region'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/forwardingRules',
              request_field=u'forwardingRule',
              request_type_name=u'ComputeForwardingRulesInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.forwardingRules.list',
              ordered_params=[u'project', u'region'],
              path_params=[u'project', u'region'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/regions/{region}/forwardingRules',
              request_field='',
              request_type_name=u'ComputeForwardingRulesListRequest',
              response_type_name=u'ForwardingRuleList',
              supports_download=False,
          ),
          'SetTarget': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.forwardingRules.setTarget',
              ordered_params=[u'project', u'region', u'forwardingRule'],
              path_params=[u'forwardingRule', u'project', u'region'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/forwardingRules/{forwardingRule}/setTarget',
              request_field=u'targetReference',
              request_type_name=u'ComputeForwardingRulesSetTargetRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def AggregatedList(self, request, global_params=None):
      """Retrieves the list of forwarding rules grouped by scope.

      Args:
        request: (ComputeForwardingRulesAggregatedListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ForwardingRuleAggregatedList) The response message.
      """
      config = self.GetMethodConfig('AggregatedList')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Deletes the specified ForwardingRule resource.

      Args:
        request: (ComputeForwardingRulesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified ForwardingRule resource.

      Args:
        request: (ComputeForwardingRulesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ForwardingRule) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates a ForwardingRule resource in the specified project and region using the data included in the request.

      Args:
        request: (ComputeForwardingRulesInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of ForwardingRule resources available to the specified project and region.

      Args:
        request: (ComputeForwardingRulesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ForwardingRuleList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def SetTarget(self, request, global_params=None):
      """Changes target url for forwarding rule.

      Args:
        request: (ComputeForwardingRulesSetTargetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('SetTarget')
      return self._RunMethod(
          config, request, global_params=global_params)

  class GlobalAddressesService(base_api.BaseApiService):
    """Service class for the globalAddresses resource."""

    _NAME = u'globalAddresses'

    def __init__(self, client):
      super(ComputeV1.GlobalAddressesService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.globalAddresses.delete',
              ordered_params=[u'project', u'address'],
              path_params=[u'address', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/addresses/{address}',
              request_field='',
              request_type_name=u'ComputeGlobalAddressesDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.globalAddresses.get',
              ordered_params=[u'project', u'address'],
              path_params=[u'address', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/addresses/{address}',
              request_field='',
              request_type_name=u'ComputeGlobalAddressesGetRequest',
              response_type_name=u'Address',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.globalAddresses.insert',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/addresses',
              request_field=u'address',
              request_type_name=u'ComputeGlobalAddressesInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.globalAddresses.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/global/addresses',
              request_field='',
              request_type_name=u'ComputeGlobalAddressesListRequest',
              response_type_name=u'AddressList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified address resource.

      Args:
        request: (ComputeGlobalAddressesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified address resource.

      Args:
        request: (ComputeGlobalAddressesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Address) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates an address resource in the specified project using the data included in the request.

      Args:
        request: (ComputeGlobalAddressesInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of global address resources.

      Args:
        request: (ComputeGlobalAddressesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (AddressList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class GlobalForwardingRulesService(base_api.BaseApiService):
    """Service class for the globalForwardingRules resource."""

    _NAME = u'globalForwardingRules'

    def __init__(self, client):
      super(ComputeV1.GlobalForwardingRulesService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.globalForwardingRules.delete',
              ordered_params=[u'project', u'forwardingRule'],
              path_params=[u'forwardingRule', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/forwardingRules/{forwardingRule}',
              request_field='',
              request_type_name=u'ComputeGlobalForwardingRulesDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.globalForwardingRules.get',
              ordered_params=[u'project', u'forwardingRule'],
              path_params=[u'forwardingRule', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/forwardingRules/{forwardingRule}',
              request_field='',
              request_type_name=u'ComputeGlobalForwardingRulesGetRequest',
              response_type_name=u'ForwardingRule',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.globalForwardingRules.insert',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/forwardingRules',
              request_field=u'forwardingRule',
              request_type_name=u'ComputeGlobalForwardingRulesInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.globalForwardingRules.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/global/forwardingRules',
              request_field='',
              request_type_name=u'ComputeGlobalForwardingRulesListRequest',
              response_type_name=u'ForwardingRuleList',
              supports_download=False,
          ),
          'SetTarget': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.globalForwardingRules.setTarget',
              ordered_params=[u'project', u'forwardingRule'],
              path_params=[u'forwardingRule', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/forwardingRules/{forwardingRule}/setTarget',
              request_field=u'targetReference',
              request_type_name=u'ComputeGlobalForwardingRulesSetTargetRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified ForwardingRule resource.

      Args:
        request: (ComputeGlobalForwardingRulesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified ForwardingRule resource.

      Args:
        request: (ComputeGlobalForwardingRulesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ForwardingRule) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates a ForwardingRule resource in the specified project and region using the data included in the request.

      Args:
        request: (ComputeGlobalForwardingRulesInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of ForwardingRule resources available to the specified project.

      Args:
        request: (ComputeGlobalForwardingRulesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ForwardingRuleList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def SetTarget(self, request, global_params=None):
      """Changes target url for forwarding rule.

      Args:
        request: (ComputeGlobalForwardingRulesSetTargetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('SetTarget')
      return self._RunMethod(
          config, request, global_params=global_params)

  class GlobalOperationsService(base_api.BaseApiService):
    """Service class for the globalOperations resource."""

    _NAME = u'globalOperations'

    def __init__(self, client):
      super(ComputeV1.GlobalOperationsService, self).__init__(client)
      self._method_configs = {
          'AggregatedList': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.globalOperations.aggregatedList',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/aggregated/operations',
              request_field='',
              request_type_name=u'ComputeGlobalOperationsAggregatedListRequest',
              response_type_name=u'OperationAggregatedList',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.globalOperations.delete',
              ordered_params=[u'project', u'operation'],
              path_params=[u'operation', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/operations/{operation}',
              request_field='',
              request_type_name=u'ComputeGlobalOperationsDeleteRequest',
              response_type_name=u'ComputeGlobalOperationsDeleteResponse',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.globalOperations.get',
              ordered_params=[u'project', u'operation'],
              path_params=[u'operation', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/operations/{operation}',
              request_field='',
              request_type_name=u'ComputeGlobalOperationsGetRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.globalOperations.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/global/operations',
              request_field='',
              request_type_name=u'ComputeGlobalOperationsListRequest',
              response_type_name=u'OperationList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def AggregatedList(self, request, global_params=None):
      """Retrieves the list of all operations grouped by scope.

      Args:
        request: (ComputeGlobalOperationsAggregatedListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (OperationAggregatedList) The response message.
      """
      config = self.GetMethodConfig('AggregatedList')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Deletes the specified operation resource.

      Args:
        request: (ComputeGlobalOperationsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ComputeGlobalOperationsDeleteResponse) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Retrieves the specified operation resource.

      Args:
        request: (ComputeGlobalOperationsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of operation resources contained within the specified project.

      Args:
        request: (ComputeGlobalOperationsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (OperationList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class HttpHealthChecksService(base_api.BaseApiService):
    """Service class for the httpHealthChecks resource."""

    _NAME = u'httpHealthChecks'

    def __init__(self, client):
      super(ComputeV1.HttpHealthChecksService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.httpHealthChecks.delete',
              ordered_params=[u'project', u'httpHealthCheck'],
              path_params=[u'httpHealthCheck', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/httpHealthChecks/{httpHealthCheck}',
              request_field='',
              request_type_name=u'ComputeHttpHealthChecksDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.httpHealthChecks.get',
              ordered_params=[u'project', u'httpHealthCheck'],
              path_params=[u'httpHealthCheck', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/httpHealthChecks/{httpHealthCheck}',
              request_field='',
              request_type_name=u'ComputeHttpHealthChecksGetRequest',
              response_type_name=u'HttpHealthCheck',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.httpHealthChecks.insert',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/httpHealthChecks',
              request_field=u'httpHealthCheck',
              request_type_name=u'ComputeHttpHealthChecksInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.httpHealthChecks.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/global/httpHealthChecks',
              request_field='',
              request_type_name=u'ComputeHttpHealthChecksListRequest',
              response_type_name=u'HttpHealthCheckList',
              supports_download=False,
          ),
          'Patch': base_api.ApiMethodInfo(
              http_method=u'PATCH',
              method_id=u'compute.httpHealthChecks.patch',
              ordered_params=[u'project', u'httpHealthCheck'],
              path_params=[u'httpHealthCheck', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/httpHealthChecks/{httpHealthCheck}',
              request_field=u'httpHealthCheckResource',
              request_type_name=u'ComputeHttpHealthChecksPatchRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Update': base_api.ApiMethodInfo(
              http_method=u'PUT',
              method_id=u'compute.httpHealthChecks.update',
              ordered_params=[u'project', u'httpHealthCheck'],
              path_params=[u'httpHealthCheck', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/httpHealthChecks/{httpHealthCheck}',
              request_field=u'httpHealthCheckResource',
              request_type_name=u'ComputeHttpHealthChecksUpdateRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified HttpHealthCheck resource.

      Args:
        request: (ComputeHttpHealthChecksDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified HttpHealthCheck resource.

      Args:
        request: (ComputeHttpHealthChecksGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (HttpHealthCheck) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates a HttpHealthCheck resource in the specified project using the data included in the request.

      Args:
        request: (ComputeHttpHealthChecksInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of HttpHealthCheck resources available to the specified project.

      Args:
        request: (ComputeHttpHealthChecksListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (HttpHealthCheckList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Patch(self, request, global_params=None):
      """Updates a HttpHealthCheck resource in the specified project using the data included in the request. This method supports patch semantics.

      Args:
        request: (ComputeHttpHealthChecksPatchRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Patch')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Update(self, request, global_params=None):
      """Updates a HttpHealthCheck resource in the specified project using the data included in the request.

      Args:
        request: (ComputeHttpHealthChecksUpdateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Update')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ImagesService(base_api.BaseApiService):
    """Service class for the images resource."""

    _NAME = u'images'

    def __init__(self, client):
      super(ComputeV1.ImagesService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.images.delete',
              ordered_params=[u'project', u'image'],
              path_params=[u'image', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/images/{image}',
              request_field='',
              request_type_name=u'ComputeImagesDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Deprecate': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.images.deprecate',
              ordered_params=[u'project', u'image'],
              path_params=[u'image', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/images/{image}/deprecate',
              request_field=u'deprecationStatus',
              request_type_name=u'ComputeImagesDeprecateRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.images.get',
              ordered_params=[u'project', u'image'],
              path_params=[u'image', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/images/{image}',
              request_field='',
              request_type_name=u'ComputeImagesGetRequest',
              response_type_name=u'Image',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.images.insert',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/images',
              request_field=u'image',
              request_type_name=u'ComputeImagesInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.images.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/global/images',
              request_field='',
              request_type_name=u'ComputeImagesListRequest',
              response_type_name=u'ImageList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified image resource.

      Args:
        request: (ComputeImagesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Deprecate(self, request, global_params=None):
      """Sets the deprecation status of an image. If no message body is given, clears the deprecation status instead.

      Args:
        request: (ComputeImagesDeprecateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Deprecate')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified image resource.

      Args:
        request: (ComputeImagesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Image) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates an image resource in the specified project using the data included in the request.

      Args:
        request: (ComputeImagesInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of image resources available to the specified project.

      Args:
        request: (ComputeImagesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ImageList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class InstanceTemplatesService(base_api.BaseApiService):
    """Service class for the instanceTemplates resource."""

    _NAME = u'instanceTemplates'

    def __init__(self, client):
      super(ComputeV1.InstanceTemplatesService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.instanceTemplates.delete',
              ordered_params=[u'project', u'instanceTemplate'],
              path_params=[u'instanceTemplate', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/instanceTemplates/{instanceTemplate}',
              request_field='',
              request_type_name=u'ComputeInstanceTemplatesDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.instanceTemplates.get',
              ordered_params=[u'project', u'instanceTemplate'],
              path_params=[u'instanceTemplate', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/instanceTemplates/{instanceTemplate}',
              request_field='',
              request_type_name=u'ComputeInstanceTemplatesGetRequest',
              response_type_name=u'InstanceTemplate',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.instanceTemplates.insert',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/instanceTemplates',
              request_field=u'instanceTemplate',
              request_type_name=u'ComputeInstanceTemplatesInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.instanceTemplates.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/global/instanceTemplates',
              request_field='',
              request_type_name=u'ComputeInstanceTemplatesListRequest',
              response_type_name=u'InstanceTemplateList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified instance template resource.

      Args:
        request: (ComputeInstanceTemplatesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified instance template resource.

      Args:
        request: (ComputeInstanceTemplatesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (InstanceTemplate) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates an instance template resource in the specified project using the data included in the request.

      Args:
        request: (ComputeInstanceTemplatesInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of instance template resources contained within the specified project.

      Args:
        request: (ComputeInstanceTemplatesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (InstanceTemplateList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class InstancesService(base_api.BaseApiService):
    """Service class for the instances resource."""

    _NAME = u'instances'

    def __init__(self, client):
      super(ComputeV1.InstancesService, self).__init__(client)
      self._method_configs = {
          'AddAccessConfig': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.instances.addAccessConfig',
              ordered_params=[u'project', u'zone', u'instance', u'networkInterface'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[u'networkInterface'],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}/addAccessConfig',
              request_field=u'accessConfig',
              request_type_name=u'ComputeInstancesAddAccessConfigRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'AggregatedList': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.instances.aggregatedList',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/aggregated/instances',
              request_field='',
              request_type_name=u'ComputeInstancesAggregatedListRequest',
              response_type_name=u'InstanceAggregatedList',
              supports_download=False,
          ),
          'AttachDisk': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.instances.attachDisk',
              ordered_params=[u'project', u'zone', u'instance'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}/attachDisk',
              request_field=u'attachedDisk',
              request_type_name=u'ComputeInstancesAttachDiskRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.instances.delete',
              ordered_params=[u'project', u'zone', u'instance'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}',
              request_field='',
              request_type_name=u'ComputeInstancesDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'DeleteAccessConfig': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.instances.deleteAccessConfig',
              ordered_params=[u'project', u'zone', u'instance', u'accessConfig', u'networkInterface'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[u'accessConfig', u'networkInterface'],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}/deleteAccessConfig',
              request_field='',
              request_type_name=u'ComputeInstancesDeleteAccessConfigRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'DetachDisk': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.instances.detachDisk',
              ordered_params=[u'project', u'zone', u'instance', u'deviceName'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[u'deviceName'],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}/detachDisk',
              request_field='',
              request_type_name=u'ComputeInstancesDetachDiskRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.instances.get',
              ordered_params=[u'project', u'zone', u'instance'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}',
              request_field='',
              request_type_name=u'ComputeInstancesGetRequest',
              response_type_name=u'Instance',
              supports_download=False,
          ),
          'GetSerialPortOutput': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.instances.getSerialPortOutput',
              ordered_params=[u'project', u'zone', u'instance'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}/serialPort',
              request_field='',
              request_type_name=u'ComputeInstancesGetSerialPortOutputRequest',
              response_type_name=u'SerialPortOutput',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.instances.insert',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instances',
              request_field=u'instance',
              request_type_name=u'ComputeInstancesInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.instances.list',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/zones/{zone}/instances',
              request_field='',
              request_type_name=u'ComputeInstancesListRequest',
              response_type_name=u'InstanceList',
              supports_download=False,
          ),
          'Reset': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.instances.reset',
              ordered_params=[u'project', u'zone', u'instance'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}/reset',
              request_field='',
              request_type_name=u'ComputeInstancesResetRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'SetDiskAutoDelete': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.instances.setDiskAutoDelete',
              ordered_params=[u'project', u'zone', u'instance', u'autoDelete', u'deviceName'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[u'autoDelete', u'deviceName'],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}/setDiskAutoDelete',
              request_field='',
              request_type_name=u'ComputeInstancesSetDiskAutoDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'SetMetadata': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.instances.setMetadata',
              ordered_params=[u'project', u'zone', u'instance'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}/setMetadata',
              request_field=u'metadata',
              request_type_name=u'ComputeInstancesSetMetadataRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'SetScheduling': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.instances.setScheduling',
              ordered_params=[u'project', u'zone', u'instance'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}/setScheduling',
              request_field=u'scheduling',
              request_type_name=u'ComputeInstancesSetSchedulingRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'SetTags': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.instances.setTags',
              ordered_params=[u'project', u'zone', u'instance'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}/setTags',
              request_field=u'tags',
              request_type_name=u'ComputeInstancesSetTagsRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Start': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.instances.start',
              ordered_params=[u'project', u'zone', u'instance'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}/start',
              request_field='',
              request_type_name=u'ComputeInstancesStartRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Stop': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.instances.stop',
              ordered_params=[u'project', u'zone', u'instance'],
              path_params=[u'instance', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instances/{instance}/stop',
              request_field='',
              request_type_name=u'ComputeInstancesStopRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def AddAccessConfig(self, request, global_params=None):
      """Adds an access config to an instance's network interface.

      Args:
        request: (ComputeInstancesAddAccessConfigRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('AddAccessConfig')
      return self._RunMethod(
          config, request, global_params=global_params)

    def AggregatedList(self, request, global_params=None):
      """AggregatedList method for the instances service.

      Args:
        request: (ComputeInstancesAggregatedListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (InstanceAggregatedList) The response message.
      """
      config = self.GetMethodConfig('AggregatedList')
      return self._RunMethod(
          config, request, global_params=global_params)

    def AttachDisk(self, request, global_params=None):
      """Attaches a disk resource to an instance.

      Args:
        request: (ComputeInstancesAttachDiskRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('AttachDisk')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Deletes the specified instance resource.

      Args:
        request: (ComputeInstancesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def DeleteAccessConfig(self, request, global_params=None):
      """Deletes an access config from an instance's network interface.

      Args:
        request: (ComputeInstancesDeleteAccessConfigRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('DeleteAccessConfig')
      return self._RunMethod(
          config, request, global_params=global_params)

    def DetachDisk(self, request, global_params=None):
      """Detaches a disk from an instance.

      Args:
        request: (ComputeInstancesDetachDiskRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('DetachDisk')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified instance resource.

      Args:
        request: (ComputeInstancesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Instance) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def GetSerialPortOutput(self, request, global_params=None):
      """Returns the specified instance's serial port output.

      Args:
        request: (ComputeInstancesGetSerialPortOutputRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (SerialPortOutput) The response message.
      """
      config = self.GetMethodConfig('GetSerialPortOutput')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates an instance resource in the specified project using the data included in the request.

      Args:
        request: (ComputeInstancesInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of instance resources contained within the specified zone.

      Args:
        request: (ComputeInstancesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (InstanceList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Reset(self, request, global_params=None):
      """Performs a hard reset on the instance.

      Args:
        request: (ComputeInstancesResetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Reset')
      return self._RunMethod(
          config, request, global_params=global_params)

    def SetDiskAutoDelete(self, request, global_params=None):
      """Sets the auto-delete flag for a disk attached to an instance.

      Args:
        request: (ComputeInstancesSetDiskAutoDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('SetDiskAutoDelete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def SetMetadata(self, request, global_params=None):
      """Sets metadata for the specified instance to the data included in the request.

      Args:
        request: (ComputeInstancesSetMetadataRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('SetMetadata')
      return self._RunMethod(
          config, request, global_params=global_params)

    def SetScheduling(self, request, global_params=None):
      """Sets an instance's scheduling options.

      Args:
        request: (ComputeInstancesSetSchedulingRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('SetScheduling')
      return self._RunMethod(
          config, request, global_params=global_params)

    def SetTags(self, request, global_params=None):
      """Sets tags for the specified instance to the data included in the request.

      Args:
        request: (ComputeInstancesSetTagsRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('SetTags')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Start(self, request, global_params=None):
      """Starts an instance.

      Args:
        request: (ComputeInstancesStartRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Start')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Stop(self, request, global_params=None):
      """Stops an instance.

      Args:
        request: (ComputeInstancesStopRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Stop')
      return self._RunMethod(
          config, request, global_params=global_params)

  class LicensesService(base_api.BaseApiService):
    """Service class for the licenses resource."""

    _NAME = u'licenses'

    def __init__(self, client):
      super(ComputeV1.LicensesService, self).__init__(client)
      self._method_configs = {
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.licenses.get',
              ordered_params=[u'project', u'license'],
              path_params=[u'license', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/licenses/{license}',
              request_field='',
              request_type_name=u'ComputeLicensesGetRequest',
              response_type_name=u'License',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Get(self, request, global_params=None):
      """Returns the specified license resource.

      Args:
        request: (ComputeLicensesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (License) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

  class MachineTypesService(base_api.BaseApiService):
    """Service class for the machineTypes resource."""

    _NAME = u'machineTypes'

    def __init__(self, client):
      super(ComputeV1.MachineTypesService, self).__init__(client)
      self._method_configs = {
          'AggregatedList': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.machineTypes.aggregatedList',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/aggregated/machineTypes',
              request_field='',
              request_type_name=u'ComputeMachineTypesAggregatedListRequest',
              response_type_name=u'MachineTypeAggregatedList',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.machineTypes.get',
              ordered_params=[u'project', u'zone', u'machineType'],
              path_params=[u'machineType', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/machineTypes/{machineType}',
              request_field='',
              request_type_name=u'ComputeMachineTypesGetRequest',
              response_type_name=u'MachineType',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.machineTypes.list',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/zones/{zone}/machineTypes',
              request_field='',
              request_type_name=u'ComputeMachineTypesListRequest',
              response_type_name=u'MachineTypeList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def AggregatedList(self, request, global_params=None):
      """Retrieves the list of machine type resources grouped by scope.

      Args:
        request: (ComputeMachineTypesAggregatedListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (MachineTypeAggregatedList) The response message.
      """
      config = self.GetMethodConfig('AggregatedList')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified machine type resource.

      Args:
        request: (ComputeMachineTypesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (MachineType) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of machine type resources available to the specified project.

      Args:
        request: (ComputeMachineTypesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (MachineTypeList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class NetworksService(base_api.BaseApiService):
    """Service class for the networks resource."""

    _NAME = u'networks'

    def __init__(self, client):
      super(ComputeV1.NetworksService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.networks.delete',
              ordered_params=[u'project', u'network'],
              path_params=[u'network', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/networks/{network}',
              request_field='',
              request_type_name=u'ComputeNetworksDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.networks.get',
              ordered_params=[u'project', u'network'],
              path_params=[u'network', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/networks/{network}',
              request_field='',
              request_type_name=u'ComputeNetworksGetRequest',
              response_type_name=u'Network',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.networks.insert',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/networks',
              request_field=u'network',
              request_type_name=u'ComputeNetworksInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.networks.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/global/networks',
              request_field='',
              request_type_name=u'ComputeNetworksListRequest',
              response_type_name=u'NetworkList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified network resource.

      Args:
        request: (ComputeNetworksDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified network resource.

      Args:
        request: (ComputeNetworksGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Network) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates a network resource in the specified project using the data included in the request.

      Args:
        request: (ComputeNetworksInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of network resources available to the specified project.

      Args:
        request: (ComputeNetworksListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (NetworkList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ProjectsService(base_api.BaseApiService):
    """Service class for the projects resource."""

    _NAME = u'projects'

    def __init__(self, client):
      super(ComputeV1.ProjectsService, self).__init__(client)
      self._method_configs = {
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.projects.get',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}',
              request_field='',
              request_type_name=u'ComputeProjectsGetRequest',
              response_type_name=u'Project',
              supports_download=False,
          ),
          'SetCommonInstanceMetadata': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.projects.setCommonInstanceMetadata',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/setCommonInstanceMetadata',
              request_field=u'metadata',
              request_type_name=u'ComputeProjectsSetCommonInstanceMetadataRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'SetUsageExportBucket': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.projects.setUsageExportBucket',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/setUsageExportBucket',
              request_field=u'usageExportLocation',
              request_type_name=u'ComputeProjectsSetUsageExportBucketRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Get(self, request, global_params=None):
      """Returns the specified project resource.

      Args:
        request: (ComputeProjectsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Project) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def SetCommonInstanceMetadata(self, request, global_params=None):
      """Sets metadata common to all instances within the specified project using the data included in the request.

      Args:
        request: (ComputeProjectsSetCommonInstanceMetadataRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('SetCommonInstanceMetadata')
      return self._RunMethod(
          config, request, global_params=global_params)

    def SetUsageExportBucket(self, request, global_params=None):
      """Sets usage export location.

      Args:
        request: (ComputeProjectsSetUsageExportBucketRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('SetUsageExportBucket')
      return self._RunMethod(
          config, request, global_params=global_params)

  class RegionOperationsService(base_api.BaseApiService):
    """Service class for the regionOperations resource."""

    _NAME = u'regionOperations'

    def __init__(self, client):
      super(ComputeV1.RegionOperationsService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.regionOperations.delete',
              ordered_params=[u'project', u'region', u'operation'],
              path_params=[u'operation', u'project', u'region'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/operations/{operation}',
              request_field='',
              request_type_name=u'ComputeRegionOperationsDeleteRequest',
              response_type_name=u'ComputeRegionOperationsDeleteResponse',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.regionOperations.get',
              ordered_params=[u'project', u'region', u'operation'],
              path_params=[u'operation', u'project', u'region'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/operations/{operation}',
              request_field='',
              request_type_name=u'ComputeRegionOperationsGetRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.regionOperations.list',
              ordered_params=[u'project', u'region'],
              path_params=[u'project', u'region'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/regions/{region}/operations',
              request_field='',
              request_type_name=u'ComputeRegionOperationsListRequest',
              response_type_name=u'OperationList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified region-specific operation resource.

      Args:
        request: (ComputeRegionOperationsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ComputeRegionOperationsDeleteResponse) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Retrieves the specified region-specific operation resource.

      Args:
        request: (ComputeRegionOperationsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of operation resources contained within the specified region.

      Args:
        request: (ComputeRegionOperationsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (OperationList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class RegionsService(base_api.BaseApiService):
    """Service class for the regions resource."""

    _NAME = u'regions'

    def __init__(self, client):
      super(ComputeV1.RegionsService, self).__init__(client)
      self._method_configs = {
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.regions.get',
              ordered_params=[u'project', u'region'],
              path_params=[u'project', u'region'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}',
              request_field='',
              request_type_name=u'ComputeRegionsGetRequest',
              response_type_name=u'Region',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.regions.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/regions',
              request_field='',
              request_type_name=u'ComputeRegionsListRequest',
              response_type_name=u'RegionList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Get(self, request, global_params=None):
      """Returns the specified region resource.

      Args:
        request: (ComputeRegionsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Region) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of region resources available to the specified project.

      Args:
        request: (ComputeRegionsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (RegionList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class RoutesService(base_api.BaseApiService):
    """Service class for the routes resource."""

    _NAME = u'routes'

    def __init__(self, client):
      super(ComputeV1.RoutesService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.routes.delete',
              ordered_params=[u'project', u'route'],
              path_params=[u'project', u'route'],
              query_params=[],
              relative_path=u'projects/{project}/global/routes/{route}',
              request_field='',
              request_type_name=u'ComputeRoutesDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.routes.get',
              ordered_params=[u'project', u'route'],
              path_params=[u'project', u'route'],
              query_params=[],
              relative_path=u'projects/{project}/global/routes/{route}',
              request_field='',
              request_type_name=u'ComputeRoutesGetRequest',
              response_type_name=u'Route',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.routes.insert',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/routes',
              request_field=u'route',
              request_type_name=u'ComputeRoutesInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.routes.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/global/routes',
              request_field='',
              request_type_name=u'ComputeRoutesListRequest',
              response_type_name=u'RouteList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified route resource.

      Args:
        request: (ComputeRoutesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified route resource.

      Args:
        request: (ComputeRoutesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Route) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates a route resource in the specified project using the data included in the request.

      Args:
        request: (ComputeRoutesInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of route resources available to the specified project.

      Args:
        request: (ComputeRoutesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (RouteList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class SnapshotsService(base_api.BaseApiService):
    """Service class for the snapshots resource."""

    _NAME = u'snapshots'

    def __init__(self, client):
      super(ComputeV1.SnapshotsService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.snapshots.delete',
              ordered_params=[u'project', u'snapshot'],
              path_params=[u'project', u'snapshot'],
              query_params=[],
              relative_path=u'projects/{project}/global/snapshots/{snapshot}',
              request_field='',
              request_type_name=u'ComputeSnapshotsDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.snapshots.get',
              ordered_params=[u'project', u'snapshot'],
              path_params=[u'project', u'snapshot'],
              query_params=[],
              relative_path=u'projects/{project}/global/snapshots/{snapshot}',
              request_field='',
              request_type_name=u'ComputeSnapshotsGetRequest',
              response_type_name=u'Snapshot',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.snapshots.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/global/snapshots',
              request_field='',
              request_type_name=u'ComputeSnapshotsListRequest',
              response_type_name=u'SnapshotList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified persistent disk snapshot resource.

      Args:
        request: (ComputeSnapshotsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified persistent disk snapshot resource.

      Args:
        request: (ComputeSnapshotsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Snapshot) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of persistent disk snapshot resources contained within the specified project.

      Args:
        request: (ComputeSnapshotsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (SnapshotList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class TargetHttpProxiesService(base_api.BaseApiService):
    """Service class for the targetHttpProxies resource."""

    _NAME = u'targetHttpProxies'

    def __init__(self, client):
      super(ComputeV1.TargetHttpProxiesService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.targetHttpProxies.delete',
              ordered_params=[u'project', u'targetHttpProxy'],
              path_params=[u'project', u'targetHttpProxy'],
              query_params=[],
              relative_path=u'projects/{project}/global/targetHttpProxies/{targetHttpProxy}',
              request_field='',
              request_type_name=u'ComputeTargetHttpProxiesDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.targetHttpProxies.get',
              ordered_params=[u'project', u'targetHttpProxy'],
              path_params=[u'project', u'targetHttpProxy'],
              query_params=[],
              relative_path=u'projects/{project}/global/targetHttpProxies/{targetHttpProxy}',
              request_field='',
              request_type_name=u'ComputeTargetHttpProxiesGetRequest',
              response_type_name=u'TargetHttpProxy',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.targetHttpProxies.insert',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/targetHttpProxies',
              request_field=u'targetHttpProxy',
              request_type_name=u'ComputeTargetHttpProxiesInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.targetHttpProxies.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/global/targetHttpProxies',
              request_field='',
              request_type_name=u'ComputeTargetHttpProxiesListRequest',
              response_type_name=u'TargetHttpProxyList',
              supports_download=False,
          ),
          'SetUrlMap': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.targetHttpProxies.setUrlMap',
              ordered_params=[u'project', u'targetHttpProxy'],
              path_params=[u'project', u'targetHttpProxy'],
              query_params=[],
              relative_path=u'projects/{project}/targetHttpProxies/{targetHttpProxy}/setUrlMap',
              request_field=u'urlMapReference',
              request_type_name=u'ComputeTargetHttpProxiesSetUrlMapRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified TargetHttpProxy resource.

      Args:
        request: (ComputeTargetHttpProxiesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified TargetHttpProxy resource.

      Args:
        request: (ComputeTargetHttpProxiesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TargetHttpProxy) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates a TargetHttpProxy resource in the specified project using the data included in the request.

      Args:
        request: (ComputeTargetHttpProxiesInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of TargetHttpProxy resources available to the specified project.

      Args:
        request: (ComputeTargetHttpProxiesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TargetHttpProxyList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def SetUrlMap(self, request, global_params=None):
      """Changes the URL map for TargetHttpProxy.

      Args:
        request: (ComputeTargetHttpProxiesSetUrlMapRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('SetUrlMap')
      return self._RunMethod(
          config, request, global_params=global_params)

  class TargetInstancesService(base_api.BaseApiService):
    """Service class for the targetInstances resource."""

    _NAME = u'targetInstances'

    def __init__(self, client):
      super(ComputeV1.TargetInstancesService, self).__init__(client)
      self._method_configs = {
          'AggregatedList': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.targetInstances.aggregatedList',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/aggregated/targetInstances',
              request_field='',
              request_type_name=u'ComputeTargetInstancesAggregatedListRequest',
              response_type_name=u'TargetInstanceAggregatedList',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.targetInstances.delete',
              ordered_params=[u'project', u'zone', u'targetInstance'],
              path_params=[u'project', u'targetInstance', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/targetInstances/{targetInstance}',
              request_field='',
              request_type_name=u'ComputeTargetInstancesDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.targetInstances.get',
              ordered_params=[u'project', u'zone', u'targetInstance'],
              path_params=[u'project', u'targetInstance', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/targetInstances/{targetInstance}',
              request_field='',
              request_type_name=u'ComputeTargetInstancesGetRequest',
              response_type_name=u'TargetInstance',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.targetInstances.insert',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/targetInstances',
              request_field=u'targetInstance',
              request_type_name=u'ComputeTargetInstancesInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.targetInstances.list',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/zones/{zone}/targetInstances',
              request_field='',
              request_type_name=u'ComputeTargetInstancesListRequest',
              response_type_name=u'TargetInstanceList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def AggregatedList(self, request, global_params=None):
      """Retrieves the list of target instances grouped by scope.

      Args:
        request: (ComputeTargetInstancesAggregatedListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TargetInstanceAggregatedList) The response message.
      """
      config = self.GetMethodConfig('AggregatedList')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Deletes the specified TargetInstance resource.

      Args:
        request: (ComputeTargetInstancesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified TargetInstance resource.

      Args:
        request: (ComputeTargetInstancesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TargetInstance) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates a TargetInstance resource in the specified project and zone using the data included in the request.

      Args:
        request: (ComputeTargetInstancesInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of TargetInstance resources available to the specified project and zone.

      Args:
        request: (ComputeTargetInstancesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TargetInstanceList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class TargetPoolsService(base_api.BaseApiService):
    """Service class for the targetPools resource."""

    _NAME = u'targetPools'

    def __init__(self, client):
      super(ComputeV1.TargetPoolsService, self).__init__(client)
      self._method_configs = {
          'AddHealthCheck': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.targetPools.addHealthCheck',
              ordered_params=[u'project', u'region', u'targetPool'],
              path_params=[u'project', u'region', u'targetPool'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/targetPools/{targetPool}/addHealthCheck',
              request_field=u'targetPoolsAddHealthCheckRequest',
              request_type_name=u'ComputeTargetPoolsAddHealthCheckRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'AddInstance': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.targetPools.addInstance',
              ordered_params=[u'project', u'region', u'targetPool'],
              path_params=[u'project', u'region', u'targetPool'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/targetPools/{targetPool}/addInstance',
              request_field=u'targetPoolsAddInstanceRequest',
              request_type_name=u'ComputeTargetPoolsAddInstanceRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'AggregatedList': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.targetPools.aggregatedList',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/aggregated/targetPools',
              request_field='',
              request_type_name=u'ComputeTargetPoolsAggregatedListRequest',
              response_type_name=u'TargetPoolAggregatedList',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.targetPools.delete',
              ordered_params=[u'project', u'region', u'targetPool'],
              path_params=[u'project', u'region', u'targetPool'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/targetPools/{targetPool}',
              request_field='',
              request_type_name=u'ComputeTargetPoolsDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.targetPools.get',
              ordered_params=[u'project', u'region', u'targetPool'],
              path_params=[u'project', u'region', u'targetPool'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/targetPools/{targetPool}',
              request_field='',
              request_type_name=u'ComputeTargetPoolsGetRequest',
              response_type_name=u'TargetPool',
              supports_download=False,
          ),
          'GetHealth': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.targetPools.getHealth',
              ordered_params=[u'project', u'region', u'targetPool'],
              path_params=[u'project', u'region', u'targetPool'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/targetPools/{targetPool}/getHealth',
              request_field=u'instanceReference',
              request_type_name=u'ComputeTargetPoolsGetHealthRequest',
              response_type_name=u'TargetPoolInstanceHealth',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.targetPools.insert',
              ordered_params=[u'project', u'region'],
              path_params=[u'project', u'region'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/targetPools',
              request_field=u'targetPool',
              request_type_name=u'ComputeTargetPoolsInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.targetPools.list',
              ordered_params=[u'project', u'region'],
              path_params=[u'project', u'region'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/regions/{region}/targetPools',
              request_field='',
              request_type_name=u'ComputeTargetPoolsListRequest',
              response_type_name=u'TargetPoolList',
              supports_download=False,
          ),
          'RemoveHealthCheck': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.targetPools.removeHealthCheck',
              ordered_params=[u'project', u'region', u'targetPool'],
              path_params=[u'project', u'region', u'targetPool'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/targetPools/{targetPool}/removeHealthCheck',
              request_field=u'targetPoolsRemoveHealthCheckRequest',
              request_type_name=u'ComputeTargetPoolsRemoveHealthCheckRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'RemoveInstance': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.targetPools.removeInstance',
              ordered_params=[u'project', u'region', u'targetPool'],
              path_params=[u'project', u'region', u'targetPool'],
              query_params=[],
              relative_path=u'projects/{project}/regions/{region}/targetPools/{targetPool}/removeInstance',
              request_field=u'targetPoolsRemoveInstanceRequest',
              request_type_name=u'ComputeTargetPoolsRemoveInstanceRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'SetBackup': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.targetPools.setBackup',
              ordered_params=[u'project', u'region', u'targetPool'],
              path_params=[u'project', u'region', u'targetPool'],
              query_params=[u'failoverRatio'],
              relative_path=u'projects/{project}/regions/{region}/targetPools/{targetPool}/setBackup',
              request_field=u'targetReference',
              request_type_name=u'ComputeTargetPoolsSetBackupRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def AddHealthCheck(self, request, global_params=None):
      """Adds health check URL to targetPool.

      Args:
        request: (ComputeTargetPoolsAddHealthCheckRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('AddHealthCheck')
      return self._RunMethod(
          config, request, global_params=global_params)

    def AddInstance(self, request, global_params=None):
      """Adds instance url to targetPool.

      Args:
        request: (ComputeTargetPoolsAddInstanceRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('AddInstance')
      return self._RunMethod(
          config, request, global_params=global_params)

    def AggregatedList(self, request, global_params=None):
      """Retrieves the list of target pools grouped by scope.

      Args:
        request: (ComputeTargetPoolsAggregatedListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TargetPoolAggregatedList) The response message.
      """
      config = self.GetMethodConfig('AggregatedList')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Deletes the specified TargetPool resource.

      Args:
        request: (ComputeTargetPoolsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified TargetPool resource.

      Args:
        request: (ComputeTargetPoolsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TargetPool) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def GetHealth(self, request, global_params=None):
      """Gets the most recent health check results for each IP for the given instance that is referenced by given TargetPool.

      Args:
        request: (ComputeTargetPoolsGetHealthRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TargetPoolInstanceHealth) The response message.
      """
      config = self.GetMethodConfig('GetHealth')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates a TargetPool resource in the specified project and region using the data included in the request.

      Args:
        request: (ComputeTargetPoolsInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of TargetPool resources available to the specified project and region.

      Args:
        request: (ComputeTargetPoolsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TargetPoolList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def RemoveHealthCheck(self, request, global_params=None):
      """Removes health check URL from targetPool.

      Args:
        request: (ComputeTargetPoolsRemoveHealthCheckRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('RemoveHealthCheck')
      return self._RunMethod(
          config, request, global_params=global_params)

    def RemoveInstance(self, request, global_params=None):
      """Removes instance URL from targetPool.

      Args:
        request: (ComputeTargetPoolsRemoveInstanceRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('RemoveInstance')
      return self._RunMethod(
          config, request, global_params=global_params)

    def SetBackup(self, request, global_params=None):
      """Changes backup pool configurations.

      Args:
        request: (ComputeTargetPoolsSetBackupRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('SetBackup')
      return self._RunMethod(
          config, request, global_params=global_params)

  class UrlMapsService(base_api.BaseApiService):
    """Service class for the urlMaps resource."""

    _NAME = u'urlMaps'

    def __init__(self, client):
      super(ComputeV1.UrlMapsService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.urlMaps.delete',
              ordered_params=[u'project', u'urlMap'],
              path_params=[u'project', u'urlMap'],
              query_params=[],
              relative_path=u'projects/{project}/global/urlMaps/{urlMap}',
              request_field='',
              request_type_name=u'ComputeUrlMapsDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.urlMaps.get',
              ordered_params=[u'project', u'urlMap'],
              path_params=[u'project', u'urlMap'],
              query_params=[],
              relative_path=u'projects/{project}/global/urlMaps/{urlMap}',
              request_field='',
              request_type_name=u'ComputeUrlMapsGetRequest',
              response_type_name=u'UrlMap',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.urlMaps.insert',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/global/urlMaps',
              request_field=u'urlMap',
              request_type_name=u'ComputeUrlMapsInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.urlMaps.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/global/urlMaps',
              request_field='',
              request_type_name=u'ComputeUrlMapsListRequest',
              response_type_name=u'UrlMapList',
              supports_download=False,
          ),
          'Patch': base_api.ApiMethodInfo(
              http_method=u'PATCH',
              method_id=u'compute.urlMaps.patch',
              ordered_params=[u'project', u'urlMap'],
              path_params=[u'project', u'urlMap'],
              query_params=[],
              relative_path=u'projects/{project}/global/urlMaps/{urlMap}',
              request_field=u'urlMapResource',
              request_type_name=u'ComputeUrlMapsPatchRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Update': base_api.ApiMethodInfo(
              http_method=u'PUT',
              method_id=u'compute.urlMaps.update',
              ordered_params=[u'project', u'urlMap'],
              path_params=[u'project', u'urlMap'],
              query_params=[],
              relative_path=u'projects/{project}/global/urlMaps/{urlMap}',
              request_field=u'urlMapResource',
              request_type_name=u'ComputeUrlMapsUpdateRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Validate': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'compute.urlMaps.validate',
              ordered_params=[u'project', u'urlMap'],
              path_params=[u'project', u'urlMap'],
              query_params=[],
              relative_path=u'projects/{project}/global/urlMaps/{urlMap}/validate',
              request_field=u'urlMapsValidateRequest',
              request_type_name=u'ComputeUrlMapsValidateRequest',
              response_type_name=u'UrlMapsValidateResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified UrlMap resource.

      Args:
        request: (ComputeUrlMapsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified UrlMap resource.

      Args:
        request: (ComputeUrlMapsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (UrlMap) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates a UrlMap resource in the specified project using the data included in the request.

      Args:
        request: (ComputeUrlMapsInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of UrlMap resources available to the specified project.

      Args:
        request: (ComputeUrlMapsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (UrlMapList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Patch(self, request, global_params=None):
      """Update the entire content of the UrlMap resource. This method supports patch semantics.

      Args:
        request: (ComputeUrlMapsPatchRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Patch')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Update(self, request, global_params=None):
      """Update the entire content of the UrlMap resource.

      Args:
        request: (ComputeUrlMapsUpdateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Update')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Validate(self, request, global_params=None):
      """Run static validation for the UrlMap. In particular, the tests of the provided UrlMap will be run. Calling this method does NOT create the UrlMap.

      Args:
        request: (ComputeUrlMapsValidateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (UrlMapsValidateResponse) The response message.
      """
      config = self.GetMethodConfig('Validate')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ZoneOperationsService(base_api.BaseApiService):
    """Service class for the zoneOperations resource."""

    _NAME = u'zoneOperations'

    def __init__(self, client):
      super(ComputeV1.ZoneOperationsService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'compute.zoneOperations.delete',
              ordered_params=[u'project', u'zone', u'operation'],
              path_params=[u'operation', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/operations/{operation}',
              request_field='',
              request_type_name=u'ComputeZoneOperationsDeleteRequest',
              response_type_name=u'ComputeZoneOperationsDeleteResponse',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.zoneOperations.get',
              ordered_params=[u'project', u'zone', u'operation'],
              path_params=[u'operation', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/operations/{operation}',
              request_field='',
              request_type_name=u'ComputeZoneOperationsGetRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.zoneOperations.list',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/zones/{zone}/operations',
              request_field='',
              request_type_name=u'ComputeZoneOperationsListRequest',
              response_type_name=u'OperationList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified zone-specific operation resource.

      Args:
        request: (ComputeZoneOperationsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ComputeZoneOperationsDeleteResponse) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Retrieves the specified zone-specific operation resource.

      Args:
        request: (ComputeZoneOperationsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of operation resources contained within the specified zone.

      Args:
        request: (ComputeZoneOperationsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (OperationList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ZonesService(base_api.BaseApiService):
    """Service class for the zones resource."""

    _NAME = u'zones'

    def __init__(self, client):
      super(ComputeV1.ZonesService, self).__init__(client)
      self._method_configs = {
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.zones.get',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}',
              request_field='',
              request_type_name=u'ComputeZonesGetRequest',
              response_type_name=u'Zone',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'compute.zones.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/zones',
              request_field='',
              request_type_name=u'ComputeZonesListRequest',
              response_type_name=u'ZoneList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Get(self, request, global_params=None):
      """Returns the specified zone resource.

      Args:
        request: (ComputeZonesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Zone) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of zone resources available to the specified project.

      Args:
        request: (ComputeZonesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ZoneList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)
