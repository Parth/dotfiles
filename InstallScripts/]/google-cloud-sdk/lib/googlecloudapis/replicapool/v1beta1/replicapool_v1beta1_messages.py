"""Generated message classes for replicapool version v1beta1.

The Replica Pool API allows users to declaratively provision and manage groups
of Google Compute Engine instances based on a common template.
"""

from protorpc import messages


package = 'replicapool'


class AccessConfig(messages.Message):
  """A Compute Engine network accessConfig. Identical to the accessConfig on
  corresponding Compute Engine resource.

  Fields:
    name: Name of this access configuration.
    natIp: An external IP address associated with this instance.
    type: Type of this access configuration file. Currently only
      ONE_TO_ONE_NAT is supported.
  """

  name = messages.StringField(1)
  natIp = messages.StringField(2)
  type = messages.StringField(3)


class Action(messages.Message):
  """An action that gets executed during initialization of the replicas.

  Fields:
    commands: A list of commands to run, one per line. If any command fails,
      the whole action is considered a failure and no further actions are run.
      This also marks the virtual machine or replica as a failure.
    envVariables: A list of environment variables to use for the commands in
      this action.
    timeoutMilliSeconds: If an action's commands on a particular replica do
      not finish in the specified timeoutMilliSeconds, the replica is
      considered to be in a FAILING state. No efforts are made to stop any
      processes that were spawned or created as the result of running the
      action's commands. The default is the max allowed value, 1 hour (i.e.
      3600000 milliseconds).
  """

  commands = messages.StringField(1, repeated=True)
  envVariables = messages.MessageField('EnvVariable', 2, repeated=True)
  timeoutMilliSeconds = messages.IntegerField(3, variant=messages.Variant.INT32)


class DiskAttachment(messages.Message):
  """Specifies how to attach a disk to a Replica.

  Fields:
    deviceName: The device name of this disk.
    index: A zero-based index to assign to this disk, where 0 is reserved for
      the boot disk. If not specified, this is assigned by the server.
  """

  deviceName = messages.StringField(1)
  index = messages.IntegerField(2, variant=messages.Variant.UINT32)


class EnvVariable(messages.Message):
  """An environment variable to set for an action.

  Fields:
    hidden: Deprecated, do not use.
    name: The name of the environment variable.
    value: The value of the variable.
  """

  hidden = messages.BooleanField(1)
  name = messages.StringField(2)
  value = messages.StringField(3)


class ExistingDisk(messages.Message):
  """A pre-existing persistent disk that will be attached to every Replica in
  the Pool in READ_ONLY mode.

  Fields:
    attachment: How the disk will be attached to the Replica.
    source: The name of the Persistent Disk resource. The Persistent Disk
      resource must be in the same zone as the Pool.
  """

  attachment = messages.MessageField('DiskAttachment', 1)
  source = messages.StringField(2)


class HealthCheck(messages.Message):
  """A HealthCheck object.

  Fields:
    checkIntervalSec: How often (in seconds) to make HTTP requests for this
      healthcheck. The default value is 5 seconds.
    description: The description for this health check.
    healthyThreshold: The number of consecutive health check requests that
      need to succeed before the replica is considered healthy again. The
      default value is 2.
    host: The value of the host header in the HTTP health check request. If
      left empty (default value), the localhost IP 127.0.0.1 will be used.
    name: The name of this health check.
    path: The localhost request path to send this health check, in the format
      /path/to/use. For example, /healthcheck.
    port: The TCP port for the health check requests.
    timeoutSec: How long (in seconds) to wait before a timeout failure for
      this healthcheck. The default value is 5 seconds.
    unhealthyThreshold: The number of consecutive health check requests that
      need to fail in order to consider the replica unhealthy. The default
      value is 2.
  """

  checkIntervalSec = messages.IntegerField(1, variant=messages.Variant.INT32)
  description = messages.StringField(2)
  healthyThreshold = messages.IntegerField(3, variant=messages.Variant.INT32)
  host = messages.StringField(4)
  name = messages.StringField(5)
  path = messages.StringField(6)
  port = messages.IntegerField(7, variant=messages.Variant.INT32)
  timeoutSec = messages.IntegerField(8, variant=messages.Variant.INT32)
  unhealthyThreshold = messages.IntegerField(9, variant=messages.Variant.INT32)


