# Copyright 2014 Google Inc. All Rights Reserved.

"""Utility library for configuring access to the Google Container Registry.

Sets docker up to authenticate with the Google Container Registry using the
active gcloud credential.
"""

import base64
import json
import os

from googlecloudsdk.core import exceptions
from googlecloudsdk.core.credentials import store as c_store

USERNAME = '_token'


# Other tools like the python docker library (used by gcloud app)
# also rely on .dockercfg (in addition to the docker CLI client)
# NOTE: Lazy for manipulation of HOME / mocking.
def GetDockerConfig():
  # TODO(user): While os.path.expanduser('~') is more portable, here we
  # very intentionally match the paired logic from docker/docker-py, which
  # uses the HOME variable directly.
  return os.path.join(os.environ.get('HOME', '.'), '.dockercfg')


def ReadDockerConfig():
  with open(GetDockerConfig(), 'r') as reader:
    return reader.read()


def WriteDockerConfig(contents):
  with open(GetDockerConfig(), 'w') as writer:
    writer.write(contents)


def UpdateDockerCredentials(server):
  """Updates the docker config to have fresh credentials."""
  # Loading credentials will ensure that we're logged in.
  # And prompt/abort to 'run gcloud auth login' otherwise.
  cred = c_store.Load()

  # Ensure our credential has a valid access token,
  # which has the full duration available.
  c_store.Refresh(cred)
  if not cred.access_token:
    raise exceptions.Error('No access token could be obtained '
                           'from the current credentials.')

  # Update the docker configuration file passing the access token
  # as a password, and a benign value as the username.
  _UpdateDockerConfig(server, USERNAME, cred.access_token)


def _UpdateDockerConfig(server, username, access_token):
  """Register the username and token for the given server in '.dockercfg'."""

  # NOTE: using "docker login" doesn't work as they're quite strict on what
  # is allowed in username/password.
  try:
    dockercfg_contents = json.loads(ReadDockerConfig())
  except IOError:
    # If the file doesn't exist, start with an empty map.
    dockercfg_contents = {}

  # Add the entry for our server.
  auth = base64.b64encode(username + ':' + access_token)

  # Clear out any unqualified stale entry for this server
  if server in dockercfg_contents:
    del dockercfg_contents[server]

  scheme = 'https://'
  dockercfg_contents[scheme + server] = {'auth': auth,
                                         'email': 'not@val.id'}

  # TODO(user): atomic replace?
  # Be nice and pretty-print.
  WriteDockerConfig(json.dumps(dockercfg_contents, indent=2))
