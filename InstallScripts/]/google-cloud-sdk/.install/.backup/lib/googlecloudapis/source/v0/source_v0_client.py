"""Generated client library for source version v0."""

from googlecloudapis.apitools.base.py import base_api
from googlecloudapis.source.v0 import source_v0_messages as messages


class SourceV0(base_api.BaseApiClient):
  """Generated client library for service source version v0."""

  MESSAGES_MODULE = messages

  _PACKAGE = u'source'
  _SCOPES = [u'https://www.googleapis.com/auth/projecthosting']
  _VERSION = u'v0'
  _CLIENT_ID = ''
  _CLIENT_SECRET = ''
  _USER_AGENT = ''
  _CLIENT_CLASS_NAME = u'SourceV0'
  _URL_VERSION = u'v0'

  def __init__(self, url='', credentials=None,
               get_credentials=True, http=None, model=None,
               log_request=False, log_response=False,
               credentials_args=None, default_global_params=None,
               additional_http_headers=None):
    """Create a new source handle."""
    url = url or u'https://www.googleapis.com/source/v0/'
    super(SourceV0, self).__init__(
        url, credentials=credentials,
        get_credentials=get_credentials, http=http, model=model,
        log_request=log_request, log_response=log_response,
        credentials_args=credentials_args,
        default_global_params=default_global_params,
        additional_http_headers=additional_http_headers)
    self.repos = self.ReposService(self)

  class ReposService(base_api.BaseApiService):
    """Service class for the repos resource."""

    _NAME = u'repos'

    def __init__(self, client):
      super(SourceV0.ReposService, self).__init__(client)
      self._method_configs = {
          'List': base_api.ApiMethodInfo(
              http_method=u'GET',
              method_id=u'source.repos.list',
              ordered_params=[u'projectId'],
              path_params=[u'projectId'],
              query_params=[],
              relative_path=u'{projectId}',
              request_field='',
              request_type_name=u'SourceReposListRequest',
              response_type_name=u'ListReposResponse',
              supports_download=False,
          ),
          }

      self._upload_configs = {
          }

    def List(self, request, global_params=None):
      """List Repos belonging to a project.

      Args:
        request: (SourceReposListRequest) input message
        global_params: (StandardQueryParameters, default: None) global arguments
      Returns:
        (ListReposResponse) The response message.
      """
      config = self.GetMethodConfig('List')
      return self._RunMethod(
          config, request, global_params=global_params)