class Label(messages.Message):
  """A label to apply to this replica pool.

  Fields:
    key: The key for this label.
    value: The value of this label.
  """

  key = messages.StringField(1)
  value = messages.StringField(2)


class Metadata(messages.Message):
  """A Compute Engine metadata entry. Identical to the metadata on the
  corresponding Compute Engine resource.

  Fields:
    fingerPrint: The fingerprint of the metadata. Required for updating the
      metadata entries for this instance.
    items: A list of metadata items.
  """

  fingerPrint = messages.StringField(1)
  items = messages.MessageField('MetadataItem', 2, repeated=True)


class MetadataItem(messages.Message):
  """A Compute Engine metadata item, defined as a key:value pair. Identical to
  the metadata on the corresponding Compute Engine resource.

  Fields:
    key: A metadata key.
    value: A metadata value.
  """

  key = messages.StringField(1)
  value = messages.StringField(2)


class NetworkInterface(messages.Message):
  """A Compute Engine NetworkInterface resource. Identical to the
  NetworkInterface on the corresponding Compute Engine resource.

  Fields:
    accessConfigs: An array of configurations for this interface. This
      specifies how this interface is configured to interact with other
      network services.
    network: Name the Network resource to which this interface applies.
    networkIp: An optional IPV4 internal network address to assign to the
      instance for this network interface.
  """

  accessConfigs = messages.MessageField('AccessConfig', 1, repeated=True)
  network = messages.StringField(2)
  networkIp = messages.StringField(3)


class NewDisk(messages.Message):
  """A Persistent Disk resource that will be created and attached to each
  Replica in the Pool. Each Replica will have a unique persistent disk that is
  created and attached to that Replica in READ_WRITE mode.

  Fields:
    attachment: How the disk will be attached to the Replica.
    autoDelete: If true, then this disk will be deleted when the instance is
      deleted. The default value is true.
    boot: If true, indicates that this is the root persistent disk.
    initializeParams: Create the new disk using these parameters. The name of
      the disk will be <instance_name>-<four_random_charactersgt;.
  """

  attachment = messages.MessageField('DiskAttachment', 1)
  autoDelete = messages.BooleanField(2)
  boot = messages.BooleanField(3)
  initializeParams = messages.MessageField('NewDiskInitializeParams', 4)


class NewDiskInitializeParams(messages.Message):
  """Initialization parameters for creating a new disk.

  Fields:
    diskSizeGb: The size of the created disk in gigabytes.
    diskType: Name of the disk type resource describing which disk type to use
      to create the disk. For example 'pd-ssd' or 'pd-standard'. Default is
      'pd-standard'
    sourceImage: The name or fully-qualified URL of a source image to use to
      create this disk. If you provide a name of the source image, Replica
      Pool will look for an image with that name in your project. If you are
      specifying an image provided by Compute Engine, you will need to provide
      the full URL with the correct project, such as:
      http://www.googleapis.com/compute/v1/projects/debian-cloud/
      global/images/debian-wheezy-7-vYYYYMMDD
  """

  diskSizeGb = messages.IntegerField(1)
  diskType = messages.StringField(2)
  sourceImage = messages.StringField(3)


