# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Cache of previously used flag values."""

from __future__ import with_statement



import copy
import os

import gflags as flags
from gcutil_lib import gcutil_logging

FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER

flags.DEFINE_bool(
    'cache_flag_values',
    False,
    'If true, cache all specified flag values in the file specified '
    'by the "cached_flags_file" flag.')
flags.DEFINE_string(
    'cached_flags_file',
    '.gcutil.flags',
    'File storing a cache of gcutil flag values. If the name does not '
    'contain a path separator it will be searched in the current working '
    'directory and up to "/", as well as the user\'s home directory. '
    'The first matching file will be used and no merging is done upstream. '
    'Use the "cache_flag_values" flag to persist the current flags.')


class FlagsCache(object):
  """File based cache of values for flags with user-specific defaults."""

  def __init__(self, cache_file_name=None, open_function=open, os_module=os):
    """Constructor.

    Args:
      cache_file_name: (str) optional path of the flags cache file (default
        is FLAGS.cached_flags_file).
      open_function: (function) used to open a file (overriden in tests).
      os_module: (module) used to perform OS operations (overriden in testsa).
    """
    self._open = open_function
    self._os = os_module
    self.cache_file_path = FlagsCache._FindFlagsCacheFile(
        cache_file_name or FLAGS.cached_flags_file, self._os)
    if self._os.path.exists(self.cache_file_path):
      LOGGER.debug('Found flag cache file: %s', self.cache_file_path)
      with self._open(self.cache_file_path) as cache_file:
        self.cache_string = cache_file.read()
    else:
      self.cache_string = ''

    self._serialized_flags = None

  @staticmethod
  def _FindFlagsCacheFile(name, os_module):
    """Returns the full path to the flags cache file.

    If the name contains a file separator or a user expander ('~'), then
    its full expanded path is returned.  Otherwise name is searched in
    the current working directory and recursively up, as well as in the
    user's home directory.  If an existing flags cache file cannot be found,
    then the full path to the config file in the user's home directory is
    returned so that it can be optionally created.

    Args:
      name: (string) the name of the file to search.
      os_module: (module) used to perform OS operations.
    Returns:
      (string) the path to an existing or expected cache flag file, or the
        empty string if name is None or empty.
    """
    if not name:
      return ''

    name = os_module.path.expanduser(name)

    if os_module.path.isdir(name):
      gcutil_flags = '.gcutil.flags'
      return os_module.path.join(name, gcutil_flags)
    elif os_module.path.dirname(name):
      # name contains a path separator.
      return os_module.path.realpath(name)

    # Search for the flags cache file up the directory path.
    directory = os_module.path.realpath(os_module.getcwd())
    while directory:
      filename = os_module.path.join(directory, name)
      if os_module.path.exists(filename):
        return filename
      parent = os_module.path.dirname(directory)
      if parent == directory:
        directory = None
      else:
        directory = parent

    # Use the flags cache file in the home directory.
    return os_module.path.realpath(os_module.path.expanduser(
        os_module.path.join('~', name)))

  @staticmethod
  def _GetCacheableFlagValues(flag_values):
    """Get the subset of flags that are appropriate to cache.

    All non-duplicate flags excluding --cache_flag_values and
    --cached_flags_file are eligible for caching.

    Args:
      flag_values: The superset FlagValues object.
    Returns:
      A subset FlagValues object that contains only the cacheable flags.
    """
    cacheable_flag_values = flags.FlagValues()
    for name, flag in flag_values.FlagDict().iteritems():
      # We only process the flag if seen by its full name (not short_name).
      if (name == flag.name and
          not name in ['cache_flag_values', 'cached_flags_file'] and
          not name in cacheable_flag_values and
          not flag.short_name in cacheable_flag_values):
        cacheable_flag_values[name] = flag

    return cacheable_flag_values

  @staticmethod
  def _GetCachedFlagValues(flag_values, cache_string):
    """Get the values for cacheable flags from the given cache string.

    Any flags in the parsed_flags argument will be omitted regardless of
    whether or not they are in the cache_string. This allows cached and
    parsed flags to be combined without conflict.

    Args:
      flag_values: A FlagValues instance defining the cacheable flags.
      cache_string: The contents of the cache as a newline delimited string.
    Returns:
      A FlagValues instance containing the flags present in the cache.
    """
    # We don't want to inadvertantly overwrite the parsed members of the
    # cacheable_flags, so we make a deep copy of it before appending.
    flag_values_copy = copy.deepcopy(flag_values)

    # Clear flags to load cache into clean state.
    for _, flag in flag_values_copy.FlagDict().iteritems():
      flag.present = 0
      flag.value = None

    cached_flag_values = flags.FlagValues()
    cached_flag_values.AppendFlagValues(flag_values_copy)
    undefok = []
    cache_entries = cache_string.split('\n')
    while cache_entries:
      try:
        argv = (['dummy_command', '--undefok=\'%s\'' % ','.join(undefok)] +
                cache_entries)
        cache_entries = cached_flag_values(argv)[2:]
      except flags.UnrecognizedFlagError, err:
        undefok.append(err.flagname)
    return cached_flag_values

  @staticmethod
  def _UnifyProjectFlags(flags, warn=False):
    """Unifies --project and --project_id flags in the flag value set.

    Args:
      flags: A FlagValues instance with the flags to unify.
      warn: If True, log warning if project_id is encountered.
    """
    if 'project_id' in flags and 'project' in flags:
      project_id = flags['project_id']
      project = flags['project']
      if project_id.present:
        if not project.present:
          if warn:
            LOGGER.warning('--project_id is deprecated, please use --project')
          project.present = project_id.present
          project.value = project_id.value
        elif warn:
          LOGGER.warning('--project_id and --project provided. '
                         '--project_id is deprecated, using value of '
                         '--project.')
        project_id.present = 0
        project_id.value = None

  @staticmethod
  def _ApplyCachedFlags(cacheable, cached):
    """Applies cached values to the flags in cacheable flag set.

    Only flags that are not themselves present are updated with the
    cached value.  Returns flags whose value is present, either by
    user specifying them at command line (cacheable) or by having been
    loaded from cache (cached).

    Args:
      cacheable: flags whose value can be cached (and whose values will be
          updated from cache if value not present)
      cache: flags loaded from the cache.

    Returns:
      FlagValues object which contains all present flags
    """
    canonical = flags.FlagValues()
    for name, flag in cacheable.FlagDict().iteritems():
      if flag.name == name:
        if not flag.present:
          cached_flag = cached[name]
          if cached_flag.present:
            LOGGER.debug('Flag override from cache file: %s -> %s',
                         repr(name), repr(cached_flag.value))
            flag.present = cached_flag.present
            flag.value = cached_flag.value

        if flag.present:
          canonical[name] = flag
    return canonical

  def UpdateCacheFile(self, update_cache=None):
    """Updates the flags cache file.

    This method assumes that SynchronizeFlags() has been called. If
    the assumption is violated, this method will produce a DEBUG log
    message and return.

    Args:
      update_cache: If True, updates the cache file. This is for testing.
    """
    if self._serialized_flags is None:
      LOGGER.debug('Flags cache cannot be updated before synchronizing flags.')
      return

    if update_cache or FLAGS.cache_flag_values:
      with self._open(self.cache_file_path, 'w') as cache_file:
        cache_file.write(self._serialized_flags)

  def SynchronizeFlags(self, flag_values=None):
    """Synchronize the given FlagValues instance with this cache.

    This updates the FlagValues instance with values for any unparsed flags if
    they have an entry in the cache.

    Args:
      flag_values: The FlagValues instance to synchronized. If not specified,
          then the global FlagValues instance is used.
    Returns:
      The synchronized FlagValues instance.
    """
    if not flag_values:
      flag_values = FLAGS
    # update_cache will be set to a boolean value, so we have to explicitly
    # check if it is None rather than relying on the implicit false behavior.

    cacheable = FlagsCache._GetCacheableFlagValues(flag_values)
    cached = FlagsCache._GetCachedFlagValues(cacheable, self.cache_string)

    FlagsCache._UnifyProjectFlags(cacheable, True)
    FlagsCache._UnifyProjectFlags(cached)

    canonical = FlagsCache._ApplyCachedFlags(cacheable, cached)
    self._serialized_flags = canonical.FlagsIntoString()
    return flag_values
