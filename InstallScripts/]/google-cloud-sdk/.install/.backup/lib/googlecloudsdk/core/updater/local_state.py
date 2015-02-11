# Copyright 2013 Google Inc. All Rights Reserved.

"""Manages the state of what is installed in the cloud SDK.

This tracks the installed modules along with the files they created.  It also
provides functionality like extracting tar files into the installation and
tracking when we check for updates.
"""

import errno
import json
import logging
import os
import shutil
import sys
import time

from googlecloudsdk.core import config
from googlecloudsdk.core import exceptions
from googlecloudsdk.core.updater import installers
from googlecloudsdk.core.updater import snapshots
from googlecloudsdk.core.util import console_io
from googlecloudsdk.core.util import files as file_utils


class Error(exceptions.Error):
  """Base exception for the local_state module."""
  pass


class InvalidSDKRootError(Error):
  """Error for when the root of the Cloud SDK is invalid or cannot be found."""

  def __init__(self):
    super(InvalidSDKRootError, self).__init__(
        'The update action could not be performed because the installation root'
        ' of the Cloud SDK could not be located.  Please re-install the Cloud '
        'SDK and try again.')


class InvalidDownloadError(Error):
  """Exception for when the SDK that was download was invalid."""

  def __init__(self):
    super(InvalidDownloadError, self).__init__(
        'The Cloud SDK download was invalid.')


class PermissionsError(Error):
  """Error for when a file operation cannot complete due to permissions."""

  def __init__(self, message, path):
    """Initialize a PermissionsError.

    Args:
      message: str, The message from the underlying error.
      path: str, The absolute path to a file or directory that needs to be
          operated on, but can't because of insufficient permissions.
    """
    super(PermissionsError, self).__init__(
        '{message}: [{path}]\n\nEnsure you have the permissions to access the '
        'file and that the file is not in use.'
        .format(message=message, path=path))


