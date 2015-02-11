# Copyright 2013 Google Inc. All Rights Reserved.

"""Backend stuff for the calliope.cli module.

Not to be used by mortals.

"""

import argparse
import imp
import os
import re
import sys

from googlecloudsdk.calliope import actions
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.calliope import markdown
from googlecloudsdk.calliope import usage_text
from googlecloudsdk.core import cli as core_cli
from googlecloudsdk.core import exceptions as core_exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.util import resource_printer


class ArgumentException(Exception):
  """ArgumentException is for problems with the provided arguments."""
  pass


class MissingArgumentException(ArgumentException):
  """An exception for when required arguments are not provided."""

  def __init__(self, command_path, missing_arguments):
    """Creates a new MissingArgumentException.

    Args:
      command_path: A list representing the command or group that had the
          required arguments
      missing_arguments: A list of the arguments that were not provided
    """
    message = ('The following required arguments were not provided for command '
               '[{0}]: [{1}]'.format('.'.join(command_path),
                                     ', '.join(missing_arguments)))
    super(MissingArgumentException, self).__init__(message)


class UnexpectedArgumentException(ArgumentException):
  """An exception for when required arguments are not provided."""

  def __init__(self, command_path, unexpected_arguments):
    """Creates a new UnexpectedArgumentException.

    Args:
      command_path: A list representing the command or group that was given the
          unexpected arguments
      unexpected_arguments: A list of the arguments that were not valid
    """
    message = ('The following arguments were unexpected for command '
               '[{0}]: [{1}]'.format('.'.join(command_path),
                                     ', '.join(unexpected_arguments)))
    super(UnexpectedArgumentException, self).__init__(message)


class LayoutException(Exception):
  """LayoutException is for problems with module directory structure."""
  pass


class CommandLoadFailure(Exception):
  """An exception for when a command or group module cannot be imported."""

  def __init__(self, command, root_exception):
    self.command = command
    self.root_exception = root_exception
    super(CommandLoadFailure, self).__init__(
        'Problem loading {command}: {issue}.'.format(
            command=command, issue=str(root_exception)))


class ArgumentParser(argparse.ArgumentParser):
  """A custom subclass for arg parsing behavior.

  This overrides the default argparse parser.  It only changes a few things,
  mostly around the printing of usage error messages.
  """

  def __init__(self, *args, **kwargs):
    self._calliope_command = kwargs.pop('calliope_command', None)
    self._is_group = isinstance(self._calliope_command, CommandGroup)
    super(ArgumentParser, self).__init__(*args, **kwargs)

  def _check_value(self, action, value):
    """Override's argparse.ArgumentParser's ._check_value(action, value) method.

    Args:
      action: argparse.Action, The action being checked against this value.
      value: The command line argument provided that needs to correspond to this
          action.

    Raises:
      argparse.ArgumentError: If the action and value don't work together.
    """
    # This is copied from this method in argparse's version of this method.
    if action.choices is None or value in action.choices:
      return

    is_subparser = isinstance(action, CloudSDKSubParsersAction)
    # We add this to check if we can lazy load the element.
    if is_subparser and action.IsValidChoice(value):
      return

    # Not something we know, raise an error.

    if is_subparser:
      # We are going to show the usage anyway, which requires loading
      # everything.  Do this here so that choices gets populated.
      self._calliope_command.LoadAllSubElements()

    choices = sorted(action.choices)
    suggestion = usage_text.CommandChoiceSuggester().SuggestCommandChoice(
        value, choices)
    if suggestion:
      suggest = ' Did you mean %r?' % suggestion
    else:
      suggest = ''
    message = """\
Invalid choice: %r.%s
""" % (value, suggest)
    raise argparse.ArgumentError(action, message)

  def error(self, message):
    """Override's argparse.ArgumentParser's .error(message) method.

    Specifically, it avoids reprinting the program name and the string "error:".

    Args:
      message: str, The error message to print.
    """
    if self._is_group:
      # pylint:disable=protected-access
      shorthelp = usage_text.ShortHelpText(
          self._calliope_command, self._calliope_command._ai)
      # pylint:disable=protected-access
      argparse._sys.stderr.write(shorthelp + '\n')
    else:
      self.usage = usage_text.GenerateUsage(
          # pylint:disable=protected-access
          self._calliope_command, self._calliope_command._ai)
      # pylint:disable=protected-access
      self.print_usage(argparse._sys.stderr)

    log.error('({prog}) {message}'.format(prog=self.prog, message=message))
    self.exit(2)

  def _parse_optional(self, arg_string):
    """Override's argparse.ArgumentParser's ._parse_optional method.

    This allows the parser to have leading flags included in the grabbed
    arguments and stored in the namespace.

    Args:
      arg_string: str, The argument string.

    Returns:
      The normal return value of argparse.ArgumentParser._parse_optional.
    """
    positional_actions = self._get_positional_actions()
    option_tuple = super(ArgumentParser, self)._parse_optional(arg_string)
    # If parse_optional finds an action for this arg_string, use that option.
    # Note: option_tuple = (action, option_string, explicit_arg) or None
    known_option = option_tuple and option_tuple[0]
    if (len(positional_actions) == 1 and
        positional_actions[0].nargs == argparse.REMAINDER and
        not known_option):
      return None
    return option_tuple


