"""Generated message classes for dns version v1beta1.

The Google Cloud DNS API provides services for configuring and serving
authoritative DNS records.
"""

from protorpc import messages


package = 'dns'


class Change(messages.Message):
  """An atomic update to a collection of ResourceRecordSets.

  Fields:
    additions: Which ResourceRecordSets to add?
    deletions: Which ResourceRecordSets to remove? Must match existing data
      exactly.
    id: Unique identifier for the resource; defined by the server (output
      only).
    kind: Identifies what kind of resource this is. Value: the fixed string
      "dns#change".
    startTime: The time that this operation was started by the server. This is
      in RFC3339 text format.
    status: Status of the operation. Can be one of the following: "PENDING" or
      "DONE" (output only).
  """

  additions = messages.MessageField('ResourceRecordSet', 1, repeated=True)
  deletions = messages.MessageField('ResourceRecordSet', 2, repeated=True)
  id = messages.StringField(3)
  kind = messages.StringField(4, default=u'dns#change')
  startTime = messages.StringField(5)
  status = messages.StringField(6)


class ChangesListResponse(messages.Message):
  """The response to a request to enumerate Changes to a ResourceRecordSets
  collection.

  Fields:
    changes: The requested changes.
    kind: Type of resource.
    nextPageToken: The presence of this field indicates that there exist more
      results following your last page of results in pagination order. To
      fetch them, make another list request using this value as your
      pagination token.  In this way you can retrieve the complete contents of
      even very large collections one page at a time. However, if the contents
      of the collection change between the first and last paginated list
      request, the set of all elements returned will be an inconsistent view
      of the collection. There is no way to retrieve a "snapshot" of
      collections larger than the maximum page size.
  """

  changes = messages.MessageField('Change', 1, repeated=True)
  kind = messages.StringField(2, default=u'dns#changesListResponse')
  nextPageToken = messages.StringField(3)


class DnsChangesCreateRequest(messages.Message):
  """A DnsChangesCreateRequest object.

  Fields:
    change: A Change resource to be passed as the request body.
    managedZone: Identifies the managed zone addressed by this request. Can be
      the managed zone name or id.
    project: Identifies the project addressed by this request.
  """

  change = messages.MessageField('Change', 1)
  managedZone = messages.StringField(2, required=True)
  project = messages.StringField(3, required=True)


class DnsChangesGetRequest(messages.Message):
  """A DnsChangesGetRequest object.

  Fields:
    changeId: The identifier of the requested change, from a previous
      ResourceRecordSetsChangeResponse.
    managedZone: Identifies the managed zone addressed by this request. Can be
      the managed zone name or id.
    project: Identifies the project addressed by this request.
  """

  changeId = messages.StringField(1, required=True)
  managedZone = messages.StringField(2, required=True)
  project = messages.StringField(3, required=True)


class DnsChangesListRequest(messages.Message):
  """A DnsChangesListRequest object.

  Enums:
    SortByValueValuesEnum: Sorting criterion. The only supported value is
      change sequence.

  Fields:
    managedZone: Identifies the managed zone addressed by this request. Can be
      the managed zone name or id.
    maxResults: Optional. Maximum number of results to be returned. If
      unspecified, the server will decide how many results to return.
    pageToken: Optional. A tag returned by a previous list request that was
      truncated. Use this parameter to continue a previous list request.
    project: Identifies the project addressed by this request.
    sortBy: Sorting criterion. The only supported value is change sequence.
    sortOrder: Sorting order direction: 'ascending' or 'descending'.
  """

  class SortByValueValuesEnum(messages.Enum):
    """Sorting criterion. The only supported value is change sequence.

    Values:
      changeSequence: <no description>
    """
    changeSequence = 0

  managedZone = messages.StringField(1, required=True)
  maxResults = messages.IntegerField(2, variant=messages.Variant.INT32)
  pageToken = messages.StringField(3)
  project = messages.StringField(4, required=True)
  sortBy = messages.EnumField('SortByValueValuesEnum', 5, default=u'changeSequence')
  sortOrder = messages.StringField(6)


class DnsManagedZonesCreateRequest(messages.Message):
  """A DnsManagedZonesCreateRequest object.

  Fields:
    managedZone: A ManagedZone resource to be passed as the request body.
    project: Identifies the project addressed by this request.
  """

  managedZone = messages.MessageField('ManagedZone', 1)
  project = messages.StringField(2, required=True)


