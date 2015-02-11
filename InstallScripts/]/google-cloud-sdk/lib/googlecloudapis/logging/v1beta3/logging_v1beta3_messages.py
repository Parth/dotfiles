"""Generated message classes for logging version v1beta3.

Google Cloud Logging API lets you manage logs, ingest and retrieve log entries
within a log, and manage log sinks and metrics.
"""

from protorpc import messages

from googlecloudapis.apitools.base.py import encoding


package = 'logging'


class Empty(messages.Message):
  """A Empty object."""


class ListLogEntriesResponse(messages.Message):
  """A ListLogEntriesResponse object.

  Fields:
    entries: A LogEntry attribute.
    nextPageToken: A string attribute.
  """

  entries = messages.MessageField('LogEntry', 1, repeated=True)
  nextPageToken = messages.StringField(2)


class ListLogMetricsResponse(messages.Message):
  """A ListLogMetricsResponse object.

  Fields:
    metrics: A LogMetric attribute.
    nextPageToken: A string attribute.
  """

  metrics = messages.MessageField('LogMetric', 1, repeated=True)
  nextPageToken = messages.StringField(2)


class ListLogServiceIndexesResponse(messages.Message):
  """A ListLogServiceIndexesResponse object.

  Fields:
    nextPageToken: A string attribute.
    serviceIndexPrefixes: A string attribute.
  """

  nextPageToken = messages.StringField(1)
  serviceIndexPrefixes = messages.StringField(2, repeated=True)


class ListLogServiceSinksResponse(messages.Message):
  """A ListLogServiceSinksResponse object.

  Fields:
    sinks: A LogSink attribute.
  """

  sinks = messages.MessageField('LogSink', 1, repeated=True)


class ListLogServicesResponse(messages.Message):
  """A ListLogServicesResponse object.

  Fields:
    logServices: A LogService attribute.
    nextPageToken: A string attribute.
  """

  logServices = messages.MessageField('LogService', 1, repeated=True)
  nextPageToken = messages.StringField(2)


class ListLogSinksResponse(messages.Message):
  """A ListLogSinksResponse object.

  Fields:
    sinks: A LogSink attribute.
  """

  sinks = messages.MessageField('LogSink', 1, repeated=True)


class ListLogsResponse(messages.Message):
  """A ListLogsResponse object.

  Fields:
    logs: A Log attribute.
    nextPageToken: A string attribute.
  """

  logs = messages.MessageField('Log', 1, repeated=True)
  nextPageToken = messages.StringField(2)


class Log(messages.Message):
  """A Log object.

  Fields:
    displayName: A string attribute.
    name: A string attribute.
    payloadType: A string attribute.
  """

  displayName = messages.StringField(1)
  name = messages.StringField(2)
  payloadType = messages.StringField(3)