def _RaisesPermissionsError(func):
  """Use this decorator for functions that deal with files.

  If an exception indicating file permissions is raised, this decorator will
  raise a PermissionsError instead, so that the caller only has to watch for
  one type of exception.

  Args:
    func: The function to decorate.

  Returns:
    A decorator.
  """

  def _TryFunc(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except (OSError, IOError) as e:
      if e.errno == errno.EACCES:
        new_exc = PermissionsError(
            message=e.strerror, path=os.path.abspath(e.filename))
        # Maintain original stack trace.
        raise new_exc, None, sys.exc_info()[2]
      raise
    except shutil.Error as e:
      args = e.args[0][0]
      # unfortunately shutil.Error *only* has formatted strings to inspect.
      # Looking for this substring is looking for errno.EACCES, which has
      # a numeric value of 13.
      if args[2].startswith('[Errno 13]'):
        new_exc = PermissionsError(
            message=args[2], path=os.path.abspath(args[0]))
        # Maintain original stack trace.
        raise new_exc, None, sys.exc_info()[2]
      raise
  return _TryFunc


class InstallationState(object):
  """The main class for checking / updating local installation state."""

  STATE_DIR_NAME = config.Paths.CLOUDSDK_STATE_DIR
  BACKUP_DIR_NAME = '.backup'
  TRASH_DIR_NAME = '.trash'
  STAGING_ROOT_SUFFIX = '.staging'
  COMPONENT_SNAPSHOT_FILE_SUFFIX = '.snapshot.json'

  @staticmethod
  def ForCurrent():
    """Gets the installation state for the SDK that this code is running in.

    Returns:
      InstallationState, The state for this area.

    Raises:
      InvalidSDKRootError: If this code is not running under a valid SDK.
    """
    sdk_root = config.Paths().sdk_root
    if not sdk_root:
      raise InvalidSDKRootError()
    return InstallationState(os.path.realpath(sdk_root))

  @staticmethod
  def VersionForInstalledComponent(component_id):
    """Gets the version string for the given installed component.

    This function is to be used to get component versions for metrics reporting.
    If it fails in any way or if the component_id is unknown, it will return
    None.  This prevents errors from surfacing when the version is needed
    strictly for reporting purposes.

    Args:
      component_id: str, The component id of the component you want the version
        for.

    Returns:
      str, The installed version of the component, or None if it is not
        installed or if an error occurs.
    """
    try:
      state = InstallationState.ForCurrent()
      # pylint: disable=protected-access, This is the same class.
      return InstallationManifest(
          state._state_directory, component_id).VersionString()
    # pylint: disable=bare-except, We never want to fail because of metrics.
    except:
      logging.debug('Failed to get installed version for component [%s]: [%s]',
                    component_id, sys.exc_info())
    return None

  @_RaisesPermissionsError
  def __init__(self, sdk_root):
    """Initializes the installation state for the given sdk install.

    Args:
      sdk_root: str, The file path of the root of the SDK installation.

    Raises:
      ValueError: If the given SDK root does not exist.
    """
    if not os.path.isdir(sdk_root):
      raise ValueError('The given Cloud SDK root does not exist: [{}]'
                       .format(sdk_root))

    self.__sdk_root = sdk_root
    self._state_directory = os.path.join(sdk_root,
                                         InstallationState.STATE_DIR_NAME)
    self.__backup_directory = os.path.join(self._state_directory,
                                           InstallationState.BACKUP_DIR_NAME)
    self.__trash_directory = os.path.join(self._state_directory,
                                          InstallationState.TRASH_DIR_NAME)

    self.__sdk_staging_root = (os.path.normpath(self.__sdk_root) +
                               InstallationState.STAGING_ROOT_SUFFIX)

    for d in [self._state_directory]:
      if not os.path.isdir(d):
        file_utils.MakeDir(d)

  @property
  def sdk_root(self):
    """Gets the root of the SDK that this state corresponds to.

    Returns:
      str, the path to the root directory.
    """
    return self.__sdk_root

  def _FilesForSuffix(self, suffix):
    """Returns the files in the state directory that have the given suffix.

    Args:
      suffix: str, The file suffix to match on.

    Returns:
      list of str, The file names that match.
    """
    files = os.listdir(self._state_directory)
    matching = [f for f in files
                if os.path.isfile(os.path.join(self._state_directory, f))
                and f.endswith(suffix)]
    return matching

  @_RaisesPermissionsError
  def InstalledComponents(self):
    """Gets all the components that are currently installed.

    Returns:
      A dictionary of component id string to InstallationManifest.
    """
    snapshot_files = self._FilesForSuffix(
        InstallationState.COMPONENT_SNAPSHOT_FILE_SUFFIX)
    manifests = {}
    for f in snapshot_files:
      component_id = f[:-len(InstallationState.COMPONENT_SNAPSHOT_FILE_SUFFIX)]
      manifests[component_id] = InstallationManifest(self._state_directory,
                                                     component_id)
    return manifests

  @_RaisesPermissionsError
  def Snapshot(self):
    """Generates a ComponentSnapshot from the currently installed components."""
    return snapshots.ComponentSnapshot.FromInstallState(self)

  def LastUpdateCheck(self):
    """Gets a LastUpdateCheck object to check update status."""
    return LastUpdateCheck(self)

  def DiffCurrentState(self, latest_snapshot, platform_filter=None):
    """Generates a ComponentSnapshotDiff from current state and the given state.

    Args:
      latest_snapshot:  snapshots.ComponentSnapshot, The current state of the
        world to diff against.
      platform_filter: platforms.Platform, A platform that components must
        match in order to be considered for any operations.

    Returns:
      A ComponentSnapshotDiff.
    """
    return self.Snapshot().CreateDiff(latest_snapshot,
                                      platform_filter=platform_filter)

  @_RaisesPermissionsError
  def CloneToStaging(self, progress_callback=None):
    """Clones this state to the temporary staging area.

    This is used for making temporary copies of the entire Cloud SDK
    installation when doing updates.  The entire installation is cloned, but
    doing so removes any backups and trash from this state before doing the
    copy.

    Args:
      progress_callback: f(float), A function to call with the fraction of
        completeness.

    Returns:
      An InstallationState object for the cloned install.
    """
    (rm_staging_cb, rm_backup_cb, rm_trash_cb, copy_cb) = (
        console_io.ProgressBar.SplitProgressBar(progress_callback,
                                                [1, 1, 1, 7]))

    self._ClearStaging(progress_callback=rm_staging_cb)
    self.ClearBackup(progress_callback=rm_backup_cb)
    self.ClearTrash(progress_callback=rm_trash_cb)

    class Counter(object):

      def __init__(self, progress_callback, total):
        self.count = 0
        self.progress_callback = progress_callback
        self.total = float(total)

      # This function must match the signature that shutil expects for the
      # ignore function.
      def Tick(self, *unused_args):
        self.count += 1
        self.progress_callback(self.count / self.total)
        return []

    if progress_callback:
      # This takes a little time, so only do it if we are going to report
      # progress.
      dirs = set()
      for _, manifest in self.InstalledComponents().iteritems():
        dirs.update(manifest.InstalledDirectories())
      # There is always the root directory itself and the .install directory.
      # In general, there could be in the SDK (if people just put stuff in there
      # but this is fine for an estimate.  The progress bar will at worst stay
      # at 100% for slightly longer.
      total_dirs = len(dirs) + 2
      ticker = Counter(copy_cb, total_dirs).Tick if total_dirs else None
    else:
      ticker = None

    shutil.copytree(self.__sdk_root, self.__sdk_staging_root, symlinks=True,
                    ignore=ticker)
    return InstallationState(self.__sdk_staging_root)

  @_RaisesPermissionsError
  def CreateStagingFromDownload(self, url):
    """Creates a new staging area from a fresh download of the Cloud SDK.

    Args:
      url: str, The url to download the new SDK from.

    Returns:
      An InstallationState object for the new install.

    Raises:
      installers.URLFetchError: If the new SDK could not be downloaded.
      InvalidDownloadError: If the new SDK was malformed.
    """
    self._ClearStaging()

    with file_utils.TemporaryDirectory() as t:
      download_dir = os.path.join(t, '.download')
      extract_dir = os.path.join(t, '.extract')
      installers.ComponentInstaller.DownloadAndExtractTar(
          url, download_dir, extract_dir)
      files = os.listdir(extract_dir)
      if len(files) != 1:
        raise InvalidDownloadError()
      sdk_root = os.path.join(extract_dir, files[0])
      file_utils.MoveDir(sdk_root, self.__sdk_staging_root)

    staging_sdk = InstallationState(self.__sdk_staging_root)
    self.CopyMachinePropertiesTo(staging_sdk)
    return staging_sdk

  @_RaisesPermissionsError
  def ReplaceWith(self, other_install_state):
    """Replaces this installation with the given other installation.

    This moves the current installation to the backup directory of the other
    installation.  Then, it moves the entire second installation to replace
    this one on the file system.  The result is that the other installation
    completely replaces the current one, but the current one is snapshotted and
    stored as a backup under the new one (and can be restored later).

    Args:
      other_install_state: InstallationState, The other state with which to
        replace this one.
    """
    self.ClearBackup()
    self.ClearTrash()
    other_install_state.ClearBackup()
    # pylint: disable=protected-access, This is an instance of InstallationState
    file_utils.MoveDir(self.__sdk_root, other_install_state.__backup_directory)
    file_utils.MoveDir(other_install_state.__sdk_root, self.__sdk_root)

  @_RaisesPermissionsError
  def RestoreBackup(self):
    """Restore the backup from this install state if it exists.

    If this installation has a backup stored in it (created by and update that
    used ReplaceWith(), above), it replaces this installation with the backup,
    using a temporary staging area.  This installation is moved to the trash
    directory under the installation that exists after this is done.  The trash
    directory can be removed at any point in the future.  We just don't want to
    delete code that is running since some platforms have a problem with that.

    Returns:
      bool, True if there was a backup to restore, False otherwise.
    """
    if not self.HasBackup():
      return False

    self._ClearStaging()

    file_utils.MoveDir(self.__backup_directory, self.__sdk_staging_root)
    staging_state = InstallationState(self.__sdk_staging_root)
    staging_state.ClearTrash()
    # pylint: disable=protected-access, This is an instance of InstallationState
    file_utils.MoveDir(self.__sdk_root, staging_state.__trash_directory)
    file_utils.MoveDir(staging_state.__sdk_root, self.__sdk_root)
    return True

  def HasBackup(self):
    """Determines if this install has a valid backup that can be restored.

    Returns:
      bool, True if there is a backup, False otherwise.
    """
    return os.path.isdir(self.__backup_directory)

  def BackupDirectory(self):
    """Gets the backup directory of this installation if it exists.

    Returns:
      str, The path to the backup directory or None if it does not exist.
    """
    if self.HasBackup():
      return self.__backup_directory
    return None

  @_RaisesPermissionsError
  def _ClearStaging(self, progress_callback=None):
    """Deletes the current staging directory if it exists.

    Args:
      progress_callback: f(float), A function to call with the fraction of
        completeness.
    """
    if os.path.exists(self.__sdk_staging_root):
      file_utils.RmTree(self.__sdk_staging_root)
    if progress_callback:
      progress_callback(1)

  @_RaisesPermissionsError
  def ClearBackup(self, progress_callback=None):
    """Deletes the current backup if it exists.

    Args:
      progress_callback: f(float), A function to call with the fraction of
        completeness.
    """
    if os.path.isdir(self.__backup_directory):
      file_utils.RmTree(self.__backup_directory)
    if progress_callback:
      progress_callback(1)

  @_RaisesPermissionsError
  def ClearTrash(self, progress_callback=None):
    """Deletes the current trash directory if it exists.

    Args:
      progress_callback: f(float), A function to call with the fraction of
        completeness.
    """
    if os.path.isdir(self.__trash_directory):
      file_utils.RmTree(self.__trash_directory)
    if progress_callback:
      progress_callback(1)

  def _GetInstaller(self, snapshot):
    """Gets a component installer based on the given snapshot.

    Args:
      snapshot: snapshots.ComponentSnapshot, The snapshot that describes the
        component to install.

    Returns:
      The installers.ComponentInstaller.
    """
    return installers.ComponentInstaller(self.__sdk_root,
                                         self._state_directory,
                                         snapshot)

  @_RaisesPermissionsError
  def Install(self, snapshot, component_id, progress_callback=None):
    """Installs the given component based on the given snapshot.

    Args:
      snapshot: snapshots.ComponentSnapshot, The snapshot that describes the
        component to install.
      component_id: str, The component to install from the given snapshot.
      progress_callback: f(float), A function to call with the fraction of
        completeness.

    Raises:
      installers.URLFetchError: If the component associated with the provided
        component ID has a URL that is not fetched correctly.
    """
    files = self._GetInstaller(snapshot).Install(
        component_id, progress_callback=progress_callback)
    manifest = InstallationManifest(self._state_directory, component_id)
    manifest.MarkInstalled(snapshot, files)

  @_RaisesPermissionsError
  def Uninstall(self, component_id, progress_callback=None):
    """Uninstalls the given component.

    Deletes all the files for this component and marks it as no longer being
    installed.

    Args:
      component_id: str, The id of the component to uninstall.
      progress_callback: f(float), A function to call with the fraction of
        completeness.
    """
    manifest = InstallationManifest(self._state_directory, component_id)
    paths = manifest.InstalledPaths()
    total_paths = float(len(paths))
    root = self.__sdk_root

    dirs_to_remove = set()
    for num, p in enumerate(paths, start=1):
      path = os.path.join(root, p)
      if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)
        # Clean up the pyc files that correspond to any py files being removed.
        if p.endswith('.py'):
          pyc_path = path + 'c'
          if os.path.isfile(pyc_path):
            os.remove(pyc_path)
        dir_path = os.path.dirname(path)
        if dir_path:
          dirs_to_remove.add(os.path.normpath(dir_path))
      elif os.path.isdir(path):
        dirs_to_remove.add(os.path.normpath(path))
      if progress_callback:
        progress_callback(num / total_paths)

    # Remove dirs from the bottom up.  Subdirs will always have a longer path
    # than it's parent.
    for d in sorted(dirs_to_remove, key=len, reverse=True):
      if os.path.isdir(d) and not os.path.islink(d) and not os.listdir(d):
        os.rmdir(d)

    manifest.MarkUninstalled()

  def CopyMachinePropertiesTo(self, other_state):
    """Copy this state's properties file to another state.

    This is primarily intended to be used to maintain the machine properties
    file during a schema-change-induced reinstall.

    Args:
      other_state: InstallationState, The installation state of the fresh
          Cloud SDK that needs the properties file mirrored in.
    """
    my_properties = os.path.join(
        self.sdk_root, config.Paths.CLOUDSDK_PROPERTIES_NAME)
    other_properties = os.path.join(
        other_state.sdk_root, config.Paths.CLOUDSDK_PROPERTIES_NAME)
    if not os.path.exists(my_properties):
      return
    shutil.copyfile(my_properties, other_properties)


