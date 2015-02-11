# Copyright 2013 Google Inc. All Rights Reserved.

"""Exceptions that can be thrown by calliope tools.

The exceptions in this file, and those that extend them, can be thrown by
the Run() function in calliope tools without worrying about stack traces
littering the screen in CLI mode. In interpreter mode, they are not caught
from within calliope.
"""

from functools import wraps
import sys

from googlecloudsdk.core import exceptions as core_exceptions
from googlecloudsdk.core import log


class ToolException(core_exceptions.Error):
  """ToolException is for Run methods to throw for non-code-bug errors.

  Attributes:
    command_name: The dotted group and command name for the command that threw
        this exception. This value is set by calliope.
  """

  @staticmethod
  def FromCurrent(*args):
    """Creates a new ToolException based on the current exception being handled.

    If no exception is being handled, a new ToolException with the given args
    is created.  If there is a current exception, the original exception is
    first logged (to file only).  A new ToolException is then created with the
    same args as the current one.

    Args:
      *args: The standard args taken by the constructor of Exception for the new
        exception that is created.  If None, the args from the exception
        currently being handled will be used.

    Returns:
      The generated ToolException.
    """
    (_, current_exception, _) = sys.exc_info()

    # Log original exception details and traceback to the log file if we are
    # currently handling an exception.
    if current_exception:
      file_logger = log.file_only_logger
      file_logger.error('Handling the source of a tool exception, '
                        'original details follow.')
      file_logger.exception(current_exception)

    if args:
      return ToolException(*args)
    elif current_exception:
      return ToolException(*current_exception.args)
    return ToolException('An unknown error has occurred')


class ExitCodeNoError(core_exceptions.Error):
  """A special exception for exit codes without error messages.

  If this exception is raised, it's identical in behavior to returning from
  the command code, except the overall exit code will be different.
  """


def RaiseToolExceptionInsteadOf(*error_types):
  """RaiseToolExceptionInsteadOf is a decorator that re-raises as ToolException.

  If any of the error_types are raised in the decorated function, this decorator
  will re-raise the as a ToolException.

  Args:
    *error_types: [Exception], A list of exception types that this decorator
        will watch for.

  Returns:
    The decorated function.
  """
  def Wrap(func):
    """Wrapper function for the decorator."""
    @wraps(func)
    def TryFunc(*args, **kwargs):
      try:
        return func(*args, **kwargs)
      except error_types:
        (_, _, exc_traceback) = sys.exc_info()
        # The 3 element form takes (type, instance, traceback).  If the first
        # element is an instance, it is used as the type and instance and the
        # second element must be None.  This preserves the original traceback.
        # pylint:disable=nonstandard-exception, ToolException is an Exception.
        raise ToolException.FromCurrent(), None, exc_traceback
    return TryFunc
  return Wrap


class InvalidArgumentException(ToolException):
  """InvalidArgumentException is for malformed arguments."""

  def __init__(self, parameter_name, message):
    self.parameter_name = parameter_name
    self.message = message
    super(InvalidArgumentException, self).__init__(
        'Invalid value for [{0}]: {1}'.format(
            self.parameter_name,
            self.message))


class InvalidStringException(ToolException):
  """InvalidArgumentException is for non-ASCII CLI arguments."""

  def __init__(self, invalid_arg):
    self.invalid_arg = invalid_arg
    super(InvalidStringException, self).__init__(
        u'Invalid argument [{0}]: all arguments must be ASCII'.format(
            self.invalid_arg))


class HttpException(ToolException):
  """HttpException is raised whenever the Http response status code != 200."""

  def __init__(self, error):
    super(HttpException, self).__init__(error)
    self.error = error


class UnknownArgumentException(ToolException):
  """UnknownArgumentException is for arguments with unexpected values."""

  def __init__(self, parameter_name, message):
    self.parameter_name = parameter_name
    self.message = message
    super(UnknownArgumentException, self).__init__(
        'Unknown value for [{0}]: {1}'.format(
            self.parameter_name,
            self.message))


class BadFileException(ToolException):
  """BadFileException is for problems reading or writing a file."""


class RequiredArgumentException(ToolException):
  """An exception for when a usually optional argument is required in this case.
  """

  def __init__(self, parameter_name, message):
    self.parameter_name = parameter_name
    self.message = message
    super(RequiredArgumentException, self).__init__(
        'Missing required argument [{0}]: {1}'.format(
            self.parameter_name,
            self.message))
