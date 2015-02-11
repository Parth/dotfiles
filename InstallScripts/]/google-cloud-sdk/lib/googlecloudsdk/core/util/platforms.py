# Copyright 2013 Google Inc. All Rights Reserved.

"""Utilities for determining the current platform and architecture."""

import os
import platform
import sys


class Error(Exception):
  """Base class for exceptions in the platforms moudle."""
  pass


class InvalidEnumValue(Error):
  """Exception for when a string could not be parsed to a valid enum value."""

  def __init__(self, given, enum_type, options):
    """Constructs a new exception.

    Args:
      given: str, The given string that could not be parsed.
      enum_type: str, The human readable name of the enum you were trying to
        parse.
      options: list(str), The valid values for this enum.
    """
    super(InvalidEnumValue, self).__init__(
        'Could not parse [{}] into a valid {}.  Valid values are [{}]'
        .format(given, enum_type, ', '.join(options)))


class OperatingSystem(object):
  """An enum representing the operating system you are running on."""

  class _OS(object):

    # pylint: disable=redefined-builtin
    def __init__(self, id, name):
      self.id = id
      self.name = name

  WINDOWS = _OS('WINDOWS', 'Windows')
  MACOSX = _OS('MACOSX', 'Mac OS X')
  LINUX = _OS('LINUX', 'Linux')
  CYGWIN = _OS('CYGWIN', 'Cygwin')
  MSYS = _OS('MSYS', 'Msys')
  _ALL = [WINDOWS, MACOSX, LINUX, CYGWIN, MSYS]

  @staticmethod
  def AllValues():
    """Gets all possible enum values.

    Returns:
      list, All the enum values.
    """
    return list(OperatingSystem._ALL)

  @staticmethod
  def FromId(os_id):
    """Gets the enum corresponding to the given operating system id.

    Args:
      os_id: str, The operating system id to parse

    Raises:
      InvalidEnumValue: If the given value cannot be parsed.

    Returns:
      OperatingSystemTuple, One of the OperatingSystem constants or None if the
      input is None.
    """
    if not os_id:
      return None
    for operating_system in OperatingSystem._ALL:
      if operating_system.id == os_id:
        return operating_system
    raise InvalidEnumValue(os_id, 'Operating System',
                           [value.id for value in OperatingSystem._ALL])

  @staticmethod
  def Current():
    """Determines the current operating system.

    Returns:
      OperatingSystemTuple, One of the OperatingSystem constants or None if it
      cannot be determined.
    """
    if os.name == 'nt':
      return OperatingSystem.WINDOWS
    elif 'linux' in sys.platform:
      return OperatingSystem.LINUX
    elif 'darwin' in sys.platform:
      return OperatingSystem.MACOSX
    elif 'cygwin' in sys.platform:
      return OperatingSystem.CYGWIN
    # TODO(user): More reliable handling of OS types
    # TODO(user): What happens when we use jython, does it actually use the
    # 'java' os name?
    return None


class Architecture(object):
  """An enum representing the system architecture you are running on."""

  class _ARCH(object):

    # pylint: disable=redefined-builtin
    def __init__(self, id, name):
      self.id = id
      self.name = name

  x86 = _ARCH('x86', 'x86')
  x86_64 = _ARCH('x86_64', 'x86_64')
  ppc = _ARCH('PPC', 'PPC')
  _ALL = [x86, x86_64, ppc]
  _MACHINE_TO_ARCHITECTURE = {'AMD64': x86_64, 'x86_64': x86_64,
                              'i386': x86, 'i686': x86, 'x86': x86,
                              'Power Macintosh': ppc}

  @staticmethod
  def AllValues():
    """Gets all possible enum values.

    Returns:
      list, All the enum values.
    """
    return list(Architecture._ALL)

  @staticmethod
  def FromId(architecture_id):
    """Gets the enum corresponding to the given architecture id.

    Args:
      architecture_id: str, The architecture id to parse

    Raises:
      InvalidEnumValue: If the given value cannot be parsed.

    Returns:
      ArchitectureTuple, One of the Architecture constants or None if the input
      is None.
    """
    if not architecture_id:
      return None
    for arch in Architecture._ALL:
      if arch.id == architecture_id:
        return arch
    raise InvalidEnumValue(architecture_id, 'Architecture',
                           [value.id for value in Architecture._ALL])

  @staticmethod
  def Current():
    """Determines the current system architecture.

    Returns:
      ArchitectureTuple, One of the Architecture constants or None if it cannot
      be determined.
    """
    return Architecture._MACHINE_TO_ARCHITECTURE.get(platform.machine())


