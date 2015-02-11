"""Generated message classes for manager version v1beta2.

The Deployment Manager API allows users to declaratively configure, deploy and
run complex solutions on the Google Cloud Platform.
"""

from protorpc import messages

from googlecloudapis.apitools.base.py import encoding


package = 'manager'


class AccessConfig(messages.Message):
  """A Compute Engine network accessConfig. Identical to the accessConfig on
  corresponding Compute Engine resource.

  Fields:
    name: Name of this access configuration.
    natIp: An external IP address associated with this instance.
    type: Type of this access configuration file. (Currently only
      ONE_TO_ONE_NAT is legal.)
  """

  name = messages.StringField(1)
  natIp = messages.StringField(2)
  type = messages.StringField(3)


class Action(messages.Message):
  """An Action encapsulates a set of commands as a single runnable module with
  additional information needed during run-time.

  Fields:
    commands: A list of commands to run sequentially for this action.
    timeoutMs: The timeout in milliseconds for this action to run.
  """

  commands = messages.StringField(1, repeated=True)
  timeoutMs = messages.IntegerField(2, variant=messages.Variant.INT32)


class AllowedRule(messages.Message):
  """An allowed port resource.

  Fields:
    IPProtocol: ?tcp?, ?udp? or ?icmp?
    ports: List of ports or port ranges (Example inputs include: ["22"],
      [?33?, "12345-12349"].
  """

  IPProtocol = messages.StringField(1)
  ports = messages.StringField(2, repeated=True)


class AutoscalingModule(messages.Message):
  """A AutoscalingModule object.

  Fields:
    coolDownPeriodSec: A integer attribute.
    description: A string attribute.
    maxNumReplicas: A integer attribute.
    minNumReplicas: A integer attribute.
    signalType: A string attribute.
    targetModule: A string attribute.
    targetUtilization: target_utilization should be in range [0,1].
  """

  coolDownPeriodSec = messages.IntegerField(1, variant=messages.Variant.INT32)
  description = messages.StringField(2)
  maxNumReplicas = messages.IntegerField(3, variant=messages.Variant.INT32)
  minNumReplicas = messages.IntegerField(4, variant=messages.Variant.INT32)
  signalType = messages.StringField(5)
  targetModule = messages.StringField(6)
  targetUtilization = messages.FloatField(7)


class AutoscalingModuleStatus(messages.Message):
  """A AutoscalingModuleStatus object.

  Fields:
    autoscalingConfigUrl: [Output Only] The URL of the corresponding
      Autoscaling configuration.
  """

  autoscalingConfigUrl = messages.StringField(1)


class DeployState(messages.Message):
  """[Output Only] The current state of a replica or module.

  Fields:
    details: [Output Only] Human readable details about the current state.
    status: [Output Only] The status of the deployment. Possible values
      include:  - UNKNOWN - DEPLOYING - DEPLOYED - DEPLOYMENT_FAILED -
      DELETING - DELETED - DELETE_FAILED
  """

  details = messages.StringField(1)
  status = messages.StringField(2)


