# Copyright 2013 Google Inc. All Rights Reserved.

"""The calliope CLI/API is a framework for building library interfaces."""

import os
import re
import subprocess
import sys
import uuid
import argcomplete

from googlecloudsdk.calliope import actions
from googlecloudsdk.calliope import backend
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import config
from googlecloudsdk.core import log
from googlecloudsdk.core import metrics
from googlecloudsdk.core import properties
from googlecloudsdk.core.util import resource_printer


class NoHelpFoundError(exceptions.ToolException):
  """Raised when a help file cannot be located."""


def GetHelp(help_dir):
  """Returns a function that can display long help.

  Long help is displayed using the man utility if it's available on
  the user's platform. If man is not available, a plain-text version
  of help is written to standard out.

  Args:
    help_dir: str, The path to the directory containing help documents.

  Returns:
    func([str]), A function that can display help if help_dir exists,
    otherwise None.
  """
  def Help(path, default=None):
    """Displays help for the given subcommand.

    This function first attempts to display help using the man utility.
    If man is unavailable, a plain-text version of the help is printed
    to standard out.

    Args:
      path: A path representing the subcommand for which help is being
          requested (e.g., ['my-prog', 'my-subcommand'] if help is being
          requested for "my-prog my-subcommand").
      default: str, Text to print out if no help files can be found.

    Raises:
      HelpNotFound: If man is not available and no help exists for the
          given subcommand. Note that if man is available and no help exists,
          error reporting is deferred to man.
    """
    base = '_'.join(path)
    try:
      exit_code = subprocess.call(
          ['man',
           '-M', os.path.join(help_dir, 'man'),  # Sets the man search path.
           base])
      if exit_code == 0:
        return
      else:
        log.debug('man process returned with exit code %s', exit_code)
    except OSError as e:
      log.debug('There was a problem launching man: %s', e)

    log.debug('Falling back to plain-text help.')

    text_help_file_path = os.path.join(help_dir, 'text.long', base)
    try:
      with open(text_help_file_path) as f:
        sys.stdout.write(f.read())
    except IOError:
      if default:
        print default
      else:
        raise NoHelpFoundError(
            'No manual entry for command: {0}'.format(' '.join(path)))

  if help_dir and os.path.exists(help_dir):
    return Help
  else:
    return None


def GoogleCloudSDKPackageRoot():
  return config.GoogleCloudSDKPackageRoot()


class RunHook(object):
  """Encapsulates a function to be run before or after command execution."""

  def __init__(self, func, include_commands=None, exclude_commands=None):
    """Constructs the hook.

    Args:
      func: function, The no args function to run.
      include_commands: str, A regex for the command paths to run.  If not
        provided, the hook will be run for all commands.
      exclude_commands: str, A regex for the command paths to exclude.  If not
        provided, nothing will be excluded.
    """
    self.__func = func
    self.__include_commands = include_commands if include_commands else '.*'
    self.__exclude_commands = exclude_commands

  def Run(self, command_path):
    """Runs this hook if the filters match the given command.

    Args:
      command_path: str, The calliope command path for the command that was run.

    Returns:
      bool, True if the hook was run, False if it did not match.
    """
    if not re.match(self.__include_commands, command_path):
      return False
    if self.__exclude_commands and re.match(self.__exclude_commands,
                                            command_path):
      return False
    self.__func()
    return True


