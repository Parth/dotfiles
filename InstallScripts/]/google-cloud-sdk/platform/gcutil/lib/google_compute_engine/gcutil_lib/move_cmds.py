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

"""Commands for moving resources from one zone to another."""



import copy
import cStringIO
import datetime
import json
import os
import uuid


from apiclient.http import BatchHttpRequest
from apiclient.http import HttpRequest
from apiclient.model import JsonModel

from google.apputils import app
from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_logging
from gcutil_lib import utils
from gcutil_lib import version


LOGGER = gcutil_logging.LOGGER

MAX_INSTANCES_TO_MOVE = 100
MAX_DISKS_TO_MOVE = 100

DEFAULT_SLEEP_BETWEEN_POLLS = 10
DEFAULT_OPERATION_TIMEOUT = 3600
DEFAULT_SNAPSHOT_TIMEOUT = 7200


class DependencyDownloader(object):
  """Downloads all resource dependencies and their replacements.

  Starting with a set of instances, will download their dependencies (images,
  machine types) and all replacements for any deprecated resources.
  """

  BATCH_SIZE = 10

  def __init__(self, move_command, batch_uri):
    # Resource tracking
    self._pending = []     # List of resources to download.
    self._resources = {}   # Resource URL -> Resource JSON.
    # Set of visited resources to prevent redundant download
    self._visited = set()

    # Support for http batch execution.
    self._move_command = move_command
    self._batch_uri = batch_uri
    # HTTP response post-processing to hook into google-api-python-client
    self._http_postproc = JsonModel().response
    self._errors = []  # list of exceptions encountered

  def AddInstance(self, instance):
    self._Add(instance.get('image'))
    self._Add(instance.get('machineType'))

  def _Add(self, url):
    if url and url not in self._visited:
      self._visited.add(url)
      self._pending.append(url)

  def _AddResource(self, resource):
    kind = resource.get('kind')

    if kind == 'compute#instance':
      self.AddInstance(resource)
    else:
      # Check for deprecation replacement
      self._AddReplacement(resource)

  def _AddReplacement(self, resource):
    deprecated = resource.get('deprecated')
    if deprecated:
      self._Add(deprecated.get('replacement'))

  def _Callback(self, request_id, response, exception):
    if exception is not None:
      self._errors.append(exception)
    elif response:
      assert request_id == response.get('selfLink'), 'selfLink mismatch'
      self._resources[request_id] = response
      self._AddResource(response)

  def Download(self):
    """Performs the actual download based on the initial set of instances.

    Returns:
        tuple (resources, errors).
        'resources' is a dictionary from resource URL to its parsed JSON
        representation and includes the whole transitive closure of all
        dependent resources and, if deprecated, their replacements.
        'errors' is a list of errors encountered during transitive closure
        download. Empty list if no errors were encountered.
    """

    while self._pending:
      batch = self._pending[:self.BATCH_SIZE]
      self._pending = self._pending[self.BATCH_SIZE:]

      batch_request = BatchHttpRequest(batch_uri=self._batch_uri)
      for url in batch:
        request = HttpRequest(None, self._http_postproc, url, headers={})
        batch_request.add(request, callback=self._Callback, request_id=url)
      batch_request.execute(http=self._move_command.CreateHttp())

    return self._resources, self._errors


