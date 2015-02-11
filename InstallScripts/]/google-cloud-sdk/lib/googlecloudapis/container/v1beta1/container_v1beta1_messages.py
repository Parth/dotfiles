"""Generated message classes for container version v1beta1.

The Google Container Engine API is used for building and managing container
based applications, powered by the open source Kubernetes technology.
"""

from protorpc import messages


package = 'container'


class Cluster(messages.Message):
  """A Cluster object.

  Enums:
    StatusValueValuesEnum: [Output only] The current status of this cluster.

  Fields:
    clusterApiVersion: The API version of the Kubernetes master and kubelets
      running in this cluster. Leave blank to pick up the latest stable
      release, or specify a version of the form "x.y.z". The Google Container
      Engine release notes lists the currently supported versions. If an
      incorrect version is specified, the server returns an error listing the
      currently supported versions.
    containerIpv4Cidr: [Output only] The IP addresses of the container pods in
      this cluster, in  CIDR notation (e.g. 1.2.3.4/29).
    creationTimestamp: [Output only] The time the cluster was created, in
      RFC3339 text format.
    description: An optional description of this cluster.
    endpoint: [Output only] The IP address of this cluster's Kubernetes
      master. The endpoint can be accessed from the internet at
      https://username:password@endpoint/.  See the masterAuth property of
      this resource for username and password information.
    masterAuth: The HTTP basic authentication information for accessing the
      master. Because the master endpoint is open to the internet, you should
      create a strong password.
    name: The name of this cluster. The name must be unique within this
      project and zone, and can be up to 40 characters with the following
      restrictions:   - Lowercase letters, numbers, and hyphens only. - Must
      start with a letter. - Must end with a number or a letter.
    network: The name of the Google Compute Engine network to which the
      cluster is connected.
    nodeConfig: The machine type and image to use for all nodes in this
      cluster. See the descriptions of the child properties of nodeConfig.
    nodeRoutingPrefixSize: [Output only] The size of the address space on each
      node for hosting containers.
    numNodes: The number of nodes to create in this cluster. You must ensure
      that your Compute Engine resource quota is sufficient for this number of
      instances plus one (to include the master). You must also have available
      firewall and routes quota.
    selfLink: [Output only] Server-defined URL for the resource.
    servicesIpv4Cidr: [Output only] The IP addresses of the Kubernetes
      services in this cluster, in  CIDR notation (e.g. 1.2.3.4/29). Service
      addresses are always in the 10.0.0.0/16 range.
    status: [Output only] The current status of this cluster.
    statusMessage: [Output only] Additional information about the current
      status of this cluster, if available.
    zone: [Output only] The name of the Google Compute Engine zone in which
      the cluster resides.
  """

  class StatusValueValuesEnum(messages.Enum):
    """[Output only] The current status of this cluster.

    Values:
      error: <no description>
      provisioning: <no description>
      running: <no description>
      stopping: <no description>
    """
    error = 0
    provisioning = 1
    running = 2
    stopping = 3

  clusterApiVersion = messages.StringField(1)
  containerIpv4Cidr = messages.StringField(2)
  creationTimestamp = messages.StringField(3)
  description = messages.StringField(4)
  endpoint = messages.StringField(5)
  masterAuth = messages.MessageField('MasterAuth', 6)
  name = messages.StringField(7)
  network = messages.StringField(8)
  nodeConfig = messages.MessageField('NodeConfig', 9)
  nodeRoutingPrefixSize = messages.IntegerField(10, variant=messages.Variant.INT32)
  numNodes = messages.IntegerField(11, variant=messages.Variant.INT32)
  selfLink = messages.StringField(12)
  servicesIpv4Cidr = messages.StringField(13)
  status = messages.EnumField('StatusValueValuesEnum', 14)
  statusMessage = messages.StringField(15)
  zone = messages.StringField(16)


class ContainerProjectsClustersListRequest(messages.Message):
  """A ContainerProjectsClustersListRequest object.

  Fields:
    projectId: The Google Developers Console project ID or  project number.
  """

  projectId = messages.StringField(1, required=True)


class ContainerProjectsOperationsListRequest(messages.Message):
  """A ContainerProjectsOperationsListRequest object.

  Fields:
    projectId: The Google Developers Console project ID or  project number.
  """

  projectId = messages.StringField(1, required=True)


class ContainerProjectsZonesClustersCreateRequest(messages.Message):
  """A ContainerProjectsZonesClustersCreateRequest object.

  Fields:
    createClusterRequest: A CreateClusterRequest resource to be passed as the
      request body.
    projectId: The Google Developers Console project ID or  project number.
    zoneId: The name of the Google Compute Engine zone in which the cluster
      resides.
  """

  createClusterRequest = messages.MessageField('CreateClusterRequest', 1)
  projectId = messages.StringField(2, required=True)
  zoneId = messages.StringField(3, required=True)


class ContainerProjectsZonesClustersDeleteRequest(messages.Message):
  """A ContainerProjectsZonesClustersDeleteRequest object.

  Fields:
    clusterId: The name of the cluster to delete.
    projectId: The Google Developers Console project ID or  project number.
    zoneId: The name of the Google Compute Engine zone in which the cluster
      resides.
  """

  clusterId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)
  zoneId = messages.StringField(3, required=True)


class ContainerProjectsZonesClustersGetRequest(messages.Message):
  """A ContainerProjectsZonesClustersGetRequest object.

  Fields:
    clusterId: The name of the cluster to retrieve.
    projectId: The Google Developers Console project ID or  project number.
    zoneId: The name of the Google Compute Engine zone in which the cluster
      resides.
  """

  clusterId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)
  zoneId = messages.StringField(3, required=True)


