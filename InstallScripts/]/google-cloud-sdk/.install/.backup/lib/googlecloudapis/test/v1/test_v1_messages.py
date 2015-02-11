"""Generated message classes for test version v1.

The Test API allows developers to run automated tests for their applications
on Google infrastructure.
"""

from protorpc import messages

from googlecloudapis.apitools.base.py import encoding


package = 'test'


class AndroidDevice(messages.Message):
  """A AndroidDevice object.

  Fields:
    androidModelId: A string attribute.
    androidVersionId: A string attribute.
    locale: A string attribute.
    orientation: A string attribute.
  """

  androidModelId = messages.StringField(1)
  androidVersionId = messages.StringField(2)
  locale = messages.StringField(3)
  orientation = messages.StringField(4)


class AndroidDeviceCatalog(messages.Message):
  """A AndroidDeviceCatalog object.

  Fields:
    models: A AndroidModel attribute.
    runtimeConfiguration: A AndroidRuntimeConfiguration attribute.
    versions: A AndroidVersion attribute.
  """

  models = messages.MessageField('AndroidModel', 1, repeated=True)
  runtimeConfiguration = messages.MessageField('AndroidRuntimeConfiguration', 2)
  versions = messages.MessageField('AndroidVersion', 3, repeated=True)


class AndroidInstrumentationTest(messages.Message):
  """A AndroidInstrumentationTest object.

  Fields:
    appApk: A FileReference attribute.
    appPackageId: A string attribute.
    testApk: A FileReference attribute.
    testPackageId: A string attribute.
    testRunnerClass: A string attribute.
    testTargets: A string attribute.
  """

  appApk = messages.MessageField('FileReference', 1)
  appPackageId = messages.StringField(2)
  testApk = messages.MessageField('FileReference', 3)
  testPackageId = messages.StringField(4)
  testRunnerClass = messages.StringField(5)
  testTargets = messages.StringField(6, repeated=True)


class AndroidMatrix(messages.Message):
  """A AndroidMatrix object.

  Fields:
    androidModelIds: A string attribute.
    androidVersionIds: A string attribute.
    locales: A string attribute.
    orientations: A string attribute.
  """

  androidModelIds = messages.StringField(1, repeated=True)
  androidVersionIds = messages.StringField(2, repeated=True)
  locales = messages.StringField(3, repeated=True)
  orientations = messages.StringField(4, repeated=True)


class AndroidModel(messages.Message):
  """A AndroidModel object.

  Enums:
    FormValueValuesEnum:

  Fields:
    form: A FormValueValuesEnum attribute.
    id: A string attribute.
    manufacturer: A string attribute.
    name: A string attribute.
    screenX: A integer attribute.
    screenY: A integer attribute.
    supportedVersionIds: A string attribute.
  """

  class FormValueValuesEnum(messages.Enum):
    """FormValueValuesEnum enum type.

    Values:
      PHYSICAL: <no description>
      UNSPECIFIED: <no description>
      VIRTUAL: <no description>
    """
    PHYSICAL = 0
    UNSPECIFIED = 1
    VIRTUAL = 2

  form = messages.EnumField('FormValueValuesEnum', 1)
  id = messages.StringField(2)
  manufacturer = messages.StringField(3)
  name = messages.StringField(4)
  screenX = messages.IntegerField(5, variant=messages.Variant.INT32)
  screenY = messages.IntegerField(6, variant=messages.Variant.INT32)
  supportedVersionIds = messages.StringField(7, repeated=True)


class AndroidRuntimeConfiguration(messages.Message):
  """A AndroidRuntimeConfiguration object.

  Fields:
    locales: A Locale attribute.
    orientations: A Orientation attribute.
  """

  locales = messages.MessageField('Locale', 1, repeated=True)
  orientations = messages.MessageField('Orientation', 2, repeated=True)


class AndroidVersion(messages.Message):
  """A AndroidVersion object.

  Fields:
    apiLevel: A integer attribute.
    codeName: A string attribute.
    distribution: A Distribution attribute.
    id: A string attribute.
    releaseDate: A string attribute.
    versionString: A string attribute.
  """

  apiLevel = messages.IntegerField(1, variant=messages.Variant.INT32)
  codeName = messages.StringField(2)
  distribution = messages.MessageField('Distribution', 3)
  id = messages.StringField(4)
  releaseDate = messages.StringField(5)
  versionString = messages.StringField(6)


