"""Generated client library for resourceviews version v1beta1."""

from googlecloudapis.apitools.base.py import base_api
from googlecloudapis.resourceviews.v1beta1 import resourceviews_v1beta1_messages as messages


class ResourceviewsV1beta1(base_api.BaseApiClient):
  """Generated client library for service resourceviews version v1beta1."""

  MESSAGES_MODULE = messages

  _PACKAGE = u'resourceviews'
  _SCOPES = [u'https://www.googleapis.com/auth/cloud-platform', u'https://www.googleapis.com/auth/compute', u'https://www.googleapis.com/auth/compute.readonly', u'https://www.googleapis.com/auth/ndev.cloudman', u'https://www.googleapis.com/auth/ndev.cloudman.readonly']
  _VERSION = u'v1beta1'
  _CLIENT_ID = ''
  _CLIENT_SECRET = ''
  _USER_AGENT = ''
  _CLIENT_CLASS_NAME = u'ResourceviewsV1beta1'
  _URL_VERSION = u'v1beta1'

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new resourceviews handle."""
    url = url or u'https://www.googleapis.com/resourceviews/v1beta1/'
    super(ResourceviewsV1beta1, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.regionViews = self.RegionViewsService(self)
    self.zoneViews = self.ZoneViewsService(self)

  class RegionViewsService(base_api.BaseApiService):
    """Service class for the regionViews resource."""

    _NAME = u'regionViews'

    def __init__(self, client):
      super(ResourceviewsV1beta1.RegionViewsService, self).__init__(client)
      self._method_configs = {
          'Addresources': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'resourceviews.regionViews.addresources',
              ordered_params=[u'projectName', u'region', u'resourceViewName'],
              path_params=[u'projectName', u'region', u'resourceViewName'],
              query_params=[],
              relative_path=u'projects/{projectName}/regions/{region}/resourceViews/{resourceViewName}/addResources',
              request_field=u'regionViewsAddResourcesRequest',
              request_type_name=u'ResourceviewsRegionViewsAddresourcesRequest',
              response_type_name=u'ResourceviewsRegionViewsAddresourcesResponse',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'resourceviews.regionViews.delete',
              ordered_params=[u'projectName', u'region', u'resourceViewName'],
              path_params=[u'projectName', u'region', u'resourceViewName'],
              query_params=[],
              relative_path=u'projects/{projectName}/regions/{region}/resourceViews/{resourceViewName}',
              request_field='',
              request_type_name=u'ResourceviewsRegionViewsDeleteRequest',
              response_type_name=u'ResourceviewsRegionViewsDeleteResponse',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'resourceviews.regionViews.get',
              ordered_params=[u'projectName', u'region', u'resourceViewName'],
              path_params=[u'projectName', u'region', u'resourceViewName'],
              query_params=[],
              relative_path=u'projects/{projectName}/regions/{region}/resourceViews/{resourceViewName}',
              request_field='',
              request_type_name=u'ResourceviewsRegionViewsGetRequest',
              response_type_name=u'ResourceView',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'resourceviews.regionViews.insert',
              ordered_params=[u'projectName', u'region'],
              path_params=[u'projectName', u'region'],
              query_params=[],
              relative_path=u'projects/{projectName}/regions/{region}/resourceViews',
              request_field=u'resourceView',
              request_type_name=u'ResourceviewsRegionViewsInsertRequest',
              response_type_name=u'RegionViewsInsertResponse',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'resourceviews.regionViews.list',
              ordered_params=[u'projectName', u'region'],
              path_params=[u'projectName', u'region'],
              query_params=[u'maxResults', u'pageToken'],
              relative_path=u'projects/{projectName}/regions/{region}/resourceViews',
              request_field='',
              request_type_name=u'ResourceviewsRegionViewsListRequest',
              response_type_name=u'RegionViewsListResponse',
              supports_download=False,
          ),
          'Listresources': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'resourceviews.regionViews.listresources',
              ordered_params=[u'projectName', u'region', u'resourceViewName'],
              path_params=[u'projectName', u'region', u'resourceViewName'],
              query_params=[u'maxResults', u'pageToken'],
              relative_path=u'projects/{projectName}/regions/{region}/resourceViews/{resourceViewName}/resources',
              request_field='',
              request_type_name=u'ResourceviewsRegionViewsListresourcesRequest',
              response_type_name=u'RegionViewsListResourcesResponse',
              supports_download=False,
          ),
          'Removeresources': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'resourceviews.regionViews.removeresources',
              ordered_params=[u'projectName', u'region', u'resourceViewName'],
              path_params=[u'projectName', u'region', u'resourceViewName'],
              query_params=[],
              relative_path=u'projects/{projectName}/regions/{region}/resourceViews/{resourceViewName}/removeResources',
              request_field=u'regionViewsRemoveResourcesRequest',
              request_type_name=u'ResourceviewsRegionViewsRemoveresourcesRequest',
              response_type_name=u'ResourceviewsRegionViewsRemoveresourcesResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Addresources(self, request, global_params=None):
      """Add resources to the view.

      Args:
        request: (ResourceviewsRegionViewsAddresourcesRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ResourceviewsRegionViewsAddresourcesResponse) The response message.
      """
      config = self.GetMethodConfig('Addresources')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Delete a resource view.

      Args:
        request: (ResourceviewsRegionViewsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ResourceviewsRegionViewsDeleteResponse) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Get the information of a resource view.

      Args:
        request: (ResourceviewsRegionViewsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ResourceView) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Create a resource view.

      Args:
        request: (ResourceviewsRegionViewsInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (RegionViewsInsertResponse) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """List resource views.

      Args:
        request: (ResourceviewsRegionViewsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (RegionViewsListResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Listresources(self, request, global_params=None):
      """List the resources in the view.

      Args:
        request: (ResourceviewsRegionViewsListresourcesRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (RegionViewsListResourcesResponse) The response message.
      """
      config = self.GetMethodConfig('Listresources')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Removeresources(self, request, global_params=None):
      """Remove resources from the view.

      Args:
        request: (ResourceviewsRegionViewsRemoveresourcesRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ResourceviewsRegionViewsRemoveresourcesResponse) The response message.
      """
      config = self.GetMethodConfig('Removeresources')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ZoneViewsService(base_api.BaseApiService):
    """Service class for the zoneViews resource."""

    _NAME = u'zoneViews'

    def __init__(self, client):
      super(ResourceviewsV1beta1.ZoneViewsService, self).__init__(client)
      self._method_configs = {
          'Addresources': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'resourceviews.zoneViews.addresources',
              ordered_params=[u'projectName', u'zone', u'resourceViewName'],
              path_params=[u'projectName', u'resourceViewName', u'zone'],
              query_params=[],
              relative_path=u'projects/{projectName}/zones/{zone}/resourceViews/{resourceViewName}/addResources',
              request_field=u'zoneViewsAddResourcesRequest',
              request_type_name=u'ResourceviewsZoneViewsAddresourcesRequest',
              response_type_name=u'ResourceviewsZoneViewsAddresourcesResponse',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'resourceviews.zoneViews.delete',
              ordered_params=[u'projectName', u'zone', u'resourceViewName'],
              path_params=[u'projectName', u'resourceViewName', u'zone'],
              query_params=[],
              relative_path=u'projects/{projectName}/zones/{zone}/resourceViews/{resourceViewName}',
              request_field='',
              request_type_name=u'ResourceviewsZoneViewsDeleteRequest',
              response_type_name=u'ResourceviewsZoneViewsDeleteResponse',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'resourceviews.zoneViews.get',
              ordered_params=[u'projectName', u'zone', u'resourceViewName'],
              path_params=[u'projectName', u'resourceViewName', u'zone'],
              query_params=[],
              relative_path=u'projects/{projectName}/zones/{zone}/resourceViews/{resourceViewName}',
              request_field='',
              request_type_name=u'ResourceviewsZoneViewsGetRequest',
              response_type_name=u'ResourceView',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'resourceviews.zoneViews.insert',
              ordered_params=[u'projectName', u'zone'],
              path_params=[u'projectName', u'zone'],
              query_params=[],
              relative_path=u'projects/{projectName}/zones/{zone}/resourceViews',
              request_field=u'resourceView',
              request_type_name=u'ResourceviewsZoneViewsInsertRequest',
              response_type_name=u'ZoneViewsInsertResponse',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'resourceviews.zoneViews.list',
              ordered_params=[u'projectName', u'zone'],
              path_params=[u'projectName', u'zone'],
              query_params=[u'maxResults', u'pageToken'],
              relative_path=u'projects/{projectName}/zones/{zone}/resourceViews',
              request_field='',
              request_type_name=u'ResourceviewsZoneViewsListRequest',
              response_type_name=u'ZoneViewsListResponse',
              supports_download=False,
          ),
          'Listresources': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'resourceviews.zoneViews.listresources',
              ordered_params=[u'projectName', u'zone', u'resourceViewName'],
              path_params=[u'projectName', u'resourceViewName', u'zone'],
              query_params=[u'maxResults', u'pageToken'],
              relative_path=u'projects/{projectName}/zones/{zone}/resourceViews/{resourceViewName}/resources',
              request_field='',
              request_type_name=u'ResourceviewsZoneViewsListresourcesRequest',
              response_type_name=u'ZoneViewsListResourcesResponse',
              supports_download=False,
          ),
          'Removeresources': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'resourceviews.zoneViews.removeresources',
              ordered_params=[u'projectName', u'zone', u'resourceViewName'],
              path_params=[u'projectName', u'resourceViewName', u'zone'],
              query_params=[],
              relative_path=u'projects/{projectName}/zones/{zone}/resourceViews/{resourceViewName}/removeResources',
              request_field=u'zoneViewsRemoveResourcesRequest',
              request_type_name=u'ResourceviewsZoneViewsRemoveresourcesRequest',
              response_type_name=u'ResourceviewsZoneViewsRemoveresourcesResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Addresources(self, request, global_params=None):
      """Add resources to the view.

      Args:
        request: (ResourceviewsZoneViewsAddresourcesRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ResourceviewsZoneViewsAddresourcesResponse) The response message.
      """
      config = self.GetMethodConfig('Addresources')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Delete a resource view.

      Args:
        request: (ResourceviewsZoneViewsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ResourceviewsZoneViewsDeleteResponse) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Get the information of a zonal resource view.

      Args:
        request: (ResourceviewsZoneViewsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ResourceView) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Create a resource view.

      Args:
        request: (ResourceviewsZoneViewsInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ZoneViewsInsertResponse) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """List resource views.

      Args:
        request: (ResourceviewsZoneViewsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ZoneViewsListResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Listresources(self, request, global_params=None):
      """List the resources of the resource view.

      Args:
        request: (ResourceviewsZoneViewsListresourcesRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ZoneViewsListResourcesResponse) The response message.
      """
      config = self.GetMethodConfig('Listresources')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Removeresources(self, request, global_params=None):
      """Remove resources from the view.

      Args:
        request: (ResourceviewsZoneViewsRemoveresourcesRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ResourceviewsZoneViewsRemoveresourcesResponse) The response message.
      """
      config = self.GetMethodConfig('Removeresources')
      return self._RunMethod(
          config, request, global_params=global_params)