class LogEntry(messages.Message):
  """A LogEntry object.

  Messages:
    ProtoPayloadValue: A ProtoPayloadValue object.

  Fields:
    insertId: A string attribute.
    log: A string attribute.
    metadata: A LogEntryMetadata attribute.
    protoPayload: A ProtoPayloadValue attribute.
    textPayload: A string attribute.
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ProtoPayloadValue(messages.Message):
    """A ProtoPayloadValue object.

    Messages:
      AdditionalProperty: An additional property for a ProtoPayloadValue
        object.

    Fields:
      additionalProperties: Additional properties of type ProtoPayloadValue
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a ProtoPayloadValue object.

      Fields:
        key: Name of the additional property.
        value: A extra_types.JsonValue attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('extra_types.JsonValue', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  insertId = messages.StringField(1)
  log = messages.StringField(2)
  metadata = messages.MessageField('LogEntryMetadata', 3)
  protoPayload = messages.MessageField('ProtoPayloadValue', 4)
  textPayload = messages.StringField(5)


class LogEntryMetadata(messages.Message):
  """A LogEntryMetadata object.

  Enums:
    SeverityValueValuesEnum:

  Messages:
    LabelsValue: A LabelsValue object.

  Fields:
    labels: A LabelsValue attribute.
    projectId: A string attribute.
    projectNumber: A string attribute.
    region: A string attribute.
    serviceName: A string attribute.
    severity: A SeverityValueValuesEnum attribute.
    timeNanos: A string attribute.
    timestamp: A string attribute.
    userId: A string attribute.
    zone: A string attribute.
  """

  class SeverityValueValuesEnum(messages.Enum):
    """SeverityValueValuesEnum enum type.

    Values:
      ALERT: <no description>
      CRITICAL: <no description>
      DEBUG: <no description>
      DEFAULT: <no description>
      EMERGENCY: <no description>
      ERROR: <no description>
      INFO: <no description>
      NOTICE: <no description>
      WARNING: <no description>
    """
    ALERT = 0
    CRITICAL = 1
    DEBUG = 2
    DEFAULT = 3
    EMERGENCY = 4
    ERROR = 5
    INFO = 6
    NOTICE = 7
    WARNING = 8

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

  labels = messages.MessageField('LabelsValue', 1)
  projectId = messages.StringField(2)
  projectNumber = messages.IntegerField(3)
  region = messages.StringField(4)
  serviceName = messages.StringField(5)
  severity = messages.EnumField('SeverityValueValuesEnum', 6)
  timeNanos = messages.IntegerField(7)
  timestamp = messages.StringField(8)
  userId = messages.StringField(9)
  zone = messages.StringField(10)


class LogError(messages.Message):
  """A LogError object.

  Fields:
    resource: A string attribute.
    status: A Status attribute.
    timeNanos: A string attribute.
  """

  resource = messages.StringField(1)
  status = messages.MessageField('Status', 2)
  timeNanos = messages.IntegerField(3)


class LogMetric(messages.Message):
  """A LogMetric object.

  Fields:
    description: A string attribute.
    filter: A string attribute.
    name: A string attribute.
  """

  description = messages.StringField(1)
  filter = messages.StringField(2)
  name = messages.StringField(3)


class LogService(messages.Message):
  """A LogService object.

  Fields:
    indexKeys: A string attribute.
    name: A string attribute.
  """

  indexKeys = messages.StringField(1, repeated=True)
  name = messages.StringField(2)


class LogSink(messages.Message):
  """A LogSink object.

  Fields:
    destination: A string attribute.
    errors: A LogError attribute.
    name: A string attribute.
  """

  destination = messages.StringField(1)
  errors = messages.MessageField('LogError', 2, repeated=True)
  name = messages.StringField(3)


class LoggingProjectsLogEntriesListRequest(messages.Message):
  """A LoggingProjectsLogEntriesListRequest object.

  Fields:
    filter: A string attribute.
    orderBy: A string attribute.
    pageSize: A integer attribute.
    pageToken: A string attribute.
    projectId: A string attribute.
  """

  filter = messages.StringField(1)
  orderBy = messages.StringField(2)
  pageSize = messages.IntegerField(3, variant=messages.Variant.INT32)
  pageToken = messages.StringField(4)
  projectId = messages.StringField(5, required=True)


class LoggingProjectsLogServicesIndexesListRequest(messages.Message):
  """A LoggingProjectsLogServicesIndexesListRequest object.

  Fields:
    depth: A integer attribute.
    indexPrefix: A string attribute.
    log: A string attribute.
    pageSize: A integer attribute.
    pageToken: A string attribute.
    service: A string attribute.
  """

  depth = messages.IntegerField(1, variant=messages.Variant.INT32)
  indexPrefix = messages.StringField(2)
  log = messages.StringField(3)
  pageSize = messages.IntegerField(4, variant=messages.Variant.INT32)
  pageToken = messages.StringField(5)
  service = messages.StringField(6, required=True)


class LoggingProjectsLogServicesListRequest(messages.Message):
  """A LoggingProjectsLogServicesListRequest object.

  Fields:
    log: A string attribute.
    pageSize: A integer attribute.
    pageToken: A string attribute.
    projectId: A string attribute.
  """

  log = messages.StringField(1)
  pageSize = messages.IntegerField(2, variant=messages.Variant.INT32)
  pageToken = messages.StringField(3)
  projectId = messages.StringField(4, required=True)


class LoggingProjectsLogServicesSinksDeleteRequest(messages.Message):
  """A LoggingProjectsLogServicesSinksDeleteRequest object.

  Fields:
    sink: A string attribute.
  """

  sink = messages.StringField(1, required=True)


class LoggingProjectsLogServicesSinksGetRequest(messages.Message):
  """A LoggingProjectsLogServicesSinksGetRequest object.

  Fields:
    sink: A string attribute.
  """

  sink = messages.StringField(1, required=True)


class LoggingProjectsLogServicesSinksListRequest(messages.Message):
  """A LoggingProjectsLogServicesSinksListRequest object.

  Fields:
    service: A string attribute.
  """

  service = messages.StringField(1, required=True)


class LoggingProjectsLogServicesSinksPatchRequest(messages.Message):
  """A LoggingProjectsLogServicesSinksPatchRequest object.

  Fields:
    logSink: A LogSink resource to be passed as the request body.
    sink: A string attribute.
    sinkName: A string attribute.
  """

  logSink = messages.MessageField('LogSink', 1)
  sink = messages.StringField(2, required=True)
  sinkName = messages.StringField(3, required=True)


class LoggingProjectsLogServicesSinksUpdateRequest(messages.Message):
  """A LoggingProjectsLogServicesSinksUpdateRequest object.

  Fields:
    logSink: A LogSink resource to be passed as the request body.
    sinkName: A string attribute.
  """

  logSink = messages.MessageField('LogSink', 1)
  sinkName = messages.StringField(2, required=True)


class LoggingProjectsLogsDeleteRequest(messages.Message):
  """A LoggingProjectsLogsDeleteRequest object.

  Fields:
    log: A string attribute.
  """

  log = messages.StringField(1, required=True)


class LoggingProjectsLogsEntriesWriteRequest(messages.Message):
  """A LoggingProjectsLogsEntriesWriteRequest object.

  Fields:
    log: A string attribute.
    writeLogEntriesRequest: A WriteLogEntriesRequest resource to be passed as
      the request body.
  """

  log = messages.StringField(1, required=True)
  writeLogEntriesRequest = messages.MessageField('WriteLogEntriesRequest', 2)


class LoggingProjectsLogsListRequest(messages.Message):
  """A LoggingProjectsLogsListRequest object.

  Fields:
    pageSize: A integer attribute.
    pageToken: A string attribute.
    projectId: A string attribute.
    serviceIndexPrefix: A string attribute.
    serviceName: A string attribute.
  """

  pageSize = messages.IntegerField(1, variant=messages.Variant.INT32)
  pageToken = messages.StringField(2)
  projectId = messages.StringField(3, required=True)
  serviceIndexPrefix = messages.StringField(4)
  serviceName = messages.StringField(5)


class LoggingProjectsLogsSinksDeleteRequest(messages.Message):
  """A LoggingProjectsLogsSinksDeleteRequest object.

  Fields:
    sink: A string attribute.
  """

  sink = messages.StringField(1, required=True)


class LoggingProjectsLogsSinksGetRequest(messages.Message):
  """A LoggingProjectsLogsSinksGetRequest object.

  Fields:
    sink: A string attribute.
  """

  sink = messages.StringField(1, required=True)


class LoggingProjectsLogsSinksListRequest(messages.Message):
  """A LoggingProjectsLogsSinksListRequest object.

  Fields:
    log: A string attribute.
  """

  log = messages.StringField(1, required=True)


class LoggingProjectsLogsSinksPatchRequest(messages.Message):
  """A LoggingProjectsLogsSinksPatchRequest object.

  Fields:
    logSink: A LogSink resource to be passed as the request body.
    sink: A string attribute.
    sinkName: A string attribute.
  """

  logSink = messages.MessageField('LogSink', 1)
  sink = messages.StringField(2, required=True)
  sinkName = messages.StringField(3, required=True)


class LoggingProjectsLogsSinksUpdateRequest(messages.Message):
  """A LoggingProjectsLogsSinksUpdateRequest object.

  Fields:
    logSink: A LogSink resource to be passed as the request body.
    sinkName: A string attribute.
  """

  logSink = messages.MessageField('LogSink', 1)
  sinkName = messages.StringField(2, required=True)


class LoggingProjectsMetricsDeleteRequest(messages.Message):
  """A LoggingProjectsMetricsDeleteRequest object.

  Fields:
    metric: A string attribute.
  """

  metric = messages.StringField(1, required=True)


class LoggingProjectsMetricsGetRequest(messages.Message):
  """A LoggingProjectsMetricsGetRequest object.

  Fields:
    metric: A string attribute.
  """

  metric = messages.StringField(1, required=True)


class LoggingProjectsMetricsListRequest(messages.Message):
  """A LoggingProjectsMetricsListRequest object.

  Fields:
    pageSize: A integer attribute.
    pageToken: A string attribute.
    projectId: A string attribute.
  """

  pageSize = messages.IntegerField(1, variant=messages.Variant.INT32)
  pageToken = messages.StringField(2)
  projectId = messages.StringField(3, required=True)


class LoggingProjectsMetricsPatchRequest(messages.Message):
  """A LoggingProjectsMetricsPatchRequest object.

  Fields:
    logMetric: A LogMetric resource to be passed as the request body.
    metric: A string attribute.
    metricName: A string attribute.
  """

  logMetric = messages.MessageField('LogMetric', 1)
  metric = messages.StringField(2, required=True)
  metricName = messages.StringField(3, required=True)


class LoggingProjectsMetricsUpdateRequest(messages.Message):
  """A LoggingProjectsMetricsUpdateRequest object.

  Fields:
    logMetric: A LogMetric resource to be passed as the request body.
    metricName: A string attribute.
  """

  logMetric = messages.MessageField('LogMetric', 1)
  metricName = messages.StringField(2, required=True)


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


class Status(messages.Message):
  """A Status object.

  Messages:
    DetailsValueListEntry: A DetailsValueListEntry object.

  Fields:
    code: A integer attribute.
    details: A DetailsValueListEntry attribute.
    message: A string attribute.
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class DetailsValueListEntry(messages.Message):
    """A DetailsValueListEntry object.

    Messages:
      AdditionalProperty: An additional property for a DetailsValueListEntry
        object.

    Fields:
      additionalProperties: Additional properties of type
        DetailsValueListEntry
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a DetailsValueListEntry object.

      Fields:
        key: Name of the additional property.
        value: A extra_types.JsonValue attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('extra_types.JsonValue', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  code = messages.IntegerField(1, variant=messages.Variant.INT32)
  details = messages.MessageField('DetailsValueListEntry', 2, repeated=True)
  message = messages.StringField(3)


class WriteLogEntriesRequest(messages.Message):
  """A WriteLogEntriesRequest object.

  Messages:
    CommonLabelsValue: A CommonLabelsValue object.

  Fields:
    commonLabels: A CommonLabelsValue attribute.
    entries: A LogEntry attribute.
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class CommonLabelsValue(messages.Message):
    """A CommonLabelsValue object.

    Messages:
      AdditionalProperty: An additional property for a CommonLabelsValue
        object.

    Fields:
      additionalProperties: Additional properties of type CommonLabelsValue
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a CommonLabelsValue object.

      Fields:
        key: Name of the additional property.
        value: A string attribute.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  commonLabels = messages.MessageField('CommonLabelsValue', 1)
  entries = messages.MessageField('LogEntry', 2, repeated=True)


class WriteLogEntriesResponse(messages.Message):
  """A WriteLogEntriesResponse object."""