class InstallationManifest(object):
  """Class to encapsulate the data stored in installation manifest files."""

  MANIFEST_SUFFIX = '.manifest'

  def __init__(self, state_dir, component_id):
    """Creates a new InstallationManifest.

    Args:
      state_dir: str, The directory path where install state is stored.
      component_id: str, The component id that you want to get the manifest for.
    """
    self.state_dir = state_dir
    self.id = component_id
    self.snapshot_file = os.path.join(
        self.state_dir,
        component_id + InstallationState.COMPONENT_SNAPSHOT_FILE_SUFFIX)
    self.manifest_file = os.path.join(
        self.state_dir,
        component_id + InstallationManifest.MANIFEST_SUFFIX)

  def MarkInstalled(self, snapshot, files):
    """Marks this component as installed with the given snapshot and files.

    This saves the ComponentSnapshot and writes the installed files to a
    manifest so they can be removed later.

    Args:
      snapshot: snapshots.ComponentSnapshot, The snapshot that was the source
        of the install.
      files: list of str, The files that were created by the installation.
    """
    with open(self.manifest_file, 'w') as fp:
      for f in files:
        fp.write(f + '\n')
    snapshot.WriteToFile(self.snapshot_file)

  def MarkUninstalled(self):
    """Marks this component as no longer being installed.

    This does not actually uninstall the component, but rather just removes the
    snapshot and manifest.
    """
    for f in [self.manifest_file, self.snapshot_file]:
      if os.path.isfile(f):
        os.remove(f)

  def ComponentSnapshot(self):
    """Loads the local ComponentSnapshot for this component.

    Returns:
      The snapshots.ComponentSnapshot for this component.
    """
    return snapshots.ComponentSnapshot.FromFile(self.snapshot_file)

  def ComponentDefinition(self):
    """Loads the ComponentSnapshot and get the schemas.Component this component.

    Returns:
      The schemas.Component for this component.
    """
    return self.ComponentSnapshot().ComponentFromId(self.id)

  def VersionString(self):
    """Gets the version string of this component as it was installed.

    Returns:
      str, The installed version of this component.
    """
    return self.ComponentDefinition().version.version_string

  def InstalledPaths(self):
    """Gets the list of files and dirs created by installing this component.

    Returns:
      list of str, The files and directories installed by this component.
    """
    with open(self.manifest_file) as f:
      files = [line.rstrip() for line in f]
    return files

  def InstalledDirectories(self):
    """Gets the set of directories created by installing this component.

    Returns:
      set(str), The directories installed by this component.
    """
    with open(self.manifest_file) as f:
      dirs = set()
      for line in f:
        fixed = line.rstrip()
        if fixed.endswith('/'):
          dirs.add(fixed)
    return dirs