class Deployment(messages.Message):
  """A deployment represents a physical instantiation of a Template.

  Messages:
    ModulesValue: [Output Only] List of status for the modules in this
      deployment.

  Fields:
    creationDate: [Output Only] The time when this deployment was created.
    description: A user-supplied description of this Deployment.
    modules: [Output Only] List of status for the modules in this deployment.
    name: Name of this deployment. The name must conform to the following
      regular expression: [a-zA-Z0-9-_]{1,64}
    overrides: The set of parameter overrides to apply to the corresponding
      Template before deploying.
    state: [Output Only] Current status of this deployment.
    templateName: The name of the Template on which this deployment is based.
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ModulesValue(messages.Message):
    """[Output Only] List of status for the modules in this deployment.

    Messages:
      AdditionalProperty: An additional property for a ModulesValue object.

    Fields:
      additionalProperties: Name of the module.
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a ModulesValue object.

      Fields:
        key: Name of the additional property.
        value: A ModuleStatus attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('ModuleStatus', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  creationDate = messages.StringField(1)
  description = messages.StringField(2)
  modules = messages.MessageField('ModulesValue', 3)
  name = messages.StringField(4)
  overrides = messages.MessageField('ParamOverride', 5, repeated=True)
  state = messages.MessageField('DeployState', 6)
  templateName = messages.StringField(7)


class DeploymentsListResponse(messages.Message):
  """A DeploymentsListResponse object.

  Fields:
    nextPageToken: A string attribute.
    resources: A Deployment attribute.
  """

  nextPageToken = messages.StringField(1)
  resources = messages.MessageField('Deployment', 2, repeated=True)


class DiskAttachment(messages.Message):
  """How to attach a disk to a Replica.

  Fields:
    deviceName: The device name of this disk.
    index: A zero-based index to assign to this disk, where 0 is reserved for
      the boot disk. If not specified, this is assigned by the server.
  """

  deviceName = messages.StringField(1)
  index = messages.IntegerField(2, variant=messages.Variant.UINT32)


class EnvVariable(messages.Message):
  """An environment variable.

  Fields:
    hidden: Whether this variable is hidden or visible.
    value: Value of the environment variable.
  """

  hidden = messages.BooleanField(1)
  value = messages.StringField(2)


class ExistingDisk(messages.Message):
  """A pre-existing persistent disk that will be attached to every Replica in
  the Pool.

  Fields:
    attachment: Optional. How the disk will be attached to the Replica.
    source: The fully-qualified URL of the Persistent Disk resource. It must
      be in the same zone as the Pool.
  """

  attachment = messages.MessageField('DiskAttachment', 1)
  source = messages.StringField(2)


class FirewallModule(messages.Message):
  """A Firewall resource

  Fields:
    allowed: The allowed ports or port ranges.
    description: The description of the firewall (optional)
    network: The NetworkModule to which this firewall should apply. If not
      specified, or if specified as 'default', this firewall will be applied
      to the 'default' network.
    sourceRanges: Source IP ranges to apply this firewall to, see the GCE Spec
      for details on syntax
    sourceTags: Source Tags to apply this firewall to, see the GCE Spec for
      details on syntax
    targetTags: Target Tags to apply this firewall to, see the GCE Spec for
      details on syntax
  """

  allowed = messages.MessageField('AllowedRule', 1, repeated=True)
  description = messages.StringField(2)
  network = messages.StringField(3)
  sourceRanges = messages.StringField(4, repeated=True)
  sourceTags = messages.StringField(5, repeated=True)
  targetTags = messages.StringField(6, repeated=True)


class FirewallModuleStatus(messages.Message):
  """A FirewallModuleStatus object.

  Fields:
    firewallUrl: [Output Only] The URL of the corresponding Firewall resource.
  """

  firewallUrl = messages.StringField(1)


class HealthCheckModule(messages.Message):
  """A HealthCheckModule object.

  Fields:
    checkIntervalSec: A integer attribute.
    description: A string attribute.
    healthyThreshold: A integer attribute.
    host: A string attribute.
    path: A string attribute.
    port: A integer attribute.
    timeoutSec: A integer attribute.
    unhealthyThreshold: A integer attribute.
  """

  checkIntervalSec = messages.IntegerField(1, variant=messages.Variant.INT32)
  description = messages.StringField(2)
  healthyThreshold = messages.IntegerField(3, variant=messages.Variant.INT32)
  host = messages.StringField(4)
  path = messages.StringField(5)
  port = messages.IntegerField(6, variant=messages.Variant.INT32)
  timeoutSec = messages.IntegerField(7, variant=messages.Variant.INT32)
  unhealthyThreshold = messages.IntegerField(8, variant=messages.Variant.INT32)


class HealthCheckModuleStatus(messages.Message):
  """A HealthCheckModuleStatus object.

  Fields:
    healthCheckUrl: [Output Only] The HealthCheck URL.
  """

  healthCheckUrl = messages.StringField(1)


class LbModule(messages.Message):
  """A LbModule object.

  Fields:
    description: A string attribute.
    healthChecks: A string attribute.
    ipAddress: A string attribute.
    ipProtocol: A string attribute.
    portRange: A string attribute.
    sessionAffinity: A string attribute.
    targetModules: A string attribute.
  """

  description = messages.StringField(1)
  healthChecks = messages.StringField(2, repeated=True)
  ipAddress = messages.StringField(3)
  ipProtocol = messages.StringField(4)
  portRange = messages.StringField(5)
  sessionAffinity = messages.StringField(6)
  targetModules = messages.StringField(7, repeated=True)


class LbModuleStatus(messages.Message):
  """A LbModuleStatus object.

  Fields:
    forwardingRuleUrl: [Output Only] The URL of the corresponding
      ForwardingRule in GCE.
    targetPoolUrl: [Output Only] The URL of the corresponding TargetPool
      resource in GCE.
  """

  forwardingRuleUrl = messages.StringField(1)
  targetPoolUrl = messages.StringField(2)


class ManagerDeploymentsDeleteRequest(messages.Message):
  """A ManagerDeploymentsDeleteRequest object.

  Fields:
    deploymentName: A string attribute.
    projectId: A string attribute.
    region: A string attribute.
  """

  deploymentName = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)


