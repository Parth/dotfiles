"""Generated client library for test version v1."""

from googlecloudapis.apitools.base.py import base_api
from googlecloudapis.test.v1 import test_v1_messages as messages


class TestV1(base_api.BaseApiClient):
  """Generated client library for service test version v1."""

  MESSAGES_MODULE = messages

  _PACKAGE = u'test'
  _SCOPES = [u'https://www.googleapis.com/auth/cloud-platform']
  _VERSION = u'v1'
  _CLIENT_ID = ''
  _CLIENT_SECRET = ''
  _USER_AGENT = ''
  _CLIENT_CLASS_NAME = u'TestV1'
  _URL_VERSION = u'v1'

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new test handle."""
    url = url or u'https://test-devtools.googleapis.com/v1/'
    super(TestV1, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.projects_device = self.ProjectsDeviceService(self)
    self.projects_devices = self.ProjectsDevicesService(self)
    self.projects_testExecutions = self.ProjectsTestExecutionsService(self)
    self.projects_testMatrices = self.ProjectsTestMatricesService(self)
    self.projects = self.ProjectsService(self)
    self.testEnvironmentCatalog = self.TestEnvironmentCatalogService(self)

  class ProjectsDeviceService(base_api.BaseApiService):
    """Service class for the projects_device resource."""

    _NAME = u'projects_device'

    def __init__(self, client):
      super(TestV1.ProjectsDeviceService, self).__init__(client)
      self._method_configs = {
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'test.projects.device.delete',
              ordered_params=[u'projectId', u'deviceId'],
              path_params=[u'deviceId', u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}/device/{deviceId}',
              request_field='',
              request_type_name=u'TestProjectsDeviceDeleteRequest',
              response_type_name=u'Empty',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Delete(self, request, global_params=None):
      """Deletes a GCE Android device instance. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the project does not exist.

      Args:
        request: (TestProjectsDeviceDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Empty) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ProjectsDevicesService(base_api.BaseApiService):
    """Service class for the projects_devices resource."""

    _NAME = u'projects_devices'

    def __init__(self, client):
      super(TestV1.ProjectsDevicesService, self).__init__(client)
      self._method_configs = {
          'Create': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'test.projects.devices.create',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}/devices',
              request_field=u'device',
              request_type_name=u'TestProjectsDevicesCreateRequest',
              response_type_name=u'Device',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'test.projects.devices.get',
              ordered_params=[u'projectId', u'deviceId'],
              path_params=[u'deviceId', u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}/devices/{deviceId}',
              request_field='',
              request_type_name=u'TestProjectsDevicesGetRequest',
              response_type_name=u'Device',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'test.projects.devices.list',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[u'pageSize', u'pageToken'],
              relative_path=u'projects/{projectId}/devices',
              request_field='',
              request_type_name=u'TestProjectsDevicesListRequest',
              response_type_name=u'ListDevicesResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Create(self, request, global_params=None):
      """Creates a new GCE Android device. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to write to project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the device type or project does not exist.

      Args:
        request: (TestProjectsDevicesCreateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Device) The response message.
      """
      config = self.GetMethodConfig('Create')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Returns the GCE Android device. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the device type or project does not exist.

      Args:
        request: (TestProjectsDevicesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Device) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Lists all the current devices. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the project does not exist.

      Args:
        request: (TestProjectsDevicesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListDevicesResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ProjectsTestExecutionsService(base_api.BaseApiService):
    """Service class for the projects_testExecutions resource."""

    _NAME = u'projects_testExecutions'

    def __init__(self, client):
      super(TestV1.ProjectsTestExecutionsService, self).__init__(client)
      self._method_configs = {
          'Cancel': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'test.projects.testExecutions.cancel',
              ordered_params=[u'projectId', u'testExecutionId'],
              path_params=[u'projectId', u'testExecutionId'],
              query_params=[],
              relative_path=u'projects/{projectId}/testExecutions/{testExecutionId}:cancel',
              request_field='',
              request_type_name=u'TestProjectsTestExecutionsCancelRequest',
              response_type_name=u'CancelTestExecutionResponse',
              supports_download=False,
          ),
          'Create': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'test.projects.testExecutions.create',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}/testExecutions',
              request_field=u'testExecution',
              request_type_name=u'TestProjectsTestExecutionsCreateRequest',
              response_type_name=u'TestExecution',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'test.projects.testExecutions.delete',
              ordered_params=[u'projectId', u'testExecutionId'],
              path_params=[u'projectId', u'testExecutionId'],
              query_params=[],
              relative_path=u'projects/{projectId}/testExecutions/{testExecutionId}',
              request_field='',
              request_type_name=u'TestProjectsTestExecutionsDeleteRequest',
              response_type_name=u'Empty',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'test.projects.testExecutions.get',
              ordered_params=[u'projectId', u'testExecutionId'],
              path_params=[u'projectId', u'testExecutionId'],
              query_params=[],
              relative_path=u'projects/{projectId}/testExecutions/{testExecutionId}',
              request_field='',
              request_type_name=u'TestProjectsTestExecutionsGetRequest',
              response_type_name=u'TestExecution',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'test.projects.testExecutions.list',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[u'query'],
              relative_path=u'projects/{projectId}/testExecutions',
              request_field='',
              request_type_name=u'TestProjectsTestExecutionsListRequest',
              response_type_name=u'ListTestExecutionsResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Cancel(self, request, global_params=None):
      """Cancel an individual test execution. If the specified test execution is running it will be aborted. If it's pending then it will simply be removed from the queue. The cancelled test execution will still be visible in the results of ListTestExecutions and GetTestExecution. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the Test Execution does not exist.

      Args:
        request: (TestProjectsTestExecutionsCancelRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (CancelTestExecutionResponse) The response message.
      """
      config = self.GetMethodConfig('Cancel')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Create(self, request, global_params=None):
      """Request to execute a single test according to the given specification. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to write to project - INVALID_ARGUMENT - if the request is malformed - UNSUPPORTED - if the given test environment is not supported.

      Args:
        request: (TestProjectsTestExecutionsCreateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TestExecution) The response message.
      """
      config = self.GetMethodConfig('Create')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Delete all record of an individual test execution. The test execution will first be canceled if it is running or queued. It will no longer appear in the response from ListTestExecutions or GetTestExecution. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the Test Execution does not exist.

      Args:
        request: (TestProjectsTestExecutionsDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Empty) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Check the status of an individual test execution. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the Test Execution does not exist.

      Args:
        request: (TestProjectsTestExecutionsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TestExecution) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """List Test Executions The executions are sorted by creation_time in descending order. The test_execution_id key will be used to order the executions with the same creation_time. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed.

      Args:
        request: (TestProjectsTestExecutionsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListTestExecutionsResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ProjectsTestMatricesService(base_api.BaseApiService):
    """Service class for the projects_testMatrices resource."""

    _NAME = u'projects_testMatrices'

    def __init__(self, client):
      super(TestV1.ProjectsTestMatricesService, self).__init__(client)
      self._method_configs = {
          'Cancel': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'test.projects.testMatrices.cancel',
              ordered_params=[u'projectId', u'testMatrixId'],
              path_params=[u'projectId', u'testMatrixId'],
              query_params=[],
              relative_path=u'projects/{projectId}/testMatrices/{testMatrixId}:cancel',
              request_field='',
              request_type_name=u'TestProjectsTestMatricesCancelRequest',
              response_type_name=u'CancelTestMatrixResponse',
              supports_download=False,
          ),
          'Create': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'test.projects.testMatrices.create',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[],
              relative_path=u'projects/{projectId}/testMatrices',
              request_field=u'testMatrix',
              request_type_name=u'TestProjectsTestMatricesCreateRequest',
              response_type_name=u'TestMatrix',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'test.projects.testMatrices.delete',
              ordered_params=[u'projectId', u'testMatrixId'],
              path_params=[u'projectId', u'testMatrixId'],
              query_params=[],
              relative_path=u'projects/{projectId}/testMatrices/{testMatrixId}',
              request_field='',
              request_type_name=u'TestProjectsTestMatricesDeleteRequest',
              response_type_name=u'Empty',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'test.projects.testMatrices.get',
              ordered_params=[u'projectId', u'testMatrixId'],
              path_params=[u'projectId', u'testMatrixId'],
              query_params=[],
              relative_path=u'projects/{projectId}/testMatrices/{testMatrixId}',
              request_field='',
              request_type_name=u'TestProjectsTestMatricesGetRequest',
              response_type_name=u'TestMatrix',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'test.projects.testMatrices.list',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[u'query'],
              relative_path=u'projects/{projectId}/testMatrices',
              request_field='',
              request_type_name=u'TestProjectsTestMatricesListRequest',
              response_type_name=u'ListTestMatricesResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Cancel(self, request, global_params=None):
      """Cancel a test matrix. If the test executions associated with the matrix are running they will be aborted. If they're pending then they will simply be removed from the queue. The cancelled tests may still be queried via calls to List* and Get*. This is equivalent to calling CancelTestExecution once for each test execution in the matrix. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the Test Matrix does not exist.

      Args:
        request: (TestProjectsTestMatricesCancelRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (CancelTestMatrixResponse) The response message.
      """
      config = self.GetMethodConfig('Cancel')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Create(self, request, global_params=None):
      """Request to run a matrix of tests according to the given specifications. Unsupported environments will be ignored. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to write to project - INVALID_ARGUMENT - if the request is malformed.

      Args:
        request: (TestProjectsTestMatricesCreateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TestMatrix) The response message.
      """
      config = self.GetMethodConfig('Create')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Delete all record of a test matrix plus any associated test executions. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the Test Matrix does not exist.

      Args:
        request: (TestProjectsTestMatricesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Empty) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Check the status of a test matrix. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the Test Matrix does not exist.

      Args:
        request: (TestProjectsTestMatricesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TestMatrix) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """List test matrices. The returned matrices are currently unsorted. May return any of the following canonical error codes: - PERMISSION_DENIED - if the user is not authorized to read project - INVALID_ARGUMENT - if the request is malformed.

      Args:
        request: (TestProjectsTestMatricesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListTestMatricesResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ProjectsService(base_api.BaseApiService):
    """Service class for the projects resource."""

    _NAME = u'projects'

    def __init__(self, client):
      super(TestV1.ProjectsService, self).__init__(client)
      self._method_configs = {
          }

      self._upload_configs = {
          }

  class TestEnvironmentCatalogService(base_api.BaseApiService):
    """Service class for the testEnvironmentCatalog resource."""

    _NAME = u'testEnvironmentCatalog'

    def __init__(self, client):
      super(TestV1.TestEnvironmentCatalogService, self).__init__(client)
      self._method_configs = {
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'test.testEnvironmentCatalog.get',
              ordered_params=[u'environmentType'],
              path_params=[u'environmentType'],
              query_params=[],
              relative_path=u'testEnvironmentCatalog/{environmentType}',
              request_field='',
              request_type_name=u'TestTestEnvironmentCatalogGetRequest',
              response_type_name=u'TestEnvironmentCatalog',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Get(self, request, global_params=None):
      """Get the catalog of supported test environments. May return any of the following canonical error codes: - INVALID_ARGUMENT - if the request is malformed - NOT_FOUND - if the environment type does not exist - INTERNAL - if an internal error occurred.

      Args:
        request: (TestTestEnvironmentCatalogGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (TestEnvironmentCatalog) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)
