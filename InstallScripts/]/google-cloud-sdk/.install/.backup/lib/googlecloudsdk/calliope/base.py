# Copyright 2013 Google Inc. All Rights Reserved.
"""Base classes for calliope commands and groups.

"""

import abc

from googlecloudsdk.calliope import usage_text


class LayoutException(Exception):
  """An exception for when a command or group .py file has the wrong types."""


class _Common(object):
  """Base class for Command and Group.

  Attributes:
    config: {str:object}, A set of key-value pairs that will persist (as long
        as they are JSON-serializable) between command invocations. Can be used
        for caching.
    http_func: function that returns an http object that can be used during
        service requests.
  """

  __metaclass__ = abc.ABCMeta
  _cli_generator = None
  _is_hidden = False
  _release_stage = None

  def __init__(self, http_func):
    self._http_func = http_func

  @staticmethod
  def FromModule(module):
    """Get the type implementing CommandBase from the module.

    Args:
      module: module, The module resulting from importing the file containing a
          command.

    Returns:
      type, The custom class that implements CommandBase.

    Raises:
      LayoutException: If there is not exactly one type inheriting
          CommonBase.

    """
    command_type = None

    for thing in module.__dict__.values():
      if issubclass(type(thing), type) and issubclass(thing, _Common):
        if command_type:
          raise LayoutException(
              'More than one _CommonBase subclasses in %s' % module.__file__)
        command_type = thing

    if not command_type:
      raise LayoutException(
          'No _CommonBase subclasses in %s' % module.__file__)

    return command_type

  @staticmethod
  def Args(parser):
    """Set up arguments for this command.

    Args:
      parser: An argparse.ArgumentParser-like object. It is mocked out in order
          to capture some information, but behaves like an ArgumentParser.
    """
    pass

  @classmethod
  def IsHidden(cls):
    return cls._is_hidden

  @classmethod
  def ReleaseStage(cls):
    return cls._release_stage

  @classmethod
  def GetExecutionFunction(cls, *args):
    """Get a fully bound function that will call another gcloud command.

    This class method can be called at any time to generate a function that will
    execute another gcloud command.  The function itself can only be executed
    after the gcloud CLI has been build i.e. after all Args methods have
    been called.

    Args:
      *args: str, The args for the command to execute.  Each token should be a
        separate string and the tokens should start from after the 'gcloud'
        part of the invocation.

    Returns:
      A bound function to call the gcloud command.
    """
    def ExecFunc():
      return cls._cli_generator.Generate().Execute(list(args),
                                                   call_arg_complete=False)
    return ExecFunc

  @classmethod
  def GetCLIGenerator(cls):
    """Get a generator function that can be used to execute a gcloud command.

    Returns:
      A bound generator function to execute a gcloud command.
    """
    return cls._cli_generator.Generate

  def Http(self, auth=True, creds=None, timeout=None):
    """Get the http object to be used during service requests.

    Args:
      auth: bool, True if the http object returned should be authorized.
      creds: oauth2client.client.Credentials, If auth is True and creds is not
          None, use those credentials to authorize the httplib2.Http object.
      timeout: double, The timeout in seconds to pass to httplib2.  This is the
          socket level timeout.  If timeout is None, timeout is infinite.

    Returns:
      httplib2.Http, http object to be used during service requests.
    """
    return self._http_func(auth=auth, creds=creds, timeout=timeout)


class Command(_Common):
  """Command is a base class for commands to implement.

  Attributes:
    cli: calliope.cli.CLI, The CLI object representing this command line tool.
    context: {str:object}, A set of key-value pairs that can be used for
        common initialization among commands.
    group: base.Group, The instance of the group class above this command.  You
        can use this to access common methods within a group.
    format: func(obj), A function that prints objects to stdout using the
        user-chosen formatting option.
    http_func: function that returns an http object that can be used during
        service requests.
  """

  __metaclass__ = abc.ABCMeta

  def __init__(self, cli, context, group, http_func):
    super(Command, self).__init__(http_func)
    self.cli = cli
    self.context = context
    self.group = group
    self.format = None  # This attribute is set before .Run() is called.

  def ExecuteCommand(self, args):
    self.cli.Execute(args, call_arg_complete=False)

  @abc.abstractmethod
  def Run(self, args):
    """Run the command.

    Args:
      args: argparse.Namespace, An object that contains the values for the
          arguments specified in the .Args() method.
    Returns:
      A python object that is given back to the python caller, or sent to the
      .Display() method in CLI mode.
    """
    raise NotImplementedError('CommandBase.Run is not overridden')

  def Display(self, args, result):
    """Print the result for a human to read from the terminal.

    Args:
      args: argparse.Namespace: The same namespace given to the corresponding
          .Run() invocation.
      result: object, The object return by the corresponding .Run() invocation.
    """
    pass


class Group(_Common):
  """Group is a base class for groups to implement.

  Attributes:
    http_func: function that returns an http object that can be used during
        service requests.
  """

  def __init__(self, http_func):
    super(Group, self).__init__(http_func)

  def Filter(self, context, args):
    """Modify the context that will be given to this group's commands when run.

    Args:
      context: {str:object}, A set of key-value pairs that can be used for
          common initialization among commands.
      args: argparse.Namespace: The same namespace given to the corresponding
          .Run() invocation.
    """
    pass


class Argument(object):
  """A class that allows you to save an argument configuration for reuse."""

  def __init__(self, *args, **kwargs):
    """Creates the argument.

    Args:
      *args: The positional args to parser.add_argument.
      **kwargs: The keyword args to parser.add_argument.
    """
    try:
      self.__detailed_help = kwargs.pop('detailed_help')
    except KeyError:
      self.__detailed_help = None
    self.__args = args
    self.__kwargs = kwargs

  def AddToParser(self, parser):
    """Adds this argument to the given parser.

    Args:
      parser: The argparse parser.

    Returns:
      The result of parser.add_argument().
    """
    arg = parser.add_argument(*self.__args, **self.__kwargs)
    if self.__detailed_help:
      arg.detailed_help = self.__detailed_help
    return arg


def Hidden(cmd_class):
  """Decorator for hiding calliope commands and groups.

  Decorate a subclass of base.Command or base.Group with this function, and the
  decorated command or group will not show up in help text.

  Args:
    cmd_class: base._Common, A calliope command or group.

  Returns:
    A modified version of the provided class.
  """
  # pylint: disable=protected-access
  cmd_class._is_hidden = True
  return cmd_class


def Alpha(cmd_class):
  """Decorator for annotating a command or group as ALPHA.

  Args:
    cmd_class: base._Common, A calliope command or group.

  Returns:
    A modified version of the provided class.
  """
  # pylint: disable=protected-access
  cmd_class._release_stage = usage_text.ReleaseStageAnnotation.ALPHA
  return cmd_class


def Beta(cmd_class):
  """Decorator for annotating a command or group as BETA.

  Args:
    cmd_class: base._Common, A calliope command or group.

  Returns:
    A modified version of the provided class.
  """
  # pylint: disable=protected-access
  cmd_class._release_stage = usage_text.ReleaseStageAnnotation.BETA
  return cmd_class
