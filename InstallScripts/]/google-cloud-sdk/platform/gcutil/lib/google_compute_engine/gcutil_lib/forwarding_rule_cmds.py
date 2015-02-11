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

"""Commands for interacting with Google Compute Engine forwarding rules."""



from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_logging
from gcutil_lib import version

FLAGS = flags.FLAGS


def _AddTargetFlags(flags_module, flag_values):
  """Add command line flags to commands that require a target flag.

  Args:
    flags_module: flags module.
    flag_values: The command line flags for this command.
  """
  flags_module.DEFINE_string('target',
                             None,
                             '[Deprecated] Specifies the name of a TargetPool '
                             'resource to handle rule-matched network traffic. '
                             'The target pool must exist before you can use it '
                             'for a forwarding rule. You can only specify one '
                             'target pool per forwarding rule.',
                             flag_values=flag_values)
  flags_module.DEFINE_string('target_pool',
                             None,
                             'Specifies the name of the TargetPool '
                             'resource to handle rule-matched network traffic. '
                             'The target pool must exist before you can use it '
                             'for a forwarding rule. You must specify only '
                             'one of --target_pool or --target_instance.',
                             flag_values=flag_values)
  flags_module.DEFINE_string('target_instance',
                             None,
                             'Specifies the name of the TargetInstance '
                             'resource to handle rule-matched network traffic. '
                             'The target instance must exist before you can use'
                             ' it for a forwarding rule. You must specify only '
                             'one of --target_pool or --target_instance.',
                             flag_values=flag_values)


