# Copyright 2013 Google Inc. All Rights Reserved.

"""Generates credentials for gsutil."""

import base64
import os
import textwrap

from oauth2client import client as oauth2_client
from oauth2client import multistore_file as oauth2_multistore_file

from googlecloudsdk.core import config
from googlecloudsdk.core.util import files


class CredentialGenerator(object):
  """Base class for all credential generators."""

  def __init__(self, path, credentials, project_id, scopes):
    # path is relative to the user's home directory.
    self.path = path
    self.credentials = credentials
    self.project_id = project_id
    self.scopes = scopes

  def _WriteFileContents(self, filepath, contents):
    """Writes contents to a path, ensuring mkdirs.

    Args:
      filepath: str, The path of the file to write.
      contents: str, The contents to write to the file.
    """

    full_path = os.path.realpath(os.path.expanduser(filepath))

    try:
      with files.OpenForWritingPrivate(full_path) as cred_file:
        cred_file.write(contents)
    except (OSError, IOError), e:
      raise Exception('Failed to open %s for writing: %s' % (self.path, e))

  def WriteTemplate(self):
    raise NotImplementedError(
        'This method needs to be overridden in subclasses')

  def Clean(self):
    raise NotImplementedError(
        'This method needs to be overridden in subclasses')


class LegacyGenerator(CredentialGenerator):
  """A class to generate the credential file for legacy tools."""

  def __init__(self, multistore_path, json_path, gae_java_path, gsutil_path,
               key_path, credentials, scopes):
    self._multistore_path = multistore_path
    self._json_path = json_path
    self._gae_java_path = gae_java_path
    self._gsutil_path = gsutil_path
    self._key_path = key_path
    super(LegacyGenerator, self).__init__(
        path=None,
        credentials=credentials,
        project_id=None,
        scopes=scopes,
    )

  def Clean(self):
    """Remove the credential file."""

    paths = [
        self._multistore_path,
        self._json_path,
        self._gae_java_path,
        self._gsutil_path,
        self._key_path,
    ]
    for p in paths:
      try:
        os.remove(p)
      except OSError:
        # file did not exist, so we're already done.
        pass

  def WriteTemplate(self):
    """Write the credential file."""

    # straight up credentials in JSON
    self._WriteFileContents(self._json_path,
                            self.credentials.to_json())
    # multistore version
    self._WriteFileContents(self._multistore_path, '')
    storage = oauth2_multistore_file.get_credential_storage(
        self._multistore_path,
        self.credentials.client_id,
        self.credentials.user_agent,
        self.scopes)
    storage.put(self.credentials)

    if self.credentials.refresh_token:
      # gae java wants something special
      self._WriteFileContents(self._gae_java_path, textwrap.dedent("""\
          oauth2_client_secret: {secret}
          oauth2_client_id: {id}
          oauth2_refresh_token: {token}
          """).format(secret=config.CLOUDSDK_CLIENT_NOTSOSECRET,
                      id=config.CLOUDSDK_CLIENT_ID,
                      token=self.credentials.refresh_token))

      # we create a small .boto file for gsutil, to be put in BOTO_PATH
      self._WriteFileContents(self._gsutil_path, textwrap.dedent("""\
          [Credentials]
          gs_oauth2_refresh_token = {token}
          """).format(token=self.credentials.refresh_token))

    if (oauth2_client.HAS_CRYPTO and
        type(self.credentials) == oauth2_client.SignedJwtAssertionCredentials):
      with files.OpenForWritingPrivate(self._key_path) as pk:
        pk.write(base64.b64decode(self.credentials.private_key))
      # the .boto file gets some different fields
      self._WriteFileContents(self._gsutil_path, textwrap.dedent("""\
          [Credentials]
          gs_service_client_id = {account}
          gs_service_key_file = {key_file}
          gs_service_key_file_password = {key_password}
          """).format(account=self.credentials.service_account_name,
                      key_file=self._key_path,
                      key_password=self.credentials.private_key_password))
