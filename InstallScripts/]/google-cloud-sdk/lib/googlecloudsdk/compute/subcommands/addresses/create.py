# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for reserving IP addresses."""
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import addresses_utils
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import name_generator


class Create(base_classes.ListOutputMixin, addresses_utils.AddressesMutator):
  """Reserve IP addresses."""

  @staticmethod
  def Args(parser):
    addresses_utils.AddressesMutator.Args(parser)

    addresses = parser.add_argument(
        '--addresses',
        metavar='ADDRESS',
        nargs='+',
        help='Ephemeral IP addresses to promote to reserved status.')
    addresses.detailed_help = """\
        Ephemeral IP addresses to promote to reserved status. Only addresses
        that are being used by resources in the project can be promoted. When
        providing this flag, a parallel list of names for the addresses can
        be provided. For example,

          $ {command} ADDRESS-1 ADDRESS-2 --addresses 162.222.181.197 162.222.181.198 --region us-central1

        will result in 162.222.181.197 being reserved as
        'ADDRESS-1' and 162.222.181.198 as 'ADDRESS-2'. If
        no names are given, randomly-generated names will be assigned
        to the IP addresses.
        """

    parser.add_argument(
        '--description',
        help='An optional textual description for the addresses.')

    parser.add_argument(
        'names',
        metavar='NAME',
        nargs='*',
        help='The names to assign to the reserved IP addresses.')

  @property
  def method(self):
    return 'Insert'

  def GetNamesAndAddresses(self, args):
    """Returns names and addresses provided in args."""
    if not args.addresses and not args.names:
      raise exceptions.ToolException(
          'At least one name or address must be provided.')

    if args.names:
      names = args.names
    else:
      # If we dont have any names then we must some addresses.
      names = [name_generator.GenerateRandomName() for _ in args.addresses]

    if args.addresses:
      addresses = args.addresses
    else:
      # If we dont have any addresses then we must some names.
      addresses = [None] * len(args.names)

    if len(addresses) != len(names):
      raise exceptions.ToolException(
          'If providing both, you must specify the same number of names as '
          'addresses.')

    return names, addresses

  def CreateGlobalRequests(self, args):
    names, addresses = self.GetNamesAndAddresses(args)
    address_refs = self.CreateGlobalReferences(
        names, resource_type='globalAddresses')

    requests = []
    for address, address_ref in zip(addresses, address_refs):
      request = self.messages.ComputeGlobalAddressesInsertRequest(
          address=self.messages.Address(
              address=address,
              description=args.description,
              name=address_ref.Name(),
          ),
          project=self.project)
      requests.append(request)

    return requests

  def CreateRegionalRequests(self, args):
    names, addresses = self.GetNamesAndAddresses(args)
    address_refs = self.CreateRegionalReferences(names, args.region)

    requests = []
    for address, address_ref in zip(addresses, address_refs):
      request = self.messages.ComputeAddressesInsertRequest(
          address=self.messages.Address(
              address=address,
              description=args.description,
              name=address_ref.Name(),
          ),
          project=self.project,
          region=address_ref.region)
      requests.append(request)

    return requests


Create.detailed_help = {
    'brief': 'Reserve IP addresses',
    'DESCRIPTION': """\
        *{command}* is used to reserve one or more IP addresses. Once
        an IP address is reserved, it will be associated with the
        project until it is released using 'gcloud compute addresses
        delete'. Ephemeral IP addresses that are in use by resources
        in the project, can be reserved using the ``--addresses''
        flag.
        """,
    'EXAMPLES': """\
        To reserve three IP addresses in the ``us-central1'' region,
        run:

          $ {command} ADDRESS-1 ADDRESS-2 ADDRESS-3 --region us-central1

        To reserve ephemeral IP addresses 162.222.181.198 and
        23.251.146.189 which are being used by virtual machine
        instances in the ``us-central1'' region, run:

          $ {command} --addresses 162.222.181.198 23.251.146.189 --region us-central1

        In the above invocation, the two addresses will be assigned
        random names.
        """,
}