class CLILoader(object):
  """A class to encapsulate loading the CLI and bootstrapping the REPL."""

  # Splits a path like foo.bar.baz into 2 groups: foo.bar, and baz.  Group 1 is
  # optional.
  PATH_RE = re.compile(r'(?:([\w\.]+)\.)?([^\.]+)')

  def __init__(self, name, command_root_directory,
               allow_non_existing_modules=False, load_context=None,
               logs_dir=config.Paths().logs_dir, version_func=None,
               help_func=None):
    """Initialize Calliope.

    Args:
      name: str, The name of the top level command, used for nice error
        reporting.
      command_root_directory: str, The path to the directory containing the main
        CLI module.
      allow_non_existing_modules: True to allow extra module directories to not
        exist, False to raise an exception if a module does not exist.
      load_context: A function that returns a context dict, or None for a
        default which always returns {}.
      logs_dir: str, The path to the root directory to store logs in, or None
        for no log files.
      version_func: func, A function to call for a top-level -v and
        --version flag. If None, no flags will be available.
      help_func: func([command path]), A function to call for in-depth help
        messages. It is passed the set of subparsers used (not including the
        top-level command). After it is called calliope will exit. This function
        will be called when a top-level 'help' command is run, or when the
        --help option is added on to any command.

    Raises:
      backend.LayoutException: If no command root directory is given.
    """
    self.__name = name
    self.__command_root_directory = command_root_directory
    if not self.__command_root_directory:
      raise backend.LayoutException(
          'You must specify a command root directory.')

    self.__allow_non_existing_modules = allow_non_existing_modules

    self.__config_hooks = backend.ConfigHooks(load_context=load_context)
    self.__logs_dir = logs_dir
    self.__version_func = version_func
    self.__help_func = help_func

    self.__pre_run_hooks = []
    self.__post_run_hooks = []

    self.__modules = []

  def AddModule(self, name, path):
    """Adds a module to this CLI tool.

    If you are making a CLI that has subgroups, use this to add in more
    directories of commands.

    Args:
      name: str, The name of the group to create under the main CLI.  If this is
        to be placed under another group, a dotted name can be used.
      path: str, The full path the directory containing the commands for this
        group.
    """
    self.__modules.append((name, path))

  def RegisterPreRunHook(self, func,
                         include_commands=None, exclude_commands=None):
    """Register a function to be run before command execution.

    Args:
      func: function, The no args function to run.
      include_commands: str, A regex for the command paths to run.  If not
        provided, the hook will be run for all commands.
      exclude_commands: str, A regex for the command paths to exclude.  If not
        provided, nothing will be excluded.
    """
    hook = RunHook(func, include_commands, exclude_commands)
    self.__pre_run_hooks.append(hook)

  def RegisterPostRunHook(self, func,
                          include_commands=None, exclude_commands=None):
    """Register a function to be run after command execution.

    Args:
      func: function, The no args function to run.
      include_commands: str, A regex for the command paths to run.  If not
        provided, the hook will be run for all commands.
      exclude_commands: str, A regex for the command paths to exclude.  If not
        provided, nothing will be excluded.
    """
    hook = RunHook(func, include_commands, exclude_commands)
    self.__post_run_hooks.append(hook)

  def Generate(self):
    """Uses the registered information to generate the CLI tool.

    Returns:
      CLI, The generated CLI tool.
    """
    return self.__LoadCLIFromGroups()

  def __LoadCLIFromGroups(self):
    """Load the CLI from a command directory.

    Returns:
      CLI, The generated CLI tool.
    """
    top_group = self.__LoadTopGroup(
        self.__GetGroupInfo(
            module_directory=self.__command_root_directory, module_path=None,
            allow_non_existing_modules=False, exception_if_present=None,
            is_top_group=True))
    self.__AddBuiltinGlobalFlags(top_group)

    for module_dot_path, module_dir in self.__modules:
      try:
        match = CLILoader.PATH_RE.match(module_dot_path)
        root, name = match.group(1, 2)
        parent_group = self.__FindParentGroup(top_group, root)
        exception_if_present = None
        if not parent_group:
          exception_if_present = backend.LayoutException(
              'Root [{root}] for command group [{group}] does not exist.'
              .format(root=root, group=name))

        path_list = module_dot_path.split('.')
        group_info = self.__GetGroupInfo(
            module_directory=module_dir, module_path=path_list,
            allow_non_existing_modules=self.__allow_non_existing_modules,
            exception_if_present=exception_if_present, is_top_group=False)

        if group_info:
          parent_group.AddSubGroup(group_info)
      except backend.CommandLoadFailure as e:
        log.exception(e)

    cli = self.__MakeCLI(top_group)

    return cli

  def __FindParentGroup(self, top_group, root):
    """Find the group that should be the parent of this command.

    Args:
      top_group: _CommandCommon, The top group in this CLI hierarchy.
      root: str, The dotted path of where this command or group should appear
        in the command tree.

    Returns:
      _CommandCommon, The group that should be parent of this new command tree
        or None if it could not be found.
    """
    if not root:
      return top_group
    root_path = root.split('.')
    group = top_group
    for part in root_path:
      group = group.LoadSubElement(part)
      if not group:
        return None
    return group

  def __GetGroupInfo(self, module_directory, module_path=None,
                     allow_non_existing_modules=False,
                     exception_if_present=None, is_top_group=False):
    """Generates the information necessary to be able to load a command group.

    The group might actually be loaded now if it is the root of the SDK, or the
    information might be saved for later if it is to be lazy loaded.

    Args:
      module_directory: The path to the location of the module.
      module_path: An optional name override for the module. If not set, it will
        default to using the name of the directory containing the module.
      allow_non_existing_modules: True to allow this module directory to not
        exist, False to raise an exception if this module does not exist.
      exception_if_present: Exception, An exception to throw if the module
        actually exists, or None.
      is_top_group: bool, True if this is the root command group.

    Raises:
      LayoutException: If the module directory does not exist and
      allow_non_existing is False.

    Returns:
      A tuple of (module_dir, module_path, path) or None if the module directory
      does not exist and allow_non_existing is True.  This tuple can be passed
      to self.__LoadTopGroup() or backend.CommandGroup.AddGroup().  The
      module_dir is the directory the group is found under.  The module_path is
      the relative path of the root of the command group from the module_dir.
      path is the logical path that the group will appear under in the command
      heirarchy of the tool.
    """
    if not os.path.isdir(module_directory):
      if allow_non_existing_modules:
        return None
      raise backend.LayoutException(
          'The given module directory does not exist: {}'.format(
              module_directory))
    elif exception_if_present:
      # pylint: disable=raising-bad-type, This will be an actual exception.
      raise exception_if_present

    module_root, module = os.path.split(module_directory)

    # If this is the top level, don't register the name of the module directory
    # itself, it should assume the name of the command.  If this is another
    # module directory, its name gets explicitly registered under the root
    # command.
    path = [self.__name]
    if not is_top_group:
      module_path = module_path or [module]
      path.extend(module_path)

    return (module_root, [module], path)

  def __LoadTopGroup(self, group_info):
    """Actually loads the top group of the CLI based on the given group_info.

    Args:
      group_info: A tuple of (module_dir, module_path, path) generated by
        self.__GetGroupInfo()

    Returns:
      The backend.CommandGroup object.
    """
    (module_root, module, path) = group_info
    return backend.CommandGroup(
        module_root, module, path, uuid.uuid4().hex, self, None,
        self.__config_hooks, help_func=self.__help_func)

  def __AddBuiltinGlobalFlags(self, top_element):
    """Adds in calliope builtin global flags.

    This needs to happen immediately after the top group is loaded and before
    any other groups are loaded.  The flags must be present so when sub groups
    are loaded, the flags propagate down.

    Args:
      top_element: backend._CommandCommon, The root of the command tree.
    """
    if self.__version_func is not None:
      # pylint: disable=protected-access
      version_flag = top_element._ai.add_argument(
          '-v', '--version',
          action=actions.FunctionExitAction(self.__version_func),
          help='Print version information.')
      version_flag.global_only = True
    # pylint: disable=protected-access
    top_element._ai.add_argument(
        '--verbosity',
        choices=log.OrderedVerbosityNames(),
        default=None,
        help=(
            'Override the default verbosity for this command.  This must be '
            'a standard logging verbosity level: [{values}] (Default: '
            '[{default}]).').format(
                values=', '.join(log.OrderedVerbosityNames()),
                default=log.DEFAULT_VERBOSITY_STRING),
        action=actions.StoreProperty(properties.VALUES.core.verbosity))
    top_element._ai.add_argument(
        '--user-output-enabled',
        default=None,
        choices=('true', 'false'),
        help=(
            'Control whether user intended output is printed to the console.  '
            '(true/false)'),
        action=actions.StoreProperty(
            properties.VALUES.core.user_output_enabled))
    format_flag = top_element._ai.add_argument(
        '--format', help='Format for printed output.',
        choices=resource_printer.SUPPORTED_FORMATS)
    format_flag.detailed_help = """\
        Specify a format for printed output. By default, a command-specific
        human-friendly output format is used. Setting this flag to one of
        the available options will serialize the result of the command in
        the chosen format and print it to stdout. Supported formats are:
        `{0}`.""".format('`, `'.join(resource_printer.SUPPORTED_FORMATS))

  def __MakeCLI(self, top_element):
    """Generate a CLI object from the given data.

    Args:
      top_element: The top element of the command tree
        (that extends backend.CommandCommon).

    Returns:
      CLI, The generated CLI tool.
    """
    if '_ARGCOMPLETE' not in os.environ:
      # Don't bother setting up logging if we are just doing a completion.
      log.AddFileLogging(self.__logs_dir)

    # Pre-load all commands if lazy loading is disabled.
    if properties.VALUES.core.disable_command_lazy_loading.GetBool():
      top_element.LoadAllSubElements(recursive=True)

    cli = CLI(top_element, self.__pre_run_hooks, self.__post_run_hooks,
              self.__help_func)
    return cli


