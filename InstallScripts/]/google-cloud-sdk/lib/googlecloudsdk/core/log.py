# Copyright 2013 Google Inc. All Rights Reserved.

"""Module with logging related functionality for calliope."""

import datetime
import errno
import logging
import os
import sys
import time

from googlecloudsdk.core import properties
from googlecloudsdk.core.util import platforms


DEFAULT_VERBOSITY = logging.WARNING
DEFAULT_VERBOSITY_STRING = 'warning'
DEFAULT_USER_OUTPUT_ENABLED = False
# This will get set once at import.  This is how we can know whether this was
# set in the properties before it was changed by running commands.
INITIAL_USER_OUTPUT_ENABLED = (properties.VALUES.core.user_output_enabled
                               .GetBool())
VERBOSITY_LEVELS = [
    ('debug', logging.DEBUG),
    ('info', logging.INFO),
    ('warning', logging.WARNING),
    ('error', logging.ERROR),
    ('critical', logging.CRITICAL),
    ('none', logging.CRITICAL + 10)]
VALID_VERBOSITY_STRINGS = dict(VERBOSITY_LEVELS)
LOG_FILE_EXTENSION = '.log'
# datastore upload and download creates temporary sql3 files in the log dir.
_KNOWN_LOG_FILE_EXTENSIONS = [LOG_FILE_EXTENSION, '.sql3']


class _NullHandler(logging.Handler, object):
  """A replication of python2.7's logging.NullHandler.

  We recreate this class here to ease python2.6 compatibility.
  """

  def handle(self, record):
    pass

  def emit(self, record):
    pass

  def createLock(self):
    self.lock = None


class _UserOutputFilter(object):
  """A filter to turn on and off user output.

  This filter is used by the ConsoleWriter to determine if output messages
  should be printed or not.
  """

  def __init__(self, enabled):
    """Creates the filter.

    Args:
      enabled: bool, True to enable output, false to suppress.
    """
    self.enabled = enabled


class _StreamWrapper(object):
  """A class to hold an output stream that we can manipulate."""

  def __init__(self, stream):
    """Creates the stream wrapper.

    Args:
      stream: The stream to hold on to.
    """
    self.stream = stream


class _ConsoleWriter(object):
  """A class that wraps stdout or stderr so we can control how it gets logged.

  This class is a stripped down file-like object that provides the basic
  writing methods.  When you write to this stream, if it is enabled, it will be
  written to stdout.  All strings will also be logged at DEBUG level so they
  can be captured by the log file.
  """

  def __init__(self, logger, output_filter, stream_wrapper):
    """Creates a new _ConsoleWriter wrapper.

    Args:
      logger: logging.Logger, The logger to log to.
      output_filter: _UserOutputFilter, Used to determine whether to write
        output or not.
      stream_wrapper: _StreamWrapper, The wrapper for the output stream,
        stdout or stderr.
    """
    self.__logger = logger
    self.__filter = output_filter
    self.__stream_wrapper = stream_wrapper

  def Print(self, *msg):
    """Writes the given message to the output stream, and adds a newline.

    This method has the same output behavior as the build in print method but
    respects the configured verbosity.

    Args:
      *msg: str, The messages to print.
    """
    message = ' '.join([str(m) for m in msg])
    self.__logger.info(message)
    if self.__filter.enabled:
      self.__stream_wrapper.stream.write(message + '\n')

  # pylint: disable=g-bad-name, This must match file-like objects
  def write(self, msg):
    self.__logger.info(msg)
    if self.__filter.enabled:
      self.__stream_wrapper.stream.write(msg)

  # pylint: disable=g-bad-name, This must match file-like objects
  def writelines(self, lines):
    for line in lines:
      self.__logger.info(line)
    if self.__filter.enabled:
      self.__stream_wrapper.stream.writelines(lines)

  # pylint: disable=g-bad-name, This must match file-like objects
  def flush(self):
    if self.__filter.enabled:
      self.__stream_wrapper.stream.flush()

  def isatty(self):
    isatty = getattr(self.__stream_wrapper.stream, 'isatty', None)
    return isatty() if isatty else False