# pylint:disable=protected-access
class CloudSDKSubParsersAction(argparse._SubParsersAction):
  """A custom subclass for arg parsing behavior.

  While the above ArgumentParser overrides behavior for parsing the flags
  associated with a specific group or command, this class overrides behavior
  for loading those sub parsers.  We use this to intercept the parsing right
  before it needs to start parsing args for sub groups and we then load the
  specific sub group it needs.
  """

  def __init__(self, *args, **kwargs):
    self._calliope_command = kwargs.pop('calliope_command', None)
    super(CloudSDKSubParsersAction, self).__init__(*args, **kwargs)

  def IsValidChoice(self, choice):
    """Determines if the given arg is a valid sub group or command.

    Args:
      choice: str, The name of the sub element to check.

    Returns:
      bool, True if the given item is a valid sub element, False otherwise.
    """
    # When using tab completion, argcomplete monkey patches various parts of
    # argparse and interferes with the normal argument parsing flow.  Usually
    # it is sufficient to check if the given choice is valid here, but delay
    # the loading until __call__ is invoked later during the parsing process.
    # During completion time, argcomplete tries to patch the subparser before
    # __call__ is called, so nothing has been loaded yet.  We need to force
    # load things here so that there will be something loaded for it to patch.
    # We also need to set self._orig_class because argcomplete compares this
    # directly to argparse._SubParsersAction to see if it should recursively
    # patch this parser.  It should really check to see if it is a subclass
    # but alas, it does not.
    if '_ARGCOMPLETE' in os.environ:
      self._calliope_command.LoadSubElement(choice)
      self._orig_class = argparse._SubParsersAction
    return self._calliope_command.IsValidSubElement(choice)

  def __call__(self, parser, namespace, values, option_string=None):
    # This is the name of the arg that is the sub element that needs to be
    # loaded.
    parser_name = values[0]
    # Load that element if it's there.  If it's not valid, nothing will be
    # loaded and normal error handling will take over.
    if self._calliope_command:
      self._calliope_command.LoadSubElement(parser_name)
    super(CloudSDKSubParsersAction, self).__call__(
        parser, namespace, values, option_string=option_string)


