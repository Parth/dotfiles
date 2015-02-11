"""Generated client library for replicapool version v1beta1."""

from googlecloudapis.apitools.base.py import base_api
from googlecloudapis.replicapool.v1beta1 import replicapool_v1beta1_messages as messages


class ReplicapoolV1beta1(base_api.BaseApiClient):
  """Generated client library for service replicapool version v1beta1."""

  MESSAGES_MODULE = messages

  _PACKAGE = u'replicapool'
  _SCOPES = [u'https://www.googleapis.com/auth/cloud-platform', u'https://www.googleapis.com/auth/ndev.cloudman', u'https://www.googleapis.com/auth/ndev.cloudman.readonly', u'https://www.googleapis.com/auth/replicapool', u'https://www.googleapis.com/auth/replicapool.readonly']
  _VERSION = u'v1beta1'
  _CLIENT_ID = ''
  _CLIENT_SECRET = ''
  _USER_AGENT = ''
  _CLIENT_CLASS_NAME = u'ReplicapoolV1beta1'
  _URL_VERSION = u'v1beta1'

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new replicapool handle."""
    url = url or u'https://www.googleapis.com/replicapool/v1beta1/'
    super(ReplicapoolV1beta1, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.pools = self.PoolsService(self)
    self.replicas = self.ReplicasService(self)

  class PoolsService(base_api.BaseApiService):
    """Service class for the pools resource."""

    _NAME = u'pools'

    def __init__(self, client):
      super(ReplicapoolV1beta1.PoolsService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapool.pools.delete',
              ordered_params=[u'projectName', u'zone', u'poolName'],
              path_params=[u'poolName', u'projectName', u'zone'],
              query_params=[],
              relative_path=u'projects/{projectName}/zones/{zone}/pools/{poolName}',
              request_field=u'poolsDeleteRequest',
              request_type_name=u'ReplicapoolPoolsDeleteRequest',
              response_type_name=u'ReplicapoolPoolsDeleteResponse',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'replicapool.pools.get',
              ordered_params=[u'projectName', u'zone', u'poolName'],
              path_params=[u'poolName', u'projectName', u'zone'],
              query_params=[],
              relative_path=u'projects/{projectName}/zones/{zone}/pools/{poolName}',
              request_field='',
              request_type_name=u'ReplicapoolPoolsGetRequest',
              response_type_name=u'Pool',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapool.pools.insert',
              ordered_params=[u'projectName', u'zone'],
              path_params=[u'projectName', u'zone'],
              query_params=[],
              relative_path=u'projects/{projectName}/zones/{zone}/pools',
              request_field=u'pool',
              request_type_name=u'ReplicapoolPoolsInsertRequest',
              response_type_name=u'Pool',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'replicapool.pools.list',
              ordered_params=[u'projectName', u'zone'],
              path_params=[u'projectName', u'zone'],
              query_params=[u'maxResults', u'pageToken'],
              relative_path=u'projects/{projectName}/zones/{zone}/pools',
              request_field='',
              request_type_name=u'ReplicapoolPoolsListRequest',
              response_type_name=u'PoolsListResponse',
              supports_download=False,
          ),
          'Resize': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapool.pools.resize',
              ordered_params=[u'projectName', u'zone', u'poolName'],
              path_params=[u'poolName', u'projectName', u'zone'],
              query_params=[u'numReplicas'],
              relative_path=u'projects/{projectName}/zones/{zone}/pools/{poolName}/resize',
              request_field='',
              request_type_name=u'ReplicapoolPoolsResizeRequest',
              response_type_name=u'Pool',
              supports_download=False,
          ),
          'Updatetemplate': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapool.pools.updatetemplate',
              ordered_params=[u'projectName', u'zone', u'poolName'],
              path_params=[u'poolName', u'projectName', u'zone'],
              query_params=[],
              relative_path=u'projects/{projectName}/zones/{zone}/pools/{poolName}/updateTemplate',
              request_field=u'template',
              request_type_name=u'ReplicapoolPoolsUpdatetemplateRequest',
              response_type_name=u'ReplicapoolPoolsUpdatetemplateResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes a replica pool.

      Args:
        request: (ReplicapoolPoolsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ReplicapoolPoolsDeleteResponse) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Gets information about a single replica pool.

      Args:
        request: (ReplicapoolPoolsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Pool) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Inserts a new replica pool.

      Args:
        request: (ReplicapoolPoolsInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Pool) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """List all replica pools.

      Args:
        request: (ReplicapoolPoolsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (PoolsListResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Resize(self, request, global_params=None):
      """Resize a pool. This is an asynchronous operation, and multiple overlapping resize requests can be made. Replica Pools will use the information from the last resize request.

      Args:
        request: (ReplicapoolPoolsResizeRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Pool) The response message.
      """
      config = self.GetMethodConfig('Resize')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Updatetemplate(self, request, global_params=None):
      """Update the template used by the pool.

      Args:
        request: (ReplicapoolPoolsUpdatetemplateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ReplicapoolPoolsUpdatetemplateResponse) The response message.
      """
      config = self.GetMethodConfig('Updatetemplate')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ReplicasService(base_api.BaseApiService):
    """Service class for the replicas resource."""

    _NAME = u'replicas'

    def __init__(self, client):
      super(ReplicapoolV1beta1.ReplicasService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapool.replicas.delete',
              ordered_params=[u'projectName', u'zone', u'poolName', u'replicaName'],
              path_params=[u'poolName', u'projectName', u'replicaName', u'zone'],
              query_params=[],
              relative_path=u'projects/{projectName}/zones/{zone}/pools/{poolName}/replicas/{replicaName}',
              request_field=u'replicasDeleteRequest',
              request_type_name=u'ReplicapoolReplicasDeleteRequest',
              response_type_name=u'Replica',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'replicapool.replicas.get',
              ordered_params=[u'projectName', u'zone', u'poolName', u'replicaName'],
              path_params=[u'poolName', u'projectName', u'replicaName', u'zone'],
              query_params=[],
              relative_path=u'projects/{projectName}/zones/{zone}/pools/{poolName}/replicas/{replicaName}',
              request_field='',
              request_type_name=u'ReplicapoolReplicasGetRequest',
              response_type_name=u'Replica',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'replicapool.replicas.list',
              ordered_params=[u'projectName', u'zone', u'poolName'],
              path_params=[u'poolName', u'projectName', u'zone'],
              query_params=[u'maxResults', u'pageToken'],
              relative_path=u'projects/{projectName}/zones/{zone}/pools/{poolName}/replicas',
              request_field='',
              request_type_name=u'ReplicapoolReplicasListRequest',
              response_type_name=u'ReplicasListResponse',
              supports_download=False,
          ),
          'Restart': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapool.replicas.restart',
              ordered_params=[u'projectName', u'zone', u'poolName', u'replicaName'],
              path_params=[u'poolName', u'projectName', u'replicaName', u'zone'],
              query_params=[],
              relative_path=u'projects/{projectName}/zones/{zone}/pools/{poolName}/replicas/{replicaName}/restart',
              request_field='',
              request_type_name=u'ReplicapoolReplicasRestartRequest',
              response_type_name=u'Replica',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes a replica from the pool.

      Args:
        request: (ReplicapoolReplicasDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Replica) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Gets information about a specific replica.

      Args:
        request: (ReplicapoolReplicasGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Replica) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Lists all replicas in a pool.

      Args:
        request: (ReplicapoolReplicasListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ReplicasListResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Restart(self, request, global_params=None):
      """Restarts a replica in a pool.

      Args:
        request: (ReplicapoolReplicasRestartRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Replica) The response message.
      """
      config = self.GetMethodConfig('Restart')
      return self._RunMethod(
          config, request, global_params=global_params)
