"""Generated client library for replicapool version v1beta2."""

from googlecloudapis.apitools.base.py import base_api
from googlecloudapis.replicapool.v1beta2 import replicapool_v1beta2_messages as messages


class ReplicapoolV1beta2(base_api.BaseApiClient):
  """Generated client library for service replicapool version v1beta2."""

  MESSAGES_MODULE = messages

  _PACKAGE = u'replicapool'
  _SCOPES = [u'https://www.googleapis.com/auth/cloud-platform', u'https://www.googleapis.com/auth/compute', u'https://www.googleapis.com/auth/compute.readonly']
  _VERSION = u'v1beta2'
  _CLIENT_ID = ''
  _CLIENT_SECRET = ''
  _USER_AGENT = ''
  _CLIENT_CLASS_NAME = u'ReplicapoolV1beta2'
  _URL_VERSION = u'v1beta2'

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new replicapool handle."""
    url = url or u'https://www.googleapis.com/replicapool/v1beta2/'
    super(ReplicapoolV1beta2, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.instanceGroupManagers = self.InstanceGroupManagersService(self)
    self.zoneOperations = self.ZoneOperationsService(self)

  class InstanceGroupManagersService(base_api.BaseApiService):
    """Service class for the instanceGroupManagers resource."""

    _NAME = u'instanceGroupManagers'

    def __init__(self, client):
      super(ReplicapoolV1beta2.InstanceGroupManagersService, self).__init__(client)
      self._method_configs = {
          'AbandonInstances': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapool.instanceGroupManagers.abandonInstances',
              ordered_params=[u'project', u'zone', u'instanceGroupManager'],
              path_params=[u'instanceGroupManager', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instanceGroupManagers/{instanceGroupManager}/abandonInstances',
              request_field=u'instanceGroupManagersAbandonInstancesRequest',
              request_type_name=u'ReplicapoolInstanceGroupManagersAbandonInstancesRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'replicapool.instanceGroupManagers.delete',
              ordered_params=[u'project', u'zone', u'instanceGroupManager'],
              path_params=[u'instanceGroupManager', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instanceGroupManagers/{instanceGroupManager}',
              request_field='',
              request_type_name=u'ReplicapoolInstanceGroupManagersDeleteRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'DeleteInstances': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapool.instanceGroupManagers.deleteInstances',
              ordered_params=[u'project', u'zone', u'instanceGroupManager'],
              path_params=[u'instanceGroupManager', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instanceGroupManagers/{instanceGroupManager}/deleteInstances',
              request_field=u'instanceGroupManagersDeleteInstancesRequest',
              request_type_name=u'ReplicapoolInstanceGroupManagersDeleteInstancesRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'replicapool.instanceGroupManagers.get',
              ordered_params=[u'project', u'zone', u'instanceGroupManager'],
              path_params=[u'instanceGroupManager', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instanceGroupManagers/{instanceGroupManager}',
              request_field='',
              request_type_name=u'ReplicapoolInstanceGroupManagersGetRequest',
              response_type_name=u'InstanceGroupManager',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapool.instanceGroupManagers.insert',
              ordered_params=[u'project', u'zone', u'size'],
              path_params=[u'project', u'zone'],
              query_params=[u'size'],
              relative_path=u'projects/{project}/zones/{zone}/instanceGroupManagers',
              request_field=u'instanceGroupManager',
              request_type_name=u'ReplicapoolInstanceGroupManagersInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'replicapool.instanceGroupManagers.list',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/zones/{zone}/instanceGroupManagers',
              request_field='',
              request_type_name=u'ReplicapoolInstanceGroupManagersListRequest',
              response_type_name=u'InstanceGroupManagerList',
              supports_download=False,
          ),
          'RecreateInstances': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapool.instanceGroupManagers.recreateInstances',
              ordered_params=[u'project', u'zone', u'instanceGroupManager'],
              path_params=[u'instanceGroupManager', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instanceGroupManagers/{instanceGroupManager}/recreateInstances',
              request_field=u'instanceGroupManagersRecreateInstancesRequest',
              request_type_name=u'ReplicapoolInstanceGroupManagersRecreateInstancesRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Resize': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapool.instanceGroupManagers.resize',
              ordered_params=[u'project', u'zone', u'instanceGroupManager', u'size'],
              path_params=[u'instanceGroupManager', u'project', u'zone'],
              query_params=[u'size'],
              relative_path=u'projects/{project}/zones/{zone}/instanceGroupManagers/{instanceGroupManager}/resize',
              request_field='',
              request_type_name=u'ReplicapoolInstanceGroupManagersResizeRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'SetInstanceTemplate': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapool.instanceGroupManagers.setInstanceTemplate',
              ordered_params=[u'project', u'zone', u'instanceGroupManager'],
              path_params=[u'instanceGroupManager', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instanceGroupManagers/{instanceGroupManager}/setInstanceTemplate',
              request_field=u'instanceGroupManagersSetInstanceTemplateRequest',
              request_type_name=u'ReplicapoolInstanceGroupManagersSetInstanceTemplateRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'SetTargetPools': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapool.instanceGroupManagers.setTargetPools',
              ordered_params=[u'project', u'zone', u'instanceGroupManager'],
              path_params=[u'instanceGroupManager', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/instanceGroupManagers/{instanceGroupManager}/setTargetPools',
              request_field=u'instanceGroupManagersSetTargetPoolsRequest',
              request_type_name=u'ReplicapoolInstanceGroupManagersSetTargetPoolsRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def AbandonInstances(self, request, global_params=None):
      """Removes the specified instances from the managed instance group, and from any target pools of which they were members, without deleting the instances.

      Args:
        request: (ReplicapoolInstanceGroupManagersAbandonInstancesRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('AbandonInstances')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Deletes the instance group manager and all instances contained within. If you'd like to delete the manager without deleting the instances, you must first abandon the instances to remove them from the group.

      Args:
        request: (ReplicapoolInstanceGroupManagersDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def DeleteInstances(self, request, global_params=None):
      """Deletes the specified instances. The instances are deleted, then removed from the instance group and any target pools of which they were a member. The targetSize of the instance group manager is reduced by the number of instances deleted.

      Args:
        request: (ReplicapoolInstanceGroupManagersDeleteInstancesRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('DeleteInstances')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the specified Instance Group Manager resource.

      Args:
        request: (ReplicapoolInstanceGroupManagersGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (InstanceGroupManager) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Creates an instance group manager, as well as the instance group and the specified number of instances.

      Args:
        request: (ReplicapoolInstanceGroupManagersInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Retrieves the list of Instance Group Manager resources contained within the specified zone.

      Args:
        request: (ReplicapoolInstanceGroupManagersListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (InstanceGroupManagerList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def RecreateInstances(self, request, global_params=None):
      """Recreates the specified instances. The instances are deleted, then recreated using the instance group manager's current instance template.

      Args:
        request: (ReplicapoolInstanceGroupManagersRecreateInstancesRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('RecreateInstances')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Resize(self, request, global_params=None):
      """Resizes the managed instance group up or down. If resized up, new instances are created using the current instance template. If resized down, instances are removed in the order outlined in Resizing a managed instance group.

      Args:
        request: (ReplicapoolInstanceGroupManagersResizeRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Resize')
      return self._RunMethod(
          config, request, global_params=global_params)

    def SetInstanceTemplate(self, request, global_params=None):
      """Sets the instance template to use when creating new instances in this group. Existing instances are not affected.

      Args:
        request: (ReplicapoolInstanceGroupManagersSetInstanceTemplateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('SetInstanceTemplate')
      return self._RunMethod(
          config, request, global_params=global_params)

    def SetTargetPools(self, request, global_params=None):
      """Modifies the target pools to which all new instances in this group are assigned. Existing instances in the group are not affected.

      Args:
        request: (ReplicapoolInstanceGroupManagersSetTargetPoolsRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('SetTargetPools')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ZoneOperationsService(base_api.BaseApiService):
    """Service class for the zoneOperations resource."""

    _NAME = u'zoneOperations'

    def __init__(self, client):
      super(ReplicapoolV1beta2.ZoneOperationsService, self).__init__(client)
      self._method_configs = {
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'replicapool.zoneOperations.get',
              ordered_params=[u'project', u'zone', u'operation'],
              path_params=[u'operation', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/operations/{operation}',
              request_field='',
              request_type_name=u'ReplicapoolZoneOperationsGetRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'replicapool.zoneOperations.list',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/zones/{zone}/operations',
              request_field='',
              request_type_name=u'ReplicapoolZoneOperationsListRequest',
              response_type_name=u'OperationList',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Get(self, request, global_params=None):
      """Retrieves the specified zone-specific operation resource.

      Args:
        request: (ReplicapoolZoneOperationsGetRequest) input message
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
        request: (ReplicapoolZoneOperationsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (OperationList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)
