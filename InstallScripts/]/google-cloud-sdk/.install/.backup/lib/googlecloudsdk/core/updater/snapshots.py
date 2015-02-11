# Copyright 2013 Google Inc. All Rights Reserved.

"""Classes for working with component snapshots.

A snapshot is basically a state of the world at a given point in time.  It
describes the components that exist and how they depend on each other.  This
module lets you do operations on snapshots like getting dependency closures,
as well as diff'ing snapshots.
"""

import collections
import json
import os
import re
import ssl
import urllib2

from googlecloudsdk.core import config
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.updater import installers
from googlecloudsdk.core.updater import schemas
from googlecloudsdk.core.util import console_io


class Error(exceptions.Error):
  """Base exception for the snapshots module."""
  pass


class URLFetchError(Error):
  """Error for problems fetching via HTTP."""

  def __init__(self, code=None, malformed=False, extra_repo=None):
    msg = 'Failed to fetch component listing from server.'
    if code:
      msg += ' Received response code [{0}].'.format(code)
    elif malformed:
      msg += ' The repository URL was malformed.'
    else:
      msg += ' Check your network settings and try again.'

    if extra_repo:
      msg += ('\nPlease ensure that the additional component repository [{0}] '
              'is correct and still valid.  To remove it, run:\n'
              '  $ gcloud components repositories remove {0}'
              .format(extra_repo))
    else:
      fixed_version = (properties.VALUES.component_manager.fixed_sdk_version
                       .Get())
      if fixed_version:
        msg += ('\nYou have configured your Cloud SDK installation to be fixed '
                'to version [{0}]. Make sure this is a valid archived Cloud '
                'SDK version.'.format(fixed_version))
    super(URLFetchError, self).__init__(msg)


class IncompatibleSchemaVersionError(Error):
  """Error for when we are unable to parse the new version of the snapshot."""

  def __init__(self, schema_version):
    super(IncompatibleSchemaVersionError, self).__init__(
        'The latest version snapshot is incompatible with this installation.')
    self.schema_version = schema_version