class Pool(messages.Message):
  """A Pool object.

  Fields:
    autoRestart: Whether replicas in this pool should be restarted if they
      experience a failure. The default value is true.
    baseInstanceName: The base instance name to use for the replicas in this
      pool. This must match the regex [a-z]([-a-z0-9]*[a-z0-9])?. If
      specified, the instances in this replica pool will be named in the
      format <base-instance-name>-<ID>. The <ID> postfix will be a four
      character alphanumeric identifier generated by the service.  If this is
      not specified by the user, a random base instance name is generated by
      the service.
    currentNumReplicas: [Output Only] The current number of replicas in the
      pool.
    description: An optional description of the replica pool.
    healthChecks: Deprecated. Please use template[].healthChecks instead.
    initialNumReplicas: The initial number of replicas this pool should have.
      You must provide a value greater than or equal to 0.
    labels: A list of labels to attach to this replica pool and all created
      virtual machines in this replica pool.
    name: The name of the replica pool. Must follow the regex
      [a-z]([-a-z0-9]*[a-z0-9])? and be 1-28 characters long.
    numReplicas: Deprecated! Use initial_num_replicas instead.
    resourceViews: The list of resource views that should be updated with all
      the replicas that are managed by this pool.
    selfLink: [Output Only] A self-link to the replica pool.
    targetPool: Deprecated, please use target_pools instead.
    targetPools: A list of target pools to update with the replicas that are
      managed by this pool. If specified, the replicas in this replica pool
      will be added to the specified target pools for load balancing purposes.
      The replica pool must live in the same region as the specified target
      pools. These values must be the target pool resource names, and not
      fully qualified URLs.
    template: The template to use when creating replicas in this pool. This
      template is used during initial instance creation of the pool, when
      growing the pool in size, or when a replica restarts.
    type: Deprecated! Do not set.
  """

  autoRestart = messages.BooleanField(1)
  baseInstanceName = messages.StringField(2)
  currentNumReplicas = messages.IntegerField(3, variant=messages.Variant.INT32)
  description = messages.StringField(4)
  healthChecks = messages.MessageField('HealthCheck', 5, repeated=True)
  initialNumReplicas = messages.IntegerField(6, variant=messages.Variant.INT32)
  labels = messages.MessageField('Label', 7, repeated=True)
  name = messages.StringField(8)
  numReplicas = messages.IntegerField(9, variant=messages.Variant.INT32)
  resourceViews = messages.StringField(10, repeated=True)
  selfLink = messages.StringField(11)
  targetPool = messages.StringField(12)
  targetPools = messages.StringField(13, repeated=True)
  template = messages.MessageField('Template', 14)
  type = messages.StringField(15)


class PoolsDeleteRequest(messages.Message):
  """A PoolsDeleteRequest object.

  Fields:
    abandonInstances: If there are instances you would like to keep, you can
      specify them here. These instances won't be deleted, but the associated
      replica objects will be removed.
  """

  abandonInstances = messages.StringField(1, repeated=True)


class PoolsListResponse(messages.Message):
  """A PoolsListResponse object.

  Fields:
    nextPageToken: A string attribute.
    resources: A Pool attribute.
  """

  nextPageToken = messages.StringField(1)
  resources = messages.MessageField('Pool', 2, repeated=True)


class Replica(messages.Message):
  """An individual Replica within a Pool. Replicas are automatically created
  by the replica pool, using the template provided by the user. You cannot
  directly create replicas.

  Fields:
    name: [Output Only] The name of the Replica object.
    selfLink: [Output Only] The self-link of the Replica.
    status: [Output Only] Last known status of the Replica.
  """

  name = messages.StringField(1)
  selfLink = messages.StringField(2)
  status = messages.MessageField('ReplicaStatus', 3)


class ReplicaStatus(messages.Message):
  """The current status of a Replica.

  Fields:
    details: [Output Only] Human-readable details about the current state of
      the replica
    state: [Output Only] The state of the Replica.
    templateVersion: [Output Only] The template used to build the replica.
    vmLink: [Output Only] Link to the virtual machine that this Replica
      represents.
    vmStartTime: [Output Only] The time that this Replica got to the RUNNING
      state, in RFC 3339 format. If the start time is unknown, UNKNOWN is
      returned.
  """

  details = messages.StringField(1)
  state = messages.StringField(2)
  templateVersion = messages.StringField(3)
  vmLink = messages.StringField(4)
  vmStartTime = messages.StringField(5)


class ReplicapoolPoolsDeleteRequest(messages.Message):
  """A ReplicapoolPoolsDeleteRequest object.

  Fields:
    poolName: The name of the replica pool for this request.
    poolsDeleteRequest: A PoolsDeleteRequest resource to be passed as the
      request body.
    projectName: The project ID for this replica pool.
    zone: The zone for this replica pool.
  """

  poolName = messages.StringField(1, required=True)
  poolsDeleteRequest = messages.MessageField('PoolsDeleteRequest', 2)
  projectName = messages.StringField(3, required=True)
  zone = messages.StringField(4, required=True)


class ReplicapoolPoolsDeleteResponse(messages.Message):
  """An empty ReplicapoolPoolsDelete response."""


