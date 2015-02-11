"""Generated message classes for sqladmin version v1beta3.

API for Cloud SQL database instance management.
"""

from protorpc import message_types
from protorpc import messages


package = 'sqladmin'


class BackupConfiguration(messages.Message):
  """Database instance backup configuration.

  Fields:
    binaryLogEnabled: Whether binary log is enabled. If backup configuration
      is disabled, binary log must be disabled as well.
    enabled: Whether this configuration is enabled.
    id: Identifier for this configuration. This gets generated automatically
      when a backup configuration is created.
    kind: This is always sql#backupConfiguration.
    startTime: Start time for the daily backup configuration in UTC timezone
      in the 24 hour format - HH:MM.
  """

  binaryLogEnabled = messages.BooleanField(1)
  enabled = messages.BooleanField(2)
  id = messages.StringField(3)
  kind = messages.StringField(4, default=u'sql#backupConfiguration')
  startTime = messages.StringField(5)


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


class BinLogCoordinates(messages.Message):
  """Binary log coordinates.

  Fields:
    binLogFileName: Name of the binary log file for a Cloud SQL instance.
    binLogPosition: Position (offset) within the binary log file.
    kind: This is always sql#binLogCoordinates.
  """

  binLogFileName = messages.StringField(1)
  binLogPosition = messages.IntegerField(2)
  kind = messages.StringField(3, default=u'sql#binLogCoordinates')


class CloneContext(messages.Message):
  """Database instance clone context.

  Fields:
    binLogCoordinates: Binary log coordinates, if specified, indentify the
      position up to which the source instance should be cloned. If not
      specified, the source instance is cloned up to the most recent binary
      log coordinates.
    destinationInstanceName: Name of the Cloud SQL instance to be created as a
      clone.
    kind: This is always sql#cloneContext.
    sourceInstanceName: Name of the Cloud SQL instance to be cloned.
  """

  binLogCoordinates = messages.MessageField('BinLogCoordinates', 1)
  destinationInstanceName = messages.StringField(2)
  kind = messages.StringField(3, default=u'sql#cloneContext')
  sourceInstanceName = messages.StringField(4)


class DatabaseFlags(messages.Message):
  """MySQL flags for Cloud SQL instances.

  Fields:
    name: The name of the flag. These flags are passed at instance startup, so
      include both MySQL server options and MySQL system variables. Flags
      should be specified with underscores, not hyphens. Refer to the official
      MySQL documentation on server options and system variables for
      descriptions of what these flags do. Acceptable values are:
      character_set_server utf8 or utf8mb4 event_scheduler on or off (Note:
      The event scheduler will only work reliably if the instance
      activationPolicy is set to ALWAYS) general_log on or off
      group_concat_max_len 4..17179869184 innodb_flush_log_at_trx_commit 0..2
      innodb_lock_wait_timeout 1..1073741824 log_bin_trust_function_creators
      on or off log_output Can be either TABLE or NONE, FILE is not supported
      log_queries_not_using_indexes on or off long_query_time 0..30000000
      lower_case_table_names 0..2 max_allowed_packet 16384..1073741824
      read_only on or off skip_show_database on or off slow_query_log on or
      off. If set to on, you must also set the log_output flag to TABLE to
      receive logs. wait_timeout 1..31536000
    value: The value of the flag. Booleans should be set using 1 for true, and
      0 for false. This field must be omitted if the flag doesn't take a
      value.
  """

  name = messages.StringField(1)
  value = messages.StringField(2)