class _ConsoleFormatter(logging.Formatter):
  """A formatter for the console logger, handles colorizing messages."""

  LEVEL = '%(levelname)s:'
  MESSAGE = ' %(message)s'
  DEFAULT_FORMAT = LEVEL + MESSAGE

  RED = '\033[1;31m'
  YELLOW = '\033[1;33m'
  END = '\033[0m'

  FORMATS = {}
  COLOR_FORMATS = {
      logging.WARNING: YELLOW + LEVEL + END + MESSAGE,
      logging.ERROR: RED + LEVEL + END + MESSAGE,
      logging.FATAL: RED + LEVEL + MESSAGE + END,
  }

  def __init__(self, out_stream):
    logging.Formatter.__init__(self)
    use_color = not properties.VALUES.core.disable_color.GetBool()
    use_color &= out_stream.isatty()
    use_color &= (platforms.OperatingSystem.Current() !=
                  platforms.OperatingSystem.WINDOWS)
    self._formats = (_ConsoleFormatter.COLOR_FORMATS
                     if use_color else _ConsoleFormatter.FORMATS)

  def format(self, record):
    self._fmt = self._formats.get(record.levelno,
                                  _ConsoleFormatter.DEFAULT_FORMAT)
    return logging.Formatter.format(self, record)


class _LogManager(object):
  """A class to manage the logging handlers based on how calliope is being used.

  We want to always log to a file, in addition to logging to stdout if in CLI
  mode.  This sets up the required handlers to do this.
  """
  FILE_ONLY_LOGGER_NAME = '___FILE_ONLY___'
  MAX_AGE = 60 * 60 * 24 * 30  # 30 days' worth of seconds.

  def __init__(self):
    self.console_formatter = _ConsoleFormatter(sys.stderr)
    self.file_formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)-8s %(name)-15s %(message)s')

    # Set up the root logger, it accepts all levels.
    self.logger = logging.getLogger()
    self.logger.setLevel(logging.NOTSET)

    # This logger will get handlers for each output file, but will not propagate
    # to the root logger.  This allows us to log exceptions and errors to the
    # files without it showing up in the terminal.
    self.file_only_logger = logging.getLogger(_LogManager.FILE_ONLY_LOGGER_NAME)
    # Accept all log levels for files.
    self.file_only_logger.setLevel(logging.NOTSET)
    self.file_only_logger.propagate = False

    self.logs_dirs = []

    self.user_output_filter = _UserOutputFilter(DEFAULT_USER_OUTPUT_ENABLED)
    self.stdout_stream_wrapper = _StreamWrapper(sys.stdout)
    self.stderr_stream_wrapper = _StreamWrapper(sys.stderr)

    self.stdout_writer = _ConsoleWriter(self.file_only_logger,
                                        self.user_output_filter,
                                        self.stdout_stream_wrapper)
    self.stderr_writer = _ConsoleWriter(self.file_only_logger,
                                        self.user_output_filter,
                                        self.stderr_stream_wrapper)

    self.verbosity = None
    self.user_output_enabled = None
    self.current_log_file = None
    self.Reset()

  def Reset(self):
    """Resets all logging functionality to its default state."""
    # Clears any existing logging handlers.
    self.logger.handlers[:] = []

    # Refresh the streams for the console writers.
    self.stdout_stream_wrapper.stream = sys.stdout
    self.stderr_stream_wrapper.stream = sys.stderr

    # Reset the color handling.
    self.console_formatter = _ConsoleFormatter(sys.stderr)

    # A handler to redirect logs to stderr, this one is standard.
    self.stderr_handler = logging.StreamHandler(sys.stderr)
    self.stderr_handler.setFormatter(self.console_formatter)
    self.stderr_handler.setLevel(DEFAULT_VERBOSITY)
    self.logger.addHandler(self.stderr_handler)

    # Reset all the log file handlers.
    self.file_only_logger.handlers[:] = []
    self.file_only_logger.addHandler(_NullHandler())

    # Reset verbosity and output settings.
    self.SetVerbosity(None)
    self.SetUserOutputEnabled(None)
    self.current_log_file = None

  def SetVerbosity(self, verbosity):
    """Sets the active verbosity for the logger.

    Args:
      verbosity: int, A verbosity constant from the logging module that
        determines what level of logs will show in the console. If None, the
        value from properties or the default will be used.

    Returns:
      int, The current verbosity.
    """
    if verbosity is None:
      # Try to load from properties if set.
      verbosity_string = properties.VALUES.core.verbosity.Get()
      if verbosity_string is not None:
        verbosity = VALID_VERBOSITY_STRINGS.get(verbosity_string.lower())
    if verbosity is None:
      # Final fall back to default verbosity.
      verbosity = DEFAULT_VERBOSITY

    if self.verbosity == verbosity:
      return self.verbosity

    self.stderr_handler.setLevel(verbosity)

    old_verbosity = self.verbosity
    self.verbosity = verbosity
    return old_verbosity

  def SetUserOutputEnabled(self, enabled):
    """Sets whether user output should go to the console.

    Args:
      enabled: bool, True to enable output, False to suppress.  If None, the
        value from properties or the default will be used.

    Returns:
      bool, The old value of enabled.
    """
    if enabled is None:
      enabled = properties.VALUES.core.user_output_enabled.GetBool()
    if enabled is None:
      enabled = DEFAULT_USER_OUTPUT_ENABLED

    self.user_output_filter.enabled = enabled

    old_enabled = self.user_output_enabled
    self.user_output_enabled = enabled
    return old_enabled

  def AddLogsDir(self, logs_dir):
    """Adds a new logging directory to the logging config.

    Args:
      logs_dir: str, Path to a directory to store log files under.  This method
        has no effect if this is None, or if this directory has already been
        registered.
    """
    if not logs_dir or logs_dir in self.logs_dirs:
      return
    self.logs_dirs.append(logs_dir)

    # Try to delete old log files in the given directory. Continue normally if
    # we try to delete log files that do not exist. This can happen when two
    # gcloud instances are cleaning up logs in parallel.
    try:
      self._CleanLogsDir(logs_dir)
    except OSError as exp:
      if exp.errno != errno.ENOENT:
        raise

    # A handler to write DEBUG and above to log files in the given directory
    log_file = self._SetupLogsDir(logs_dir)
    self.current_log_file = log_file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.NOTSET)
    file_handler.setFormatter(self.file_formatter)
    self.logger.addHandler(file_handler)
    self.file_only_logger.addHandler(file_handler)

  def _CleanLogsDir(self, logs_dir):
    """Cleans up old log files form the given logs directory.

    Args:
      logs_dir: str, The path to the logs directory.
    """
    now_seconds = time.time()

    # First delete log files in this directory that are older than MAX_AGE.
    for (dirpath, dirnames, filenames) in os.walk(logs_dir, topdown=True):
      # We skip any directories with a too-new st_mtime. This skipping can
      # result in some false negatives, but that's ok since the files in the
      # skipped directory are at most one day too old.
      to_process = []
      for dirname in dirnames:
        logdirpath = os.path.join(dirpath, dirname)
        if self._ShouldDelete(now_seconds, logdirpath):
          to_process.append(dirname)
      dirnames[:] = to_process

      for filename in filenames:
        # Skip if filename is not formatted like a log file.
        unused_non_ext, ext = os.path.splitext(filename)
        if ext not in _KNOWN_LOG_FILE_EXTENSIONS:
          continue

        # Remove if the file is older than MAX_AGE.
        filepath = os.path.join(dirpath, filename)
        if self._ShouldDelete(now_seconds, filepath):
          os.remove(filepath)

    # Second, delete any log directories that are now empty.
    for (dirpath, dirnames, filenames) in os.walk(logs_dir, topdown=False):
      # Since topdown is false, we get the children before the parents.
      if not filenames and not dirnames:
        # Delete if empty.
        os.rmdir(dirpath)

  def _ShouldDelete(self, now_seconds, path):
    """Determines if the file or directory is old enough to be deleted.

    Args:
      now_seconds: int, The current time in seconds.
      path: str, The file or directory path to check.

    Returns:
      bool, True if it should be deleted, False otherwise.
    """
    stat_info = os.stat(path)
    return now_seconds - stat_info.st_mtime > _LogManager.MAX_AGE

  def _SetupLogsDir(self, logs_dir):
    """Creates the necessary log directories and get the file name to log to.

    Logs are created under the given directory.  There is a sub-directory for
    each day, and logs for individual invocations are created under that.

    Deletes files in this directory that are older than MAX_AGE.

    Args:
      logs_dir: str, Path to a directory to store log files under

    Returns:
      str, The path to the file to log to
    """
    now = datetime.datetime.now()
    day_dir_name = now.strftime('%Y.%m.%d')
    day_dir_path = os.path.join(logs_dir, day_dir_name)
    try:
      os.makedirs(day_dir_path)
    except OSError as ex:
      if ex.errno == errno.EEXIST and os.path.isdir(day_dir_path):
        pass
      else:
        raise

    filename = '{timestamp}{ext}'.format(timestamp=now.strftime('%H.%M.%S.%f'),
                                         ext=LOG_FILE_EXTENSION)
    log_file = os.path.join(day_dir_path, filename)
    return log_file


