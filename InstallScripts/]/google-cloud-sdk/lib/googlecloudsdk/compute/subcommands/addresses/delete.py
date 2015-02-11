# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deleting addresses."""

from googlecloudsdk.compute.lib import addresses_utils
from googlecloudsdk.compute.lib import utils


class Delete(addresses_utils.AddressesMutator):
  """Release reserved IP addresses."""

  @staticmethod
  def Args(parser):
    addresses_utils.AddressesMutator.Args(parser)

    parser.add_argument(
        'names',
        metavar='NAME',
        nargs='+',
        help='The names of the addresses to delete.')

  @property
  def method(self):
    return 'Delete'

  def CreateGlobalRequests(self, args):
    """Create a globally scoped request."""

    address_refs = self.CreateGlobalReferences(
        args.names, resource_type='globalAddresses')
    utils.PromptForDeletion(address_refs)
    requests = []
    for address_ref in address_refs:
      request = self.messages.ComputeGlobalAddressesDeleteRequest(
          address=address_ref.Name(),
          project=self.project,
      )
      requests.append(request)

    return requests

  def CreateRegionalRequests(self, args):
    """Create a regionally scoped request."""

    address_refs = (
        self.CreateRegionalReferences(args.names, args.region))
    utils.PromptForDeletion(address_refs, scope_name='region')
    requests = []
    for address_ref in address_refs:
      request = self.messages.ComputeAddressesDeleteRequest(
          address=address_ref.Name(),
          project=self.project,
          region=address_ref.region,
      )
      requests.append(request)

    return requests


Delete.detailed_help = {
    'brief': 'Release reserved IP addresses',
    'DESCRIPTION': """\
        *{command}* releases one or more Google Compute Engine IP addresses.
        """,
}