class MoveInstancesBase(command_base.GoogleComputeCommand):
  """The base class for the move commands."""

  def __init__(self, name, flag_values):
    super(MoveInstancesBase, self).__init__(name, flag_values)
    self._common_region = ''

    flags.DEFINE_boolean(
        'force',
        False,
        'Override the confirmation prompt.',
        flag_values=flag_values)

    flags.DEFINE_boolean(
        'keep_snapshots',
        False,
        'Do not delete snapshots that were created for the disks.',
        flag_values=flag_values)

    flags.DEFINE_boolean(
        'replace_deprecated',
        False,
        'Replaces deprecated resource with their recommended replacement.',
        flag_values=flag_values)

  def _GetFlagValue(self, name, default):
    """Gets flag value, returning provided default if flag not specified."""
    flag = self._flags[name]
    return flag.value if flag.present else default

  def _GetTimeoutSeconds(self):
    return self._GetFlagValue('max_wait_time', DEFAULT_OPERATION_TIMEOUT)

  def _GetSleepBetweenPollsSeconds(self):
    return self._GetFlagValue('sleep_between_polls',
                              DEFAULT_SLEEP_BETWEEN_POLLS)

  def Handle(self, *args, **kwargs):
    """The point of entry to the command.

    This dispatches the subclass' HandleMove method.
    """
    if self.api.version != version.get('v1'):
      raise gcutil_errors.UnsupportedCommand(
          'Moving instances is supported only in service version v1.')

    self._project = utils.GetProjectId(self._project, self.api)

    self._project_resource = self.api.projects.get(
        project=self._project).execute()
    if self.api.addresses:
      self._address_list = utils.AllAggregated(
          self.api.addresses.aggregatedList,
          self._project)
    self.HandleMove(*args, **kwargs)
    print 'The move completed successfully.'

  def _Confirm(self, instances_to_mv, instances_to_ignore, disks_to_mv,
               dest_zone, src_zone):
    """Displays what is about to happen and prompts the user to proceed.

    Args:
      instances_to_mv: The instances that will be moved.
      instances_to_ignore: Instances that will not be moved because they're
        already in the destination zone.
      disks_to_mv: A list of the disk names that will be moved.
      dest_zone: The destination zone.
      src_zone: The source zone.

    Raises:
      CommandError: If the user declines to proceed.
    """
    # Ensures that the parameters make sense.
    assert instances_to_mv, (
        'Cannot confirm move if there are no instances to move.')
    assert not [i for i in instances_to_mv if i['zone'].endswith(dest_zone)], (
        'Some instances in the move set are already in the destination zone.')
    assert ([i for i in instances_to_ignore if i['zone'].endswith(dest_zone)] ==
            instances_to_ignore), (
                'Not all instances in ignore set are in destination zone.')

    if instances_to_ignore:
      print ('These instances are already in %s and will not be moved:' %
             dest_zone)
      print utils.ListStrings(i['name'] for i in instances_to_ignore)

    print 'The following instances will be moved to %s:' % dest_zone
    print utils.ListStrings(i['name'] for i in instances_to_mv)

    if disks_to_mv:
      print 'The following disks will be moved to %s:' % dest_zone
      print utils.ListStrings(disks_to_mv)

    # Checks for the same region in src and dest
    src_zone_resource = self.api.zones.get(
        project=self._project, zone=src_zone).execute()

    dest_zone_resource = self.api.zones.get(
        project=self._project, zone=dest_zone).execute()

    if src_zone_resource['region'] != dest_zone_resource['region']:
      LOGGER.warn('The regions for source and destination zones do not match. '
                  'If you are using reserved external IPs, they will not be '
                  'preserved in this operation.')
      self._common_region = None
    else:
      self._common_region = self.DenormalizeResourceName(
          src_zone_resource['region'])
    print 'WARNING: Do not attempt to move instances to zones that cannot'
    print '  support the current instances (e.g. Moving instances using SSDs'
    print '  to zones that do not support SSD, Windows to non-Windows, etc.)'
    print '*** Be prepared to recover manually in the event of failure ***'

    if not self._PresentSafetyPrompt('Proceed', True):
      raise gcutil_errors.CommandError('Move aborted.')

  def _GetPersistentDiskDeviceName(self, instance):
    res = []
    for disk in instance.get('disks', []):
      if disk['type'] == 'PERSISTENT':
        res.append(disk['deviceName'])
    return res

  def _TurnOffAutoDeleteForDisks(self, instances, zone):
    """Auto-Delete must be switched off for all instances.

    Args:
      instances: A list of instance resources for which auto-delete
        must be turned off.
      zone: The zone of the instances.

    Raises:
      CommandError: If one or more of the changes fail.
    """
    if not instances:
      return

    print 'Turning off auto delete for disks in the instances...'
    requests = []

    for instance in instances:
      instance_devices = self._GetPersistentDiskDeviceName(instance)
      for device_name in instance_devices:
        requests.append(self.api.instances.setDiskAutoDelete(
            project=self._project,
            zone=zone,
            instance=instance['name'],
            deviceName=device_name,
            autoDelete=False))

    results, exceptions = self.ExecuteRequests(
        requests, wait_for_operations=True,
        timeout_seconds=self._GetTimeoutSeconds(),
        sleep_between_polls_seconds=self._GetSleepBetweenPollsSeconds(),
        collection_name='instances')

    if exceptions:
      raise gcutil_errors.CommandError(
          'Aborting due to errors while turning off auto delete:\n%s' %
          utils.ListStrings(exceptions))

    self._VerifyOperations(self.MakeListResult(results, 'operationList'))

  def _DeleteInstances(self, instances, zone):
    """Deletes the given instances.

    Args:
      instances: A list of instance resources.
      zone: The zone to which the instances belong.

    Raises:
      CommandError: If one or more of the deletions fail.
    """
    if not instances:
      return

    print 'Deleting instances...'
    requests = []
    for instance in instances:
      requests.append(self.api.instances.delete(
          project=self._project,
          zone=zone,
          instance=instance['name']))
    results, exceptions = self.ExecuteRequests(
        requests, wait_for_operations=True,
        timeout_seconds=self._GetTimeoutSeconds(),
        sleep_between_polls_seconds=self._GetSleepBetweenPollsSeconds(),
        collection_name='instances')
    if exceptions:
      raise gcutil_errors.CommandError(
          'Aborting due to errors while deleting instances:\n%s' %
          utils.ListStrings(exceptions))
    self._VerifyOperations(self.MakeListResult(results, 'operationList'))

  def _MapPerZoneMachineType(self, machine_type, dst_zone):
    return self.NormalizeMachineTypeResourceName(
        self._project, dst_zone, 'machineTypes',
        self.DenormalizeResourceName(machine_type))

  def _CreateInstances(self, instances, src_zone, dest_zone):
    """Creates the instance resources in the given list in dest_zone.

    The instance resources are changed in two ways:
      (1) Their zone fields are changed to dest_zone; and
      (2) Their ephemeral IPs are cleared.

    Args:
      instances: A list of instance resources.
      src_zone: The zone to which the instances belong.
      dest_zone: The destination zone.

    Raises:
      CommandError: If one or more of the insertions fail.
    """
    if not instances:
      return

    print 'Recreating instances in %s...' % dest_zone

    ip_addresses = []

    if self._common_region:
      ip_addresses = set(self._project_resource.get('externalIpAddresses', []))

      addresses_json = self._address_list.get(
          'items', [])['regions/{0}'.format(self._common_region)].get(
              'addresses', [])

      ip_addresses = set(address['address'] for address in addresses_json)

    self._SetIps(instances, ip_addresses)

    requests = []
    for instance in instances:
      instance['zone'] = self.NormalizeTopLevelResourceName(
          self._project, 'zones', dest_zone)

      instance['machineType'] = self._MapPerZoneMachineType(
          instance.get('machineType'), dest_zone)

      # Replaces the zones for the persistent disks.
      for disk in instance['disks']:
        if 'source' in disk:
          disk['source'] = disk['source'].replace(
              'zones/' + src_zone, 'zones/' + dest_zone)

      requests.append(self.api.instances.insert(
          project=self._project, body=instance, zone=dest_zone))
    results, exceptions = self.ExecuteRequests(
        requests, wait_for_operations=True,
        timeout_seconds=self._GetTimeoutSeconds(),
        sleep_between_polls_seconds=self._GetSleepBetweenPollsSeconds(),
        collection_name='instances')
    if exceptions:
      raise gcutil_errors.CommandError(
          'Aborting due to errors while creating instances:\n%s' %
          utils.ListStrings(exceptions))
    self._VerifyOperations(self.MakeListResult(results, 'operationList'))

  def _CheckForFailedOperation(self, operation):
    error = operation.get('error')
    if not error: return None

    errors = error.get('errors')
    if not errors: return None

    messages = []
    for error in errors:
      if error:
        message = error.get('message')
        if message:
          messages.append(message)
          continue

        code = error.get('code')
        if code:
          messages.append('Operation failed with code %s.' % code)
          continue

      messages.append('Operation %s failed, server returned no error' % (
          operation.get('name') or '<unknown name>'))
    return messages

  def _CheckForUnfinishedOperation(self, operation):
    status = operation.get('status', 'unknown')
    if status == 'DONE':
      # Operation completed.
      return None

    return 'Operation %s did not complete. Its status is %s.' % (
        operation.get('name') or '<unknown name>', status)

  def _VerifyOperations(self, results):
    """Verifies successful completion of asynchronous operations.

    If any of the operations resulted in an error, or didn't complete due to
    timeout, raise CommandError.

    Args:
      results: Results from executing a batch of operations. This is a
          dictionary { 'items': [ { resource }, ... { operation }, ... ] }
    """
    _, ops = self._PartitionResults(results)
    error_list = []
    for op in (ops or []):
      errors = self._CheckForFailedOperation(op)
      if errors:
        error_list.extend(errors)
        continue
      error = self._CheckForUnfinishedOperation(op)
      if error:
        error_list.append(error)
    if error_list:
      raise gcutil_errors.CommandError(
          'Encountered errors:\n%s' % utils.ListStrings(error_list))

  def _SetIps(self, instances, ip_addresses):
    """Clears the natIP field for instances without reserved addresses."""
    for instance in instances:
      for interface in instance.get('networkInterfaces', []):
        for config in interface.get('accessConfigs', []):
          if 'natIP' in config and config['natIP'] not in ip_addresses:
            config.pop('natIP', None)

  def _WaitForSnapshots(self, snapshots):
    """Waits for the given snapshots to be in the READY state."""
    snapshots = set(snapshots)
    start_sec = self._timer.time()
    timeout_seconds = self._GetTimeoutSeconds()
    sleep_between_polls_seconds = self._GetSleepBetweenPollsSeconds()

    while True:
      if (timeout_seconds >= 0 and
          self._timer.time() - start_sec > timeout_seconds):
        raise gcutil_errors.CommandError(
            'Timeout reached while waiting for snapshots to be ready.')

      all_snapshots = [
          s for s in utils.All(self.api.snapshots.list, self._project)['items']
          if s['name'] in snapshots and s['status'] != 'READY']
      if not all_snapshots:
        print 'Snapshots created and READY.'
        break
      LOGGER.info('Waiting for snapshots to be READY. Sleeping for %ss' %
                  sleep_between_polls_seconds)
      self._timer.sleep(sleep_between_polls_seconds)

  def _CreateSnapshots(self, snapshot_mappings, src_zone, dest_zone):
    """Creates snapshots for the disks to be moved.

    Args:
      snapshot_mappings: A map of disk names that should be moved to
        the names that should be used for each disk's snapshot.
      src_zone: The source zone. All disks in snapshot_mappings must be
        in this zone.
      dest_zone: The zone the disks are destined for.
    """
    if not snapshot_mappings:
      return

    print 'Snapshotting disks...'
    requests = []
    for disk_name, snapshot_name in snapshot_mappings.iteritems():
      snapshot_resource = {
          'name': snapshot_name,
          'description': ('Snapshot for moving disk %s from %s to %s.' %
                          (disk_name, src_zone, dest_zone))}

      requests.append(self.api.disks.createSnapshot(
          project=self._project,
          zone=src_zone,
          disk=disk_name,
          body=snapshot_resource))

    results, exceptions = self.ExecuteRequests(
        requests, wait_for_operations=True,
        timeout_seconds=self._GetTimeoutSeconds(),
        sleep_between_polls_seconds=self._GetSleepBetweenPollsSeconds(),
        collection_name='snapshots')
    if exceptions:
      raise gcutil_errors.CommandError(
          'Aborting due to errors while creating snapshots:\n%s' %
          utils.ListStrings(exceptions))
    self._VerifyOperations(self.MakeListResult(results, 'operationList'))
    self._WaitForSnapshots(snapshot_mappings.values())

  def _DeleteSnapshots(self, snapshot_names, zone):
    """Deletes the given snapshots.

    Args:
      snapshot_names: A list of snapshot names to delete.
      zone: The zones to which the snapshots belong.
    """
    if not snapshot_names or self._flags.keep_snapshots:
      return

    print 'Deleting snapshots...'
    requests = []
    for name in snapshot_names:
      requests.append(self.api.snapshots.delete(
          project=self._project, snapshot=name))

    results, exceptions = self.ExecuteRequests(
        requests, wait_for_operations=True,
        timeout_seconds=self._GetTimeoutSeconds(),
        sleep_between_polls_seconds=self._GetSleepBetweenPollsSeconds(),
        collection_name='snapshots')
    if exceptions:
      raise gcutil_errors.CommandError(
          'Aborting due to errors while deleting snapshots:\n%s' %
          utils.ListStrings(exceptions))
    self._VerifyOperations(self.MakeListResult(results, 'operationList'))

  def _CreateDisksFromSnapshots(self, snapshot_mappings, disktype_mappings,
                                dest_zone):
    """Creates disks in the destination zone from the given snapshots.

    Args:
      snapshot_mappings: A dict of disk names to snapshot names. Disks are
        created in the destination zone from the given snapshot names. The
        disks will assume their previous names as indicated by the key-value
        pairs.
      dest_zone: The zone in which the disks will be created.
    """
    if not snapshot_mappings:
      return

    print 'Recreating disks from snapshots...'
    requests = []
    for disk_name, snapshot_name in snapshot_mappings.iteritems():
      disk_resource = {
          'name': disk_name,
          'type': disktype_mappings[disk_name],
          'sourceSnapshot': self.NormalizeGlobalResourceName(
              self._project, 'snapshots', snapshot_name)}
      requests.append(self.api.disks.insert(
          project=self._project, body=disk_resource, zone=dest_zone))

    results, exceptions = self.ExecuteRequests(
        requests, wait_for_operations=True,
        timeout_seconds=self._GetTimeoutSeconds(),
        sleep_between_polls_seconds=self._GetSleepBetweenPollsSeconds(),
        collection_name='disks')
    if exceptions:
      raise gcutil_errors.CommandError(
          'Aborting due to errors while re-creating disks:\n%s' %
          utils.ListStrings(exceptions))
    self._VerifyOperations(self.MakeListResult(results, 'operationList'))

  def _DeleteDisks(self, disk_names, zone):
    """Deletes the given disks.

    Args:
      disk_names: A list of disk names to delete.
      zone: The zone to which the disks belong.
    """
    if not disk_names:
      return

    print 'Deleting disks...'
    requests = []
    for name in disk_names:
      requests.append(self.api.disks.delete(
          project=self._project, disk=name, zone=zone))

    results, exceptions = self.ExecuteRequests(
        requests, wait_for_operations=True,
        timeout_seconds=self._GetTimeoutSeconds(),
        sleep_between_polls_seconds=self._GetSleepBetweenPollsSeconds(),
        collection_name='disks')
    if exceptions:
      raise gcutil_errors.CommandError(
          'Aborting due to errors while deleting disks:\n%s' %
          utils.ListStrings(exceptions))
    self._VerifyOperations(self.MakeListResult(results, 'operationList'))

  def _CalculateNumCpus(self, instances_to_mv, src_zone):
    """Calculates the amount of CPUs used by the given instances."""
    kwargs = {'zone': src_zone}
    machines = utils.All(
        self.api.machine_types.list,
        self._project,
        **kwargs)['items']
    num_cpus = dict((m['selfLink'], m['guestCpus']) for m in machines)
    return sum(float(num_cpus[i['machineType']]) for i in instances_to_mv)

  def _CalculateTotalDisksSizeGb(self, disk_names, zone):
    """Calculates the total size of the given disks."""
    disk_names = set(disk_names)
    disks = utils.All(
        self.api.disks.list,
        self._project,
        zone=zone)['items']
    disk_sizes = [float(d['sizeGb']) for d in disks if d['name'] in disk_names]
    return sum(disk_sizes)

  def _CreateQuotaRequirementsDict(self, instances_to_mv, disks_to_mv,
                                   src_zone, snapshots_to_create=None):
    """Generates a mapping between resource type to the quota required."""
    return {'INSTANCES': len(instances_to_mv),
            'CPUS': self._CalculateNumCpus(instances_to_mv, src_zone),
            'DISKS': len(disks_to_mv),
            'DISKS_TOTAL_GB': self._CalculateTotalDisksSizeGb(
                disks_to_mv, src_zone),
            'SNAPSHOTS': (len(snapshots_to_create)
                          if snapshots_to_create is not None
                          else len(disks_to_mv))}

  def _CheckQuotas(self, instances_to_mv, disks_to_mv, src_zone, dest_zone,
                   snapshots_to_create=None):
    """Raises a CommandError if the quota to perform the move does not exist."""
    print 'Checking quotas...'


    requirements = self._CreateQuotaRequirementsDict(
        instances_to_mv, disks_to_mv, src_zone,
        snapshots_to_create=snapshots_to_create)

    dest_zone_resource = self.api.zones.get(
        project=self._project, zone=dest_zone).execute()

    dest_name = self.DenormalizeResourceName(
        dest_zone_resource['region'])

    src_zone_resource = self.api.zones.get(
        project=self._project, zone=src_zone).execute()

    dest_region_resource = self.api.regions.get(
        project=self._project, region=dest_name).execute()

    if src_zone_resource['region'] == dest_zone_resource['region']:
      # When moving within a region, the only quota that matters is
      # snapshots.
      if 'SNAPSHOTS' in requirements:
        requirements = {'SNAPSHOTS': requirements['SNAPSHOTS']}
      else:
        requirements = {}

    local_quotas = dest_region_resource.get('quotas', [])

    available = self._ExtractAvailableQuota(
        self._project_resource.get('quotas', []),
        local_quotas, requirements)

    LOGGER.debug('Required quota for move is: %s', requirements)
    LOGGER.debug('Available quota is: %s', available)

    for metric, required in requirements.iteritems():
      if metric in available:
        if available[metric] - required < 0:
          raise gcutil_errors.CommandError(
              'You do not have enough quota for %s in %s for your project '
              '(%d available, %d needed.)' % (
                  metric, dest_name, available.get(metric, 0), required))

  def _ExtractAvailableQuota(self, project_quota, local_quota, requirements):
    """Extracts the required quota from the given project and zone resources.

    Args:
      project_quota: The list of project quotas that's included in a project
        resource.
      local_quota: The list of local quotas that's included in a zone or region
        resource.
      requirements: A dict mapping resource type to the amount of required
        quota.

    Returns:
      A mapping of available quota for INSTANCES, CPUS, DISKS, DISKS_TOTAL_GB,
      and SNAPSHOTS. The value can be negative if enough quota does not exist.
    """
    pertinent_resources = set(requirements.keys())
    available = {}

    for quota in project_quota:
      metric = quota['metric']
      if metric in pertinent_resources:
        available[metric] = quota['limit'] - quota['usage']
        # For existing resources that are to be moved (i.e.,
        # everything in requirements except snapshots since they do
        # not exist yet) since they do not exist yet) we must count
        # them into the available number since they will be deleted
        # shortly.
        if metric != 'SNAPSHOTS':
          available[metric] += requirements[metric]

    for quota in local_quota:
      metric = quota['metric']
      if metric in pertinent_resources:
        if metric in available:
          available[metric] = min(available[metric],
                                  quota['limit'] - quota['usage'])
        else:
          available[metric] = quota['limit'] - quota['usage']

    return available

  def _CheckDeprecatedResources(self, instances_to_move):
    print 'Checking for dependencies on deprecated resources...'

    # 1. Download all dependencies of the instances being moved
    resources, exceptions = self._DownloadDependencies(instances_to_move)
    if exceptions:
      raise gcutil_errors.CommandError(
          'Aborting due to errors while checking resource deprecation:\n%s' %
          utils.ListStrings(exceptions))

    # 2. Find deprecated dependencies, and find their replacements
    deprecated = self._FindDeprecatedResourceReplacements(resources)

    # 3. Check all instances for deprecated depencencies and apply replacements
    if not self._flags.replace_deprecated:
      # Act as if no replacement resources are available.
      deprecated = dict((key, None) for key in deprecated)

    upgraded_instances, errors = self._ApplyReplacements(
        instances_to_move, deprecated, resources)

    if errors:
      message = cStringIO.StringIO()
      message.write(
          'Move aborted.\n'
          'Cannot find replacement for deprecated dependencies of the '
          'following instances:\n')
      for instance, fields in errors:
        message.write('\n  %s:\n' % self._presenter.PresentElement(instance))
        for field in sorted(fields.keys()):
          message.write(
              '    %s: %s\n' % (field,
                                self._presenter.PresentElement(fields[field])))
      if not self._flags.replace_deprecated:
        message.write('\n\nConsider running with --replace_deprecated')
      raise gcutil_errors.CommandError(message.getvalue())

    if self._flags.replace_deprecated:
      return upgraded_instances
    else:
      return instances_to_move

  def _FindDeprecatedResourceReplacements(self, resources):
    """Finds replacements for deprecated resources.

    Args:
      resources: dictionary map url -> resource JSON.
    Returns:
      dictionary resource -> replacement (or None)
    """
    deprecated_replacements = {}

    for url in resources.keys():
      replacement = url

      # Resolve chain of deprecated resource replacements.
      while True:
        resource = resources[replacement]
        deprecated = resource.get('deprecated')
        if deprecated and self._WillCauseError(deprecated):
          replacement = deprecated.get('replacement')
          if not replacement:  # No replacement for deprecated resource
            replacement = None
            break
        else:
          break  # Found replacement, possibly self

      if replacement != url:
        assert (replacement is None or
                not resources[replacement].get('deprecated'))
        deprecated_replacements[url] = replacement

    return deprecated_replacements

  def _WillCauseError(self, deprecated):
    # Only OBSOLETE and DELETED resources cause errors on creation.
    return deprecated.get('state', '') in ('OBSOLETE', 'DELETED')

  def _ApplyReplacements(self, instances_to_move, deprecated, resources):
    """Applies replacement for deprecated resources to the instances list.

    Args:
      instances_to_move: List of instances (parsed JSON) being moved.
      deprecated: dict; maps deprecated resource URL to its replacement (or None
          if no replacement is available).
      resources: dict; URL -> parsed JSON resource of the transitive closure of
          all dependent resources and their replacements, if deprecated.

    Returns:
      Tuple updated_instances, list of failures. Each failure is a tuple:
      (instance_url, {dependent resource type: URL}) and represents dependent
      resource which is obsolete but replacement could not be found.
    """

    def Apply(instance, *fields):
      """Looks up replacements for deprecated resources in specified fields.

      Args:
        instance: The instance resource to apply changes to.
        *fields: List of field specifiers. Each specifier is a tuple
                 (name, default value). Default value is used if resource
                 doesn't have property with a given name.

      Returns:
          Dictionary for collecting error information.
          Maps property name -> URL fo resource without replacement.
      """
      error = {}
      for property_name, default in fields:
        url = instance.get(property_name) or default
        if url and url in deprecated:
          replacement = deprecated[url]
          if replacement:
            # Replacement exists, apply it.
            instance[property_name] = replacement
          else:
            # No replacement. Error.
            error[property_name] = url
        else:
          # Resource is not deprecated
          pass
      return error

    updated = []
    errors = []

    for instance in instances_to_move:
      instance = copy.deepcopy(instance)
      updated.append(instance)

      error = Apply(
          instance,
          ('image', None),
          ('machineType', None))

      if error:
        errors.append((instance.get('selfLink'), error))

    return updated, errors

  def _DownloadDependencies(self, instances_to_move):
    downloader = DependencyDownloader(
        self, self._flags.api_host.rstrip('/') + '/batch')
    for instance in instances_to_move:
      downloader.AddInstance(instance)
    return downloader.Download()