class ManagerDeploymentsDeleteResponse(messages.Message):
  """An empty ManagerDeploymentsDelete response."""


class ManagerDeploymentsGetRequest(messages.Message):
  """A ManagerDeploymentsGetRequest object.

  Fields:
    deploymentName: A string attribute.
    projectId: A string attribute.
    region: A string attribute.
  """

  deploymentName = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)


class ManagerDeploymentsInsertRequest(messages.Message):
  """A ManagerDeploymentsInsertRequest object.

  Fields:
    deployment: A Deployment resource to be passed as the request body.
    projectId: A string attribute.
    region: A string attribute.
  """

  deployment = messages.MessageField('Deployment', 1)
  projectId = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)


class ManagerDeploymentsListRequest(messages.Message):
  """A ManagerDeploymentsListRequest object.

  Fields:
    maxResults: Maximum count of results to be returned. Acceptable values are
      0 to 100, inclusive. (Default: 50)
    pageToken: Specifies a nextPageToken returned by a previous list request.
      This token can be used to request the next page of results from a
      previous list request.
    projectId: A string attribute.
    region: A string attribute.
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.INT32, default=50)
  pageToken = messages.StringField(2)
  projectId = messages.StringField(3, required=True)
  region = messages.StringField(4, required=True)


class ManagerTemplatesDeleteRequest(messages.Message):
  """A ManagerTemplatesDeleteRequest object.

  Fields:
    projectId: A string attribute.
    templateName: A string attribute.
  """

  projectId = messages.StringField(1, required=True)
  templateName = messages.StringField(2, required=True)


class ManagerTemplatesDeleteResponse(messages.Message):
  """An empty ManagerTemplatesDelete response."""


class ManagerTemplatesGetRequest(messages.Message):
  """A ManagerTemplatesGetRequest object.

  Fields:
    projectId: A string attribute.
    templateName: A string attribute.
  """

  projectId = messages.StringField(1, required=True)
  templateName = messages.StringField(2, required=True)


class ManagerTemplatesInsertRequest(messages.Message):
  """A ManagerTemplatesInsertRequest object.

  Fields:
    projectId: A string attribute.
    template: A Template resource to be passed as the request body.
  """

  projectId = messages.StringField(1, required=True)
  template = messages.MessageField('Template', 2)


class ManagerTemplatesListRequest(messages.Message):
  """A ManagerTemplatesListRequest object.

  Fields:
    maxResults: Maximum count of results to be returned. Acceptable values are
      0 to 100, inclusive. (Default: 50)
    pageToken: Specifies a nextPageToken returned by a previous list request.
      This token can be used to request the next page of results from a
      previous list request.
    projectId: A string attribute.
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.INT32, default=50)
  pageToken = messages.StringField(2)
  projectId = messages.StringField(3, required=True)


