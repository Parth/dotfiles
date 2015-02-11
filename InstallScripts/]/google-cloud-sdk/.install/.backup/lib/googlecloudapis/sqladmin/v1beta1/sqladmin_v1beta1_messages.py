"""Generated message classes for sqladmin version v1beta1.

API for Cloud SQL database instance management.
"""

from protorpc import message_types
from protorpc import messages


package = 'sqladmin'


class BackupConfiguration(messages.Message):
  """Database instance backup configuration.

  Fields:
    enabled: Whether this configuration is enabled.
    id: Identifier for this configuration. This gets generated automatically
      when a backup configuration is created.
    kind: This is always sql#backupConfiguration.
    startTime: Start time for the daily backup configuration in UTC timezone
      in the 24 hour format - HH:MM.
  """

  enabled = messages.BooleanField(1)
  id = messages.StringField(2)
  kind = messages.StringField(3, default=u'sql#backupConfiguration')
  startTime = messages.StringField(4)


class BackupRun(messages.Message):
  """A database instance backup run resource.

  Fields:
    backupConfiguration: Backup Configuration identifier.
    dueTime: The due time of this run in UTC timezone in RFC 3339 format, for
      example 2012-11-15T16:19:00.094Z.
    endTime: The time the backup operation completed in UTC timezone in RFC
      3339 format, for example 2012-11-15T16:19:00.094Z.
    enqueuedTime: The time the run was enqueued in UTC timezone in RFC 3339
      format, for example 2012-11-15T16:19:00.094Z.
    error: Information about why the backup operation failed. This is only
      present if the run has the FAILED status.
    instance: Name of the database instance.
    kind: This is always sql#backupRun.
    startTime: The time the backup operation actually started in UTC timezone
      in RFC 3339 format, for example 2012-11-15T16:19:00.094Z.
    status: The status of this run.
  """

  backupConfiguration = messages.StringField(1)
  dueTime = message_types.DateTimeField(2)
  endTime = message_types.DateTimeField(3)
  enqueuedTime = message_types.DateTimeField(4)
  error = messages.MessageField('OperationError', 5)
  instance = messages.StringField(6)
  kind = messages.StringField(7, default=u'sql#backupRun')
  startTime = message_types.DateTimeField(8)
  status = messages.StringField(9)


class BackupRunsListResponse(messages.Message):
  """Backup run list results.

  Fields:
    items: A list of backup runs in reverse chronological order of the
      enqueued time.
    kind: This is always sql#backupRunsList.
    nextPageToken: The continuation token, used to page through large result
      sets. Provide this value in a subsequent request to return the next page
      of results.
  """

  items = messages.MessageField('BackupRun', 1, repeated=True)
  kind = messages.StringField(2, default=u'sql#backupRunsList')
  nextPageToken = messages.StringField(3)


class DatabaseInstance(messages.Message):
  """A Cloud SQL instance resource.

  Fields:
    currentDiskSize: The current disk usage of the instance in bytes.
    databaseVersion: The database engine type and version, for example
      MYSQL_5_5 for MySQL 5.5.
    etag: Etag for this resource - a version number for the settings object in
      this resource. This field has no effect when passed as a request
      parameter. Instead, the contents of this field should be passed in an
      'If-Match' http header for use in optimistic locking.
    instance: Name of the Cloud SQL instance. This does not include the
      project ID.
    kind: This is always sql#instance.
    maxDiskSize: The maximum disk size of the instance in bytes.
    project: The project ID of the project containing the Cloud SQL instance.
      The Google apps domain is prefixed if applicable.
    region: The geographical region. Can be us-central or europe-west1.
      Defaults to us-central. The region can not be changed after instance
      creation.
    settings: The user settings.
    state: The current serving state of the Cloud SQL instance. This can be
      one of the following. RUNNABLE: The instance is running, or is ready to
      run when accessed. SUSPENDED: The instance is not available, for example
      due to problems with billing. PENDING_CREATE: The instance is being
      created. MAINTENANCE: The instance is down for maintenance.
      UNKNOWN_STATE: The state of the instance is unknown.
  """

  currentDiskSize = messages.IntegerField(1)
  databaseVersion = messages.StringField(2)
  etag = messages.StringField(3)
  instance = messages.StringField(4)
  kind = messages.StringField(5, default=u'sql#instance')
  maxDiskSize = messages.IntegerField(6)
  project = messages.StringField(7)
  region = messages.StringField(8)
  settings = messages.MessageField('Settings', 9)
  state = messages.StringField(10)