class MoveInstances(MoveInstancesBase):
  """Move VM instances from one zone to another zone.

  This command also moves any persistent disks that are attached to
  the instances.

  During the move, do not modify your project, as changes to the
  project may interfere with the move.

  You can pick which instances to move by specifying a series of regular
  expressions that will be used to match instance names in the source
  zone. For example, the following command will move all instances in
  zone-a whose names match the regular expressions i-[0-9] or b-.* to
  zone-b:

    gcutil moveinstances \
      --source_zone=zone-a \
      --destination_zone=zone-b \
      "i-[0-9]" "b-.*"

  WARNING: Instances that are moved will lose ALL of their transient
  state (i.e., scratch disks, ephemeral IP addresses, and memory).

  WARNING: This command may fail. If failure happens during validation,
  the state of your instances is preserved. If failure happens during
  the move, the 'resumemove' command may be used to recover. In rare
  circumstances, you may need to move your instances by hand.
  """

  positional_args = '<name-regex-1> ... <name-regex-n>'

  def __init__(self, name, flag_values):
    """Constructs a new MoveInstances object."""
    super(MoveInstances, self).__init__(name, flag_values)

    flags.DEFINE_string(
        'source_zone',
        None,
        '[Required] The source zone from which instances will be moved.',
        flag_values=flag_values)
    flags.DEFINE_string(
        'destination_zone',
        None,
        '[Required] The zone to which the instances should be moved.',
        flag_values=flag_values)

  def _ValidateFlags(self):
    """Raises a UsageError if there is any problem with the flags."""
    if not self._flags.source_zone:
      raise app.UsageError(
          'You must specify a source zone through the --source_zone flag.')
    if not self._flags.destination_zone:
      raise app.UsageError('You must specify a destination zone '
                           'through the --destination_zone flag.')
    if self._flags.source_zone == self._flags.destination_zone:
      raise app.UsageError('The destination and source zones cannot be equal.')

  def HandleMove(self, *instance_regexes):
    """Handles the actual move.

    Args:
      *instance_regexes: The sequence of name regular expressions used
        for filtering.

    Raises:
      app.UsageError: If no regexes were provided.
    """
    self._ValidateFlags()

    if not instance_regexes:
      raise app.UsageError(
          'You must specify at least one regex for instances to move.')

    self._flags.destination_zone = self.DenormalizeResourceName(
        self._flags.destination_zone)
    self._CheckDestinationZone()

    print 'Retrieving instances in %s matching: %s...' % (
        self._flags.source_zone, ' '.join(instance_regexes))
    instances_to_mv = utils.All(
        self.api.instances.list,
        self._project,
        filter='name eq %s' % utils.CombineRegexes(instance_regexes),
        zone=self._flags.source_zone)['items']
    instances_in_dest = utils.All(
        self.api.instances.list,
        self._project,
        filter='name eq %s' % utils.CombineRegexes(instance_regexes),
        zone=self._flags.destination_zone)['items']

    self._CheckInstancePreconditions(instances_to_mv, instances_in_dest)

    instances_to_ignore = utils.All(
        self.api.instances.list,
        self._project,
        filter='name ne %s' % utils.CombineRegexes(instance_regexes),
        zone=self._flags.source_zone)['items']

    print 'Checking disk preconditions...'
    disks_to_mv = self._GetPersistentDiskNames(instances_to_mv)
    self._CheckDiskPreconditions(instances_to_ignore, disks_to_mv)
    # At this point, all disks in use by instances_to_mv are only
    # attached to instances in the set instances_to_mv.

    # Check the snapshots quota and the quota in the destination zone
    # to make sure that enough quota exists to support the move.
    self._CheckQuotas(instances_to_mv, disks_to_mv, self._flags.source_zone,
                      self._flags.destination_zone)

    # Check if any dependencies of the moved instances are deprecated.
    instances_to_mv = self._CheckDeprecatedResources(instances_to_mv)

    self._Confirm(instances_to_mv, [], disks_to_mv,
                  self._flags.destination_zone, self._flags.source_zone)

    log_path = self._GenerateLogPath()
    snapshot_mappings = self._GenerateSnapshotNames(disks_to_mv)
    disktype_mappings = self._GetDiskTypes(disks_to_mv, self._flags.source_zone,
                                           self._flags.destination_zone)

    try:
      self._WriteLog(log_path, instances_to_mv, snapshot_mappings,
                     disktype_mappings)

      self._TurnOffAutoDeleteForDisks(instances_to_mv, self._flags.source_zone)
      self._DeleteInstances(instances_to_mv, self._flags.source_zone)

      # Assuming no other processes have modified the user's project, at
      # this point, we can assume that all disks-to-be-moved are
      # dormant.
      self._CreateSnapshots(snapshot_mappings,
                            self._flags.source_zone,
                            self._flags.destination_zone)
      self._DeleteDisks(disks_to_mv, self._flags.source_zone)
      self._CreateDisksFromSnapshots(snapshot_mappings, disktype_mappings,
                                     self._flags.destination_zone)
      self._CreateInstances(instances_to_mv,
                            self._flags.source_zone,
                            self._flags.destination_zone)

      self._DeleteSnapshots(snapshot_mappings.values(),
                            self._flags.destination_zone)

      # We have succeeded, so it's safe to delete the log file.
      self._DeleteLog(log_path)

    except Exception as e:
      print 'Sorry, we encountered an error while moving your instances.'
      print 'Please try to resume the move using the command: '
      print '  gcutil --project=%s resumemove %s' % (self._project, log_path)
      raise e

  def _GenerateSnapshotNames(self, disk_names):
    """Returns a dict mapping each disk name to a random UUID.

    The UUID will be used as the disk's snapshot name. UUID's are
    valid Compute resource names. Further, UUID collisions are
    improbable, so using them is a great way for generating resource
    names (e.g., we avoid network communication to check if the name
    we choose already exists).

    Args:
      disk_names: A list of disk_names for which snapshot names
        should be generated.

    Returns:
      A dict with the mapping.
    """
    return dict((name, 'snapshot-' + str(uuid.uuid4())) for name in disk_names)

  def _GetDiskTypes(self, disk_names, src_zone, dest_zone):
    """Returns a dict mapping each disk name to its type.

    The type will be the type of the disk in the destination zone.

    Args:
      disk_names: an array of all the disk names to be moved.
      src_zone: the source zone.
      dest_zone: the destination zone.

    Returns:
      A dict with the mapping.
    """

    all_disks = [
        d for d in utils.All(self.api.disks.list, self._project,
                             None, None, zone=src_zone)['items']
        if d['name'] in disk_names]

    return dict((d['name'], d['type'].replace(
        '/zones/'+ src_zone, '/zones/' + dest_zone)) for d in all_disks)

  def _CheckInstancePreconditions(self, instances_to_mv, instances_in_dest):
    if not instances_to_mv:
      raise gcutil_errors.CommandError('No matching instances were found.')

    if len(instances_to_mv) > MAX_INSTANCES_TO_MOVE:
      raise gcutil_errors.CommandError(
          'At most %s instances can be moved at a '
          'time. Refine your query and try again.' % MAX_INSTANCES_TO_MOVE)

    # Checks for name collisions.
    src_names = [i['name'] for i in instances_to_mv]
    dest_names = [i['name'] for i in instances_in_dest]
    common_names = set(src_names) & set(dest_names)
    if common_names:
      raise gcutil_errors.CommandError(
          'Encountered name collisions. Instances with the following names '
          'exist in both the source and destination zones: \n%s' %
          utils.ListStrings(common_names))

  def _CheckDiskPreconditions(self, instances_to_ignore, disk_names):
    if len(disk_names) > MAX_DISKS_TO_MOVE:
      raise gcutil_errors.CommandError(
          'At most %s disks can be moved at a '
          'time. Refine your query and try again.' % MAX_DISKS_TO_MOVE)

    res = self._CheckForDisksInUseByOtherInstances(
        instances_to_ignore, disk_names)
    if res:
      offending_instances = ['%s: %s' % (instance, ', '.join(disks))
                             for instance, disks in res]
      raise gcutil_errors.CommandError(
          'Some of the instances you\'d like to move have disks that are in '
          'use by other instances: (Offending instance: disks attached)\n%s' %
          (utils.ListStrings(offending_instances)))

  def _CheckForDisksInUseByOtherInstances(self, instances, disk_names):
    """Returns a list containing a mapping of instance to persistent disks.

    Args:
      instances: The set of instances to inspect.
      disk_names: The disks to look for.

    Returns:
      A list of tuples where the first element of each tuple is an instance
      name and the second element is a list of disks attached to that
      instance.
    """
    res = {}
    disk_names = set(disk_names)
    for instance in instances:
      instance_name = instance['name']
      for disk in instance.get('disks', []):
        if disk['type'] != 'PERSISTENT':
          continue
        disk_name = disk['source'].split('/')[-1]
        if disk_name in disk_names:
          if instance_name not in res:
            res[instance_name] = []
          res[instance_name].append(disk_name)
    return sorted(res.iteritems())

  def _GetPersistentDiskNames(self, instances):
    res = []
    for instance in instances:
      for disk in instance.get('disks', []):
        if disk['type'] == 'PERSISTENT':
          res.append(disk['source'].split('/')[-1])
    return res

  def _CheckDestinationZone(self):
    """Raises an exception if the destination zone is not valid."""
    print 'Checking destination zone...'
    zone_name = self._flags.destination_zone
    zone = self.api.zones.get(project=self._project, zone=zone_name).execute()
    if zone.get('status', '') != 'UP':
      raise gcutil_errors.CommandError(
          'Destination zone %s is not available.' % zone_name)

    now = datetime.datetime.utcnow()
    maintenance_window = self.GetNextMaintenanceStart(zone, now)
    if maintenance_window is not None:
      if maintenance_window <= now:
        raise gcutil_errors.CommandError(
            'Destination zone %s is in maintenance.' % zone_name)
      delta = maintenance_window - now
      if delta < datetime.timedelta(weeks=2):
        warning = 'Zone %s will enter maintenance in' % zone_name
        if delta.days:
          warning += ' %d day%s' % (
              delta.days, ('' if delta.days == 1 else 's'))
        if delta.seconds:
          if delta.days: warning += ' and'
          hours = delta.seconds / 3600
          warning += ' %d hour%s' % (hours, '' if hours == 1 else 's')
        if not self._PresentSafetyPrompt('%s. Proceed' % warning, True):
          raise gcutil_errors.CommandError('Move aborted.')

    deprecated = zone.get('deprecated')
    if deprecated and deprecated.get('state') in ('OBSOLETE', 'DELETED'):
      raise gcutil_errors.CommandError(
          'Destination zone %s is deprecated.' % zone_name)

  def _DeleteLog(self, log_path):
    """Deletes the log at log_path."""
    os.remove(log_path)

  def _WriteLog(self, log_path, instances_to_mv, snapshot_mappings,
                disktype_mappings):
    """Logs the instances that will be moved and the destination zone."""
    print 'If the move fails, you can re-attempt it using:'
    print '  gcutil --project=%s resumemove %s' % (self._project, log_path)
    with open(log_path, 'w') as f:
      contents = {'version': version.__version__,
                  'dest_zone': self._flags.destination_zone,
                  'src_zone': self._flags.source_zone,
                  'instances': instances_to_mv,
                  'snapshot_mappings': snapshot_mappings,
                  'disktype_mappings': disktype_mappings}
      json.dump(contents, f)

  def _GenerateLogPath(self):
    """Generates a file path in the form ~/.gcutil.move.YYmmddHHMMSS."""
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return os.path.join(os.path.expanduser('~'), '.gcutil.move.' + timestamp)


