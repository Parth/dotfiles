"""Generated message classes for compute version v1.

API for the Google Compute Engine service.
"""

from protorpc import messages

from googlecloudapis.apitools.base.py import encoding


package = 'compute'


class AccessConfig(messages.Message):
  """An access configuration attached to an instance's network interface.

  Enums:
    TypeValueValuesEnum: Type of configuration. Must be set to
      "ONE_TO_ONE_NAT". This configures port-for-port NAT to the internet.

  Fields:
    kind: Type of the resource.
    name: Name of this access configuration.
    natIP: An external IP address associated with this instance. Specify an
      unused static IP address available to the project. If not specified, the
      external IP will be drawn from a shared ephemeral pool.
    type: Type of configuration. Must be set to "ONE_TO_ONE_NAT". This
      configures port-for-port NAT to the internet.
  """

  class TypeValueValuesEnum(messages.Enum):
    """Type of configuration. Must be set to "ONE_TO_ONE_NAT". This configures
    port-for-port NAT to the internet.

    Values:
      ONE_TO_ONE_NAT: <no description>
    """
    ONE_TO_ONE_NAT = 0

  kind = messages.StringField(1, default=u'compute#accessConfig')
  name = messages.StringField(2)
  natIP = messages.StringField(3)
  type = messages.EnumField('TypeValueValuesEnum', 4, default=u'ONE_TO_ONE_NAT')


class Address(messages.Message):
  """A reserved address resource.

  Enums:
    StatusValueValuesEnum: The status of the address (output only).

  Fields:
    address: The IP address represented by this resource.
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    region: URL of the region where the regional address resides (output
      only). This field is not applicable to global addresses.
    selfLink: Server defined URL for the resource (output only).
    status: The status of the address (output only).
    users: The resources that are using this address resource.
  """

  class StatusValueValuesEnum(messages.Enum):
    """The status of the address (output only).

    Values:
      IN_USE: <no description>
      RESERVED: <no description>
    """
    IN_USE = 0
    RESERVED = 1

  address = messages.StringField(1)
  creationTimestamp = messages.StringField(2)
  description = messages.StringField(3)
  id = messages.IntegerField(4, variant=messages.Variant.UINT64)
  kind = messages.StringField(5, default=u'compute#address')
  name = messages.StringField(6)
  region = messages.StringField(7)
  selfLink = messages.StringField(8)
  status = messages.EnumField('StatusValueValuesEnum', 9)
  users = messages.StringField(10, repeated=True)


class AddressAggregatedList(messages.Message):
  """A AddressAggregatedList object.

  Messages:
    ItemsValue: A map of scoped address lists.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A map of scoped address lists.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ItemsValue(messages.Message):
    """A map of scoped address lists.

    Messages:
      AdditionalProperty: An additional property for a ItemsValue object.

    Fields:
      additionalProperties: Name of the scope containing this set of
        addresses.
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a ItemsValue object.

      Fields:
        key: Name of the additional property.
        value: A AddressesScopedList attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('AddressesScopedList', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  id = messages.StringField(1)
  items = messages.MessageField('ItemsValue', 2)
  kind = messages.StringField(3, default=u'compute#addressAggregatedList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class AddressList(messages.Message):
  """Contains a list of address resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of Address resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for the resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('Address', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#addressList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class AddressesScopedList(messages.Message):
  """A AddressesScopedList object.

  Messages:
    WarningValue: Informational warning which replaces the list of addresses
      when the list is empty.

  Fields:
    addresses: List of addresses contained in this scope.
    warning: Informational warning which replaces the list of addresses when
      the list is empty.
  """

  class WarningValue(messages.Message):
    """Informational warning which replaces the list of addresses when the
    list is empty.

    Enums:
      CodeValueValuesEnum: The warning type identifier for this warning.

    Messages:
      DataValueListEntry: A DataValueListEntry object.

    Fields:
      code: The warning type identifier for this warning.
      data: Metadata for this warning in 'key: value' format.
      message: Optional human-readable details for this warning.
    """

    class CodeValueValuesEnum(messages.Enum):
      """The warning type identifier for this warning.

      Values:
        DEPRECATED_RESOURCE_USED: <no description>
        DISK_SIZE_LARGER_THAN_IMAGE_SIZE: <no description>
        INJECTED_KERNELS_DEPRECATED: <no description>
        NEXT_HOP_ADDRESS_NOT_ASSIGNED: <no description>
        NEXT_HOP_CANNOT_IP_FORWARD: <no description>
        NEXT_HOP_INSTANCE_NOT_FOUND: <no description>
        NEXT_HOP_INSTANCE_NOT_ON_NETWORK: <no description>
        NEXT_HOP_NOT_RUNNING: <no description>
        NO_RESULTS_ON_PAGE: <no description>
        REQUIRED_TOS_AGREEMENT: <no description>
        RESOURCE_NOT_DELETED: <no description>
        UNREACHABLE: <no description>
      """
      DEPRECATED_RESOURCE_USED = 0
      DISK_SIZE_LARGER_THAN_IMAGE_SIZE = 1
      INJECTED_KERNELS_DEPRECATED = 2
      NEXT_HOP_ADDRESS_NOT_ASSIGNED = 3
      NEXT_HOP_CANNOT_IP_FORWARD = 4
      NEXT_HOP_INSTANCE_NOT_FOUND = 5
      NEXT_HOP_INSTANCE_NOT_ON_NETWORK = 6
      NEXT_HOP_NOT_RUNNING = 7
      NO_RESULTS_ON_PAGE = 8
      REQUIRED_TOS_AGREEMENT = 9
      RESOURCE_NOT_DELETED = 10
      UNREACHABLE = 11

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: A key for the warning data.
        value: A warning data value corresponding to the key.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.EnumField('CodeValueValuesEnum', 1)
    data = messages.MessageField('DataValueListEntry', 2, repeated=True)
    message = messages.StringField(3)

  addresses = messages.MessageField('Address', 1, repeated=True)
  warning = messages.MessageField('WarningValue', 2)


class AttachedDisk(messages.Message):
  """An instance-attached disk resource.

  Enums:
    InterfaceValueValuesEnum:
    ModeValueValuesEnum: The mode in which to attach this disk, either
      "READ_WRITE" or "READ_ONLY".
    TypeValueValuesEnum: Type of the disk, either "SCRATCH" or "PERSISTENT".
      Note that persistent disks must be created before you can specify them
      here.

  Fields:
    autoDelete: Whether the disk will be auto-deleted when the instance is
      deleted (but not when the disk is detached from the instance).
    boot: Indicates that this is a boot disk. VM will use the first partition
      of the disk for its root filesystem.
    deviceName: Persistent disk only; must be unique within the instance when
      specified. This represents a unique device name that is reflected into
      the /dev/ tree of a Linux operating system running within the instance.
      If not specified, a default will be chosen by the system.
    index: A zero-based index to assign to this disk, where 0 is reserved for
      the boot disk. If not specified, the server will choose an appropriate
      value (output only).
    initializeParams: Initialization parameters.
    interface: A InterfaceValueValuesEnum attribute.
    kind: Type of the resource.
    licenses: Public visible licenses.
    mode: The mode in which to attach this disk, either "READ_WRITE" or
      "READ_ONLY".
    source: Persistent disk only; the URL of the persistent disk resource.
    type: Type of the disk, either "SCRATCH" or "PERSISTENT". Note that
      persistent disks must be created before you can specify them here.
  """

  class InterfaceValueValuesEnum(messages.Enum):
    """InterfaceValueValuesEnum enum type.

    Values:
      NVME: <no description>
      SCSI: <no description>
    """
    NVME = 0
    SCSI = 1

  class ModeValueValuesEnum(messages.Enum):
    """The mode in which to attach this disk, either "READ_WRITE" or
    "READ_ONLY".

    Values:
      READ_ONLY: <no description>
      READ_WRITE: <no description>
    """
    READ_ONLY = 0
    READ_WRITE = 1

  class TypeValueValuesEnum(messages.Enum):
    """Type of the disk, either "SCRATCH" or "PERSISTENT". Note that
    persistent disks must be created before you can specify them here.

    Values:
      PERSISTENT: <no description>
      SCRATCH: <no description>
    """
    PERSISTENT = 0
    SCRATCH = 1

  autoDelete = messages.BooleanField(1)
  boot = messages.BooleanField(2)
  deviceName = messages.StringField(3)
  index = messages.IntegerField(4, variant=messages.Variant.INT32)
  initializeParams = messages.MessageField('AttachedDiskInitializeParams', 5)
  interface = messages.EnumField('InterfaceValueValuesEnum', 6)
  kind = messages.StringField(7, default=u'compute#attachedDisk')
  licenses = messages.StringField(8, repeated=True)
  mode = messages.EnumField('ModeValueValuesEnum', 9)
  source = messages.StringField(10)
  type = messages.EnumField('TypeValueValuesEnum', 11)


class AttachedDiskInitializeParams(messages.Message):
  """Initialization parameters for the new disk (input-only). Can only be
  specified on the boot disk or local SSDs. Mutually exclusive with 'source'.

  Fields:
    diskName: Name of the disk (when not provided defaults to the name of the
      instance).
    diskSizeGb: Size of the disk in base-2 GB.
    diskType: URL of the disk type resource describing which disk type to use
      to create the disk; provided by the client when the disk is created.
    sourceImage: The source image used to create this disk.
  """

  diskName = messages.StringField(1)
  diskSizeGb = messages.IntegerField(2)
  diskType = messages.StringField(3)
  sourceImage = messages.StringField(4)


class Backend(messages.Message):
  """Message containing information of one individual backend.

  Enums:
    BalancingModeValueValuesEnum: The balancing mode of this backend, default
      is UTILIZATION.

  Fields:
    balancingMode: The balancing mode of this backend, default is UTILIZATION.
    capacityScaler: The multiplier (a value between 0 and 1e6) of the max
      capacity (CPU or RPS, depending on 'balancingMode') the group should
      serve up to. 0 means the group is totally drained. Default value is 1.
      Valid range is [0, 1e6].
    description: An optional textual description of the resource, which is
      provided by the client when the resource is created.
    group: URL of a zonal Cloud Resource View resource. This resource view
      defines the list of instances that serve traffic. Member virtual machine
      instances from each resource view must live in the same zone as the
      resource view itself. No two backends in a backend service are allowed
      to use same Resource View resource.
    maxRate: The max RPS of the group. Can be used with either balancing mode,
      but required if RATE mode. For RATE mode, either maxRate or
      maxRatePerInstance must be set.
    maxRatePerInstance: The max RPS that a single backed instance can handle.
      This is used to calculate the capacity of the group. Can be used in
      either balancing mode. For RATE mode, either maxRate or
      maxRatePerInstance must be set.
    maxUtilization: Used when 'balancingMode' is UTILIZATION. This ratio
      defines the CPU utilization target for the group. The default is 0.8.
      Valid range is [0, 1].
  """

  class BalancingModeValueValuesEnum(messages.Enum):
    """The balancing mode of this backend, default is UTILIZATION.

    Values:
      RATE: <no description>
      UTILIZATION: <no description>
    """
    RATE = 0
    UTILIZATION = 1

  balancingMode = messages.EnumField('BalancingModeValueValuesEnum', 1)
  capacityScaler = messages.FloatField(2, variant=messages.Variant.FLOAT)
  description = messages.StringField(3)
  group = messages.StringField(4)
  maxRate = messages.IntegerField(5, variant=messages.Variant.INT32)
  maxRatePerInstance = messages.FloatField(6, variant=messages.Variant.FLOAT)
  maxUtilization = messages.FloatField(7, variant=messages.Variant.FLOAT)


class BackendService(messages.Message):
  """A BackendService resource. This resource defines a group of backend VMs
  together with their serving capacity.

  Enums:
    ProtocolValueValuesEnum:

  Fields:
    backends: The list of backends that serve this BackendService.
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    fingerprint: Fingerprint of this resource. A hash of the contents stored
      in this object. This field is used in optimistic locking. This field
      will be ignored when inserting a BackendService. An up-to-date
      fingerprint must be provided in order to update the BackendService.
    healthChecks: The list of URLs to the HttpHealthCheck resource for health
      checking this BackendService. Currently at most one health check can be
      specified, and a health check is required.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    port: Deprecated in favor of port_name. The TCP port to connect on the
      backend. The default value is 80.
    portName: Name of backend port. The same name should appear in the
      resource views referenced by this service. Required.
    protocol: A ProtocolValueValuesEnum attribute.
    selfLink: Server defined URL for the resource (output only).
    timeoutSec: How many seconds to wait for the backend before considering it
      a failed request. Default is 30 seconds.
  """

  class ProtocolValueValuesEnum(messages.Enum):
    """ProtocolValueValuesEnum enum type.

    Values:
      HTTP: <no description>
    """
    HTTP = 0

  backends = messages.MessageField('Backend', 1, repeated=True)
  creationTimestamp = messages.StringField(2)
  description = messages.StringField(3)
  fingerprint = messages.BytesField(4)
  healthChecks = messages.StringField(5, repeated=True)
  id = messages.IntegerField(6, variant=messages.Variant.UINT64)
  kind = messages.StringField(7, default=u'compute#backendService')
  name = messages.StringField(8)
  port = messages.IntegerField(9, variant=messages.Variant.INT32)
  portName = messages.StringField(10)
  protocol = messages.EnumField('ProtocolValueValuesEnum', 11)
  selfLink = messages.StringField(12)
  timeoutSec = messages.IntegerField(13, variant=messages.Variant.INT32)


class BackendServiceGroupHealth(messages.Message):
  """A BackendServiceGroupHealth object.

  Fields:
    healthStatus: A HealthStatus attribute.
    kind: Type of resource.
  """

  healthStatus = messages.MessageField('HealthStatus', 1, repeated=True)
  kind = messages.StringField(2, default=u'compute#backendServiceGroupHealth')


class BackendServiceList(messages.Message):
  """Contains a list of BackendService resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of BackendService resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('BackendService', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#backendServiceList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class ComputeAddressesAggregatedListRequest(messages.Message):
  """A ComputeAddressesAggregatedListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeAddressesDeleteRequest(messages.Message):
  """A ComputeAddressesDeleteRequest object.

  Fields:
    address: Name of the address resource to delete.
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
  """

  address = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)


class ComputeAddressesGetRequest(messages.Message):
  """A ComputeAddressesGetRequest object.

  Fields:
    address: Name of the address resource to return.
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
  """

  address = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)


class ComputeAddressesInsertRequest(messages.Message):
  """A ComputeAddressesInsertRequest object.

  Fields:
    address: A Address resource to be passed as the request body.
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
  """

  address = messages.MessageField('Address', 1)
  project = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)


class ComputeAddressesListRequest(messages.Message):
  """A ComputeAddressesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  region = messages.StringField(5, required=True)


class ComputeBackendServicesDeleteRequest(messages.Message):
  """A ComputeBackendServicesDeleteRequest object.

  Fields:
    backendService: Name of the BackendService resource to delete.
    project: Name of the project scoping this request.
  """

  backendService = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeBackendServicesGetHealthRequest(messages.Message):
  """A ComputeBackendServicesGetHealthRequest object.

  Fields:
    backendService: Name of the BackendService resource to which the queried
      instance belongs.
    project: A string attribute.
    resourceGroupReference: A ResourceGroupReference resource to be passed as
      the request body.
  """

  backendService = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  resourceGroupReference = messages.MessageField('ResourceGroupReference', 3)


class ComputeBackendServicesGetRequest(messages.Message):
  """A ComputeBackendServicesGetRequest object.

  Fields:
    backendService: Name of the BackendService resource to return.
    project: Name of the project scoping this request.
  """

  backendService = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeBackendServicesInsertRequest(messages.Message):
  """A ComputeBackendServicesInsertRequest object.

  Fields:
    backendService: A BackendService resource to be passed as the request
      body.
    project: Name of the project scoping this request.
  """

  backendService = messages.MessageField('BackendService', 1)
  project = messages.StringField(2, required=True)


class ComputeBackendServicesListRequest(messages.Message):
  """A ComputeBackendServicesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeBackendServicesPatchRequest(messages.Message):
  """A ComputeBackendServicesPatchRequest object.

  Fields:
    backendService: Name of the BackendService resource to update.
    backendServiceResource: A BackendService resource to be passed as the
      request body.
    project: Name of the project scoping this request.
  """

  backendService = messages.StringField(1, required=True)
  backendServiceResource = messages.MessageField('BackendService', 2)
  project = messages.StringField(3, required=True)


class ComputeBackendServicesUpdateRequest(messages.Message):
  """A ComputeBackendServicesUpdateRequest object.

  Fields:
    backendService: Name of the BackendService resource to update.
    backendServiceResource: A BackendService resource to be passed as the
      request body.
    project: Name of the project scoping this request.
  """

  backendService = messages.StringField(1, required=True)
  backendServiceResource = messages.MessageField('BackendService', 2)
  project = messages.StringField(3, required=True)


class ComputeDiskTypesAggregatedListRequest(messages.Message):
  """A ComputeDiskTypesAggregatedListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeDiskTypesGetRequest(messages.Message):
  """A ComputeDiskTypesGetRequest object.

  Fields:
    diskType: Name of the disk type resource to return.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  diskType = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeDiskTypesListRequest(messages.Message):
  """A ComputeDiskTypesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  zone = messages.StringField(5, required=True)


class ComputeDisksAggregatedListRequest(messages.Message):
  """A ComputeDisksAggregatedListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeDisksCreateSnapshotRequest(messages.Message):
  """A ComputeDisksCreateSnapshotRequest object.

  Fields:
    disk: Name of the persistent disk resource to snapshot.
    project: Name of the project scoping this request.
    snapshot: A Snapshot resource to be passed as the request body.
    zone: Name of the zone scoping this request.
  """

  disk = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  snapshot = messages.MessageField('Snapshot', 3)
  zone = messages.StringField(4, required=True)


class ComputeDisksDeleteRequest(messages.Message):
  """A ComputeDisksDeleteRequest object.

  Fields:
    disk: Name of the persistent disk resource to delete.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  disk = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeDisksGetRequest(messages.Message):
  """A ComputeDisksGetRequest object.

  Fields:
    disk: Name of the persistent disk resource to return.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  disk = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeDisksInsertRequest(messages.Message):
  """A ComputeDisksInsertRequest object.

  Fields:
    disk: A Disk resource to be passed as the request body.
    project: Name of the project scoping this request.
    sourceImage: Optional. Source image to restore onto a disk.
    zone: Name of the zone scoping this request.
  """

  disk = messages.MessageField('Disk', 1)
  project = messages.StringField(2, required=True)
  sourceImage = messages.StringField(3)
  zone = messages.StringField(4, required=True)


class ComputeDisksListRequest(messages.Message):
  """A ComputeDisksListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  zone = messages.StringField(5, required=True)


class ComputeFirewallsDeleteRequest(messages.Message):
  """A ComputeFirewallsDeleteRequest object.

  Fields:
    firewall: Name of the firewall resource to delete.
    project: Name of the project scoping this request.
  """

  firewall = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeFirewallsGetRequest(messages.Message):
  """A ComputeFirewallsGetRequest object.

  Fields:
    firewall: Name of the firewall resource to return.
    project: Name of the project scoping this request.
  """

  firewall = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeFirewallsInsertRequest(messages.Message):
  """A ComputeFirewallsInsertRequest object.

  Fields:
    firewall: A Firewall resource to be passed as the request body.
    project: Name of the project scoping this request.
  """

  firewall = messages.MessageField('Firewall', 1)
  project = messages.StringField(2, required=True)


class ComputeFirewallsListRequest(messages.Message):
  """A ComputeFirewallsListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeFirewallsPatchRequest(messages.Message):
  """A ComputeFirewallsPatchRequest object.

  Fields:
    firewall: Name of the firewall resource to update.
    firewallResource: A Firewall resource to be passed as the request body.
    project: Name of the project scoping this request.
  """

  firewall = messages.StringField(1, required=True)
  firewallResource = messages.MessageField('Firewall', 2)
  project = messages.StringField(3, required=True)


class ComputeFirewallsUpdateRequest(messages.Message):
  """A ComputeFirewallsUpdateRequest object.

  Fields:
    firewall: Name of the firewall resource to update.
    firewallResource: A Firewall resource to be passed as the request body.
    project: Name of the project scoping this request.
  """

  firewall = messages.StringField(1, required=True)
  firewallResource = messages.MessageField('Firewall', 2)
  project = messages.StringField(3, required=True)


class ComputeForwardingRulesAggregatedListRequest(messages.Message):
  """A ComputeForwardingRulesAggregatedListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeForwardingRulesDeleteRequest(messages.Message):
  """A ComputeForwardingRulesDeleteRequest object.

  Fields:
    forwardingRule: Name of the ForwardingRule resource to delete.
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
  """

  forwardingRule = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)


class ComputeForwardingRulesGetRequest(messages.Message):
  """A ComputeForwardingRulesGetRequest object.

  Fields:
    forwardingRule: Name of the ForwardingRule resource to return.
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
  """

  forwardingRule = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)


class ComputeForwardingRulesInsertRequest(messages.Message):
  """A ComputeForwardingRulesInsertRequest object.

  Fields:
    forwardingRule: A ForwardingRule resource to be passed as the request
      body.
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
  """

  forwardingRule = messages.MessageField('ForwardingRule', 1)
  project = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)