class ReplicapoolPoolsGetRequest(messages.Message):
  """A ReplicapoolPoolsGetRequest object.

  Fields:
    poolName: The name of the replica pool for this request.
    projectName: The project ID for this replica pool.
    zone: The zone for this replica pool.
  """

  poolName = messages.StringField(1, required=True)
  projectName = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ReplicapoolPoolsInsertRequest(messages.Message):
  """A ReplicapoolPoolsInsertRequest object.

  Fields:
    pool: A Pool resource to be passed as the request body.
    projectName: The project ID for this replica pool.
    zone: The zone for this replica pool.
  """

  pool = messages.MessageField('Pool', 1)
  projectName = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ReplicapoolPoolsListRequest(messages.Message):
  """A ReplicapoolPoolsListRequest object.

  Fields:
    maxResults: Maximum count of results to be returned. Acceptable values are
      0 to 100, inclusive. (Default: 50)
    pageToken: Set this to the nextPageToken value returned by a previous list
      request to obtain the next page of results from the previous list
      request.
    projectName: The project ID for this request.
    zone: The zone for this replica pool.
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.INT32, default=500)
  pageToken = messages.StringField(2)
  projectName = messages.StringField(3, required=True)
  zone = messages.StringField(4, required=True)


class ReplicapoolPoolsResizeRequest(messages.Message):
  """A ReplicapoolPoolsResizeRequest object.

  Fields:
    numReplicas: The desired number of replicas to resize to. If this number
      is larger than the existing number of replicas, new replicas will be
      added. If the number is smaller, then existing replicas will be deleted.
    poolName: The name of the replica pool for this request.
    projectName: The project ID for this replica pool.
    zone: The zone for this replica pool.
  """

  numReplicas = messages.IntegerField(1, variant=messages.Variant.INT32)
  poolName = messages.StringField(2, required=True)
  projectName = messages.StringField(3, required=True)
  zone = messages.StringField(4, required=True)


class ReplicapoolPoolsUpdatetemplateRequest(messages.Message):
  """A ReplicapoolPoolsUpdatetemplateRequest object.

  Fields:
    poolName: The name of the replica pool for this request.
    projectName: The project ID for this replica pool.
    template: A Template resource to be passed as the request body.
    zone: The zone for this replica pool.
  """

  poolName = messages.StringField(1, required=True)
  projectName = messages.StringField(2, required=True)
  template = messages.MessageField('Template', 3)
  zone = messages.StringField(4, required=True)


class ReplicapoolPoolsUpdatetemplateResponse(messages.Message):
  """An empty ReplicapoolPoolsUpdatetemplate response."""


class ReplicapoolReplicasDeleteRequest(messages.Message):
  """A ReplicapoolReplicasDeleteRequest object.

  Fields:
    poolName: The replica pool name for this request.
    projectName: The project ID for this request.
    replicaName: The name of the replica for this request.
    replicasDeleteRequest: A ReplicasDeleteRequest resource to be passed as
      the request body.
    zone: The zone where the replica lives.
  """

  poolName = messages.StringField(1, required=True)
  projectName = messages.StringField(2, required=True)
  replicaName = messages.StringField(3, required=True)
  replicasDeleteRequest = messages.MessageField('ReplicasDeleteRequest', 4)
  zone = messages.StringField(5, required=True)


class ReplicapoolReplicasGetRequest(messages.Message):
  """A ReplicapoolReplicasGetRequest object.

  Fields:
    poolName: The replica pool name for this request.
    projectName: The project ID for this request.
    replicaName: The name of the replica for this request.
    zone: The zone where the replica lives.
  """

  poolName = messages.StringField(1, required=True)
  projectName = messages.StringField(2, required=True)
  replicaName = messages.StringField(3, required=True)
  zone = messages.StringField(4, required=True)


class ReplicapoolReplicasListRequest(messages.Message):
  """A ReplicapoolReplicasListRequest object.

  Fields:
    maxResults: Maximum count of results to be returned. Acceptable values are
      0 to 100, inclusive. (Default: 50)
    pageToken: Set this to the nextPageToken value returned by a previous list
      request to obtain the next page of results from the previous list
      request.
    poolName: The replica pool name for this request.
    projectName: The project ID for this request.
    zone: The zone where the replica pool lives.
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.INT32, default=500)
  pageToken = messages.StringField(2)
  poolName = messages.StringField(3, required=True)
  projectName = messages.StringField(4, required=True)
  zone = messages.StringField(5, required=True)


class ReplicapoolReplicasRestartRequest(messages.Message):
  """A ReplicapoolReplicasRestartRequest object.

  Fields:
    poolName: The replica pool name for this request.
    projectName: The project ID for this request.
    replicaName: The name of the replica for this request.
    zone: The zone where the replica lives.
  """

  poolName = messages.StringField(1, required=True)
  projectName = messages.StringField(2, required=True)
  replicaName = messages.StringField(3, required=True)
  zone = messages.StringField(4, required=True)