class Platform(object):
  """Holds an operating system and architecture."""

  def __init__(self, operating_system, architecture):
    """Constructs a new platform.

    Args:
      operating_system: OperatingSystem, The OS
      architecture: Architecture, The machine architecture.
    """
    self.operating_system = operating_system
    self.architecture = architecture

  @staticmethod
  def Current(os_override=None, arch_override=None):
    """Determines the current platform you are running on.

    Args:
      os_override: OperatingSystem, A value to use instead of the current.
      arch_override: Architecture, A value to use instead of the current.

    Returns:
      Platform, The platform tuple of operating system and architecture.  Either
      can be None if it could not be determined.
    """
    return Platform(
        os_override if os_override else OperatingSystem.Current(),
        arch_override if arch_override else Architecture.Current())

  def UserAgentFragment(self):
    """Generates the fragment of the User-Agent that represents the OS.

    Examples:
      (Linux 3.2.5-gg1236)
      (Windows NT 6.1.7601)
      (Macintosh; PPC Mac OS X 12.4.0)
      (Macintosh; Intel Mac OS X 12.4.0)

    Returns:
      str, The fragment of the User-Agent string.
    """
    # Below, there are examples of the value of platform.uname() per platform.
    # platform.release() is uname[2], platform.version() is uname[3].
    if self.operating_system == OperatingSystem.LINUX:
      # ('Linux', '<hostname goes here>', '3.2.5-gg1236',
      # '#1 SMP Tue May 21 02:35:06 PDT 2013', 'x86_64', 'x86_64')
      return '({name} {version})'.format(
          name=self.operating_system.name, version=platform.release())
    elif self.operating_system == OperatingSystem.WINDOWS:
      # ('Windows', '<hostname goes here>', '7', '6.1.7601', 'AMD64',
      # 'Intel64 Family 6 Model 45 Stepping 7, GenuineIntel')
      return '({name} NT {version})'.format(
          name=self.operating_system.name, version=platform.version())
    elif self.operating_system == OperatingSystem.MACOSX:
      # ('Darwin', '<hostname goes here>', '12.4.0',
      # 'Darwin Kernel Version 12.4.0: Wed May  1 17:57:12 PDT 2013;
      # root:xnu-2050.24.15~1/RELEASE_X86_64', 'x86_64', 'i386')
      format_string = '(Macintosh; {name} Mac OS X {version})'
      arch_string = (self.architecture.name
                     if self.architecture == Architecture.ppc else 'Intel')
      return format_string.format(
          name=arch_string, version=platform.release())
    else:
      return '()'

  def AsycPopenArgs(self):
    """Returns the args for spawning an async process using Popen on this OS.

    Returns:
      {str:}, The args for spawning an async process using Popen on this OS.
    """
    args = {}
    if self.operating_system == OperatingSystem.WINDOWS:
      args['close_fds'] = True
      detached_process = 0x00000008
      args['creationflags'] = detached_process
    return args

  def IsSupported(self):
    """Ensure that we support the given platform.

    This will print an error message if not supported.

    Returns:
      bool, True if the platform is valid, False otherwise.
    """
    if (self.operating_system == OperatingSystem.CYGWIN and
        self.architecture == Architecture.x86_64):
      sys.stderr.write('ERROR: Cygwin 64 bit is not supported by the Google '
                       'Cloud SDK.  Please use a 32 bit version of Cygwin.')
      return False
    return True


class PythonVersion(object):
  """Class to validate the Python version we are using."""
  MIN_REQUIRED_VERSION = (2, 6)

  def __init__(self):
    if hasattr(sys, 'version_info'):
      self.version = sys.version_info[:2]
    else:
      self.version = None

  def __MinVersionString(self):
    return '%s.%s' % (str(PythonVersion.MIN_REQUIRED_VERSION[0]),
                      str(PythonVersion.MIN_REQUIRED_VERSION[1]))

  def __PrintEnvVarMessage(self):
    """Prints how to set CLOUDSDK_PYTHON."""
    sys.stderr.write('\nIf you have a compatible Python interpreter installed, '
                     'you can use it by setting the CLOUDSDK_PYTHON '
                     'environment variable to point to it.\n')

  def IsSupported(self):
    """Ensure that the Python version we are using is compatible.

    This will print an error message if not supported.

    Returns:
      bool, True if the version is valid, False otherwise.
    """
    if not self.version:
      sys.stderr.write('ERROR: Your current version of Python is not supported '
                       'by the Google Cloud SDK.  Please upgrade to Python '
                       '%s or greater.\n' % (self.__MinVersionString()))
      self.__PrintEnvVarMessage()
      return False
    if self.version[0] == 3:
      sys.stderr.write('ERROR: Python 3 is not supported by the Google Cloud '
                       'SDK.  Please use a Python 2.x version that is %s or '
                       'greater.\n' % (self.__MinVersionString()))
      self.__PrintEnvVarMessage()
      return False
    if self.version < PythonVersion.MIN_REQUIRED_VERSION:
      sys.stderr.write('ERROR: Python %s.%s is not supported by the Google '
                       'Cloud SDK. Please upgrade to version %s or greater.\n'
                       % (str(self.version[0]), str(self.version[1]),
                          self.__MinVersionString()))
      self.__PrintEnvVarMessage()
      return False
    return True
