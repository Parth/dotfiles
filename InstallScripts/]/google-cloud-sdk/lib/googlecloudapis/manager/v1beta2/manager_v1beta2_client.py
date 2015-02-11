"""Generated client library for manager version v1beta2."""

from googlecloudapis.apitools.base.py import base_api
from googlecloudapis.manager.v1beta2 import manager_v1beta2_messages as messages


class ManagerV1beta2(base_api.BaseApiClient):
  """Generated client library for service manager version v1beta2."""

  MESSAGES_MODULE = messages

  _PACKAGE = u'manager'
  _SCOPES = [u'https://www.googleapis.com/auth/appengine.admin', u'https://www.googleapis.com/auth/cloud-platform', u'https://www.googleapis.com/auth/compute', u'https://www.googleapis.com/auth/devstorage.read_write', u'https://www.googleapis.com/auth/ndev.cloudman', u'https://www.googleapis.com/auth/ndev.cloudman.readonly']
  _VERSION = u'v1beta2'
  _CLIENT_ID = ''
  _CLIENT_SECRET = ''
  _USER_AGENT = ''
  _CLIENT_CLASS_NAME = u'ManagerV1beta2'
  _URL_VERSION = u'v1beta2'

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new manager handle."""
    url = url or u'https://www.googleapis.com/manager/v1beta2/'
    super(ManagerV1beta2, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.deployments = self.DeploymentsService(self)
    self.templates = self.TemplatesService(self)

  class DeploymentsService(base_api.BaseApiService):
    """Service class for the deployments resource."""

    _NAME = u'deployments'

    def __init__(self, client):
      super(ManagerV1beta2.DeploymentsService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'manager.deployments.delete',
              ordered_params=[u'projectId', u'region', u'deploymentName'],
              path_params=[u'deploymentName', u'projectId', u'region'],
              query_params=[],
              relative_path=u'projects/{projectId}/regions/{region}/deployments/{deploymentName}',
              request_field='',
              request_type_name=u'ManagerDeploymentsDeleteRequest',
              response_type_name=u'ManagerDeploymentsDeleteResponse',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'manager.deployments.get',
              ordered_params=[u'projectId', u'region', u'deploymentName'],
              path_params=[u'deploymentName', u'projectId', u'region'],
              query_params=[],
              relative_path=u'projects/{projectId}/regions/{region}/deployments/{deploymentName}',
              request_field='',
              request_type_name=u'ManagerDeploymentsGetRequest',
              response_type_name=u'Deployment',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'manager.deployments.insert',
              ordered_params=[u'projectId', u'region'],
              path_params=[u'projectId', u'region'],
              query_params=[],
              relative_path=u'projects/{projectId}/regions/{region}/deployments',
              request_field=u'deployment',
              request_type_name=u'ManagerDeploymentsInsertRequest',
              response_type_name=u'Deployment',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'manager.deployments.list',
              ordered_params=[u'projectId', u'region'],
              path_params=[u'projectId', u'region'],
              query_params=[u'maxResults', u'pageToken'],
              relative_path=u'projects/{projectId}/regions/{region}/deployments',
              request_field='',
              request_type_name=u'ManagerDeploymentsListRequest',
              response_type_name=u'DeploymentsListResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Delete method for the deployments service.

      Args:
        request: (ManagerDeploymentsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ManagerDeploymentsDeleteResponse) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Get method for the deployments service.

      Args:
        request: (ManagerDeploymentsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Deployment) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Insert method for the deployments service.

      Args:
        request: (ManagerDeploymentsInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Deployment) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """List method for the deployments service.

      Args:
        request: (ManagerDeploymentsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (DeploymentsListResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class TemplatesService(base_api.BaseApiService):
    """Service class for the templates resource."""

    _NAME = u'templates'

    def __init__(self, client):
      super(ManagerV1beta2.TemplatesService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'manager.templates.delete',
              ordered_params=[u'projectId', u'templateName'],
              path_params=[u'projectId', u'templateName'],
              query_params=[],
              relative_path=u'projects/{projectId}/templates/{templateName}',
              request_field='',
              request_type_name=u'ManagerTemplatesDeleteRequest',
              response_type_name=u'ManagerTemplatesDeleteResponse',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'manager.templates.get',
              ordered_params=[u'projectId', u'templateName'],
              path_params=[u'projectId', u'templateName'],
              query_params=[],
              relative_path=u'projects/{projectId}/templates/{templateName}',
              request_field='',
              request_type_name=u'ManagerTemplatesGetRequest',
              response_type_name=u'Template',
              supports_download=False,
          ),
          'Insert': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'manager.templates.insert',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}/templates',
              request_field=u'template',
              request_type_name=u'ManagerTemplatesInsertRequest',
              response_type_name=u'Template',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'manager.templates.list',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[u'maxResults', u'pageToken'],
              relative_path=u'projects/{projectId}/templates',
              request_field='',
              request_type_name=u'ManagerTemplatesListRequest',
              response_type_name=u'TemplatesListResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Delete method for the templates service.

      Args:
        request: (ManagerTemplatesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ManagerTemplatesDeleteResponse) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Get method for the templates service.

      Args:
        request: (ManagerTemplatesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Template) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Insert(self, request, global_params=None):
      """Insert method for the templates service.

      Args:
        request: (ManagerTemplatesInsertRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Template) The response message.
      """
      config = self.GetMethodConfig('Insert')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """List method for the templates service.

      Args:
        request: (ManagerTemplatesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TemplatesListResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)
