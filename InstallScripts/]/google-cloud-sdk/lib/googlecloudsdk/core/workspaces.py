# Copyright 2013 Google Inc. All Rights Reserved.

"""Manage gcloud workspaces.

A gcloud workspace is a directory that contains a .gcloud folder. This module
does manipulations of the gcloud workspace, including creation and component
importing.
"""

import errno
import os
import os.path
import re
import subprocess
import textwrap
import uritemplate

from googlecloudsdk.core import config
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.util import compat26
from googlecloudsdk.core.util import files
from googlecloudsdk.core.util import platforms

# This regular expression is used to extract the URL of the 'origin' remote by
# scraping 'git remote show origin'.
_ORIGIN_URL_RE = re.compile(r'remote origin\n.*Fetch URL: (?P<url>.+)\n', re.M)
# This is the minimum version of git required to use credential helpers.
_HELPER_MIN = (1, 7, 9)

DEFAULT_REPOSITORY_ALIAS = 'default'


class Error(Exception):
  """Exceptions for this module."""


class UnknownRepositoryAliasException(Error):
  """Exception to be thrown when a repository alias provided cannot be found."""


class CannotInitRepositoryException(Error):
  """Exception to be thrown when a repository cannot be created."""


class CannotFetchRepositoryException(Error):
  """Exception to be thrown when a repository cannot be fetched."""


class NoSuchCategoryException(Error):
  """Exception to be thrown when a category is unknown."""

  def __init__(self, category):
    super(NoSuchCategoryException, self).__init__(
        'Unknown category "{category}".'.format(category))
    self.category = category


class InvalidWorkspaceException(Error):

  def __init__(self, path, gcloud_path):
    """Creates a new InvalidWorkspaceException.

    Used when it is impossible to create a gcloud workspace because it would be
    contained in another gcloud workspace.

    Args:
      path: The path that cannot be a new gcloud workspace.
      gcloud_path: The gcloud workspace that blocks path.
    """
    message = ('Cannot initialize gcloud workspace in [{0}] (blocked by [{1}]).'
               .format(path, gcloud_path))
    super(InvalidWorkspaceException, self).__init__(message)
    self.blocking_path = gcloud_path
    self.path = path


class NoWorkspaceException(Error):

  def __init__(self, path):
    """Creates a new NoWorkspaceException.

    Used when there is no workspace at the provided path.

    Args:
      path: The path that is not in a gcloud workspace.
    """
    message = 'Cannot find workspace in [{0}].'.format(path)
    super(NoWorkspaceException, self).__init__(message)
    self.path = path


class CannotCreateWorkspaceException(Error):

  def __init__(self, path):
    """Creates a new CannotCreateWorkspaceException.

    Args:
      path: The path that cannot be used to create a gcloud workspace.
    """
    message = 'Cannot create workspace at [{0}].'.format(path)
    super(CannotCreateWorkspaceException, self).__init__(message)


class NoContainingWorkspaceException(Error):

  def __init__(self, path):
    """Creates a new NoContainingWorkspaceException.

    Args:
      path: The path that is not in a gcloud workspace.
    """
    message = ('Cannot find workspace containing [{0}].'
               .format(path))
    super(NoContainingWorkspaceException, self).__init__(message)


class GitVersionException(Error):
  """Exceptions for when git version is too old."""

  def __init__(self, fmtstr, cur_version, min_version):
    super(GitVersionException, self).__init__(
        fmtstr.format(cur_version=cur_version, min_version=min_version))


class InvalidGitException(Error):
  """Exceptions for when git version is empty or invalid."""

  def __init__(self, message):
    super(InvalidGitException, self).__init__(message)


def CheckGitVersion(version_lower_bound):
  """Returns true when version of git is >= min_version.

  Args:
    version_lower_bound: (int,int,int), The lowest allowed version.

  Returns:
    True if version >= min_version.
  """
  try:
    output = compat26.subprocess.check_output(['git', 'version'])
    if not output:
      raise InvalidGitException('The git version string is empty.')
    if not output.startswith('git version '):
      raise InvalidGitException(('The git version string must start with '
                                 'git version .'))
    match = re.search(r'(\d+)\.(\d+)\.(\d+)', output)
    if not match:
      raise InvalidGitException('The git version string must contain a '
                                'version number.')
    cur_version = match.group(1, 2, 3)
    current_version = tuple([int(item) for item in cur_version])
    if current_version < version_lower_bound:
      min_version = '.'.join(str(i) for i in version_lower_bound)
      raise GitVersionException(
          ('Your git version {cur_version} is older than the minimum version '
           '{min_version}. Please install a newer version of git.'),
          output, min_version)
  except OSError as e:
    if e.errno == errno.ENOENT:
      raise NoGitException()
    raise
  return True