class ComputeForwardingRulesListRequest(messages.Message):
  """A ComputeForwardingRulesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  region = messages.StringField(5, required=True)


class ComputeForwardingRulesSetTargetRequest(messages.Message):
  """A ComputeForwardingRulesSetTargetRequest object.

  Fields:
    forwardingRule: Name of the ForwardingRule resource in which target is to
      be set.
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
    targetReference: A TargetReference resource to be passed as the request
      body.
  """

  forwardingRule = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)
  targetReference = messages.MessageField('TargetReference', 4)


class ComputeGlobalAddressesDeleteRequest(messages.Message):
  """A ComputeGlobalAddressesDeleteRequest object.

  Fields:
    address: Name of the address resource to delete.
    project: Name of the project scoping this request.
  """

  address = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeGlobalAddressesGetRequest(messages.Message):
  """A ComputeGlobalAddressesGetRequest object.

  Fields:
    address: Name of the address resource to return.
    project: Name of the project scoping this request.
  """

  address = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeGlobalAddressesInsertRequest(messages.Message):
  """A ComputeGlobalAddressesInsertRequest object.

  Fields:
    address: A Address resource to be passed as the request body.
    project: Name of the project scoping this request.
  """

  address = messages.MessageField('Address', 1)
  project = messages.StringField(2, required=True)


class ComputeGlobalAddressesListRequest(messages.Message):
  """A ComputeGlobalAddressesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeGlobalForwardingRulesDeleteRequest(messages.Message):
  """A ComputeGlobalForwardingRulesDeleteRequest object.

  Fields:
    forwardingRule: Name of the ForwardingRule resource to delete.
    project: Name of the project scoping this request.
  """

  forwardingRule = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeGlobalForwardingRulesGetRequest(messages.Message):
  """A ComputeGlobalForwardingRulesGetRequest object.

  Fields:
    forwardingRule: Name of the ForwardingRule resource to return.
    project: Name of the project scoping this request.
  """

  forwardingRule = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeGlobalForwardingRulesInsertRequest(messages.Message):
  """A ComputeGlobalForwardingRulesInsertRequest object.

  Fields:
    forwardingRule: A ForwardingRule resource to be passed as the request
      body.
    project: Name of the project scoping this request.
  """

  forwardingRule = messages.MessageField('ForwardingRule', 1)
  project = messages.StringField(2, required=True)


class ComputeGlobalForwardingRulesListRequest(messages.Message):
  """A ComputeGlobalForwardingRulesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeGlobalForwardingRulesSetTargetRequest(messages.Message):
  """A ComputeGlobalForwardingRulesSetTargetRequest object.

  Fields:
    forwardingRule: Name of the ForwardingRule resource in which target is to
      be set.
    project: Name of the project scoping this request.
    targetReference: A TargetReference resource to be passed as the request
      body.
  """

  forwardingRule = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  targetReference = messages.MessageField('TargetReference', 3)


class ComputeGlobalOperationsAggregatedListRequest(messages.Message):
  """A ComputeGlobalOperationsAggregatedListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeGlobalOperationsDeleteRequest(messages.Message):
  """A ComputeGlobalOperationsDeleteRequest object.

  Fields:
    operation: Name of the operation resource to delete.
    project: Name of the project scoping this request.
  """

  operation = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeGlobalOperationsDeleteResponse(messages.Message):
  """An empty ComputeGlobalOperationsDelete response."""


class ComputeGlobalOperationsGetRequest(messages.Message):
  """A ComputeGlobalOperationsGetRequest object.

  Fields:
    operation: Name of the operation resource to return.
    project: Name of the project scoping this request.
  """

  operation = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeGlobalOperationsListRequest(messages.Message):
  """A ComputeGlobalOperationsListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeHttpHealthChecksDeleteRequest(messages.Message):
  """A ComputeHttpHealthChecksDeleteRequest object.

  Fields:
    httpHealthCheck: Name of the HttpHealthCheck resource to delete.
    project: Name of the project scoping this request.
  """

  httpHealthCheck = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeHttpHealthChecksGetRequest(messages.Message):
  """A ComputeHttpHealthChecksGetRequest object.

  Fields:
    httpHealthCheck: Name of the HttpHealthCheck resource to return.
    project: Name of the project scoping this request.
  """

  httpHealthCheck = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeHttpHealthChecksInsertRequest(messages.Message):
  """A ComputeHttpHealthChecksInsertRequest object.

  Fields:
    httpHealthCheck: A HttpHealthCheck resource to be passed as the request
      body.
    project: Name of the project scoping this request.
  """

  httpHealthCheck = messages.MessageField('HttpHealthCheck', 1)
  project = messages.StringField(2, required=True)


class ComputeHttpHealthChecksListRequest(messages.Message):
  """A ComputeHttpHealthChecksListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeHttpHealthChecksPatchRequest(messages.Message):
  """A ComputeHttpHealthChecksPatchRequest object.

  Fields:
    httpHealthCheck: Name of the HttpHealthCheck resource to update.
    httpHealthCheckResource: A HttpHealthCheck resource to be passed as the
      request body.
    project: Name of the project scoping this request.
  """

  httpHealthCheck = messages.StringField(1, required=True)
  httpHealthCheckResource = messages.MessageField('HttpHealthCheck', 2)
  project = messages.StringField(3, required=True)


class ComputeHttpHealthChecksUpdateRequest(messages.Message):
  """A ComputeHttpHealthChecksUpdateRequest object.

  Fields:
    httpHealthCheck: Name of the HttpHealthCheck resource to update.
    httpHealthCheckResource: A HttpHealthCheck resource to be passed as the
      request body.
    project: Name of the project scoping this request.
  """

  httpHealthCheck = messages.StringField(1, required=True)
  httpHealthCheckResource = messages.MessageField('HttpHealthCheck', 2)
  project = messages.StringField(3, required=True)


class ComputeImagesDeleteRequest(messages.Message):
  """A ComputeImagesDeleteRequest object.

  Fields:
    image: Name of the image resource to delete.
    project: Name of the project scoping this request.
  """

  image = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeImagesDeprecateRequest(messages.Message):
  """A ComputeImagesDeprecateRequest object.

  Fields:
    deprecationStatus: A DeprecationStatus resource to be passed as the
      request body.
    image: Image name.
    project: Name of the project scoping this request.
  """

  deprecationStatus = messages.MessageField('DeprecationStatus', 1)
  image = messages.StringField(2, required=True)
  project = messages.StringField(3, required=True)


class ComputeImagesGetRequest(messages.Message):
  """A ComputeImagesGetRequest object.

  Fields:
    image: Name of the image resource to return.
    project: Name of the project scoping this request.
  """

  image = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeImagesInsertRequest(messages.Message):
  """A ComputeImagesInsertRequest object.

  Fields:
    image: A Image resource to be passed as the request body.
    project: Name of the project scoping this request.
  """

  image = messages.MessageField('Image', 1)
  project = messages.StringField(2, required=True)


class ComputeImagesListRequest(messages.Message):
  """A ComputeImagesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeInstanceTemplatesDeleteRequest(messages.Message):
  """A ComputeInstanceTemplatesDeleteRequest object.

  Fields:
    instanceTemplate: Name of the instance template resource to delete.
    project: Name of the project scoping this request.
  """

  instanceTemplate = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeInstanceTemplatesGetRequest(messages.Message):
  """A ComputeInstanceTemplatesGetRequest object.

  Fields:
    instanceTemplate: Name of the instance template resource to return.
    project: Name of the project scoping this request.
  """

  instanceTemplate = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeInstanceTemplatesInsertRequest(messages.Message):
  """A ComputeInstanceTemplatesInsertRequest object.

  Fields:
    instanceTemplate: A InstanceTemplate resource to be passed as the request
      body.
    project: Name of the project scoping this request.
  """

  instanceTemplate = messages.MessageField('InstanceTemplate', 1)
  project = messages.StringField(2, required=True)


class ComputeInstanceTemplatesListRequest(messages.Message):
  """A ComputeInstanceTemplatesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeInstancesAddAccessConfigRequest(messages.Message):
  """A ComputeInstancesAddAccessConfigRequest object.

  Fields:
    accessConfig: A AccessConfig resource to be passed as the request body.
    instance: Instance name.
    networkInterface: Network interface name.
    project: Project name.
    zone: Name of the zone scoping this request.
  """

  accessConfig = messages.MessageField('AccessConfig', 1)
  instance = messages.StringField(2, required=True)
  networkInterface = messages.StringField(3, required=True)
  project = messages.StringField(4, required=True)
  zone = messages.StringField(5, required=True)


class ComputeInstancesAggregatedListRequest(messages.Message):
  """A ComputeInstancesAggregatedListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeInstancesAttachDiskRequest(messages.Message):
  """A ComputeInstancesAttachDiskRequest object.

  Fields:
    attachedDisk: A AttachedDisk resource to be passed as the request body.
    instance: Instance name.
    project: Project name.
    zone: Name of the zone scoping this request.
  """

  attachedDisk = messages.MessageField('AttachedDisk', 1)
  instance = messages.StringField(2, required=True)
  project = messages.StringField(3, required=True)
  zone = messages.StringField(4, required=True)


class ComputeInstancesDeleteAccessConfigRequest(messages.Message):
  """A ComputeInstancesDeleteAccessConfigRequest object.

  Fields:
    accessConfig: Access config name.
    instance: Instance name.
    networkInterface: Network interface name.
    project: Project name.
    zone: Name of the zone scoping this request.
  """

  accessConfig = messages.StringField(1, required=True)
  instance = messages.StringField(2, required=True)
  networkInterface = messages.StringField(3, required=True)
  project = messages.StringField(4, required=True)
  zone = messages.StringField(5, required=True)


class ComputeInstancesDeleteRequest(messages.Message):
  """A ComputeInstancesDeleteRequest object.

  Fields:
    instance: Name of the instance resource to delete.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeInstancesDetachDiskRequest(messages.Message):
  """A ComputeInstancesDetachDiskRequest object.

  Fields:
    deviceName: Disk device name to detach.
    instance: Instance name.
    project: Project name.
    zone: Name of the zone scoping this request.
  """

  deviceName = messages.StringField(1, required=True)
  instance = messages.StringField(2, required=True)
  project = messages.StringField(3, required=True)
  zone = messages.StringField(4, required=True)


class ComputeInstancesGetRequest(messages.Message):
  """A ComputeInstancesGetRequest object.

  Fields:
    instance: Name of the instance resource to return.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeInstancesGetSerialPortOutputRequest(messages.Message):
  """A ComputeInstancesGetSerialPortOutputRequest object.

  Fields:
    instance: Name of the instance scoping this request.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeInstancesInsertRequest(messages.Message):
  """A ComputeInstancesInsertRequest object.

  Fields:
    instance: A Instance resource to be passed as the request body.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  instance = messages.MessageField('Instance', 1)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeInstancesListRequest(messages.Message):
  """A ComputeInstancesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  zone = messages.StringField(5, required=True)


class ComputeInstancesResetRequest(messages.Message):
  """A ComputeInstancesResetRequest object.

  Fields:
    instance: Name of the instance scoping this request.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeInstancesSetDiskAutoDeleteRequest(messages.Message):
  """A ComputeInstancesSetDiskAutoDeleteRequest object.

  Fields:
    autoDelete: Whether to auto-delete the disk when the instance is deleted.
    deviceName: Disk device name to modify.
    instance: Instance name.
    project: Project name.
    zone: Name of the zone scoping this request.
  """

  autoDelete = messages.BooleanField(1, required=True)
  deviceName = messages.StringField(2, required=True)
  instance = messages.StringField(3, required=True)
  project = messages.StringField(4, required=True)
  zone = messages.StringField(5, required=True)


class ComputeInstancesSetMetadataRequest(messages.Message):
  """A ComputeInstancesSetMetadataRequest object.

  Fields:
    instance: Name of the instance scoping this request.
    metadata: A Metadata resource to be passed as the request body.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  instance = messages.StringField(1, required=True)
  metadata = messages.MessageField('Metadata', 2)
  project = messages.StringField(3, required=True)
  zone = messages.StringField(4, required=True)


class ComputeInstancesSetSchedulingRequest(messages.Message):
  """A ComputeInstancesSetSchedulingRequest object.

  Fields:
    instance: Instance name.
    project: Project name.
    scheduling: A Scheduling resource to be passed as the request body.
    zone: Name of the zone scoping this request.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  scheduling = messages.MessageField('Scheduling', 3)
  zone = messages.StringField(4, required=True)


class ComputeInstancesSetTagsRequest(messages.Message):
  """A ComputeInstancesSetTagsRequest object.

  Fields:
    instance: Name of the instance scoping this request.
    project: Name of the project scoping this request.
    tags: A Tags resource to be passed as the request body.
    zone: Name of the zone scoping this request.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  tags = messages.MessageField('Tags', 3)
  zone = messages.StringField(4, required=True)


class ComputeInstancesStartRequest(messages.Message):
  """A ComputeInstancesStartRequest object.

  Fields:
    instance: Name of the instance resource to start.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeInstancesStopRequest(messages.Message):
  """A ComputeInstancesStopRequest object.

  Fields:
    instance: Name of the instance resource to start.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  instance = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeLicensesGetRequest(messages.Message):
  """A ComputeLicensesGetRequest object.

  Fields:
    license: Name of the license resource to return.
    project: Name of the project scoping this request.
  """

  license = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeMachineTypesAggregatedListRequest(messages.Message):
  """A ComputeMachineTypesAggregatedListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Project ID for this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeMachineTypesGetRequest(messages.Message):
  """A ComputeMachineTypesGetRequest object.

  Fields:
    machineType: Name of the machine type resource to return.
    project: Project ID for this request.
    zone: Name of the zone scoping this request.
  """

  machineType = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeMachineTypesListRequest(messages.Message):
  """A ComputeMachineTypesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Project ID for this request.
    zone: Name of the zone scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  zone = messages.StringField(5, required=True)


class ComputeNetworksDeleteRequest(messages.Message):
  """A ComputeNetworksDeleteRequest object.

  Fields:
    network: Name of the network resource to delete.
    project: Name of the project scoping this request.
  """

  network = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeNetworksGetRequest(messages.Message):
  """A ComputeNetworksGetRequest object.

  Fields:
    network: Name of the network resource to return.
    project: Name of the project scoping this request.
  """

  network = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class ComputeNetworksInsertRequest(messages.Message):
  """A ComputeNetworksInsertRequest object.

  Fields:
    network: A Network resource to be passed as the request body.
    project: Name of the project scoping this request.
  """

  network = messages.MessageField('Network', 1)
  project = messages.StringField(2, required=True)


