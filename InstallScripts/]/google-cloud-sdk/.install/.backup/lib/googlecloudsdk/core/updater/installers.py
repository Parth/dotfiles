# Copyright 2013 Google Inc. All Rights Reserved.

"""Implementations of installers for different component types."""

import os
import re
import ssl
import tarfile
import urllib2

from googlecloudsdk.core import exceptions
from googlecloudsdk.core import properties
from googlecloudsdk.core.credentials import store
from googlecloudsdk.core.util import console_io
from googlecloudsdk.core.util import files as file_utils


TIMEOUT_IN_SEC = 60


class Error(exceptions.Error):
  """Base exception for the installers module."""
  pass


class ComponentDownloadFailedError(Error):
  """Exception for when we cannot download a component for some reason."""

  def __init__(self, component_id, e):
    super(ComponentDownloadFailedError, self).__init__(
        'The component [{component_id}] failed to download.\n\n'.format(
            component_id=component_id) + str(e))


class URLFetchError(Error):
  """Exception for problems fetching via HTTP."""
  pass


class AuthenticationError(Error):
  """Exception for when the resource is protected by authentication."""

  def __init__(self, msg, e):
    super(AuthenticationError, self).__init__(msg + '\n\n' + str(e))


class UnsupportedSourceError(Error):
  """An exception when trying to install a component with an unknown source."""
  pass