class LastUpdateCheck(object):
  """A class to encapsulate information on when we last checked for updates."""

  LAST_UPDATE_CHECK_FILE = 'last_update_check.json'
  DATE = 'date'
  LAST_NAG_DATE = 'last_nag_date'
  REVISION = 'revision'
  UPDATES_AVAILABLE = 'updates_available'

  def __init__(self, install_state):
    self.__install_state = install_state
    # pylint: disable=protected-access, These classes work together
    self.__last_update_check_file = os.path.join(
        install_state._state_directory, LastUpdateCheck.LAST_UPDATE_CHECK_FILE)
    self._LoadData()

  def _LoadData(self):
    """Deserializes data from the json file."""
    self.__dirty = False
    if not os.path.isfile(self.__last_update_check_file):
      data = {}
    else:
      with open(self.__last_update_check_file) as fp:
        data = json.loads(fp.read())
    self.__last_update_check_date = data.get(LastUpdateCheck.DATE, 0)
    self.__last_nag_date = data.get(LastUpdateCheck.LAST_NAG_DATE, 0)
    self.__last_update_check_revision = data.get(LastUpdateCheck.REVISION, 0)
    self.__updates_available = data.get(LastUpdateCheck.UPDATES_AVAILABLE,
                                        False)

  def _SaveData(self):
    """Serializes data to the json file."""
    if not self.__dirty:
      return
    data = {LastUpdateCheck.DATE: self.__last_update_check_date,
            LastUpdateCheck.LAST_NAG_DATE: self.__last_nag_date,
            LastUpdateCheck.REVISION: self.__last_update_check_revision,
            LastUpdateCheck.UPDATES_AVAILABLE: self.__updates_available}
    with open(self.__last_update_check_file, 'w') as fp:
      fp.write(json.dumps(data))
    self.__dirty = False

  def __enter__(self):
    return self

  def __exit__(self, *args):
    self._SaveData()

  def UpdatesAvailable(self):
    """Returns whether we already know about updates that are available.

    Returns:
      bool, True if we know about updates, False otherwise.
    """
    return self.__updates_available

  def LastUpdateCheckRevision(self):
    """Gets the revision of the snapshot from the last update check.

    Returns:
      int, The revision of the last checked snapshot.
    """
    return self.__last_update_check_revision

  def LastUpdateCheckDate(self):
    """Gets the time of the last update check as seconds since the epoch.

    Returns:
      int, The time of the last update check.
    """
    return self.__last_update_check_date

  def LastNagDate(self):
    """Gets the time when the last nag was printed as seconds since the epoch.

    Returns:
      int, The time of the last nag.
    """
    return self.__last_nag_date

  def SecondsSinceLastUpdateCheck(self):
    """Gets the number of seconds since we last did an update check.

    Returns:
      int, The amount of time in seconds.
    """
    return time.time() - self.__last_update_check_date

  def SecondsSinceLastNag(self):
    """Gets the number of seconds since we last printed that there were updates.

    Returns:
      int, The amount of time in seconds.
    """
    return time.time() - self.__last_nag_date

  @_RaisesPermissionsError
  def SetFromSnapshot(self, snapshot, force=False):
    """Sets that we just did an update check and found the given snapshot.

    If the given snapshot is different that the last one we saw, this will also
    diff the new snapshot with the current install state to refresh whether
    there are components available for update.

    You must call Save() to persist these changes.

    Args:
      snapshot: snapshots.ComponentSnapshot, The snapshot pulled from the
        server.
      force: bool, True to force a recalculation of whether there are available
        updates, even if the snapshot revision has not changed.

    Returns:
      bool, True if there are now components to update, False otherwise.
    """
    if force or self.__last_update_check_revision != snapshot.revision:
      diff = self.__install_state.DiffCurrentState(snapshot)
      self.__updates_available = bool(diff.AvailableUpdates())
      self.__last_update_check_revision = snapshot.revision

    self.__last_update_check_date = time.time()
    self.__dirty = True
    return self.__updates_available

  def SetFromIncompatibleSchema(self):
    """Sets that we just did an update check and found a new schema version.

    You must call Save() to persist these changes.
    """
    self.__updates_available = True
    self.__last_update_check_revision = 0  # Doesn't matter
    self.__last_update_check_date = time.time()
    self.__dirty = True

  def SetNagged(self):
    """Sets that we printed the update nag."""
    self.__last_nag_date = time.time()
    self.__dirty = True

  def Save(self):
    """Saves the changes we made to this object."""
    self._SaveData()