class ComputeNetworksListRequest(messages.Message):
  """A ComputeNetworksListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeProjectsGetRequest(messages.Message):
  """A ComputeProjectsGetRequest object.

  Fields:
    project: Name of the project resource to retrieve.
  """

  project = messages.StringField(1, required=True)


class ComputeProjectsSetCommonInstanceMetadataRequest(messages.Message):
  """A ComputeProjectsSetCommonInstanceMetadataRequest object.

  Fields:
    metadata: A Metadata resource to be passed as the request body.
    project: Name of the project scoping this request.
  """

  metadata = messages.MessageField('Metadata', 1)
  project = messages.StringField(2, required=True)


class ComputeProjectsSetUsageExportBucketRequest(messages.Message):
  """A ComputeProjectsSetUsageExportBucketRequest object.

  Fields:
    project: Name of the project scoping this request.
    usageExportLocation: A UsageExportLocation resource to be passed as the
      request body.
  """

  project = messages.StringField(1, required=True)
  usageExportLocation = messages.MessageField('UsageExportLocation', 2)


class ComputeRegionOperationsDeleteRequest(messages.Message):
  """A ComputeRegionOperationsDeleteRequest object.

  Fields:
    operation: Name of the operation resource to delete.
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
  """

  operation = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)


class ComputeRegionOperationsDeleteResponse(messages.Message):
  """An empty ComputeRegionOperationsDelete response."""


class ComputeRegionOperationsGetRequest(messages.Message):
  """A ComputeRegionOperationsGetRequest object.

  Fields:
    operation: Name of the operation resource to return.
    project: Name of the project scoping this request.
    region: Name of the zone scoping this request.
  """

  operation = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)


class ComputeRegionOperationsListRequest(messages.Message):
  """A ComputeRegionOperationsListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  region = messages.StringField(5, required=True)


class ComputeRegionsGetRequest(messages.Message):
  """A ComputeRegionsGetRequest object.

  Fields:
    project: Name of the project scoping this request.
    region: Name of the region resource to return.
  """

  project = messages.StringField(1, required=True)
  region = messages.StringField(2, required=True)


class ComputeRegionsListRequest(messages.Message):
  """A ComputeRegionsListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeRoutesDeleteRequest(messages.Message):
  """A ComputeRoutesDeleteRequest object.

  Fields:
    project: Name of the project scoping this request.
    route: Name of the route resource to delete.
  """

  project = messages.StringField(1, required=True)
  route = messages.StringField(2, required=True)


class ComputeRoutesGetRequest(messages.Message):
  """A ComputeRoutesGetRequest object.

  Fields:
    project: Name of the project scoping this request.
    route: Name of the route resource to return.
  """

  project = messages.StringField(1, required=True)
  route = messages.StringField(2, required=True)


class ComputeRoutesInsertRequest(messages.Message):
  """A ComputeRoutesInsertRequest object.

  Fields:
    project: Name of the project scoping this request.
    route: A Route resource to be passed as the request body.
  """

  project = messages.StringField(1, required=True)
  route = messages.MessageField('Route', 2)


class ComputeRoutesListRequest(messages.Message):
  """A ComputeRoutesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeSnapshotsDeleteRequest(messages.Message):
  """A ComputeSnapshotsDeleteRequest object.

  Fields:
    project: Name of the project scoping this request.
    snapshot: Name of the persistent disk snapshot resource to delete.
  """

  project = messages.StringField(1, required=True)
  snapshot = messages.StringField(2, required=True)


class ComputeSnapshotsGetRequest(messages.Message):
  """A ComputeSnapshotsGetRequest object.

  Fields:
    project: Name of the project scoping this request.
    snapshot: Name of the persistent disk snapshot resource to return.
  """

  project = messages.StringField(1, required=True)
  snapshot = messages.StringField(2, required=True)


class ComputeSnapshotsListRequest(messages.Message):
  """A ComputeSnapshotsListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeTargetHttpProxiesDeleteRequest(messages.Message):
  """A ComputeTargetHttpProxiesDeleteRequest object.

  Fields:
    project: Name of the project scoping this request.
    targetHttpProxy: Name of the TargetHttpProxy resource to delete.
  """

  project = messages.StringField(1, required=True)
  targetHttpProxy = messages.StringField(2, required=True)


class ComputeTargetHttpProxiesGetRequest(messages.Message):
  """A ComputeTargetHttpProxiesGetRequest object.

  Fields:
    project: Name of the project scoping this request.
    targetHttpProxy: Name of the TargetHttpProxy resource to return.
  """

  project = messages.StringField(1, required=True)
  targetHttpProxy = messages.StringField(2, required=True)


class ComputeTargetHttpProxiesInsertRequest(messages.Message):
  """A ComputeTargetHttpProxiesInsertRequest object.

  Fields:
    project: Name of the project scoping this request.
    targetHttpProxy: A TargetHttpProxy resource to be passed as the request
      body.
  """

  project = messages.StringField(1, required=True)
  targetHttpProxy = messages.MessageField('TargetHttpProxy', 2)


class ComputeTargetHttpProxiesListRequest(messages.Message):
  """A ComputeTargetHttpProxiesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeTargetHttpProxiesSetUrlMapRequest(messages.Message):
  """A ComputeTargetHttpProxiesSetUrlMapRequest object.

  Fields:
    project: Name of the project scoping this request.
    targetHttpProxy: Name of the TargetHttpProxy resource whose URL map is to
      be set.
    urlMapReference: A UrlMapReference resource to be passed as the request
      body.
  """

  project = messages.StringField(1, required=True)
  targetHttpProxy = messages.StringField(2, required=True)
  urlMapReference = messages.MessageField('UrlMapReference', 3)


class ComputeTargetInstancesAggregatedListRequest(messages.Message):
  """A ComputeTargetInstancesAggregatedListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeTargetInstancesDeleteRequest(messages.Message):
  """A ComputeTargetInstancesDeleteRequest object.

  Fields:
    project: Name of the project scoping this request.
    targetInstance: Name of the TargetInstance resource to delete.
    zone: Name of the zone scoping this request.
  """

  project = messages.StringField(1, required=True)
  targetInstance = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeTargetInstancesGetRequest(messages.Message):
  """A ComputeTargetInstancesGetRequest object.

  Fields:
    project: Name of the project scoping this request.
    targetInstance: Name of the TargetInstance resource to return.
    zone: Name of the zone scoping this request.
  """

  project = messages.StringField(1, required=True)
  targetInstance = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeTargetInstancesInsertRequest(messages.Message):
  """A ComputeTargetInstancesInsertRequest object.

  Fields:
    project: Name of the project scoping this request.
    targetInstance: A TargetInstance resource to be passed as the request
      body.
    zone: Name of the zone scoping this request.
  """

  project = messages.StringField(1, required=True)
  targetInstance = messages.MessageField('TargetInstance', 2)
  zone = messages.StringField(3, required=True)


class ComputeTargetInstancesListRequest(messages.Message):
  """A ComputeTargetInstancesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  zone = messages.StringField(5, required=True)


class ComputeTargetPoolsAddHealthCheckRequest(messages.Message):
  """A ComputeTargetPoolsAddHealthCheckRequest object.

  Fields:
    project: A string attribute.
    region: Name of the region scoping this request.
    targetPool: Name of the TargetPool resource to which health_check_url is
      to be added.
    targetPoolsAddHealthCheckRequest: A TargetPoolsAddHealthCheckRequest
      resource to be passed as the request body.
  """

  project = messages.StringField(1, required=True)
  region = messages.StringField(2, required=True)
  targetPool = messages.StringField(3, required=True)
  targetPoolsAddHealthCheckRequest = messages.MessageField('TargetPoolsAddHealthCheckRequest', 4)


class ComputeTargetPoolsAddInstanceRequest(messages.Message):
  """A ComputeTargetPoolsAddInstanceRequest object.

  Fields:
    project: A string attribute.
    region: Name of the region scoping this request.
    targetPool: Name of the TargetPool resource to which instance_url is to be
      added.
    targetPoolsAddInstanceRequest: A TargetPoolsAddInstanceRequest resource to
      be passed as the request body.
  """

  project = messages.StringField(1, required=True)
  region = messages.StringField(2, required=True)
  targetPool = messages.StringField(3, required=True)
  targetPoolsAddInstanceRequest = messages.MessageField('TargetPoolsAddInstanceRequest', 4)


class ComputeTargetPoolsAggregatedListRequest(messages.Message):
  """A ComputeTargetPoolsAggregatedListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeTargetPoolsDeleteRequest(messages.Message):
  """A ComputeTargetPoolsDeleteRequest object.

  Fields:
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
    targetPool: Name of the TargetPool resource to delete.
  """

  project = messages.StringField(1, required=True)
  region = messages.StringField(2, required=True)
  targetPool = messages.StringField(3, required=True)


class ComputeTargetPoolsGetHealthRequest(messages.Message):
  """A ComputeTargetPoolsGetHealthRequest object.

  Fields:
    instanceReference: A InstanceReference resource to be passed as the
      request body.
    project: A string attribute.
    region: Name of the region scoping this request.
    targetPool: Name of the TargetPool resource to which the queried instance
      belongs.
  """

  instanceReference = messages.MessageField('InstanceReference', 1)
  project = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)
  targetPool = messages.StringField(4, required=True)


class ComputeTargetPoolsGetRequest(messages.Message):
  """A ComputeTargetPoolsGetRequest object.

  Fields:
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
    targetPool: Name of the TargetPool resource to return.
  """

  project = messages.StringField(1, required=True)
  region = messages.StringField(2, required=True)
  targetPool = messages.StringField(3, required=True)


class ComputeTargetPoolsInsertRequest(messages.Message):
  """A ComputeTargetPoolsInsertRequest object.

  Fields:
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
    targetPool: A TargetPool resource to be passed as the request body.
  """

  project = messages.StringField(1, required=True)
  region = messages.StringField(2, required=True)
  targetPool = messages.MessageField('TargetPool', 3)


class ComputeTargetPoolsListRequest(messages.Message):
  """A ComputeTargetPoolsListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  region = messages.StringField(5, required=True)


class ComputeTargetPoolsRemoveHealthCheckRequest(messages.Message):
  """A ComputeTargetPoolsRemoveHealthCheckRequest object.

  Fields:
    project: A string attribute.
    region: Name of the region scoping this request.
    targetPool: Name of the TargetPool resource to which health_check_url is
      to be removed.
    targetPoolsRemoveHealthCheckRequest: A TargetPoolsRemoveHealthCheckRequest
      resource to be passed as the request body.
  """

  project = messages.StringField(1, required=True)
  region = messages.StringField(2, required=True)
  targetPool = messages.StringField(3, required=True)
  targetPoolsRemoveHealthCheckRequest = messages.MessageField('TargetPoolsRemoveHealthCheckRequest', 4)


class ComputeTargetPoolsRemoveInstanceRequest(messages.Message):
  """A ComputeTargetPoolsRemoveInstanceRequest object.

  Fields:
    project: A string attribute.
    region: Name of the region scoping this request.
    targetPool: Name of the TargetPool resource to which instance_url is to be
      removed.
    targetPoolsRemoveInstanceRequest: A TargetPoolsRemoveInstanceRequest
      resource to be passed as the request body.
  """

  project = messages.StringField(1, required=True)
  region = messages.StringField(2, required=True)
  targetPool = messages.StringField(3, required=True)
  targetPoolsRemoveInstanceRequest = messages.MessageField('TargetPoolsRemoveInstanceRequest', 4)


class ComputeTargetPoolsSetBackupRequest(messages.Message):
  """A ComputeTargetPoolsSetBackupRequest object.

  Fields:
    failoverRatio: New failoverRatio value for the containing target pool.
    project: Name of the project scoping this request.
    region: Name of the region scoping this request.
    targetPool: Name of the TargetPool resource for which the backup is to be
      set.
    targetReference: A TargetReference resource to be passed as the request
      body.
  """

  failoverRatio = messages.FloatField(1, variant=messages.Variant.FLOAT)
  project = messages.StringField(2, required=True)
  region = messages.StringField(3, required=True)
  targetPool = messages.StringField(4, required=True)
  targetReference = messages.MessageField('TargetReference', 5)


class ComputeUrlMapsDeleteRequest(messages.Message):
  """A ComputeUrlMapsDeleteRequest object.

  Fields:
    project: Name of the project scoping this request.
    urlMap: Name of the UrlMap resource to delete.
  """

  project = messages.StringField(1, required=True)
  urlMap = messages.StringField(2, required=True)


class ComputeUrlMapsGetRequest(messages.Message):
  """A ComputeUrlMapsGetRequest object.

  Fields:
    project: Name of the project scoping this request.
    urlMap: Name of the UrlMap resource to return.
  """

  project = messages.StringField(1, required=True)
  urlMap = messages.StringField(2, required=True)


class ComputeUrlMapsInsertRequest(messages.Message):
  """A ComputeUrlMapsInsertRequest object.

  Fields:
    project: Name of the project scoping this request.
    urlMap: A UrlMap resource to be passed as the request body.
  """

  project = messages.StringField(1, required=True)
  urlMap = messages.MessageField('UrlMap', 2)


class ComputeUrlMapsListRequest(messages.Message):
  """A ComputeUrlMapsListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class ComputeUrlMapsPatchRequest(messages.Message):
  """A ComputeUrlMapsPatchRequest object.

  Fields:
    project: Name of the project scoping this request.
    urlMap: Name of the UrlMap resource to update.
    urlMapResource: A UrlMap resource to be passed as the request body.
  """

  project = messages.StringField(1, required=True)
  urlMap = messages.StringField(2, required=True)
  urlMapResource = messages.MessageField('UrlMap', 3)


class ComputeUrlMapsUpdateRequest(messages.Message):
  """A ComputeUrlMapsUpdateRequest object.

  Fields:
    project: Name of the project scoping this request.
    urlMap: Name of the UrlMap resource to update.
    urlMapResource: A UrlMap resource to be passed as the request body.
  """

  project = messages.StringField(1, required=True)
  urlMap = messages.StringField(2, required=True)
  urlMapResource = messages.MessageField('UrlMap', 3)


class ComputeUrlMapsValidateRequest(messages.Message):
  """A ComputeUrlMapsValidateRequest object.

  Fields:
    project: Name of the project scoping this request.
    urlMap: Name of the UrlMap resource to be validated as.
    urlMapsValidateRequest: A UrlMapsValidateRequest resource to be passed as
      the request body.
  """

  project = messages.StringField(1, required=True)
  urlMap = messages.StringField(2, required=True)
  urlMapsValidateRequest = messages.MessageField('UrlMapsValidateRequest', 3)


class ComputeZoneOperationsDeleteRequest(messages.Message):
  """A ComputeZoneOperationsDeleteRequest object.

  Fields:
    operation: Name of the operation resource to delete.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  operation = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeZoneOperationsDeleteResponse(messages.Message):
  """An empty ComputeZoneOperationsDelete response."""


class ComputeZoneOperationsGetRequest(messages.Message):
  """A ComputeZoneOperationsGetRequest object.

  Fields:
    operation: Name of the operation resource to return.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  operation = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ComputeZoneOperationsListRequest(messages.Message):
  """A ComputeZoneOperationsListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
    zone: Name of the zone scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  zone = messages.StringField(5, required=True)


class ComputeZonesGetRequest(messages.Message):
  """A ComputeZonesGetRequest object.

  Fields:
    project: Name of the project scoping this request.
    zone: Name of the zone resource to return.
  """

  project = messages.StringField(1, required=True)
  zone = messages.StringField(2, required=True)


class ComputeZonesListRequest(messages.Message):
  """A ComputeZonesListRequest object.

  Fields:
    filter: Optional. Filter expression for filtering listed resources.
    maxResults: Optional. Maximum count of results to be returned. Maximum
      value is 500 and default value is 500.
    pageToken: Optional. Tag returned by a previous list request truncated by
      maxResults. Used to continue a previous list request.
    project: Name of the project scoping this request.
  """

  filter = messages.StringField(1)
  maxResults = messages.IntegerField(2, variant=messages.Variant.UINT32, default=500)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)


class DeprecationStatus(messages.Message):
  """Deprecation status for a public resource.

  Enums:
    StateValueValuesEnum: The deprecation state. Can be "DEPRECATED",
      "OBSOLETE", or "DELETED". Operations which create a new resource using a
      "DEPRECATED" resource will return successfully, but with a warning
      indicating the deprecated resource and recommending its replacement. New
      uses of "OBSOLETE" or "DELETED" resources will result in an error.

  Fields:
    deleted: An optional RFC3339 timestamp on or after which the deprecation
      state of this resource will be changed to DELETED.
    deprecated: An optional RFC3339 timestamp on or after which the
      deprecation state of this resource will be changed to DEPRECATED.
    obsolete: An optional RFC3339 timestamp on or after which the deprecation
      state of this resource will be changed to OBSOLETE.
    replacement: A URL of the suggested replacement for the deprecated
      resource. The deprecated resource and its replacement must be resources
      of the same kind.
    state: The deprecation state. Can be "DEPRECATED", "OBSOLETE", or
      "DELETED". Operations which create a new resource using a "DEPRECATED"
      resource will return successfully, but with a warning indicating the
      deprecated resource and recommending its replacement. New uses of
      "OBSOLETE" or "DELETED" resources will result in an error.
  """

  class StateValueValuesEnum(messages.Enum):
    """The deprecation state. Can be "DEPRECATED", "OBSOLETE", or "DELETED".
    Operations which create a new resource using a "DEPRECATED" resource will
    return successfully, but with a warning indicating the deprecated resource
    and recommending its replacement. New uses of "OBSOLETE" or "DELETED"
    resources will result in an error.

    Values:
      DELETED: <no description>
      DEPRECATED: <no description>
      OBSOLETE: <no description>
    """
    DELETED = 0
    DEPRECATED = 1
    OBSOLETE = 2

  deleted = messages.StringField(1)
  deprecated = messages.StringField(2)
  obsolete = messages.StringField(3)
  replacement = messages.StringField(4)
  state = messages.EnumField('StateValueValuesEnum', 5)