class NoGitException(Error):
  """Exceptions for when git is not available."""

  def __init__(self):
    super(NoGitException, self).__init__(
        textwrap.dedent("""\
        Cannot find git. Please install git and try again.

        You can find git installers at [http://git-scm.com/downloads], or use
        your favorite package manager to install it on your computer.
        """))


def EnsureGit(func):
  """Wrap a function that uses subprocess to invoke git, make it check for git.

  Args:
    func: func, A function that uses subprocess to invoke git.

  Returns:
    The decorated function.

  Raises:
    NoGitException: If git cannot be run.
  """
  def GitFunc(*args, **kwargs):
    CheckGitVersion((0, 0, 0))
    try:
      func(*args, **kwargs)
    except OSError as e:
      if e.errno == errno.ENOENT:
        raise NoGitException()
      else:
        raise
  return GitFunc


def _GetRepositoryURI(project, alias):
  """Get the URI for a repository, given its project and alias.

  Args:
    project: str, The project name.
    alias: str, The repository alias.

  Returns:
    str, The repository URI. Or None, if it's not a valid repository.
  """
  if alias != DEFAULT_REPOSITORY_ALIAS:
    return None

  return uritemplate.expand(
      'https://source.developers.google.com/p/{project}/r/{alias}',
      {'project': project, 'alias': alias})


def Create(root_directory):
  """Create a workspace at the provided root directory and return it.

  Args:
    root_directory: str, Where to root the new workspace.

  Returns:
    The Workspace.

  Raises:
    InvalidWorkspaceException: If the desired directory is already in an
        existing gcloud workspace.
    CannotCreateWorkspaceException: If the directory for the workspace does not
        exist.
  """

  containing_workspace = files.FindDirectoryContaining(
      root_directory, config.Paths.CLOUDSDK_WORKSPACE_CONFIG_DIR_NAME)
  if containing_workspace:
    raise InvalidWorkspaceException(root_directory, containing_workspace)

  if not os.path.exists(root_directory):
    raise CannotCreateWorkspaceException(root_directory)

  workspace_config_path = os.path.join(
      root_directory,
      config.Paths.CLOUDSDK_WORKSPACE_CONFIG_DIR_NAME)

  files.MakeDir(workspace_config_path)

  log.status.write('Initialized gcloud directory in [{path}].\n'.format(
      path=workspace_config_path))

  return Workspace(root_directory=root_directory)


def FromCWD():
  """Get a workspace containing the current working directory.

  Returns:
    Workspace, The Workspace object.

  Raises:
    NoContainingWorkspaceException: If no workspace can be found containing
      current working direction.
  """
  workspace_dir = config.Paths().workspace_dir
  if not workspace_dir:
    raise NoContainingWorkspaceException(os.getcwd())
  return Workspace(workspace_dir)