class DatabaseInstance(messages.Message):
  """A Cloud SQL instance resource.

  Fields:
    currentDiskSize: The current disk usage of the instance in bytes.
    databaseVersion: The database engine type and version. Can be MYSQL_5_5 or
      MYSQL_5_6. Defaults to MYSQL_5_5. The databaseVersion cannot be changed
      after instance creation.
    etag: HTTP 1.1 Entity tag for the resource.
    instance: Name of the Cloud SQL instance. This does not include the
      project ID.
    instanceType: The instance type. This can be one of the following.
      CLOUD_SQL_INSTANCE: Regular Cloud SQL instance. READ_REPLICA_INSTANCE:
      Cloud SQL instance acting as a read-replica.
    ipAddresses: The assigned IP addresses for the instance.
    ipv6Address: The IPv6 address assigned to the instance.
    kind: This is always sql#instance.
    masterInstanceName: The name of the instance which will act as master in
      the replication setup.
    maxDiskSize: The maximum disk size of the instance in bytes.
    project: The project ID of the project containing the Cloud SQL instance.
      The Google apps domain is prefixed if applicable.
    region: The geographical region. Can be us-central, asia-east1 or europe-
      west1. Defaults to us-central. The region can not be changed after
      instance creation.
    replicaNames: The replicas of the instance.
    serverCaCert: SSL configuration.
    serviceAccountEmailAddress: The service account email address assigned to
      the instance.
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
  instanceType = messages.StringField(5)
  ipAddresses = messages.MessageField('IpMapping', 6, repeated=True)
  ipv6Address = messages.StringField(7)
  kind = messages.StringField(8, default=u'sql#instance')
  masterInstanceName = messages.StringField(9)
  maxDiskSize = messages.IntegerField(10)
  project = messages.StringField(11)
  region = messages.StringField(12)
  replicaNames = messages.StringField(13, repeated=True)
  serverCaCert = messages.MessageField('SslCert', 14)
  serviceAccountEmailAddress = messages.StringField(15)
  settings = messages.MessageField('Settings', 16)
  state = messages.StringField(17)


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


class Flag(messages.Message):
  """A Google Cloud SQL service flag resource.

  Fields:
    allowedStringValues: For STRING flags, a list of strings that the value
      can be set to.
    appliesTo: The database version this flag applies to. Currently this can
      only be [MYSQL_5_5].
    kind: This is always sql#flag.
    maxValue: For INTEGER flags, the maximum allowed value.
    minValue: For INTEGER flags, the minimum allowed value.
    name: This is the name of the flag. Flag names always use underscores, not
      hyphens, e.g. max_allowed_packet
    type: The type of the flag. Flags are typed to being BOOLEAN, STRING,
      INTEGER or NONE. NONE is used for flags which do not take a value, such
      as skip_grant_tables.
  """

  allowedStringValues = messages.StringField(1, repeated=True)
  appliesTo = messages.StringField(2, repeated=True)
  kind = messages.StringField(3, default=u'sql#flag')
  maxValue = messages.IntegerField(4)
  minValue = messages.IntegerField(5)
  name = messages.StringField(6)
  type = messages.StringField(7)


class FlagsListResponse(messages.Message):
  """Flags list response.

  Fields:
    items: List of flags.
    kind: This is always sql#flagsList.
  """

  items = messages.MessageField('Flag', 1, repeated=True)
  kind = messages.StringField(2, default=u'sql#flagsList')


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


class InstanceSetRootPasswordRequest(messages.Message):
  """Database instance set root password request.

  Fields:
    setRootPasswordContext: Set Root Password Context.
  """

  setRootPasswordContext = messages.MessageField('SetRootPasswordContext', 1)


class InstancesCloneRequest(messages.Message):
  """Database instance clone request.

  Fields:
    cloneContext: Contains details about the clone operation.
  """

  cloneContext = messages.MessageField('CloneContext', 1)


class InstancesCloneResponse(messages.Message):
  """Database instance clone response.

  Fields:
    kind: This is always sql#instancesClone.
    operation: An unique identifier for the operation associated with the
      cloned instance. You can use this identifier to retrieve the Operations
      resource, which has information about the operation.
  """

  kind = messages.StringField(1, default=u'sql#instancesClone')
  operation = messages.StringField(2)


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


class InstancesPromoteReplicaResponse(messages.Message):
  """Database promote read replica response.

  Fields:
    kind: This is always sql#instancesPromoteReplica.
    operation: An identifier that uniquely identifies the operation. You can
      use this identifier to retrieve the Operations resource that has
      information about the operation.
  """

  kind = messages.StringField(1, default=u'sql#instancesPromoteReplica')
  operation = messages.StringField(2)


class InstancesResetSslConfigResponse(messages.Message):
  """Database instance resetSslConfig response.

  Fields:
    kind: This is always sql#instancesResetSslConfig.
    operation: An identifier that uniquely identifies the operation. You can
      use this identifier to retrieve the Operations resource that has
      information about the operation. All ssl client certificates will be
      deleted and a new server certificate will be created. Does not take
      effect until the next instance restart.
  """

  kind = messages.StringField(1, default=u'sql#instancesResetSslConfig')
  operation = messages.StringField(2)


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


class InstancesSetRootPasswordResponse(messages.Message):
  """Database instance set root password response.

  Fields:
    kind: This is always sql#instancesSetRootPassword.
    operation: An identifier that uniquely identifies the operation. You can
      use this identifier to retrieve the Operations resource that has
      information about the operation.
  """

  kind = messages.StringField(1, default=u'sql#instancesSetRootPassword')
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


class IpConfiguration(messages.Message):
  """IP Management configuration.

  Fields:
    authorizedNetworks: The list of external networks that are allowed to
      connect to the instance using the IP. In CIDR notation, also known as
      'slash' notation (e.g. 192.168.100.0/24).
    enabled: Whether the instance should be assigned an IP address or not.
    kind: This is always sql#ipConfiguration.
    requireSsl: Whether the mysqld should default to 'REQUIRE X509' for users
      connecting over IP.
  """

  authorizedNetworks = messages.StringField(1, repeated=True)
  enabled = messages.BooleanField(2)
  kind = messages.StringField(3, default=u'sql#ipConfiguration')
  requireSsl = messages.BooleanField(4)


class IpMapping(messages.Message):
  """Database instance IP Mapping.

  Fields:
    ipAddress: The IP address assigned.
    timeToRetire: The due time for this IP to be retired in RFC 3339 format,
      for example 2012-11-15T16:19:00.094Z. This field is only available when
      the IP is scheduled to be retired.
  """

  ipAddress = messages.StringField(1)
  timeToRetire = message_types.DateTimeField(2)


class LocationPreference(messages.Message):
  """Preferred location. This specifies where a Cloud SQL instance should
  preferably be located, either in a specific Compute Engine zone, or co-
  located with an App Engine application. Note that if the preferred location
  is not available, the instance will be located as close as possible within
  the region. Only one location may be specified.

  Fields:
    followGaeApplication: The App Engine application to follow, it must be in
      the same region as the Cloud SQL instance.
    kind: This is always sql#locationPreference.
    zone: The preferred Compute Engine zone (e.g. us-centra1-a, us-central1-b,
      etc.).
  """

  followGaeApplication = messages.StringField(1)
  kind = messages.StringField(2, default=u'sql#locationPreference')
  zone = messages.StringField(3)


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


class SetRootPasswordContext(messages.Message):
  """Database instance set root password context.

  Fields:
    kind: This is always sql#setRootUserContext.
    password: The password for the root user.
  """

  kind = messages.StringField(1, default=u'sql#setRootUserContext')
  password = messages.StringField(2)


class Settings(messages.Message):
  """Database instance settings.

  Fields:
    activationPolicy: The activation policy for this instance. This specifies
      when the instance should be activated and is applicable only when the
      instance state is RUNNABLE. This can be one of the following. ALWAYS:
      The instance should always be active. NEVER: The instance should never
      be activated. ON_DEMAND: The instance is activated upon receiving
      requests.
    authorizedGaeApplications: The App Engine app IDs that can access this
      instance.
    backupConfiguration: The daily backup configuration for the instance.
    databaseFlags: The database flags passed to the instance at startup.
    databaseReplicationEnabled: Configuration specific to read replica
      instance. Indicates whether replication is enabled or not.
    ipConfiguration: The settings for IP Management. This allows to enable or
      disable the instance IP and manage which external networks can connect
      to the instance.
    kind: This is always sql#settings.
    locationPreference: The location preference settings. This allows the
      instance to be located as near as possible to either an App Engine app
      or GCE zone for better performance.
    pricingPlan: The pricing plan for this instance. This can be either
      PER_USE or PACKAGE.
    replicationType: The type of replication this instance uses. This can be
      either ASYNCHRONOUS or SYNCHRONOUS.
    settingsVersion: The version of instance settings. This is a required
      field for update method to make sure concurrent updates are handled
      properly. During update, use the most recent settingsVersion value for
      this instance and do not try to update this value.
    tier: The tier of service for this instance, for example D1, D2. For more
      information, see pricing.
  """

  activationPolicy = messages.StringField(1)
  authorizedGaeApplications = messages.StringField(2, repeated=True)
  backupConfiguration = messages.MessageField('BackupConfiguration', 3, repeated=True)
  databaseFlags = messages.MessageField('DatabaseFlags', 4, repeated=True)
  databaseReplicationEnabled = messages.BooleanField(5)
  ipConfiguration = messages.MessageField('IpConfiguration', 6)
  kind = messages.StringField(7, default=u'sql#settings')
  locationPreference = messages.MessageField('LocationPreference', 8)
  pricingPlan = messages.StringField(9)
  replicationType = messages.StringField(10)
  settingsVersion = messages.IntegerField(11)
  tier = messages.StringField(12)


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


class SqlFlagsListRequest(messages.Message):
  """A SqlFlagsListRequest object."""


class SqlInstancesCloneRequest(messages.Message):
  """A SqlInstancesCloneRequest object.

  Fields:
    instancesCloneRequest: A InstancesCloneRequest resource to be passed as
      the request body.
    project: Project ID of the source as well as the clone Cloud SQL instance.
  """

  instancesCloneRequest = messages.MessageField('InstancesCloneRequest', 1)
  project = messages.StringField(2, required=True)


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
    instance: Database instance ID. This does not include the project ID.
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


class SqlInstancesPromoteReplicaRequest(messages.Message):
  """A SqlInstancesPromoteReplicaRequest object.

  Fields:
    instance: Cloud SQL read replica instance name.
    project: ID of the project that contains the read replica.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class SqlInstancesResetSslConfigRequest(messages.Message):
  """A SqlInstancesResetSslConfigRequest object.

  Fields:
    instance: Cloud SQL instance ID. This does not include the project ID.
    project: Project ID of the project that contains the instance.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


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


class SqlInstancesSetRootPasswordRequest(messages.Message):
  """A SqlInstancesSetRootPasswordRequest object.

  Fields:
    instance: Cloud SQL instance ID. This does not include the project ID.
    instanceSetRootPasswordRequest: A InstanceSetRootPasswordRequest resource
      to be passed as the request body.
    project: Project ID of the project that contains the instance.
  """

  instance = messages.StringField(1, required=True)
  instanceSetRootPasswordRequest = messages.MessageField('InstanceSetRootPasswordRequest', 2)
  project = messages.StringField(3, required=True)


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


class SqlSslCertsDeleteRequest(messages.Message):
  """A SqlSslCertsDeleteRequest object.

  Fields:
    instance: Cloud SQL instance ID. This does not include the project ID.
    project: Project ID of the project that contains the instance to be
      deleted.
    sha1Fingerprint: Sha1 FingerPrint.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  sha1Fingerprint = messages.StringField(3, required=True)