class Disk(messages.Message):
  """A persistent disk resource.

  Enums:
    StatusValueValuesEnum: The status of disk creation (output only).

  Fields:
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    licenses: Public visible licenses.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    options: Internal use only.
    selfLink: Server defined URL for the resource (output only).
    sizeGb: Size of the persistent disk, specified in GB. This parameter is
      optional when creating a disk from a disk image or a snapshot, otherwise
      it is required.
    sourceImage: The source image used to create this disk.
    sourceImageId: The 'id' value of the image used to create this disk. This
      value may be used to determine whether the disk was created from the
      current or a previous instance of a given image.
    sourceSnapshot: The source snapshot used to create this disk.
    sourceSnapshotId: The 'id' value of the snapshot used to create this disk.
      This value may be used to determine whether the disk was created from
      the current or a previous instance of a given disk snapshot.
    status: The status of disk creation (output only).
    type: URL of the disk type resource describing which disk type to use to
      create the disk; provided by the client when the disk is created.
    zone: URL of the zone where the disk resides (output only).
  """

  class StatusValueValuesEnum(messages.Enum):
    """The status of disk creation (output only).

    Values:
      CREATING: <no description>
      FAILED: <no description>
      READY: <no description>
      RESTORING: <no description>
    """
    CREATING = 0
    FAILED = 1
    READY = 2
    RESTORING = 3

  creationTimestamp = messages.StringField(1)
  description = messages.StringField(2)
  id = messages.IntegerField(3, variant=messages.Variant.UINT64)
  kind = messages.StringField(4, default=u'compute#disk')
  licenses = messages.StringField(5, repeated=True)
  name = messages.StringField(6)
  options = messages.StringField(7)
  selfLink = messages.StringField(8)
  sizeGb = messages.IntegerField(9)
  sourceImage = messages.StringField(10)
  sourceImageId = messages.StringField(11)
  sourceSnapshot = messages.StringField(12)
  sourceSnapshotId = messages.StringField(13)
  status = messages.EnumField('StatusValueValuesEnum', 14)
  type = messages.StringField(15)
  zone = messages.StringField(16)