class ArgumentInterceptor(object):
  """ArgumentInterceptor intercepts calls to argparse parsers.

  The argparse module provides no public way to access a complete list of
  all arguments, and we need to know these so we can do validation of arguments
  when this library is used in the python interpreter mode. Argparse itself does
  the validation when it is run from the command line.

  Attributes:
    parser: argparse.Parser, The parser whose methods are being intercepted.
    allow_positional: bool, Whether or not to allow positional arguments.
    defaults: {str:obj}, A dict of {dest: default} for all the arguments added.
    required: [str], A list of the dests for all required arguments.
    dests: [str], A list of the dests for all arguments.
    positional_args: [argparse.Action], A list of the positional arguments.
    flag_args: [argparse.Action], A list of the flag arguments.

  Raises:
    ArgumentException: if a positional argument is made when allow_positional
        is false.
  """

  class ParserData(object):

    def __init__(self):
      self.defaults = {}
      self.required = []
      self.dests = []
      self.mutex_groups = {}
      self.positional_args = []
      self.flag_args = []
      self.ancestor_flag_args = []

  def __init__(self, parser, allow_positional, data=None, mutex_group_id=None):
    self.parser = parser
    self.allow_positional = allow_positional
    self.data = data or ArgumentInterceptor.ParserData()
    self.mutex_group_id = mutex_group_id

  @property
  def defaults(self):
    return self.data.defaults

  @property
  def required(self):
    return self.data.required

  @property
  def dests(self):
    return self.data.dests

  @property
  def mutex_groups(self):
    return self.data.mutex_groups

  @property
  def positional_args(self):
    return self.data.positional_args

  @property
  def flag_args(self):
    return self.data.flag_args

  @property
  def ancestor_flag_args(self):
    return self.data.ancestor_flag_args

  # pylint: disable=g-bad-name
  def add_argument(self, *args, **kwargs):
    """add_argument intercepts calls to the parser to track arguments."""
    # TODO(user): do not allow short-options without long-options.

    # we will choose the first option as the name
    name = args[0]

    positional = not name.startswith('-')
    if positional and not self.allow_positional:
      # TODO(user): More informative error message here about which group
      # the problem is in.
      raise ArgumentException('Illegal positional argument: ' + name)

    if positional and '-' in name:
      raise ArgumentException(
          "Positional arguments cannot contain a '-': " + name)

    dest = kwargs.get('dest')
    if not dest:
      # this is exactly what happens in argparse
      dest = name.lstrip(self.parser.prefix_chars).replace('-', '_')
    default = kwargs.get('default')
    required = kwargs.get('required')

    self.defaults[dest] = default
    if required:
      self.required.append(dest)
    self.dests.append(dest)
    if self.mutex_group_id:
      self.mutex_groups[dest] = self.mutex_group_id

    if positional and 'metavar' not in kwargs:
      kwargs['metavar'] = name.upper()

    added_argument = self.parser.add_argument(*args, **kwargs)

    if positional:
      self.positional_args.append(added_argument)
    else:
      self.flag_args.append(added_argument)

    return added_argument

  # pylint: disable=redefined-builtin
  def register(self, registry_name, value, object):
    return self.parser.register(registry_name, value, object)

  def set_defaults(self, **kwargs):
    return self.parser.set_defaults(**kwargs)

  def get_default(self, dest):
    return self.parser.get_default(dest)

  def add_argument_group(self, *args, **kwargs):
    new_parser = self.parser.add_argument_group(*args, **kwargs)
    return ArgumentInterceptor(parser=new_parser,
                               allow_positional=self.allow_positional,
                               data=self.data)

  def add_mutually_exclusive_group(self, **kwargs):
    new_parser = self.parser.add_mutually_exclusive_group(**kwargs)
    return ArgumentInterceptor(parser=new_parser,
                               allow_positional=self.allow_positional,
                               data=self.data,
                               mutex_group_id=id(new_parser))

  def AddFlagActionFromAncestors(self, action):
    """Add a flag action to this parser, but segregate it from the others.

    Segregating the action allows automatically generated help text to ignore
    this flag.

    Args:
      action: argparse.Action, The action for the flag being added.

    """
    # pylint:disable=protected-access, simply no other way to do this.
    self.parser._add_action(action)
    # explicitly do this second, in case ._add_action() fails.
    self.data.ancestor_flag_args.append(action)


