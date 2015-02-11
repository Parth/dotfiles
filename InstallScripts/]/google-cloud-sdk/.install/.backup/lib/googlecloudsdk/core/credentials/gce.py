# Copyright 2013 Google Inc. All Rights Reserved.

"""One-line documentation for auth module.

A detailed description of auth.
"""

import mutex
import os
import time
import urllib2

from googlecloudsdk.core import config
from googlecloudsdk.core.util import files


GOOGLE_GCE_METADATA_URI = (
    'http://metadata.google.internal')
GOOGLE_GCE_METADATA_DEFAULT_ACCOUNT_URI = '/'.join([
    GOOGLE_GCE_METADATA_URI,
    'computeMetadata', 'v1beta1', 'instance', 'service-accounts', 'default',
    'email'])
GOOGLE_GCE_METADATA_PROJECT_URI = '/'.join([
    GOOGLE_GCE_METADATA_URI,
    'computeMetadata', 'v1beta1', 'project', 'project-id'])
GOOGLE_GCE_METADATA_NUMERIC_PROJECT_URI = '/'.join([
    GOOGLE_GCE_METADATA_URI,
    'computeMetadata', 'v1beta1', 'project', 'numeric-project-id'])
GOOGLE_GCE_METADATA_ACCOUNTS_URI = '/'.join([
    GOOGLE_GCE_METADATA_URI,
    'computeMetadata', 'v1beta1', 'instance', 'service-accounts'])
GOOGLE_GCE_METADATA_ACCOUNT_URI = '/'.join([
    GOOGLE_GCE_METADATA_ACCOUNTS_URI, '{account}', 'email'])

_GCE_CACHE_MAX_AGE = 10*60  # 10 minutes


class Error(Exception):
  """Exceptions for the gce module."""


class MetadataServerException(Error):
  """Exception for when the metadata server cannot be reached."""


class CannotConnectToMetadataServerException(MetadataServerException):
  """Exception for when the metadata server cannot be reached."""


class _GCEMetadata(object):
  """Class for fetching GCE metadata.

  Attributes:
    connected: bool, True if the metadata server is available.

  """

  def __init__(self):
    if _IsGCECached():
      self.connected = _IsOnGCEViaCache()
      return

    req = urllib2.Request(GOOGLE_GCE_METADATA_NUMERIC_PROJECT_URI)

    try:
      numeric_project_id = urllib2.urlopen(req, timeout=1).read()
      self.connected = numeric_project_id.isdigit()
    except urllib2.HTTPError:
      self.connected = False
    except urllib2.URLError:
      self.connected = False

    _CacheIsOnGCE(self.connected)

  def DefaultAccount(self):
    """Get the default service account for the host GCE instance.

    Fetches GOOGLE_GCE_METADATA_DEFAULT_ACCOUNT_URI and returns its contents.

    Raises:
      CannotConnectToMetadataServerException: If the metadata server
          cannot be reached.
      MetadataServerException: If there is a problem communicating with the
          metadata server.

    Returns:
      str, The email address for the default service account. None if not on a
          GCE VM, or if there are no service accounts associated with this VM.
    """

    if not self.connected:
      return None

    req = urllib2.Request(GOOGLE_GCE_METADATA_DEFAULT_ACCOUNT_URI)
    try:
      return urllib2.urlopen(req, timeout=1).read()
    except urllib2.HTTPError as e:
      if e.code == 404:
        return None
      raise MetadataServerException(e)
    except urllib2.URLError as e:
      raise CannotConnectToMetadataServerException(e)

  def Project(self):
    """Get the project that owns the current GCE instance.

    Fetches GOOGLE_GCE_METADATA_PROJECT_URI and returns its contents.

    Raises:
      CannotConnectToMetadataServerException: If the metadata server
          cannot be reached.
      MetadataServerException: If there is a problem communicating with the
          metadata server.

    Returns:
      str, The email address for the default service account. None if not on a
          GCE VM.
    """

    if not self.connected:
      return None

    req = urllib2.Request(GOOGLE_GCE_METADATA_PROJECT_URI)
    try:
      return urllib2.urlopen(req, timeout=1).read()
    except urllib2.HTTPError as e:
      raise MetadataServerException(e)
    except urllib2.URLError as e:
      raise CannotConnectToMetadataServerException(e)

  def Accounts(self):
    """Get the list of service accounts available from the metadata server.

    Returns:
      [str], The list of accounts. [] if not on a GCE VM.

    Raises:
      CannotConnectToMetadataServerException: If no metadata server is present.
      MetadataServerException: If there is a problem communicating with the
          metadata server.
    """

    if not self.connected:
      return []

    req = urllib2.Request(GOOGLE_GCE_METADATA_ACCOUNTS_URI + '/')
    try:
      accounts_listing = urllib2.urlopen(req, timeout=1).read()
      accounts_lines = accounts_listing.split()
      accounts = []
      for account_line in accounts_lines:
        account = account_line.strip('/')
        if account == 'default':
          continue
        accounts.append(account)
      return accounts
    except urllib2.HTTPError as e:
      raise MetadataServerException(e)
    except urllib2.URLError as e:
      raise CannotConnectToMetadataServerException(e)


_metadata = None
_metadata_lock = mutex.mutex()
_GCE_CACHE_MAX_AGE = 10*60  # 10 minutes


def Metadata():
  """Get a singleton that fetches GCE metadata.

  Returns:
    _GCEMetadata, An object used to collect information from the GCE metadata
    server.
  """
  def _CreateMetadata(unused_none):
    global _metadata
    if not _metadata:
      _metadata = _GCEMetadata()
  _metadata_lock.lock(function=_CreateMetadata, argument=None)
  _metadata_lock.unlock()
  return _metadata


def _CacheIsOnGCE(on_gce):
  with files.OpenForWritingPrivate(
      config.Paths().GCECachePath()) as gcecache_file:
    gcecache_file.write(str(on_gce))


def _IsGCECached():
  gce_cache_path = config.Paths().GCECachePath()
  if not os.path.exists(gce_cache_path):
    return False
  cache_mod = os.stat(gce_cache_path).st_mtime
  cache_age = time.time() - cache_mod
  if cache_age > _GCE_CACHE_MAX_AGE:
    return False
  return True


def _IsOnGCEViaCache():
  gce_cache_path = config.Paths().GCECachePath()
  if os.path.exists(gce_cache_path):
    with open(gce_cache_path) as gcecache_file:
      return gcecache_file.read() == str(True)
  return False
