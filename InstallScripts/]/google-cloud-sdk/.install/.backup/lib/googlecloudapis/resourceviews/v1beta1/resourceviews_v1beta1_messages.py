"""Generated message classes for resourceviews version v1beta1.

The Resource View API allows users to create and manage logical sets of Google
Compute Engine instances.
"""

from protorpc import messages


package = 'resourceviews'


class Label(messages.Message):
  """The Label to be applied to the resource views.

  Fields:
    key: Key of the label.
    value: Value of the label.
  """

  key = messages.StringField(1)
  value = messages.StringField(2)


class RegionViewsAddResourcesRequest(messages.Message):
  """The request to add resources to the resource view.

  Fields:
    resources: The list of resources to be added.
  """

  resources = messages.StringField(1, repeated=True)


class RegionViewsInsertResponse(messages.Message):
  """The response to a resource view insert request.

  Fields:
    resource: The resource view object inserted.
  """

  resource = messages.MessageField('ResourceView', 1)


class RegionViewsListResourcesResponse(messages.Message):
  """The response to the list resource request.

  Fields:
    members: The resources in the view.
    nextPageToken: A token used for pagination.
  """

  members = messages.StringField(1, repeated=True)
  nextPageToken = messages.StringField(2)


class RegionViewsListResponse(messages.Message):
  """The response to the list resource view request.

  Fields:
    nextPageToken: A token used for pagination.
    resourceViews: The list of resource views that meet the criteria.
  """

  nextPageToken = messages.StringField(1)
  resourceViews = messages.MessageField('ResourceView', 2, repeated=True)


class RegionViewsRemoveResourcesRequest(messages.Message):
  """The request to remove resources from the resource view.

  Fields:
    resources: The list of resources to be removed.
  """

  resources = messages.StringField(1, repeated=True)


class ResourceView(messages.Message):
  """The resource view object.

  Fields:
    creationTime: The creation time of the resource view.
    description: The detailed description of the resource view.
    id: [Output Only] The ID of the resource view.
    kind: Type of the resource.
    labels: The labels for events.
    lastModified: The last modified time of the view. Not supported yet.
    members: A list of all resources in the resource view.
    name: The name of the resource view.
    numMembers: The total number of resources in the resource view.
    selfLink: [Output Only] A self-link to the resource view.
  """

  creationTime = messages.StringField(1)
  description = messages.StringField(2)
  id = messages.StringField(3)
  kind = messages.StringField(4, default=u'resourceviews#resourceView')
  labels = messages.MessageField('Label', 5, repeated=True)
  lastModified = messages.StringField(6)
  members = messages.StringField(7, repeated=True)
  name = messages.StringField(8)
  numMembers = messages.IntegerField(9, variant=messages.Variant.UINT32)
  selfLink = messages.StringField(10)


class ResourceviewsRegionViewsAddresourcesRequest(messages.Message):
  """A ResourceviewsRegionViewsAddresourcesRequest object.

  Fields:
    projectName: The project name of the resource view.
    region: The region name of the resource view.
    regionViewsAddResourcesRequest: A RegionViewsAddResourcesRequest resource
      to be passed as the request body.
    resourceViewName: The name of the resource view.
  """

  projectName = messages.StringField(1, required=True)
  region = messages.StringField(2, required=True)
  regionViewsAddResourcesRequest = messages.MessageField('RegionViewsAddResourcesRequest', 3)
  resourceViewName = messages.StringField(4, required=True)


class ResourceviewsRegionViewsAddresourcesResponse(messages.Message):
  """An empty ResourceviewsRegionViewsAddresources response."""


class ResourceviewsRegionViewsDeleteRequest(messages.Message):
  """A ResourceviewsRegionViewsDeleteRequest object.

  Fields:
    projectName: The project name of the resource view.
    region: The region name of the resource view.
    resourceViewName: The name of the resource view.
  """

  projectName = messages.StringField(1, required=True)
  region = messages.StringField(2, required=True)
  resourceViewName = messages.StringField(3, required=True)


class ResourceviewsRegionViewsDeleteResponse(messages.Message):
  """An empty ResourceviewsRegionViewsDelete response."""


