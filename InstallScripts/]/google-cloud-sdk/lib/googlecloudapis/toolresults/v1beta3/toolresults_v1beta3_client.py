"""Generated client library for toolresults version v1beta3."""

from googlecloudapis.apitools.base.py import base_api
from googlecloudapis.toolresults.v1beta3 import toolresults_v1beta3_messages as messages


class ToolresultsV1beta3(base_api.BaseApiClient):
  """Generated client library for service toolresults version v1beta3."""

  MESSAGES_MODULE = messages

  _PACKAGE = u'toolresults'
  _SCOPES = [u'https://www.googleapis.com/auth/cloud-platform']
  _VERSION = u'v1beta3'
  _CLIENT_ID = ''
  _CLIENT_SECRET = ''
  _USER_AGENT = ''
  _CLIENT_CLASS_NAME = u'ToolresultsV1beta3'
  _URL_VERSION = u'v1beta3'

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new toolresults handle."""
    url = url or u'https://www.googleapis.com/toolresults/v1beta3/'
    super(ToolresultsV1beta3, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.projects_histories_executions_steps = self.ProjectsHistoriesExecutionsStepsService(self)
    self.projects_histories_executions = self.ProjectsHistoriesExecutionsService(self)
    self.projects_histories = self.ProjectsHistoriesService(self)
    self.projects = self.ProjectsService(self)

  class ProjectsHistoriesExecutionsStepsService(base_api.BaseApiService):
    """Service class for the projects_histories_executions_steps resource."""

    _NAME = u'projects_histories_executions_steps'

    def __init__(self, client):
      super(ToolresultsV1beta3.ProjectsHistoriesExecutionsStepsService, self).__init__(client)
      self._method_configs = {
          'Create': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'toolresults.projects.histories.executions.steps.create',
              ordered_params=[u'projectId', u'historyId', u'executionId'],
              path_params=[u'executionId', u'historyId', u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}/histories/{historyId}/executions/{executionId}/steps',
              request_field=u'step',
              request_type_name=u'ToolresultsProjectsHistoriesExecutionsStepsCreateRequest',
              response_type_name=u'Step',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'toolresults.projects.histories.executions.steps.get',
              ordered_params=[u'projectId', u'historyId', u'executionId', u'stepId'],
              path_params=[u'executionId', u'historyId', u'projectId', u'stepId'],
              query_params=[],
              relative_path=u'projects/{projectId}/histories/{historyId}/executions/{executionId}/steps/{stepId}',
              request_field='',
              request_type_name=u'ToolresultsProjectsHistoriesExecutionsStepsGetRequest',
              response_type_name=u'Step',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'toolresults.projects.histories.executions.steps.list',
              ordered_params=[u'projectId', u'historyId', u'executionId'],
              path_params=[u'executionId', u'historyId', u'projectId'],
              query_params=[u'pageSize', u'pageToken'],
              relative_path=u'projects/{projectId}/histories/{historyId}/executions/{executionId}/steps',
              request_field='',
              request_type_name=u'ToolresultsProjectsHistoriesExecutionsStepsListRequest',
              response_type_name=u'ListStepsResponse',
              supports_download=False,
          ),
          'Patch': base_api.ApiMethodInfo(
              http_method=u'PATCH',
              method_id=u'toolresults.projects.histories.executions.steps.patch',
              ordered_params=[u'projectId', u'historyId', u'executionId', u'stepId'],
              path_params=[u'executionId', u'historyId', u'projectId', u'stepId'],
              query_params=[],
              relative_path=u'projects/{projectId}/histories/{historyId}/executions/{executionId}/steps/{stepId}',
              request_field=u'step',
              request_type_name=u'ToolresultsProjectsHistoriesExecutionsStepsPatchRequest',
              response_type_name=u'Step',
              supports_download=False,
          ),
          'PublishXunitXmlFiles': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'toolresults.projects.histories.executions.steps.publishXunitXmlFiles',
              ordered_params=[u'projectId', u'historyId', u'executionId', u'stepId'],
              path_params=[u'executionId', u'historyId', u'projectId', u'stepId'],
              query_params=[],
              relative_path=u'projects/{projectId}/histories/{historyId}/executions/{executionId}/steps/{stepId}:publishXunitXmlFiles',
              request_field=u'publishXunitXmlFilesRequest',
              request_type_name=u'ToolresultsProjectsHistoriesExecutionsStepsPublishXunitXmlFilesRequest',
              response_type_name=u'Step',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Create(self, request, global_params=None):
      """Creates a Step.

