# Copyright 2013 Google Inc. All Rights Reserved.

"""A command that prints out information about your gcloud environment."""

import os
import StringIO
import sys
import textwrap

from googlecloudsdk.calliope import base
from googlecloudsdk.core import config
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.updater import update_manager
from googlecloudsdk.core.util import platforms


class Info(base.Command):
  """Display information about the current gcloud environment.

     This command displays information about the current gcloud environment.
  """

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--show-log',
        action='store_true',
        help='Print the contents of the last log file.')

  def Run(self, args):
    return InfoHolder()

  def Display(self, args, info):
    log.Print(info)

    if args.show_log and info.logs.last_log:
      log.Print('\nContents of log file: [{0}]\n'
                '==========================================================\n'
                '{1}\n\n'
                .format(info.logs.last_log, info.logs.LastLogContents()))


class InfoHolder(object):
  """Base object to hold all the configuration info."""

  def __init__(self):
    self.basic = BasicInfo()
    self.installation = InstallationInfo()
    self.config = ConfigInfo()
    self.logs = LogsInfo()

  def __str__(self):
    out = StringIO.StringIO()
    out.write(str(self.basic) + '\n')
    out.write(str(self.installation) + '\n')
    out.write(str(self.config) + '\n')
    out.write(str(self.logs) + '\n')
    return out.getvalue()


class BasicInfo(object):
  """Holds basic information about your system setup."""

  def __init__(self):
    platform = platforms.Platform.Current()
    self.version = config.CLOUD_SDK_VERSION
    self.operating_system = platform.operating_system
    self.architecture = platform.architecture
    self.python_version = sys.version
    self.site_packages = 'site' in sys.modules

  def __str__(self):
    return textwrap.dedent("""\
        Google Cloud SDK [{version}]

        Platform: [{os}, {arch}]
        Python Version: [{python_version}]
        Site Packages: [{site_packages}]
        """.format(
            version=self.version,
            os=self.operating_system.name,
            arch=self.architecture.name,
            python_version=self.python_version.replace('\n', ' '),
            site_packages='Enabled' if self.site_packages else 'Disabled'))


class InstallationInfo(object):
  """Holds information about your Cloud SDK installation."""

  def __init__(self):
    self.sdk_root = config.Paths().sdk_root
    self.release_channel = config.INSTALLATION_CONFIG.release_channel
    self.repo_url = config.INSTALLATION_CONFIG.snapshot_url
    repos = properties.VALUES.component_manager.additional_repositories.Get(
        validate=False)
    self.additional_repos = repos.split(',') if repos else []
    self.path = os.environ.get('PATH', '')

    if self.sdk_root:
      manager = update_manager.UpdateManager()
      self.components = manager.GetCurrentVersionsInformation()
      self.old_tool_paths = manager.FindAllOldToolsOnPath()
      paths = [os.path.realpath(p) for p in self.path.split(os.pathsep)]
      this_path = os.path.realpath(
          os.path.join(self.sdk_root,
                       update_manager.UpdateManager.BIN_DIR_NAME))
      # TODO(user): Validate symlinks in /usr/local/bin when we start
      # creating them.
      self.on_path = this_path in paths
    else:
      self.components = {}
      self.old_tool_paths = []
      self.on_path = False

  def __str__(self):
    out = StringIO.StringIO()
    out.write('Installation Root: [{0}]\n'.format(
        self.sdk_root if self.sdk_root else 'Unknown'))
    if config.INSTALLATION_CONFIG.IsAlternateReleaseChannel():
      out.write('Release Channel: [{0}]\n'.format(self.release_channel))
      out.write('Repository URL: [{0}]\n'.format(self.repo_url))
    if self.additional_repos:
      out.write('Additional Repositories:\n  {0}\n'.format(
          '\n  '.join(self.additional_repos)))

    if self.components:
      components = ['{0}: [{1}]'.format(name, value) for name, value in
                    self.components.iteritems()]
      out.write('Installed Components:\n  {0}\n'.format(
          '\n  '.join(components)))

    out.write('System PATH: [{0}]\n'.format(self.path))
    out.write('Cloud SDK on PATH: [{0}]\n'.format(self.on_path))

    if self.old_tool_paths:
      out.write('\nWARNING: There are old versions of the Google Cloud '
                'Platform tools on your system PATH.\n  {0}\n'
                .format('\n  '.join(self.old_tool_paths)))
    return out.getvalue()


class ConfigInfo(object):
  """Holds information about where config is stored and what values are set."""

  def __init__(self):
    self.paths = config.Paths()
    self.account = properties.VALUES.core.account.Get(validate=False)
    self.project = properties.VALUES.core.project.Get(validate=False)
    self.properties = properties.VALUES.AllValues()

  def __str__(self):
    out = StringIO.StringIO()
    out.write(textwrap.dedent("""\
        Installation Properties: [{installation_properties}]
        User Config Directory: [{global_config}]
        User Properties: [{user_properties}]
        Current Workspace: [{workspace}]
        Workspace Config Directory: [{workspace_config}]
        Workspace Properties: [{workspace_properties}]

        Account: [{account}]
        Project: [{project}]

        """.format(
            installation_properties=self.paths.installation_properties_path,
            global_config=self.paths.global_config_dir,
            user_properties=self.paths.user_properties_path,
            workspace=self.paths.workspace_dir,
            workspace_config=self.paths.workspace_config_dir,
            workspace_properties=self.paths.workspace_properties_path,
            account=self.account,
            project=self.project)))

    out.write('Current Properties:\n')
    for section, props in self.properties.iteritems():
      out.write('  [{section}]\n'.format(section=section))
      for name, value in props.iteritems():
        out.write('    {name}: [{value}]\n'.format(
            name=name, value=value))
    return out.getvalue()


class LogsInfo(object):
  """Holds information about where logs are located."""

  def __init__(self):
    paths = config.Paths()
    self.logs_dir = paths.logs_dir
    self.last_log = self.LastLogFile(self.logs_dir)

  def __str__(self):
    return textwrap.dedent("""\
        Logs Directory: [{logs_dir}]
        Last Log File: [{log_file}]
        """.format(logs_dir=self.logs_dir, log_file=self.last_log))

  def LastLogContents(self):
    if not self.last_log:
      return ''
    with open(self.last_log) as fp:
      return fp.read()

  def LastLogFile(self, logs_dir):
    """Finds the last (not current) gcloud log file.

    Args:
      logs_dir: str, The path to the logs directory being used.

    Returns:
      str, The full path to the last (but not the currently in use) log file
      if it exists, or None.
    """
    date_dirs = self.FilesSortedByName(logs_dir)
    if not date_dirs:
      return None

    found_file = False
    for date_dir in reversed(date_dirs):
      log_files = self.FilesSortedByName(date_dir)
      if log_files:
        if not found_file:
          log_files.pop()
          found_file = True
        if log_files:
          return log_files[-1]

    return None

  def FilesSortedByName(self, directory):
    """Gets the list of files in the given directory, sorted by name.

    Args:
      directory: str, The path to the directory to list.

    Returns:
      [str], The full paths of the files, sorted by file name, or None.
    """
    if not os.path.isdir(directory):
      return None
    dates = os.listdir(directory)
    if not dates:
      return None
    return [os.path.join(directory, date) for date in sorted(dates)]