class ExportContext(messages.Message):
  """Database instance export context.

  Fields:
    database: Databases (for example, guestbook) from which the export is
      made. If unspecified, all databases are exported.
    kind: This is always sql#exportContext.
    table: Tables to export, or that were exported, from the specified
      database. If you specify tables, specify one and only one database.
    uri: The path to the file in Google Cloud Storage where the export will be
      stored, or where it was already stored. The URI is in the form
      gs://bucketName/fileName. If the file already exists, the operation
      fails. If the filename ends with .gz, the contents are compressed.
  """

  database = messages.StringField(1, repeated=True)
  kind = messages.StringField(2, default=u'sql#exportContext')
  table = messages.StringField(3, repeated=True)
  uri = messages.StringField(4)


class ImportContext(messages.Message):
  """Database instance import context.

  Fields:
    database: The database (for example, guestbook) to which the import is
      made. If not set, it is assumed that the database is specified in the
      file to be imported.
    kind: This is always sql#importContext.
    uri: A path to the MySQL dump file in Google Cloud Storage from which the
      import is made. The URI is in the form gs://bucketName/fileName.
      Compressed gzip files (.gz) are also supported.
  """

  database = messages.StringField(1)
  kind = messages.StringField(2, default=u'sql#importContext')
  uri = messages.StringField(3, repeated=True)


class InstanceOperation(messages.Message):
  """An Operations resource contains information about database instance
  operations such as create, delete, and restart. Operations resources are
  created in response to operations that were initiated; you never create them
  directly.

  Fields:
    endTime: The time this operation finished in UTC timezone in RFC 3339
      format, for example 2012-11-15T16:19:00.094Z.
    enqueuedTime: The time this operation was enqueued in UTC timezone in RFC
      3339 format, for example 2012-11-15T16:19:00.094Z.
    error: The error(s) encountered by this operation. Only set if the
      operation results in an error.
    exportContext: The context for export operation, if applicable.
    importContext: The context for import operation, if applicable.
    instance: Name of the database instance.
    kind: This is always sql#instanceOperation.
    operation: An identifier that uniquely identifies the operation. You can
      use this identifier to retrieve the Operations resource that has
      information about the operation.
    operationType: The type of the operation. Valid values are CREATE, DELETE,
      UPDATE, RESTART, IMPORT, EXPORT, BACKUP_VOLUME, RESTORE_VOLUME.
    startTime: The time this operation actually started in UTC timezone in RFC
      3339 format, for example 2012-11-15T16:19:00.094Z.
    state: The state of an operation. Valid values are PENDING, RUNNING, DONE,
      UNKNOWN.
    userEmailAddress: The email address of the user who initiated this
      operation.
  """

  endTime = message_types.DateTimeField(1)
  enqueuedTime = message_types.DateTimeField(2)
  error = messages.MessageField('OperationError', 3, repeated=True)
  exportContext = messages.MessageField('ExportContext', 4)
  importContext = messages.MessageField('ImportContext', 5)
  instance = messages.StringField(6)
  kind = messages.StringField(7, default=u'sql#instanceOperation')
  operation = messages.StringField(8)
  operationType = messages.StringField(9)
  startTime = message_types.DateTimeField(10)
  state = messages.StringField(11)
  userEmailAddress = messages.StringField(12)