class Workspace(object):
  """gcloud workspace.

  Attributes:
    root_directory: str, The path to the directory containing this workspace.
        Contains a subdirectory '.gcloud'.

  """

  def __init__(self, root_directory):
    """Get an existing workspace.

    Args:
      root_directory: str, The path to the root directory, which must contain
          a '.gcloud' directory.

    Raises:
      NoWorkspaceException: If root_directory is not None and is not the root
          of a workspace.
      NoContainingWorkspaceException: If root_directory is None and the cwd is
          not contained in a workspace.
    """
    if not os.path.isdir(
        os.path.join(root_directory,
                     config.Paths.CLOUDSDK_WORKSPACE_CONFIG_DIR_NAME)):
      raise NoWorkspaceException(root_directory)
    self.root_directory = root_directory

  def CloneProjectRepository(
      self, project, alias=DEFAULT_REPOSITORY_ALIAS, uri=None):
    """Clone a repository associated with a Google Cloud Project.

    Looks up the URL of the indicated repository, and clones it to
    WORKSPACE/PROJECT/ALIAS.

    Args:
      project: str, The name of the project that has a repository associated
          with it.
      alias: str, The alias of the repository to clone.
      uri: str, The URI of the repository to clone, or None if it must be
          inferred from the alias.

    Returns:
      str, The relative path of the repository, from the workspace root.

    Raises:
      UnknownRepositoryAliasException: If the alias is not known to be
          associated with the project.
    """
    uri = uri or _GetRepositoryURI(project, alias)
    if not uri:
      raise UnknownRepositoryAliasException()

    log.status.write('Cloning [{uri}] into [{path}].\n'.format(
        uri=uri, path=alias))
    self.CloneGitRepository(uri, alias)

  def GetProperty(self, prop):
    """Get a property defined in only this workspace.

    Ignores the global properties, or properties defined in the workspace for
    your current directory.

    Args:
      prop: properties._Property, The property for which you want the value.

    Returns:

    """
    # TODO(user): Update the properties package to make this easier.
    prop_file = os.path.join(self.root_directory,
                             config.Paths.CLOUDSDK_WORKSPACE_CONFIG_DIR_NAME,
                             'properties')
    # pylint:disable=protected-access
    pfile = properties._PropertiesFile([prop_file])
    return pfile.Get(prop)

  def SetProperty(self, prop, value):
    """Set a property defined in only this workspace.

    Ignores the global properties, or properties defined in the workspace for
    your current directory.

    Args:
      prop: properties._Property, The property you want to set.
      value: str, The value to set the property to.
    """
    prop_file = os.path.join(self.root_directory,
                             config.Paths.CLOUDSDK_WORKSPACE_CONFIG_DIR_NAME,
                             'properties')
    properties.PersistProperty(prop, value, properties_file=prop_file)

  @EnsureGit
  def CloneGitRepository(self, repository_url, repository_path):
    """Clone a git repository into a gcloud workspace.

    If the resulting clone does not have a .gcloud directory, create one. Also,
    sets the credential.helper to use the gcloud credential helper.

    Args:
      repository_url: str, The URL of the repository to clone.
      repository_path: str, The relative path from the root of the workspace to
          the repository clone.

    Raises:
      InvalidWorkspaceException: If workspace_dir_path is not a workspace.
      CannotInitRepositoryException: If there is already a file or directory in
          the way of creating this repository.
      CannotFetchRepositoryException: If there is a problem fetching the
          repository from the remote host, or if the repository is otherwise
          misconfigured.
    """

    abs_repository_path = os.path.join(self.root_directory, repository_path)
    if os.path.exists(abs_repository_path):
      # First check if it's already the repository we're looking for.
      with files.ChDir(abs_repository_path) as _:
        try:
          output = compat26.subprocess.check_output(
              ['git', 'remote', 'show', 'origin'])
        except subprocess.CalledProcessError:
          raise CannotFetchRepositoryException(
              'Repository in [{path}] is misconfigured.'.format(
                  path=abs_repository_path))
        output_match = _ORIGIN_URL_RE.search(output)
        if not output_match or output_match.group('url') != repository_url:
          raise CannotInitRepositoryException(
              ('Repository [{url}] cannot be cloned to [{path}]: there'
               ' is something already there.').format(
                   url=repository_url,
                   path=os.path.join(self.root_directory, repository_path)))
        else:
          # Repository exists and is correctly configured: abort.
          log.err.Print(
              ('Repository in [{path}] exists and is correctly configured.'
               .format(path=abs_repository_path)))
          return

    # Nothing is there, make a brand new repository.
    try:
      if (repository_url.startswith('https://code.google.com') or
          repository_url.startswith('https://source.developers.google.com')):

        # If this is a Google-hosted repo, clone with the cred helper.
        try:
          CheckGitVersion(_HELPER_MIN)
        except GitVersionException:
          log.warn(textwrap.dedent("""\
              You are cloning a Google-hosted repository with a version of git
              older than 1.7.9. If you upgrade to 1.7.9 or later, gcloud can
              handle authentication to this repository. Otherwise, to
              authenticate, use your Google account and the password found by
              running the following command.
               $ gcloud auth print-refresh-token
              """))
          subprocess.check_call(
              ['git', 'clone', repository_url, abs_repository_path])
        else:
          if (platforms.OperatingSystem.Current() ==
              platforms.OperatingSystem.WINDOWS):
            helper_name = 'gcloud.cmd'
          else:
            helper_name = 'gcloud.sh'
          subprocess.check_call(
              ['git', 'clone', repository_url, abs_repository_path,
               '--config', 'credential.helper=%s' % helper_name])
      else:
        # Otherwise, just do a simple clone. We do this clone, without the
        # credential helper, because a user may have already set a default
        # credential helper that would know the repo's auth info.
        subprocess.check_call(
            ['git', 'clone', repository_url, abs_repository_path])
    except subprocess.CalledProcessError as e:
      raise CannotFetchRepositoryException(e)
