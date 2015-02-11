"""Generated client library for developerprojects version v2beta1."""

from googlecloudapis.apitools.base.py import base_api
from googlecloudapis.developerprojects.v2beta1 import developerprojects_v2beta1_messages as messages


class DeveloperprojectsV2beta1(base_api.BaseApiClient):
  """Generated client library for service developerprojects version v2beta1."""

  MESSAGES_MODULE = messages

  _PACKAGE = u'developerprojects'
  _SCOPES = [u'https://www.googleapis.com/auth/cloud-platform']
  _VERSION = u'v2beta1'
  _CLIENT_ID = ''
  _CLIENT_SECRET = ''
  _USER_AGENT = ''
  _CLIENT_CLASS_NAME = u'DeveloperprojectsV2beta1'
  _URL_VERSION = u'v2beta1'

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new developerprojects handle."""
    url = url or u'https://www.googleapis.com/developerprojects/v2beta1/'
    super(DeveloperprojectsV2beta1, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.projects = self.ProjectsService(self)

  class ProjectsService(base_api.BaseApiService):
    """Service class for the projects resource."""

    _NAME = u'projects'

    def __init__(self, client):
      super(DeveloperprojectsV2beta1.ProjectsService, self).__init__(client)
      self._method_configs = {
          'Create': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'developerprojects.projects.create',
              ordered_params=[],
              path_params=[],
              query_params=[u'appengineStorageLocation', u'createAppengineProject'],
              relative_path=u'projects',
              request_field=u'project',
              request_type_name=u'DeveloperprojectsProjectsCreateRequest',
              response_type_name=u'Project',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'developerprojects.projects.delete',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}',
              request_field='',
              request_type_name=u'DeveloperprojectsProjectsDeleteRequest',
              response_type_name=u'DeveloperprojectsProjectsDeleteResponse',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'developerprojects.projects.get',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}',
              request_field='',
              request_type_name=u'DeveloperprojectsProjectsGetRequest',
              response_type_name=u'Project',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'developerprojects.projects.list',
              ordered_params=[],
              path_params=[],
              query_params=[u'maxResults', u'pageToken', u'query'],
              relative_path=u'projects',
              request_field='',
              request_type_name=u'DeveloperprojectsProjectsListRequest',
              response_type_name=u'ListProjectsResponse',
              supports_download=False,
          ),
          'Patch': base_api.ApiMethodInfo(
              http_method=u'PATCH',
              method_id=u'developerprojects.projects.patch',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}',
              request_field='<request>',
              request_type_name=u'Project',
              response_type_name=u'Project',
              supports_download=False,
          ),
          'Undelete': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'developerprojects.projects.undelete',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}:undelete',
              request_field='',
              request_type_name=u'DeveloperprojectsProjectsUndeleteRequest',
              response_type_name=u'DeveloperprojectsProjectsUndeleteResponse',
              supports_download=False,
          ),
          'Update': base_api.ApiMethodInfo(
              http_method=u'PUT',
              method_id=u'developerprojects.projects.update',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}',
              request_field='<request>',
              request_type_name=u'Project',
              response_type_name=u'Project',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Create(self, request, global_params=None):
      """Creates a project resource.

Initially, the project resource is owned by its creator exclusively. The creator may then grant permission to read or update the project to others.

      Args:
        request: (DeveloperprojectsProjectsCreateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Project) The response message.
      """
      config = self.GetMethodConfig('Create')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Initiates deletion for this project.

      Args:
        request: (DeveloperprojectsProjectsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (DeveloperprojectsProjectsDeleteResponse) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Retrieves a limited project metadata set, given any project identifier.

      Args:
        request: (DeveloperprojectsProjectsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Project) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Lists projects visible to the user.

      Args:
        request: (DeveloperprojectsProjectsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListProjectsResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Patch(self, request, global_params=None):
      """Updates the metadata associated with the project.

. This method supports patch semantics.

      Args:
        request: (Project) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Project) The response message.
      """
      config = self.GetMethodConfig('Patch')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Undelete(self, request, global_params=None):
      """Request un-deletion for this project.

      Args:
        request: (DeveloperprojectsProjectsUndeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (DeveloperprojectsProjectsUndeleteResponse) The response message.
      """
      config = self.GetMethodConfig('Undelete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Update(self, request, global_params=None):
      """Updates the metadata associated with the project.

      Args:
        request: (Project) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Project) The response message.
      """
      config = self.GetMethodConfig('Update')
      return self._RunMethod(
          config, request, global_params=global_params)