class ConfigHooks(object):
  """This class holds function hooks for context and config loading/saving."""

  def __init__(
      self,
      load_context=None,
      context_filters=None,
      group_class=None):
    """Create a new object with the given hooks.

    Args:
      load_context: a function returns the context to be sent to commands.
      context_filters: a list of functions that take (contex, args),
          that will be called in order before a command is run. They are
          described in the README under the heading GROUP SPECIFICATION.
      group_class: base.Group, The class that this config hooks object is for.
    """
    self.load_context = load_context if load_context else lambda: {}
    self.context_filters = context_filters if context_filters else []
    self.group_class = group_class

  def OverrideWithBase(self, group_base):
    """Get a new ConfigHooks object with overridden functions based on module.

    If module defines any of the function, they will be used instead of what
    is in this object.  Anything that is not defined will use the existing
    behavior.

    Args:
      group_base: The base.Group class corresponding to the group.

    Returns:
      A new ConfigHooks object updated with any newly found hooks
    """

    def ContextFilter(context, http_func, args):
      group = group_base(http_func)
      group.Filter(context, args)
      return group
    # We want the new_context_filters to be a completely new list, if there is
    # a change.
    new_context_filters = self.context_filters + [ContextFilter]
    return ConfigHooks(load_context=self.load_context,
                       context_filters=new_context_filters,
                       group_class=group_base)