class ReplicasDeleteRequest(messages.Message):
  """A ReplicasDeleteRequest object.

  Fields:
    abandonInstance: Whether the instance resource represented by this replica
      should be deleted or abandoned. If abandoned, the replica will be
      deleted but the virtual machine instance will remain. By default, this
      is set to false and the instance will be deleted along with the replica.
  """

  abandonInstance = messages.BooleanField(1)


class ReplicasListResponse(messages.Message):
  """A ReplicasListResponse object.

  Fields:
    nextPageToken: A string attribute.
    resources: A Replica attribute.
  """

  nextPageToken = messages.StringField(1)
  resources = messages.MessageField('Replica', 2, repeated=True)


class ServiceAccount(messages.Message):
  """A Compute Engine service account, identical to the Compute Engine
  resource.

  Fields:
    email: The service account email address, for example:
      123845678986@project.gserviceaccount.com
    scopes: The list of OAuth2 scopes to obtain for the service account, for
      example: https://www.googleapis.com/auth/devstorage.full_control
  """

  email = messages.StringField(1)
  scopes = messages.StringField(2, repeated=True)


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


class Tag(messages.Message):
  """A Compute Engine Instance tag, identical to the tags on the corresponding
  Compute Engine Instance resource.

  Fields:
    fingerPrint: The fingerprint of the tag. Required for updating the list of
      tags.
    items: Items contained in this tag.
  """

  fingerPrint = messages.StringField(1)
  items = messages.StringField(2, repeated=True)


class Template(messages.Message):
  """The template used for creating replicas in the pool.

  Fields:
    action: An action to run during initialization of your replicas. An action
      is run as shell commands which are executed one after the other in the
      same bash shell, so any state established by one command is inherited by
      later commands.
    healthChecks: A list of HTTP Health Checks to configure for this replica
      pool and all virtual machines in this replica pool.
    version: A free-form string describing the version of this template. You
      can provide any versioning string you would like. For example, version1
      or template-v1.
    vmParams: The virtual machine parameters to use for creating replicas. You
      can define settings such as the machine type and the image of replicas
      in this pool. This is required if replica type is SMART_VM.
  """

  action = messages.MessageField('Action', 1)
  healthChecks = messages.MessageField('HealthCheck', 2, repeated=True)
  version = messages.StringField(3)
  vmParams = messages.MessageField('VmParams', 4)


class VmParams(messages.Message):
  """Parameters for creating a Compute Engine Instance resource. Most fields
  are identical to the corresponding Compute Engine resource.

  Fields:
    baseInstanceName: Deprecated. Please use baseInstanceName instead.
    canIpForward: Enables IP Forwarding, which allows this instance to receive
      packets destined for a different IP address, and send packets with a
      different source IP. See IP Forwarding for more information.
    description: An optional textual description of the instance.
    disksToAttach: A list of existing Persistent Disk resources to attach to
      each replica in the pool. Each disk will be attached in read-only mode
      to every replica.
    disksToCreate: A list of Disk resources to create and attach to each
      Replica in the Pool. Currently, you can only define one disk and it must
      be a root persistent disk. Note that Replica Pool will create a root
      persistent disk for each replica.
    machineType: The machine type for this instance. The resource name (e.g.
      n1-standard-1).
    metadata: The metadata key/value pairs assigned to this instance.
    networkInterfaces: A list of network interfaces for the instance.
      Currently only one interface is supported by Google Compute Engine,
      ONE_TO_ONE_NAT.
    onHostMaintenance: A string attribute.
    serviceAccounts: A list of Service Accounts to enable for this instance.
    tags: A list of tags to apply to the Google Compute Engine instance to
      identify resources.
  """

  baseInstanceName = messages.StringField(1)
  canIpForward = messages.BooleanField(2)
  description = messages.StringField(3)
  disksToAttach = messages.MessageField('ExistingDisk', 4, repeated=True)
  disksToCreate = messages.MessageField('NewDisk', 5, repeated=True)
  machineType = messages.StringField(6)
  metadata = messages.MessageField('Metadata', 7)
  networkInterfaces = messages.MessageField('NetworkInterface', 8, repeated=True)
  onHostMaintenance = messages.StringField(9)
  serviceAccounts = messages.MessageField('ServiceAccount', 10, repeated=True)
  tags = messages.MessageField('Tag', 11)


