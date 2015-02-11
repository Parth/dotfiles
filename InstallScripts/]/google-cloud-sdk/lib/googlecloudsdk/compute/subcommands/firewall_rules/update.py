# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for updating firewall rules."""

from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import firewalls_utils


class UpdateFirewall(base_classes.ReadWriteCommand):
  """Update a firewall rule."""

  @staticmethod
  def Args(parser):
    allow = parser.add_argument(
        '--allow',
        nargs='*',
        metavar=firewalls_utils.ALLOWED_METAVAR,
        help='The list of IP protocols and ports which will be allowed.')
    allow.detailed_help = """\
        A list of protocols and ports whose traffic will be allowed. Setting
        this will override the current values.

        ``PROTOCOL'' is the IP protocol whose traffic will be allowed.
        ``PROTOCOL'' can be either the name of a well-known protocol
        (e.g., ``tcp'' or ``icmp'') or the IP protocol number.
        A list of IP protocols can be found at
        link:http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml[].

        A port or port range can be specified after ``PROTOCOL'' to
        allow traffic through specific ports. If no port or port range
        is specified, connections through all ranges are allowed. For
        example, the following will create a rule that allows TCP traffic
        through port 80 and allows ICMP traffic:

          $ {command} MY-RULE --allow tcp:80 icmp

        TCP and UDP rules must include a port or port range.
        """

    parser.add_argument(
        '--description',
        help=('A textual description for the firewall rule. Set to an empty '
              'string to clear existing description.'))

    source_ranges = parser.add_argument(
        '--source-ranges',
        metavar='CIDR_RANGE',
        nargs='*',
        help=('A list of IP address blocks that may make inbound connections '
              'in CIDR format.'))
    source_ranges.detailed_help = """\
        A list of IP address blocks that are allowed to make inbound
        connections that match the firewall rule to the instances on
        the network. The IP address blocks must be specified in CIDR
        format:
        link:http://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing[].
        Setting this will override the existing source ranges for the firewall.
        The following will clear the existing source ranges:

          $ {command} MY-RULE --source-ranges
        """

    source_tags = parser.add_argument(
        '--source-tags',
        metavar='TAG',
        nargs='*',
        help=('A list of instance tags indicating the set of instances on the '
              'network which may accept inbound connections that match the '
              'firewall rule.'))
    source_tags.detailed_help = """\
        A list of instance tags indicating the set of instances on the
        network which may accept inbound connections that match the
        firewall rule. If omitted, all instances on the network can
        receive inbound connections that match the rule.

        Tags can be assigned to instances during instance creation.
        Setting this will override the existing source tags for the firewall.
        The following will clear the existing source tags:

          $ {command} MY-RULE --source-tags
        """

    target_tags = parser.add_argument(
        '--target-tags',
        metavar='TAG',
        nargs='*',
        help=('A list of instance tags indicating the set of instances on the '
              'network which may make network connections that match the '
              'firewall rule.'))
    target_tags.detailed_help = """\
        A list of instance tags indicating the set of instances on the
        network which may make network connections that match the
        firewall rule. If omitted, all instances on the network can
        make connections that match the rule.

        Tags can be assigned to instances during instance creation.
        Setting this will override the existing target tags for the firewall.
        The following will clear the existing target tags:

          $ {command} MY-RULE --target-tags
        """

    parser.add_argument(
        'name',
        help='The name of the firewall rule to update.')

  @property
  def service(self):
    return self.compute.firewalls

  @property
  def resource_type(self):
    return 'firewalls'

  def CreateReference(self, args):
    return self.CreateGlobalReference(args.name, resource_type='firewalls')

  def Run(self, args):
    self.new_allowed = firewalls_utils.ParseAllowed(args.allow, self.messages)
    args_unset = (args.allow is None
                  and args.description is None
                  and args.source_ranges is None
                  and args.source_tags is None
                  and args.target_tags is None)

    if args_unset:
      raise calliope_exceptions.ToolException(
          'At least one property must be modified.')

    return super(UpdateFirewall, self).Run(args)

  def GetGetRequest(self, args):
    """Returns the request for the existing Firewall resource."""
    return (self.service,
            'Get',
            self.messages.ComputeFirewallsGetRequest(
                firewall=self.ref.Name(),
                project=self.project))

  def GetSetRequest(self, args, replacement, existing):
    return (self.service,
            'Update',
            self.messages.ComputeFirewallsUpdateRequest(
                firewall=replacement.name,
                firewallResource=replacement,
                project=self.project))

  def Modify(self, args, existing):
    """Returns a modified Firewall message."""
    if args.allow is None:
      allowed = existing.allowed
    else:
      allowed = self.new_allowed

    if args.description:
      description = args.description
    elif args.description is None:
      description = existing.description
    else:
      description = None

    if args.source_ranges:
      source_ranges = args.source_ranges
    elif args.source_ranges is None:
      source_ranges = existing.sourceRanges
    else:
      source_ranges = []

    if args.source_tags:
      source_tags = args.source_tags
    elif args.source_tags is None:
      source_tags = existing.sourceTags
    else:
      source_tags = []

    if args.target_tags:
      target_tags = args.target_tags
    elif args.target_tags is None:
      target_tags = existing.targetTags
    else:
      target_tags = []

    new_firewall = self.messages.Firewall(
        name=existing.name,
        allowed=allowed,
        description=description,
        network=existing.network,
        sourceRanges=source_ranges,
        sourceTags=source_tags,
        targetTags=target_tags,
    )

    return new_firewall


UpdateFirewall.detailed_help = {
    'brief': 'Update a firewall rule',
    'DESCRIPTION': """\
        *{command}* is used to update firewall rules that allow incoming
        traffic to a network. Only arguments passed in will be updated on the
        firewall rule.  Other attributes will remain unaffected.
        """,
}
