"""Generated message classes for deploymentmanager version v2beta1.

The Deployment Manager API allows users to declaratively configure, deploy and
run complex solutions on the Google Cloud Platform.
"""

from protorpc import messages


package = 'deploymentmanager'


class Deployment(messages.Message):
  """A Deployment object.

  Fields:
    description: An optional user-provided description of the deployment.
    id: [Output Only] Unique identifier for the resource; defined by the
      server.
    manifest: [Output Only] URL of the manifest representing the full
      configuration of this deployment.
    name: The name of the deployment, which must be unique within the project.
    targetConfig: [Input Only] The YAML configuration to use in processing
      this deployment.  When you create a deployment, the server creates a new
      manifest with the given YAML configuration and sets the `manifest`
      property to the URL of the manifest resource.
  """

  description = messages.StringField(1)
  id = messages.IntegerField(2, variant=messages.Variant.UINT64)
  manifest = messages.StringField(3)
  name = messages.StringField(4)
  targetConfig = messages.StringField(5)


class DeploymentmanagerDeploymentsDeleteRequest(messages.Message):
  """A DeploymentmanagerDeploymentsDeleteRequest object.

  Fields:
    deployment: The name of the deployment for this request.
    project: The project ID for this request.
  """

  deployment = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class DeploymentmanagerDeploymentsGetRequest(messages.Message):
  """A DeploymentmanagerDeploymentsGetRequest object.

  Fields:
    deployment: The name of the deployment for this request.
    project: The project ID for this request.
  """

  deployment = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class DeploymentmanagerDeploymentsInsertRequest(messages.Message):
  """A DeploymentmanagerDeploymentsInsertRequest object.

  Fields:
    deployment: A Deployment resource to be passed as the request body.
    project: The project ID for this request.
  """

  deployment = messages.MessageField('Deployment', 1)
  project = messages.StringField(2, required=True)


class DeploymentmanagerDeploymentsListRequest(messages.Message):
  """A DeploymentmanagerDeploymentsListRequest object.

  Fields:
    maxResults: Maximum count of results to be returned. Acceptable values are
      0 to 100, inclusive. (Default: 50)
    pageToken: Specifies a nextPageToken returned by a previous list request.
      This token can be used to request the next page of results from a
      previous list request.
    project: The project ID for this request.
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.INT32, default=50)
  pageToken = messages.StringField(2)
  project = messages.StringField(3, required=True)


class DeploymentmanagerManifestsGetRequest(messages.Message):
  """A DeploymentmanagerManifestsGetRequest object.

  Fields:
    deployment: The name of the deployment for this request.
    manifest: The name of the manifest for this request.
    project: The project ID for this request.
  """

  deployment = messages.StringField(1, required=True)
  manifest = messages.StringField(2, required=True)
  project = messages.StringField(3, required=True)


class DeploymentmanagerManifestsListRequest(messages.Message):
  """A DeploymentmanagerManifestsListRequest object.

  Fields:
    deployment: The name of the deployment for this request.
    maxResults: Maximum count of results to be returned. Acceptable values are
      0 to 100, inclusive. (Default: 50)
    pageToken: Specifies a nextPageToken returned by a previous list request.
      This token can be used to request the next page of results from a
      previous list request.
    project: The project ID for this request.
  """

  deployment = messages.StringField(1, required=True)
  maxResults = messages.IntegerField(2, variant=messages.Variant.INT32, default=50)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class DeploymentmanagerOperationsGetRequest(messages.Message):
  """A DeploymentmanagerOperationsGetRequest object.

  Fields:
    operation: The name of the operation for this request.
    project: The project ID for this request.
  """

  operation = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class DeploymentmanagerOperationsListRequest(messages.Message):
  """A DeploymentmanagerOperationsListRequest object.

  Fields:
    maxResults: Maximum count of results to be returned. Acceptable values are
      0 to 100, inclusive. (Default: 50)
    pageToken: Specifies a nextPageToken returned by a previous list request.
      This token can be used to request the next page of results from a
      previous list request.
    project: The project ID for this request.
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.INT32, default=50)
  pageToken = messages.StringField(2)
  project = messages.StringField(3, required=True)


class DeploymentmanagerResourcesGetRequest(messages.Message):
  """A DeploymentmanagerResourcesGetRequest object.

  Fields:
    deployment: The name of the deployment for this request.
    project: The project ID for this request.
    resource: The name of the resource for this request.
  """

  deployment = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  resource = messages.StringField(3, required=True)


