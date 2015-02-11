# Copyright 2014 Google Inc. All Rights Reserved.
"""Common classes and functions for addresses."""
import abc
import socket

from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import request_helper
from googlecloudsdk.compute.lib import utils


class AddressesMutator(base_classes.BaseAsyncMutator):
  """Base class for modifying addresses."""

  @staticmethod
  def Args(parser):
    """Adds common flags for mutating addresses."""
    scope = parser.add_mutually_exclusive_group()

    utils.AddRegionFlag(
        scope,
        resource_type='address',
        operation_type='operate on')

    scope.add_argument(
        '--global',
        action='store_true',
        help='If provided, it is assumed the addresses are global.')

  @property
  def service(self):
    if self.global_request:
      return self.compute.globalAddresses
    else:
      return self.compute.addresses

  @property
  def resource_type(self):
    return 'addresses'

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


class AddressExpander(object):
  """Mixin class for expanding address names to IP address."""

  def GetAddress(self, address_ref):
    """Returns the address resource corresponding to the given reference."""
    errors = []
    res = list(request_helper.MakeRequests(
        requests=[(self.compute.addresses,
                   'Get',
                   self.messages.ComputeAddressesGetRequest(
                       address=address_ref.Name(),
                       project=address_ref.project,
                       region=address_ref.region))],
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None))
    if errors:
      utils.RaiseToolException(
          errors,
          error_message='Could not fetch address resource:')
    return res[0]

  def ExpandAddressFlag(self, args, region):
    """Resolves the --address flag value.

    If the value of --address is a name, the regional address is queried.

    Args:
      args: The command-line flags. The flag accessed is --address.
      region: The region.

    Returns:
      If an --address is given, the resolved IP address; otherwise None.
    """
    if not args.address:
      return None

    # Try interpreting the address as IPv4 first, then IPv6.
    try:
      socket.inet_aton(args.address)
      return args.address
    except socket.error:
      pass

    try:
      socket.inet_pton(socket.AF_INET6, args.address)
      return args.address
    except socket.error:
      pass

    # Lookup the address.
    address_ref = self.CreateRegionalReference(
        args.address, region, resource_type='addresses')
    res = self.GetAddress(address_ref)
    return res.address