class DnsManagedZonesDeleteRequest(messages.Message):
  """A DnsManagedZonesDeleteRequest object.

  Fields:
    managedZone: Identifies the managed zone addressed by this request. Can be
      the managed zone name or id.
    project: Identifies the project addressed by this request.
  """

  managedZone = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class DnsManagedZonesDeleteResponse(messages.Message):
  """An empty DnsManagedZonesDelete response."""


class DnsManagedZonesGetRequest(messages.Message):
  """A DnsManagedZonesGetRequest object.

  Fields:
    managedZone: Identifies the managed zone addressed by this request. Can be
      the managed zone name or id.
    project: Identifies the project addressed by this request.
  """

  managedZone = messages.StringField(1, required=True)
  project = messages.StringField(2, required=True)


class DnsManagedZonesListRequest(messages.Message):
  """A DnsManagedZonesListRequest object.

  Fields:
    maxResults: Optional. Maximum number of results to be returned. If
      unspecified, the server will decide how many results to return.
    pageToken: Optional. A tag returned by a previous list request that was
      truncated. Use this parameter to continue a previous list request.
    project: Identifies the project addressed by this request.
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.INT32)
  pageToken = messages.StringField(2)
  project = messages.StringField(3, required=True)


class DnsProjectsGetRequest(messages.Message):
  """A DnsProjectsGetRequest object.

  Fields:
    project: Identifies the project addressed by this request.
  """

  project = messages.StringField(1, required=True)


class DnsResourceRecordSetsListRequest(messages.Message):
  """A DnsResourceRecordSetsListRequest object.

  Fields:
    managedZone: Identifies the managed zone addressed by this request. Can be
      the managed zone name or id.
    maxResults: Optional. Maximum number of results to be returned. If
      unspecified, the server will decide how many results to return.
    name: Restricts the list to return only records with this fully qualified
      domain name.
    pageToken: Optional. A tag returned by a previous list request that was
      truncated. Use this parameter to continue a previous list request.
    project: Identifies the project addressed by this request.
    type: Restricts the list to return only records of this type. If present,
      the "name" parameter must also be present.
  """

  managedZone = messages.StringField(1, required=True)
  maxResults = messages.IntegerField(2, variant=messages.Variant.INT32)
  name = messages.StringField(3)
  pageToken = messages.StringField(4)
  project = messages.StringField(5, required=True)
  type = messages.StringField(6)


class ManagedZone(messages.Message):
  """A zone is a subtree of the DNS namespace under one administrative
  responsibility. A ManagedZone is a resource that represents a DNS zone
  hosted by the Cloud DNS service.

  Fields:
    creationTime: The time that this resource was created on the server. This
      is in RFC3339 text format. Output only.
    description: A mutable string of at most 1024 characters associated with
      this resource for the user's convenience. Has no effect on the managed
      zone's function.
    dnsName: The DNS name of this managed zone, for instance "example.com.".
    id: Unique identifier for the resource; defined by the server (output
      only)
    kind: Identifies what kind of resource this is. Value: the fixed string
      "dns#managedZone".
    name: User assigned name for this resource. Must be unique within the
      project. The name must be 1-32 characters long, must begin with a
      letter, end with a letter or digit, and only contain lowercase letters,
      digits or dashes.
    nameServerSet: Optionally specifies the NameServerSet for this
      ManagedZone. A NameServerSet is a set of DNS name servers that all host
      the same ManagedZones. Most users will leave this field unset.
    nameServers: Delegate your managed_zone to these virtual name servers;
      defined by the server (output only)
  """

  creationTime = messages.StringField(1)
  description = messages.StringField(2)
  dnsName = messages.StringField(3)
  id = messages.IntegerField(4, variant=messages.Variant.UINT64)
  kind = messages.StringField(5, default=u'dns#managedZone')
  name = messages.StringField(6)
  nameServerSet = messages.StringField(7)
  nameServers = messages.StringField(8, repeated=True)


class ManagedZonesListResponse(messages.Message):
  """A ManagedZonesListResponse object.

  Fields:
    kind: Type of resource.
    managedZones: The managed zone resources.
    nextPageToken: The presence of this field indicates that there exist more
      results following your last page of results in pagination order. To
      fetch them, make another list request using this value as your page
      token.  In this way you can retrieve the complete contents of even very
      large collections one page at a time. However, if the contents of the
      collection change between the first and last paginated list request, the
      set of all elements returned will be an inconsistent view of the
      collection. There is no way to retrieve a consistent snapshot of a
      collection larger than the maximum page size.
  """

  kind = messages.StringField(1, default=u'dns#managedZonesListResponse')
  managedZones = messages.MessageField('ManagedZone', 2, repeated=True)
  nextPageToken = messages.StringField(3)


class Project(messages.Message):
  """A project resource. The project is a top level container for resources
  including Cloud DNS ManagedZones. Projects can be created only in the APIs
  console.

  Fields:
    id: User assigned unique identifier for the resource (output only).
    kind: Identifies what kind of resource this is. Value: the fixed string
      "dns#project".
    number: Unique numeric identifier for the resource; defined by the server
      (output only).
    quota: Quotas assigned to this project (output only).
  """

  id = messages.StringField(1)
  kind = messages.StringField(2, default=u'dns#project')
  number = messages.IntegerField(3, variant=messages.Variant.UINT64)
  quota = messages.MessageField('Quota', 4)


class Quota(messages.Message):
  """Limits associated with a Project.

  Fields:
    kind: Identifies what kind of resource this is. Value: the fixed string
      "dns#quota".
    managedZones: Maximum allowed number of managed zones in the project.
    resourceRecordsPerRrset: Maximum allowed number of ResourceRecords per
      ResourceRecordSet.
    rrsetAdditionsPerChange: Maximum allowed number of ResourceRecordSets to
      add per ChangesCreateRequest.
    rrsetDeletionsPerChange: Maximum allowed number of ResourceRecordSets to
      delete per ChangesCreateRequest.
    rrsetsPerManagedZone: Maximum allowed number of ResourceRecordSets per
      zone in the project.
    totalRrdataSizePerChange: Maximum allowed size for total rrdata in one
      ChangesCreateRequest in bytes.
  """

  kind = messages.StringField(1, default=u'dns#quota')
  managedZones = messages.IntegerField(2, variant=messages.Variant.INT32)
  resourceRecordsPerRrset = messages.IntegerField(3, variant=messages.Variant.INT32)
  rrsetAdditionsPerChange = messages.IntegerField(4, variant=messages.Variant.INT32)
  rrsetDeletionsPerChange = messages.IntegerField(5, variant=messages.Variant.INT32)
  rrsetsPerManagedZone = messages.IntegerField(6, variant=messages.Variant.INT32)
  totalRrdataSizePerChange = messages.IntegerField(7, variant=messages.Variant.INT32)


class ResourceRecordSet(messages.Message):
  """A unit of data that will be returned by the DNS servers.

  Fields:
    kind: Identifies what kind of resource this is. Value: the fixed string
      "dns#resourceRecordSet".
    name: For example, www.example.com.
    rrdatas: As defined in RFC 1035 (section 5) and RFC 1034 (section 3.6.1)
    ttl: Number of seconds that this ResourceRecordSet can be cached by
      resolvers.
    type: One of A, AAAA, SOA, MX, NS, TXT
  """

  kind = messages.StringField(1, default=u'dns#resourceRecordSet')
  name = messages.StringField(2)
  rrdatas = messages.StringField(3, repeated=True)
  ttl = messages.IntegerField(4, variant=messages.Variant.INT32)
  type = messages.StringField(5)


class ResourceRecordSetsListResponse(messages.Message):
  """A ResourceRecordSetsListResponse object.

  Fields:
    kind: Type of resource.
    nextPageToken: The presence of this field indicates that there exist more
      results following your last page of results in pagination order. To
      fetch them, make another list request using this value as your
      pagination token.  In this way you can retrieve the complete contents of
      even very large collections one page at a time. However, if the contents
      of the collection change between the first and last paginated list
      request, the set of all elements returned will be an inconsistent view
      of the collection. There is no way to retrieve a consistent snapshot of
      a collection larger than the maximum page size.
    rrsets: The resource record set resources.
  """

  kind = messages.StringField(1, default=u'dns#resourceRecordSetsListResponse')
  nextPageToken = messages.StringField(2)
  rrsets = messages.MessageField('ResourceRecordSet', 3, repeated=True)


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


