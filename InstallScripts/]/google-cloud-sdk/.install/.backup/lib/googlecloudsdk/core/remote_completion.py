# Copyright 2014 Google Inc. All Rights Reserved.
"""Remote resource completion and caching."""
import logging
import os
import threading
import time

import argcomplete

from googlecloudsdk.core import config
from googlecloudsdk.core import properties


class CompletionProgressTracker(object):
  """A context manager for telling the user about long-running completions."""

  SPIN_MARKS = [
      '|',
      '/',
      '-',
      '\\',
  ]

  def __init__(self, ofile, timeout=3.0, autotick=True):
    self._ticks = 0
    self._autotick = autotick
    self._done = False
    self._lock = threading.Lock()
    self.ofile = ofile
    self.timeout = timeout

  def __enter__(self):

    if self._autotick:
      def Ticker():
        time.sleep(.2)
        self.timeout -= .2
        while True:
          if self.timeout < 0:
            self.ofile.write('?\b')
            self.ofile.flush()
            os.kill(0, 15)
          time.sleep(.1)
          self.timeout -= .1
          if self.Tick():
            return
      threading.Thread(target=Ticker).start()

    return self

  def Tick(self):
    """Give a visual indication to the user that some progress has been made."""
    with self._lock:
      if not self._done:
        self._ticks += 1
        self.ofile.write(
            CompletionProgressTracker.SPIN_MARKS[
                self._ticks % len(CompletionProgressTracker.SPIN_MARKS)] + '\b')
        self.ofile.flush()
      return self._done

  def __exit__(self, unused_type=None, unused_value=True,
               unused_traceback=None):
    with self._lock:
      self.ofile.write(' \b')
      self._done = True


class RemoteCompletion(object):
  """Class to cache the names of remote resources."""

  CACHE_HITS = 0
  CACHE_TRIES = 0
  _TIMEOUTS = {  # Timeouts for resources in seconds
      'sql.instances': 600,
      'compute.instances': 600,
      'compute.regions': 3600*10,
      'compute.zones': 3600*10
  }
  ITEM_NAME_FUN = {
      'compute': lambda item: item['name'],
      'sql': lambda item: item.instance
  }

  def __init__(self):
    """Set the cache directory."""
    try:
      self.project = properties.VALUES.core.project.Get(required=True)
    except Exception:  # pylint:disable=broad-except
      self.project = 0
    self.cache_dir = config.Paths().completion_cache_dir

  def ResourceIsCached(self, resource):
    """Returns True for resources that can be cached.

    Args:
      resource: The resource as subcommand.resource.

    Returns:
      True when resource is cacheable.
    """
    if resource == 'sql.instances':
      return True
    if resource.startswith('compute.'):
      return True
    return False

  def CachePath(self, resource, zoneregion):
    """Creates a pathname for the resource.

    Args:
      resource: The resource as subcommand.resource.
      zoneregion: The zone or region name.

    Returns:
      Returns a pathname for the resource.
    """
    if self.project:
      path = os.path.join(self.cache_dir, resource, self.project)
    else:
      return 0
    if zoneregion:
      path = os.path.join(path, zoneregion)
    return path

  def GetFromCache(self, resource, zoneregion=None):
    """Return a list of names for the resource and zoneregion.

    Args:
      resource: The resource as subcommand.resource.
      zoneregion: The zone or region name or None.

    Returns:
      Returns a list of names if in the cache.
    """
    options = []
    RemoteCompletion.CACHE_TRIES += 1
    fpath = self.CachePath(resource, zoneregion)
    if not fpath:
      return None
    try:
      if os.path.getmtime(fpath) > time.time():
        with open(fpath, 'r') as f:
          line = f.read().rstrip('\n')
        options = line.split(' ')
        RemoteCompletion.CACHE_HITS += 1
        return options
    except Exception:  # pylint:disable=broad-except
      return None
    return None

  def StoreInCache(self, resource, options, zoneregion):
    """Return the list of names for the resource and zoneregion.

    Args:
      resource: The resource as subcommand.resource.
      options: A list of possible completions.
      zoneregion: The zone or region name, or None if no zone or region.

    Returns:
      None
    """
    path = self.CachePath(resource, zoneregion)
    if not path:
      return
    if not zoneregion and os.path.isdir(path):
      name = os.path.join(path, '_ALL_ZONES')
      try:
        os.remove(name)
      except OSError:
        pass
      os.rmdir(path)
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
      os.makedirs(dirname)
    if options:
      with open(path, 'w') as f:
        f.write(' '.join(options) + '\n')
    now = time.time()
    if options is None:
      timeout = 0
    else:
      timeout = RemoteCompletion._TIMEOUTS.get(resource, 300)
    os.utime(path, (now, now+timeout))

  @staticmethod
  def GetTickerStream():
    return argcomplete.debug_stream

  @staticmethod
  def GetCompleterForResource(resource, cli):
    """Returns a completer function for the give resource.

    Args:
      resource: The resource as subcommand.resource.
      cli: The calliope instance.

    Returns:
      A completer function for the specified resource.
    """

    def RemoteCompleter(parsed_args, **unused_kwargs):
      """Run list command on  resource to generates completion options."""
      options = []
      try:
        command = resource.split('.') + ['list']
        zoneregion = None
        if command[0] == 'compute':
          zoneregion = ''
        if hasattr(parsed_args, 'zone') and parsed_args.zone:
          zoneregion = parsed_args.zone
          command.append('--zone')
          command.append(zoneregion)
        if hasattr(parsed_args, 'region') and parsed_args.region:
          zoneregion = parsed_args.region
          command.append('--region')
          command.append(zoneregion)
        ccache = RemoteCompletion()
        if not ccache.project and hasattr(parsed_args, 'project'):
          ccache.project = parsed_args.project

        options = ccache.GetFromCache(resource, zoneregion)
        if options is None:
          properties.VALUES.core.user_output_enabled.Set(False)
          ofile = RemoteCompletion.GetTickerStream()
          with CompletionProgressTracker(ofile):
            items = list(cli().Execute(command, call_arg_complete=False))
          fun = RemoteCompletion.ITEM_NAME_FUN[command[0]]
          options = []
          allzones = False
          for item in items:
            if zoneregion == '':  # pylint:disable=g-explicit-bool-comparison
              if 'zone' in item or 'region' in item:
                zoneregion = '_ALL_ZONES'
                allzones = True
                zones = {}
              else:
                zoneregion = None
            options.append(fun(item))
            if allzones:
              if 'zone' in item:
                zone = item['zone']
              else:
                zone = item['region']
              if zone and zone in zones:
                zones[zone].append(fun(item))
              elif zone:
                zones[zone] = [fun(item)]
          if allzones:
            for zone in zones:
              ccache.StoreInCache(resource, zones[zone], zone)
          ccache.StoreInCache(resource, options, zoneregion)
      except Exception:  # pylint:disable=broad-except
        logging.error(resource + 'completion command failed', exc_info=True)
        return []
      return options
    return RemoteCompleter