class CommandCommon(object):
  """A base class for CommandGroup and Command.

  It is responsible for extracting arguments from the modules and does argument
  validation, since this is always the same for groups and commands.
  """

  def __init__(self, module_dir, module_path, path, construction_id,
               cli_generator, config_hooks, help_func, parser_group,
               allow_positional_args, parent_group):
    """Create a new CommandCommon.

    Args:
      module_dir: str, The path to the tools directory that this command or
          group lives within. Used to find the command or group's source file.
      module_path: [str], The command group names that brought us down to this
          command group or command from the top module directory.
      path: [str], Similar to module_path, but is the path to this command or
          group with respect to the CLI itself.  This path should be used for
          things like error reporting when a specific element in the tree needs
          to be referenced.
      construction_id: str, A unique identifier for the CLILoader that is
          being constructed.
      cli_generator: cli.CLILoader, The builder used to generate this CLI.
      config_hooks: a ConfigHooks object to use for loading context.
      help_func: func([command path]), A function to call with --help.
      parser_group: argparse.Parser, The parser that this command or group will
          live in.
      allow_positional_args: bool, True if this command can have positional
          arguments.
      parent_group: CommandGroup, The parent of this command or group. None if
          at the root.
    """
    module = self._GetModuleFromPath(module_dir, module_path, path,
                                     construction_id)

    self._help_func = help_func
    self._config_hooks = config_hooks
    self._parent_group = parent_group

    # pylint:disable=protected-access, The base module is effectively an
    # extension of calliope, and we want to leave _Common private so people
    # don't extend it directly.
    common_type = base._Common.FromModule(module)

    self.name = path[-1]
    # For the purposes of argparse and the help, we should use dashes.
    self.cli_name = self.name.replace('_', '-')
    log.debug('Loaded Command Group: %s', path)
    path[-1] = self.cli_name
    self._module_path = module_path
    self._path = path
    self._construction_id = construction_id
    self._cli_generator = cli_generator

    self._common_type = common_type
    self._common_type.group_class = config_hooks.group_class
    self._common_type._cli_generator = cli_generator

    # Propagate down the hidden and release stage attributes of commands.
    if parent_group:
      if parent_group.is_hidden:
        self._common_type._is_hidden = True
      if parent_group.release_stage and not self._common_type.ReleaseStage():
        self._common_type._release_stage = parent_group.release_stage
    self.is_hidden = self._common_type.IsHidden()
    self.release_stage = self._common_type.ReleaseStage()

    (self.short_help, self.long_help) = usage_text.ExtractHelpStrings(
        self._common_type.__doc__)
    # Add an annotation to the help strings to mark the release stage.
    if self.release_stage:
      self.short_help = self.release_stage.tag + (self.short_help
                                                  if self.short_help else '')
      self.long_help = self.release_stage.tag + (self.long_help
                                                 if self.long_help else '')

    self.detailed_help = getattr(self._common_type, 'detailed_help', {})

    self._AssignParser(
        parser_group=parser_group,
        help_func=help_func,
        allow_positional_args=allow_positional_args)

  def _AssignParser(self, parser_group, help_func, allow_positional_args):
    """Assign a parser group to model this Command or CommandGroup.

    Args:
      parser_group: argparse._ArgumentGroup, the group that will model this
          command or group's arguments.
      help_func: func([str]), The long help function that is used for --help.
      allow_positional_args: bool, Whether to allow positional args for this
          group or not.

    """
    if not parser_group:
      # This is the root of the command tree, so we create the first parser.
      self._parser = ArgumentParser(
          description=self.long_help,
          add_help=False,
          prog='.'.join(self._path),
          calliope_command=self)
    else:
      # This is a normal sub group, so just add a new subparser to the existing
      # one.
      self._parser = parser_group.add_parser(
          self.cli_name,
          help=self.short_help,
          description=self.long_help,
          add_help=False,
          prog='.'.join(self._path),
          calliope_command=self)

    self._sub_parser = None

    self._ai = ArgumentInterceptor(
        parser=self._parser,
        allow_positional=allow_positional_args)

    self._short_help_action = actions.ShortHelpAction(self, self._ai)

    self._ai.add_argument(
        '-h', action=self._short_help_action,
        help='Print a summary help and exit.')

    if help_func:
      def LongHelp():
        help_func(
            self._path,
            default=usage_text.ShortHelpText(self, self._ai))
      long_help_action = actions.FunctionExitAction(LongHelp)
    else:
      long_help_action = self._short_help_action

    self._ai.add_argument(
        '--help', action=long_help_action,
        help='Display detailed help.')

    def Markdown(command):
      """Returns an action that lists the markdown help for command."""

      class Action(argparse.Action):

        def __call__(self, parser, namespace, values, option_string=None):
          command.LoadAllSubElements()
          markdown.Markdown(command, sys.stdout.write)
          sys.exit(0)

      return Action

    self._ai.add_argument(
        '--markdown', action=Markdown(self),
        nargs=0,
        help=argparse.SUPPRESS)

    self._AcquireArgs()

  def AllSubElements(self):
    return []

  def LoadAllSubElements(self, recursive=False):
    pass

  def LoadSubElement(self, name):
    pass

  def GetPath(self):
    return self._path

  def GetShortHelp(self):
    return usage_text.ShortHelpText(self, self._ai)

  def GetSubCommandHelps(self):
    return {}

  def GetSubGroupHelps(self):
    return {}

  def _GetModuleFromPath(self, module_dir, module_path, path, construction_id):
    """Import the module and dig into it to return the namespace we are after.

    Import the module relative to the top level directory.  Then return the
    actual module corresponding to the last bit of the path.

    Args:
      module_dir: str, The path to the tools directory that this command or
        group lives within.
      module_path: [str], The command group names that brought us down to this
        command group or command from the top module directory.
      path: [str], The same as module_path but with the groups named as they
        will be in the CLI.
      construction_id: str, A unique identifier for the CLILoader that is
        being constructed.

    Returns:
      The imported module.
    """
    src_dir = os.path.join(module_dir, *module_path[:-1])
    m = imp.find_module(module_path[-1], [src_dir])
    f, file_path, items = m
    # Make sure this module name never collides with any real module name.
    # Use the CLI naming path, so values are always unique.
    name = '__calliope__command__.{construction_id}.{name}'.format(
        construction_id=construction_id,
        name='.'.join(path).replace('-', '_'))
    try:
      module = imp.load_module(name, f, file_path, items)
    # pylint:disable=broad-except, We really do want to catch everything here,
    # because if any exceptions make it through for any single command or group
    # file, the whole CLI will not work. Instead, just log whatever it is.
    except Exception as e:
      _, _, exc_traceback = sys.exc_info()
      raise CommandLoadFailure('.'.join(path), e), None, exc_traceback
    finally:
      if f:
        f.close()
    return module

  def _AcquireArgs(self):
    """Call the function to register the arguments for this module."""
    args_func = self._common_type.Args
    if not args_func:
      return
    args_func(self._ai)

    if self._parent_group:
      # Add parent flags to children, if they aren't represented already
      for flag in self._parent_group.GetAllAvailableFlags():
        if flag.option_strings in [['-h'], ['--help'], ['-h', '--help'],
                                   ['--markdown']]:
          # Each command or group gets its own unique help flags.
          continue
        # Don't propagate down flags that we only want to be present at the top
        # level.
        if getattr(flag, 'global_only', False):
          continue
        if flag.required:
          # It is not easy to replicate required flags to subgroups and
          # subcommands, since then there would be two+ identical required
          # flags, and we'd want only one of them to be necessary.
          continue
        try:
          self._ai.AddFlagActionFromAncestors(flag)
        except argparse.ArgumentError:
          raise ArgumentException(
              'repeated flag in {command}: {flag}'.format(
                  command='.'.join(self._path),
                  flag=flag.option_strings))

  def GetAllAvailableFlags(self):
    return self._ai.flag_args + self._ai.ancestor_flag_args

  def _GetSubPathForName(self, name):
    """Gets a list of (module path, path) for the sub name.

    Args:
      name: str, The name of the sub group or command the path is for.

    Returns:
      A tuple of the new (module_path, path) for the given name.
      These terms are that as used by the constructor of CommandGroup and
      Command.
    """
    return (self._module_path + [name], self._path + [name])