class ComponentSnapshot(object):
  """Contains a state-of-the-world for existing components.

  A snapshot can be loaded from different sources.  It can be the latest that
  exists on the server or it can be constructed from local install state.
  Either way, it describes the components that are available, how they depend
  on each other, and other information about them like descriptions and version
  information.

  Attributes:
    revision: int, The global revision number for this snapshot.  If it was
      created from an InstallState, this will be -1 to indicate that it is
      potentially a composition of more than one snapshot.
    sdk_definition: schemas.SDKDefinition, The full definition for this
      component snapshot.
    url: str, The full URL of the file from which this snapshot was loaded.
      This could be a web address like http://internet.com/components.json or
      a local file path as a URL like file:///some/local/path/components.json.
      It may also be None if the data did not come from a file.
    components = dict from component id string to schemas.Component, All the
      Components in this snapshot.
  """
  ABSOLUTE_RE = re.compile(r'^\w+://')

  @staticmethod
  def FromFile(snapshot_file):
    """Loads a snapshot from a local file.

    Args:
      snapshot_file: str, The path of the file to load.

    Returns:
      A ComponentSnapshot object
    """
    with open(snapshot_file) as input_file:
      data = json.load(input_file)
    # Windows paths will start with a drive letter so they need an extra '/' up
    # front.  Also, URLs must only have forward slashes to work correctly.
    url = ('file://' +
           ('/' if not snapshot_file.startswith('/') else '') +
           snapshot_file.replace('\\', '/'))
    return ComponentSnapshot._FromDictionary((data, url))

  @staticmethod
  def FromURLs(*urls):
    """Loads a snapshot from a series of URLs.

    Args:
      *urls: str, The URLs to the files to load.

    Returns:
      A ComponentSnapshot object.

    Raises:
      URLFetchError: If the URL cannot be fetched.
    """
    # TODO(user) Handle a json parse error here.
    first = urls[0]
    data = [
        (ComponentSnapshot._DictFromURL(url, is_extra_repo=(url != first)), url)
        for url in urls]
    return ComponentSnapshot._FromDictionary(*data)

  @staticmethod
  def _DictFromURL(url, is_extra_repo=False):
    """Loads a json dictionary from a URL.

    Args:
      url: str, The URL to the file to load.
      is_extra_repo: bool, True if this is not the primary repository.

    Returns:
      A ComponentSnapshot object.

    Raises:
      URLFetchError: If the URL cannot be fetched.
    """
    extra_repo = url if is_extra_repo else None
    try:
      response = installers.ComponentInstaller.MakeRequest(url)
    except (urllib2.HTTPError, urllib2.URLError, ssl.SSLError):
      log.debug('Could not fetch [{url}]'.format(url=url), exc_info=True)
      response = None
    except ValueError as e:
      if not e.message or 'unknown url type' not in e.message:
        raise e
      log.debug('Bad repository url: [{url}]'.format(url=url), exc_info=True)
      raise URLFetchError(malformed=True, extra_repo=extra_repo)

    if not response:
      raise URLFetchError(extra_repo=extra_repo)
    code = response.getcode()
    if code and code != 200:
      raise URLFetchError(code=code, extra_repo=extra_repo)
    data = json.loads(response.read())
    return data

  @staticmethod
  def FromInstallState(install_state):
    """Loads a snapshot from the local installation state.

    This creates a snapshot that may not have actually existed at any point in
    time.  It does, however, exactly reflect the current state of your local
    SDK.

    Args:
      install_state: install_state.InstallState, The InstallState object to load
        from.

    Returns:
      A ComponentSnapshot object.
    """
    installed = install_state.InstalledComponents()
    components = [manifest.ComponentDefinition()
                  for manifest in installed.values()]
    sdk_definition = schemas.SDKDefinition(revision=-1, schema_version=None,
                                           components=components)
    return ComponentSnapshot(sdk_definition)

  @staticmethod
  def _FromDictionary(*data):
    """Loads a snapshot from a dictionary representing the raw JSON data.

    Args:
      *data: ({}, str), A tuple of parsed JSON data and the URL it came from.

    Returns:
      A ComponentSnapshot object.

    Raises:
      IncompatibleSchemaVersionError: If the latest snapshot cannot be parsed
        by this code.
    """
    merged = None
    for (json_dictionary, url) in data:
      # Parse just the schema version first, to see if we should continue.
      schema_version = schemas.SDKDefinition.SchemaVersion(json_dictionary)
      if (schema_version.version >
          config.INSTALLATION_CONFIG.snapshot_schema_version):
        raise IncompatibleSchemaVersionError(schema_version)

      sdk_def = schemas.SDKDefinition.FromDictionary(json_dictionary)

      # Convert relative data sources into absolute URLs if a URL is given.
      if url:
        for c in sdk_def.components:
          if not c.data or not c.data.source:
            continue
          if not ComponentSnapshot.ABSOLUTE_RE.search(c.data.source):
            # This is a relative path, look relative to the snapshot file.
            c.data.source = os.path.dirname(url) + '/' + c.data.source

      if not merged:
        merged = sdk_def
      else:
        merged.Merge(sdk_def)
    return ComponentSnapshot(merged)

  def __init__(self, sdk_definition):
    self.sdk_definition = sdk_definition
    self.revision = sdk_definition.revision
    self.components = dict((c.id, c) for c in sdk_definition.components)
    deps = dict((c.id, set(c.dependencies)) for c in sdk_definition.components)
    self.__dependencies = {}
    # Prune out unknown dependencies
    for comp, dep_ids in deps.iteritems():
      self.__dependencies[comp] = set(dep_id for dep_id in dep_ids
                                      if dep_id in deps)

    self.__consumers = dict((id, set()) for id in self.__dependencies)
    for component_id, dep_ids in self.__dependencies.iteritems():
      for dep_id in dep_ids:
        self.__consumers[dep_id].add(component_id)

  def _ClosureFor(self, ids, dependencies=False, consumers=False,
                  platform_filter=None):
    """Calculates a dependency closure for the components with the given ids.

    This can calculate a dependency closure, consumer closure, or the union of
    both depending on the flags.  If both dependencies and consumers are set to
    True, this is basically calculating the set of components that are connected
    by dependencies to anything in the starting set.  The given ids, are always
    included in the output if they are valid components.

    Args:
      ids: list of str, The component ids to get the dependency closure for.
      dependencies: bool, True to add dependencies of the given components to
        the closure.
      consumers: bool, True to add consumers of the given components to the
        closure.
      platform_filter: platforms.Platform, A platform that components must
        match to be pulled into the dependency closure.

    Returns:
      set of str, The set of component ids in the closure.
    """
    closure = set()
    to_process = collections.deque(ids)
    while to_process:
      current = to_process.popleft()
      if current not in self.components or current in closure:
        continue
      if not self.components[current].platform.Matches(platform_filter):
        continue
      closure.add(current)
      if dependencies:
        to_process.extend(self.__dependencies[current])
      if consumers:
        to_process.extend(self.__consumers[current])
    return closure

  def ComponentFromId(self, component_id):
    """Gets the schemas.Component from this snapshot with the given id.

    Args:
      component_id: str, The id component to get.

    Returns:
      The corresponding schemas.Component object.
    """
    return self.components.get(component_id)

  def ComponentsFromIds(self, component_ids):
    """Gets the schemas.Component objects for each of the given ids.

    Args:
      component_ids: iterable of str, The ids of the  components to get

    Returns:
      The corresponding schemas.Component objects.
    """
    return set(self.components.get(component_id)
               for component_id in component_ids)

  def AllComponentIdsMatching(self, platform_filter):
    """Gets all components in the snapshot that match the given platform.

    Args:
      platform_filter: platforms.Platform, A platform the components must match.

    Returns:
      set(str), The matching component ids.
    """
    return set(c_id for c_id, component in self.components.iteritems()
               if component.platform.Matches(platform_filter))

  def DependencyClosureForComponents(self, component_ids, platform_filter=None):
    """Gets all the components that are depended on by any of the given ids.

    Args:
      component_ids: list of str, The ids of the components to get the
        dependencies of.
      platform_filter: platforms.Platform, A platform that components must
        match to be pulled into the dependency closure.

    Returns:
      set of str, All component ids that are in the dependency closure,
      including the given components.
    """
    return self._ClosureFor(component_ids, dependencies=True, consumers=False,
                            platform_filter=platform_filter)

  def ConsumerClosureForComponents(self, component_ids, platform_filter=None):
    """Gets all the components that depend on any of the given ids.

    Args:
      component_ids: list of str, The ids of the components to get the consumers
        of.
      platform_filter: platforms.Platform, A platform that components must
        match to be pulled into the consumer closure.

    Returns:
      set of str, All component ids that are in the consumer closure, including
      the given components.
    """
    return self._ClosureFor(component_ids, dependencies=False, consumers=True,
                            platform_filter=platform_filter)

  def ConnectedComponents(self, component_ids, platform_filter=None):
    """Gets all the components that are connected to any of the given ids.

    Connected means in the connected graph of dependencies.  This is basically
    the union of the dependency and consumer closure for the given ids.

    Args:
      component_ids: list of str, The ids of the components to get the
        connected graph of.
      platform_filter: platforms.Platform, A platform that components must
        match to be pulled into the connected graph.

    Returns:
      set of str, All component ids that are connected to the given ids,
      including the given components.
    """
    return self._ClosureFor(component_ids, dependencies=True, consumers=True,
                            platform_filter=platform_filter)

  def CreateDiff(self, latest_snapshot, platform_filter=None):
    """Creates a ComponentSnapshotDiff based on this snapshot and the given one.

    Args:
      latest_snapshot: ComponentSnapshot, The latest state of the world that we
        want to compare to.
      platform_filter: platforms.Platform, A platform that components must
        match in order to be considered for any operations.

    Returns:
      A ComponentSnapshotDiff object.
    """
    return ComponentSnapshotDiff(self, latest_snapshot,
                                 platform_filter=platform_filter)

  def WriteToFile(self, path):
    """Writes this snapshot back out to a JSON file.

    Args:
      path: str, The path of the file to write to.
    """
    with open(path, 'w') as fp:
      json.dump(self.sdk_definition.ToDictionary(),
                fp, indent=2, sort_keys=True)


