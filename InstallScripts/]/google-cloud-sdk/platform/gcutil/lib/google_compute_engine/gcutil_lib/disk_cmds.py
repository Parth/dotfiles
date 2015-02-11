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

"""Commands for interacting with Google Compute Engine persistent disks."""




from google.apputils import app
from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base
from gcutil_lib import gcutil_logging
from gcutil_lib import version

FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER
DEFAULT_DISK_SIZE_GB = {'pd-standard': 500, 'pd-ssd': 100}
PERFORMANCE_WARNING_SIZE_GB = {'pd-standard': 200, 'pd-ssd': 10}


class DiskCommand(command_base.GoogleComputeCommand):
  """Base command for working with the disks collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'zone', 'status', 'disk-type', 'size-gb'],
      field_mappings=(
          ('name', 'name'),
          ('description', 'description'),
          ('zone', 'zone'),
          ('status', 'status'),
          ('source-snapshot', 'sourceSnapshot'),
          ('disk-type', 'type'),
          ('size-gb', 'sizeGb')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('zone', 'zone'),
          ('status', 'status'),
          ('source-snapshot', 'sourceSnapshot'),
          ('source-image', 'sourceImage'),
          ('source-image-id', 'sourceImageId'),
          ('disk-type', 'type'),
          ('size-gb', 'sizeGb')),
      sort_by='name')

  resource_collection_name = 'disks'

  def __init__(self, name, flag_values):
    super(DiskCommand, self).__init__(name, flag_values)

    flags.DEFINE_string('zone',
                        None,
                        'The zone for this request.',
                        flag_values=flag_values)

  def _AutoDetectZone(self):
    """Causes this command to auto detect zone."""
    def _GetZoneContext(unused_object_type, context):
      return self.GetZoneForResource(
          self.api.disks, context['disk'], context['project'])

    self._context_parser.context_prompt_fxns['zone'] = _GetZoneContext

  def _PromptForZoneOnlyOnce(self):
    """Instruct this command to only prompt for the zone once."""
    def _GetZoneContext(unused_object_type, unused_context):
      if not self._flags.zone:
        self._flags.zone = self._presenter.PromptForZone(self.api.zones)['name']

      return self.DenormalizeResourceName(self._flags.zone)

    self._context_parser.context_prompt_fxns['zone'] = _GetZoneContext

  def _PrepareRequestArgs(self, disk_name, **other_args):
    """Gets the dictionary of API method keyword arguments.

    Args:
      disk_name: The name of the disk.
      **other_args: Keyword arguments that should be included in the request.

    Returns:
      Dictionary of keyword arguments that should be passed in the API call,
      includes all keyword arguments passed in 'other_args' plus
      common keys such as the name of the resource and the project.
    """
    disk_context = self._context_parser.ParseContextOrPrompt('disks', disk_name)

    kwargs = {
        'project': disk_context['project'],
        'disk': disk_context['disk'],
        'zone': disk_context['zone']
    }

    for key, value in other_args.items():
      kwargs[key] = value

    return kwargs


class AddDisk(DiskCommand):
  """Create new persistent disks.

  Specify multiple disks as multiple arguments. Multiple disks will be
  created in parallel.
  """

  positional_args = '<disk-name-1> ... <disk-name-n>'
  status_field = 'status'
  _TERMINAL_STATUS = ['READY', 'FAILED']

  def __init__(self, name, flag_values):
    super(AddDisk, self).__init__(name, flag_values)

    flags.DEFINE_string('description',
                        '',
                        'An optional description for this disk.',
                        flag_values=flag_values)
    flags.DEFINE_string('disk_type',
                        'pd-standard',
                        'Specifies the disk type used to create the disk. '
                        'For example, \'--disk_type=pd-standard\'. '
                        'To get a list of avaiable disk types, run '
                        '\'gcutil listdisktypes\'.',
                        flag_values=flag_values)
    flags.DEFINE_integer('size_gb',
                         None,
                         'Sets the size of this disk, in GB. The default '
                         'size is %s GB. If source_snapshot is also specified, '
                         'This value must be greater than or equal to the size '
                         'of the disk from which the source_snapshot was '
                         'created.'
                         % DEFAULT_DISK_SIZE_GB[flag_values['disk_type'].value],
                         flag_values=flag_values)
    flags.DEFINE_string('source_snapshot',
                        None,
                        'Specifies the source snapshot for this disk. If you '
                        'set this option, you cannot specify a source_image. ',
                        flag_values=flag_values)
    flags.DEFINE_string('source_image',
                        None,
                        'Specifies a source image for this disk, making this a '
                        'root persistent disk. If you set this option, you '
                        'cannot specify a source_snapshot. ',
                        flag_values=flag_values)
    flags.DEFINE_boolean('wait_until_complete',
                         False,
                         'Specifies that gcutil should wait until the disk '
                         'is successfully created before it returns.',
                         flag_values=flag_values)

  def Handle(self, *disk_names):
    """Add the specified disks.

    Args:
      *disk_names: The names of the disks to add.

    Returns:
      A tuple of (results, exceptions).

    Raises:
      CommandError: If the command is unsupported in this API version.
      UsageError: If no disk names are specified.
    """
    if not disk_names:
      raise app.UsageError('Please specify at least one disk name.')

    if self._flags.source_image and self._flags.source_snapshot:
      raise app.UsageError('You must specify either a source_image or a'
                           'source_snapshot but not both.')

    perf_min = PERFORMANCE_WARNING_SIZE_GB[self._flags.disk_type]
    if (not self._flags.source_image and self._flags.size_gb and
        self._flags.size_gb < perf_min):
      LOGGER.warn(('You have selected a volume size of under %s GB. '
                   'This may result in reduced performance. '
                   'For sizing and performance guidelines, see '
                   'https://developers.google.com/compute/docs/disks'
                   '#pdperformance.')
                  % PERFORMANCE_WARNING_SIZE_GB[self._flags.disk_type])

    self._PromptForZoneOnlyOnce()

    kind = self._GetResourceApiKind('disk')

    source_image = None
    if self._flags.source_image:
      source_image = self._context_parser.NormalizeOrPrompt(
          'images', command_base.ResolveImageTrackOrImage(
              self.api.images, self._flags.project, self._flags.source_image,
              lambda image: self._presenter.PresentElement(image['selfLink'])))

    source_snapshot = None
    if self._flags.source_snapshot:
      source_snapshot = self._context_parser.NormalizeOrPrompt(
          'snapshots', self._flags.source_snapshot)

    requests = []
    for name in disk_names:
      disk_context = self._context_parser.ParseContextOrPrompt('disks', name)

      disk = {
          'kind': kind,
          'name': disk_context['disk'],
          'description': self._flags.description,
      }

      kwargs = {
          'zone': disk_context['zone']
      }

      if source_snapshot is not None:
        disk['sourceSnapshot'] = source_snapshot
        if self._flags.size_gb:
          disk['sizeGb'] = self._flags.size_gb
      elif source_image is not None:
        kwargs['sourceImage'] = source_image
        if self._flags.size_gb:
          disk['sizeGb'] = self._flags.size_gb
      else:
        disk_type_default = str(DEFAULT_DISK_SIZE_GB[self._flags.disk_type])
        disk['sizeGb'] = (self._flags.size_gb or disk_type_default)

      if self.api.version >= version.get('v1') and self._flags.disk_type:
        disk['type'] = self._context_parser.NormalizeOrPrompt(
            'diskTypes', self._flags.disk_type)
      requests.append(self.api.disks.insert(project=disk_context['project'],
                                            body=disk, **kwargs))

    wait_for_operations = (
        self._flags.wait_until_complete or self._flags.synchronous_mode)

    (results, exceptions) = self.ExecuteRequests(
        requests, wait_for_operations=wait_for_operations)

    if self._flags.wait_until_complete:
      awaiting = (result for result in results
                  if result['kind'] == 'compute#disk')
      results = []
      for result in awaiting:
        if 'error' not in result:
          result = self._WaitUntilDiskIsComplete(result)
        results.append(result)

    list_type = 'diskList' if self._flags.synchronous_mode else 'operationList'
    return (self.MakeListResult(results, list_type), exceptions)

  def _InternalGetDisk(self, disk_name):
    """A simple implementation of getting current disk state.

    Args:
      disk_name: the name of the disk to get.

    Returns:
      Json containing full disk information.
    """
    disk_request = self.api.disks.get(**self._PrepareRequestArgs(disk_name))
    return disk_request.execute()

  def _WaitUntilDiskIsComplete(self, result):
    """Waits for the disk to complete.

    Periodically polls the server for current disk status. Exits if the
    status of the disk is READY or FAILED or the maximum waiting timeout
    has been reached. In both cases returns the last known disk details.

    Args:
      result: the current state of the disk.

    Returns:
      Json containing full disk information.
    """
    current_status = result[self.status_field]
    disk_name = result['selfLink']
    start_time = self._timer.time()
    LOGGER.info('Will wait for restore for: %d seconds.',
                self._flags.max_wait_time)
    while (self._timer.time() - start_time < self._flags.max_wait_time and
           current_status not in self._TERMINAL_STATUS):
      LOGGER.info(
          'Waiting for disk. Current status: %s. Sleeping for %ss.',
          current_status, self._flags.sleep_between_polls)
      self._timer.sleep(self._flags.sleep_between_polls)
      result = self._InternalGetDisk(disk_name)
      current_status = result[self.status_field]
    if current_status not in self._TERMINAL_STATUS:
      LOGGER.warn('Timeout reached. Disk %s has not yet been restored.',
                  disk_name)
    return result


class GetDisk(DiskCommand):
  """Get a machine disk."""

  positional_args = '<disk-name>'

  def __init__(self, name, flag_values):
    super(GetDisk, self).__init__(name, flag_values)

  def Handle(self, disk_name):
    """Get the specified disk.

    Args:
      disk_name: The name of the disk to get

    Returns:
      The result of getting the disk.
    """
    self._AutoDetectZone()

    disk_request = self.api.disks.get(**self._PrepareRequestArgs(disk_name))
    return disk_request.execute()


class DeleteDisk(DiskCommand):
  """Delete one or more persistent disks.

  Specify multiple disks as space-separated entries. If multiple disk names
  are specified, the disks will be deleted in parallel.
  """

  positional_args = '<disk-name-1> ... <disk-name-n>'
  safety_prompt = 'Delete disk'

  def __init__(self, name, flag_values):
    super(DeleteDisk, self).__init__(name, flag_values)

  def Handle(self, *disk_names):
    """Delete the specified disks.

    Args:
      *disk_names: The names of the disks to delete

    Returns:
      Tuple (results, exceptions) - result of deleting the disks.
    """
    self._AutoDetectZone()

    requests = []

    for disk_name in disk_names:
      requests.append(self.api.disks.delete(
          **self._PrepareRequestArgs(disk_name)))
    results, exceptions = self.ExecuteRequests(requests)
    return (self.MakeListResult(results, 'operationList'), exceptions)


class ListDisks(DiskCommand, command_base.GoogleComputeListCommand):
  """List the disks for a project."""

  def IsZoneLevelCollection(self):
    return True

  def IsGlobalLevelCollection(self):
    return False

  def __init__(self, name, flag_values):
    super(ListDisks, self).__init__(name, flag_values)

  def ListFunc(self):
    """Returns the function for listing disks."""
    return None

  def ListZoneFunc(self):
    """Returns the function for listing disks in a zone."""
    return self.api.disks.list

  def ListAggregatedFunc(self):
    """Returns the function for listing disks across all zones."""
    return self.api.disks.aggregatedList


def AddCommands():
  appcommands.AddCmd('adddisk', AddDisk)
  appcommands.AddCmd('getdisk', GetDisk)
  appcommands.AddCmd('deletedisk', DeleteDisk)
  appcommands.AddCmd('listdisks', ListDisks)