class InstancesDeleteResponse(messages.Message):
  """Database instance delete response.

  Fields:
    kind: This is always sql#instancesDelete.
    operation: An identifier that uniquely identifies the operation. You can
      use this identifier to retrieve the Operations resource that has
      information about the operation.
  """

  kind = messages.StringField(1, default=u'sql#instancesDelete')
  operation = messages.StringField(2)


class InstancesExportRequest(messages.Message):
  """Database instance export request.

  Fields:
    exportContext: Contains details about the export operation.
  """

  exportContext = messages.MessageField('ExportContext', 1)


class InstancesExportResponse(messages.Message):
  """Database instance export response.

  Fields:
    kind: This is always sql#instancesExport.
    operation: An identifier that uniquely identifies the operation. You can
      use this identifier to retrieve the Operations resource that has
      information about the operation.
  """

  kind = messages.StringField(1, default=u'sql#instancesExport')
  operation = messages.StringField(2)


class InstancesImportRequest(messages.Message):
  """Database instance import request.

  Fields:
    importContext: Contains details about the import operation.
  """

  importContext = messages.MessageField('ImportContext', 1)


class InstancesImportResponse(messages.Message):
  """Database instance import response.

  Fields:
    kind: This is always sql#instancesImport.
    operation: An identifier that uniquely identifies the operation. You can
      use this identifier to retrieve the Operations resource that has
      information about the operation.
  """

  kind = messages.StringField(1, default=u'sql#instancesImport')
  operation = messages.StringField(2)


class InstancesInsertResponse(messages.Message):
  """Database instance insert response.

  Fields:
    kind: This is always sql#instancesInsert.
    operation: An identifier that uniquely identifies the operation. You can
      use this identifier to retrieve the Operations resource that has
      information about the operation.
  """

  kind = messages.StringField(1, default=u'sql#instancesInsert')
  operation = messages.StringField(2)


class InstancesListResponse(messages.Message):
  """Database instances list response.

  Fields:
    items: List of database instance resources.
    kind: This is always sql#instancesList.
    nextPageToken: The continuation token, used to page through large result
      sets. Provide this value in a subsequent request to return the next page
      of results.
  """

  items = messages.MessageField('DatabaseInstance', 1, repeated=True)
  kind = messages.StringField(2, default=u'sql#instancesList')
  nextPageToken = messages.StringField(3)


class InstancesRestartResponse(messages.Message):
  """Database instance restart response.

  Fields:
    kind: This is always sql#instancesRestart.
    operation: An identifier that uniquely identifies the operation. You can
      use this identifier to retrieve the Operations resource that has
      information about the operation.
  """

  kind = messages.StringField(1, default=u'sql#instancesRestart')
  operation = messages.StringField(2)


class InstancesRestoreBackupResponse(messages.Message):
  """Database instance restore backup response.

  Fields:
    kind: This is always sql#instancesRestoreBackup.
    operation: An identifier that uniquely identifies the operation. You can
      use this identifier to retrieve the Operations resource that has
      information about the operation.
  """

  kind = messages.StringField(1, default=u'sql#instancesRestoreBackup')
  operation = messages.StringField(2)


class InstancesUpdateResponse(messages.Message):
  """Database instance update response.

  Fields:
    kind: This is always sql#instancesUpdate.
    operation: An identifier that uniquely identifies the operation. You can
      use this identifier to retrieve information about the operation.
  """

  kind = messages.StringField(1, default=u'sql#instancesUpdate')
  operation = messages.StringField(2)


class OperationError(messages.Message):
  """Database instance operation error.

  Fields:
    code: Identifies the specific error that occurred.
    kind: This is always sql#operationError.
  """

  code = messages.StringField(1)
  kind = messages.StringField(2, default=u'sql#operationError')


