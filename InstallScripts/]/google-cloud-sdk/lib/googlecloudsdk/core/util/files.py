# Copyright 2013 Google Inc. All Rights Reserved.

"""Some general file utilities used that can be used by the Cloud SDK."""

import errno
import hashlib
import logging
import os
import shutil
import sys
import tempfile
import time


NUM_RETRIES = 10

# WindowsError only exists when running on Windows
try:
  # pylint: disable=invalid-name, We are not defining this name.
  WindowsError
except NameError:
  # pylint: disable=invalid-name, We are not defining this name.
  WindowsError = None


class Error(Exception):
  """Base exception for the file_utils module."""
  pass


def MakeDir(path, mode=0777):
  """Creates the given directory and its parents and does not fail if it exists.

  Args:
    path: str, The path of the directory to create.
    mode: int, The permissions to give the created directories. 0777 is the
        default mode for os.makedirs(), allowing reading, writing, and listing
        by all users on the machine.

  Raises:
    OSError: if the operation fails.
  """
  try:
    os.makedirs(path, mode=mode)
  except OSError as ex:
    if ex.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise


def _WaitForRetry(retries_left):
  """Sleeps for a period of time based on the retry count.

  Args:
    retries_left: int, The number of retries remaining.  Should be in the range
      of NUM_RETRIES - 1 to 0.
  """
  time_to_wait = .1 * (2 * (NUM_RETRIES - retries_left))
  logging.debug('Waiting for retry: [%s]', time_to_wait)
  time.sleep(time_to_wait)


RETRY_ERROR_CODES = [32, 145]


def _ShouldRetryOperation(func, exc_info):
  """Matches specific error types that should be retried.

  This will retry the following errors:
    WindowsError(32, 'The process cannot access the file because it is being '
      'used by another process'), When a file is in use.
    WindowsError(145, 'The directory is not empty'), When a directory cannot be
      deleted.

  Args:
    func: function, The function that failed.
    exc_info: sys.exc_info(), The current exception state.

  Returns:
    True if the error can be retried or false if we should just fail.
  """
  if not (func == os.remove or func == os.rmdir):
    return False
  if not WindowsError or exc_info[0] != WindowsError:
    return False
  e = exc_info[1]
  return e.winerror in RETRY_ERROR_CODES


def _RetryOperation(exc_info, func, args,
                    retry_test_function=lambda func, exc_info: True):
  """Attempts to retry the failed file operation.

  Args:
    exc_info: sys.exc_info(), The current exception state.
    func: function, The function that failed.
    args: (str, ...), The tuple of args that should be passed to func when
      retrying.
    retry_test_function: The function to call to determine if a retry should be
      attempted.  Takes the function that is being retried as well as the
      current exc_info.

  Returns:
    True if the operation eventually succeeded or False if it continued to fail
    for all retries.
  """
  retries_left = NUM_RETRIES
  while retries_left > 0 and retry_test_function(func, exc_info):
    logging.debug('Retrying file system operation: %s, %s, %s, retries_left=%s',
                  func, args, exc_info, retries_left)
    retries_left -= 1
    try:
      _WaitForRetry(retries_left)
      func(*args)
      return True
    # pylint: disable=bare-except, We look at the exception later.
    except:
      exc_info = sys.exc_info()
  return False


def _HandleRemoveError(func, failed_path, exc_info):
  """A fucntion to pass as the onerror arg to rmdir for handling errors.

  Args:
    func: function, The function that failed.
    failed_path: str, The path of the file the error occurred on.
    exc_info: sys.exc_info(), The current exception state.
  """
  logging.debug('Handling file system error: %s, %s, %s',
                func, failed_path, exc_info)

  # Don't remove the trailing comma in the passed arg tuple.  It indicates that
  # it is a tuple of 1, rather than a tuple of characters that will get expanded
  # by *args.
  if not _RetryOperation(exc_info, func, (failed_path,), _ShouldRetryOperation):
    # Always raise the original error.
    # raises is weird in that you can raise exc_info directly even though it's
    # a tuple.
    raise exc_info[0], exc_info[1], exc_info[2]


