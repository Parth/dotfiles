# Copyright 2013 Google Inc. All Rights Reserved.

"""Common bootstrapping functionality used by the wrapper scripts."""

# Disables import order warning and unused import.  Setup changes the python
# path so cloud sdk imports will actually work, so it must come first.
# pylint: disable=C6203
# pylint: disable=W0611
import setup

import json
import os
import signal
import subprocess
import sys

import oauth2client.gce as gce
from googlecloudsdk.core import config
from googlecloudsdk.core.credentials import store as c_store
from googlecloudsdk.core import metrics
from googlecloudsdk.core import properties
from googlecloudsdk.core.updater import local_state
from googlecloudsdk.core.updater import update_manager
from googlecloudsdk.core.util import execution_utils


BOOTSTRAPPING_DIR = os.path.dirname(os.path.realpath(__file__))
BIN_DIR = os.path.dirname(BOOTSTRAPPING_DIR)
SDK_ROOT = os.path.dirname(BIN_DIR)


def _FullPath(tool_dir, exec_name):
  return os.path.join(SDK_ROOT, tool_dir, exec_name)


def ExecutePythonTool(tool_dir, exec_name, *args):
  """Execute the given python script with the given args and command line.

  Args:
    tool_dir: the directory the tool is located in
    exec_name: additional path to the executable under the tool_dir
    *args: args for the command
  """
  _ExecuteTool(
      execution_utils.ArgsForPythonTool(_FullPath(tool_dir, exec_name), *args))


def ExecuteShellTool(tool_dir, exec_name, *args):
  """Execute the given bash script with the given args.

  Args:
    tool_dir: the directory the tool is located in
    exec_name: additional path to the executable under the tool_dir
    *args: args for the command
  """
  _ExecuteTool(
      execution_utils.ArgsForShellTool(_FullPath(tool_dir, exec_name), *args))


def ExecuteCMDTool(tool_dir, exec_name, *args):
  """Execute the given batch file with the given args.

  Args:
    tool_dir: the directory the tool is located in
    exec_name: additional path to the executable under the tool_dir
    *args: args for the command
  """
  _ExecuteTool(
      execution_utils.ArgsForCMDTool(_FullPath(tool_dir, exec_name), *args))


def _GetToolEnv():
  env = dict(os.environ)
  env['CLOUDSDK_WRAPPER'] = '1'
  env['CLOUDSDK_VERSION'] = config.CLOUD_SDK_VERSION
  env['CLOUDSDK_PYTHON'] = execution_utils.GetPythonExecutable()
  return env


def _ExecuteTool(args):
  """Executes a new tool with the given args, plus the args from the cmdline.

  Args:
    args: [str], The args of the command to execute.
  """
  execution_utils.Exec(args + sys.argv[1:], env=_GetToolEnv())


def CheckCredOrExit(can_be_gce=False):
  try:
    cred = c_store.Load()
    if not can_be_gce and isinstance(cred, gce.AppAssertionCredentials):
      raise c_store.NoActiveAccountException()
  except (c_store.NoActiveAccountException,
          c_store.NoCredentialsForAccountException) as e:
    sys.stderr.write(str(e) + '\n\n')
    sys.exit(1)


def GetDefaultInstalledComponents():
  """Gets the list of components to install by default.

  Returns:
    list(str), The component ids that should be installed.  It will return []
    if there are no default components, or if there is any error in reading
    the file with the defaults.
  """
  default_components_file = os.path.join(BOOTSTRAPPING_DIR,
                                         '.default_components')
  try:
    with open(default_components_file) as f:
      return json.load(f)
  # pylint:disable=bare-except, If the file does not exist or is malformed,
  # we don't want to expose this as an error.  Setup will just continue
  # without installing any components by default and will tell the user how
  # to install the components they want manually.
  except:
    pass
  return []


def CheckForBlacklistedCommand(args, blacklist, warn=True, die=False):
  """Blacklist certain subcommands, and warn the user.

  Args:
    args: the command line arguments, including the 0th argument which is
        the program name.
    blacklist: a map of blacklisted commands to the messages that should be
        printed when they're run.
    warn: if true, print a warning message.
    die: if true, exit.

  Returns:
    True if a command in the blacklist is being indicated by args.

  """
  bad_arg = None
  for arg in args[1:]:
    if arg and arg[0] is '-':
      continue
    if arg in blacklist:
      bad_arg = arg
      break

  blacklisted = bad_arg is not None

  if blacklisted:
    if warn:
      sys.stderr.write('It looks like you are trying to run "%s %s".\n'
                       % (args[0], bad_arg))
      sys.stderr.write('The "%s" command is no longer needed with the '
                       'Cloud SDK.\n' % bad_arg)
      sys.stderr.write(blacklist[bad_arg] + '\n')
      answer = raw_input('Really run this command? (y/N) ')
      if answer in ['y', 'Y']:
        return False

    if die:
      sys.exit(1)

  return blacklisted


def CheckUpdates():
  """Check for updates and inform the user.

  """
  try:
    update_manager.UpdateManager().PerformUpdateCheck()
  # pylint:disable=broad-except, We never want this to escape, ever. Only
  # messages printed should reach the user.
  except Exception:
    pass


def CommandStart(command_name, component_id=None):
  """Logs that the given command is being executed.

  Args:
    command_name: str, The name of the command being executed.
    component_id: str, The component id that this command belongs to.  Used for
      version information.
  """
  version = None
  if component_id:
    version = local_state.InstallationState.VersionForInstalledComponent(
        component_id)
  metrics.Executions(command_name, version)


def PrerunChecks(can_be_gce=False):
  """Call all normal pre-command checks.

  Checks for credentials and updates. If no credentials exist, exit. If there
  are updates available, inform the user and continue.

  Silent when there are credentials and no updates.

  Args:
    can_be_gce: bool, True is the credentials may be those provided by the
        GCE metadata server.
  """
  CheckCredOrExit(can_be_gce=can_be_gce)
  CheckUpdates()


def GetActiveProjectAndAccount():
  """Get the active project name and account for the active credentials.

  For use with wrapping legacy tools that take projects and credentials on
  the command line.

  Returns:
    (str, str), A tuple whose first element is the project, and whose second
    element is the account.
  """
  project_name = properties.VALUES.core.project.Get(validate=False)
  account = properties.VALUES.core.account.Get(validate=False)
  return (project_name, account)