class OperationsListResponse(messages.Message):
  """Database instance list operations response.

  Fields:
    items: List of operation resources.
    kind: This is always sql#operationsList.
    nextPageToken: The continuation token, used to page through large result
      sets. Provide this value in a subsequent request to return the next page
      of results.
  """

  items = messages.MessageField('InstanceOperation', 1, repeated=True)
  kind = messages.StringField(2, default=u'sql#operationsList')
  nextPageToken = messages.StringField(3)


class Settings(messages.Message):
  """Database instance settings.

  Fields:
    activationPolicy: The activation policy for this instance. This specifies
      when the instance should be activated and is applicable only when the
      instance state is RUNNABLE. This can be one of the following. ALWAYS:
      The instance should always be active. NEVER: The instance should never
      be activated. ON_DEMAND: The instance is activated upon receiving
      requests.
    authorizedGaeApplications: The AppEngine app ids that can access this
      instance.
    backupConfiguration: The daily backup configuration for the instance.
    kind: This is always sql#settings.
    pricingPlan: The pricing plan for this instance. This can be either
      PER_USE or PACKAGE.
    replicationType: The type of replication this instance uses. This can be
      either ASYNCHRONOUS or SYNCHRONOUS.
    tier: The tier of service for this instance, for example D1, D2. For more
      information, see pricing.
  """

  activationPolicy = messages.StringField(1)
  authorizedGaeApplications = messages.StringField(2, repeated=True)
  backupConfiguration = messages.MessageField('BackupConfiguration', 3, repeated=True)
  kind = messages.StringField(4, default=u'sql#settings')
  pricingPlan = messages.StringField(5)
  replicationType = messages.StringField(6)
  tier = messages.StringField(7)


class SqlBackupRunsGetRequest(messages.Message):
  """A SqlBackupRunsGetRequest object.

  Fields:
    backupConfiguration: Identifier for the backup configuration. This gets
      generated automatically when a backup configuration is created.
    dueTime: The start time of the four-hour backup window. The backup can
      occur any time in the window. The time is in RFC 3339 format, for
      example 2012-11-15T16:19:00.094Z.
    instance: Cloud SQL instance ID. This does not include the project ID.
    project: Project ID of the project that contains the instance.
  """

  backupConfiguration = messages.StringField(1, required=True)
  dueTime = messages.StringField(2, required=True)
  instance = messages.StringField(3, required=True)
  project = messages.StringField(4, required=True)


class SqlBackupRunsListRequest(messages.Message):
  """A SqlBackupRunsListRequest object.

  Fields:
    backupConfiguration: Identifier for the backup configuration. This gets
      generated automatically when a backup configuration is created.
    instance: Cloud SQL instance ID. This does not include the project ID.
    maxResults: Maximum number of backup runs per response.
    pageToken: A previously-returned page token representing part of the
      larger set of results to view.
    project: Project ID of the project that contains the instance.
  """

  backupConfiguration = messages.StringField(1, required=True)
  instance = messages.StringField(2, required=True)
  maxResults = messages.IntegerField(3, variant=messages.Variant.INT32)
  pageToken = messages.StringField(4)
  project = messages.StringField(5, required=True)


class SqlInstancesDeleteRequest(messages.Message):
  """A SqlInstancesDeleteRequest object.

  Fields:
    instance: Cloud SQL instance ID. This does not include the project ID.
    project: Project ID of the project that contains the instance to be
      deleted.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class SqlInstancesExportRequest(messages.Message):
  """A SqlInstancesExportRequest object.

  Fields:
    instance: Cloud SQL instance ID. This does not include the project ID.
    instancesExportRequest: A InstancesExportRequest resource to be passed as
      the request body.
    project: Project ID of the project that contains the instance to be
      exported.
  """

  instance = messages.StringField(1, required=True)
  instancesExportRequest = messages.MessageField('InstancesExportRequest', 2)
  project = messages.StringField(3, required=True)


class SqlInstancesGetRequest(messages.Message):
  """A SqlInstancesGetRequest object.

  Fields:
    instance: Cloud SQL instance ID. This does not include the project ID.
    project: Project ID of the project that contains the instance.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class SqlInstancesImportRequest(messages.Message):
  """A SqlInstancesImportRequest object.

  Fields:
    instance: Cloud SQL instance ID. This does not include the project ID.
    instancesImportRequest: A InstancesImportRequest resource to be passed as
      the request body.
    project: Project ID of the project that contains the instance.
  """

  instance = messages.StringField(1, required=True)
  instancesImportRequest = messages.MessageField('InstancesImportRequest', 2)
  project = messages.StringField(3, required=True)