class BlobstoreFile(messages.Message):
  """A BlobstoreFile object.

  Fields:
    blobId: A string attribute.
    md5Hash: A string attribute.
  """

  blobId = messages.StringField(1)
  md5Hash = messages.StringField(2)


class CancelTestExecutionResponse(messages.Message):
  """A CancelTestExecutionResponse object.

  Enums:
    TestStateValueValuesEnum:

  Fields:
    testState: A TestStateValueValuesEnum attribute.
  """

  class TestStateValueValuesEnum(messages.Enum):
    """TestStateValueValuesEnum enum type.

    Values:
      ERROR: <no description>
      FINISHED: <no description>
      IN_PROGRESS: <no description>
      QUEUED: <no description>
      UNSPECIFIED_TEST_STATE: <no description>
    """
    ERROR = 0
    FINISHED = 1
    IN_PROGRESS = 2
    QUEUED = 3
    UNSPECIFIED_TEST_STATE = 4

  testState = messages.EnumField('TestStateValueValuesEnum', 1)


class CancelTestMatrixResponse(messages.Message):
  """A CancelTestMatrixResponse object.

  Enums:
    TestStateValueValuesEnum:

  Fields:
    testState: A TestStateValueValuesEnum attribute.
  """

  class TestStateValueValuesEnum(messages.Enum):
    """TestStateValueValuesEnum enum type.

    Values:
      ERROR: <no description>
      FINISHED: <no description>
      IN_PROGRESS: <no description>
      QUEUED: <no description>
      UNSPECIFIED_TEST_STATE: <no description>
    """
    ERROR = 0
    FINISHED = 1
    IN_PROGRESS = 2
    QUEUED = 3
    UNSPECIFIED_TEST_STATE = 4

  testState = messages.EnumField('TestStateValueValuesEnum', 1)


class ConnectionInfo(messages.Message):
  """A ConnectionInfo object.

  Fields:
    adbPort: A integer attribute.
    ipAddress: A string attribute.
    sshPort: A integer attribute.
    vncPassword: A string attribute.
    vncPort: A integer attribute.
  """

  adbPort = messages.IntegerField(1, variant=messages.Variant.INT32)
  ipAddress = messages.StringField(2)
  sshPort = messages.IntegerField(3, variant=messages.Variant.INT32)
  vncPassword = messages.StringField(4)
  vncPort = messages.IntegerField(5, variant=messages.Variant.INT32)


class Device(messages.Message):
  """A Device object.

  Enums:
    StateValueValuesEnum:

  Fields:
    androidDevice: A AndroidDevice attribute.
    creationTime: A string attribute.
    deviceDetails: A DeviceDetails attribute.
    id: A string attribute.
    state: A StateValueValuesEnum attribute.
    stateDetails: A DeviceStateDetails attribute.
  """

  class StateValueValuesEnum(messages.Enum):
    """StateValueValuesEnum enum type.

    Values:
      CLOSED: <no description>
      DEVICE_ERROR: <no description>
      DEVICE_UNSPECIFIED: <no description>
      PREPARING: <no description>
      READY: <no description>
    """
    CLOSED = 0
    DEVICE_ERROR = 1
    DEVICE_UNSPECIFIED = 2
    PREPARING = 3
    READY = 4

  androidDevice = messages.MessageField('AndroidDevice', 1)
  creationTime = messages.StringField(2)
  deviceDetails = messages.MessageField('DeviceDetails', 3)
  id = messages.StringField(4)
  state = messages.EnumField('StateValueValuesEnum', 5)
  stateDetails = messages.MessageField('DeviceStateDetails', 6)


class DeviceDetails(messages.Message):
  """A DeviceDetails object.

  Fields:
    connectionInfo: A ConnectionInfo attribute.
    gceInstanceDetails: A GceInstanceDetails attribute.
  """

  connectionInfo = messages.MessageField('ConnectionInfo', 1)
  gceInstanceDetails = messages.MessageField('GceInstanceDetails', 2)