_log_manager = _LogManager()

# The configured stdout writer.  This writer is a stripped down file-like
# object that provides the basic writing methods.  When you write to this
# stream, it will be written to stdout only if user output is enabled.  All
# strings will also be logged at INFO level to any registered log files.
out = _log_manager.stdout_writer


# The configured stderr writer.  This writer is a stripped down file-like
# object that provides the basic writing methods.  When you write to this
# stream, it will be written to stderr only if user output is enabled.  All
# strings will also be logged at INFO level to any registered log files.
err = _log_manager.stderr_writer

# Status output writer. For things that are useful to know for someone watching
# a command run, but aren't normally scraped.
status = err


# Gets a logger object that logs only to a file and never to the console.
# You usually don't want to use this logger directly.  All normal logging will
# also go to files.  This logger specifically prevents the messages from going
# to the console under any verbosity setting.
file_only_logger = _log_manager.file_only_logger


def Print(*msg):
  """Writes the given message to the output stream, and adds a newline.

  This method has the same output behavior as the build in print method but
  respects the configured user output setting.

  Args:
    *msg: str, The messages to print.
  """
  out.Print(*msg)


def Reset():
  """Reinitialize the logging system.

  This clears all loggers registered in the logging module, and reinitializes
  it with the specific loggers we want for calliope.

  This will set the initial values for verbosity or user_output_enabled to their
  values saved in the properties.

  Since we are using the python logging module, and that is all statically
  initialized, this method does not actually turn off all the loggers.  If you
  hold references to loggers or writers after calling this method, it is
  possible they will continue to work, but their behavior might change when the
  logging framework is reinitialized.  This is useful mainly for clearing the
  loggers between tests so stubs can get reset.
  """
  _log_manager.Reset()