class CommandGroup(CommandCommon):
  """A class to encapsulate a group of commands."""

  def __init__(self, module_dir, module_path, path, construction_id,
               cli_generator, parser_group, config_hooks, help_func,
               parent_group=None):
    """Create a new command group.

    Args:
      module_dir: always the root of the whole command tree
      module_path: a list of command group names that brought us down to this
          command group from the top module directory
      path: similar to module_path, but is the path to this command group
          with respect to the CLI itself.  This path should be used for things
          like error reporting when a specific element in the tree needs to be
          referenced
      construction_id: str, A unique identifier for the CLILoader that is
          being constructed.
      cli_generator: cli.CLILoader, The builder used to generate this CLI.
      parser_group: the current argparse parser, or None if this is the root
          command group.  The root command group will allocate the initial
          top level argparse parser.
      config_hooks: a ConfigHooks object to use for loading context
      help_func: func([command path]), A function to call with --help.
      parent_group: CommandGroup, The parent of this group. None if at the
          root.

    Raises:
      LayoutException: if the module has no sub groups or commands
    """

    super(CommandGroup, self).__init__(
        module_dir=module_dir,
        module_path=module_path,
        path=path,
        construction_id=construction_id,
        cli_generator=cli_generator,
        config_hooks=config_hooks,
        help_func=help_func,
        allow_positional_args=False,
        parser_group=parser_group,
        parent_group=parent_group)

    self._module_dir = module_dir

    self._config_hooks = self._config_hooks.OverrideWithBase(self._common_type)
    # find sub groups and commands
    self.groups = {}
    self.commands = {}
    self._groups_to_load = {}
    (self._group_names, self._command_names) = self._FindSubGroups()
    if not self._group_names and not self._command_names:
      raise LayoutException('Group %s has no subgroups or commands'
                            % '.'.join(self._path))
    # Initialize the sub-parser so sub groups can be found.
    self.SubParser()

  def SubParser(self):
    """Gets or creates the argparse sub parser for this group.

    Returns:
      The argparse subparser that children of this group should register with.
          If a sub parser has not been allocated, it is created now.
    """
    if not self._sub_parser:
      self._sub_parser = self._parser.add_subparsers(
          action=CloudSDKSubParsersAction, calliope_command=self)
    return self._sub_parser

  def AllSubElements(self):
    """Gets all the sub elements of this group.

    Returns:
      set(str), The names of all sub groups or commands under this group.
    """
    return (self._group_names |
            self._command_names |
            set(self._groups_to_load.iterkeys()))

  def IsValidSubElement(self, name):
    """Determines if the given name is a valid sub group or command.

    Args:
      name: str, The name of the possible sub element.

    Returns:
      bool, True if the name is a valid sub element of this group.
    """
    fixed_name = name.replace('-', '_')
    return fixed_name in self.AllSubElements()

  def LoadAllSubElements(self, recursive=False):
    """Load all the sub groups and commands of this group."""
    for name in self.AllSubElements():
      element = self.LoadSubElement(name)
      if recursive:
        element.LoadAllSubElements(recursive=recursive)

  def LoadSubElement(self, name):
    """Load a specific sub group or command.

    Args:
      name: str, The name of the element to load.

    Returns:
      _CommandCommon, The loaded sub element, or None if it did not exist.
    """
    name = name.replace('-', '_')

    # See if this element has already been loaded.
    existing = self.groups.get(name, None)
    if not existing:
      existing = self.commands.get(name, None)
    if existing:
      return existing
    if not self.IsValidSubElement(name):
      return None

    (new_module_path, new_path) = self._GetSubPathForName(name)

    element = None
    if name in self._group_names:
      element = self._LoadSubGroup(self._module_dir, new_module_path, new_path)
    elif name in self._groups_to_load:
      element = self._LoadSubGroup(*self._groups_to_load[name])
    elif name in self._command_names:
      element = Command(
          self._module_dir, new_module_path, new_path, self._construction_id,
          self._cli_generator, self._config_hooks, self.SubParser(),
          self._help_func, parent_group=self)
      self.commands[element.name] = element
    return element

  def _LoadSubGroup(self, module_dir, module_path, path):
    group = CommandGroup(
        module_dir, module_path, path, self._construction_id,
        self._cli_generator, self.SubParser(), self._config_hooks,
        help_func=self._help_func, parent_group=self)
    self.groups[group.name] = group
    return group

  def GetSubCommandHelps(self):
    return dict(
        (item.cli_name,
         usage_text.HelpInfo(help_text=item.short_help,
                             is_hidden=item.is_hidden,
                             release_stage=item.release_stage))
        for item in self.commands.values())

  def GetSubGroupHelps(self):
    return dict(
        (item.cli_name,
         usage_text.HelpInfo(help_text=item.short_help,
                             is_hidden=item.is_hidden,
                             release_stage=item.release_stage))
        for item in self.groups.values())

  def GetHelpFunc(self):
    return self._help_func

  def AddSubGroup(self, group_info):
    """Merges another command group under this one.

    If we load command groups for alternate locations, this method is used to
    make those extra sub groups fall under this main group in the CLI.

    Args:
      group_info: A tuple of (module_dir, module_path, path).  The arguments
        to pass to the _LoadSubGroup() method for lazy loading this group.
    """
    # The last element of the path (which is the group's name.
    name = group_info[2][-1]
    self._groups_to_load[name] = group_info

  def _FindSubGroups(self):
    """Final all the sub groups and commands under this group.

    Returns:
      A tuple containing two sets. The first is a set of strings for each
      command group, and the second is a set of strings for each command.

    Raises:
      LayoutException: if there is a command or group with an illegal name.
    """
    location = os.path.join(self._module_dir, *self._module_path)
    items = os.listdir(location)
    groups = set()
    commands = set()
    items.sort()
    for item in items:
      name, ext = os.path.splitext(item)
      itempath = os.path.join(location, item)

      if ext == '.py':
        if name == '__init__':
          continue
      elif not os.path.isdir(itempath):
        continue

      if re.search('[A-Z]', name):
        raise LayoutException('Commands and groups cannot have capital letters:'
                              ' %s.' % name)

      if not os.path.isdir(itempath):
        commands.add(name)
      else:
        init_path = os.path.join(itempath, '__init__.py')
        if os.path.exists(init_path):
          groups.add(item)
    return groups, commands