class ForwardingRuleCommand(command_base.GoogleComputeCommand):
  """Base command for working with the forwarding rule collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'region', 'ip'],
      field_mappings=(
          ('name', 'name'),
          ('description', 'description'),
          ('region', 'region'),
          ('ip', 'IPAddress'),
          ('protocol', 'IPProtocol'),
          ('port-range', 'portRange'),
          ('target', 'target')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('region', 'region'),
          ('ip', 'IPAddress'),
          ('protocol', 'IPProtocol'),
          ('port-range', 'portRange'),
          ('target', 'target')),
      sort_by='name')

  resource_collection_name = 'forwardingRules'

  # The default IP protocol.
  DEFAULT_IP_PROTOCOL = 'TCP'

  def __init__(self, name, flag_values):
    super(ForwardingRuleCommand, self).__init__(name, flag_values)
    flags.DEFINE_string('region',
                        None,
                        '[Required] The region for this request.',
                        flag_values=flag_values)

  def _PrepareRequestArgs(self, forwarding_rule_context):
    """Gets the dictionary of API method keyword arguments.

    Args:
      forwarding_rule_context: Context dict for a forwarding rule.

    Returns:
      Dictionary of keyword arguments that should be passed in the API call.
    """

    kwargs = {
        'project': forwarding_rule_context['project'],
        'forwardingRule': forwarding_rule_context['forwardingRule'],
        'region': forwarding_rule_context['region']
    }

    return kwargs

  def _VerifyAndGetTargetFromFlags(
      self, target_pool_flag, target_instance_flag):
    """Gets forwarding rule target from flag values.

    Args:
      target_pool_flag: the value of --target_pool flag
      target_instance_flag: the value of --target_instance flag
    Returns:
      (target_pool, target_instance) pair, with one and only one field set.
    """
    if (target_pool_flag is None) == (target_instance_flag is None):
      raise gcutil_errors.CommandError('Please specify exactly one of '
                                       '--target_pool or --target_instance.')
    elif target_pool_flag:
      return target_pool_flag, None
    else:
      if self.api.version < version.get('v1'):
        raise gcutil_errors.CommandError(
            'Version does not support target instance.')
      return None, target_instance_flag

  def _AutoDetectRegion(self):
    """Instruct this command to auto detect region instead of prompting."""
    def _GetRegionContext(object_type, context):
      if self._flags.region:
        return self.DenormalizeResourceName(self._flags.region)
      if object_type == 'forwardingRules':
        return self.GetRegionForResource(self.api.forwarding_rules,
                                         context['forwardingRule'],
                                         project=context['project'])
      elif object_type == 'targetPools':
        return self.GetRegionForResource(self.api.target_pools,
                                         context['targetPool'],
                                         project=context['project'])

    self._context_parser.context_prompt_fxns['region'] = _GetRegionContext

  def _AutoDetectRegionForTargetPoolsOnly(self):
    """Instruct this command to auto detect region for target pools only."""
    def _GetRegionContext(object_type, context):
      if self._flags.region:
        return self.DenormalizeResourceName(self._flags.region)

      if object_type == 'targetPools':
        return self.GetRegionForResource(self.api.target_pools,
                                         context['targetPool'],
                                         project=context['project'])
      else:
        return self._presenter.PromptForRegion(self.api.regions)['name']

    self._context_parser.context_prompt_fxns['region'] = _GetRegionContext

  def _AutoDetectZoneForTargetInstancesOnly(self):
    """Instruct this command to auto-detect zone for target instances only."""
    def _GetZoneContext(object_type, context):
      if object_type == 'targetInstances':
        return self.GetZoneForResource(self.api.target_instances,
                                       context['targetInstance'],
                                       project=context['project'])
      else:
        return self._presenter.PromptForZone(self.api.zones)['name']

    self._context_parser.context_prompt_fxns['zone'] = _GetZoneContext

  def _BuildForwardingRuleTarget(self):
    """Parses commandline flags and constructs a target resource.

    Returns:
      the target resource configured to receive forwarded traffic
    """
    target_pool = None
    target_instance = None
    if self._flags.target:
      gcutil_logging.LOGGER.warn(
          '--target flag is deprecated. Use --target_pool instead.')
      target_pool = self._flags.target
    else:
      target_pool, target_instance = self._VerifyAndGetTargetFromFlags(
          self._flags.target_pool, self._flags.target_instance)

    self._AutoDetectRegion()
    self._AutoDetectZoneForTargetInstancesOnly()

    if target_pool:
      return self._context_parser.NormalizeOrPrompt(
          'targetPools', target_pool)
    else:
      return self._context_parser.NormalizeOrPrompt(
          'targetInstances', target_instance)


class AddForwardingRule(ForwardingRuleCommand):
  """Create a new forwarding rule to handle network load balancing."""

  positional_args = '<forwarding-rule-name>'

  def __init__(self, name, flag_values):
    super(AddForwardingRule, self).__init__(name, flag_values)
    flags.DEFINE_string('description',
                        '',
                        'An optional forwarding rule description.',
                        flag_values=flag_values)
    flags.DEFINE_string('ip',
                        '',
                        'Specifies the IP address for which this '
                        'forwarding rule applies. The default value is '
                        '\'ephemeral\' which indicates that the service '
                        'should use any available ephemeral IP address. If '
                        'you want to explicitly use a certain IP, the IP '
                        'must be reserved by the project and not in use by '
                        'another resource.',
                        flag_values=flag_values)
    flags.DEFINE_string('protocol',
                        self.DEFAULT_IP_PROTOCOL,
                        'Specifies the IP protocol for which this rule '
                        'applies. Valid values are \'TCP\' and \'UDP\'. The '
                        'default value is \'TCP\'.',
                        flag_values=flag_values)
    flags.DEFINE_string('port_range',
                        '',
                        'Specifies the port range of packets that will be '
                        'forwarded to the target pool. Only packets '
                        'addressed to ports in this range will be forwarded. '
                        'Can be a single port (e.g. \'--port_range=80\') or '
                        'a single range (e.g \'--port=8000-9000\'). If no '
                        'ports are specified, the forwarding rule sends all '
                        'traffic from ports for the specified protocol, to '
                        'the specified target pool.',
                        flag_values=flag_values)
    _AddTargetFlags(flags, flag_values)

  def Handle(self, forwarding_rule_name):
    """Add the specified forwarding rule.

    Args:
      forwarding_rule_name: The name of the forwarding rule to add.

    Returns:
      The result of inserting the forwarding rule.
    """

    forwarding_rule_context = self._context_parser.ParseContextOrPrompt(
        'forwardingRules', forwarding_rule_name)

    forwarding_rule_resource = {
        'kind': self._GetResourceApiKind('forwardingRule'),
        'name': forwarding_rule_context['forwardingRule'],
        'description': self._flags.description,
        'IPAddress': self._flags.ip,
        'IPProtocol': self._flags.protocol,
        'portRange': self._flags.port_range,
        }

    forwarding_rule_resource['target'] = (self._BuildForwardingRuleTarget())

    kwargs = {'region': forwarding_rule_context['region']}

    forwarding_rule_request = (self.api.forwarding_rules.insert(
        project=forwarding_rule_context['project'],
        body=forwarding_rule_resource, **kwargs))
    return forwarding_rule_request.execute()


class SetForwardingRuleTarget(ForwardingRuleCommand):
  """Set the target of an existing forwarding rule."""

  positional_args = '<forwarding-rule-name>'

  def __init__(self, name, flag_values):
    super(SetForwardingRuleTarget, self).__init__(name, flag_values)
    _AddTargetFlags(flags, flag_values)

  def Handle(self, forwarding_rule_name):
    """Set the specified target pool as a target.

    Args:
      forwarding_rule_name: The name of the forwarding rule to update.

    Returns:
      The result of inserting the forwarding rule.
    """

    forwarding_rule_context = self._context_parser.ParseContextOrPrompt(
        'forwardingRules', forwarding_rule_name)

    kwargs = self._PrepareRequestArgs(forwarding_rule_context)
    forwarding_rule_resource = {}
    forwarding_rule_resource['target'] = (self._BuildForwardingRuleTarget())

    forwarding_rule_request = self.api.forwarding_rules.setTarget(
        body=forwarding_rule_resource, **kwargs)
    return forwarding_rule_request.execute()


class GetForwardingRule(ForwardingRuleCommand):
  """Get a forwarding rule."""

  positional_args = '<forwarding-rule-name>'

  def __init__(self, name, flag_values):
    super(GetForwardingRule, self).__init__(name, flag_values)

  def Handle(self, forwarding_rule_name):
    """Get the specified forwarding rule.

    Args:
      forwarding_rule_name: The name of the forwarding rule to get.

    Returns:
      The result of getting the forwarding rule.
    """
    self._AutoDetectRegion()

    forwarding_rule_context = self._context_parser.ParseContextOrPrompt(
        'forwardingRules', forwarding_rule_name)

    kwargs = self._PrepareRequestArgs(forwarding_rule_context)

    forwarding_rule_request = self.api.forwarding_rules.get(**kwargs)

    return forwarding_rule_request.execute()


class DeleteForwardingRule(ForwardingRuleCommand):
  """Delete one or more forwarding rule.

  Specify multiple forwarding rules as multiple arguments. The forwarding
  rules will be deleted in parallel.
  """

  positional_args = '<forwarding-rule-name-1> ... <forwarding-rule-name-n>'
  safety_prompt = 'Delete forwarding rule'

  def __init__(self, name, flag_values):
    super(DeleteForwardingRule, self).__init__(name, flag_values)

  def Handle(self, *forwarding_rule_names):
    """Delete the specified forwarding rules.

    Args:
      *forwarding_rule_names: The names of the forwarding rules to delete.

    Returns:
      Tuple (results, exceptions) - results of deleting the forwarding rules.
    """
    self._AutoDetectRegion()

    requests = []
    for name in forwarding_rule_names:
      forwarding_rule_context = self._context_parser.ParseContextOrPrompt(
          'forwardingRules', name)
      requests.append(self.api.forwarding_rules.delete(
          **self._PrepareRequestArgs(forwarding_rule_context)))
    results, exceptions = self.ExecuteRequests(requests)
    return (self.MakeListResult(results, 'operationList'), exceptions)


class ListForwardingRules(ForwardingRuleCommand,
                          command_base.GoogleComputeListCommand):
  """List the forwarding rule for a project."""

  def IsZoneLevelCollection(self):
    return False

  def IsRegionLevelCollection(self):
    return True

  def IsGlobalLevelCollection(self):
    return False

  def __init__(self, name, flag_values):
    super(ListForwardingRules, self).__init__(name, flag_values)

  def ListFunc(self):
    """Returns the function for listing addresses."""
    return None

  def ListRegionFunc(self):
    """Returns the function for listing addresses in a region."""
    return self.api.forwarding_rules.list

  def ListAggregatedFunc(self):
    """Returns the function for listing forwarding rules across all regions."""
    return self.api.forwarding_rules.aggregatedList


def AddCommands():
  appcommands.AddCmd('addforwardingrule', AddForwardingRule)
  appcommands.AddCmd('getforwardingrule', GetForwardingRule)
  appcommands.AddCmd('deleteforwardingrule', DeleteForwardingRule)
  appcommands.AddCmd('listforwardingrules', ListForwardingRules)
  appcommands.AddCmd('setforwardingruletarget', SetForwardingRuleTarget)