class DeviceStateDetails(messages.Message):
  """A DeviceStateDetails object.

  Fields:
    errorDetails: A string attribute.
    progressDetails: A string attribute.
  """

  errorDetails = messages.StringField(1)
  progressDetails = messages.StringField(2)


class Distribution(messages.Message):
  """A Distribution object.

  Fields:
    marketShare: A number attribute.
    measurementTime: A string attribute.
  """

  marketShare = messages.FloatField(1)
  measurementTime = messages.StringField(2)


class Empty(messages.Message):
  """A Empty object."""


class Environment(messages.Message):
  """A Environment object.

  Fields:
    androidDevice: A AndroidDevice attribute.
  """

  androidDevice = messages.MessageField('AndroidDevice', 1)


class EnvironmentMatrix(messages.Message):
  """A EnvironmentMatrix object.

  Fields:
    androidMatrix: A AndroidMatrix attribute.
  """

  androidMatrix = messages.MessageField('AndroidMatrix', 1)


class FileReference(messages.Message):
  """A FileReference object.

  Fields:
    blob: A BlobstoreFile attribute.
    gcsPath: A string attribute.
  """

  blob = messages.MessageField('BlobstoreFile', 1)
  gcsPath = messages.StringField(2)


class GceInstanceDetails(messages.Message):
  """A GceInstanceDetails object.

  Fields:
    name: A string attribute.
    projectId: A string attribute.
    zone: A string attribute.
  """

  name = messages.StringField(1)
  projectId = messages.StringField(2)
  zone = messages.StringField(3)


class GoogleCloudStorage(messages.Message):
  """A GoogleCloudStorage object.

  Fields:
    gcsPath: A string attribute.
  """

  gcsPath = messages.StringField(1)


class ListDevicesResponse(messages.Message):
  """A ListDevicesResponse object.

  Fields:
    devices: A Device attribute.
    nextPageToken: A string attribute.
  """

  devices = messages.MessageField('Device', 1, repeated=True)
  nextPageToken = messages.StringField(2)


class ListTestExecutionsResponse(messages.Message):
  """A ListTestExecutionsResponse object.

  Fields:
    testExecutions: A TestExecution attribute.
  """

  testExecutions = messages.MessageField('TestExecution', 1, repeated=True)


class ListTestMatricesResponse(messages.Message):
  """A ListTestMatricesResponse object.

  Fields:
    testMatrices: A TestMatrix attribute.
  """

  testMatrices = messages.MessageField('TestMatrix', 1, repeated=True)


class Locale(messages.Message):
  """A Locale object.

  Fields:
    id: A string attribute.
    name: A string attribute.
    region: A string attribute.
  """

  id = messages.StringField(1)
  name = messages.StringField(2)
  region = messages.StringField(3)


class Orientation(messages.Message):
  """A Orientation object.

  Fields:
    id: A string attribute.
    name: A string attribute.
  """

  id = messages.StringField(1)
  name = messages.StringField(2)


class ResultStorage(messages.Message):
  """A ResultStorage object.

  Fields:
    googleCloudStorage: A GoogleCloudStorage attribute.
    toolResultsExecutionId: A string attribute.
    toolResultsHistoryId: A string attribute.
    toolResultsStepId: A string attribute.
  """

  googleCloudStorage = messages.MessageField('GoogleCloudStorage', 1)
  toolResultsExecutionId = messages.StringField(2)
  toolResultsHistoryId = messages.StringField(3)
  toolResultsStepId = messages.StringField(4)


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


class TestDetails(messages.Message):
  """A TestDetails object.

  Fields:
    errorDetails: A string attribute.
    progressDetails: A string attribute.
  """

  errorDetails = messages.StringField(1)
  progressDetails = messages.StringField(2)


class TestEnvironmentCatalog(messages.Message):
  """A TestEnvironmentCatalog object.

  Fields:
    androidDeviceCatalog: A AndroidDeviceCatalog attribute.
  """

  androidDeviceCatalog = messages.MessageField('AndroidDeviceCatalog', 1)


