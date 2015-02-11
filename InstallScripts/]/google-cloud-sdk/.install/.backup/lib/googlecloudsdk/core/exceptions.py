# Copyright 2014 Google Inc. All Rights Reserved.

"""Base exceptions for the Cloud SDK."""


from googlecloudsdk.core.util import platforms


class _Error(Exception):
  """A base exception for all Cloud SDK errors.

  This exception should not be used directly.
  """
  pass


class InternalError(_Error):
  """A base class for all non-recoverable internal errors."""
  pass


class Error(_Error):
  """A base exception for all user recoverable errors.

  Any exception that extends this class will not be printed with a stack trace
  when running from CLI mode.  Instead it will be shows with a message of how
  the user can correct this problem.

  All exceptions of this type must have a message for the user.
  """

  def __init__(self, *args, **kwargs):
    """Initialize a core.Error.

    Args:
      *args: positional args for exceptions.
      **kwargs: keyword args for exceptions, and additional arguments:
        - exit_code: int, The desired exit code for the CLI.
    """
    super(Error, self).__init__(*args)
    self.exit_code = kwargs.get('exit_code', 1)


class RequiresAdminRightsError(Error):
  """An exception for when you don't have permission to modify the SDK.

  This tells the user how to run their command with administrator rights so that
  they can perform the operation.
  """

  def __init__(self, sdk_root):
    message = (
        'You cannot perform this action because you do not have permission '
        'to modify the Google Cloud SDK installation directory [{root}].\n\n'
        .format(root=sdk_root))
    if (platforms.OperatingSystem.Current() ==
        platforms.OperatingSystem.WINDOWS):
      message += (
          'Click the Google Cloud SDK Shell icon and re-run the command in '
          'that window, or re-run the command with elevated privileges by '
          'right-clicking cmd.exe and selecting "Run as Administrator".')
    else:
      message += (
          'Re-run the command with sudo: sudo gcloud ...')
    super(RequiresAdminRightsError, self).__init__(message)