class DeploymentmanagerResourcesListRequest(messages.Message):
  """A DeploymentmanagerResourcesListRequest object.

  Fields:
    deployment: The name of the deployment for this request.
    maxResults: Maximum count of results to be returned. Acceptable values are
      0 to 100, inclusive. (Default: 50)
    pageToken: Specifies a nextPageToken returned by a previous list request.
      This token can be used to request the next page of results from a
      previous list request.
    project: The project ID for this request.
  """

  deployment = messages.StringField(1, required=True)
  maxResults = messages.IntegerField(2, variant=messages.Variant.INT32, default=50)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class DeploymentmanagerTypesListRequest(messages.Message):
  """A DeploymentmanagerTypesListRequest object.

  Fields:
    maxResults: Maximum count of results to be returned. Acceptable values are
      0 to 100, inclusive. (Default: 50)
    pageToken: Specifies a nextPageToken returned by a previous list request.
      This token can be used to request the next page of results from a
      previous list request.
    project: The project ID for this request.
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.INT32, default=50)
  pageToken = messages.StringField(2)
  project = messages.StringField(3, required=True)


class DeploymentsListResponse(messages.Message):
  """A response containing a partial list of deployments and a page token used
  to build the next request if the request has been truncated.

  Fields:
    deployments: The deployments contained in this response.
    nextPageToken: A token used to continue a truncated list request.
  """

  deployments = messages.MessageField('Deployment', 1, repeated=True)
  nextPageToken = messages.StringField(2)


class Manifest(messages.Message):
  """A Manifest object.

  Fields:
    config: The YAML configuration for this manifest.
    evaluatedConfig: [Output Only] The fully-expanded configuration file,
      including any templates and references.
    id: [Output Only] Unique identifier for the resource; defined by the
      server.
    name: [Output Only] The name of the manifest.
    selfLink: [Output Only] Self link for the manifest.
  """

  config = messages.StringField(1)
  evaluatedConfig = messages.StringField(2)
  id = messages.IntegerField(3, variant=messages.Variant.UINT64)
  name = messages.StringField(4)
  selfLink = messages.StringField(5)


class ManifestsListResponse(messages.Message):
  """A response containing a partial list of manifests and a page token used
  to build the next request if the request has been truncated.

  Fields:
    manifests: Manifests contained in this list response.
    nextPageToken: A token used to continue a truncated list request.
  """

  manifests = messages.MessageField('Manifest', 1, repeated=True)
  nextPageToken = messages.StringField(2)


class Operation(messages.Message):
  """An operation resource, used to manage asynchronous API requests.

  Messages:
    ErrorValue: [Output Only] If errors occurred during processing of this
      operation, this field will be populated.
    WarningsValueListEntry: A WarningsValueListEntry object.

  Fields:
    creationTimestamp: [Output Only] Creation timestamp in RFC3339 text
      format.
    endTime: [Output Only] The time that this operation was completed. This is
      in RFC3339 format.
    error: [Output Only] If errors occurred during processing of this
      operation, this field will be populated.
    httpErrorMessage: [Output Only] If operation fails, the HTTP error message
      returned, e.g. NOT FOUND.
    httpErrorStatusCode: [Output Only] If operation fails, the HTTP error
      status code returned, e.g. 404.
    id: [Output Only] Unique identifier for the resource; defined by the
      server.
    insertTime: [Output Only] The time that this operation was requested. This
      is in RFC 3339 format.
    name: [Output Only] Name of the operation.
    operationType: [Output Only] Type of the operation. Examples include
      "insert", or "delete"
    progress: [Output Only] An optional progress indicator that ranges from 0
      to 100. There is no requirement that this be linear or support any
      granularity of operations. This should not be used to guess at when the
      operation will be complete. This number should be monotonically
      increasing as the operation progresses.
    selfLink: [Output Only] Self link for the manifest.
    startTime: [Output Only] The time that this operation was started by the
      server. This is in RFC 3339 format.
    status: [Output Only] Status of the operation. Can be one of the
      following: "PENDING", "RUNNING", or "DONE".
    statusMessage: [Output Only] An optional textual description of the
      current status of the operation.
    targetId: [Output Only] Unique target id which identifies a particular
      incarnation of the target.
    targetLink: [Output Only] URL of the resource the operation is mutating.
    user: [Output Only] User who requested the operation, for example
      "user@example.com"
    warnings: [Output Only] If warning messages generated during processing of
      this operation, this field will be populated.
  """

  class ErrorValue(messages.Message):
    """[Output Only] If errors occurred during processing of this operation,
    this field will be populated.

    Messages:
      ErrorsValueListEntry: A ErrorsValueListEntry object.

    Fields:
      errors: The array of errors encountered while processing this operation.
    """

    class ErrorsValueListEntry(messages.Message):
      """A ErrorsValueListEntry object.

      Fields:
        code: The error type identifier for this error.
        location: Indicates the field in the request which caused the error.
          This property is optional.
        message: An optional, human-readable error message.
      """

      code = messages.StringField(1)
      location = messages.StringField(2)
      message = messages.StringField(3)

    errors = messages.MessageField('ErrorsValueListEntry', 1, repeated=True)

  class WarningsValueListEntry(messages.Message):
    """A WarningsValueListEntry object.

    Messages:
      DataValueListEntry: A DataValueListEntry object.

    Fields:
      code: The warning type identifier for this warning.
      data: Metadata for this warning in 'key: value' format.
      message: Optional human-readable details for this warning.
    """

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: A key for the warning data.
        value: A warning data value corresponding to the key.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.MessageField('extra_types.JsonValue', 1)
    data = messages.MessageField('DataValueListEntry', 2, repeated=True)
    message = messages.StringField(3)

  creationTimestamp = messages.StringField(1)
  endTime = messages.StringField(2)
  error = messages.MessageField('ErrorValue', 3)
  httpErrorMessage = messages.StringField(4)
  httpErrorStatusCode = messages.IntegerField(5, variant=messages.Variant.INT32)
  id = messages.IntegerField(6, variant=messages.Variant.UINT64)
  insertTime = messages.StringField(7)
  name = messages.StringField(8)
  operationType = messages.StringField(9)
  progress = messages.IntegerField(10, variant=messages.Variant.INT32)
  selfLink = messages.StringField(11)
  startTime = messages.StringField(12)
  status = messages.StringField(13)
  statusMessage = messages.StringField(14)
  targetId = messages.IntegerField(15, variant=messages.Variant.UINT64)
  targetLink = messages.StringField(16)
  user = messages.StringField(17)
  warnings = messages.MessageField('WarningsValueListEntry', 18, repeated=True)


class OperationsListResponse(messages.Message):
  """A response containing a partial list of operations and a page token used
  to build the next request if the request has been truncated.

  Fields:
    nextPageToken: A token used to continue a truncated list request.
    operations: Operations contained in this list response.
  """

  nextPageToken = messages.StringField(1)
  operations = messages.MessageField('Operation', 2, repeated=True)


class Resource(messages.Message):
  """A Resource object.

  Fields:
    errors: [Output Only] A list of any errors that occurred during
      deployment.
    id: [Output Only] Unique identifier for the resource; defined by the
      server.
    intent: [Output Only] The intended state of the resource.
    manifest: [Output Only] URL of the manifest representing the current
      configuration of this resource.
    name: [Output Only] The name of the resource as it appears in the YAML
      config.
    state: [Output Only] The state of the resource.
    type: [Output Only] The type of the resource, for example
      ?compute.v1.instance?, or ?replicaPools.v1beta2.instanceGroupManager?
    url: [Output Only] The URL of the actual resource.
  """

  errors = messages.StringField(1, repeated=True)
  id = messages.IntegerField(2, variant=messages.Variant.UINT64)
  intent = messages.StringField(3)
  manifest = messages.StringField(4)
  name = messages.StringField(5)
  state = messages.StringField(6)
  type = messages.StringField(7)
  url = messages.StringField(8)


class ResourcesListResponse(messages.Message):
  """A response containing a partial list of resources and a page token used
  to build the next request if the request has been truncated.

  Fields:
    nextPageToken: A token used to continue a truncated list request.
    resources: Resources contained in this list response.
  """

  nextPageToken = messages.StringField(1)
  resources = messages.MessageField('Resource', 2, repeated=True)


class StandardQueryParameters(messages.Message):
  """Query parameters accepted by all methods.

  Enums:
    AltValueValuesEnum: Data format for the response.

  Fields:
    alt: Data format for the response.
    fields: Selector specifying which fields to include in a partial response.
    key: API key. Your API key identifies your project and provides you with
      API access, quota, and reports. Required unless you provide an OAuth 2.0
      token.
    oauth_token: OAuth 2.0 token for the current user.
    prettyPrint: Returns response with indentations and line breaks.
    quotaUser: Available to use for quota purposes for server-side
      applications. Can be any arbitrary string assigned to a user, but should
      not exceed 40 characters. Overrides userIp if both are provided.
    trace: A tracing token of the form "token:<tokenid>" or "email:<ldap>" to
      include in api requests.
    userIp: IP address of the site where the request originates. Use this if
      you want to enforce per-user limits.
  """

  class AltValueValuesEnum(messages.Enum):
    """Data format for the response.

    Values:
      json: Responses with Content-Type of application/json
    """
    json = 0

  alt = messages.EnumField('AltValueValuesEnum', 1, default=u'json')
  fields = messages.StringField(2)
  key = messages.StringField(3)
  oauth_token = messages.StringField(4)
  prettyPrint = messages.BooleanField(5, default=True)
  quotaUser = messages.StringField(6)
  trace = messages.StringField(7)
  userIp = messages.StringField(8)


class Type(messages.Message):
  """A type supported by Deployment Manager.

  Fields:
    name: Name of the type.
  """

  name = messages.StringField(1)


class TypesListResponse(messages.Message):
  """A response that returns all Types supported by Deployment Manager

  Fields:
    types: Types supported by Deployment Manager
  """

  types = messages.MessageField('Type', 1, repeated=True)


