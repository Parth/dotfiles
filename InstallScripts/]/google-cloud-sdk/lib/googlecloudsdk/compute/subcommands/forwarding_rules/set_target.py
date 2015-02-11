# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for modifying the target of forwarding rules."""

from googlecloudsdk.compute.lib import forwarding_rules_utils as utils


class Set(utils.ForwardingRulesTargetMutator):
  """Modify a forwarding rule to direct network traffic to a new target."""

  @staticmethod
  def Args(parser):
    utils.ForwardingRulesTargetMutator.Args(parser)

  @property
  def method(self):
    return 'SetTarget'

  def CreateGlobalRequests(self, args):
    """Create a globally scoped request."""

    forwarding_rule_ref = self.CreateGlobalReference(
        args.name, resource_type='globalForwardingRules')
    target_ref = self.GetGlobalTarget(args)

    request = self.messages.ComputeGlobalForwardingRulesSetTargetRequest(
        forwardingRule=forwarding_rule_ref.Name(),
        project=self.project,
        targetReference=self.messages.TargetReference(
            target=target_ref.SelfLink(),
        ),
    )

    return [request]

  def CreateRegionalRequests(self, args):
    """Create a regionally scoped request."""

    forwarding_rule_ref = self.CreateRegionalReference(
        args.name, args.region, flag_names=['--region', '--global'])
    target_ref, _ = self.GetRegionalTarget(args, forwarding_rule_ref)

    request = self.messages.ComputeForwardingRulesSetTargetRequest(
        forwardingRule=forwarding_rule_ref.Name(),
        project=self.project,
        region=forwarding_rule_ref.region,
        targetReference=self.messages.TargetReference(
            target=target_ref.SelfLink(),
        ),
    )

    return [request]

Set.detailed_help = {
    'brief': ('Modify a forwarding rule to direct network traffic to a new '
              'target'),
    'DESCRIPTION': """\
        *{command}* is used to set a new target for a forwarding rule.
        Forwarding rules match and direct certain types of traffic to a load
        balancer which is controlled by a target pool, a target instance,
        or a target HTTP proxy. Target pools and target instances perform load
        balancing at the layer 3 of the OSI networking model
        (link:http://en.wikipedia.org/wiki/Network_layer[]). Target
        HTTP proxies perform load balancing at layer 7.

        Forwarding rules can be either regional or global. They are
        regional if they point to a target pool or a target instance
        and global if they point to a target HTTP proxy.

        For more information on load balancing, see
        link:https://developers.google.com/compute/docs/load-balancing/[].

        When modifying a forwarding rule, exactly one of  ``--target-instance''
        ``--target-pool'', and ``--target-http-proxy'' must be specified.
        """,
}
