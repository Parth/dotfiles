"""Generated client library for autoscaler version v1beta2."""

from googlecloudapis.apitools.base.py import base_api
from googlecloudapis.autoscaler.v1beta2 import autoscaler_v1beta2_messages as messages


class AutoscalerV1beta2(base_api.BaseApiClient):
  """Generated client library for service autoscaler version v1beta2."""

  MESSAGES_MODULE = messages

  _PACKAGE = u'autoscaler'
  _SCOPES = [u'https://www.googleapis.com/auth/compute', u'https://www.googleapis.com/auth/compute.readonly']
  _VERSION = u'v1beta2'
  _CLIENT_ID = ''
  _CLIENT_SECRET = ''
  _USER_AGENT = ''
  _CLIENT_CLASS_NAME = u'AutoscalerV1beta2'
  _URL_VERSION = u'v1beta2'

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new autoscaler handle."""
    url = url or u'https://www.googleapis.com/autoscaler/v1beta2/'
    super(AutoscalerV1beta2, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.autoscalers = self.AutoscalersService(self)
    self.zoneOperations = self.ZoneOperationsService(self)
    self.zones = self.ZonesService(self)

  class AutoscalersService(base_api.BaseApiService):
    """Service class for the autoscalers resource."""

    _NAME = u'autoscalers'

    def __init__(self, client):
      super(AutoscalerV1beta2.AutoscalersService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'autoscaler.autoscalers.delete',
              ordered_params=[u'project', u'zone', u'autoscaler'],
              path_params=[u'autoscaler', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/autoscalers/{autoscaler}',
              request_field='',
              request_type_name=u'AutoscalerAutoscalersDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'autoscaler.autoscalers.get',
              ordered_params=[u'project', u'zone', u'autoscaler'],
              path_params=[u'autoscaler', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/autoscalers/{autoscaler}',
              request_field='',
              request_type_name=u'AutoscalerAutoscalersGetRequest',
              response_type_name=u'Autoscaler',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'autoscaler.autoscalers.insert',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/autoscalers',
              request_field=u'autoscaler',
              request_type_name=u'AutoscalerAutoscalersInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'autoscaler.autoscalers.list',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/zones/{zone}/autoscalers',
              request_field='',
              request_type_name=u'AutoscalerAutoscalersListRequest',
              response_type_name=u'AutoscalerListResponse',
              supports_download=False,
          ),
          'Patch': base_api.ApiMethodInfo(
              http_method=u'PATCH',
              method_id=u'autoscaler.autoscalers.patch',
              ordered_params=[u'project', u'zone', u'autoscaler'],
              path_params=[u'autoscaler', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/autoscalers/{autoscaler}',
              request_field=u'autoscalerResource',
              request_type_name=u'AutoscalerAutoscalersPatchRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Update': base_api.ApiMethodInfo(
              http_method=u'PUT',
              method_id=u'autoscaler.autoscalers.update',
              ordered_params=[u'project', u'zone', u'autoscaler'],
              path_params=[u'autoscaler', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/autoscalers/{autoscaler}',
              request_field=u'autoscalerResource',
              request_type_name=u'AutoscalerAutoscalersUpdateRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified Autoscaler resource.

      Args:
        request: (AutoscalerAutoscalersDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Gets the specified Autoscaler resource.

      Args:
        request: (AutoscalerAutoscalersGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Autoscaler) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Adds new Autoscaler resource.

      Args:
        request: (AutoscalerAutoscalersInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Lists all Autoscaler resources in this zone.

      Args:
        request: (AutoscalerAutoscalersListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (AutoscalerListResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Patch(self, request, global_params=None):
      """Update the entire content of the Autoscaler resource. This method supports patch semantics.

      Args:
        request: (AutoscalerAutoscalersPatchRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Patch')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Update(self, request, global_params=None):
      """Update the entire content of the Autoscaler resource.

      Args:
        request: (AutoscalerAutoscalersUpdateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Update')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ZoneOperationsService(base_api.BaseApiService):
    """Service class for the zoneOperations resource."""

    _NAME = u'zoneOperations'

    def __init__(self, client):
      super(AutoscalerV1beta2.ZoneOperationsService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'autoscaler.zoneOperations.delete',
              ordered_params=[u'project', u'zone', u'operation'],
              path_params=[u'operation', u'project', u'zone'],
              query_params=[],
              relative_path=u'{project}/zones/{zone}/operations/{operation}',
              request_field='',
              request_type_name=u'AutoscalerZoneOperationsDeleteRequest',
              response_type_name=u'AutoscalerZoneOperationsDeleteResponse',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'autoscaler.zoneOperations.get',
              ordered_params=[u'project', u'zone', u'operation'],
              path_params=[u'operation', u'project', u'zone'],
              query_params=[],
              relative_path=u'{project}/zones/{zone}/operations/{operation}',
              request_field='',
              request_type_name=u'AutoscalerZoneOperationsGetRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'autoscaler.zoneOperations.list',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'{project}/zones/{zone}/operations',
              request_field='',
              request_type_name=u'AutoscalerZoneOperationsListRequest',
              response_type_name=u'OperationList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes the specified zone-specific operation resource.

      Args:
        request: (AutoscalerZoneOperationsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (AutoscalerZoneOperationsDeleteResponse) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Retrieves the specified zone-specific operation resource.

      Args:
        request: (AutoscalerZoneOperationsGetRequest) input message
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
        request: (AutoscalerZoneOperationsListRequest) input message
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
      super(AutoscalerV1beta2.ZonesService, self).__init__(client)
      self._method_configs = {
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'autoscaler.zones.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'{project}/zones',
              request_field='',
              request_type_name=u'AutoscalerZonesListRequest',
              response_type_name=u'ZoneList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def List(self, request, global_params=None):
      """List method for the zones service.

      Args:
        request: (AutoscalerZonesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ZoneList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)