class ResourceviewsRegionViewsGetRequest(messages.Message):
  """A ResourceviewsRegionViewsGetRequest object.

  Fields:
    projectName: The project name of the resource view.
    region: The region name of the resource view.
    resourceViewName: The name of the resource view.
  """

  projectName = messages.StringField(1, required=True)
  region = messages.StringField(2, required=True)
  resourceViewName = messages.StringField(3, required=True)


class ResourceviewsRegionViewsInsertRequest(messages.Message):
  """A ResourceviewsRegionViewsInsertRequest object.

  Fields:
    projectName: The project name of the resource view.
    region: The region name of the resource view.
    resourceView: A ResourceView resource to be passed as the request body.
  """

  projectName = messages.StringField(1, required=True)
  region = messages.StringField(2, required=True)
  resourceView = messages.MessageField('ResourceView', 3)


class ResourceviewsRegionViewsListRequest(messages.Message):
  """A ResourceviewsRegionViewsListRequest object.

  Fields:
    maxResults: Maximum count of results to be returned. Acceptable values are
      0 to 5000, inclusive. (Default: 5000)
    pageToken: Specifies a nextPageToken returned by a previous list request.
      This token can be used to request the next page of results from a
      previous list request.
    projectName: The project name of the resource view.
    region: The region name of the resource view.
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.INT32, default=5000)
  pageToken = messages.StringField(2)
  projectName = messages.StringField(3, required=True)
  region = messages.StringField(4, required=True)


class ResourceviewsRegionViewsListresourcesRequest(messages.Message):
  """A ResourceviewsRegionViewsListresourcesRequest object.

  Fields:
    maxResults: Maximum count of results to be returned. Acceptable values are
      0 to 5000, inclusive. (Default: 5000)
    pageToken: Specifies a nextPageToken returned by a previous list request.
      This token can be used to request the next page of results from a
      previous list request.
    projectName: The project name of the resource view.
    region: The region name of the resource view.
    resourceViewName: The name of the resource view.
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.INT32, default=5000)
  pageToken = messages.StringField(2)
  projectName = messages.StringField(3, required=True)
  region = messages.StringField(4, required=True)
  resourceViewName = messages.StringField(5, required=True)


class ResourceviewsRegionViewsRemoveresourcesRequest(messages.Message):
  """A ResourceviewsRegionViewsRemoveresourcesRequest object.

  Fields:
    projectName: The project name of the resource view.
    region: The region name of the resource view.
    regionViewsRemoveResourcesRequest: A RegionViewsRemoveResourcesRequest
      resource to be passed as the request body.
    resourceViewName: The name of the resource view.
  """

  projectName = messages.StringField(1, required=True)
  region = messages.StringField(2, required=True)
  regionViewsRemoveResourcesRequest = messages.MessageField('RegionViewsRemoveResourcesRequest', 3)
  resourceViewName = messages.StringField(4, required=True)


class ResourceviewsRegionViewsRemoveresourcesResponse(messages.Message):
  """An empty ResourceviewsRegionViewsRemoveresources response."""


class ResourceviewsZoneViewsAddresourcesRequest(messages.Message):
  """A ResourceviewsZoneViewsAddresourcesRequest object.

  Fields:
    projectName: The project name of the resource view.
    resourceViewName: The name of the resource view.
    zone: The zone name of the resource view.
    zoneViewsAddResourcesRequest: A ZoneViewsAddResourcesRequest resource to
      be passed as the request body.
  """

  projectName = messages.StringField(1, required=True)
  resourceViewName = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)
  zoneViewsAddResourcesRequest = messages.MessageField('ZoneViewsAddResourcesRequest', 4)


class ResourceviewsZoneViewsAddresourcesResponse(messages.Message):
  """An empty ResourceviewsZoneViewsAddresources response."""


class ResourceviewsZoneViewsDeleteRequest(messages.Message):
  """A ResourceviewsZoneViewsDeleteRequest object.

  Fields:
    projectName: The project name of the resource view.
    resourceViewName: The name of the resource view.
    zone: The zone name of the resource view.
  """

  projectName = messages.StringField(1, required=True)
  resourceViewName = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ResourceviewsZoneViewsDeleteResponse(messages.Message):
  """An empty ResourceviewsZoneViewsDelete response."""