def RmTree(path):
  """Calls shutil.rmtree() with error handling to fix Windows problems.

  It also ensures that the top level directory deletion is actually reflected
  in the file system before this returns.

  Args:
    path: str, The path to remove.
  """
  shutil.rmtree(path, onerror=_HandleRemoveError)
  retries_left = NUM_RETRIES
  while os.path.isdir(path) and retries_left > 0:
    logging.debug('Waiting for directory to disappear: %s', path)
    retries_left -= 1
    _WaitForRetry(retries_left)


def _DestInSrc(src, dst):
  # Copied directly from shutil
  src = os.path.abspath(src)
  dst = os.path.abspath(dst)
  if not src.endswith(os.path.sep):
    src += os.path.sep
  if not dst.endswith(os.path.sep):
    dst += os.path.sep
  return dst.startswith(src)


def MoveDir(src, dst):
  """Recursively moves a directory to another location.

  This code is mostly copied from shutil.move(), but has been scoped down to
  specifically handle only directories.  The src must be a directory, and
  the dst must not exist.  It uses functions from this module to be resilient
  against spurious file system errors in Windows.  It will try to do an
  os.rename() of the directory.  If that fails, the tree will be copied to the
  new location and then deleted from the old location.

  Args:
    src: str, The directory path to move.
    dst: str, The path to move the directory to.

  Raises:
    Error: If the src or dst directories are not valid.
  """
  if not os.path.isdir(src):
    raise Error("Source path '{}' must be a directory".format(src))
  if os.path.exists(dst):
    raise Error("Destination path '{}' already exists".format(dst))
  if _DestInSrc(src, dst):
    raise Error("Cannot move a directory '{}' into itself '{}'."
                .format(src, dst))
  try:
    logging.debug('Attempting to move directory [%s] to [%s]', src, dst)
    try:
      os.rename(src, dst)
    except OSError:
      if not _RetryOperation(sys.exc_info(), os.rename, (src, dst)):
        raise
  except OSError as e:
    logging.debug('Directory rename failed.  Falling back to copy. [%s]', e)
    shutil.copytree(src, dst, symlinks=True)
    RmTree(src)


def FindDirectoryContaining(starting_dir_path, directory_entry_name):
  """Searches directories upwards until it finds one with the given contents.

  This can be used to find the directory above you that contains the given
  entry.  It is useful for things like finding the workspace root you are under
  that contains a configuration directory.

  Args:
    starting_dir_path: str, The path of the directory to start searching
      upwards from.
    directory_entry_name: str, The name of the directory that must be present
      in order to return the current directory.

  Returns:
    str, The full path to the directory above the starting dir that contains the
    given entry, or None if the root of the file system was hit without finding
    it.
  """
  prev_path = None
  path = os.path.realpath(starting_dir_path)
  while path != prev_path:
    search_dir = os.path.join(path, directory_entry_name)
    if os.path.isdir(search_dir):
      return path
    prev_path = path
    path, _ = os.path.split(path)
  return None


def SearchForExecutableOnPath(executable, path=None):
  """Tries to find all 'executable' in the directories listed in the PATH.

  This is mostly copied from distutils.spawn.find_executable() but with a
  few differences.  It does not check the current directory for the
  executable.  We only want to find things that are actually on the path, not
  based on what the CWD is.  It also returns a list of all matching
  executables.  If there are multiple versions of an executable on the path
  it will return all of them at once.

  Args:
    executable: The name of the executable to find
    path: A path to search.  If none, the system PATH will be used.

  Returns:
    A list of full paths to matching executables or an empty list if none
    are found.
  """
  if not path:
    path = os.getenv('PATH')
  paths = path.split(os.pathsep)

  matching = []
  for p in paths:
    f = os.path.join(p, executable)
    if os.path.isfile(f):
      matching.append(f)

  return matching


