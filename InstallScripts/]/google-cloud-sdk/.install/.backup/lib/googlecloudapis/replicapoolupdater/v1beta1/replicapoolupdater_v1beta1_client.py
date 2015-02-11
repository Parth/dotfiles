"""Generated client library for replicapoolupdater version v1beta1."""

from googlecloudapis.apitools.base.py import base_api
from googlecloudapis.replicapoolupdater.v1beta1 import replicapoolupdater_v1beta1_messages as messages


class ReplicapoolupdaterV1beta1(base_api.BaseApiClient):
  """Generated client library for service replicapoolupdater version v1beta1."""

  MESSAGES_MODULE = messages

  _PACKAGE = u'replicapoolupdater'
  _SCOPES = [u'https://www.googleapis.com/auth/cloud-platform', u'https://www.googleapis.com/auth/replicapool', u'https://www.googleapis.com/auth/replicapool.readonly']
  _VERSION = u'v1beta1'
  _CLIENT_ID = ''
  _CLIENT_SECRET = ''
  _USER_AGENT = ''
  _CLIENT_CLASS_NAME = u'ReplicapoolupdaterV1beta1'
  _URL_VERSION = u'v1beta1'

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new replicapoolupdater handle."""
    url = url or u'https://www.googleapis.com/replicapoolupdater/v1beta1/'
    super(ReplicapoolupdaterV1beta1, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.rollingUpdates = self.RollingUpdatesService(self)
    self.zoneOperations = self.ZoneOperationsService(self)

  class RollingUpdatesService(base_api.BaseApiService):
    """Service class for the rollingUpdates resource."""

    _NAME = u'rollingUpdates'

    def __init__(self, client):
      super(ReplicapoolupdaterV1beta1.RollingUpdatesService, self).__init__(client)
      self._method_configs = {
          'Cancel': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapoolupdater.rollingUpdates.cancel',
              ordered_params=[u'project', u'zone', u'rollingUpdate'],
              path_params=[u'project', u'rollingUpdate', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/rollingUpdates/{rollingUpdate}/cancel',
              request_field='',
              request_type_name=u'ReplicapoolupdaterRollingUpdatesCancelRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'replicapoolupdater.rollingUpdates.get',
              ordered_params=[u'project', u'zone', u'rollingUpdate'],
              path_params=[u'project', u'rollingUpdate', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/rollingUpdates/{rollingUpdate}',
              request_field='',
              request_type_name=u'ReplicapoolupdaterRollingUpdatesGetRequest',
              response_type_name=u'RollingUpdate',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapoolupdater.rollingUpdates.insert',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/rollingUpdates',
              request_field=u'rollingUpdate',
              request_type_name=u'ReplicapoolupdaterRollingUpdatesInsertRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'replicapoolupdater.rollingUpdates.list',
              ordered_params=[u'project', u'zone'],
              path_params=[u'project', u'zone'],
              query_params=[u'filter', u'instanceGroupManager', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/zones/{zone}/rollingUpdates',
              request_field='',
              request_type_name=u'ReplicapoolupdaterRollingUpdatesListRequest',
              response_type_name=u'RollingUpdateList',
              supports_download=False,
          ),
          'ListInstanceUpdates': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'replicapoolupdater.rollingUpdates.listInstanceUpdates',
              ordered_params=[u'project', u'zone', u'rollingUpdate'],
              path_params=[u'project', u'rollingUpdate', u'zone'],
              query_params=[u'filter', u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/zones/{zone}/rollingUpdates/{rollingUpdate}/instanceUpdates',
              request_field='',
              request_type_name=u'ReplicapoolupdaterRollingUpdatesListInstanceUpdatesRequest',
              response_type_name=u'InstanceUpdateList',
              supports_download=False,
          ),
          'Pause': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapoolupdater.rollingUpdates.pause',
              ordered_params=[u'project', u'zone', u'rollingUpdate'],
              path_params=[u'project', u'rollingUpdate', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/rollingUpdates/{rollingUpdate}/pause',
              request_field='',
              request_type_name=u'ReplicapoolupdaterRollingUpdatesPauseRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Resume': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapoolupdater.rollingUpdates.resume',
              ordered_params=[u'project', u'zone', u'rollingUpdate'],
              path_params=[u'project', u'rollingUpdate', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/rollingUpdates/{rollingUpdate}/resume',
              request_field='',
              request_type_name=u'ReplicapoolupdaterRollingUpdatesResumeRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          'Rollback': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'replicapoolupdater.rollingUpdates.rollback',
              ordered_params=[u'project', u'zone', u'rollingUpdate'],
              path_params=[u'project', u'rollingUpdate', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/rollingUpdates/{rollingUpdate}/rollback',
              request_field='',
              request_type_name=u'ReplicapoolupdaterRollingUpdatesRollbackRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Cancel(self, request, global_params=None):
      """Cancels an update. The update must be PAUSED before it can be cancelled. This has no effect if the update is already CANCELLED.

      Args:
        request: (ReplicapoolupdaterRollingUpdatesCancelRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Cancel')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns information about an update.

      Args:
        request: (ReplicapoolupdaterRollingUpdatesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (RollingUpdate) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Inserts and starts a new update.

      Args:
        request: (ReplicapoolupdaterRollingUpdatesInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Lists recent updates for a given managed instance group, in reverse chronological order and paginated format.

      Args:
        request: (ReplicapoolupdaterRollingUpdatesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (RollingUpdateList) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def ListInstanceUpdates(self, request, global_params=None):
      """Lists the current status for each instance within a given update.

      Args:
        request: (ReplicapoolupdaterRollingUpdatesListInstanceUpdatesRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (InstanceUpdateList) The response message.
      """
      config = self.GetMethodConfig('ListInstanceUpdates')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Pause(self, request, global_params=None):
      """Pauses the update in state from ROLLING_FORWARD or ROLLING_BACK. Has no effect if invoked when the state of the update is PAUSED.

      Args:
        request: (ReplicapoolupdaterRollingUpdatesPauseRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Pause')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Resume(self, request, global_params=None):
      """Continues an update in PAUSED state. Has no effect if invoked when the state of the update is ROLLED_OUT.

      Args:
        request: (ReplicapoolupdaterRollingUpdatesResumeRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Resume')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Rollback(self, request, global_params=None):
      """Rolls back the update in state from ROLLING_FORWARD or PAUSED. Has no effect if invoked when the state of the update is ROLLED_BACK.

      Args:
        request: (ReplicapoolupdaterRollingUpdatesRollbackRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Rollback')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ZoneOperationsService(base_api.BaseApiService):
    """Service class for the zoneOperations resource."""

    _NAME = u'zoneOperations'

    def __init__(self, client):
      super(ReplicapoolupdaterV1beta1.ZoneOperationsService, self).__init__(client)
      self._method_configs = {
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'replicapoolupdater.zoneOperations.get',
              ordered_params=[u'project', u'zone', u'operation'],
              path_params=[u'operation', u'project', u'zone'],
              query_params=[],
              relative_path=u'projects/{project}/zones/{zone}/operations/{operation}',
              request_field='',
              request_type_name=u'ReplicapoolupdaterZoneOperationsGetRequest',
              response_type_name=u'Operation',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Get(self, request, global_params=None):
      """Retrieves the specified zone-specific operation resource.

      Args:
        request: (ReplicapoolupdaterZoneOperationsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Operation) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)