The returned Step will have the id set.

May return any of the following canonical error codes:

- PERMISSION_DENIED - if the user is not authorized to write to project - INVALID_ARGUMENT - if the request is malformed - FAILED_PRECONDITION - if the step is too large (more than 10Mib) - NOT_FOUND - if the containing Execution does not exist

      Args:
        request: (ToolresultsProjectsHistoriesExecutionsStepsCreateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Step) The response message.
      """
      config = self.GetMethodConfig('Create')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Gets a Step.

May return any of the following canonical error codes:

- PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the Step does not exist

      Args:
        request: (ToolresultsProjectsHistoriesExecutionsStepsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Step) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Lists Steps for a given Execution.

The steps are sorted by creation_time in descending order. The step_id key will be used to order the steps with the same creation_time.

May return any of the following canonical error codes:

- PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - FAILED_PRECONDITION - if an argument in the request happens to be invalid; e.g. if an attempt is made to list the children of a nonexistent Step - NOT_FOUND - if the containing Execution does not exist

      Args:
        request: (ToolresultsProjectsHistoriesExecutionsStepsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListStepsResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Patch(self, request, global_params=None):
      """Updates an existing Step with the supplied partial entity.

May return any of the following canonical error codes:

- PERMISSION_DENIED - if the user is not authorized to write project - INVALID_ARGUMENT - if the request is malformed - FAILED_PRECONDITION - if the requested state transition is illegal (e.g try to upload a duplicate xml file), if the updated step is too large (more than 10Mib) - NOT_FOUND - if the containing Execution does not exist

      Args:
        request: (ToolresultsProjectsHistoriesExecutionsStepsPatchRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Step) The response message.
      """
      config = self.GetMethodConfig('Patch')
      return self._RunMethod(
          config, request, global_params=global_params)

    def PublishXunitXmlFiles(self, request, global_params=None):
      """Publish an xml file to an existing Step. This will trigger an xml parsing action in server side and one or more TestSuiteOverview will be added to this step based on the xml parsing result.

May return any of the following canonical error codes:

- PERMISSION_DENIED - if the user is not authorized to write project - INVALID_ARGUMENT - if the request is malformed - FAILED_PRECONDITION - if the requested state transition is illegal, e.g try to upload a duplicate xml file or a file too large. - NOT_FOUND - if the containing Execution does not exist

      Args:
        request: (ToolresultsProjectsHistoriesExecutionsStepsPublishXunitXmlFilesRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Step) The response message.
      """
      config = self.GetMethodConfig('PublishXunitXmlFiles')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ProjectsHistoriesExecutionsService(base_api.BaseApiService):
    """Service class for the projects_histories_executions resource."""

    _NAME = u'projects_histories_executions'

    def __init__(self, client):
      super(ToolresultsV1beta3.ProjectsHistoriesExecutionsService, self).__init__(client)
      self._method_configs = {
          'Create': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'toolresults.projects.histories.executions.create',
              ordered_params=[u'projectId', u'historyId'],
              path_params=[u'historyId', u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}/histories/{historyId}/executions',
              request_field=u'execution',
              request_type_name=u'ToolresultsProjectsHistoriesExecutionsCreateRequest',
              response_type_name=u'Execution',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'toolresults.projects.histories.executions.get',
              ordered_params=[u'projectId', u'historyId', u'executionId'],
              path_params=[u'executionId', u'historyId', u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}/histories/{historyId}/executions/{executionId}',
              request_field='',
              request_type_name=u'ToolresultsProjectsHistoriesExecutionsGetRequest',
              response_type_name=u'Execution',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'toolresults.projects.histories.executions.list',
              ordered_params=[u'projectId', u'historyId'],
              path_params=[u'historyId', u'projectId'],
              query_params=[u'pageSize', u'pageToken'],
              relative_path=u'projects/{projectId}/histories/{historyId}/executions',
              request_field='',
              request_type_name=u'ToolresultsProjectsHistoriesExecutionsListRequest',
              response_type_name=u'ListExecutionsResponse',
              supports_download=False,
          ),
          'Patch': base_api.ApiMethodInfo(
              http_method=u'PATCH',
              method_id=u'toolresults.projects.histories.executions.patch',
              ordered_params=[u'projectId', u'historyId', u'executionId'],
              path_params=[u'executionId', u'historyId', u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}/histories/{historyId}/executions/{executionId}',
              request_field=u'execution',
              request_type_name=u'ToolresultsProjectsHistoriesExecutionsPatchRequest',
              response_type_name=u'Execution',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Create(self, request, global_params=None):
      """Creates a Execution.