def FindExecutableOnPath(executable, path=None, pathext=None):
  """Searches for 'executable' in the directories listed in 'path'.

  If 'executable' contains any directory components then 'path' is ignored.  If
  'pathext' is specified and 'executable' does not have any of those extensions
  then 'executable'+'extension' is checked.

  Args:
    executable: The name of the executable to find.
    path: A list of directories to search separated by 'os.pathsep'.  If none
      then the system PATH is used.
    pathext: A list of file name extensions to use separated by 'os.pathsep'.
      If none then the platform specific system PATHEXT is used.

  Returns:
    The path of 'executable' (+ 'extension' if necessary) if found and
      executable, None if not found.
  """

  head, tail = os.path.split(executable)
  if head:
    path = '.'
  elif path is None:
    path = os.environ.get('PATH')
  if not path:
    return None
  paths = path.split(os.pathsep)
  if pathext is None:
    if sys.platform == 'win32' or os.name == 'os2':
      pathext = os.environ.get('PATHEXT')
    if pathext is None:
      pathext = ''
  extensions = pathext.split(os.pathsep)
  if extensions:
    _, extension = os.path.splitext(tail)
    for ext in extensions:
      if extension == ext:
        extensions = []
  for directory in paths:
    head = os.path.join(directory, executable)
    for tail in [''] + extensions:
      full = head + tail
      if os.path.isfile(full) and os.access(full, os.X_OK):
        return full
  return None


def HasWriteAccessInDir(directory):
  """Determines if the current user is able to modify the contents of the dir.

  Args:
    directory: str, The full path of the directory to check.

  Raises:
    ValueError: If the given directory path is not a valid directory.

  Returns:
    True if the current user has missing write and execute permissions.
  """
  if not os.path.isdir(directory):
    raise ValueError(
        'The given path [{path}] is not a directory.'.format(path=directory))
  # Appending . tests search permissions, especially on windows, by forcing
  # 'directory' to be treated as a directory
  path = os.path.join(directory, '.')
  if not os.access(path, os.X_OK) or not os.access(path, os.W_OK):
    # We can believe os.access() indicating no access.
    return False

  # At this point the only platform and filesystem independent method is to
  # attempt to create or delete a file in the directory.
  #
  # Why? os.accesss() and os.stat() use the underlying C library on Windows,
  # which doesn't check the correct user and group permissions and almost always
  # results in false positive writability tests.

  path = os.path.join(directory,
                      '.HasWriteAccessInDir{pid}'.format(pid=os.getpid()))
  # while True: should work here, but we limit the retries just in case.
  for _ in range(10):

    try:
      fd = os.open(path, os.O_RDWR | os.O_CREAT, 0666)
      os.close(fd)
    except OSError as e:
      if e.errno == errno.EACCES:
        # No write access.
        return False
      if e.errno in [errno.ENOTDIR, errno.ENOENT]:
        # The directory has been removed or replaced by a file.
        raise ValueError('The given path [{path}] is not a directory.'.format(
            path=directory))
      raise

    try:
      os.remove(path)
      # Write access.
      return True
    except OSError as e:
      if e.errno == errno.EACCES:
        # No write access.
        return False
      # os.remove() could fail with ENOENT if we're in a race with another
      # process/thread (which just succeeded) or if the directory has been
      # removed.
      if e.errno != errno.ENOENT:
        raise

  return False


class TemporaryDirectory(object):
  """A class to easily create and dispose of temporary directories.

  Securely creates a directory for temporary use.  This class can be used with
  a context manager (the with statement) to ensure cleanup in exceptional
  situations.
  """

  def __init__(self):
    self.__temp_dir = tempfile.mkdtemp()

  @property
  def path(self):
    return self.__temp_dir

  def __enter__(self):
    return self.path

  def __exit__(self, *exceptional):
    self.Close()
    # always return False so any exceptions will be re-raised
    return False

  def Close(self):
    if self.path:
      RmTree(self.path)
      self.__temp_dir = None
      return True
    return False


