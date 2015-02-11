"""Generated client library for dns version v1beta1."""

from googlecloudapis.apitools.base.py import base_api
from googlecloudapis.dns.v1beta1 import dns_v1beta1_messages as messages


class DnsV1beta1(base_api.BaseApiClient):
  """Generated client library for service dns version v1beta1."""

  MESSAGES_MODULE = messages

  _PACKAGE = u'dns'
  _SCOPES = [u'https://www.googleapis.com/auth/cloud-platform', u'https://www.googleapis.com/auth/ndev.clouddns.readonly', u'https://www.googleapis.com/auth/ndev.clouddns.readwrite']
  _VERSION = u'v1beta1'
  _CLIENT_ID = ''
  _CLIENT_SECRET = ''
  _USER_AGENT = ''
  _CLIENT_CLASS_NAME = u'DnsV1beta1'
  _URL_VERSION = u'v1beta1'

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new dns handle."""
    url = url or u'https://www.googleapis.com/dns/v1beta1/'
    super(DnsV1beta1, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.changes = self.ChangesService(self)
    self.managedZones = self.ManagedZonesService(self)
    self.projects = self.ProjectsService(self)
    self.resourceRecordSets = self.ResourceRecordSetsService(self)

  class ChangesService(base_api.BaseApiService):
    """Service class for the changes resource."""

    _NAME = u'changes'

    def __init__(self, client):
      super(DnsV1beta1.ChangesService, self).__init__(client)
      self._method_configs = {
          'Create': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'dns.changes.create',
              ordered_params=[u'project', u'managedZone'],
              path_params=[u'managedZone', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/managedZones/{managedZone}/changes',
              request_field=u'change',
              request_type_name=u'DnsChangesCreateRequest',
              response_type_name=u'Change',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'dns.changes.get',
              ordered_params=[u'project', u'managedZone', u'changeId'],
              path_params=[u'changeId', u'managedZone', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/managedZones/{managedZone}/changes/{changeId}',
              request_field='',
              request_type_name=u'DnsChangesGetRequest',
              response_type_name=u'Change',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'dns.changes.list',
              ordered_params=[u'project', u'managedZone'],
              path_params=[u'managedZone', u'project'],
              query_params=[u'maxResults', u'pageToken', u'sortBy', u'sortOrder'],
              relative_path=u'projects/{project}/managedZones/{managedZone}/changes',
              request_field='',
              request_type_name=u'DnsChangesListRequest',
              response_type_name=u'ChangesListResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Create(self, request, global_params=None):
      """Atomically update the ResourceRecordSet collection.

      Args:
        request: (DnsChangesCreateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Change) The response message.
      """
      config = self.GetMethodConfig('Create')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Fetch the representation of an existing Change.

      Args:
        request: (DnsChangesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Change) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Enumerate Changes to a ResourceRecordSet collection.

      Args:
        request: (DnsChangesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ChangesListResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ManagedZonesService(base_api.BaseApiService):
    """Service class for the managedZones resource."""

    _NAME = u'managedZones'

    def __init__(self, client):
      super(DnsV1beta1.ManagedZonesService, self).__init__(client)
      self._method_configs = {
          'Create': base_api.ApiMethodInfo(
              http_method=u'POST',
              method_id=u'dns.managedZones.create',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}/managedZones',
              request_field=u'managedZone',
              request_type_name=u'DnsManagedZonesCreateRequest',
              response_type_name=u'ManagedZone',
              supports_download=False,
          ),
          'Delete': base_api.ApiMethodInfo(
              http_method=u'DELETE',
              method_id=u'dns.managedZones.delete',
              ordered_params=[u'project', u'managedZone'],
              path_params=[u'managedZone', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/managedZones/{managedZone}',
              request_field='',
              request_type_name=u'DnsManagedZonesDeleteRequest',
              response_type_name=u'DnsManagedZonesDeleteResponse',
              supports_download=False,
          ),
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'dns.managedZones.get',
              ordered_params=[u'project', u'managedZone'],
              path_params=[u'managedZone', u'project'],
              query_params=[],
              relative_path=u'projects/{project}/managedZones/{managedZone}',
              request_field='',
              request_type_name=u'DnsManagedZonesGetRequest',
              response_type_name=u'ManagedZone',
              supports_download=False,
          ),
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'dns.managedZones.list',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[u'maxResults', u'pageToken'],
              relative_path=u'projects/{project}/managedZones',
              request_field='',
              request_type_name=u'DnsManagedZonesListRequest',
              response_type_name=u'ManagedZonesListResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Create(self, request, global_params=None):
      """Create a new ManagedZone.

      Args:
        request: (DnsManagedZonesCreateRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ManagedZone) The response message.
      """
      config = self.GetMethodConfig('Create')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Delete(self, request, global_params=None):
      """Delete a previously created ManagedZone.

      Args:
        request: (DnsManagedZonesDeleteRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (DnsManagedZonesDeleteResponse) The response message.
      """
      config = self.GetMethodConfig('Delete')
      return self._RunMethod(
          config, request, global_params=global_params)

    def Get(self, request, global_params=None):
      """Fetch the representation of an existing ManagedZone.

      Args:
        request: (DnsManagedZonesGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ManagedZone) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

    def List(self, request, global_params=None):
      """Enumerate ManagedZones that have been created but not yet deleted.

      Args:
        request: (DnsManagedZonesListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ManagedZonesListResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ProjectsService(base_api.BaseApiService):
    """Service class for the projects resource."""

    _NAME = u'projects'

    def __init__(self, client):
      super(DnsV1beta1.ProjectsService, self).__init__(client)
      self._method_configs = {
          'Get': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'dns.projects.get',
              ordered_params=[u'project'],
              path_params=[u'project'],
              query_params=[],
              relative_path=u'projects/{project}',
              request_field='',
              request_type_name=u'DnsProjectsGetRequest',
              response_type_name=u'Project',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def Get(self, request, global_params=None):
      """Fetch the representation of an existing Project.

      Args:
        request: (DnsProjectsGetRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (Project) The response message.
      """
      config = self.GetMethodConfig('Get')
      return self._RunMethod(
          config, request, global_params=global_params)

  class ResourceRecordSetsService(base_api.BaseApiService):
    """Service class for the resourceRecordSets resource."""

    _NAME = u'resourceRecordSets'

    def __init__(self, client):
      super(DnsV1beta1.ResourceRecordSetsService, self).__init__(client)
      self._method_configs = {
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'dns.resourceRecordSets.list',
              ordered_params=[u'project', u'managedZone'],
              path_params=[u'managedZone', u'project'],
              query_params=[u'maxResults', u'name', u'pageToken', u'type'],
              relative_path=u'projects/{project}/managedZones/{managedZone}/rrsets',
              request_field='',
              request_type_name=u'DnsResourceRecordSetsListRequest',
              response_type_name=u'ResourceRecordSetsListResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def List(self, request, global_params=None):
      """Enumerate ResourceRecordSets that have been created but not yet deleted.

      Args:
        request: (DnsResourceRecordSetsListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ResourceRecordSetsListResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)
