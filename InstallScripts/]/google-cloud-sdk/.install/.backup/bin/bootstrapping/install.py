#!/usr/bin/env python
#
# Copyright 2013 Google Inc. All Rights Reserved.
#

"""Do initial setup for the Cloud SDK."""

import bootstrapping

# pylint:disable=g-bad-import-order
import argparse
import os
import re
import shutil
import sys

from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import config
from googlecloudsdk.core import properties
from googlecloudsdk.core.credentials import gce as c_gce
from googlecloudsdk.core.util import console_io
from googlecloudsdk.core.util import platforms
from googlecloudsdk.gcloud import gcloud

# pylint:disable=superfluous-parens


def ParseArgs():
  """Parse args for the installer, so interactive prompts can be avoided."""

  def Bool(s):
    return s.lower() in ['true', '1']

  parser = argparse.ArgumentParser()

  parser.add_argument('--usage-reporting',
                      default=None, type=Bool,
                      help='(true/false) Disable anonymous usage reporting.')
  parser.add_argument('--rc-path',
                      help='Profile to update with PATH and completion.')
  parser.add_argument('--bash-completion',
                      default=None, type=Bool,
                      help=('(true/false) Add a line for bash completion in'
                            ' the profile.'))
  parser.add_argument('--path-update',
                      default=None, type=Bool,
                      help=('(true/false) Add a line for path updating in the'
                            ' profile.'))
  parser.add_argument('--disable-installation-options', action='store_true',
                      help='DEPRECATED.  This flag is no longer used.')
  parser.add_argument('--override-components', nargs='*',
                      help='Override the components that would be installed by '
                      'default and install these instead.')
  parser.add_argument('--additional-components', nargs='+',
                      help='Additional components to install by default.  These'
                      ' components will either be added to the default install '
                      'list, or to the override-components (if provided).')

  return parser.parse_args()


def Prompts(usage_reporting):
  """Display prompts to opt out of usage reporting.

  Args:
    usage_reporting: bool, If True, enable usage reporting. If None, ask.
  """

  if config.InstallationConfig.Load().IsAlternateReleaseChannel():
    usage_reporting = True
    print("""
Usage reporting is always on for alternate release channels.
""")
    return

  if usage_reporting is None:
    print("""
The Google Cloud SDK is currently in developer preview. To help improve the
quality of this product, we collect anonymized data on how the SDK is used.
You may choose to opt out of this collection now (by choosing 'N' at the below
prompt), or at any time in the future by running the following command:
    gcloud config set --scope=user disable_usage_reporting true
""")

    usage_reporting = console_io.PromptContinue(
        prompt_string='Do you want to help improve the Google Cloud SDK')
  properties.PersistProperty(
      properties.VALUES.core.disable_usage_reporting, not usage_reporting,
      scope=properties.Scope.INSTALLATION)


# pylint:disable=unused-argument
def UpdatePathForWindows(bin_path):
  """Update the Windows system path to include bin_path.

  Args:
    bin_path: str, The absolute path to the directory that will contain
        Cloud SDK binaries.
  """

  # pylint:disable=g-import-not-at-top, we want to only attempt these imports
  # on windows.
  try:
    import win32con
    import win32gui
    try:
      # Python 3
      import winreg
    except ImportError:
      # Python 2
      import _winreg as winreg
  except ImportError:
    print("""\
The installer is unable to automatically update your system PATH. Please add
  {path}
to your system PATH to enable easy use of the Cloud SDK Command Line Tools.
""".format(path=bin_path))
    return

  def GetEnv(name):
    root = winreg.HKEY_CURRENT_USER
    subkey = 'Environment'
    key = winreg.OpenKey(root, subkey, 0, winreg.KEY_READ)
    try:
      value, _ = winreg.QueryValueEx(key, name)
    # pylint:disable=undefined-variable, This variable is defined in windows.
    except WindowsError:
      return ''
    return value

  def SetEnv(name, value):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0,
                         winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
    winreg.CloseKey(key)
    win32gui.SendMessage(
        win32con.HWND_BROADCAST, win32con.WM_SETTINGCHANGE, 0, 'Environment')
    return value

  def Remove(paths, value):
    while value in paths:
      paths.remove(value)

  def PrependEnv(name, values):
    paths = GetEnv(name).split(';')
    for value in values:
      if value in paths:
        Remove(paths, value)
      paths.insert(0, value)
    SetEnv(name, ';'.join(paths))

  PrependEnv('Path', [bin_path])

  print("""\
The following directory has been added to your PATH.
  {bin_path}

Create a new command shell for the changes to take effect.
""".format(bin_path=bin_path))