class CLI(object):
  """A generated command line tool."""

  def __init__(self, top_element, pre_run_hooks, post_run_hooks, help_func):
    # pylint: disable=protected-access
    self.__parser = top_element._parser
    self.__top_element = top_element
    self.__pre_run_hooks = pre_run_hooks
    self.__post_run_hooks = post_run_hooks
    self.__help_func = help_func

  def _ArgComplete(self):
    argcomplete.autocomplete(self.__parser, always_complete_options=False)

  def _TopElement(self):
    return self.__top_element

  def _HelpFunc(self):
    return self.__help_func

  def Execute(self, args=None, call_arg_complete=True):
    """Execute the CLI tool with the given arguments.

    Args:
      args: The arguments from the command line or None to use sys.argv
      call_arg_complete: Call the _ArgComplete function if True

    Returns:
      The result of executing the command determined by the command
      implementation.
    """
    if call_arg_complete:
      self._ArgComplete()

    if not args:
      args = sys.argv[1:]

    for s in args:
      try:
        s.decode('ascii')
      except UnicodeError:
        raise exceptions.InvalidStringException(s)

    try:
      properties.VALUES.PushInvocationValues()
      args = self.__parser.parse_args(args)
      command_path_string = '.'.join(args.command_path)

      # TODO(user): put a real version here
      metrics.Commands(command_path_string, None)

      return args.cmd_func(
          cli=self,
          args=args,
          pre_run_hooks=self.__pre_run_hooks,
          post_run_hooks=self.__post_run_hooks)
    finally:
      properties.VALUES.PopInvocationValues()