class ComponentSnapshotDiff(object):
  """Provides the ability to compare two ComponentSnapshots.

  This class is used to see how the current state-of-the-word compares to what
  we have installed.  It can be for informational purposes (to list available
  updates) but also to determine specifically what components need to be
  uninstalled / installed for a specific update command.

  Attributes:
    current: ComponentSnapshot, The current snapshot state.
    latest: CompnentSnapshot, The new snapshot that is being compared.
  """

  def __init__(self, current, latest, platform_filter=None):
    """Creates a new diff between two ComponentSnapshots.

    Args:
      current: The current ComponentSnapshot
      latest: The ComponentSnapshot representing a new state we can move to
      platform_filter: platforms.Platform, A platform that components must
        match in order to be considered for any operations.
    """
    self.current = current
    self.latest = latest
    self.__platform_filter = platform_filter

    self.__all_components = (current.AllComponentIdsMatching(platform_filter) |
                             latest.AllComponentIdsMatching(platform_filter))
    self.__diffs = [ComponentDiff(component_id, current, latest)
                    for component_id in self.__all_components]

    self.__removed_components = set(diff.id for diff in self.__diffs
                                    if diff.state is ComponentState.REMOVED)
    self.__new_components = set(diff.id for diff in self.__diffs
                                if diff.state is ComponentState.NEW)
    self.__updated_components = set(diff.id for diff in self.__diffs
                                    if diff.state is
                                    ComponentState.UPDATE_AVAILABLE)

  def InvalidUpdateSeeds(self, component_ids):
    """Sees if any of the given components don't exist locally or remotely.

    Args:
      component_ids: list of str, The components that the user wants to update.

    Returns:
      set of str, The component ids that do not exist anywhere.
    """
    return set(component_ids) - self.__all_components

  def AllDiffs(self):
    """Gets all ComponentDiffs for this snapshot comparison.

    Returns:
      The list of all ComponentDiffs between the snapshots.
    """
    return self._FilterDiffs(None)

  def AvailableUpdates(self):
    """Gets ComponentDiffs for components where there is an update available.

    Returns:
      The list of ComponentDiffs.
    """
    return self._FilterDiffs(ComponentState.UPDATE_AVAILABLE)

  def AvailableToInstall(self):
    """Gets ComponentDiffs for new components that can be installed.

    Returns:
      The list of ComponentDiffs.
    """
    return self._FilterDiffs(ComponentState.NEW)

  def Removed(self):
    """Gets ComponentDiffs for components that no longer exist.

    Returns:
      The list of ComponentDiffs.
    """
    return self._FilterDiffs(ComponentState.REMOVED)

  def UpToDate(self):
    """Gets ComponentDiffs for installed components that are up to date.

    Returns:
      The list of ComponentDiffs.
    """
    return self._FilterDiffs(ComponentState.UP_TO_DATE)

  def _FilterDiffs(self, state):
    if not state:
      filtered = self.__diffs
    else:
      filtered = [diff for diff in self.__diffs if diff.state is state]
    return sorted(filtered, key=lambda d: d.name)

  def ToRemove(self, update_seed):
    """Calculate the components that need to be uninstalled.

    Based on this given set of components, determine what we need to remove.
    When an update is done, we update all components connected to the initial
    set.  Based on this, we need to remove things that have been updated, or
    that no longer exist.  This method works with ToInstall().  For a given
    update set the update process should remove anything from ToRemove()
    followed by installing everything in ToInstall().  It is possible (and
    likely) that a component will be in both of these sets (when a new version
    is available).

    Args:
      update_seed: list of str, The component ids that we want to update.

    Returns:
      set of str, The component ids that should be removed.
    """
    # Get the full set of everything that needs to be updated together that we
    # currently have installed
    connected = self.current.ConnectedComponents(update_seed)
    connected |= self.latest.ConnectedComponents(connected | set(update_seed))
    removal_candidates = connected & set(self.current.components.keys())
    # We need to remove anything that no longer exists or that has been updated
    return (self.__removed_components |
            self.__updated_components) & removal_candidates

  def ToInstall(self, update_seed):
    """Calculate the components that need to be installed.

    Based on this given set of components, determine what we need to install.
    When an update is done, we update all components connected to the initial
    set.  Based on this, we need to install things that have been updated or
    that are new.  This method works with ToRemove().  For a given update set
    the update process should remove anything from ToRemove() followed by
    installing everything in ToInstall().  It is possible (and likely) that a
    component will be in both of these sets (when a new version is available).

    Args:
      update_seed: list of str, The component ids that we want to update.

    Returns:
      set of str, The component ids that should be removed.
    """
    installed_components = self.current.components.keys()
    local_connected = self.current.ConnectedComponents(update_seed)
    all_required = self.latest.DependencyClosureForComponents(
        local_connected | set(update_seed),
        platform_filter=self.__platform_filter)

    # Add in anything in the connected graph that we already have installed.
    # Even though the update seed might not depend on it, if it was already
    # installed, it might have been removed in ToRemove() if an update was
    # available so we should put it back.
    remote_connected = self.latest.ConnectedComponents(
        local_connected | set(update_seed),
        platform_filter=self.__platform_filter)
    all_required |= remote_connected & set(installed_components)

    different = self.__new_components | self.__updated_components

    # all new or updated components, or if it has not been changed but we
    # don't have it
    return set(c for c in all_required
               if c in different or c not in installed_components)

  def DetailsForCurrent(self, component_ids):
    """Gets the schema.Component objects for all ids from the current snapshot.

    Args:
      component_ids: list of str, The component ids to get.

    Returns:
      A list of schema.Component objects sorted by component display name.
    """
    return sorted(self.current.ComponentsFromIds(component_ids),
                  key=lambda c: c.details.display_name)

  def DetailsForLatest(self, component_ids):
    """Gets the schema.Component objects for all ids from the latest snapshot.

    Args:
      component_ids: list of str, The component ids to get.

    Returns:
      A list of schema.Component objects sorted by component display name.
    """
    return sorted(self.latest.ComponentsFromIds(component_ids),
                  key=lambda c: c.details.display_name)