class ResourceviewsZoneViewsGetRequest(messages.Message):
  """A ResourceviewsZoneViewsGetRequest object.

  Fields:
    projectName: The project name of the resource view.
    resourceViewName: The name of the resource view.
    zone: The zone name of the resource view.
  """

  projectName = messages.StringField(1, required=True)
  resourceViewName = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)


class ResourceviewsZoneViewsInsertRequest(messages.Message):
  """A ResourceviewsZoneViewsInsertRequest object.

  Fields:
    projectName: The project name of the resource view.
    resourceView: A ResourceView resource to be passed as the request body.
    zone: The zone name of the resource view.
  """

  projectName = messages.StringField(1, required=True)
  resourceView = messages.MessageField('ResourceView', 2)
  zone = messages.StringField(3, required=True)


class ResourceviewsZoneViewsListRequest(messages.Message):
  """A ResourceviewsZoneViewsListRequest object.

  Fields:
    maxResults: Maximum count of results to be returned. Acceptable values are
      0 to 5000, inclusive. (Default: 5000)
    pageToken: Specifies a nextPageToken returned by a previous list request.
      This token can be used to request the next page of results from a
      previous list request.
    projectName: The project name of the resource view.
    zone: The zone name of the resource view.
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.INT32, default=5000)
  pageToken = messages.StringField(2)
  projectName = messages.StringField(3, required=True)
  zone = messages.StringField(4, required=True)


class ResourceviewsZoneViewsListresourcesRequest(messages.Message):
  """A ResourceviewsZoneViewsListresourcesRequest object.

  Fields:
    maxResults: Maximum count of results to be returned. Acceptable values are
      0 to 5000, inclusive. (Default: 5000)
    pageToken: Specifies a nextPageToken returned by a previous list request.
      This token can be used to request the next page of results from a
      previous list request.
    projectName: The project name of the resource view.
    resourceViewName: The name of the resource view.
    zone: The zone name of the resource view.
  """

  maxResults = messages.IntegerField(1, variant=messages.Variant.INT32, default=5000)
  pageToken = messages.StringField(2)
  projectName = messages.StringField(3, required=True)
  resourceViewName = messages.StringField(4, required=True)
  zone = messages.StringField(5, required=True)


class ResourceviewsZoneViewsRemoveresourcesRequest(messages.Message):
  """A ResourceviewsZoneViewsRemoveresourcesRequest object.

  Fields:
    projectName: The project name of the resource view.
    resourceViewName: The name of the resource view.
    zone: The zone name of the resource view.
    zoneViewsRemoveResourcesRequest: A ZoneViewsRemoveResourcesRequest
      resource to be passed as the request body.
  """

  projectName = messages.StringField(1, required=True)
  resourceViewName = messages.StringField(2, required=True)
  zone = messages.StringField(3, required=True)
  zoneViewsRemoveResourcesRequest = messages.MessageField('ZoneViewsRemoveResourcesRequest', 4)


class ResourceviewsZoneViewsRemoveresourcesResponse(messages.Message):
  """An empty ResourceviewsZoneViewsRemoveresources response."""


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


class ZoneViewsAddResourcesRequest(messages.Message):
  """The request to add resources to the resource view.

  Fields:
    resources: The list of resources to be added.
  """

  resources = messages.StringField(1, repeated=True)


class ZoneViewsInsertResponse(messages.Message):
  """The response to an insert request.

  Fields:
    resource: The resource view object that has been inserted.
  """

  resource = messages.MessageField('ResourceView', 1)


class ZoneViewsListResourcesResponse(messages.Message):
  """The response to a list resource request.

  Fields:
    members: The full URL of resources in the view.
    nextPageToken: A token used for pagination.
  """

  members = messages.StringField(1, repeated=True)
  nextPageToken = messages.StringField(2)


class ZoneViewsListResponse(messages.Message):
  """The response to a list request.

  Fields:
    nextPageToken: A token used for pagination.
    resourceViews: The result that contains all resource views that meet the
      criteria.
  """

  nextPageToken = messages.StringField(1)
  resourceViews = messages.MessageField('ResourceView', 2, repeated=True)


class ZoneViewsRemoveResourcesRequest(messages.Message):
  """The request to remove resources from the resource view.

  Fields:
    resources: The list of resources to be removed.
  """

  resources = messages.StringField(1, repeated=True)