class TestExecution(messages.Message):
  """A TestExecution object.

  Enums:
    StateValueValuesEnum:

  Messages:
    LabelsValue: A LabelsValue object.

  Fields:
    environment: A Environment attribute.
    id: A string attribute.
    labels: A LabelsValue attribute.
    resultStorage: A ResultStorage attribute.
    state: A StateValueValuesEnum attribute.
    testDetails: A TestDetails attribute.
    testSpecification: A TestSpecification attribute.
    timestamp: A string attribute.
  """

  class StateValueValuesEnum(messages.Enum):
    """StateValueValuesEnum enum type.

    Values:
      ERROR: <no description>
      FINISHED: <no description>
      IN_PROGRESS: <no description>
      QUEUED: <no description>
      UNSPECIFIED_TEST_STATE: <no description>
    """
    ERROR = 0
    FINISHED = 1
    IN_PROGRESS = 2
    QUEUED = 3
    UNSPECIFIED_TEST_STATE = 4

  @encoding.MapUnrecognizedFields('additionalProperties')
  class LabelsValue(messages.Message):
    """A LabelsValue object.

    Messages:
      AdditionalProperty: An additional property for a LabelsValue object.

    Fields:
      additionalProperties: Additional properties of type LabelsValue
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a LabelsValue object.

      Fields:
        key: Name of the additional property.
        value: A string attribute.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  environment = messages.MessageField('Environment', 1)
  id = messages.StringField(2)
  labels = messages.MessageField('LabelsValue', 3)
  resultStorage = messages.MessageField('ResultStorage', 4)
  state = messages.EnumField('StateValueValuesEnum', 5)
  testDetails = messages.MessageField('TestDetails', 6)
  testSpecification = messages.MessageField('TestSpecification', 7)
  timestamp = messages.StringField(8)


class TestMatrix(messages.Message):
  """A TestMatrix object.

  Messages:
    LabelsValue: A LabelsValue object.

  Fields:
    environmentMatrix: A EnvironmentMatrix attribute.
    labels: A LabelsValue attribute.
    resultStorage: A ResultStorage attribute.
    testExecutions: A TestExecution attribute.
    testMatrixId: A string attribute.
    testSpecification: A TestSpecification attribute.
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class LabelsValue(messages.Message):
    """A LabelsValue object.

    Messages:
      AdditionalProperty: An additional property for a LabelsValue object.

    Fields:
      additionalProperties: Additional properties of type LabelsValue
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a LabelsValue object.

      Fields:
        key: Name of the additional property.
        value: A string attribute.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  environmentMatrix = messages.MessageField('EnvironmentMatrix', 1)
  labels = messages.MessageField('LabelsValue', 2)
  resultStorage = messages.MessageField('ResultStorage', 3)
  testExecutions = messages.MessageField('TestExecution', 4, repeated=True)
  testMatrixId = messages.StringField(5)
  testSpecification = messages.MessageField('TestSpecification', 6)


class TestProjectsDeviceDeleteRequest(messages.Message):
  """A TestProjectsDeviceDeleteRequest object.

  Fields:
    deviceId: A string attribute.
    projectId: A string attribute.
  """

  deviceId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)


class TestProjectsDevicesCreateRequest(messages.Message):
  """A TestProjectsDevicesCreateRequest object.

  Fields:
    device: A Device resource to be passed as the request body.
    projectId: A string attribute.
  """

  device = messages.MessageField('Device', 1)
  projectId = messages.StringField(2, required=True)


class TestProjectsDevicesGetRequest(messages.Message):
  """A TestProjectsDevicesGetRequest object.

  Fields:
    deviceId: A string attribute.
    projectId: A string attribute.
  """

  deviceId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)


class TestProjectsDevicesListRequest(messages.Message):
  """A TestProjectsDevicesListRequest object.

  Fields:
    pageSize: A integer attribute.
    pageToken: A string attribute.
    projectId: A string attribute.
  """

  pageSize = messages.IntegerField(1, variant=messages.Variant.INT32)
  pageToken = messages.StringField(2)
  projectId = messages.StringField(3, required=True)


class TestProjectsTestExecutionsCancelRequest(messages.Message):
  """A TestProjectsTestExecutionsCancelRequest object.

  Fields:
    projectId: A string attribute.
    testExecutionId: A string attribute.
  """

  projectId = messages.StringField(1, required=True)
  testExecutionId = messages.StringField(2, required=True)


class TestProjectsTestExecutionsCreateRequest(messages.Message):
  """A TestProjectsTestExecutionsCreateRequest object.

  Fields:
    projectId: A string attribute.
    testExecution: A TestExecution resource to be passed as the request body.
  """

  projectId = messages.StringField(1, required=True)
  testExecution = messages.MessageField('TestExecution', 2)


class TestProjectsTestExecutionsDeleteRequest(messages.Message):
  """A TestProjectsTestExecutionsDeleteRequest object.

  Fields:
    projectId: A string attribute.
    testExecutionId: A string attribute.
  """

  projectId = messages.StringField(1, required=True)
  testExecutionId = messages.StringField(2, required=True)


class TestProjectsTestExecutionsGetRequest(messages.Message):
  """A TestProjectsTestExecutionsGetRequest object.

  Fields:
    projectId: A string attribute.
    testExecutionId: A string attribute.
  """

  projectId = messages.StringField(1, required=True)
  testExecutionId = messages.StringField(2, required=True)


class TestProjectsTestExecutionsListRequest(messages.Message):
  """A TestProjectsTestExecutionsListRequest object.

  Fields:
    projectId: A string attribute.
    query: A string attribute.
  """

  projectId = messages.StringField(1, required=True)
  query = messages.StringField(2)


class TestProjectsTestMatricesCancelRequest(messages.Message):
  """A TestProjectsTestMatricesCancelRequest object.

  Fields:
    projectId: A string attribute.
    testMatrixId: A string attribute.
  """

  projectId = messages.StringField(1, required=True)
  testMatrixId = messages.StringField(2, required=True)


class TestProjectsTestMatricesCreateRequest(messages.Message):
  """A TestProjectsTestMatricesCreateRequest object.

  Fields:
    projectId: A string attribute.
    testMatrix: A TestMatrix resource to be passed as the request body.
  """

  projectId = messages.StringField(1, required=True)
  testMatrix = messages.MessageField('TestMatrix', 2)


class TestProjectsTestMatricesDeleteRequest(messages.Message):
  """A TestProjectsTestMatricesDeleteRequest object.

  Fields:
    projectId: A string attribute.
    testMatrixId: A string attribute.
  """

  projectId = messages.StringField(1, required=True)
  testMatrixId = messages.StringField(2, required=True)


class TestProjectsTestMatricesGetRequest(messages.Message):
  """A TestProjectsTestMatricesGetRequest object.

  Fields:
    projectId: A string attribute.
    testMatrixId: A string attribute.
  """

  projectId = messages.StringField(1, required=True)
  testMatrixId = messages.StringField(2, required=True)


class TestProjectsTestMatricesListRequest(messages.Message):
  """A TestProjectsTestMatricesListRequest object.

  Fields:
    projectId: A string attribute.
    query: A string attribute.
  """

  projectId = messages.StringField(1, required=True)
  query = messages.StringField(2)


class TestSpecification(messages.Message):
  """A TestSpecification object.

  Fields:
    androidInstrumentationTest: A AndroidInstrumentationTest attribute.
    testTimeout: A string attribute.
  """

  androidInstrumentationTest = messages.MessageField('AndroidInstrumentationTest', 1)
  testTimeout = messages.StringField(2)


class TestTestEnvironmentCatalogGetRequest(messages.Message):
  """A TestTestEnvironmentCatalogGetRequest object.

  Enums:
    EnvironmentTypeValueValuesEnum:

  Fields:
    environmentType: A EnvironmentTypeValueValuesEnum attribute.
  """

  class EnvironmentTypeValueValuesEnum(messages.Enum):
    """EnvironmentTypeValueValuesEnum enum type.

    Values:
      ANDROID: <no description>
      UNSPECIFIED: <no description>
    """
    ANDROID = 0
    UNSPECIFIED = 1

  environmentType = messages.EnumField('EnvironmentTypeValueValuesEnum', 1, required=True)


