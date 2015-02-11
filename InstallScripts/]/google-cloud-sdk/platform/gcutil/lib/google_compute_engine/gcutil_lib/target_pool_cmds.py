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

"""Commands for interacting with Google Compute Engine target pools."""



from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_flags
from gcutil_lib import gcutil_logging
from gcutil_lib import version

FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER


class TargetPoolCommand(command_base.GoogleComputeCommand):
  """Base command for working with the target pool collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'region'],
      field_mappings=(
          ('name', 'name'),
          ('description', 'description'),
          ('region', 'region')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('health-checks', 'healthChecks'),
          ('session-affinity', 'sessionAffinity'),
          ('failover-ratio', 'failoverRatio'),
          ('backup-pool', 'backupPool')
          ),
      sort_by='name')

  resource_collection_name = 'targetPools'

  # The default session affinity option
  DEFAULT_SESSION_AFFINITY = 'NONE'

  def __init__(self, name, flag_values):
    super(TargetPoolCommand, self).__init__(name, flag_values)
    flags.DEFINE_string('region',
                        None,
                        '[Required] The region for this request.',
                        flag_values=flag_values)

  def _PrepareRequestArgs(self, target_pool_context):
    """Gets the dictionary of API method keyword arguments.

    Args:
      target_pool_context:  A context dict for the desired target pool.

    Returns:
      Dictionary of keyword arguments that should be passed in the API call.
    """

    kwargs = {
        'project': target_pool_context['project'],
        'targetPool': target_pool_context['targetPool'],
        'region': target_pool_context['region'],
    }
    return kwargs

  def _AutoDetectZoneForInstances(self):
    """Instruct this command to auto detect zone instead of prompting."""
    def _GetZoneContext(object_type, context):
      if object_type == 'instances':
        return self.GetZoneForResource(self.api.instances,
                                       context['instance'],
                                       project=context['project'])

    self._context_parser.context_prompt_fxns['zone'] = _GetZoneContext

  def _AutoDetectRegion(self):
    """Instruct this command to auto detect region instead of prompting."""
    def _GetRegionContext(unused_object_type, context):
      if self._flags.region:
        return self.DenormalizeResourceName(self._flags.region)
      return self.GetRegionForResource(self.api.target_pools,
                                       context['targetPool'],
                                       project=context['project'])

    self._context_parser.context_prompt_fxns['region'] = _GetRegionContext

  def ParseZoneInstancePair(self, zone_instance):
    """Parses an element of the --instance flag for this command.

    Args:
      zone_instance: The instances as specified in the flag.

    Returns:
      A list of <zone, instance> pairs.

    Raises:
      ValueError: If zone_instance is invalid.
    """
    zone_instance_pair = zone_instance.split('/')

    # Invalid pair.
    if len(zone_instance_pair) != 2:
      raise ValueError('Invalid value for instance: %s' % zone_instance)

    LOGGER.warn('The <zone>/<instance> short form is deprecated. '
                'Please use a relative or fully-qualified path, such as '
                '<zone>/instances/<instance>.')

    return zone_instance_pair


class AddTargetPool(TargetPoolCommand):
  """Create a new target pool to handle network load balancing."""

  positional_args = '<target-pool-name>'

  def __init__(self, name, flag_values):
    super(AddTargetPool, self).__init__(name, flag_values)
    flags.DEFINE_string('description',
                        '',
                        'An optional Target Pool description',
                        flag_values=flag_values)
    flags.DEFINE_list('health_checks',
                      [],
                      'Specifies a HttpHealthCheck resource to use to '
                      'determine the health of VMs in this pool. '
                      'If no health check is specified, traffic will be '
                      'sent to all instances in this target pool as if the '
                      'instances were healthy, but the health status of this '
                      'pool will appear as unhealthy as a warning that this '
                      'target pool does not have a health check.',
                      flag_values=flag_values)
    flags.DEFINE_list('instances',
                      [],
                      '[Required] Specifies a list of instances that will '
                      'receive traffic directed to this target pool. Each '
                      'entry must be specified by the instance name '
                      '(e.g., \'--instances=myinstance\') or a relative or '
                      'fully-qualified path to the instance (e.g., '
                      '\'--instances=<zone>/instances/myotherinstance\'). To '
                      'specify multiple instances, provide them as '
                      'comma-separated entries. All instances in one target '
                      'pool must belong to the same region as the target pool. '
                      'Instances do not need to exist at the time the target '
                      'pool is created and can be created afterwards.',
                      flag_values=flag_values)
    gcutil_flags.DEFINE_case_insensitive_enum(
        'session_affinity',
        self.DEFAULT_SESSION_AFFINITY,
        ['NONE', 'CLIENT_IP', 'CLIENT_IP_PROTO'],
        'Specifies the session affinity option for the '
        'connection. Options include:'
        '\n NONE: connections from the same client IP '
        'may go to any VM in the target pool '
        '\n CLIENT_IP: connections from the same client IP '
        'will go to the same VM in the target pool; '
        '\n CLIENT_IP_PROTO: connections from the same '
        'client IP with the same IP protocol will go to the '
        'same VM in the targetpool. ',
        flag_values=flag_values)
    flags.DEFINE_float('failover_ratio',
                       None,
                       'If set, --backup_pool must also be set to point to an '
                       'existing target pool in the same region. They together '
                       'define the fallback behavior of the target pool '
                       '(primary pool) to be created by this command: if the '
                       'ratio of the healthy VMs in the primary pool is at '
                       'or below this number, traffic arriving at the '
                       'load-balanced IP will be directed to the backup pool. '
                       'If not set, the traaffic will be directed the VMs in '
                       'this pool in the "force" mode, where traffic will be '
                       'spread to the healthy VMs with the best effort, or '
                       'to all VMs when no VM is healthy.',
                       flag_values=flag_values)
    flags.DEFINE_string('backup_pool',
                        None,
                        'Together with --failover_ratio, this flag defines '
                        'the fallback behavior of the target pool '
                        '(primary pool) to be created by this command: if the '
                        'ratio of the healthy VMs in the primary pool is at '
                        'or below --failover_ratio, traffic arriving at the '
                        'load-balanced IP will be directed to the backup '
                        'pool. ',
                        flag_values=flag_values)

  def Handle(self, target_pool_name):
    """Add the specified target pool.

    Args:
      target_pool_name: The name of the target pool to add.

    Returns:
      The result of inserting the target pool.
    """

    self._AutoDetectZoneForInstances()

    target_pool_context = self._context_parser.ParseContextOrPrompt(
        'targetPools', target_pool_name)

    # Under no circumstance should we prompt for region again if we already
    # have. If it was otherwise specified in a fully qualified path,
    # assume that that's what the user meant for the backupPool.
    if not self._flags.region:
      self._flags.region = target_pool_context['region']

    target_pool_resource = {
        'kind': self._GetResourceApiKind('targetPool'),
        'name': target_pool_context['targetPool'],
        'description': self._flags.description,
        }

    target_pool_resource['sessionAffinity'] = self._flags.session_affinity
    if (self._flags['failover_ratio'].present !=
        self._flags['backup_pool'].present):
      raise gcutil_errors.CommandError('--failover_ratio and --backup_pool '
                                       'must be either both set or both not '
                                       'set.')
    if self._flags.failover_ratio:
      target_pool_resource['failoverRatio'] = self._flags.failover_ratio

      if self._flags.backup_pool:
        backup_pool = self._context_parser.NormalizeOrPrompt(
            'targetPools', self._flags.backup_pool)
        target_pool_resource['backupPool'] = backup_pool

    health_checks = []
    for health_check in self._flags.health_checks:
      health_checks.append(self._context_parser.NormalizeOrPrompt(
          'httpHealthChecks', health_check))
    target_pool_resource['healthChecks'] = health_checks

    instances = []
    for zone_instance in self._flags.instances:
      try:
        path = self._context_parser.NormalizeOrPrompt(
            'instances', zone_instance)
      except ValueError:
        zone, instance = self.ParseZoneInstancePair(zone_instance)
        path = self.NormalizePerZoneResourceName(
            self._project, zone, 'instances', instance)

      instances.append(path)

    target_pool_resource['instances'] = instances

    kwargs = {'region': target_pool_context['region']}

    target_pool_request = (self.api.target_pools.insert(
        project=target_pool_context['project'], body=target_pool_resource,
        **kwargs))

    return target_pool_request.execute()


class AddTargetPoolInstance(TargetPoolCommand):
  """Add VM instances to an existing target pool."""

  positional_args = '<target-pool-name>'

  def __init__(self, name, flag_values):
    super(AddTargetPoolInstance, self).__init__(name, flag_values)
    flags.DEFINE_string('instance',
                        None,
                        '[Deprecated]. Please use --instances to add one or '
                        'more instances to the target pool. Must match '
                        'the pattern [<zone>/]<instance>".',
                        flag_values=flag_values)

    flags.DEFINE_list('instances',
                      [],
                      '[Required] Specifies a list of instances add to this '
                      'target pool. Each entry must be specified by the '
                      'instance name (e.g., \'--instances=<instance>\') or '
                      'by a relative or fully-qualified path to the instance  '
                      '(e.g., \'--instances=<zone>/instances/<instance>\'). To '
                      'specify multiple instances, provide them as '
                      'comma-separated entries. All instances in one target '
                      'pool must belong to the same region as the target '
                      'pool. Instances do not need to exist at the time it '
                      'is added to the target pool and can be created '
                      'afterwards.',
                      flag_values=flag_values)

  def Handle(self, target_pool_name):
    """Add the instance to the target pool.

    Args:
      target_pool_name: The name of the target_pool to update.

    Returns:
      The result of adding an instance to the target_pool.
    """
    self._AutoDetectZoneForInstances()

    target_pool_context = self._context_parser.ParseContextOrPrompt(
        'targetPools', target_pool_name)

    if not self._flags.instances and not self._flags.instance:
      raise gcutil_errors.CommandError('Please specify --instances.')
    if self._flags.instance:
      gcutil_logging.LOGGER.warn(
          '--instance flag is deprecated; use --instances to add one or more'
          ' instances')
      instances = [self._flags.instance]
    else:
      instances = self._flags.instances
    requests = []
    kwargs = self._PrepareRequestArgs(target_pool_context)
    instance_urls = []
    for zone_instance in instances:
      try:
        path = self._context_parser.NormalizeOrPrompt(
            'instances', zone_instance)
      except ValueError:
        zone, instance = self.ParseZoneInstancePair(zone_instance)
        path = self.NormalizePerZoneResourceName(
            self._project, zone, 'instances', instance)

      instance_urls.append(path)

    add_instance_request_resource = {
        'instances': [{'instance': instance_url} for instance_url in
                      instance_urls]
        }
    requests.append(self.api.target_pools.addInstance(
        body=add_instance_request_resource, **kwargs))

    # This may be multiple API calls.
    return self.ExecuteRequests(requests)


class AddTargetPoolHealthCheck(TargetPoolCommand):
  """Add a health check to an existing target pool."""

  positional_args = '<target-pool-name>'

  def __init__(self, name, flag_values):
    super(AddTargetPoolHealthCheck, self).__init__(name, flag_values)
    flags.DEFINE_string('health_check',
                        None,
                        '[Required] Specifies the healthCheck resource to '
                        'add to the target pool. For example, '
                        '\'--health_check=myhealthcheck\'.',
                        flag_values=flag_values)

  def Handle(self, target_pool_name):
    """Add the health check to the target pool.

    Args:
      target_pool_name: The name of the target_pool to update.

    Returns:
      The result of adding the health check to the target_pool.
    """
    self._AutoDetectRegion()

    target_pool_context = self._context_parser.ParseContextOrPrompt(
        'targetPools', target_pool_name)

    if self._flags.health_check is None:
      raise gcutil_errors.CommandError('Please specify a --health_check.')

    health_check = self._context_parser.NormalizeOrPrompt(
        'httpHealthChecks', self._flags.health_check)

    target_pool_resource = {
        'healthChecks': [{'healthCheck': health_check}],
        }
    kwargs = self._PrepareRequestArgs(target_pool_context)
    target_pool_request = self.api.target_pools.addHealthCheck(
        body=target_pool_resource, **kwargs)
    return target_pool_request.execute()


class GetTargetPool(TargetPoolCommand):
  """Get a target pool."""

  positional_args = '<target-pool-name>'

  def __init__(self, name, flag_values):
    super(GetTargetPool, self).__init__(name, flag_values)

  def GetDetailRow(self, result):
    """Returns an associative list of items for display in a detail table.

    Args:
      result: A dict returned by the server.

    Returns:
      A list.
    """
    instances = result.get('instances', [])
    if instances:
      return [('instances',
               [self._presenter.PresentElement(i) for i in instances])]
    else:
      return []

  def Handle(self, target_pool_name):
    """Get the specified target pool.

    Args:
      target_pool_name: The name of the target pool to get.

    Returns:
      The result of getting the target pool.
    """
    self._AutoDetectRegion()

    target_pool_context = self._context_parser.ParseContextOrPrompt(
        'targetPools', target_pool_name)

    target_pool_request = self.api.target_pools.get(
        **self._PrepareRequestArgs(target_pool_context))

    return target_pool_request.execute()


class GetTargetPoolHealth(TargetPoolCommand):
  """Get the health status of a VM instance in a target pool."""

  positional_args = '<target-pool-name>'

  def PrintResult(self, result):
    """Result printing for this type.

    Args:
      result: json dictionary returned by the server

    Returns: None.
    """

    items = result.get('items', [])
    status_list = []
    for item in items:
      status_list += item.get('healthStatus', [])

    merged_result = {'healthStatus': status_list}

    t = self._CreateFormatter()
    # Print instance-ip tuple and it's healthy state one per row.
    t.SetColumns(('instance', 'ip', 'health-state'))
    for hs in merged_result.get('healthStatus', []):
      t.AppendRow((
          self._presenter.PresentElement(hs.get('instance',
                                                'missing instance')),
          hs.get('ipAddress', 'missing ip'),
          hs.get('healthState', 'missing health state')))
    t.Write()

  def __init__(self, name, flag_values):
    super(GetTargetPoolHealth, self).__init__(name, flag_values)
    flags.DEFINE_list('instances',
                      [],
                      'Specifies the list of instance resources in a target '
                      'pool to query for health status. Each entry must be '
                      'specified by the instance name (e.g., '
                      '\'--instances=<instance>\') or a relatively or fully '
                      'qualified path to the instance instance (e.g., '
                      '\'--instances=<zone>/instances/<instance>\'). To specify'
                      ' multiple instances, provide them as comma-separated '
                      'entries. If empty, gcutil will query the status of '
                      'each instance in the pool by doing an API call for '
                      'each instance.',
                      flag_values=flag_values)

  def _GetInstancesFromPool(self, target_pool_context):
    """Fetch the list of instances in a target pool.

    Args:
      target_pool_context: A context dict for the desired target pool.

    Returns:
      List of full instance URLs.
    """
    target_pool_request = self.api.target_pools.get(
        **self._PrepareRequestArgs(target_pool_context))
    response = target_pool_request.execute()
    return response.get('instances', [])

  def _GetInstancesFromFlag(self):
    """Convert the --instances flag into normalized instance URLs.

    Returns:
      List of full instance URLs.
    """
    instances = []
    for instance_name in self._flags.instances:
      instances.append(self._context_parser.NormalizeOrPrompt(
          'instances', instance_name))

    return instances

  def Handle(self, target_pool_name):
    """Get the health of specified instances or all of them in the target pool.

    Args:
      target_pool_name: The name of the target_pool used to make health request.

    Returns:
      The result of health request to the target_pool.
    """
    self._AutoDetectRegion()
    self._AutoDetectZoneForInstances()

    target_pool_context = self._context_parser.ParseContextOrPrompt(
        'targetPools', target_pool_name)

    if self._flags.instances:
      instances = self._GetInstancesFromFlag()
    else:
      # This is one API call.
      instances = self._GetInstancesFromPool(target_pool_context)

    kwargs = self._PrepareRequestArgs(target_pool_context)
    requests = []
    for instance in instances:
      health_request_resource = {'instance': instance}
      requests.append(self.api.target_pools.getHealth(
          body=health_request_resource, **kwargs))

    # This may be multiple API calls.
    return self.ExecuteRequests(requests)


class DeleteTargetPool(TargetPoolCommand):
  """Delete one or more target pools.

  If multiple target pool names are specified, the target pool
  will be deleted in parallel.
  """

  positional_args = '<target-pool-name-1> ... <target-pool-name-n>'
  safety_prompt = 'Delete target pool'

  def __init__(self, name, flag_values):
    super(DeleteTargetPool, self).__init__(name, flag_values)

  def Handle(self, *target_pool_names):
    """Delete the specified target pools.

    Args:
      *target_pool_names: The names of the target pools to delete.

    Returns:
      Tuple (results, exceptions) - results of deleting the target pools.
    """

    self._AutoDetectRegion()

    requests = []
    for name in target_pool_names:
      target_pool_context = self._context_parser.ParseContextOrPrompt(
          'targetPools', name)
      requests.append(self.api.target_pools.delete(
          **self._PrepareRequestArgs(target_pool_context)))
    results, exceptions = self.ExecuteRequests(requests)
    return (self.MakeListResult(results, 'operationList'), exceptions)


class RemoveTargetPoolInstance(TargetPoolCommand):
  """Remove a VM instance from a target pool."""

  positional_args = '<target-pool-name>'

  def __init__(self, name, flag_values):
    super(RemoveTargetPoolInstance, self).__init__(name, flag_values)
    flags.DEFINE_string('instance',
                        None,
                        '[Deprecated]. Please use --instances to remove one or '
                        'more instances from the target pool.',
                        flag_values=flag_values)

    flags.DEFINE_list('instances',
                      [],
                      '[Required] Specifies a list of instances to be removed '
                      'this target pool. Each entry must be specified by the '
                      'instance name (e.g., \'--instances=<instance>\') or '
                      'a relatively or fully qualified path '
                      '(e.g., \'--instances=<zone>/instances/<instance>\'). To '
                      'specify multiple instances, provide them as '
                      'comma-separated entries. All instances in one target '
                      'pool must belong to the same region as the target '
                      'pool. Instances do not need to exist at the time it '
                      'is added to the target pool and can be created '
                      'afterwards.',
                      flag_values=flag_values)

  def Handle(self, target_pool_name):
    """Remove the instance from the target pool.

    Args:
      target_pool_name: The name of the target_pool to update.

    Returns:
      The result of removing an instance from the target_pool.
    """
    self._AutoDetectRegion()
    self._AutoDetectZoneForInstances()

    target_pool_context = self._context_parser.ParseContextOrPrompt(
        'targetPools', target_pool_name)

    if not self._flags.instances and not self._flags.instance:
      raise gcutil_errors.CommandError('Please specify --instances.')
    if self._flags.instance:
      gcutil_logging.LOGGER.warn(
          '--instance flag is deprecated; use --instances to remove one or more'
          ' instances')
      instances = [self._flags.instance]
    else:
      instances = self._flags.instances
    requests = []
    kwargs = self._PrepareRequestArgs(target_pool_context)
    instance_urls = []
    for zone_instance in instances:
      try:
        path = self._context_parser.NormalizeOrPrompt(
            'instances', zone_instance)
      except ValueError:
        zone, instance = self.ParseZoneInstancePair(zone_instance)
        path = self.NormalizePerZoneResourceName(
            self._project, zone, 'instances', instance)

      instance_urls.append(path)

    remove_instance_request_resource = {
        'instances': [{'instance': instance_url} for instance_url in
                      instance_urls]
        }
    requests.append(self.api.target_pools.removeInstance(
        body=remove_instance_request_resource, **kwargs))

    # This may be multiple API calls.
    return self.ExecuteRequests(requests)


class RemoveTargetPoolHealthCheck(TargetPoolCommand):
  """Remove a health check from a target pool."""

  positional_args = '<target-pool-name>'

  def __init__(self, name, flag_values):
    super(RemoveTargetPoolHealthCheck, self).__init__(name, flag_values)
    flags.DEFINE_string('health_check',
                        None,
                        '[Required] Specifies the healthCheck resource to '
                        'remove. For example, '
                        '\'--health_check=myhealthcheck\'.',
                        flag_values=flag_values)

  def Handle(self, target_pool_name):
    """Remove the health check from the target pool.

    Args:
      target_pool_name: The name of the target_pool to update.

    Returns:
      The result of removing the health check from the target_pool.
    """
    self._AutoDetectRegion()

    target_pool_context = self._context_parser.ParseContextOrPrompt(
        'targetPools', target_pool_name)

    if self._flags.health_check is None:
      raise gcutil_errors.CommandError('Please specify a --health_check.')

    health_check = self._context_parser.NormalizeOrPrompt(
        'httpHealthChecks', self._flags.health_check)

    target_pool_resource = {
        'healthChecks': [{'healthCheck': health_check}]
        }

    kwargs = self._PrepareRequestArgs(target_pool_context)
    target_pool_request = self.api.target_pools.removeHealthCheck(
        body=target_pool_resource, **kwargs)
    return target_pool_request.execute()


class ListTargetPools(TargetPoolCommand,
                      command_base.GoogleComputeListCommand):
  """List the target pools for a project."""

  def IsZoneLevelCollection(self):
    return False

  def IsRegionLevelCollection(self):
    return True

  def IsGlobalLevelCollection(self):
    return False

  def __init__(self, name, flag_values):
    super(ListTargetPools, self).__init__(name, flag_values)

  def ListFunc(self):
    """Returns the function for listing target pools."""
    return None

  def ListRegionFunc(self):
    """Returns the function for listing target pools in a region."""
    return self.api.target_pools.list

  def ListAggregatedFunc(self):
    """Returns the function for listing target pools across all regions."""
    return self.api.target_pools.aggregatedList


class SetTargetPoolBackup(TargetPoolCommand):
  """Set the backup pool of an existing target pool."""

  positional_args = '<target-pool-name>'

  def __init__(self, name, flag_values):
    super(SetTargetPoolBackup, self).__init__(name, flag_values)
    flags.DEFINE_float('failover_ratio',
                       None,
                       '--failover_ratio and --backup_pool must either be '
                       'both set or not set. If not set, existing failover '
                       'ratio will be removed from the target pool, which will '
                       'disable the fallback behavior of the primary target '
                       'pool. If set, the failover ratio of the primary target '
                       'pool will be replaced by this value.',
                       flag_values=flag_values)
    flags.DEFINE_string('backup_pool',
                        None,
                        '--backup_pool and --failover_ratio must either be '
                        'both set or not set. If not set, existing backup '
                        'pool will be removed from the target pool, which will '
                        'disable the fallback behavior of the primary target '
                        'pool. If set, the backup pool of the primary target '
                        'pool will be replaced by this value.',
                        flag_values=flag_values)

  def Handle(self, target_pool_name):
    """Set the backup pool and failover ratio for the target pool.

    Args:
      target_pool_name: The name of the target pool to update.

    Returns:
      The result of inserting the forwarding rule.
    """
    self._AutoDetectRegion()

    target_pool_context = self._context_parser.ParseContextOrPrompt(
        'targetPools', target_pool_name)

    if (self._flags['failover_ratio'].present !=
        self._flags['backup_pool'].present):
      raise gcutil_errors.CommandError('--failover_ratio and --backup_pool '
                                       'must be either both set or both not '
                                       'set.')

    kwargs = self._PrepareRequestArgs(target_pool_context)

    request_body = {}
    if self._flags.backup_pool:
      kwargs['failoverRatio'] = self._flags.failover_ratio
      backup_pool = self._context_parser.NormalizeOrPrompt(
          'targetPools', self._flags.backup_pool)
      request_body['target'] = backup_pool

    set_backup_request = self.api.target_pools.setBackup(
        body=request_body, **kwargs)
    return set_backup_request.execute()


def AddCommands():
  """Add all of the target pool related commands."""
  appcommands.AddCmd('addtargetpool', AddTargetPool)
  appcommands.AddCmd('addtargetpoolhealthcheck', AddTargetPoolHealthCheck)
  appcommands.AddCmd('addtargetpoolinstance', AddTargetPoolInstance)
  appcommands.AddCmd('gettargetpool', GetTargetPool)
  appcommands.AddCmd('gettargetpoolhealth', GetTargetPoolHealth)
  appcommands.AddCmd('deletetargetpool', DeleteTargetPool)
  appcommands.AddCmd('removetargetpoolinstance', RemoveTargetPoolInstance)
  appcommands.AddCmd('removetargetpoolhealthcheck', RemoveTargetPoolHealthCheck)
  appcommands.AddCmd('listtargetpools', ListTargetPools)
  appcommands.AddCmd('settargetpoolbackup', SetTargetPoolBackup)