class SqlSslCertsGetRequest(messages.Message):
  """A SqlSslCertsGetRequest object.

  Fields:
    instance: Cloud SQL instance ID. This does not include the project ID.
    project: Project ID of the project that contains the instance.
    sha1Fingerprint: Sha1 FingerPrint.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  sha1Fingerprint = messages.StringField(3, required=True)


class SqlSslCertsInsertRequest(messages.Message):
  """A SqlSslCertsInsertRequest object.

  Fields:
    instance: Cloud SQL instance ID. This does not include the project ID.
    project: Project ID of the project to which the newly created Cloud SQL
      instances should belong.
    sslCertsInsertRequest: A SslCertsInsertRequest resource to be passed as
      the request body.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  sslCertsInsertRequest = messages.MessageField('SslCertsInsertRequest', 3)


class SqlSslCertsListRequest(messages.Message):
  """A SqlSslCertsListRequest object.

  Fields:
    instance: Cloud SQL instance ID. This does not include the project ID.
    project: Project ID of the project for which to list Cloud SQL instances.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class SqlTiersListRequest(messages.Message):
  """A SqlTiersListRequest object.

  Fields:
    project: Project ID of the project for which to list tiers.
  """

  project = messages.StringField(1, required=True)


class SslCert(messages.Message):
  """SslCerts Resource

  Fields:
    cert: PEM representation.
    certSerialNumber: Serial number, as extracted from the certificate.
    commonName: User supplied name. Constrained to [a-zA-Z.-_ ]+.
    createTime: Time when the certificate was created.
    expirationTime: Time when the certificate expires.
    instance: Name of the database instance.
    kind: This is always sql#sslCert.
    sha1Fingerprint: Sha1 Fingerprint.
  """

  cert = messages.StringField(1)
  certSerialNumber = messages.StringField(2)
  commonName = messages.StringField(3)
  createTime = message_types.DateTimeField(4)
  expirationTime = message_types.DateTimeField(5)
  instance = messages.StringField(6)
  kind = messages.StringField(7, default=u'sql#sslCert')
  sha1Fingerprint = messages.StringField(8)


class SslCertDetail(messages.Message):
  """SslCertDetail.

  Fields:
    certInfo: The public information about the cert.
    certPrivateKey: The private key for the client cert, in pem format. Keep
      private in order to protect your security.
  """

  certInfo = messages.MessageField('SslCert', 1)
  certPrivateKey = messages.StringField(2)


class SslCertsDeleteResponse(messages.Message):
  """SslCert delete response.

  Fields:
    kind: This is always sql#sslCertsDelete.
    operation: An identifier that uniquely identifies the operation. You can
      use this identifier to retrieve the Operations resource that has
      information about the operation.
  """

  kind = messages.StringField(1, default=u'sql#sslCertsDelete')
  operation = messages.StringField(2)


class SslCertsInsertRequest(messages.Message):
  """SslCerts insert request.

  Fields:
    commonName: User supplied name. Must be a distinct name from the other
      certificates for this instance. New certificates will not be usable
      until the instance is restarted.
  """

  commonName = messages.StringField(1)


class SslCertsInsertResponse(messages.Message):
  """SslCert insert response.

  Fields:
    clientCert: The new client certificate and private key. The new
      certificate will not work until the instance is restarted.
    kind: This is always sql#sslCertsInsert.
    serverCaCert: The server Certificate Authority's certificate. If this is
      missing you can force a new one to be generated by calling
      resetSslConfig method on instances resource..
  """

  clientCert = messages.MessageField('SslCertDetail', 1)
  kind = messages.StringField(2, default=u'sql#sslCertsInsert')
  serverCaCert = messages.MessageField('SslCert', 3)


class SslCertsListResponse(messages.Message):
  """SslCerts list response.

  Fields:
    items: List of client certificates for the instance.
    kind: This is always sql#sslCertsList.
  """

  items = messages.MessageField('SslCert', 1, repeated=True)
  kind = messages.StringField(2, default=u'sql#sslCertsList')


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
    region: The applicable regions for this tier. Can be us-east1, europe-
      west1, or asia-east1.
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