The returned Execution will have the id set.

May return any of the following canonical error codes:

- PERMISSION_DENIED - if the user is not authorized to write to project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the containing History does not exist

      Args:
        request: (ToolresultsProjectsHistoriesExecutionsCreateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Execution) The response message.
      """
      config = self.GetMethodConfig('Create')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Gets a Execution.

May return any of the following canonical error codes:

- PERMISSION_DENIED - if the user is not authorized to write to project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the Execution does not exist

      Args:
        request: (ToolresultsProjectsHistoriesExecutionsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Execution) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Lists Histories for a given Project.

The executions are sorted by creation_time in descending order. The execution_id key will be used to order the executions with the same creation_time.

May return any of the following canonical error codes:

- PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the containing History does not exist

      Args:
        request: (ToolresultsProjectsHistoriesExecutionsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListExecutionsResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Patch(self, request, global_params=None):
      """Updates an existing Execution with the supplied partial entity.

May return any of the following canonical error codes:

- PERMISSION_DENIED - if the user is not authorized to write to project - INVALID_ARGUMENT - if the request is malformed - FAILED_PRECONDITION - if the requested state transition is illegal - NOT_FOUND - if the containing History does not exist

      Args:
        request: (ToolresultsProjectsHistoriesExecutionsPatchRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Execution) The response message.
      """
      config = self.GetMethodConfig('Patch')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ProjectsHistoriesService(base_api.BaseApiService):
    """Service class for the projects_histories resource."""

    _NAME = u'projects_histories'

    def __init__(self, client):
      super(ToolresultsV1beta3.ProjectsHistoriesService, self).__init__(client)
      self._method_configs = {
          'Create': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'toolresults.projects.histories.create',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}/histories',
              request_field=u'history',
              request_type_name=u'ToolresultsProjectsHistoriesCreateRequest',
              response_type_name=u'History',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'toolresults.projects.histories.get',
              ordered_params=[u'projectId', u'historyId'],
              path_params=[u'historyId', u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}/histories/{historyId}',
              request_field='',
              request_type_name=u'ToolresultsProjectsHistoriesGetRequest',
              response_type_name=u'History',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'toolresults.projects.histories.list',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[u'filterByDisplayName', u'pageSize', u'pageToken'],
              relative_path=u'projects/{projectId}/histories',
              request_field='',
              request_type_name=u'ToolresultsProjectsHistoriesListRequest',
              response_type_name=u'ListHistoriesResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Create(self, request, global_params=None):
      """Creates a History.

The returned History will have the id set.

May return any of the following canonical error codes:

- PERMISSION_DENIED - if the user is not authorized to write to project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the containing project does not exist

      Args:
        request: (ToolresultsProjectsHistoriesCreateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (History) The response message.
      """
      config = self.GetMethodConfig('Create')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Gets a History.

May return any of the following canonical error codes:

- PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the History does not exist

      Args:
        request: (ToolresultsProjectsHistoriesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (History) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Lists Histories for a given Project.

The histories are sorted by modification time in descending order. The history_id key will be used to order the history with the same modification time.

May return any of the following canonical error codes:

- PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the History does not exist

      Args:
        request: (ToolresultsProjectsHistoriesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListHistoriesResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ProjectsService(base_api.BaseApiService):
    """Service class for the projects resource."""

    _NAME = u'projects'

    def __init__(self, client):
      super(ToolresultsV1beta3.ProjectsService, self).__init__(client)
      self._method_configs = {
          }

      self._upload_configs = {
          }
