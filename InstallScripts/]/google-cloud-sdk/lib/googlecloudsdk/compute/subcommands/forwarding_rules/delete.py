# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deleting forwarding rules."""

from googlecloudsdk.compute.lib import forwarding_rules_utils
from googlecloudsdk.compute.lib import utils


class Delete(forwarding_rules_utils.ForwardingRulesMutator):
  """Delete forwarding rules."""

  @staticmethod
  def Args(parser):
    forwarding_rules_utils.ForwardingRulesMutator.Args(parser)

    parser.add_argument(
        'names',
        metavar='NAME',
        nargs='+',
        help='The names of the forwarding rules to delete.')

  @property
  def method(self):
    return 'Delete'

  def CreateGlobalRequests(self, args):
    """Create a globally scoped request."""

    forwarding_rule_refs = self.CreateGlobalReferences(
        args.names, resource_type='globalForwardingRules')
    utils.PromptForDeletion(forwarding_rule_refs)
    requests = []
    for forwarding_rule_ref in forwarding_rule_refs:
      request = self.messages.ComputeGlobalForwardingRulesDeleteRequest(
          forwardingRule=forwarding_rule_ref.Name(),
          project=self.project,
      )
      requests.append(request)

    return requests

  def CreateRegionalRequests(self, args):
    """Create a regionally scoped request."""

    forwarding_rule_refs = (
        self.CreateRegionalReferences(
            args.names, args.region, flag_names=['--region', '--global']))
    utils.PromptForDeletion(forwarding_rule_refs, scope_name='region')
    requests = []
    for forwarding_rule_ref in forwarding_rule_refs:
      request = self.messages.ComputeForwardingRulesDeleteRequest(
          forwardingRule=forwarding_rule_ref.Name(),
          project=self.project,
          region=forwarding_rule_ref.region,
      )
      requests.append(request)

    return requests


Delete.detailed_help = {
    'brief': 'Delete forwarding rules',
    'DESCRIPTION': """\
        *{command}* deletes one or more Google Compute Engine forwarding rules.
        """,
}
