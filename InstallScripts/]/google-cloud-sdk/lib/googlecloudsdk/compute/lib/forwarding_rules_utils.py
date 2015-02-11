# Copyright 2014 Google Inc. All Rights Reserved.
"""Common classes and functions for forwarding rules."""
import abc
import argparse
import textwrap

from googlecloudsdk.calliope import actions
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import utils
from googlecloudsdk.core import properties


class ForwardingRulesMutator(base_classes.BaseAsyncMutator):
  """Base class for modifying forwarding rules."""

  @staticmethod
  def Args(parser):
    """Adds common flags for mutating forwarding rules."""
    scope = parser.add_mutually_exclusive_group()

    utils.AddRegionFlag(
        scope,
        resource_type='forwarding rule',
        operation_type='operate on')

    global_flag = scope.add_argument(
        '--global',
        action='store_true',
        help='If provided, it is assumed the forwarding rules are global.')
    global_flag.detailed_help = """\
        If provided, assume the forwarding rules are global. A forwarding rule
        is global if it references a target HTTP proxy.
        """

  @property
  def service(self):
    if self.global_request:
      return self.compute.globalForwardingRules
    else:
      return self.compute.forwardingRules

  @property
  def resource_type(self):
    return 'forwardingRules'

  @abc.abstractmethod
  def CreateGlobalRequests(self, args):
    """Return a list of one of more globally-scoped request."""

  @abc.abstractmethod
  def CreateRegionalRequests(self, args):
    """Return a list of one of more regionally-scoped request."""

  def CreateRequests(self, args):
    self.global_request = getattr(args, 'global')

    if self.global_request:
      return self.CreateGlobalRequests(args)
    else:
      return self.CreateRegionalRequests(args)


class ForwardingRulesTargetMutator(ForwardingRulesMutator):
  """Base class for modifying forwarding rule targets."""

  @staticmethod
  def Args(parser):
    """Adds common flags for mutating forwarding rule targets."""
    ForwardingRulesMutator.Args(parser)

    target = parser.add_mutually_exclusive_group(required=True)

    target_instance = target.add_argument(
        '--target-instance',
        help='The target instance that will receive the traffic.')
    target_instance.detailed_help = textwrap.dedent("""\
        The name of the target instance that will receive the traffic. The
        target instance must be in a zone that's in the forwarding rule's
        region. Global forwarding rules may not direct traffic to target
        instances.
        """) + constants.ZONE_PROPERTY_EXPLANATION

    target_pool = target.add_argument(
        '--target-pool',
        help='The target pool that will receive the traffic.')
    target_pool.detailed_help = """\
        The target pool that will receive the traffic. The target pool
        must be in the same region as the forwarding rule. Global
        forwarding rules may not direct traffic to target pools.
        """

    target.add_argument(
        '--target-http-proxy',
        help='The target HTTP proxy that will receive the traffic.')


    # parser.add_argument('--target-vpn-gateway', help argparse.SUPPRESS)

    parser.add_argument(
        '--target-instance-zone',
        help='The zone of the target instance.',
        action=actions.StoreProperty(properties.VALUES.compute.zone))

    parser.add_argument(
        'name',
        help='The name of the forwarding rule.')

  def GetGlobalTarget(self, args):
    """Return the forwarding target for a globally scoped request."""

    if args.target_instance:
      raise exceptions.ToolException(
          'You cannot specify [--target-instance] for a global '
          'forwarding rule.')
    if args.target_pool:
      raise exceptions.ToolException(
          'You cannot specify [--target-pool] for a global '
          'forwarding rule.')

    if args.target_http_proxy:
      return self.CreateGlobalReference(
          args.target_http_proxy, resource_type='targetHttpProxies')

    if args.target_vpn_gateway:
      raise exceptions.ToolException(
          'You cannot specify [--target-vpn-gateway] for a global '
          'forwarding rule.')

  def GetRegionalTarget(self, args, forwarding_rule_ref=None):
    """Return the forwarding target for a regionally scoped request."""
    if args.target_http_proxy:
      raise exceptions.ToolException(
          'You cannot specify [--target-http-proxy] for a regional '
          'forwarding rule.')
    if args.target_instance_zone and not args.target_instance:
      raise exceptions.ToolException(
          'You cannot specify [--target-instance-zone] unless you are '
          'specifying [--target-instance].')

    if forwarding_rule_ref:
      region_arg = forwarding_rule_ref.region
    else:
      region_arg = args.region

    if args.target_pool:
      target_ref = self.CreateRegionalReference(
          args.target_pool, region_arg, resource_type='targetPools')
      target_region = target_ref.region
    elif args.target_instance:
      target_ref = self.CreateZonalReference(
          args.target_instance, args.target_instance_zone,
          resource_type='targetInstances',
          flag_names=['--target-instance-zone'],
          region_filter=region_arg)
      target_region = utils.ZoneNameToRegionName(target_ref.zone)
    elif args.target_vpn_gateway:
      target_ref = self.CreateRegionalReference(
          args.target_vpn_gateway, region_arg,
          resource_type='targetVpnGateways')
      target_region = target_ref.region

    return target_ref, target_region
