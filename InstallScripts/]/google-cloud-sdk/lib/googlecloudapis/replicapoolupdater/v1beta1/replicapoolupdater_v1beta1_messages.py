"""Generated message classes for replicapoolupdater version v1beta1.

The Google Compute Engine Instance Group Updater API provides services for
updating groups of Compute Engine Instances.
"""

from protorpc import messages


package = 'replicapoolupdater'


class InstanceUpdate(messages.Message):
  """Update of a single instance.

  Messages:
    ErrorValue: Errors that occurred during the instance update. Setting
      (api.field).field_number manually is a workaround for b/16512602.

  Fields:
    error: Errors that occurred during the instance update. Setting
      (api.field).field_number manually is a workaround for b/16512602.
    instance: URL of the instance being updated.
    status: Status of the instance update. Possible values are:   - "PENDING":
      The instance update is pending execution.  - "ROLLING_FORWARD": The
      instance update is going forward.  - "ROLLING_BACK": The instance update
      is being rolled back.  - "PAUSED": The instance update is temporarily
      paused (inactive).  - "ROLLED_OUT": The instance update is finished, the
      instance is running the new template.  - "ROLLED_BACK": The instance
      update is finished, the instance has been reverted to the previous
      template.  - "CANCELLED": The instance update is paused and no longer
      can be resumed, undefined in which template the instance is running.
  """

  class ErrorValue(messages.Message):
    """Errors that occurred during the instance update. Setting
    (api.field).field_number manually is a workaround for b/16512602.

    Messages:
      ErrorsValueListEntry: A ErrorsValueListEntry object.

    Fields:
      errors: [Output Only] The array of errors encountered while processing
        this operation.
    """

    class ErrorsValueListEntry(messages.Message):
      """A ErrorsValueListEntry object.

      Fields:
        code: [Output Only] The error type identifier for this error.
        location: [Output Only] Indicates the field in the request which
          caused the error. This property is optional.
        message: [Output Only] An optional, human-readable error message.
      """

      code = messages.StringField(1)
      location = messages.StringField(2)
      message = messages.StringField(3)

    errors = messages.MessageField('ErrorsValueListEntry', 1, repeated=True)

  error = messages.MessageField('ErrorValue', 1)
  instance = messages.StringField(2)
  status = messages.StringField(3)


class InstanceUpdateList(messages.Message):
  """Response returned by ListInstanceUpdates method.

  Fields:
    items: Collection of requested instance updates.
    kind: [Output Only] Type of the resource.
    nextPageToken: A token used to continue a truncated list request.
    selfLink: [Output Only] The fully qualified URL for the resource.
  """

  items = messages.MessageField('InstanceUpdate', 1, repeated=True)
  kind = messages.StringField(2, default=u'replicapoolupdater#instanceUpdateList')
  nextPageToken = messages.StringField(3)
  selfLink = messages.StringField(4)


class Operation(messages.Message):
  """An operation resource, used to manage asynchronous API requests.

  Messages:
    ErrorValue: [Output Only] If errors occurred during processing of this
      operation, this field will be populated.
    WarningsValueListEntry: A WarningsValueListEntry object.

  Fields:
    clientOperationId: A string attribute.
    creationTimestamp: [Output Only] Creation timestamp in RFC3339 text format
      (output only).
    endTime: A string attribute.
    error: [Output Only] If errors occurred during processing of this
      operation, this field will be populated.
    httpErrorMessage: A string attribute.
    httpErrorStatusCode: A integer attribute.
    id: [Output Only] Unique identifier for the resource; defined by the
      server.
    insertTime: [Output Only] The time that this operation was requested. This
      is in RFC 3339 format.
    kind: [Output Only] Type of the resource. Always kind#operation for
      Operation resources.
    name: [Output Only] Name of the resource (output only).
    operationType: A string attribute.
    progress: A integer attribute.
    region: [Output Only] URL of the region where the operation resides
      (output only).
    selfLink: [Output Only] Server defined URL for the resource.
    startTime: [Output Only] The time that this operation was started by the
      server. This is in RFC 3339 format.
    status: [Output Only] Status of the operation. Can be one of the
      following: "PENDING", "RUNNING", or "DONE".
    statusMessage: [Output Only] An optional textual description of the
      current status of the operation.
    targetId: [Output Only] Unique target id which identifies a particular
      incarnation of the target.
    targetLink: [Output Only] URL of the resource the operation is mutating
      (output only).
    user: A string attribute.
    warnings: A WarningsValueListEntry attribute.
    zone: [Output Only] URL of the zone where the operation resides (output
      only).
  """

  class ErrorValue(messages.Message):
    """[Output Only] If errors occurred during processing of this operation,
    this field will be populated.

    Messages:
      ErrorsValueListEntry: A ErrorsValueListEntry object.

    Fields:
      errors: [Output Only] The array of errors encountered while processing
        this operation.
    """

    class ErrorsValueListEntry(messages.Message):
      """A ErrorsValueListEntry object.

      Fields:
        code: [Output Only] The error type identifier for this error.
        location: [Output Only] Indicates the field in the request which
          caused the error. This property is optional.
        message: [Output Only] An optional, human-readable error message.
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
      code: [Output only] The warning type identifier for this warning.
      data: [Output only] Metadata for this warning in key:value format.
      message: [Output only] Optional human-readable details for this warning.
    """

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: [Output Only] Metadata key for this warning.
        value: [Output Only] Metadata value for this warning.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.StringField(1)
    data = messages.MessageField('DataValueListEntry', 2, repeated=True)
    message = messages.StringField(3)

  clientOperationId = messages.StringField(1)
  creationTimestamp = messages.StringField(2)
  endTime = messages.StringField(3)
  error = messages.MessageField('ErrorValue', 4)
  httpErrorMessage = messages.StringField(5)
  httpErrorStatusCode = messages.IntegerField(6, variant=messages.Variant.INT32)
  id = messages.IntegerField(7, variant=messages.Variant.UINT64)
  insertTime = messages.StringField(8)
  kind = messages.StringField(9, default=u'replicapoolupdater#operation')
  name = messages.StringField(10)
  operationType = messages.StringField(11)
  progress = messages.IntegerField(12, variant=messages.Variant.INT32)
  region = messages.StringField(13)
  selfLink = messages.StringField(14)
  startTime = messages.StringField(15)
  status = messages.StringField(16)
  statusMessage = messages.StringField(17)
  targetId = messages.IntegerField(18, variant=messages.Variant.UINT64)
  targetLink = messages.StringField(19)
  user = messages.StringField(20)
  warnings = messages.MessageField('WarningsValueListEntry', 21, repeated=True)
  zone = messages.StringField(22)