def UpdateRC(bash_completion, path_update, rc_path, bin_path):
  """Update the system path to include bin_path.

  Args:
    bash_completion: bool, Whether or not to do bash completion. If None, ask.
    path_update: bool, Whether or not to do bash completion. If None, ask.
    rc_path: str, The path to the rc file to update. If None, ask.
    bin_path: str, The absolute path to the directory that will contain
        Cloud SDK binaries.
  """

  host_os = platforms.OperatingSystem.Current()
  if host_os == platforms.OperatingSystem.WINDOWS:
    if path_update is None:
      path_update = console_io.PromptContinue(
          prompt_string='Update %PATH% to include Cloud SDK binaries?')
    if path_update:
      UpdatePathForWindows(bin_path)
    return

  if not rc_path:

    # figure out what file to edit
    if host_os == platforms.OperatingSystem.LINUX:
      if c_gce.Metadata().connected:
        file_name = '.bash_profile'
      else:
        file_name = '.bashrc'
    elif host_os == platforms.OperatingSystem.MACOSX:
      file_name = '.bash_profile'
    elif host_os == platforms.OperatingSystem.CYGWIN:
      file_name = '.bashrc'
    elif host_os == platforms.OperatingSystem.MSYS:
      file_name = '.profile'
    else:
      file_name = '.bashrc'
    rc_path = os.path.expanduser(os.path.join('~', file_name))

    rc_path_update = console_io.PromptResponse((
        'The Google Cloud SDK installer will now prompt you to update an rc '
        'file to bring the Google Cloud CLIs into your environment.\n\n'
        'Enter path to an rc file to update, or leave blank to use '
        '[{rc_path}]:  ').format(rc_path=rc_path))
    if rc_path_update:
      rc_path = os.path.expanduser(rc_path_update)

  if os.path.exists(rc_path):
    with open(rc_path) as rc_file:
      rc_data = rc_file.read()
      cached_rc_data = rc_data
  else:
    rc_data = ''
    cached_rc_data = ''

  updated_rc = False

  if path_update is None:
    path_update = console_io.PromptContinue(
        prompt_string=('\nModify profile to update your $PATH?'))

  path_rc_path = os.path.join(bootstrapping.SDK_ROOT, 'path.bash.inc')
  if path_update:
    path_comment = r'# The next line updates PATH for the Google Cloud SDK.'
    path_subre = re.compile(r'\n*'+path_comment+r'\n.*$',
                            re.MULTILINE)

    path_line = "{comment}\nsource '{path_rc_path}'\n".format(
        comment=path_comment, path_rc_path=path_rc_path)
    filtered_data = path_subre.sub('', rc_data)
    rc_data = '{filtered_data}\n{path_line}'.format(
        filtered_data=filtered_data,
        path_line=path_line)
    updated_rc = True
  else:
    print("""\
Source [{path_rc_path}]
in your profile to add the Google Cloud SDK command line tools to your $PATH.
""".format(path_rc_path=path_rc_path))

  if bash_completion is None:
    bash_completion = console_io.PromptContinue(
        prompt_string=('\nModify profile to enable bash completion?'))

  completion_rc_path = os.path.join(
      bootstrapping.SDK_ROOT, 'completion.bash.inc')
  if bash_completion:
    complete_comment = r'# The next line enables bash completion for gcloud.'
    complete_subre = re.compile(r'\n*'+complete_comment+r'\n.*$',
                                re.MULTILINE)

    complete_line = "{comment}\nsource '{rc_path}'\n".format(
        comment=complete_comment, rc_path=completion_rc_path)
    filtered_data = complete_subre.sub('', rc_data)
    rc_data = '{filtered_data}\n{complete_line}'.format(
        filtered_data=filtered_data,
        complete_line=complete_line)
    updated_rc = True
  else:
    print("""\
Source [{completion_rc_path}]
in your profile to enable bash completion for gcloud.
""".format(completion_rc_path=completion_rc_path))

  if not updated_rc:
    return

  if cached_rc_data == rc_data:
    print('No changes necessary for [{rc}].'.format(rc=rc_path))
    return

  if os.path.exists(rc_path):
    rc_backup = rc_path+'.backup'
    print('Backing up [{rc}] to [{backup}].'.format(
        rc=rc_path, backup=rc_backup))
    shutil.copyfile(rc_path, rc_backup)

  with open(rc_path, 'w') as rc_file:
    rc_file.write(rc_data)

  print("""\
[{rc_path}] has been updated.
Start a new shell for the changes to take effect.
""".format(rc_path=rc_path))


def Install(override_components, additional_components):
  """Do the normal installation of the Cloud SDK."""
  # Install the OS specific wrapper scripts for gcloud and any pre-configured
  # components for the SDK.
  to_install = (override_components if override_components is not None
                else bootstrapping.GetDefaultInstalledComponents())
  if additional_components:
    to_install.extend(additional_components)

  print("""
This will install all the core command line tools necessary for working with
the Google Cloud Platform.
""")
  InstallComponents(to_install)

  # Show the list of components if there were no pre-configured ones.
  if not to_install:
    # pylint: disable=protected-access
    gcloud._cli.Execute(['--quiet', 'components', 'list'])


def ReInstall(component_ids):
  """Do a forced reinstallation of the Cloud SDK.

  Args:
    component_ids: [str], The components that should be automatically installed.
  """
  to_install = bootstrapping.GetDefaultInstalledComponents()
  to_install.extend(component_ids)
  InstallComponents(component_ids)


def InstallComponents(component_ids):
  # Installs the selected configuration or the wrappers for core at a minimum.
  # pylint: disable=protected-access
  gcloud._cli.Execute(
      ['--quiet', 'components', 'update', '--allow-no-backup'] + component_ids)


def main():
  pargs = ParseArgs()
  reinstall_components = os.environ.get('CLOUDSDK_REINSTALL_COMPONENTS')
  try:
    if reinstall_components:
      ReInstall(reinstall_components.split(','))
    else:
      Prompts(pargs.usage_reporting)
      bootstrapping.CommandStart('INSTALL', component_id='core')
      if not config.INSTALLATION_CONFIG.disable_updater:
        Install(pargs.override_components, pargs.additional_components)

      UpdateRC(
          bash_completion=pargs.bash_completion,
          path_update=pargs.path_update,
          rc_path=pargs.rc_path,
          bin_path=bootstrapping.BIN_DIR,
      )

      print("""\

For more information on how to get started, please visit:
  https://developers.google.com/cloud/sdk/gettingstarted

""")
  except exceptions.ToolException as e:
    print(e)
    sys.exit(1)


if __name__ == '__main__':
  main()
