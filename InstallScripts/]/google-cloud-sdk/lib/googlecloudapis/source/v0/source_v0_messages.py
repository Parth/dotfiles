"""Generated message classes for source version v0.

This is an API
"""

from protorpc import messages


package = 'source'


class ListReposResponse(messages.Message):
  """A response containing a list of Repos belonging to a project.

  Fields:
    repos: Repos belonging to the project.
  """

  repos = messages.MessageField('Repo', 1, repeated=True)


class Repo(messages.Message):
  """A code repository.

  Fields:
    cloneUrl: URL where this repo can be cloned.
    repoId: ID of the Repo.
    repoName: User-defined name of the repo (or 'default')
  """

  cloneUrl = messages.StringField(1)
  repoId = messages.StringField(2)
  repoName = messages.StringField(3)


class SourceReposListRequest(messages.Message):
  """A SourceReposListRequest object.

  Fields:
    projectId: ID of the project for which to list Repos. Examples: user-
      chosen-project-id, yellow-banana-33, dyspeptic-wombat-87
  """

  projectId = messages.StringField(1, required=True)


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