class ResumeMove(MoveInstancesBase):
  """Resume a previously-failed move.

  The moveinstances subcommand produces a log file that can be used to
  re-attempt a move that fails. This is intended to help complete
  moves that are interrupted by the user or by transient network
  failures.

  WARNING: Instances that are moved will lose ALL of their transient
  state (i.e., ephemeral IP addresses, and memory).
  """

  positional_args = '<log-path>'

  def __init__(self, name, flag_values):
    super(ResumeMove, self).__init__(name, flag_values)

    flags.DEFINE_boolean(
        'keep_log_file',
        False,
        'If true, the log file is not deleted at the end of the resume.',
        flag_values=flag_values)

  def _Intersect(self, resources1, resources2):
    """set(resources1) & set(resources2) based on the name field."""
    names1 = set(r['name'] for r in resources1)
    return [r for r in resources2 if r['name'] in names1]

  def _Subtract(self, resources1, resources2):
    """set(resources1) - set(resources2) based on the name field."""
    names2 = set(r['name'] for r in resources2)
    return [r for r in resources1 if r['name'] not in names2]

  def _GetKey(self, log, key):
    """Returns log[key] or raises a CommandError if key does not exist."""
    value = log.get(key)
    if value is None:
      raise gcutil_errors.CommandError(
          'The log file did not contain a %s key.' % repr(key))
    return value

  def _ParseLog(self, log_path):
    """Loads the JSON contents of the file pointed to by log_path."""
    print 'Parsing log file...'
    with open(log_path) as f:
      result = json.load(f)
    return result

  def HandleMove(self, log_path):
    """Attempts the move dictated in the given log file.

    This method first checks the current state of the project to see
    which instances have already been moved before moving the
    instances that were left behind in a previous failed move.

    The user is prompted to continue before any changes are made.

    Args:
      log_path: The path to the replay log.
    """
    if not os.path.exists(log_path):
      raise gcutil_errors.CommandError('File not found: %s' % log_path)

    log = self._ParseLog(log_path)

    src_zone = self._GetKey(log, 'src_zone')
    print 'Source zone is %s.' % src_zone

    dest_zone = self._GetKey(log, 'dest_zone')
    print 'Destination zone is %s.' % dest_zone

    snapshot_mappings = self._GetKey(log, 'snapshot_mappings')
    disktype_mappings = self._GetKey(log, 'disktype_mappings')
    instances_to_mv = self._GetKey(log, 'instances')

    instances_in_dest = utils.All(
        self.api.instances.list, self._project, zone=dest_zone)['items']
    instances_in_source = utils.All(
        self.api.instances.list, self._project, zone=src_zone)['items']

    # Note that we cannot use normal set intersection and subtraction
    # because two different instance resources could be referring to
    # the same instance (e.g., the instance was restarted by the
    # system).
    instances_to_ignore = self._Intersect(instances_to_mv, instances_in_dest)
    instances_to_mv = self._Subtract(instances_to_mv, instances_in_dest)

    if not instances_to_mv:
      raise gcutil_errors.CommandError(
          'All instances are already in %s.' % dest_zone)

    # Figures out which disks have not been moved.
    disks_in_dest = set(utils.AllNames(
        self.api.disks.list, self._project, zone=dest_zone))
    disks_in_src = set(utils.AllNames(
        self.api.disks.list, self._project, zone=src_zone))

    disks_to_mv = set(snapshot_mappings.keys()) & disks_in_src

    instances_to_delete = self._Intersect(instances_to_mv, instances_in_source)

    # For the disks that are still in the source zone, figures out
    # which ones still need to be snapshotted before being deleted.
    snapshot_mappings_for_unmoved_disks = {}
    if disks_to_mv:
      current_snapshots = utils.AllNames(
          self.api.snapshots.list, self._project)

      for disk, snapshot in snapshot_mappings.iteritems():
        if disk in disks_to_mv and snapshot not in current_snapshots:
          snapshot_mappings_for_unmoved_disks[disk] = snapshot

    # Ensures that the current quotas can support the move and prompts
    # the user for confirmation.
    self._CheckQuotas(instances_to_mv, disks_to_mv, src_zone, dest_zone,
                      snapshots_to_create=snapshot_mappings_for_unmoved_disks)
    self._Confirm(instances_to_mv, instances_to_ignore,
                  disks_to_mv, dest_zone, src_zone)

    self._TurnOffAutoDeleteForDisks(instances_to_delete, src_zone)
    self._DeleteInstances(instances_to_delete, src_zone)
    self._CreateSnapshots(snapshot_mappings_for_unmoved_disks,
                          src_zone, dest_zone)
    self._DeleteDisks(disks_to_mv, src_zone)

    # Create disks in destination zone from snapshots.
    all_snapshots = set(utils.AllNames(
        self.api.snapshots.list, self._project))
    disks_to_create = {}
    for disk, snapshot in snapshot_mappings.iteritems():
      if snapshot in all_snapshots and disk not in disks_in_dest:
        disks_to_create[disk] = snapshot
    self._CreateDisksFromSnapshots(disks_to_create,
                                   disktype_mappings, dest_zone)

    self._CreateInstances(instances_to_mv, src_zone, dest_zone)

    self._DeleteSnapshots(disks_to_create.values(), dest_zone)

    if not self._flags.keep_log_file:
      # We have succeeded, so it's safe to delete the log file.
      os.remove(log_path)


def AddCommands():
  appcommands.AddCmd('moveinstances', MoveInstances)
  appcommands.AddCmd('resumemove', ResumeMove)