class ContainerProjectsZonesClustersListRequest(messages.Message):
  """A ContainerProjectsZonesClustersListRequest object.

  Fields:
    projectId: The Google Developers Console project ID or  project number.
    zoneId: The name of the Google Compute Engine zone in which the cluster
      resides.
  """

  projectId = messages.StringField(1, required=True)
  zoneId = messages.StringField(2, required=True)


class ContainerProjectsZonesOperationsGetRequest(messages.Message):
  """A ContainerProjectsZonesOperationsGetRequest object.

  Fields:
    operationId: The server-assigned name of the operation.
    projectId: The Google Developers Console project ID or  project number.
    zoneId: The name of the Google Compute Engine zone in which the operation
      resides. This is always the same zone as the cluster with which the
      operation is associated.
  """

  operationId = messages.StringField(1, required=True)
  projectId = messages.StringField(2, required=True)
  zoneId = messages.StringField(3, required=True)


class ContainerProjectsZonesOperationsListRequest(messages.Message):
  """A ContainerProjectsZonesOperationsListRequest object.

  Fields:
    projectId: The Google Developers Console project ID or  project number.
    zoneId: The name of the Google Compute Engine zone to return operations
      for.
  """

  projectId = messages.StringField(1, required=True)
  zoneId = messages.StringField(2, required=True)


class CreateClusterRequest(messages.Message):
  """A CreateClusterRequest object.

  Fields:
    cluster: A cluster resource.
  """

  cluster = messages.MessageField('Cluster', 1)


class ListAggregatedClustersResponse(messages.Message):
  """A ListAggregatedClustersResponse object.

  Fields:
    clusters: A list of clusters in the project, across all zones.
  """

  clusters = messages.MessageField('Cluster', 1, repeated=True)


class ListAggregatedOperationsResponse(messages.Message):
  """A ListAggregatedOperationsResponse object.

  Fields:
    operations: A list of operations in the project, across all zones.
  """

  operations = messages.MessageField('Operation', 1, repeated=True)


class ListClustersResponse(messages.Message):
  """A ListClustersResponse object.

  Fields:
    clusters: A list of clusters in the project in the specified zone.
  """

  clusters = messages.MessageField('Cluster', 1, repeated=True)


class ListOperationsResponse(messages.Message):
  """A ListOperationsResponse object.

  Fields:
    operations: A list of operations in the project in the specified zone.
  """

  operations = messages.MessageField('Operation', 1, repeated=True)


class MasterAuth(messages.Message):
  """A MasterAuth object.

  Fields:
    password: The password to use when accessing the Kubernetes master
      endpoint.
    user: The username to use when accessing the Kubernetes master endpoint.
  """

  password = messages.StringField(1)
  user = messages.StringField(2)


class NodeConfig(messages.Message):
  """A NodeConfig object.

  Fields:
    machineType: The name of a Google Compute Engine machine type (e.g.
      n1-standard-1).  If unspecified, the default machine type is
      n1-standard-1.
    serviceAccounts: The optional list of ServiceAccounts, each with their
      specified scopes, to be made available on all of the node VMs. In
      addition to the service accounts and scopes specified, the "default"
      account will always be created with the following scopes to ensure the
      correct functioning of the cluster:   -
      https://www.googleapis.com/auth/compute, -
      https://www.googleapis.com/auth/devstorage.read_only
    sourceImage: The fully-specified name of a Google Compute Engine image.
      For example: https://www.googleapis.com/compute/v1/projects/debian-
      cloud/global/images/backports-debian-7-wheezy-vYYYYMMDD (where YYYMMDD
      is the version date).  If specifying an image, you are responsible for
      ensuring its compatibility with the Debian 7 backports image. We
      recommend leaving this field blank to accept the default backports-
      debian-7-wheezy value.
  """

  machineType = messages.StringField(1)
  serviceAccounts = messages.MessageField('ServiceAccount', 2, repeated=True)
  sourceImage = messages.StringField(3)


class Operation(messages.Message):
  """Defines the operation resource. All fields are output only.

  Enums:
    OperationTypeValueValuesEnum: The operation type.
    StatusValueValuesEnum: The current status of the operation.

  Fields:
    errorMessage: If an error has occurred, a textual description of the
      error.
    name: The server-assigned ID for this operation. If the operation is
      fulfilled upfront, it may not have a resource name.
    operationType: The operation type.
    selfLink: Server-defined URL for the resource.
    status: The current status of the operation.
    target: [Optional] The URL of the cluster resource that this operation is
      associated with.
    targetLink: Server-defined URL for the target of the operation.
    zone: The name of the Google Compute Engine zone in which the operation is
      taking place.
  """

  class OperationTypeValueValuesEnum(messages.Enum):
    """The operation type.

    Values:
      createCluster: <no description>
      deleteCluster: <no description>
    """
    createCluster = 0
    deleteCluster = 1

  class StatusValueValuesEnum(messages.Enum):
    """The current status of the operation.

    Values:
      done: <no description>
      pending: <no description>
      running: <no description>
    """
    done = 0
    pending = 1
    running = 2

  errorMessage = messages.StringField(1)
  name = messages.StringField(2)
  operationType = messages.EnumField('OperationTypeValueValuesEnum', 3)
  selfLink = messages.StringField(4)
  status = messages.EnumField('StatusValueValuesEnum', 5)
  target = messages.StringField(6)
  targetLink = messages.StringField(7)
  zone = messages.StringField(8)


class ServiceAccount(messages.Message):
  """A Compute Engine service account.

  Fields:
    email: Email address of the service account.
    scopes: The list of scopes to be made available for this service account.
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