class ComponentDiff(object):
  """Encapsulates the difference for a single component between snapshots.

  Attributes:
    id: str, The component id.
    name: str, The display name of the component.
    current: schemas.Component, The current component definition.
    latest: schemas.Component, The latest component definition that we can move
      to.
    state: ComponentState constant, The type of difference that exists for this
      component between the given snapshots.
  """

  def __init__(self, component_id, current_snapshot, latest_snapshot):
    """Create a new diff.

    Args:
      component_id: str, The id of this component.
      current_snapshot: ComponentSnapshot, The base snapshot to compare against.
      latest_snapshot: ComponentSnapshot, The new snapshot.
    """
    self.id = component_id
    self.current = current_snapshot.ComponentFromId(component_id)
    self.latest = latest_snapshot.ComponentFromId(component_id)
    self.__current_version_string = (self.current.version.version_string
                                     if self.current else 'None')
    self.__latest_version_string = (self.latest.version.version_string
                                    if self.latest else 'None')

    data_provider = self.latest if self.latest else self.current
    self.name = data_provider.details.display_name
    self.is_hidden = data_provider.is_hidden
    self.is_configuration = data_provider.is_configuration
    self.size_string = data_provider.SizeString()
    self.state = self._ComputeState()

  def _ComputeState(self):
    if self.current is None:
      return ComponentState.NEW
    elif self.latest is None:
      return ComponentState.REMOVED
    elif self.latest.version.build_number > self.current.version.build_number:
      return ComponentState.UPDATE_AVAILABLE
    # We have a more recent version than the latest.  This can happen because we
    # don't release updated components if they contained identical code.  Check
    # to see if the checksums match, and suppress the update if they are the
    # same.
    elif self.latest.version.build_number < self.current.version.build_number:
      # Component has no data at all, don't flag it as an update.
      if self.latest.data is None and self.current.data is None:
        return ComponentState.UP_TO_DATE
      # One has data and the other does not.  This is clearly a change.
      elif bool(self.latest.data) ^ bool(self.current.data):
        return ComponentState.UPDATE_AVAILABLE
      # Both have data, check to see if they are the same.
      elif (self.latest.data.contents_checksum !=
            self.current.data.contents_checksum):
        return ComponentState.UPDATE_AVAILABLE
    return ComponentState.UP_TO_DATE

  @staticmethod
  def TablePrinter(show_versions=False):
    """Gets a console_io.TablePrinter for printing ComponentSnapshotDiffs.

    Args:
      show_versions: bool, True to display version information.  Defaults to
        False.

    Returns:
      console_io.TablePrinter: The table printer to use to print this object
      type.
    """
    if show_versions:
      headers = ('Status', 'Name', 'ID', 'Installed', 'Latest', 'Size')
      justification = (console_io.TablePrinter.JUSTIFY_LEFT,
                       console_io.TablePrinter.JUSTIFY_LEFT,
                       console_io.TablePrinter.JUSTIFY_LEFT,
                       console_io.TablePrinter.JUSTIFY_RIGHT,
                       console_io.TablePrinter.JUSTIFY_RIGHT,
                       console_io.TablePrinter.JUSTIFY_RIGHT)
    else:
      headers = ('Status', 'Name', 'ID', 'Size')
      justification = (console_io.TablePrinter.JUSTIFY_LEFT,
                       console_io.TablePrinter.JUSTIFY_LEFT,
                       console_io.TablePrinter.JUSTIFY_LEFT,
                       console_io.TablePrinter.JUSTIFY_RIGHT)
    return console_io.TablePrinter(headers, justification=justification)

  def AsTableRow(self, show_versions=False):
    """Gets this ComponentSnapshotDiff to print as a table row.

    Args:
      show_versions: bool, True to display version information.  Defaults to
        False.

    Returns:
      A tuple for use with the console_io.TablePrinter created with the
      TablePrinter() method.
    """
    if show_versions:
      return (self.state.name, self.name, self.id,
              self.__current_version_string, self.__latest_version_string,
              self.size_string)
    return (self.state.name, self.name, self.id, self.size_string)

  def __str__(self):
    return (
        '[ {status} ]\t{name} ({id})\t[{current_version}]\t[{latest_version}]'
        .format(status=self.state.name, name=self.name, id=self.id,
                current_version=self.__current_version_string,
                latest_version=self.__latest_version_string))


class ComponentState(object):
  """An enum for the available update states."""
  _COMPONENT_STATE_TUPLE = collections.namedtuple('ComponentStateTuple',
                                                  ['name'])
  UP_TO_DATE = _COMPONENT_STATE_TUPLE('Installed')
  UPDATE_AVAILABLE = _COMPONENT_STATE_TUPLE('Update Available')
  REMOVED = _COMPONENT_STATE_TUPLE('Deprecated')
  NEW = _COMPONENT_STATE_TUPLE('Not Installed')

  @staticmethod
  def All():
    """Gets all the different states.

    Returns:
      list(ComponentStateTuple), All the states.
    """
    return [ComponentState.UPDATE_AVAILABLE, ComponentState.REMOVED,
            ComponentState.NEW, ComponentState.UP_TO_DATE]