class DiskAggregatedList(messages.Message):
  """A DiskAggregatedList object.

  Messages:
    ItemsValue: A map of scoped disk lists.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A map of scoped disk lists.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ItemsValue(messages.Message):
    """A map of scoped disk lists.

    Messages:
      AdditionalProperty: An additional property for a ItemsValue object.

    Fields:
      additionalProperties: Name of the scope containing this set of disks.
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a ItemsValue object.

      Fields:
        key: Name of the additional property.
        value: A DisksScopedList attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('DisksScopedList', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  id = messages.StringField(1)
  items = messages.MessageField('ItemsValue', 2)
  kind = messages.StringField(3, default=u'compute#diskAggregatedList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class DiskList(messages.Message):
  """Contains a list of persistent disk resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of Disk resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('Disk', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#diskList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class DiskType(messages.Message):
  """A disk type resource.

  Fields:
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    defaultDiskSizeGb: Server defined default disk size in gb (output only).
    deprecated: The deprecation status associated with this disk type.
    description: An optional textual description of the resource.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    name: Name of the resource.
    selfLink: Server defined URL for the resource (output only).
    validDiskSize: An optional textual descroption of the valid disk size,
      e.g., "10GB-10TB".
    zone: Url of the zone where the disk type resides (output only).
  """

  creationTimestamp = messages.StringField(1)
  defaultDiskSizeGb = messages.IntegerField(2)
  deprecated = messages.MessageField('DeprecationStatus', 3)
  description = messages.StringField(4)
  id = messages.IntegerField(5, variant=messages.Variant.UINT64)
  kind = messages.StringField(6, default=u'compute#diskType')
  name = messages.StringField(7)
  selfLink = messages.StringField(8)
  validDiskSize = messages.StringField(9)
  zone = messages.StringField(10)


class DiskTypeAggregatedList(messages.Message):
  """A DiskTypeAggregatedList object.

  Messages:
    ItemsValue: A map of scoped disk type lists.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A map of scoped disk type lists.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ItemsValue(messages.Message):
    """A map of scoped disk type lists.

    Messages:
      AdditionalProperty: An additional property for a ItemsValue object.

    Fields:
      additionalProperties: Name of the scope containing this set of disk
        types.
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a ItemsValue object.

      Fields:
        key: Name of the additional property.
        value: A DiskTypesScopedList attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('DiskTypesScopedList', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  id = messages.StringField(1)
  items = messages.MessageField('ItemsValue', 2)
  kind = messages.StringField(3, default=u'compute#diskTypeAggregatedList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class DiskTypeList(messages.Message):
  """Contains a list of disk type resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of DiskType resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('DiskType', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#diskTypeList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class DiskTypesScopedList(messages.Message):
  """A DiskTypesScopedList object.

  Messages:
    WarningValue: Informational warning which replaces the list of disk types
      when the list is empty.

  Fields:
    diskTypes: List of disk types contained in this scope.
    warning: Informational warning which replaces the list of disk types when
      the list is empty.
  """

  class WarningValue(messages.Message):
    """Informational warning which replaces the list of disk types when the
    list is empty.

    Enums:
      CodeValueValuesEnum: The warning type identifier for this warning.

    Messages:
      DataValueListEntry: A DataValueListEntry object.

    Fields:
      code: The warning type identifier for this warning.
      data: Metadata for this warning in 'key: value' format.
      message: Optional human-readable details for this warning.
    """

    class CodeValueValuesEnum(messages.Enum):
      """The warning type identifier for this warning.

      Values:
        DEPRECATED_RESOURCE_USED: <no description>
        DISK_SIZE_LARGER_THAN_IMAGE_SIZE: <no description>
        INJECTED_KERNELS_DEPRECATED: <no description>
        NEXT_HOP_ADDRESS_NOT_ASSIGNED: <no description>
        NEXT_HOP_CANNOT_IP_FORWARD: <no description>
        NEXT_HOP_INSTANCE_NOT_FOUND: <no description>
        NEXT_HOP_INSTANCE_NOT_ON_NETWORK: <no description>
        NEXT_HOP_NOT_RUNNING: <no description>
        NO_RESULTS_ON_PAGE: <no description>
        REQUIRED_TOS_AGREEMENT: <no description>
        RESOURCE_NOT_DELETED: <no description>
        UNREACHABLE: <no description>
      """
      DEPRECATED_RESOURCE_USED = 0
      DISK_SIZE_LARGER_THAN_IMAGE_SIZE = 1
      INJECTED_KERNELS_DEPRECATED = 2
      NEXT_HOP_ADDRESS_NOT_ASSIGNED = 3
      NEXT_HOP_CANNOT_IP_FORWARD = 4
      NEXT_HOP_INSTANCE_NOT_FOUND = 5
      NEXT_HOP_INSTANCE_NOT_ON_NETWORK = 6
      NEXT_HOP_NOT_RUNNING = 7
      NO_RESULTS_ON_PAGE = 8
      REQUIRED_TOS_AGREEMENT = 9
      RESOURCE_NOT_DELETED = 10
      UNREACHABLE = 11

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: A key for the warning data.
        value: A warning data value corresponding to the key.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.EnumField('CodeValueValuesEnum', 1)
    data = messages.MessageField('DataValueListEntry', 2, repeated=True)
    message = messages.StringField(3)

  diskTypes = messages.MessageField('DiskType', 1, repeated=True)
  warning = messages.MessageField('WarningValue', 2)


class DisksScopedList(messages.Message):
  """A DisksScopedList object.

  Messages:
    WarningValue: Informational warning which replaces the list of disks when
      the list is empty.

  Fields:
    disks: List of disks contained in this scope.
    warning: Informational warning which replaces the list of disks when the
      list is empty.
  """

  class WarningValue(messages.Message):
    """Informational warning which replaces the list of disks when the list is
    empty.

    Enums:
      CodeValueValuesEnum: The warning type identifier for this warning.

    Messages:
      DataValueListEntry: A DataValueListEntry object.

    Fields:
      code: The warning type identifier for this warning.
      data: Metadata for this warning in 'key: value' format.
      message: Optional human-readable details for this warning.
    """

    class CodeValueValuesEnum(messages.Enum):
      """The warning type identifier for this warning.

      Values:
        DEPRECATED_RESOURCE_USED: <no description>
        DISK_SIZE_LARGER_THAN_IMAGE_SIZE: <no description>
        INJECTED_KERNELS_DEPRECATED: <no description>
        NEXT_HOP_ADDRESS_NOT_ASSIGNED: <no description>
        NEXT_HOP_CANNOT_IP_FORWARD: <no description>
        NEXT_HOP_INSTANCE_NOT_FOUND: <no description>
        NEXT_HOP_INSTANCE_NOT_ON_NETWORK: <no description>
        NEXT_HOP_NOT_RUNNING: <no description>
        NO_RESULTS_ON_PAGE: <no description>
        REQUIRED_TOS_AGREEMENT: <no description>
        RESOURCE_NOT_DELETED: <no description>
        UNREACHABLE: <no description>
      """
      DEPRECATED_RESOURCE_USED = 0
      DISK_SIZE_LARGER_THAN_IMAGE_SIZE = 1
      INJECTED_KERNELS_DEPRECATED = 2
      NEXT_HOP_ADDRESS_NOT_ASSIGNED = 3
      NEXT_HOP_CANNOT_IP_FORWARD = 4
      NEXT_HOP_INSTANCE_NOT_FOUND = 5
      NEXT_HOP_INSTANCE_NOT_ON_NETWORK = 6
      NEXT_HOP_NOT_RUNNING = 7
      NO_RESULTS_ON_PAGE = 8
      REQUIRED_TOS_AGREEMENT = 9
      RESOURCE_NOT_DELETED = 10
      UNREACHABLE = 11

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: A key for the warning data.
        value: A warning data value corresponding to the key.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.EnumField('CodeValueValuesEnum', 1)
    data = messages.MessageField('DataValueListEntry', 2, repeated=True)
    message = messages.StringField(3)

  disks = messages.MessageField('Disk', 1, repeated=True)
  warning = messages.MessageField('WarningValue', 2)


class Firewall(messages.Message):
  """A firewall resource.

  Messages:
    AllowedValueListEntry: A AllowedValueListEntry object.

  Fields:
    allowed: The list of rules specified by this firewall. Each rule specifies
      a protocol and port-range tuple that describes a permitted connection.
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    network: URL of the network to which this firewall is applied; provided by
      the client when the firewall is created.
    selfLink: Server defined URL for the resource (output only).
    sourceRanges: A list of IP address blocks expressed in CIDR format which
      this rule applies to. One or both of sourceRanges and sourceTags may be
      set; an inbound connection is allowed if either the range or the tag of
      the source matches.
    sourceTags: A list of instance tags which this rule applies to. One or
      both of sourceRanges and sourceTags may be set; an inbound connection is
      allowed if either the range or the tag of the source matches.
    targetTags: A list of instance tags indicating sets of instances located
      on network which may make network connections as specified in allowed.
      If no targetTags are specified, the firewall rule applies to all
      instances on the specified network.
  """

  class AllowedValueListEntry(messages.Message):
    """A AllowedValueListEntry object.

    Fields:
      IPProtocol: Required; this is the IP protocol that is allowed for this
        rule. This can either be one of the following well known protocol
        strings ["tcp", "udp", "icmp", "esp", "ah", "sctp"], or the IP
        protocol number.
      ports: An optional list of ports which are allowed. It is an error to
        specify this for any protocol that isn't UDP or TCP. Each entry must
        be either an integer or a range. If not specified, connections through
        any port are allowed.  Example inputs include: ["22"], ["80","443"]
        and ["12345-12349"].
    """

    IPProtocol = messages.StringField(1)
    ports = messages.StringField(2, repeated=True)

  allowed = messages.MessageField('AllowedValueListEntry', 1, repeated=True)
  creationTimestamp = messages.StringField(2)
  description = messages.StringField(3)
  id = messages.IntegerField(4, variant=messages.Variant.UINT64)
  kind = messages.StringField(5, default=u'compute#firewall')
  name = messages.StringField(6)
  network = messages.StringField(7)
  selfLink = messages.StringField(8)
  sourceRanges = messages.StringField(9, repeated=True)
  sourceTags = messages.StringField(10, repeated=True)
  targetTags = messages.StringField(11, repeated=True)


class FirewallList(messages.Message):
  """Contains a list of firewall resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of Firewall resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('Firewall', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#firewallList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class ForwardingRule(messages.Message):
  """A ForwardingRule resource. A ForwardingRule resource specifies which pool
  of target VMs to forward a packet to if it matches the given [IPAddress,
  IPProtocol, portRange] tuple.

  Enums:
    IPProtocolValueValuesEnum: The IP protocol to which this rule applies,
      valid options are 'TCP', 'UDP', 'ESP', 'AH' or 'SCTP'.

  Fields:
    IPAddress: Value of the reserved IP address that this forwarding rule is
      serving on behalf of. For global forwarding rules, the address must be a
      global IP; for regional forwarding rules, the address must live in the
      same region as the forwarding rule. If left empty (default value), an
      ephemeral IP from the same scope (global or regional) will be assigned.
    IPProtocol: The IP protocol to which this rule applies, valid options are
      'TCP', 'UDP', 'ESP', 'AH' or 'SCTP'.
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    portRange: Applicable only when 'IPProtocol' is 'TCP', 'UDP' or 'SCTP',
      only packets addressed to ports in the specified range will be forwarded
      to 'target'. If 'portRange' is left empty (default value), all ports are
      forwarded. Forwarding rules with the same [IPAddress, IPProtocol] pair
      must have disjoint port ranges.
    region: URL of the region where the regional forwarding rule resides
      (output only). This field is not applicable to global forwarding rules.
    selfLink: Server defined URL for the resource (output only).
    target: The URL of the target resource to receive the matched traffic. For
      regional forwarding rules, this target must live in the same region as
      the forwarding rule. For global forwarding rules, this target must be a
      global TargetHttpProxy resource.
  """

  class IPProtocolValueValuesEnum(messages.Enum):
    """The IP protocol to which this rule applies, valid options are 'TCP',
    'UDP', 'ESP', 'AH' or 'SCTP'.

    Values:
      AH: <no description>
      ESP: <no description>
      SCTP: <no description>
      TCP: <no description>
      UDP: <no description>
    """
    AH = 0
    ESP = 1
    SCTP = 2
    TCP = 3
    UDP = 4

  IPAddress = messages.StringField(1)
  IPProtocol = messages.EnumField('IPProtocolValueValuesEnum', 2)
  creationTimestamp = messages.StringField(3)
  description = messages.StringField(4)
  id = messages.IntegerField(5, variant=messages.Variant.UINT64)
  kind = messages.StringField(6, default=u'compute#forwardingRule')
  name = messages.StringField(7)
  portRange = messages.StringField(8)
  region = messages.StringField(9)
  selfLink = messages.StringField(10)
  target = messages.StringField(11)


class ForwardingRuleAggregatedList(messages.Message):
  """A ForwardingRuleAggregatedList object.

  Messages:
    ItemsValue: A map of scoped forwarding rule lists.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A map of scoped forwarding rule lists.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ItemsValue(messages.Message):
    """A map of scoped forwarding rule lists.

    Messages:
      AdditionalProperty: An additional property for a ItemsValue object.

    Fields:
      additionalProperties: Name of the scope containing this set of
        addresses.
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a ItemsValue object.

      Fields:
        key: Name of the additional property.
        value: A ForwardingRulesScopedList attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('ForwardingRulesScopedList', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  id = messages.StringField(1)
  items = messages.MessageField('ItemsValue', 2)
  kind = messages.StringField(3, default=u'compute#forwardingRuleAggregatedList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class ForwardingRuleList(messages.Message):
  """Contains a list of ForwardingRule resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of ForwardingRule resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('ForwardingRule', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#forwardingRuleList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class ForwardingRulesScopedList(messages.Message):
  """A ForwardingRulesScopedList object.

  Messages:
    WarningValue: Informational warning which replaces the list of forwarding
      rules when the list is empty.

  Fields:
    forwardingRules: List of forwarding rules contained in this scope.
    warning: Informational warning which replaces the list of forwarding rules
      when the list is empty.
  """

  class WarningValue(messages.Message):
    """Informational warning which replaces the list of forwarding rules when
    the list is empty.

    Enums:
      CodeValueValuesEnum: The warning type identifier for this warning.

    Messages:
      DataValueListEntry: A DataValueListEntry object.

    Fields:
      code: The warning type identifier for this warning.
      data: Metadata for this warning in 'key: value' format.
      message: Optional human-readable details for this warning.
    """

    class CodeValueValuesEnum(messages.Enum):
      """The warning type identifier for this warning.

      Values:
        DEPRECATED_RESOURCE_USED: <no description>
        DISK_SIZE_LARGER_THAN_IMAGE_SIZE: <no description>
        INJECTED_KERNELS_DEPRECATED: <no description>
        NEXT_HOP_ADDRESS_NOT_ASSIGNED: <no description>
        NEXT_HOP_CANNOT_IP_FORWARD: <no description>
        NEXT_HOP_INSTANCE_NOT_FOUND: <no description>
        NEXT_HOP_INSTANCE_NOT_ON_NETWORK: <no description>
        NEXT_HOP_NOT_RUNNING: <no description>
        NO_RESULTS_ON_PAGE: <no description>
        REQUIRED_TOS_AGREEMENT: <no description>
        RESOURCE_NOT_DELETED: <no description>
        UNREACHABLE: <no description>
      """
      DEPRECATED_RESOURCE_USED = 0
      DISK_SIZE_LARGER_THAN_IMAGE_SIZE = 1
      INJECTED_KERNELS_DEPRECATED = 2
      NEXT_HOP_ADDRESS_NOT_ASSIGNED = 3
      NEXT_HOP_CANNOT_IP_FORWARD = 4
      NEXT_HOP_INSTANCE_NOT_FOUND = 5
      NEXT_HOP_INSTANCE_NOT_ON_NETWORK = 6
      NEXT_HOP_NOT_RUNNING = 7
      NO_RESULTS_ON_PAGE = 8
      REQUIRED_TOS_AGREEMENT = 9
      RESOURCE_NOT_DELETED = 10
      UNREACHABLE = 11

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: A key for the warning data.
        value: A warning data value corresponding to the key.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.EnumField('CodeValueValuesEnum', 1)
    data = messages.MessageField('DataValueListEntry', 2, repeated=True)
    message = messages.StringField(3)

  forwardingRules = messages.MessageField('ForwardingRule', 1, repeated=True)
  warning = messages.MessageField('WarningValue', 2)


class HealthCheckReference(messages.Message):
  """A HealthCheckReference object.

  Fields:
    healthCheck: A string attribute.
  """

  healthCheck = messages.StringField(1)


class HealthStatus(messages.Message):
  """A HealthStatus object.

  Enums:
    HealthStateValueValuesEnum: Health state of the instance.

  Fields:
    healthState: Health state of the instance.
    instance: URL of the instance resource.
    ipAddress: The IP address represented by this resource.
    port: The port on the instance.
  """

  class HealthStateValueValuesEnum(messages.Enum):
    """Health state of the instance.

    Values:
      HEALTHY: <no description>
      UNHEALTHY: <no description>
    """
    HEALTHY = 0
    UNHEALTHY = 1

  healthState = messages.EnumField('HealthStateValueValuesEnum', 1)
  instance = messages.StringField(2)
  ipAddress = messages.StringField(3)
  port = messages.IntegerField(4, variant=messages.Variant.INT32)


class HostRule(messages.Message):
  """A host-matching rule for a URL. If matched, will use the named
  PathMatcher to select the BackendService.

  Fields:
    description: A string attribute.
    hosts: The list of host patterns to match. They must be valid hostnames
      except that they may start with *. or *-. The * acts like a glob and
      will match any string of atoms (separated by .s and -s) to the left.
    pathMatcher: The name of the PathMatcher to match the path portion of the
      URL, if the this HostRule matches the URL's host portion.
  """

  description = messages.StringField(1)
  hosts = messages.StringField(2, repeated=True)
  pathMatcher = messages.StringField(3)


class HttpHealthCheck(messages.Message):
  """An HttpHealthCheck resource. This resource defines a template for how
  individual VMs should be checked for health, via HTTP.

  Fields:
    checkIntervalSec: How often (in seconds) to send a health check. The
      default value is 5 seconds.
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    healthyThreshold: A so-far unhealthy VM will be marked healthy after this
      many consecutive successes. The default value is 2.
    host: The value of the host header in the HTTP health check request. If
      left empty (default value), the public IP on behalf of which this health
      check is performed will be used.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    port: The TCP port number for the HTTP health check request. The default
      value is 80.
    requestPath: The request path of the HTTP health check request. The
      default value is "/".
    selfLink: Server defined URL for the resource (output only).
    timeoutSec: How long (in seconds) to wait before claiming failure. The
      default value is 5 seconds. It is invalid for timeoutSec to have greater
      value than checkIntervalSec.
    unhealthyThreshold: A so-far healthy VM will be marked unhealthy after
      this many consecutive failures. The default value is 2.
  """

  checkIntervalSec = messages.IntegerField(1, variant=messages.Variant.INT32)
  creationTimestamp = messages.StringField(2)
  description = messages.StringField(3)
  healthyThreshold = messages.IntegerField(4, variant=messages.Variant.INT32)
  host = messages.StringField(5)
  id = messages.IntegerField(6, variant=messages.Variant.UINT64)
  kind = messages.StringField(7, default=u'compute#httpHealthCheck')
  name = messages.StringField(8)
  port = messages.IntegerField(9, variant=messages.Variant.INT32)
  requestPath = messages.StringField(10)
  selfLink = messages.StringField(11)
  timeoutSec = messages.IntegerField(12, variant=messages.Variant.INT32)
  unhealthyThreshold = messages.IntegerField(13, variant=messages.Variant.INT32)


class HttpHealthCheckList(messages.Message):
  """Contains a list of HttpHealthCheck resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of HttpHealthCheck resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('HttpHealthCheck', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#httpHealthCheckList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class Image(messages.Message):
  """A disk image resource.

  Enums:
    SourceTypeValueValuesEnum: Must be "RAW"; provided by the client when the
      disk image is created.
    StatusValueValuesEnum: Status of the image (output only). It will be one
      of the following READY - after image has been successfully created and
      is ready for use FAILED - if creating the image fails for some reason
      PENDING - the image creation is in progress An image can be used to
      create other resources suck as instances only after the image has been
      successfully created and the status is set to READY.

  Messages:
    RawDiskValue: The raw disk image parameters.

  Fields:
    archiveSizeBytes: Size of the image tar.gz archive stored in Google Cloud
      Storage (in bytes).
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    deprecated: The deprecation status associated with this image.
    description: Textual description of the resource; provided by the client
      when the resource is created.
    diskSizeGb: Size of the image when restored onto a disk (in GiB).
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    licenses: Public visible licenses.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    rawDisk: The raw disk image parameters.
    selfLink: Server defined URL for the resource (output only).
    sourceDisk: The source disk used to create this image.
    sourceDiskId: The 'id' value of the disk used to create this image. This
      value may be used to determine whether the image was taken from the
      current or a previous instance of a given disk name.
    sourceType: Must be "RAW"; provided by the client when the disk image is
      created.
    status: Status of the image (output only). It will be one of the following
      READY - after image has been successfully created and is ready for use
      FAILED - if creating the image fails for some reason PENDING - the image
      creation is in progress An image can be used to create other resources
      suck as instances only after the image has been successfully created and
      the status is set to READY.
  """

  class SourceTypeValueValuesEnum(messages.Enum):
    """Must be "RAW"; provided by the client when the disk image is created.

    Values:
      RAW: <no description>
    """
    RAW = 0

  class StatusValueValuesEnum(messages.Enum):
    """Status of the image (output only). It will be one of the following
    READY - after image has been successfully created and is ready for use
    FAILED - if creating the image fails for some reason PENDING - the image
    creation is in progress An image can be used to create other resources
    suck as instances only after the image has been successfully created and
    the status is set to READY.

    Values:
      FAILED: <no description>
      PENDING: <no description>
      READY: <no description>
    """
    FAILED = 0
    PENDING = 1
    READY = 2

  class RawDiskValue(messages.Message):
    """The raw disk image parameters.

    Enums:
      ContainerTypeValueValuesEnum: The format used to encode and transmit the
        block device. Should be TAR. This is just a container and transmission
        format and not a runtime format. Provided by the client when the disk
        image is created.

    Fields:
      containerType: The format used to encode and transmit the block device.
        Should be TAR. This is just a container and transmission format and
        not a runtime format. Provided by the client when the disk image is
        created.
      sha1Checksum: An optional SHA1 checksum of the disk image before
        unpackaging; provided by the client when the disk image is created.
      source: The full Google Cloud Storage URL where the disk image is
        stored; provided by the client when the disk image is created.
    """

    class ContainerTypeValueValuesEnum(messages.Enum):
      """The format used to encode and transmit the block device. Should be
      TAR. This is just a container and transmission format and not a runtime
      format. Provided by the client when the disk image is created.

      Values:
        TAR: <no description>
      """
      TAR = 0

    containerType = messages.EnumField('ContainerTypeValueValuesEnum', 1)
    sha1Checksum = messages.StringField(2)
    source = messages.StringField(3)

  archiveSizeBytes = messages.IntegerField(1)
  creationTimestamp = messages.StringField(2)
  deprecated = messages.MessageField('DeprecationStatus', 3)
  description = messages.StringField(4)
  diskSizeGb = messages.IntegerField(5)
  id = messages.IntegerField(6, variant=messages.Variant.UINT64)
  kind = messages.StringField(7, default=u'compute#image')
  licenses = messages.StringField(8, repeated=True)
  name = messages.StringField(9)
  rawDisk = messages.MessageField('RawDiskValue', 10)
  selfLink = messages.StringField(11)
  sourceDisk = messages.StringField(12)
  sourceDiskId = messages.StringField(13)
  sourceType = messages.EnumField('SourceTypeValueValuesEnum', 14, default=u'RAW')
  status = messages.EnumField('StatusValueValuesEnum', 15)


class ImageList(messages.Message):
  """Contains a list of disk image resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of Image resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('Image', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#imageList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class Instance(messages.Message):
  """An instance resource.

  Enums:
    StatusValueValuesEnum: Instance status. One of the following values:
      "PROVISIONING", "STAGING", "RUNNING", "STOPPING", "STOPPED",
      "TERMINATED" (output only).

  Fields:
    canIpForward: Allows this instance to send packets with source IP
      addresses other than its own and receive packets with destination IP
      addresses other than its own. If this instance will be used as an IP
      gateway or it will be set as the next-hop in a Route resource, say true.
      If unsure, leave this set to false.
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    disks: Array of disks associated with this instance. Persistent disks must
      be created before you can assign them.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    machineType: URL of the machine type resource describing which machine
      type to use to host the instance; provided by the client when the
      instance is created.
    metadata: Metadata key/value pairs assigned to this instance. Consists of
      custom metadata or predefined keys; see Instance documentation for more
      information.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    networkInterfaces: Array of configurations for this interface. This
      specifies how this interface is configured to interact with other
      network services, such as connecting to the internet. Currently,
      ONE_TO_ONE_NAT is the only access config supported. If there are no
      accessConfigs specified, then this instance will have no external
      internet access.
    scheduling: Scheduling options for this instance.
    selfLink: Server defined URL for this resource (output only).
    serviceAccounts: A list of service accounts each with specified scopes,
      for which access tokens are to be made available to the instance through
      metadata queries.
    status: Instance status. One of the following values: "PROVISIONING",
      "STAGING", "RUNNING", "STOPPING", "STOPPED", "TERMINATED" (output only).
    statusMessage: An optional, human-readable explanation of the status
      (output only).
    tags: A list of tags to be applied to this instance. Used to identify
      valid sources or targets for network firewalls. Provided by the client
      on instance creation. The tags can be later modified by the setTags
      method. Each tag within the list must comply with RFC1035.
    zone: URL of the zone where the instance resides (output only).
  """

  class StatusValueValuesEnum(messages.Enum):
    """Instance status. One of the following values: "PROVISIONING",
    "STAGING", "RUNNING", "STOPPING", "STOPPED", "TERMINATED" (output only).

    Values:
      PROVISIONING: <no description>
      RUNNING: <no description>
      STAGING: <no description>
      STOPPED: <no description>
      STOPPING: <no description>
      TERMINATED: <no description>
    """
    PROVISIONING = 0
    RUNNING = 1
    STAGING = 2
    STOPPED = 3
    STOPPING = 4
    TERMINATED = 5

  canIpForward = messages.BooleanField(1)
  creationTimestamp = messages.StringField(2)
  description = messages.StringField(3)
  disks = messages.MessageField('AttachedDisk', 4, repeated=True)
  id = messages.IntegerField(5, variant=messages.Variant.UINT64)
  kind = messages.StringField(6, default=u'compute#instance')
  machineType = messages.StringField(7)
  metadata = messages.MessageField('Metadata', 8)
  name = messages.StringField(9)
  networkInterfaces = messages.MessageField('NetworkInterface', 10, repeated=True)
  scheduling = messages.MessageField('Scheduling', 11)
  selfLink = messages.StringField(12)
  serviceAccounts = messages.MessageField('ServiceAccount', 13, repeated=True)
  status = messages.EnumField('StatusValueValuesEnum', 14)
  statusMessage = messages.StringField(15)
  tags = messages.MessageField('Tags', 16)
  zone = messages.StringField(17)


class InstanceAggregatedList(messages.Message):
  """A InstanceAggregatedList object.

  Messages:
    ItemsValue: A map of scoped instance lists.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A map of scoped instance lists.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ItemsValue(messages.Message):
    """A map of scoped instance lists.

    Messages:
      AdditionalProperty: An additional property for a ItemsValue object.

    Fields:
      additionalProperties: Name of the scope containing this set of
        instances.
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a ItemsValue object.

      Fields:
        key: Name of the additional property.
        value: A InstancesScopedList attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('InstancesScopedList', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  id = messages.StringField(1)
  items = messages.MessageField('ItemsValue', 2)
  kind = messages.StringField(3, default=u'compute#instanceAggregatedList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class InstanceList(messages.Message):
  """Contains a list of instance resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of Instance resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('Instance', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#instanceList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class InstanceProperties(messages.Message):
  """InstanceProperties message type.

  Fields:
    canIpForward: Allows instances created based on this template to send
      packets with source IP addresses other than their own and receive
      packets with destination IP addresses other than their own. If these
      instances will be used as an IP gateway or it will be set as the next-
      hop in a Route resource, say true. If unsure, leave this set to false.
    description: An optional textual description for the instances created
      based on the instance template resource; provided by the client when the
      template is created.
    disks: Array of disks associated with instance created based on this
      template.
    machineType: Name of the machine type resource describing which machine
      type to use to host the instances created based on this template;
      provided by the client when the instance template is created.
    metadata: Metadata key/value pairs assigned to instances created based on
      this template. Consists of custom metadata or predefined keys; see
      Instance documentation for more information.
    networkInterfaces: Array of configurations for this interface. This
      specifies how this interface is configured to interact with other
      network services, such as connecting to the internet. Currently,
      ONE_TO_ONE_NAT is the only access config supported. If there are no
      accessConfigs specified, then this instances created based based on this
      template will have no external internet access.
    scheduling: Scheduling options for the instances created based on this
      template.
    serviceAccounts: A list of service accounts each with specified scopes,
      for which access tokens are to be made available to the instances
      created based on this template, through metadata queries.
    tags: A list of tags to be applied to the instances created based on this
      template used to identify valid sources or targets for network
      firewalls. Provided by the client on instance creation. The tags can be
      later modified by the setTags method. Each tag within the list must
      comply with RFC1035.
  """

  canIpForward = messages.BooleanField(1)
  description = messages.StringField(2)
  disks = messages.MessageField('AttachedDisk', 3, repeated=True)
  machineType = messages.StringField(4)
  metadata = messages.MessageField('Metadata', 5)
  networkInterfaces = messages.MessageField('NetworkInterface', 6, repeated=True)
  scheduling = messages.MessageField('Scheduling', 7)
  serviceAccounts = messages.MessageField('ServiceAccount', 8, repeated=True)
  tags = messages.MessageField('Tags', 9)


class InstanceReference(messages.Message):
  """A InstanceReference object.

  Fields:
    instance: A string attribute.
  """

  instance = messages.StringField(1)


class InstanceTemplate(messages.Message):
  """An Instance Template resource.

  Fields:
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the instance template
      resource; provided by the client when the resource is created.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    name: Name of the instance template resource; provided by the client when
      the resource is created. The name must be 1-63 characters long, and
      comply with RFC1035
    properties: The instance properties portion of this instance template
      resource.
    selfLink: Server defined URL for the resource (output only).
  """

  creationTimestamp = messages.StringField(1)
  description = messages.StringField(2)
  id = messages.IntegerField(3, variant=messages.Variant.UINT64)
  kind = messages.StringField(4, default=u'compute#instanceTemplate')
  name = messages.StringField(5)
  properties = messages.MessageField('InstanceProperties', 6)
  selfLink = messages.StringField(7)


class InstanceTemplateList(messages.Message):
  """Contains a list of instance template resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of InstanceTemplate resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('InstanceTemplate', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#instanceTemplateList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class InstancesScopedList(messages.Message):
  """A InstancesScopedList object.

  Messages:
    WarningValue: Informational warning which replaces the list of instances
      when the list is empty.

  Fields:
    instances: List of instances contained in this scope.
    warning: Informational warning which replaces the list of instances when
      the list is empty.
  """

  class WarningValue(messages.Message):
    """Informational warning which replaces the list of instances when the
    list is empty.

    Enums:
      CodeValueValuesEnum: The warning type identifier for this warning.

    Messages:
      DataValueListEntry: A DataValueListEntry object.

    Fields:
      code: The warning type identifier for this warning.
      data: Metadata for this warning in 'key: value' format.
      message: Optional human-readable details for this warning.
    """

    class CodeValueValuesEnum(messages.Enum):
      """The warning type identifier for this warning.

      Values:
        DEPRECATED_RESOURCE_USED: <no description>
        DISK_SIZE_LARGER_THAN_IMAGE_SIZE: <no description>
        INJECTED_KERNELS_DEPRECATED: <no description>
        NEXT_HOP_ADDRESS_NOT_ASSIGNED: <no description>
        NEXT_HOP_CANNOT_IP_FORWARD: <no description>
        NEXT_HOP_INSTANCE_NOT_FOUND: <no description>
        NEXT_HOP_INSTANCE_NOT_ON_NETWORK: <no description>
        NEXT_HOP_NOT_RUNNING: <no description>
        NO_RESULTS_ON_PAGE: <no description>
        REQUIRED_TOS_AGREEMENT: <no description>
        RESOURCE_NOT_DELETED: <no description>
        UNREACHABLE: <no description>
      """
      DEPRECATED_RESOURCE_USED = 0
      DISK_SIZE_LARGER_THAN_IMAGE_SIZE = 1
      INJECTED_KERNELS_DEPRECATED = 2
      NEXT_HOP_ADDRESS_NOT_ASSIGNED = 3
      NEXT_HOP_CANNOT_IP_FORWARD = 4
      NEXT_HOP_INSTANCE_NOT_FOUND = 5
      NEXT_HOP_INSTANCE_NOT_ON_NETWORK = 6
      NEXT_HOP_NOT_RUNNING = 7
      NO_RESULTS_ON_PAGE = 8
      REQUIRED_TOS_AGREEMENT = 9
      RESOURCE_NOT_DELETED = 10
      UNREACHABLE = 11

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: A key for the warning data.
        value: A warning data value corresponding to the key.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.EnumField('CodeValueValuesEnum', 1)
    data = messages.MessageField('DataValueListEntry', 2, repeated=True)
    message = messages.StringField(3)

  instances = messages.MessageField('Instance', 1, repeated=True)
  warning = messages.MessageField('WarningValue', 2)


class License(messages.Message):
  """A license resource.

  Fields:
    chargesUseFee: If true, the customer will be charged license fee for
      running software that contains this license on an instance.
    kind: Type of resource.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    selfLink: Server defined URL for the resource (output only).
  """

  chargesUseFee = messages.BooleanField(1)
  kind = messages.StringField(2, default=u'compute#license')
  name = messages.StringField(3)
  selfLink = messages.StringField(4)


class MachineType(messages.Message):
  """A machine type resource.

  Messages:
    ScratchDisksValueListEntry: A ScratchDisksValueListEntry object.

  Fields:
    creationTimestamp: [Output Only] Creation timestamp in RFC3339 text
      format.
    deprecated: The deprecation status associated with this machine type.
    description: An optional textual description of the resource.
    guestCpus: Count of CPUs exposed to the instance.
    id: [Output Only] Unique identifier for the resource; defined by the
      server.
    imageSpaceGb: Space allotted for the image, defined in GB.
    kind: Type of the resource.
    maximumPersistentDisks: Maximum persistent disks allowed.
    maximumPersistentDisksSizeGb: Maximum total persistent disks size (GB)
      allowed.
    memoryMb: Physical memory assigned to the instance, defined in MB.
    name: Name of the resource.
    scratchDisks: List of extended scratch disks assigned to the instance.
    selfLink: [Output Only] Server defined URL for the resource.
    zone: [Output Only] The name of the zone where the machine type resides,
      such as us-central1-a.
  """

  class ScratchDisksValueListEntry(messages.Message):
    """A ScratchDisksValueListEntry object.

    Fields:
      diskGb: Size of the scratch disk, defined in GB.
    """

    diskGb = messages.IntegerField(1, variant=messages.Variant.INT32)

  creationTimestamp = messages.StringField(1)
  deprecated = messages.MessageField('DeprecationStatus', 2)
  description = messages.StringField(3)
  guestCpus = messages.IntegerField(4, variant=messages.Variant.INT32)
  id = messages.IntegerField(5, variant=messages.Variant.UINT64)
  imageSpaceGb = messages.IntegerField(6, variant=messages.Variant.INT32)
  kind = messages.StringField(7, default=u'compute#machineType')
  maximumPersistentDisks = messages.IntegerField(8, variant=messages.Variant.INT32)
  maximumPersistentDisksSizeGb = messages.IntegerField(9)
  memoryMb = messages.IntegerField(10, variant=messages.Variant.INT32)
  name = messages.StringField(11)
  scratchDisks = messages.MessageField('ScratchDisksValueListEntry', 12, repeated=True)
  selfLink = messages.StringField(13)
  zone = messages.StringField(14)


class MachineTypeAggregatedList(messages.Message):
  """A MachineTypeAggregatedList object.

  Messages:
    ItemsValue: A map of scoped machine type lists.

  Fields:
    id: [Output Only] Unique identifier for the resource; defined by the
      server.
    items: A map of scoped machine type lists.
    kind: Type of resource.
    nextPageToken: [Output Only] A token used to continue a truncated list
      request.
    selfLink: Server defined URL for this resource (output only).
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ItemsValue(messages.Message):
    """A map of scoped machine type lists.

    Messages:
      AdditionalProperty: An additional property for a ItemsValue object.

    Fields:
      additionalProperties: Name of the scope containing this set of machine
        types.
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a ItemsValue object.

      Fields:
        key: Name of the additional property.
        value: A MachineTypesScopedList attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('MachineTypesScopedList', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  id = messages.StringField(1)
  items = messages.MessageField('ItemsValue', 2)
  kind = messages.StringField(3, default=u'compute#machineTypeAggregatedList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class MachineTypeList(messages.Message):
  """Contains a list of machine type resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of MachineType resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('MachineType', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#machineTypeList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class MachineTypesScopedList(messages.Message):
  """A MachineTypesScopedList object.

  Messages:
    WarningValue: An informational warning that appears when the machine types
      list is empty.

  Fields:
    machineTypes: List of machine types contained in this scope.
    warning: An informational warning that appears when the machine types list
      is empty.
  """

  class WarningValue(messages.Message):
    """An informational warning that appears when the machine types list is
    empty.

    Enums:
      CodeValueValuesEnum: The warning type identifier for this warning.

    Messages:
      DataValueListEntry: A DataValueListEntry object.

    Fields:
      code: The warning type identifier for this warning.
      data: Metadata for this warning in 'key: value' format.
      message: Optional human-readable details for this warning.
    """

    class CodeValueValuesEnum(messages.Enum):
      """The warning type identifier for this warning.

      Values:
        DEPRECATED_RESOURCE_USED: <no description>
        DISK_SIZE_LARGER_THAN_IMAGE_SIZE: <no description>
        INJECTED_KERNELS_DEPRECATED: <no description>
        NEXT_HOP_ADDRESS_NOT_ASSIGNED: <no description>
        NEXT_HOP_CANNOT_IP_FORWARD: <no description>
        NEXT_HOP_INSTANCE_NOT_FOUND: <no description>
        NEXT_HOP_INSTANCE_NOT_ON_NETWORK: <no description>
        NEXT_HOP_NOT_RUNNING: <no description>
        NO_RESULTS_ON_PAGE: <no description>
        REQUIRED_TOS_AGREEMENT: <no description>
        RESOURCE_NOT_DELETED: <no description>
        UNREACHABLE: <no description>
      """
      DEPRECATED_RESOURCE_USED = 0
      DISK_SIZE_LARGER_THAN_IMAGE_SIZE = 1
      INJECTED_KERNELS_DEPRECATED = 2
      NEXT_HOP_ADDRESS_NOT_ASSIGNED = 3
      NEXT_HOP_CANNOT_IP_FORWARD = 4
      NEXT_HOP_INSTANCE_NOT_FOUND = 5
      NEXT_HOP_INSTANCE_NOT_ON_NETWORK = 6
      NEXT_HOP_NOT_RUNNING = 7
      NO_RESULTS_ON_PAGE = 8
      REQUIRED_TOS_AGREEMENT = 9
      RESOURCE_NOT_DELETED = 10
      UNREACHABLE = 11

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: A key for the warning data.
        value: A warning data value corresponding to the key.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.EnumField('CodeValueValuesEnum', 1)
    data = messages.MessageField('DataValueListEntry', 2, repeated=True)
    message = messages.StringField(3)

  machineTypes = messages.MessageField('MachineType', 1, repeated=True)
  warning = messages.MessageField('WarningValue', 2)


class Metadata(messages.Message):
  """A metadata key/value entry.

  Messages:
    ItemsValueListEntry: A ItemsValueListEntry object.

  Fields:
    fingerprint: Fingerprint of this resource. A hash of the metadata's
      contents. This field is used for optimistic locking. An up-to-date
      metadata fingerprint must be provided in order to modify metadata.
    items: Array of key/value pairs. The total size of all keys and values
      must be less than 512 KB.
    kind: Type of the resource.
  """

  class ItemsValueListEntry(messages.Message):
    """A ItemsValueListEntry object.

    Fields:
      key: Key for the metadata entry. Keys must conform to the following
        regexp: [a-zA-Z0-9-_]+, and be less than 128 bytes in length. This is
        reflected as part of a URL in the metadata server. Additionally, to
        avoid ambiguity, keys must not conflict with any other metadata keys
        for the project.
      value: Value for the metadata entry. These are free-form strings, and
        only have meaning as interpreted by the image running in the instance.
        The only restriction placed on values is that their size must be less
        than or equal to 32768 bytes.
    """

    key = messages.StringField(1)
    value = messages.StringField(2)

  fingerprint = messages.BytesField(1)
  items = messages.MessageField('ItemsValueListEntry', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#metadata')


class Network(messages.Message):
  """A network resource.

  Fields:
    IPv4Range: Required; The range of internal addresses that are legal on
      this network. This range is a CIDR specification, for example:
      192.168.0.0/16. Provided by the client when the network is created.
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    gatewayIPv4: An optional address that is used for default routing to other
      networks. This must be within the range specified by IPv4Range, and is
      typically the first usable address in that range. If not specified, the
      default value is the first usable address in IPv4Range.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    selfLink: Server defined URL for the resource (output only).
  """

  IPv4Range = messages.StringField(1)
  creationTimestamp = messages.StringField(2)
  description = messages.StringField(3)
  gatewayIPv4 = messages.StringField(4)
  id = messages.IntegerField(5, variant=messages.Variant.UINT64)
  kind = messages.StringField(6, default=u'compute#network')
  name = messages.StringField(7)
  selfLink = messages.StringField(8)


class NetworkInterface(messages.Message):
  """A network interface resource attached to an instance.

  Fields:
    accessConfigs: Array of configurations for this interface. This specifies
      how this interface is configured to interact with other network
      services, such as connecting to the internet. Currently, ONE_TO_ONE_NAT
      is the only access config supported. If there are no accessConfigs
      specified, then this instance will have no external internet access.
    name: Name of the network interface, determined by the server; for network
      devices, these are e.g. eth0, eth1, etc. (output only).
    network: URL of the network resource attached to this interface.
    networkIP: An optional IPV4 internal network address assigned to the
      instance for this network interface (output only).
  """

  accessConfigs = messages.MessageField('AccessConfig', 1, repeated=True)
  name = messages.StringField(2)
  network = messages.StringField(3)
  networkIP = messages.StringField(4)


class NetworkList(messages.Message):
  """Contains a list of network resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of Network resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('Network', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#networkList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class Operation(messages.Message):
  """An operation resource, used to manage asynchronous API requests.

  Enums:
    StatusValueValuesEnum: [Output Only] Status of the operation. Can be one
      of the following: "PENDING", "RUNNING", or "DONE".

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

  class StatusValueValuesEnum(messages.Enum):
    """[Output Only] Status of the operation. Can be one of the following:
    "PENDING", "RUNNING", or "DONE".

    Values:
      DONE: <no description>
      PENDING: <no description>
      RUNNING: <no description>
    """
    DONE = 0
    PENDING = 1
    RUNNING = 2

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

    Enums:
      CodeValueValuesEnum: The warning type identifier for this warning.

    Messages:
      DataValueListEntry: A DataValueListEntry object.

    Fields:
      code: The warning type identifier for this warning.
      data: Metadata for this warning in 'key: value' format.
      message: Optional human-readable details for this warning.
    """

    class CodeValueValuesEnum(messages.Enum):
      """The warning type identifier for this warning.

      Values:
        DEPRECATED_RESOURCE_USED: <no description>
        DISK_SIZE_LARGER_THAN_IMAGE_SIZE: <no description>
        INJECTED_KERNELS_DEPRECATED: <no description>
        NEXT_HOP_ADDRESS_NOT_ASSIGNED: <no description>
        NEXT_HOP_CANNOT_IP_FORWARD: <no description>
        NEXT_HOP_INSTANCE_NOT_FOUND: <no description>
        NEXT_HOP_INSTANCE_NOT_ON_NETWORK: <no description>
        NEXT_HOP_NOT_RUNNING: <no description>
        NO_RESULTS_ON_PAGE: <no description>
        REQUIRED_TOS_AGREEMENT: <no description>
        RESOURCE_NOT_DELETED: <no description>
        UNREACHABLE: <no description>
      """
      DEPRECATED_RESOURCE_USED = 0
      DISK_SIZE_LARGER_THAN_IMAGE_SIZE = 1
      INJECTED_KERNELS_DEPRECATED = 2
      NEXT_HOP_ADDRESS_NOT_ASSIGNED = 3
      NEXT_HOP_CANNOT_IP_FORWARD = 4
      NEXT_HOP_INSTANCE_NOT_FOUND = 5
      NEXT_HOP_INSTANCE_NOT_ON_NETWORK = 6
      NEXT_HOP_NOT_RUNNING = 7
      NO_RESULTS_ON_PAGE = 8
      REQUIRED_TOS_AGREEMENT = 9
      RESOURCE_NOT_DELETED = 10
      UNREACHABLE = 11

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: A key for the warning data.
        value: A warning data value corresponding to the key.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.EnumField('CodeValueValuesEnum', 1)
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
  kind = messages.StringField(9, default=u'compute#operation')
  name = messages.StringField(10)
  operationType = messages.StringField(11)
  progress = messages.IntegerField(12, variant=messages.Variant.INT32)
  region = messages.StringField(13)
  selfLink = messages.StringField(14)
  startTime = messages.StringField(15)
  status = messages.EnumField('StatusValueValuesEnum', 16)
  statusMessage = messages.StringField(17)
  targetId = messages.IntegerField(18, variant=messages.Variant.UINT64)
  targetLink = messages.StringField(19)
  user = messages.StringField(20)
  warnings = messages.MessageField('WarningsValueListEntry', 21, repeated=True)
  zone = messages.StringField(22)


class OperationAggregatedList(messages.Message):
  """A OperationAggregatedList object.

  Messages:
    ItemsValue: [Output Only] A map of scoped operation lists.

  Fields:
    id: [Output Only] Unique identifier for the resource; defined by the
      server.
    items: [Output Only] A map of scoped operation lists.
    kind: Type of resource.
    nextPageToken: [Output Only] A token used to continue a truncated list
      request.
    selfLink: [Output Only] Server defined URL for this resource.
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ItemsValue(messages.Message):
    """[Output Only] A map of scoped operation lists.

    Messages:
      AdditionalProperty: An additional property for a ItemsValue object.

    Fields:
      additionalProperties: [Output Only] Name of the scope containing this
        set of operations.
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a ItemsValue object.

      Fields:
        key: Name of the additional property.
        value: A OperationsScopedList attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('OperationsScopedList', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  id = messages.StringField(1)
  items = messages.MessageField('ItemsValue', 2)
  kind = messages.StringField(3, default=u'compute#operationAggregatedList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class OperationList(messages.Message):
  """Contains a list of operation resources.

  Fields:
    id: [Output Only] Unique identifier for the resource; defined by the
      server.
    items: [Output Only] The operation resources.
    kind: Type of resource. Always compute#operations for Operations resource.
    nextPageToken: [Output Only] A token used to continue a truncate.
    selfLink: [Output Only] Server defined URL for this resource.
  """

  id = messages.StringField(1)
  items = messages.MessageField('Operation', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#operationList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class OperationsScopedList(messages.Message):
  """A OperationsScopedList object.

  Messages:
    WarningValue: [Output Only] Informational warning which replaces the list
      of operations when the list is empty.

  Fields:
    operations: [Output Only] List of operations contained in this scope.
    warning: [Output Only] Informational warning which replaces the list of
      operations when the list is empty.
  """

  class WarningValue(messages.Message):
    """[Output Only] Informational warning which replaces the list of
    operations when the list is empty.

    Enums:
      CodeValueValuesEnum: The warning type identifier for this warning.

    Messages:
      DataValueListEntry: A DataValueListEntry object.

    Fields:
      code: The warning type identifier for this warning.
      data: Metadata for this warning in 'key: value' format.
      message: Optional human-readable details for this warning.
    """

    class CodeValueValuesEnum(messages.Enum):
      """The warning type identifier for this warning.

      Values:
        DEPRECATED_RESOURCE_USED: <no description>
        DISK_SIZE_LARGER_THAN_IMAGE_SIZE: <no description>
        INJECTED_KERNELS_DEPRECATED: <no description>
        NEXT_HOP_ADDRESS_NOT_ASSIGNED: <no description>
        NEXT_HOP_CANNOT_IP_FORWARD: <no description>
        NEXT_HOP_INSTANCE_NOT_FOUND: <no description>
        NEXT_HOP_INSTANCE_NOT_ON_NETWORK: <no description>
        NEXT_HOP_NOT_RUNNING: <no description>
        NO_RESULTS_ON_PAGE: <no description>
        REQUIRED_TOS_AGREEMENT: <no description>
        RESOURCE_NOT_DELETED: <no description>
        UNREACHABLE: <no description>
      """
      DEPRECATED_RESOURCE_USED = 0
      DISK_SIZE_LARGER_THAN_IMAGE_SIZE = 1
      INJECTED_KERNELS_DEPRECATED = 2
      NEXT_HOP_ADDRESS_NOT_ASSIGNED = 3
      NEXT_HOP_CANNOT_IP_FORWARD = 4
      NEXT_HOP_INSTANCE_NOT_FOUND = 5
      NEXT_HOP_INSTANCE_NOT_ON_NETWORK = 6
      NEXT_HOP_NOT_RUNNING = 7
      NO_RESULTS_ON_PAGE = 8
      REQUIRED_TOS_AGREEMENT = 9
      RESOURCE_NOT_DELETED = 10
      UNREACHABLE = 11

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: A key for the warning data.
        value: A warning data value corresponding to the key.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.EnumField('CodeValueValuesEnum', 1)
    data = messages.MessageField('DataValueListEntry', 2, repeated=True)
    message = messages.StringField(3)

  operations = messages.MessageField('Operation', 1, repeated=True)
  warning = messages.MessageField('WarningValue', 2)


class PathMatcher(messages.Message):
  """A matcher for the path portion of the URL. The BackendService from the
  longest-matched rule will serve the URL. If no rule was matched, the
  default_service will be used.

  Fields:
    defaultService: The URL to the BackendService resource. This will be used
      if none of the 'pathRules' defined by this PathMatcher is met by the
      URL's path portion.
    description: A string attribute.
    name: The name to which this PathMatcher is referred by the HostRule.
    pathRules: The list of path rules.
  """

  defaultService = messages.StringField(1)
  description = messages.StringField(2)
  name = messages.StringField(3)
  pathRules = messages.MessageField('PathRule', 4, repeated=True)


class PathRule(messages.Message):
  """A path-matching rule for a URL. If matched, will use the specified
  BackendService to handle the traffic arriving at this URL.

  Fields:
    paths: The list of path patterns to match. Each must start with / and the
      only place a * is allowed is at the end following a /. The string fed to
      the path matcher does not include any text after the first ? or #, and
      those chars are not allowed here.
    service: The URL of the BackendService resource if this rule is matched.
  """

  paths = messages.StringField(1, repeated=True)
  service = messages.StringField(2)


class Project(messages.Message):
  """A project resource. Projects can be created only in the APIs Console.
  Unless marked otherwise, values can only be modified in the console.

  Fields:
    commonInstanceMetadata: Metadata key/value pairs available to all
      instances contained in this project.
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    name: Name of the resource.
    quotas: Quotas assigned to this project.
    selfLink: Server defined URL for the resource (output only).
    usageExportLocation: The location in Cloud Storage and naming method of
      the daily usage report.
  """

  commonInstanceMetadata = messages.MessageField('Metadata', 1)
  creationTimestamp = messages.StringField(2)
  description = messages.StringField(3)
  id = messages.IntegerField(4, variant=messages.Variant.UINT64)
  kind = messages.StringField(5, default=u'compute#project')
  name = messages.StringField(6)
  quotas = messages.MessageField('Quota', 7, repeated=True)
  selfLink = messages.StringField(8)
  usageExportLocation = messages.MessageField('UsageExportLocation', 9)


class Quota(messages.Message):
  """A quotas entry.

  Enums:
    MetricValueValuesEnum: Name of the quota metric.

  Fields:
    limit: Quota limit for this metric.
    metric: Name of the quota metric.
    usage: Current usage of this metric.
  """

  class MetricValueValuesEnum(messages.Enum):
    """Name of the quota metric.

    Values:
      BACKEND_SERVICES: <no description>
      CPUS: <no description>
      DISKS: <no description>
      DISKS_TOTAL_GB: <no description>
      EPHEMERAL_ADDRESSES: <no description>
      FIREWALLS: <no description>
      FORWARDING_RULES: <no description>
      HEALTH_CHECKS: <no description>
      IMAGES: <no description>
      IMAGES_TOTAL_GB: <no description>
      INSTANCES: <no description>
      IN_USE_ADDRESSES: <no description>
      KERNELS: <no description>
      KERNELS_TOTAL_GB: <no description>
      LOCAL_SSD_TOTAL_GB: <no description>
      NETWORKS: <no description>
      OPERATIONS: <no description>
      ROUTES: <no description>
      SNAPSHOTS: <no description>
      SSD_TOTAL_GB: <no description>
      STATIC_ADDRESSES: <no description>
      TARGET_HTTP_PROXIES: <no description>
      TARGET_INSTANCES: <no description>
      TARGET_POOLS: <no description>
      URL_MAPS: <no description>
    """
    BACKEND_SERVICES = 0
    CPUS = 1
    DISKS = 2
    DISKS_TOTAL_GB = 3
    EPHEMERAL_ADDRESSES = 4
    FIREWALLS = 5
    FORWARDING_RULES = 6
    HEALTH_CHECKS = 7
    IMAGES = 8
    IMAGES_TOTAL_GB = 9
    INSTANCES = 10
    IN_USE_ADDRESSES = 11
    KERNELS = 12
    KERNELS_TOTAL_GB = 13
    LOCAL_SSD_TOTAL_GB = 14
    NETWORKS = 15
    OPERATIONS = 16
    ROUTES = 17
    SNAPSHOTS = 18
    SSD_TOTAL_GB = 19
    STATIC_ADDRESSES = 20
    TARGET_HTTP_PROXIES = 21
    TARGET_INSTANCES = 22
    TARGET_POOLS = 23
    URL_MAPS = 24

  limit = messages.FloatField(1)
  metric = messages.EnumField('MetricValueValuesEnum', 2)
  usage = messages.FloatField(3)


class Region(messages.Message):
  """Region resource.

  Enums:
    StatusValueValuesEnum: Status of the region, "UP" or "DOWN".

  Fields:
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    deprecated: The deprecation status associated with this region.
    description: Textual description of the resource.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    name: Name of the resource.
    quotas: Quotas assigned to this region.
    selfLink: Server defined URL for the resource (output only).
    status: Status of the region, "UP" or "DOWN".
    zones: A list of zones homed in this region, in the form of resource URLs.
  """

  class StatusValueValuesEnum(messages.Enum):
    """Status of the region, "UP" or "DOWN".

    Values:
      DOWN: <no description>
      UP: <no description>
    """
    DOWN = 0
    UP = 1

  creationTimestamp = messages.StringField(1)
  deprecated = messages.MessageField('DeprecationStatus', 2)
  description = messages.StringField(3)
  id = messages.IntegerField(4, variant=messages.Variant.UINT64)
  kind = messages.StringField(5, default=u'compute#region')
  name = messages.StringField(6)
  quotas = messages.MessageField('Quota', 7, repeated=True)
  selfLink = messages.StringField(8)
  status = messages.EnumField('StatusValueValuesEnum', 9)
  zones = messages.StringField(10, repeated=True)


class RegionList(messages.Message):
  """Contains a list of region resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of Region resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('Region', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#regionList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class ResourceGroupReference(messages.Message):
  """A ResourceGroupReference object.

  Fields:
    group: A URI referencing one of the resource views listed in the backend
      service.
  """

  group = messages.StringField(1)


class Route(messages.Message):
  """The route resource. A Route is a rule that specifies how certain packets
  should be handled by the virtual network. Routes are associated with VMs by
  tag and the set of Routes for a particular VM is called its routing table.
  For each packet leaving a VM, the system searches that VM's routing table
  for a single best matching Route. Routes match packets by destination IP
  address, preferring smaller or more specific ranges over larger ones. If
  there is a tie, the system selects the Route with the smallest priority
  value. If there is still a tie, it uses the layer three and four packet
  headers to select just one of the remaining matching Routes. The packet is
  then forwarded as specified by the next_hop field of the winning Route --
  either to another VM destination, a VM gateway or a GCE operated gateway.
  Packets that do not match any Route in the sending VM's routing table will
  be dropped.

  Messages:
    WarningsValueListEntry: A WarningsValueListEntry object.

  Fields:
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    destRange: Which packets does this route apply to?
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    network: URL of the network to which this route is applied; provided by
      the client when the route is created.
    nextHopGateway: The URL to a gateway that should handle matching packets.
    nextHopInstance: The URL to an instance that should handle matching
      packets.
    nextHopIp: The network IP address of an instance that should handle
      matching packets.
    nextHopNetwork: The URL of the local network if it should handle matching
      packets.
    priority: Breaks ties between Routes of equal specificity. Routes with
      smaller values win when tied with routes with larger values.
    selfLink: Server defined URL for the resource (output only).
    tags: A list of instance tags to which this route applies.
    warnings: If potential misconfigurations are detected for this route, this
      field will be populated with warning messages.
  """

  class WarningsValueListEntry(messages.Message):
    """A WarningsValueListEntry object.

    Enums:
      CodeValueValuesEnum: The warning type identifier for this warning.

    Messages:
      DataValueListEntry: A DataValueListEntry object.

    Fields:
      code: The warning type identifier for this warning.
      data: Metadata for this warning in 'key: value' format.
      message: Optional human-readable details for this warning.
    """

    class CodeValueValuesEnum(messages.Enum):
      """The warning type identifier for this warning.

      Values:
        DEPRECATED_RESOURCE_USED: <no description>
        DISK_SIZE_LARGER_THAN_IMAGE_SIZE: <no description>
        INJECTED_KERNELS_DEPRECATED: <no description>
        NEXT_HOP_ADDRESS_NOT_ASSIGNED: <no description>
        NEXT_HOP_CANNOT_IP_FORWARD: <no description>
        NEXT_HOP_INSTANCE_NOT_FOUND: <no description>
        NEXT_HOP_INSTANCE_NOT_ON_NETWORK: <no description>
        NEXT_HOP_NOT_RUNNING: <no description>
        NO_RESULTS_ON_PAGE: <no description>
        REQUIRED_TOS_AGREEMENT: <no description>
        RESOURCE_NOT_DELETED: <no description>
        UNREACHABLE: <no description>
      """
      DEPRECATED_RESOURCE_USED = 0
      DISK_SIZE_LARGER_THAN_IMAGE_SIZE = 1
      INJECTED_KERNELS_DEPRECATED = 2
      NEXT_HOP_ADDRESS_NOT_ASSIGNED = 3
      NEXT_HOP_CANNOT_IP_FORWARD = 4
      NEXT_HOP_INSTANCE_NOT_FOUND = 5
      NEXT_HOP_INSTANCE_NOT_ON_NETWORK = 6
      NEXT_HOP_NOT_RUNNING = 7
      NO_RESULTS_ON_PAGE = 8
      REQUIRED_TOS_AGREEMENT = 9
      RESOURCE_NOT_DELETED = 10
      UNREACHABLE = 11

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: A key for the warning data.
        value: A warning data value corresponding to the key.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.EnumField('CodeValueValuesEnum', 1)
    data = messages.MessageField('DataValueListEntry', 2, repeated=True)
    message = messages.StringField(3)

  creationTimestamp = messages.StringField(1)
  description = messages.StringField(2)
  destRange = messages.StringField(3)
  id = messages.IntegerField(4, variant=messages.Variant.UINT64)
  kind = messages.StringField(5, default=u'compute#route')
  name = messages.StringField(6)
  network = messages.StringField(7)
  nextHopGateway = messages.StringField(8)
  nextHopInstance = messages.StringField(9)
  nextHopIp = messages.StringField(10)
  nextHopNetwork = messages.StringField(11)
  priority = messages.IntegerField(12, variant=messages.Variant.UINT32)
  selfLink = messages.StringField(13)
  tags = messages.StringField(14, repeated=True)
  warnings = messages.MessageField('WarningsValueListEntry', 15, repeated=True)


class RouteList(messages.Message):
  """Contains a list of route resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of Route resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('Route', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#routeList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class Scheduling(messages.Message):
  """Scheduling options for an Instance.

  Enums:
    OnHostMaintenanceValueValuesEnum: How the instance should behave when the
      host machine undergoes maintenance that may temporarily impact instance
      performance.

  Fields:
    automaticRestart: Whether the Instance should be automatically restarted
      whenever it is terminated by Compute Engine (not terminated by user).
    onHostMaintenance: How the instance should behave when the host machine
      undergoes maintenance that may temporarily impact instance performance.
  """

  class OnHostMaintenanceValueValuesEnum(messages.Enum):
    """How the instance should behave when the host machine undergoes
    maintenance that may temporarily impact instance performance.

    Values:
      MIGRATE: <no description>
      TERMINATE: <no description>
    """
    MIGRATE = 0
    TERMINATE = 1

  automaticRestart = messages.BooleanField(1)
  onHostMaintenance = messages.EnumField('OnHostMaintenanceValueValuesEnum', 2)


class SerialPortOutput(messages.Message):
  """An instance serial console output.

  Fields:
    contents: The contents of the console output.
    kind: Type of the resource.
    selfLink: Server defined URL for the resource (output only).
  """

  contents = messages.StringField(1)
  kind = messages.StringField(2, default=u'compute#serialPortOutput')
  selfLink = messages.StringField(3)


class ServiceAccount(messages.Message):
  """A service account.

  Fields:
    email: Email address of the service account.
    scopes: The list of scopes to be made available for this service account.
  """

  email = messages.StringField(1)
  scopes = messages.StringField(2, repeated=True)


class Snapshot(messages.Message):
  """A persistent disk snapshot resource.

  Enums:
    StatusValueValuesEnum: The status of the persistent disk snapshot (output
      only).
    StorageBytesStatusValueValuesEnum: An indicator whether storageBytes is in
      a stable state, or it is being adjusted as a result of shared storage
      reallocation.

  Fields:
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    diskSizeGb: Size of the persistent disk snapshot, specified in GB (output
      only).
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    licenses: Public visible licenses.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    selfLink: Server defined URL for the resource (output only).
    sourceDisk: The source disk used to create this snapshot.
    sourceDiskId: The 'id' value of the disk used to create this snapshot.
      This value may be used to determine whether the snapshot was taken from
      the current or a previous instance of a given disk name.
    status: The status of the persistent disk snapshot (output only).
    storageBytes: A size of the the storage used by the snapshot. As snapshots
      share storage this number is expected to change with snapshot
      creation/deletion.
    storageBytesStatus: An indicator whether storageBytes is in a stable
      state, or it is being adjusted as a result of shared storage
      reallocation.
  """

  class StatusValueValuesEnum(messages.Enum):
    """The status of the persistent disk snapshot (output only).

    Values:
      CREATING: <no description>
      DELETING: <no description>
      FAILED: <no description>
      READY: <no description>
      UPLOADING: <no description>
    """
    CREATING = 0
    DELETING = 1
    FAILED = 2
    READY = 3
    UPLOADING = 4

  class StorageBytesStatusValueValuesEnum(messages.Enum):
    """An indicator whether storageBytes is in a stable state, or it is being
    adjusted as a result of shared storage reallocation.

    Values:
      UPDATING: <no description>
      UP_TO_DATE: <no description>
    """
    UPDATING = 0
    UP_TO_DATE = 1

  creationTimestamp = messages.StringField(1)
  description = messages.StringField(2)
  diskSizeGb = messages.IntegerField(3)
  id = messages.IntegerField(4, variant=messages.Variant.UINT64)
  kind = messages.StringField(5, default=u'compute#snapshot')
  licenses = messages.StringField(6, repeated=True)
  name = messages.StringField(7)
  selfLink = messages.StringField(8)
  sourceDisk = messages.StringField(9)
  sourceDiskId = messages.StringField(10)
  status = messages.EnumField('StatusValueValuesEnum', 11)
  storageBytes = messages.IntegerField(12)
  storageBytesStatus = messages.EnumField('StorageBytesStatusValueValuesEnum', 13)


class SnapshotList(messages.Message):
  """Contains a list of persistent disk snapshot resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of Snapshot resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('Snapshot', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#snapshotList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


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


class Tags(messages.Message):
  """A set of instance tags.

  Fields:
    fingerprint: Fingerprint of this resource. A hash of the tags stored in
      this object. This field is used optimistic locking. An up-to-date tags
      fingerprint must be provided in order to modify tags.
    items: An array of tags. Each tag must be 1-63 characters long, and comply
      with RFC1035.
  """

  fingerprint = messages.BytesField(1)
  items = messages.StringField(2, repeated=True)


class TargetHttpProxy(messages.Message):
  """A TargetHttpProxy resource. This resource defines an HTTP proxy.

  Fields:
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    selfLink: Server defined URL for the resource (output only).
    urlMap: URL to the UrlMap resource that defines the mapping from URL to
      the BackendService.
  """

  creationTimestamp = messages.StringField(1)
  description = messages.StringField(2)
  id = messages.IntegerField(3, variant=messages.Variant.UINT64)
  kind = messages.StringField(4, default=u'compute#targetHttpProxy')
  name = messages.StringField(5)
  selfLink = messages.StringField(6)
  urlMap = messages.StringField(7)


class TargetHttpProxyList(messages.Message):
  """Contains a list of TargetHttpProxy resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of TargetHttpProxy resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('TargetHttpProxy', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#targetHttpProxyList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class TargetInstance(messages.Message):
  """A TargetInstance resource. This resource defines an endpoint VM that
  terminates traffic of certain protocols.

  Enums:
    NatPolicyValueValuesEnum: NAT option controlling how IPs are NAT'ed to the
      VM. Currently only NO_NAT (default value) is supported.

  Fields:
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    id: Unique identifier for the resource; defined by the server (output
      only).
    instance: The URL to the instance that terminates the relevant traffic.
    kind: Type of the resource.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    natPolicy: NAT option controlling how IPs are NAT'ed to the VM. Currently
      only NO_NAT (default value) is supported.
    selfLink: Server defined URL for the resource (output only).
    zone: URL of the zone where the target instance resides (output only).
  """

  class NatPolicyValueValuesEnum(messages.Enum):
    """NAT option controlling how IPs are NAT'ed to the VM. Currently only
    NO_NAT (default value) is supported.

    Values:
      NO_NAT: <no description>
    """
    NO_NAT = 0

  creationTimestamp = messages.StringField(1)
  description = messages.StringField(2)
  id = messages.IntegerField(3, variant=messages.Variant.UINT64)
  instance = messages.StringField(4)
  kind = messages.StringField(5, default=u'compute#targetInstance')
  name = messages.StringField(6)
  natPolicy = messages.EnumField('NatPolicyValueValuesEnum', 7)
  selfLink = messages.StringField(8)
  zone = messages.StringField(9)


class TargetInstanceAggregatedList(messages.Message):
  """A TargetInstanceAggregatedList object.

  Messages:
    ItemsValue: A map of scoped target instance lists.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A map of scoped target instance lists.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ItemsValue(messages.Message):
    """A map of scoped target instance lists.

    Messages:
      AdditionalProperty: An additional property for a ItemsValue object.

    Fields:
      additionalProperties: Name of the scope containing this set of target
        instances.
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a ItemsValue object.

      Fields:
        key: Name of the additional property.
        value: A TargetInstancesScopedList attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('TargetInstancesScopedList', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  id = messages.StringField(1)
  items = messages.MessageField('ItemsValue', 2)
  kind = messages.StringField(3, default=u'compute#targetInstanceAggregatedList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class TargetInstanceList(messages.Message):
  """Contains a list of TargetInstance resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of TargetInstance resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('TargetInstance', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#targetInstanceList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class TargetInstancesScopedList(messages.Message):
  """A TargetInstancesScopedList object.

  Messages:
    WarningValue: Informational warning which replaces the list of addresses
      when the list is empty.

  Fields:
    targetInstances: List of target instances contained in this scope.
    warning: Informational warning which replaces the list of addresses when
      the list is empty.
  """

  class WarningValue(messages.Message):
    """Informational warning which replaces the list of addresses when the
    list is empty.

    Enums:
      CodeValueValuesEnum: The warning type identifier for this warning.

    Messages:
      DataValueListEntry: A DataValueListEntry object.

    Fields:
      code: The warning type identifier for this warning.
      data: Metadata for this warning in 'key: value' format.
      message: Optional human-readable details for this warning.
    """

    class CodeValueValuesEnum(messages.Enum):
      """The warning type identifier for this warning.

      Values:
        DEPRECATED_RESOURCE_USED: <no description>
        DISK_SIZE_LARGER_THAN_IMAGE_SIZE: <no description>
        INJECTED_KERNELS_DEPRECATED: <no description>
        NEXT_HOP_ADDRESS_NOT_ASSIGNED: <no description>
        NEXT_HOP_CANNOT_IP_FORWARD: <no description>
        NEXT_HOP_INSTANCE_NOT_FOUND: <no description>
        NEXT_HOP_INSTANCE_NOT_ON_NETWORK: <no description>
        NEXT_HOP_NOT_RUNNING: <no description>
        NO_RESULTS_ON_PAGE: <no description>
        REQUIRED_TOS_AGREEMENT: <no description>
        RESOURCE_NOT_DELETED: <no description>
        UNREACHABLE: <no description>
      """
      DEPRECATED_RESOURCE_USED = 0
      DISK_SIZE_LARGER_THAN_IMAGE_SIZE = 1
      INJECTED_KERNELS_DEPRECATED = 2
      NEXT_HOP_ADDRESS_NOT_ASSIGNED = 3
      NEXT_HOP_CANNOT_IP_FORWARD = 4
      NEXT_HOP_INSTANCE_NOT_FOUND = 5
      NEXT_HOP_INSTANCE_NOT_ON_NETWORK = 6
      NEXT_HOP_NOT_RUNNING = 7
      NO_RESULTS_ON_PAGE = 8
      REQUIRED_TOS_AGREEMENT = 9
      RESOURCE_NOT_DELETED = 10
      UNREACHABLE = 11

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: A key for the warning data.
        value: A warning data value corresponding to the key.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.EnumField('CodeValueValuesEnum', 1)
    data = messages.MessageField('DataValueListEntry', 2, repeated=True)
    message = messages.StringField(3)

  targetInstances = messages.MessageField('TargetInstance', 1, repeated=True)
  warning = messages.MessageField('WarningValue', 2)


class TargetPool(messages.Message):
  """A TargetPool resource. This resource defines a pool of VMs, associated
  HttpHealthCheck resources, and the fallback TargetPool.

  Enums:
    SessionAffinityValueValuesEnum: Sesssion affinity option, must be one of
      the following values: 'NONE': Connections from the same client IP may go
      to any VM in the pool; 'CLIENT_IP': Connections from the same client IP
      will go to the same VM in the pool while that VM remains healthy.
      'CLIENT_IP_PROTO': Connections from the same client IP with the same IP
      protocol will go to the same VM in the pool while that VM remains
      healthy.

  Fields:
    backupPool: This field is applicable only when the containing target pool
      is serving a forwarding rule as the primary pool, and its
      'failoverRatio' field is properly set to a value between [0, 1].
      'backupPool' and 'failoverRatio' together define the fallback behavior
      of the primary target pool: if the ratio of the healthy VMs in the
      primary pool is at or below 'failoverRatio', traffic arriving at the
      load-balanced IP will be directed to the backup pool.  In case where
      'failoverRatio' and 'backupPool' are not set, or all the VMs in the
      backup pool are unhealthy, the traffic will be directed back to the
      primary pool in the "force" mode, where traffic will be spread to the
      healthy VMs with the best effort, or to all VMs when no VM is healthy.
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    failoverRatio: This field is applicable only when the containing target
      pool is serving a forwarding rule as the primary pool (i.e., not as a
      backup pool to some other target pool). The value of the field must be
      in [0, 1].  If set, 'backupPool' must also be set. They together define
      the fallback behavior of the primary target pool: if the ratio of the
      healthy VMs in the primary pool is at or below this number, traffic
      arriving at the load-balanced IP will be directed to the backup pool.
      In case where 'failoverRatio' is not set or all the VMs in the backup
      pool are unhealthy, the traffic will be directed back to the primary
      pool in the "force" mode, where traffic will be spread to the healthy
      VMs with the best effort, or to all VMs when no VM is healthy.
    healthChecks: A list of URLs to the HttpHealthCheck resource. A member VM
      in this pool is considered healthy if and only if all specified health
      checks pass. An empty list means all member VMs will be considered
      healthy at all times.
    id: Unique identifier for the resource; defined by the server (output
      only).
    instances: A list of resource URLs to the member VMs serving this pool.
      They must live in zones contained in the same region as this pool.
    kind: Type of the resource.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    region: URL of the region where the target pool resides (output only).
    selfLink: Server defined URL for the resource (output only).
    sessionAffinity: Sesssion affinity option, must be one of the following
      values: 'NONE': Connections from the same client IP may go to any VM in
      the pool; 'CLIENT_IP': Connections from the same client IP will go to
      the same VM in the pool while that VM remains healthy.
      'CLIENT_IP_PROTO': Connections from the same client IP with the same IP
      protocol will go to the same VM in the pool while that VM remains
      healthy.
  """

  class SessionAffinityValueValuesEnum(messages.Enum):
    """Sesssion affinity option, must be one of the following values: 'NONE':
    Connections from the same client IP may go to any VM in the pool;
    'CLIENT_IP': Connections from the same client IP will go to the same VM in
    the pool while that VM remains healthy. 'CLIENT_IP_PROTO': Connections
    from the same client IP with the same IP protocol will go to the same VM
    in the pool while that VM remains healthy.

    Values:
      CLIENT_IP: <no description>
      CLIENT_IP_PROTO: <no description>
      NONE: <no description>
    """
    CLIENT_IP = 0
    CLIENT_IP_PROTO = 1
    NONE = 2

  backupPool = messages.StringField(1)
  creationTimestamp = messages.StringField(2)
  description = messages.StringField(3)
  failoverRatio = messages.FloatField(4, variant=messages.Variant.FLOAT)
  healthChecks = messages.StringField(5, repeated=True)
  id = messages.IntegerField(6, variant=messages.Variant.UINT64)
  instances = messages.StringField(7, repeated=True)
  kind = messages.StringField(8, default=u'compute#targetPool')
  name = messages.StringField(9)
  region = messages.StringField(10)
  selfLink = messages.StringField(11)
  sessionAffinity = messages.EnumField('SessionAffinityValueValuesEnum', 12)


class TargetPoolAggregatedList(messages.Message):
  """A TargetPoolAggregatedList object.

  Messages:
    ItemsValue: A map of scoped target pool lists.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A map of scoped target pool lists.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  @encoding.MapUnrecognizedFields('additionalProperties')
  class ItemsValue(messages.Message):
    """A map of scoped target pool lists.

    Messages:
      AdditionalProperty: An additional property for a ItemsValue object.

    Fields:
      additionalProperties: Name of the scope containing this set of target
        pools.
    """

    class AdditionalProperty(messages.Message):
      """An additional property for a ItemsValue object.

      Fields:
        key: Name of the additional property.
        value: A TargetPoolsScopedList attribute.
      """

      key = messages.StringField(1)
      value = messages.MessageField('TargetPoolsScopedList', 2)

    additionalProperties = messages.MessageField('AdditionalProperty', 1, repeated=True)

  id = messages.StringField(1)
  items = messages.MessageField('ItemsValue', 2)
  kind = messages.StringField(3, default=u'compute#targetPoolAggregatedList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class TargetPoolInstanceHealth(messages.Message):
  """A TargetPoolInstanceHealth object.

  Fields:
    healthStatus: A HealthStatus attribute.
    kind: Type of resource.
  """

  healthStatus = messages.MessageField('HealthStatus', 1, repeated=True)
  kind = messages.StringField(2, default=u'compute#targetPoolInstanceHealth')


class TargetPoolList(messages.Message):
  """Contains a list of TargetPool resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of TargetPool resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('TargetPool', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#targetPoolList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class TargetPoolsAddHealthCheckRequest(messages.Message):
  """A TargetPoolsAddHealthCheckRequest object.

  Fields:
    healthChecks: Health check URLs to be added to targetPool.
  """

  healthChecks = messages.MessageField('HealthCheckReference', 1, repeated=True)


class TargetPoolsAddInstanceRequest(messages.Message):
  """A TargetPoolsAddInstanceRequest object.

  Fields:
    instances: URLs of the instances to be added to targetPool.
  """

  instances = messages.MessageField('InstanceReference', 1, repeated=True)


class TargetPoolsRemoveHealthCheckRequest(messages.Message):
  """A TargetPoolsRemoveHealthCheckRequest object.

  Fields:
    healthChecks: Health check URLs to be removed from targetPool.
  """

  healthChecks = messages.MessageField('HealthCheckReference', 1, repeated=True)


class TargetPoolsRemoveInstanceRequest(messages.Message):
  """A TargetPoolsRemoveInstanceRequest object.

  Fields:
    instances: URLs of the instances to be removed from targetPool.
  """

  instances = messages.MessageField('InstanceReference', 1, repeated=True)


class TargetPoolsScopedList(messages.Message):
  """A TargetPoolsScopedList object.

  Messages:
    WarningValue: Informational warning which replaces the list of addresses
      when the list is empty.

  Fields:
    targetPools: List of target pools contained in this scope.
    warning: Informational warning which replaces the list of addresses when
      the list is empty.
  """

  class WarningValue(messages.Message):
    """Informational warning which replaces the list of addresses when the
    list is empty.

    Enums:
      CodeValueValuesEnum: The warning type identifier for this warning.

    Messages:
      DataValueListEntry: A DataValueListEntry object.

    Fields:
      code: The warning type identifier for this warning.
      data: Metadata for this warning in 'key: value' format.
      message: Optional human-readable details for this warning.
    """

    class CodeValueValuesEnum(messages.Enum):
      """The warning type identifier for this warning.

      Values:
        DEPRECATED_RESOURCE_USED: <no description>
        DISK_SIZE_LARGER_THAN_IMAGE_SIZE: <no description>
        INJECTED_KERNELS_DEPRECATED: <no description>
        NEXT_HOP_ADDRESS_NOT_ASSIGNED: <no description>
        NEXT_HOP_CANNOT_IP_FORWARD: <no description>
        NEXT_HOP_INSTANCE_NOT_FOUND: <no description>
        NEXT_HOP_INSTANCE_NOT_ON_NETWORK: <no description>
        NEXT_HOP_NOT_RUNNING: <no description>
        NO_RESULTS_ON_PAGE: <no description>
        REQUIRED_TOS_AGREEMENT: <no description>
        RESOURCE_NOT_DELETED: <no description>
        UNREACHABLE: <no description>
      """
      DEPRECATED_RESOURCE_USED = 0
      DISK_SIZE_LARGER_THAN_IMAGE_SIZE = 1
      INJECTED_KERNELS_DEPRECATED = 2
      NEXT_HOP_ADDRESS_NOT_ASSIGNED = 3
      NEXT_HOP_CANNOT_IP_FORWARD = 4
      NEXT_HOP_INSTANCE_NOT_FOUND = 5
      NEXT_HOP_INSTANCE_NOT_ON_NETWORK = 6
      NEXT_HOP_NOT_RUNNING = 7
      NO_RESULTS_ON_PAGE = 8
      REQUIRED_TOS_AGREEMENT = 9
      RESOURCE_NOT_DELETED = 10
      UNREACHABLE = 11

    class DataValueListEntry(messages.Message):
      """A DataValueListEntry object.

      Fields:
        key: A key for the warning data.
        value: A warning data value corresponding to the key.
      """

      key = messages.StringField(1)
      value = messages.StringField(2)

    code = messages.EnumField('CodeValueValuesEnum', 1)
    data = messages.MessageField('DataValueListEntry', 2, repeated=True)
    message = messages.StringField(3)

  targetPools = messages.MessageField('TargetPool', 1, repeated=True)
  warning = messages.MessageField('WarningValue', 2)


class TargetReference(messages.Message):
  """A TargetReference object.

  Fields:
    target: A string attribute.
  """

  target = messages.StringField(1)


class TestFailure(messages.Message):
  """A TestFailure object.

  Fields:
    actualService: A string attribute.
    expectedService: A string attribute.
    host: A string attribute.
    path: A string attribute.
  """

  actualService = messages.StringField(1)
  expectedService = messages.StringField(2)
  host = messages.StringField(3)
  path = messages.StringField(4)


class UrlMap(messages.Message):
  """A UrlMap resource. This resource defines the mapping from URL to the
  BackendService resource, based on the "longest-match" of the URL's host and
  path.

  Fields:
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    defaultService: The URL of the BackendService resource if none of the
      hostRules match.
    description: An optional textual description of the resource; provided by
      the client when the resource is created.
    fingerprint: Fingerprint of this resource. A hash of the contents stored
      in this object. This field is used in optimistic locking. This field
      will be ignored when inserting a UrlMap. An up-to-date fingerprint must
      be provided in order to update the UrlMap.
    hostRules: The list of HostRules to use against the URL.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    name: Name of the resource; provided by the client when the resource is
      created. The name must be 1-63 characters long, and comply with RFC1035.
    pathMatchers: The list of named PathMatchers to use against the URL.
    selfLink: Server defined URL for the resource (output only).
    tests: The list of expected URL mappings. Request to update this UrlMap
      will succeed only all of the test cases pass.
  """

  creationTimestamp = messages.StringField(1)
  defaultService = messages.StringField(2)
  description = messages.StringField(3)
  fingerprint = messages.BytesField(4)
  hostRules = messages.MessageField('HostRule', 5, repeated=True)
  id = messages.IntegerField(6, variant=messages.Variant.UINT64)
  kind = messages.StringField(7, default=u'compute#urlMap')
  name = messages.StringField(8)
  pathMatchers = messages.MessageField('PathMatcher', 9, repeated=True)
  selfLink = messages.StringField(10)
  tests = messages.MessageField('UrlMapTest', 11, repeated=True)


class UrlMapList(messages.Message):
  """Contains a list of UrlMap resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of UrlMap resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('UrlMap', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#urlMapList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


class UrlMapReference(messages.Message):
  """A UrlMapReference object.

  Fields:
    urlMap: A string attribute.
  """

  urlMap = messages.StringField(1)


class UrlMapTest(messages.Message):
  """Message for the expected URL mappings.

  Fields:
    description: Description of this test case.
    host: Host portion of the URL.
    path: Path portion of the URL.
    service: Expected BackendService resource the given URL should be mapped
      to.
  """

  description = messages.StringField(1)
  host = messages.StringField(2)
  path = messages.StringField(3)
  service = messages.StringField(4)


class UrlMapValidationResult(messages.Message):
  """Message representing the validation result for a UrlMap.

  Fields:
    loadErrors: A string attribute.
    loadSucceeded: Whether the given UrlMap can be successfully loaded. If
      false, 'loadErrors' indicates the reasons.
    testFailures: A TestFailure attribute.
    testPassed: If successfully loaded, this field indicates whether the test
      passed. If false, 'testFailures's indicate the reason of failure.
  """

  loadErrors = messages.StringField(1, repeated=True)
  loadSucceeded = messages.BooleanField(2)
  testFailures = messages.MessageField('TestFailure', 3, repeated=True)
  testPassed = messages.BooleanField(4)


class UrlMapsValidateRequest(messages.Message):
  """A UrlMapsValidateRequest object.

  Fields:
    resource: Content of the UrlMap to be validated.
  """

  resource = messages.MessageField('UrlMap', 1)


class UrlMapsValidateResponse(messages.Message):
  """A UrlMapsValidateResponse object.

  Fields:
    result: A UrlMapValidationResult attribute.
  """

  result = messages.MessageField('UrlMapValidationResult', 1)


class UsageExportLocation(messages.Message):
  """The location in Cloud Storage and naming method of the daily usage
  report. Contains bucket_name and report_name prefix.

  Fields:
    bucketName: The name of an existing bucket in Cloud Storage where the
      usage report object is stored. The Google Service Account is granted
      write access to this bucket. This is simply the bucket name, with no
      "gs://" or "https://storage.googleapis.com/" in front of it.
    reportNamePrefix: An optional prefix for the name of the usage report
      object stored in bucket_name. If not supplied, defaults to "usage_". The
      report is stored as a CSV file named _gce_.csv. where  is the day of the
      usage according to Pacific Time. The prefix should conform to Cloud
      Storage object naming conventions.
  """

  bucketName = messages.StringField(1)
  reportNamePrefix = messages.StringField(2)


class Zone(messages.Message):
  """A zone resource.

  Enums:
    StatusValueValuesEnum: Status of the zone. "UP" or "DOWN".

  Messages:
    MaintenanceWindowsValueListEntry: A MaintenanceWindowsValueListEntry
      object.

  Fields:
    creationTimestamp: Creation timestamp in RFC3339 text format (output
      only).
    deprecated: The deprecation status associated with this zone.
    description: Textual description of the resource.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Type of the resource.
    maintenanceWindows: Scheduled maintenance windows for the zone. When the
      zone is in a maintenance window, all resources which reside in the zone
      will be unavailable.
    name: Name of the resource.
    region: Full URL reference to the region which hosts the zone (output
      only).
    selfLink: Server defined URL for the resource (output only).
    status: Status of the zone. "UP" or "DOWN".
  """

  class StatusValueValuesEnum(messages.Enum):
    """Status of the zone. "UP" or "DOWN".

    Values:
      DOWN: <no description>
      UP: <no description>
    """
    DOWN = 0
    UP = 1

  class MaintenanceWindowsValueListEntry(messages.Message):
    """A MaintenanceWindowsValueListEntry object.

    Fields:
      beginTime: Begin time of the maintenance window, in RFC 3339 format.
      description: Textual description of the maintenance window.
      endTime: End time of the maintenance window, in RFC 3339 format.
      name: Name of the maintenance window.
    """

    beginTime = messages.StringField(1)
    description = messages.StringField(2)
    endTime = messages.StringField(3)
    name = messages.StringField(4)

  creationTimestamp = messages.StringField(1)
  deprecated = messages.MessageField('DeprecationStatus', 2)
  description = messages.StringField(3)
  id = messages.IntegerField(4, variant=messages.Variant.UINT64)
  kind = messages.StringField(5, default=u'compute#zone')
  maintenanceWindows = messages.MessageField('MaintenanceWindowsValueListEntry', 6, repeated=True)
  name = messages.StringField(7)
  region = messages.StringField(8)
  selfLink = messages.StringField(9)
  status = messages.EnumField('StatusValueValuesEnum', 10)


class ZoneList(messages.Message):
  """Contains a list of zone resources.

  Fields:
    id: Unique identifier for the resource; defined by the server (output
      only).
    items: A list of Zone resources.
    kind: Type of resource.
    nextPageToken: A token used to continue a truncated list request (output
      only).
    selfLink: Server defined URL for this resource (output only).
  """

  id = messages.StringField(1)
  items = messages.MessageField('Zone', 2, repeated=True)
  kind = messages.StringField(3, default=u'compute#zoneList')
  nextPageToken = messages.StringField(4)
  selfLink = messages.StringField(5)


