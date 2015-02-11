# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for creating firewall rules."""

from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import firewalls_utils


class Create(base_classes.BaseAsyncCreator):
  """Create Google Compute Engine firewall rules."""

  @staticmethod
  def Args(parser):
    allow = parser.add_argument(
        '--allow',
        nargs='+',
        metavar=firewalls_utils.ALLOWED_METAVAR,
        help='The list of IP protocols and ports which will be allowed.',
        required=True)
    allow.detailed_help = """\
        A list of protocols and ports whose traffic will be allowed.

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
        help='An optional, textual description for the firewall rule.')

    network = parser.add_argument(
        '--network',
        default='default',
        help='The network to which this rule is attached.')
    network.detailed_help = """\
        The network to which this rule is attached. If omitted, the
        rule is attached to the ``default'' network.
        """

    source_ranges = parser.add_argument(
        '--source-ranges',
        default=[],
        metavar='CIDR_RANGE',
        nargs='+',
        help=('A list of IP address blocks that may make inbound connections '
              'in CIDR format.'))
    source_ranges.detailed_help = """\
        A list of IP address blocks that are allowed to make inbound
        connections that match the firewall rule to the instances on
        the network. The IP address blocks must be specified in CIDR
        format:
        link:http://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing[].
        If neither --source-ranges nor --source-tags is provided, then this
        flag will default to ``0.0.0.0/0'', allowing all sources. Multiple IP
        address blocks can be specified if they are separated by spaces.
        """

    source_tags = parser.add_argument(
        '--source-tags',
        default=[],
        metavar='TAG',
        nargs='+',
        help=('A list of instance tags indicating the set of instances on the '
              'network which may accept inbound connections that match the '
              'firewall rule.'))
    source_tags.detailed_help = """\
        A list of instance tags indicating the set of instances on the
        network which may accept inbound connections that match the
        firewall rule. If omitted, all instances on the network can
        receive inbound connections that match the rule.

        Tags can be assigned to instances during instance creation.
        """

    target_tags = parser.add_argument(
        '--target-tags',
        default=[],
        metavar='TAG',
        nargs='+',
        help=('A list of instance tags indicating the set of instances on the '
              'network which may make network connections that match the '
              'firewall rule.'))
    target_tags.detailed_help = """\
        A list of instance tags indicating the set of instances on the
        network which may make network connections that match the
        firewall rule. If omitted, all instances on the network can
        make connections that match the rule.

        Tags can be assigned to instances during instance creation.
        """

    parser.add_argument(
        'name',
        help='The name of the firewall rule to create.')

  @property
  def service(self):
    return self.compute.firewalls

  @property
  def method(self):
    return 'Insert'

  @property
  def resource_type(self):
    return 'firewalls'

  def CreateRequests(self, args):
    """Returns a list of requests necessary for adding firewall rules."""
    if not args.source_ranges and not args.source_tags:
      args.source_ranges = ['0.0.0.0/0']

    allowed = firewalls_utils.ParseAllowed(args.allow, self.messages)

    network_ref = self.CreateGlobalReference(
        args.network, resource_type='networks')
    firewall_ref = self.CreateGlobalReference(
        args.name, resource_type='firewalls')

    request = self.messages.ComputeFirewallsInsertRequest(
        firewall=self.messages.Firewall(
            allowed=allowed,
            name=firewall_ref.Name(),
            description=args.description,
            network=network_ref.SelfLink(),
            sourceRanges=args.source_ranges,
            sourceTags=args.source_tags,
            targetTags=args.target_tags),
        project=self.project)
    return [request]


Create.detailed_help = {
    'brief': 'Create a Google Compute Engine firewall rule',
    'DESCRIPTION': """\
        *{command}* is used to create firewall rules to allow incoming
        traffic to a network.
        """,
}
