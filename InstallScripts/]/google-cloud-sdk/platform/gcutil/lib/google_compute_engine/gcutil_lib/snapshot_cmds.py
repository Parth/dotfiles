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

"""Commands for interacting with Google Compute Engine disk snapshots."""




from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_logging


FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER


class SnapshotCommand(command_base.GoogleComputeCommand):
  """Base command for working with the snapshots collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'status', 'disk-size-gb'],
      field_mappings=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('status', 'status'),
          ('disk-size-gb', 'diskSizeGb'),
          ('storage-bytes', 'storageBytes'),
          ('storage-bytes-status', 'storageBytesStatus'),
          ('source-disk', 'sourceDisk')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('status', 'status'),
          ('disk-size-gb', 'diskSizeGb'),
          ('storage-bytes', 'storageBytes'),
          ('storage-bytes-status', 'storageBytesStatus'),
          ('source-disk', 'sourceDisk')),
      sort_by='name')

  resource_collection_name = 'snapshots'

  def __init__(self, name, flag_values):
    super(SnapshotCommand, self).__init__(name, flag_values)

  def _PrepareRequestArgs(self, snapshot_context, **other_args):
    """Gets the dictionary of API method keyword arguments.

    Args:
      snapshot_context:  Context dict for this snapshot.
      **other_args: Keyword arguments that should be included in the request.

    Returns:
      Dictionary of keyword arguments that should be passed in the API call,
      includes all keyword arguments passed in 'other_args' plus
      common keys such as the name of the resource and the project.
    """

    kwargs = {
        'project': snapshot_context['project'],
        'snapshot': snapshot_context['snapshot']
    }
    for key, value in other_args.items():
      kwargs[key] = value
    return kwargs

  def _AutoDetectZone(self):
    """Causes this command to auto detect zone."""
    def _GetZoneContext(unused_object_type, context):
      return self.GetZoneForResource(
          self.api.disks, context['disk'], context['project'])

    self._context_parser.context_prompt_fxns['zone'] = _GetZoneContext


class AddSnapshot(SnapshotCommand):
  """Create a new persistent disk snapshot."""

  positional_args = '<snapshot-name>'
  status_field = 'status'
  _TERMINAL_STATUS = ['READY', 'FAILED']

  def __init__(self, name, flag_values):
    super(AddSnapshot, self).__init__(name, flag_values)
    flags.DEFINE_string('description',
                        '',
                        'An optional snapshot description.',
                        flag_values=flag_values)
    flags.DEFINE_string('source_disk',
                        None,
                        '[Required] Specifies the source disk from which to '
                        'create the snapshot. For example, \'--source_disk='
                        'my-disk\'.',
                        flag_values=flag_values)
    flags.DEFINE_string('zone',
                        None,
                        '[Required] The zone of the disk.',
                        flag_values=flag_values)
    flags.DEFINE_boolean('wait_until_complete',
                         False,
                         'Specifies that gcutil should wait until the '
                         'snapshot has been successfully created before '
                         'returning.',
                         flag_values=flag_values)

  def Handle(self, snapshot_name):
    """Add the specified snapshot.

    Args:
      snapshot_name: The name of the snapshot to add

    Returns:
      The result of inserting the snapshot.
    """
    self._AutoDetectZone()
    snapshot_context = self._context_parser.ParseContextOrPrompt('snapshots',
                                                                 snapshot_name)

    if not self._flags.source_disk:
      disk = self._presenter.PromptForDisk(self.api.disks)
      if not disk:
        raise gcutil_errors.CommandError(
            'You cannot create a snapshot if you have no disks.')
      self._flags.source_disk = disk['selfLink']

    disk_context = self._context_parser.ParseContextOrPrompt(
        'disks', self._flags.source_disk)

    snapshot_resource = {
        'kind': self._GetResourceApiKind('snapshot'),
        'name': snapshot_context['snapshot'],
        'description': self._flags.description
    }

    kwargs = {
        'project': snapshot_context['project'],
        'zone': disk_context['zone'],
        'disk': disk_context['disk'],
        'body': snapshot_resource
    }

    snapshot_request = self.api.disks.createSnapshot(**kwargs)
    result = snapshot_request.execute()

    result = self._WaitForCompletionIfNeeded(result,
                                             snapshot_context,
                                             'disks')
    return result

  def _WaitForCompletionIfNeeded(self, result, snapshot_context,
                                 collection_name='snapshots'):
    """Waits until the snapshot is completed if gcutil is in synchronous_mode.

    Args:
      result:  The result of a snapshot creation request.
      snapshot_context:  Context dict for the snapshot created.
      collection_name:  The name of the resource type targetted by the creation
          request.

    Returns:
      Json containing the full snapshot resource if gcutil is running in
      synchronous mode or if wait_until_complete is set.  The original
      contents of result otherwise.
    """

    if self._flags.synchronous_mode or self._flags.wait_until_complete:
      result = self.WaitForOperation(
          self._flags.max_wait_time, self._flags.sleep_between_polls,
          self._timer, result, collection_name=collection_name)

    if self._flags.wait_until_complete:
      if not [item for item in result if item.get('error', False)]:
        result = self._InternalGetSnapshot(snapshot_context)
        result = self._WaitUntilSnapshotIsComplete(result, snapshot_context)

    return result

  def _InternalGetSnapshot(self, snapshot_context):
    """A simple implementation of getting current snapshot state.

    Args:
      snapshot_context: Context dict for the snapshot to get.

    Returns:
      Json containing full snapshot information.
    """
    snapshot_request = self.api.snapshots.get(
        **self._PrepareRequestArgs(snapshot_context))
    return snapshot_request.execute()

  def _WaitUntilSnapshotIsComplete(self, result, snapshot_context):
    """Waits for the snapshot to complete.

    Periodically polls the server for current snapshot status. Exits if the
    status of the snapshot is READY or FAILED or the maximum waiting
    timeout has been reached. In both cases returns the last known snapshot
    details.

    Args:
      result: the current state of the snapshot.
      snapshot_context: Context dict the snapshot to watch.

    Returns:
      Json containing full snapshot information.
    """
    current_status = result[self.status_field]
    start_time = self._timer.time()
    LOGGER.info('Will wait for snapshot to complete for: %d seconds.',
                self._flags.max_wait_time)
    while (self._timer.time() - start_time < self._flags.max_wait_time and
           current_status not in self._TERMINAL_STATUS):
      LOGGER.info(
          'Waiting for snapshot. Current status: %s. Sleeping for %ss.',
          current_status, self._flags.sleep_between_polls)
      self._timer.sleep(self._flags.sleep_between_polls)
      result = self._InternalGetSnapshot(snapshot_context)
      current_status = result[self.status_field]
    if current_status not in self._TERMINAL_STATUS:
      LOGGER.warn('Timeout reached. Snapshot %s has not yet completed.',
                  snapshot_context['snapshot'])
    return result


class GetSnapshot(SnapshotCommand):
  """Get a persistent disk snapshot."""

  positional_args = '<snapshot-name>'

  def __init__(self, name, flag_values):
    super(GetSnapshot, self).__init__(name, flag_values)

  def Handle(self, snapshot_name):
    """Get the specified snapshot.

    Args:
      snapshot_name: The name of the snapshot to get

    Returns:
      The result of getting the snapshot.
    """
    snapshot_context = self._context_parser.ParseContextOrPrompt('snapshots',
                                                                 snapshot_name)

    snapshot_request = self.api.snapshots.get(
        **self._PrepareRequestArgs(snapshot_context))

    return snapshot_request.execute()


class DeleteSnapshot(SnapshotCommand):
  """Delete one or more persistent disk snapshot."""

  positional_args = '<snapshot-name>'
  safety_prompt = 'Delete snapshot'

  def __init__(self, name, flag_values):
    super(DeleteSnapshot, self).__init__(name, flag_values)

  def Handle(self, *snapshot_names):
    """Delete the specified snapshots.

    Args:
      *snapshot_names: The names of the snapshots to delete

    Returns:
      Tuple (results, exceptions) - results of deleting the snapshots.
    """
    requests = []
    for snapshot_name in snapshot_names:
      snapshot_context = self._context_parser.ParseContextOrPrompt(
          'snapshots', snapshot_name)
      requests.append(self.api.snapshots.delete(
          **self._PrepareRequestArgs(snapshot_context)))
    results, exceptions = self.ExecuteRequests(requests)
    return self.MakeListResult(results, 'operationList'), exceptions


class ListSnapshots(SnapshotCommand, command_base.GoogleComputeListCommand):
  """List the persistent disk snapshots for a project."""

  def ListFunc(self):
    """Returns the function for listing snapshots."""
    return self.api.snapshots.list


def AddCommands():
  appcommands.AddCmd('addsnapshot', AddSnapshot)
  appcommands.AddCmd('getsnapshot', GetSnapshot)
  appcommands.AddCmd('deletesnapshot', DeleteSnapshot)
  appcommands.AddCmd('listsnapshots', ListSnapshots)