class SqlInstancesListRequest(messages.Message):
  """A SqlInstancesListRequest object.

  Fields:
    maxResults: The maximum number of results to return per response.
    pageToken: A previously-returned page token representing part of the
      larger set of results to view.
    project: Project ID of the project for which to list Cloud SQL instances.
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.UINT32)
  pageToken = messages.StringField(2)
  project = messages.StringField(3, required=True)


class SqlInstancesRestartRequest(messages.Message):
  """A SqlInstancesRestartRequest object.

  Fields:
    instance: Cloud SQL instance ID. This does not include the project ID.
    project: Project ID of the project that contains the instance to be
      restarted.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class SqlInstancesRestoreBackupRequest(messages.Message):
  """A SqlInstancesRestoreBackupRequest object.

  Fields:
    backupConfiguration: The identifier of the backup configuration. This gets
      generated automatically when a backup configuration is created.
    dueTime: The start time of the four-hour backup window. The backup can
      occur any time in the window. The time is in RFC 3339 format, for
      example 2012-11-15T16:19:00.094Z.
    instance: Cloud SQL instance ID. This does not include the project ID.
    project: Project ID of the project that contains the instance.
  """

  backupConfiguration = messages.StringField(1, required=True)
  dueTime = messages.StringField(2, required=True)
  instance = messages.StringField(3, required=True)
  project = messages.StringField(4, required=True)


class SqlOperationsGetRequest(messages.Message):
  """A SqlOperationsGetRequest object.

  Fields:
    instance: Cloud SQL instance ID. This does not include the project ID.
    operation: Instance operation ID.
    project: Project ID of the project that contains the instance.
  """

  instance = messages.StringField(1, required=True)
  operation = messages.StringField(2, required=True)
  project = messages.StringField(3, required=True)


class SqlOperationsListRequest(messages.Message):
  """A SqlOperationsListRequest object.

  Fields:
    instance: Cloud SQL instance ID. This does not include the project ID.
    maxResults: Maximum number of operations per response.
    pageToken: A previously-returned page token representing part of the
      larger set of results to view.
    project: Project ID of the project that contains the instance.
  """

  instance = messages.StringField(1, required=True)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class SqlTiersListRequest(messages.Message):
  """A SqlTiersListRequest object."""


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


class Tier(messages.Message):
  """A Google Cloud SQL service tier resource.

  Fields:
    DiskQuota: The maximum disk size of this tier in bytes.
    RAM: The maximum RAM usage of this tier in bytes.
    kind: This is always sql#tier.
    region: The applicable regions for this tier. Can be us-east1 and europe-
      west1.
    tier: An identifier for the service tier, for example D1, D2 etc. For
      related information, see Pricing.
  """

  DiskQuota = messages.IntegerField(1)
  RAM = messages.IntegerField(2)
  kind = messages.StringField(3, default=u'sql#tier')
  region = messages.StringField(4, repeated=True)
  tier = messages.StringField(5)


class TiersListResponse(messages.Message):
  """Tiers list response.

  Fields:
    items: List of tiers.
    kind: This is always sql#tiersList.
  """

  items = messages.MessageField('Tier', 1, repeated=True)
  kind = messages.StringField(2, default=u'sql#tiersList')