class ComponentInstaller(object):
  """A class to install Cloud SDK components of different source types."""

  DOWNLOAD_DIR_NAME = '.download'
  # This is the URL prefix for files that require authentication which triggers
  # browser based cookie authentication.  We will use URLs with this pattern,
  # but we never want to actually try to download from here because we are not
  # using a browser and it will return the html of the sign in page.
  GCS_BROWSER_DL_URL = 'https://storage.cloud.google.com/'
  # All files accessible though the above prefix, are accessible through this
  # prefix when you insert authentication data into the http headers.  If no
  # auth is required, you can also use this URL directly with no headers.
  GCS_API_DL_URL = 'https://storage.googleapis.com/'

  def __init__(self, sdk_root, state_directory, snapshot):
    """Initializes an installer for components of different source types.

    Args:
      sdk_root:  str, The path to the root directory of all Cloud SDK files.
      state_directory: str, The path to the directory where the local state is
        stored.
      snapshot: snapshots.ComponentSnapshot, The snapshot that describes the
        component to install.
    """
    self.__sdk_root = sdk_root
    self.__state_directory = state_directory
    self.__download_directory = os.path.join(
        self.__state_directory, ComponentInstaller.DOWNLOAD_DIR_NAME)
    self.__snapshot = snapshot

    for d in [self.__download_directory]:
      if not os.path.isdir(d):
        file_utils.MakeDir(d)

  def Install(self, component_id, progress_callback=None):
    """Installs the given component for whatever source type it has.

    Args:
      component_id: str, The component id from the snapshot to install.
      progress_callback: f(float), A function to call with the fraction of
        completeness.

    Returns:
      list of str, The files that were installed.

    Raises:
      UnsupportedSourceError: If the component data source is of an unknown
        type.
      URLFetchError: If the URL associated with the component data source
        cannot be fetched.
    """
    component = self.__snapshot.ComponentFromId(component_id)
    data = component.data

    if not data:
      # No source data, just a configuration component
      return []

    if data.type == 'tar':
      return self._InstallTar(component, progress_callback=progress_callback)

    raise UnsupportedSourceError(
        'tar is the only supported source format [{datatype}]'.format(
            datatype=self.data.type))

  def _InstallTar(self, component, progress_callback=None):
    """Installer implementation for a component with source in a .tar.gz.

    Downloads the .tar for the component and extracts it.

    Args:
      component: schemas.Component, The component to install.
      progress_callback: f(float), A function to call with the fraction of
        completeness.

    Returns:
      list of str, The files that were installed or [] if nothing was installed.

    Raises:
      ValueError: If the source URL for the tar file is relative, but there is
        no location information associated with the snapshot we are installing
        from.
      URLFetchError: If there is a problem fetching the component's URL.
    """
    url = component.data.source
    if not url:
      # not all components must have real source
      return []

    if not re.search(r'^\w+://', url):
      raise ValueError('Cannot install component [{}] from a relative path '
                       'because the base URL of the snapshot is not defined.'
                       .format(component.id))

    try:
      return ComponentInstaller.DownloadAndExtractTar(
          url, self.__download_directory, self.__sdk_root,
          progress_callback=progress_callback)
    except (URLFetchError, AuthenticationError) as e:
      raise ComponentDownloadFailedError(component.id, e)

  @staticmethod
  def DownloadAndExtractTar(url, download_dir, extract_dir,
                            progress_callback=None):
    """Download and extract the given tar file.

    Args:
      url: str, The URL to download.
      download_dir: str, The path to put the temporary download file into.
      extract_dir: str, The path to extract the tar into.
      progress_callback: f(float), A function to call with the fraction of
        completeness.

    Returns:
      [str], The files that were extracted from the tar file.

    Raises:
      URLFetchError: If there is a problem fetching the given URL.
    """
    for d in [download_dir, extract_dir]:
      if not os.path.exists(d):
        file_utils.MakeDir(d)
    download_file_path = os.path.join(download_dir, os.path.basename(url))
    if os.path.exists(download_file_path):
      os.remove(download_file_path)

    (download_callback, install_callback) = (
        console_io.ProgressBar.SplitProgressBar(progress_callback, [1, 1]))

    try:
      req = ComponentInstaller.MakeRequest(url)
      try:
        total_size = float(req.info().getheader('Content-Length', '0'))
      # pylint: disable=broad-except, We never want progress bars to block an
      # update.
      except Exception:
        total_size = 0

      with open(download_file_path, 'wb') as fp:
        # This is the buffer size that shutil.copyfileobj uses.
        buf_size = 16*1024
        total_written = 0

        while True:
          buf = req.read(buf_size)
          if not buf:
            break
          fp.write(buf)
          total_written += len(buf)
          if total_size:
            download_callback(total_written / total_size)

      download_callback(1)

    except (urllib2.HTTPError, urllib2.URLError, ssl.SSLError) as e:
      raise URLFetchError(e)

    with file_utils.Context(tarfile.open(name=download_file_path)) as tar:
      members = tar.getmembers()
      total_files = float(len(members))

      files = []
      for num, member in enumerate(members, start=1):
        files.append(member.name + '/' if member.isdir() else member.name)
        tar.extract(member, extract_dir)
        install_callback(num / total_files)

      install_callback(1)

    os.remove(download_file_path)
    return files

  @staticmethod
  def MakeRequest(url):
    """Gets the request object for the given URL.

    If the URL is for cloud storage and we get a 403, this will try to load the
    active credentials and use them to authenticate the download.

    Args:
      url: str, The URL to download.

    Raises:
      AuthenticationError: If this download requires authentication and there
        are no credentials or the credentials do not have access.

    Returns:
      urllib2.Request, The request.
    """
    headers = {'Cache-Control': 'no-cache'}
    try:
      if url.startswith(ComponentInstaller.GCS_BROWSER_DL_URL):
        url = url.replace(ComponentInstaller.GCS_BROWSER_DL_URL,
                          ComponentInstaller.GCS_API_DL_URL,
                          1)
      req = urllib2.Request(url, headers=headers)
      return urllib2.urlopen(req, timeout=TIMEOUT_IN_SEC)
    except urllib2.HTTPError as e:
      if e.code != 403 or not url.startswith(ComponentInstaller.GCS_API_DL_URL):
        raise e
      try:
        creds = store.Load()
        store.Refresh(creds)
        creds.apply(headers)
      except store.Error as e:
        # If we fail here, it is because there are no active credentials or the
        # credentials are bad.
        raise AuthenticationError(
            'This component requires valid credentials to install.', e)
      try:
        # Retry the download using the credentials.
        req = urllib2.Request(url, headers=headers)
        return urllib2.urlopen(req, timeout=TIMEOUT_IN_SEC)
      except urllib2.HTTPError as e:
        if e.code != 403:
          raise e
        # If we fail again with a 403, that means we used the credentials, but
        # they didn't have access to the resource.
        raise AuthenticationError("""\
Account [{account}] does not have permission to install this component.  Please
ensure that this account should have access or run:

  $ gcloud config set account ``ACCOUNT''

to choose another account.""".format(
    account=properties.VALUES.core.account.Get()), e)