class Command(CommandCommon):
  """A class that encapsulates the configuration for a single command."""

  def __init__(self, module_dir, module_path, path, construction_id,
               cli_generator, config_hooks, parser_group, help_func,
               parent_group=None):
    """Create a new command.

    Args:
      module_dir: str, The root of the command tree.
      module_path: a list of command group names that brought us down to this
          command from the top module directory
      path: similar to module_path, but is the path to this command with respect
          to the CLI itself.  This path should be used for things like error
          reporting when a specific element in the tree needs to be referenced
      construction_id: str, A unique identifier for the CLILoader that is
          being constructed.
      cli_generator: cli.CLILoader, The builder used to generate this CLI.
      config_hooks: a ConfigHooks object to use for loading context
      parser_group: argparse.Parser, The parser to be used for this command.
      help_func: func([str]), Detailed help function.
      parent_group: CommandGroup, The parent of this command.
    """
    super(Command, self).__init__(
        module_dir=module_dir,
        module_path=module_path,
        path=path,
        construction_id=construction_id,
        cli_generator=cli_generator,
        config_hooks=config_hooks,
        help_func=help_func,
        allow_positional_args=True,
        parser_group=parser_group,
        parent_group=parent_group)

    self._parser.set_defaults(cmd_func=self.Run, command_path=self._path)

  def Run(self, cli, args, pre_run_hooks=None, post_run_hooks=None):
    """Run this command with the given arguments.

    Args:
      cli: The cli.CLI object for this command line tool.
      args: The arguments for this command as a namespace.
      pre_run_hooks: [_RunHook], Things to run before the command.
      post_run_hooks: [_RunHook], Things to run after the command.

    Returns:
      The object returned by the module's Run() function.

    Raises:
      exceptions.Error: if thrown by the Run() function.
    """
    command_path_string = '.'.join(self._path)

    # TODO(user): user-output-enabled was mostly needed for interactive
    # mode.  There should still be the option to disable output (for things
    # like completion) but it can be cleaned up to be on by default.
    # Enable user output for CLI mode only if it is not explicitly set in the
    # properties (or given in the provided arguments that were just pushed into
    # the properties object).
    user_output_enabled = properties.VALUES.core.user_output_enabled.GetBool()
    set_user_output_property = user_output_enabled is None
    if set_user_output_property:
      properties.VALUES.core.user_output_enabled.Set(True)
    # Now that we have pushed the args, reload the settings so the flags will
    # take effect.  These will use the values from the properties.
    old_user_output_enabled = log.SetUserOutputEnabled(None)
    old_verbosity = log.SetVerbosity(None)

    try:
      if pre_run_hooks:
        for hook in pre_run_hooks:
          hook.Run(command_path_string)

      def Http(**kwargs):
        # TODO(user) This check is required due to tests that use interactive
        # mode. Remove this check when all tests are converted to use cli mode.
        if hasattr(args, 'trace_token'):
          return core_cli.Http(cmd_path=command_path_string,
                               trace_token=args.trace_token,
                               **kwargs)
        else:
          return core_cli.Http(cmd_path=command_path_string, **kwargs)

      tool_context = self._config_hooks.load_context()
      last_group = None
      for context_filter in self._config_hooks.context_filters:
        last_group = context_filter(tool_context, Http, args)

      command_instance = self._common_type(
          cli=cli,
          context=tool_context,
          group=last_group,
          http_func=Http)

      def OutputFormatter(obj):
        command_instance.Display(args, obj)
      output_formatter = OutputFormatter

      def Format(obj):
        if not obj:
          return
        resource_printer.Print(obj, args.format or 'yaml', out=log.out)
      command_instance.format = Format
      if args.format:
        output_formatter = command_instance.format

      log.debug('Running %s with %s.', command_path_string, args)
      result = command_instance.Run(args)
      if properties.VALUES.core.user_output_enabled.GetBool():
        output_formatter(result)

      if post_run_hooks:
        for hook in post_run_hooks:
          hook.Run(command_path_string)

      return result

    except exceptions.ExitCodeNoError as exc:
      msg = '({0}) {1}'.format(command_path_string, str(exc))
      log.debug(msg, exc_info=sys.exc_info())
      self._Exit(exc)
    except core_exceptions.Error as exc:
      msg = '({0}) {1}'.format(command_path_string, str(exc))
      log.debug(msg, exc_info=sys.exc_info())
      log.error(msg)
      self._Exit(exc)
    except Exception as exc:
      # Make sure any uncaught exceptions still make it into the log file.
      log.file_only_logger.debug(str(exc), exc_info=sys.exc_info())
      raise
    finally:
      if set_user_output_property:
        properties.VALUES.core.user_output_enabled.Set(None)
      log.SetUserOutputEnabled(old_user_output_enabled)
      log.SetVerbosity(old_verbosity)

  def _Exit(self, exc):
    """This method exists so we can mock this out during testing to not exit."""
    sys.exit(exc.exit_code)