class Checksum(object):
  """Consistently handles calculating checksums across the Cloud SDK."""

  def __init__(self):
    """Creates a new Checksum."""
    self.__hash = hashlib.sha1()
    self.__files = set()

  def AddContents(self, contents):
    """Adds the given string contents to the checksum.

    Args:
      contents: str, The contents to add.

    Returns:
      self, For method chaining.
    """
    self.__hash.update(contents)
    return self

  def AddFileContents(self, file_path):
    """Adds the contents of the given file to the checksum.

    Args:
      file_path: str, The file path of the contents to add.

    Returns:
      self, For method chaining.
    """
    with open(file_path, 'rb') as fp:
      for chunk in iter(lambda: fp.read(4096), ''):
        self.__hash.update(chunk)
    return self

  def AddDirectory(self, dir_path):
    """Adds all files under the given directory to the checksum.

    This adds both the contents of the files as well as their names and
    locations to the checksum.  If the checksums of two directories are equal
    this means they have exactly the same files, and contents.

    Args:
      dir_path: str, The directory path to add all files from.

    Returns:
      self, For method chaining.
    """
    for root, dirs, files in os.walk(dir_path):
      dirs.sort(key=os.path.normcase)
      files.sort(key=os.path.normcase)
      for d in dirs:
        path = os.path.join(root, d)
        # We don't traverse directory links, but add the fact that it was found
        # in the tree.
        if os.path.islink(path):
          relpath = os.path.relpath(path, dir_path)
          self.__files.add(relpath)
          self.AddContents(relpath)
          self.AddContents(os.readlink(path))
      for f in files:
        path = os.path.join(root, f)
        relpath = os.path.relpath(path, dir_path)
        self.__files.add(relpath)
        self.AddContents(relpath)
        if os.path.islink(path):
          self.AddContents(os.readlink(path))
        else:
          self.AddFileContents(path)
    return self

  def HexDigest(self):
    """Gets the hex digest for all content added to this checksum.

    Returns:
      str, The checksum digest as a hex string.
    """
    return self.__hash.hexdigest()

  def Files(self):
    """Gets the list of all files that were discovered when adding a directory.

    Returns:
      {str}, The relative paths of all files that were found when traversing the
      directory tree.
    """
    return self.__files


def OpenForWritingPrivate(path):
  """Open a file for writing, with the right permissions for user-private files.

  Args:
    path: str, The full path to the file.

  Returns:
    A file context manager.
  """

  parent_dir_path, _ = os.path.split(path)
  full_parent_dir_path = os.path.realpath(os.path.expanduser(parent_dir_path))
  MakeDir(full_parent_dir_path, mode=0700)

  flags = os.O_RDWR | os.O_CREAT | os.O_TRUNC
  # Accommodate Windows; stolen from python2.6/tempfile.py.
  if hasattr(os, 'O_NOINHERIT'):
    flags |= os.O_NOINHERIT

  fd = os.open(path, flags, 0600)
  return os.fdopen(fd, 'w')


class Context(object):
  """Wrap a file in a context.

  Some libraries return file contexts in 2.7, but not in 2.6. Wrapping the
  returned file in this class makes it so our code works for either version.
  """

  def __init__(self, f):
    self.__f = f

  def __enter__(self):
    return self.__f

  def __exit__(self, typ, value, traceback):
    self.__f.close()


class ChDir(object):
  """Do some things from a certain directory, and reset the directory afterward.
  """

  def __init__(self, directory):
    self.__dir = directory

  def __enter__(self):
    self.__original_dir = os.getcwd()
    os.chdir(self.__dir)
    return self.__dir

  def __exit__(self, typ, value, traceback):
    os.chdir(self.__original_dir)