class ReplicapoolupdaterRollingUpdatesCancelRequest(messages.Message):
  """A ReplicapoolupdaterRollingUpdatesCancelRequest object.

  Fields:
    project: The Google Developers Console project name.
    rollingUpdate: The name of the update.
    zone: The name of the zone in which the update's target resides.
  """

  project = messages.StringField(1, required=True)
  rollingUpdate = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ReplicapoolupdaterRollingUpdatesGetRequest(messages.Message):
  """A ReplicapoolupdaterRollingUpdatesGetRequest object.

  Fields:
    project: The Google Developers Console project name.
    rollingUpdate: The name of the update.
    zone: The name of the zone in which the update's target resides.
  """

  project = messages.StringField(1, required=True)
  rollingUpdate = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ReplicapoolupdaterRollingUpdatesInsertRequest(messages.Message):
  """A ReplicapoolupdaterRollingUpdatesInsertRequest object.

  Fields:
    project: The Google Developers Console project name.
    rollingUpdate: A RollingUpdate resource to be passed as the request body.
    zone: The name of the zone in which the update's target resides.
  """

  project = messages.StringField(1, required=True)
  rollingUpdate = messages.MessageField('RollingUpdate', 2)
  zone = messages.StringField(3, required=True)


class ReplicapoolupdaterRollingUpdatesListInstanceUpdatesRequest(messages.Message):
  """A ReplicapoolupdaterRollingUpdatesListInstanceUpdatesRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: The Google Developers Console project name.
    rollingUpdate: The name of the update.
    zone: The name of the zone in which the update's target resides.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  rollingUpdate = messages.StringField(5, required=True)
  zone = messages.StringField(6, required=True)


class ReplicapoolupdaterRollingUpdatesListRequest(messages.Message):
  """A ReplicapoolupdaterRollingUpdatesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    instanceGroupManager: The name of the instance group manager used for
      filtering.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: The Google Developers Console project name.
    zone: The name of the zone in which the update's target resides.
  """

  filter = messages.StringField(1)
  instanceGroupManager = messages.StringField(2)
  maxResults = messages.IntegerField(3, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(4)
  project = messages.StringField(5, required=True)
  zone = messages.StringField(6, required=True)


class ReplicapoolupdaterRollingUpdatesPauseRequest(messages.Message):
  """A ReplicapoolupdaterRollingUpdatesPauseRequest object.

  Fields:
    project: The Google Developers Console project name.
    rollingUpdate: The name of the update.
    zone: The name of the zone in which the update's target resides.
  """

  project = messages.StringField(1, required=True)
  rollingUpdate = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ReplicapoolupdaterRollingUpdatesResumeRequest(messages.Message):
  """A ReplicapoolupdaterRollingUpdatesResumeRequest object.

  Fields:
    project: The Google Developers Console project name.
    rollingUpdate: The name of the update.
    zone: The name of the zone in which the update's target resides.
  """

  project = messages.StringField(1, required=True)
  rollingUpdate = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ReplicapoolupdaterRollingUpdatesRollbackRequest(messages.Message):
  """A ReplicapoolupdaterRollingUpdatesRollbackRequest object.

  Fields:
    project: The Google Developers Console project name.
    rollingUpdate: The name of the update.
    zone: The name of the zone in which the update's target resides.
  """

  project = messages.StringField(1, required=True)
  rollingUpdate = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ReplicapoolupdaterZoneOperationsGetRequest(messages.Message):
  """A ReplicapoolupdaterZoneOperationsGetRequest object.

  Fields:
    operation: Name of the operation resource to return.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  operation = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class RollingUpdate(messages.Message):
  """Resource describing a single update (rollout) of a group of instances to
  the given template.

  Messages:
    PolicyValue: Parameters of the update process. Setting
      (api.field).field_number manually is a workaround for b/16512602.

  Fields:
    actionType: Action to be performed for each instance. Possible values are:
      - "RECREATE": Instance will be recreated. Only for managed instance
      groups.  - "REBOOT": Soft reboot will be performed on an instance. Only
      for non-managed instance groups.
    creationTimestamp: [Output Only] Creation timestamp in RFC3339 text
      format.
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    id: [Output Only] Unique identifier for the resource; defined by the
      server.
    instanceGroup: URL of an instance group being updated. Exactly one of
      instance_group_manager and instance_group must be set.
    instanceGroupManager: URL of an instance group manager being updated.
      Exactly one of instance_group_manager and instance_group must be set.
    instanceTemplate: URL of an instance template to apply.
    kind: [Output Only] Type of the resource.
    policy: Parameters of the update process. Setting (api.field).field_number
      manually is a workaround for b/16512602.
    progress: [Output Only] An optional progress indicator that ranges from 0
      to 100. There is no requirement that this be linear or support any
      granularity of operations. This should not be used to guess at when the
      update will be complete. This number should be monotonically increasing
      as the update progresses.
    selfLink: [Output Only] The fully qualified URL for the resource.
    status: [Output Only] Status of the update. Possible values are:   -
      "ROLLING_FORWARD": The update is going forward.  - "ROLLING_BACK": The
      update is being rolled back.  - "PAUSED": The update is temporarily
      paused (inactive).  - "ROLLED_OUT": The update is finished, all
      instances have been updated successfully.  - "ROLLED_BACK": The update
      is finished, all instances have been reverted to the previous template.
      - "CANCELLED": The update is paused and no longer can be resumed,
      undefined how many instances are running in which template.
    statusMessage: [Output Only] An optional textual description of the
      current status of the update.
    user: [Output Only] User who requested the update, for example:
      user@example.com.
  """

  class PolicyValue(messages.Message):
    """Parameters of the update process. Setting (api.field).field_number
    manually is a workaround for b/16512602.

    Messages:
      CanaryValue: Parameters of a canary phase. If absent, canary will NOT be
        performed.

    Fields:
      canary: Parameters of a canary phase. If absent, canary will NOT be
        performed.
      maxNumConcurrentInstances: Maximum number of instances that can be
        updated simultaneously (concurrently). An update of an instance starts
        when the instance is about to be restarted and finishes after the
        instance has been restarted and the sleep period (defined by
        sleepAfterInstanceRestartSec) has passed.
      sleepAfterInstanceRestartSec: The number of seconds to wait between when
        the instance has been successfully updated and restarted, to when it
        is marked as done.
    """

    class CanaryValue(messages.Message):
      """Parameters of a canary phase. If absent, canary will NOT be
      performed.

      Fields:
        numInstances: Number of instances updated as a part of canary phase.
          If absent, the default number of instances will be used.
      """

      numInstances = messages.IntegerField(1, variant=messages.Variant.INT32)

    canary = messages.MessageField('CanaryValue', 1)
    maxNumConcurrentInstances = messages.IntegerField(2, variant=messages.Variant.INT32)
    sleepAfterInstanceRestartSec = messages.IntegerField(3, variant=messages.Variant.INT32)

  actionType = messages.StringField(1)
  creationTimestamp = messages.StringField(2)
  description = messages.StringField(3)
  id = messages.StringField(4)
  instanceGroup = messages.StringField(5)
  instanceGroupManager = messages.StringField(6)
  instanceTemplate = messages.StringField(7)
  kind = messages.StringField(8, default=u'replicapoolupdater#rollingUpdate')
  policy = messages.MessageField('PolicyValue', 9)
  progress = messages.IntegerField(10, variant=messages.Variant.INT32)
  selfLink = messages.StringField(11)
  status = messages.StringField(12)
  statusMessage = messages.StringField(13)
  user = messages.StringField(14)


class RollingUpdateList(messages.Message):
  """Response returned by List method.

  Fields:
    items: Collection of requested updates.
    kind: [Output Only] Type of the resource.
    nextPageToken: A token used to continue a truncated list request.
    selfLink: [Output Only] The fully qualified URL for the resource.
  """

  items = messages.MessageField('RollingUpdate', 1, repeated=True)
  kind = messages.StringField(2, default=u'replicapoolupdater#rollingUpdateList')
  nextPageToken = messages.StringField(3)
  selfLink = messages.StringField(4)


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