class Metadata(messages.Message):
  """A Compute Engine metadata entry. Identical to the metadata on the
  corresponding Compute Engine resource.

  Fields:
    fingerPrint: The fingerprint of the metadata.
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


class Module(messages.Message):
  """A module in a configuration. A module represents a single homogeneous,
  possibly replicated task.

  Fields:
    autoscalingModule: A AutoscalingModule attribute.
    firewallModule: A FirewallModule attribute.
    healthCheckModule: A HealthCheckModule attribute.
    lbModule: A LbModule attribute.
    networkModule: A NetworkModule attribute.
    replicaPoolModule: A ReplicaPoolModule attribute.
    type: The type of this module. Valid values ("AUTOSCALING", "FIREWALL",
      "HEALTH_CHECK", "LOAD_BALANCING", "NETWORK", "REPLICA_POOL")
  """

  autoscalingModule = messages.MessageField('AutoscalingModule', 1)
  firewallModule = messages.MessageField('FirewallModule', 2)
  healthCheckModule = messages.MessageField('HealthCheckModule', 3)
  lbModule = messages.MessageField('LbModule', 4)
  networkModule = messages.MessageField('NetworkModule', 5)
  replicaPoolModule = messages.MessageField('ReplicaPoolModule', 6)
  type = messages.StringField(7)


class ModuleStatus(messages.Message):
  """[Output Only] Aggregate status for a module.

  Fields:
    autoscalingModuleStatus: [Output Only] The status of the
      AutoscalingModule, set for type AUTOSCALING.
    firewallModuleStatus: [Output Only] The status of the FirewallModule, set
      for type FIREWALL.
    healthCheckModuleStatus: [Output Only] The status of the
      HealthCheckModule, set for type HEALTH_CHECK.
    lbModuleStatus: [Output Only] The status of the LbModule, set for type
      LOAD_BALANCING.
    networkModuleStatus: [Output Only] The status of the NetworkModule, set
      for type NETWORK.
    replicaPoolModuleStatus: [Output Only] The status of the
      ReplicaPoolModule, set for type VM.
    state: [Output Only] The current state of the module.
    type: [Output Only] The type of the module.
  """

  autoscalingModuleStatus = messages.MessageField('AutoscalingModuleStatus', 1)
  firewallModuleStatus = messages.MessageField('FirewallModuleStatus', 2)
  healthCheckModuleStatus = messages.MessageField('HealthCheckModuleStatus', 3)
  lbModuleStatus = messages.MessageField('LbModuleStatus', 4)
  networkModuleStatus = messages.MessageField('NetworkModuleStatus', 5)
  replicaPoolModuleStatus = messages.MessageField('ReplicaPoolModuleStatus', 6)
  state = messages.MessageField('DeployState', 7)
  type = messages.StringField(8)


class NetworkInterface(messages.Message):
  """A Compute Engine NetworkInterface resource. Identical to the
  NetworkInterface on the corresponding Compute Engine resource.

  Fields:
    accessConfigs: An array of configurations for this interface. This
      specifies how this interface is configured to interact with other
      network services
    name: Name of the interface.
    network: The name of the NetworkModule to which this interface applies. If
      not specified, or specified as 'default', this will use the 'default'
      network.
    networkIp: An optional IPV4 internal network address to assign to the
      instance for this network interface.
  """

  accessConfigs = messages.MessageField('AccessConfig', 1, repeated=True)
  name = messages.StringField(2)
  network = messages.StringField(3)
  networkIp = messages.StringField(4)


class NetworkModule(messages.Message):
  """A NetworkModule object.

  Fields:
    IPv4Range: Required; The range of internal addresses that are legal on
      this network. This range is a CIDR specification, for example:
      192.168.0.0/16.
    description: The description of the network.
    gatewayIPv4: An optional address that is used for default routing to other
      networks. This must be within the range specified by IPv4Range, and is
      typicall the first usable address in that range. If not specified, the
      default value is the first usable address in IPv4Range.
  """

  IPv4Range = messages.StringField(1)
  description = messages.StringField(2)
  gatewayIPv4 = messages.StringField(3)


class NetworkModuleStatus(messages.Message):
  """A NetworkModuleStatus object.

  Fields:
    networkUrl: [Output Only] The URL of the corresponding Network resource.
  """

  networkUrl = messages.StringField(1)


class NewDisk(messages.Message):
  """A Persistent Disk resource that will be created and attached to each
  Replica in the Pool. Each Replica will have a unique persistent disk that is
  created and attached to that Replica.

  Fields:
    attachment: How the disk will be attached to the Replica.
    autoDelete: If true, then this disk will be deleted when the instance is
      deleted.
    boot: If true, indicates that this is the root persistent disk.
    initializeParams: Create the new disk using these parameters. The name of
      the disk will be <instance_name>-<five_random_charactersgt;.
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
    sourceImage: The fully-qualified URL of a source image to use to create
      this disk.
  """

  diskSizeGb = messages.IntegerField(1)
  diskType = messages.StringField(2)
  sourceImage = messages.StringField(3)


class ParamOverride(messages.Message):
  """A specification for overriding parameters in a Template that corresponds
  to the Deployment.

  Fields:
    path: A JSON Path expression that specifies which parameter should be
      overridden.
    value: The new value to assign to the overridden parameter.
  """

  path = messages.StringField(1)
  value = messages.StringField(2)


class ReplicaPoolModule(messages.Message):
  """A ReplicaPoolModule object.

  Messages:
    EnvVariablesValue: A list of environment variables.

  Fields:
    envVariables: A list of environment variables.
    healthChecks: The Health Checks to configure for the ReplicaPoolModule
    numReplicas: Number of replicas in this module.
    replicaPoolParams: Information for a ReplicaPoolModule.
    resourceView: [Output Only] The name of the Resource View associated with
      a ReplicaPoolModule. This field will be generated by the service.
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class EnvVariablesValue(messages.Message):
    """A list of environment variables.

    Messages:
      AdditionalProperty: An additional property for a EnvVariablesValue
        object.

    Fields:
      additionalProperties: Name of the environment variable. The name must
        conform to the following regular expression: [a-zA-Z_]+[a-zA-Z0-9_]+.
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a EnvVariablesValue object.

      Fields:
        key: Name of the additional property.
        value: A EnvVariable attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('EnvVariable', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  envVariables = messages.MessageField('EnvVariablesValue', 1)
  healthChecks = messages.StringField(2, repeated=True)
  numReplicas = messages.IntegerField(3, variant=messages.Variant.INT32)
  replicaPoolParams = messages.MessageField('ReplicaPoolParams', 4)
  resourceView = messages.StringField(5)


class ReplicaPoolModuleStatus(messages.Message):
  """A ReplicaPoolModuleStatus object.

  Fields:
    replicaPoolUrl: [Output Only] The URL of the associated ReplicaPool
      resource.
    resourceViewUrl: [Output Only] The URL of the Resource Group associated
      with this ReplicaPool.
  """

  replicaPoolUrl = messages.StringField(1)
  resourceViewUrl = messages.StringField(2)


class ReplicaPoolParams(messages.Message):
  """Configuration information for a ReplicaPools resource. Specifying an item
  within will determine the ReplicaPools API version used for a
  ReplicaPoolModule. Only one may be specified.

  Fields:
    v1beta1: ReplicaPoolParams specifications for use with ReplicaPools
      v1beta1.
  """

  v1beta1 = messages.MessageField('ReplicaPoolParamsV1Beta1', 1)


class ReplicaPoolParamsV1Beta1(messages.Message):
  """Configuration information for a ReplicaPools v1beta1 API resource.
  Directly maps to ReplicaPool InitTemplate.

  Fields:
    autoRestart: Whether these replicas should be restarted if they experience
      a failure. The default value is true.
    baseInstanceName: The base name for instances within this ReplicaPool.
    canIpForward: Enables IP Forwarding
    description: An optional textual description of the resource.
    disksToAttach: A list of existing Persistent Disk resources to attach to
      each replica in the pool. Each disk will be attached in read-only mode
      to every replica.
    disksToCreate: A list of Disk resources to create and attach to each
      Replica in the Pool. Currently, you can only define one disk and it must
      be a root persistent disk. Note that Replica Pool will create a root
      persistent disk for each replica.
    initAction: Name of the Action to be run during initialization of a
      ReplicaPoolModule.
    machineType: The machine type for this instance. Either a complete URL, or
      the resource name (e.g. n1-standard-1).
    metadata: The metadata key/value pairs assigned to this instance.
    networkInterfaces: A list of network interfaces for the instance.
      Currently only one interface is supported by Google Compute Engine.
    onHostMaintenance: A string attribute.
    serviceAccounts: A list of Service Accounts to enable for this instance.
    tags: A list of tags to apply to the Google Compute Engine instance to
      identify resources.
    zone: The zone for this ReplicaPool.
  """

  autoRestart = messages.BooleanField(1)
  baseInstanceName = messages.StringField(2)
  canIpForward = messages.BooleanField(3)
  description = messages.StringField(4)
  disksToAttach = messages.MessageField('ExistingDisk', 5, repeated=True)
  disksToCreate = messages.MessageField('NewDisk', 6, repeated=True)
  initAction = messages.StringField(7)
  machineType = messages.StringField(8)
  metadata = messages.MessageField('Metadata', 9)
  networkInterfaces = messages.MessageField('NetworkInterface', 10, repeated=True)
  onHostMaintenance = messages.StringField(11)
  serviceAccounts = messages.MessageField('ServiceAccount', 12, repeated=True)
  tags = messages.MessageField('Tag', 13)
  zone = messages.StringField(14)


class ServiceAccount(messages.Message):
  """A Compute Engine service account, identical to the Compute Engine
  resource.

  Fields:
    email: Service account email address.
    scopes: List of OAuth2 scopes to obtain for the service account.
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
    fingerPrint: The fingerprint of the tag.
    items: Items contained in this tag.
  """

  fingerPrint = messages.StringField(1)
  items = messages.StringField(2, repeated=True)


class Template(messages.Message):
  """A Template represents a complete configuration for a Deployment.

  Messages:
    ActionsValue: Action definitions for use in Module intents in this
      Template.
    ModulesValue: A list of modules for this Template.

  Fields:
    actions: Action definitions for use in Module intents in this Template.
    description: A user-supplied description of this Template.
    modules: A list of modules for this Template.
    name: Name of this Template. The name must conform to the expression:
      [a-zA-Z0-9-_]{1,64}
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ActionsValue(messages.Message):
    """Action definitions for use in Module intents in this Template.

    Messages:
      AdditionalProperty: An additional property for a ActionsValue object.

    Fields:
      additionalProperties: The name of this action, used when specifying
        Actions in Module definitions.
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a ActionsValue object.

      Fields:
        key: Name of the additional property.
        value: A Action attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('Action', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ModulesValue(messages.Message):
    """A list of modules for this Template.

    Messages:
      AdditionalProperty: An additional property for a ModulesValue object.

    Fields:
      additionalProperties: Name of the module. The name must conform to the
        following regular expression: [a-zA-Z0-9-_]{1,64}
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a ModulesValue object.

      Fields:
        key: Name of the additional property.
        value: A Module attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('Module', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  actions = messages.MessageField('ActionsValue', 1)
  description = messages.StringField(2)
  modules = messages.MessageField('ModulesValue', 3)
  name = messages.StringField(4)


class TemplatesListResponse(messages.Message):
  """A TemplatesListResponse object.

  Fields:
    nextPageToken: A string attribute.
    resources: A Template attribute.
  """

  nextPageToken = messages.StringField(1)
  resources = messages.MessageField('Template', 2, repeated=True)