def SetVerbosity(verbosity):
  """Sets the active verbosity for the logger.

  Args:
    verbosity: int, A verbosity constant from the logging module that
      determines what level of logs will show in the console. If None, the
      value from properties or the default will be used.

  Returns:
    int, The current verbosity.
  """
  return _log_manager.SetVerbosity(verbosity)


def GetVerbosity():
  """Gets the current verbosity setting.

  Returns:
    int, The current verbosity.
  """
  return _log_manager.verbosity


def GetVerbosityName():
  """Gets the current verbosity setting as its named value.

  Returns:
    str, The current verbosity or None if the name is unknown.
  """
  current = GetVerbosity()
  for name, num in VALID_VERBOSITY_STRINGS.iteritems():
    if current == num:
      return name
  return None


def OrderedVerbosityNames():
  """Gets all the valid verbosity names from most verbose to least verbose."""
  return [name for name, _ in VERBOSITY_LEVELS]


def SetUserOutputEnabled(enabled):
  """Sets whether user output should go to the console.

  Args:
    enabled: bool, True to enable output, false to suppress.

  Returns:
    bool, The old value of enabled.
  """
  return _log_manager.SetUserOutputEnabled(enabled)


def IsUserOutputEnabled():
  """Gets whether user output is enabled or not.

  Returns:
    bool, True if user output is enabled, False otherwise.
  """
  return _log_manager.user_output_enabled


def AddFileLogging(logs_dir):
  """Adds a new logging file handler to the root logger.

  Args:
    logs_dir: str, The root directory to store logs in.
  """
  _log_manager.AddLogsDir(logs_dir=logs_dir)


def GetLogDir():
  """Gets the path to the currently in use log directory.

  Returns:
    str, The logging directory path.
  """
  log_file = _log_manager.current_log_file
  if not log_file:
    return None
  return os.path.dirname(log_file)


def GetLogFileName(suffix):
  """Returns a new log file name based on the currently active log file.

  Args:
    suffix: str, A suffix to add to the current log file name.

  Returns:
    str, The name of a log file, or None if file logging is not on.
  """
  log_file = _log_manager.current_log_file
  if not log_file:
    return None
  log_filename = os.path.basename(log_file)
  log_file_root_name = log_filename[:-len(LOG_FILE_EXTENSION)]
  return log_file_root_name + suffix


def CreatedResource(r):
  """Print a status message indicating that a resource was created."""
  status.write('Created [{r}].\n'.format(r=str(r)))


def DeletedResource(r):
  """Print a status message indicating that a resource was deleted."""
  status.write('Deleted [{r}].\n'.format(r=str(r)))


def UpdatedResource(r):
  """Print a status message indicating that a resource was updated."""
  status.write('Updated [{r}].\n'.format(r=str(r)))


# pylint: disable=invalid-name
# There are simple redirects to the logging module as a convenience.
getLogger = logging.getLogger
log = logging.log
debug = logging.debug
info = logging.info
warn = logging.warn
warning = logging.warning
error = logging.error
critical = logging.critical
fatal = logging.fatal
exception = logging.exception
