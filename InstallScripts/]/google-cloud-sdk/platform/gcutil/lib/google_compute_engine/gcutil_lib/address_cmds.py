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

"""Commands for interacting with Google Compute Engine reserved addresses."""




from google.apputils import app
from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_logging


FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER


class AddressCommand(command_base.GoogleComputeCommand):
  """Base command for working with the addresses collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'region', 'status', 'ip'],
      field_mappings=(
          ('name', 'name'),
          ('description', 'description'),
          ('region', 'region'),
          ('status', 'status'),
          ('ip', 'address')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('region', 'region'),
          ('status', 'status'),
          ('ip', 'address')),
      sort_by='name')

  resource_collection_name = 'addresses'

  def __init__(self, name, flag_values):
    super(AddressCommand, self).__init__(name, flag_values)

    flags.DEFINE_string('region',
                        None,
                        '[Required] The region for this request.',
                        flag_values=flag_values)

  def GetDetailRow(self, result):
    """Returns an associative list of items for display in a detail table.

    Args:
      result: A dict returned by the server.

    Returns:
      A list.
    """
    data = []
    users = []
    if 'users' in result:
      for user in result['users']:
        users.append(self.DenormalizeResourceName(user))
    data.append(('users', users))
    return data

  def _PrepareRequestArgs(self, address_context, **other_args):
    """Gets the dictionary of API method keyword arguments.

    Args:
      address_context: Context dict for this address, including region and name.
      **other_args: Keyword arguments that should be included in the request.

    Returns:
      Dictionary of keyword arguments that should be passed in the API call,
      includes all keyword arguments passed in 'other_args' plus
      common keys such as the name of the resource and the project.
    """

    kwargs = {
        'project': address_context['project'],
        'address': self.DenormalizeResourceName(address_context['address'])
    }
    if address_context['region']:
      kwargs['region'] = address_context['region']
    for key, value in other_args.items():
      kwargs[key] = value
    return kwargs

  def _AutoDetectRegion(self):
    """Instruct this command to auto detect region instead of prompting."""
    def _GetRegionContext(unused_object_type, context):
      if self._flags.region:
        return self.DenormalizeResourceName(self._flags.region)
      return self.GetRegionForResource(self.api.addresses,
                                       context['address'])

    self._context_parser.context_prompt_fxns['region'] = _GetRegionContext


class ReserveAddress(AddressCommand):
  """Reserve a new IP address."""

  positional_args = '<address-name>'

  def __init__(self, name, flag_values):
    super(ReserveAddress, self).__init__(name, flag_values)
    flags.DEFINE_string('description',
                        '',
                        'An optional description for this address.',
                        flag_values=flag_values)
    flags.DEFINE_string('source_address',
                        None,
                        'If promoting an in-use ephemeral IP address, specify '
                        'that address here. ',
                        flag_values=flag_values)
    flags.DEFINE_boolean('wait_until_complete',
                         False,
                         'Specifies that gcutil should wait until the '
                         'address is successfully reserved before returning',
                         flag_values=flag_values)

  def Handle(self, address_name):
    """Reserve the specified address.

    Args:
      address_name: The name of the address to add.

    Returns:
      The result of the reservation request.

    Raises:
      CommandError: If the command is unsupported in this API version.
      UsageError: If no address name is specified.
    """
    if not address_name:
      raise app.UsageError('Please specify an address name.')

    address_context = self._context_parser.ParseContextOrPrompt('addresses',
                                                                address_name)

    kind = self._GetResourceApiKind('address')

    kwargs = {'region': address_context['region']}

    address = {
        'kind': kind,
        'name': address_context['address'],
        'description': self._flags.description,
        }

    if self._flags.source_address is not None:
      address['address'] = self._flags.source_address

    request = self.api.addresses.insert(project=address_context['project'],
                                        body=address, **kwargs)

    if self._flags.wait_until_complete and not self._flags.synchronous_mode:
      LOGGER.warn('wait_until_complete specified. Implying synchronous_mode.')
      self._flags.synchronous_mode = True

    return request.execute()


class GetAddress(AddressCommand):
  """Get a reserved IP address."""

  positional_args = '<address-name>'

  def __init__(self, name, flag_values):
    super(GetAddress, self).__init__(name, flag_values)

  def Handle(self, address_name):
    """Get the specified address.

    Args:
      address_name: The name of the address to get

    Returns:
      The result of getting the address.

    Raises:
      CommandError: If the command is unsupported in this API version.
      UsageError: If no address name is specified.
    """
    if not address_name:
      raise app.UsageError('Please specify an address name.')

    self._AutoDetectRegion()

    address_context = self._context_parser.ParseContextOrPrompt('addresses',
                                                                address_name)

    address_request = self.api.addresses.get(
        **self._PrepareRequestArgs(address_context))
    return address_request.execute()


class ReleaseAddress(AddressCommand):
  """Release one or more reserved IP addresses.

  If multiple address names are specified, the addresses will be released in
  parallel.
  """

  positional_args = '<address-name-1> ... <address-name-n>'
  safety_prompt = 'Release address'

  def __init__(self, name, flag_values):
    super(ReleaseAddress, self).__init__(name, flag_values)

  def Handle(self, *address_names):
    """Delete the specified addresses.

    Args:
      *address_names: The names of the addresses to release.

    Returns:
      Tuple (results, exceptions) - results of deleting the addresses.
    """
    requests = []

    self._AutoDetectRegion()

    for name in address_names:
      address_context = self._context_parser.ParseContextOrPrompt('addresses',
                                                                  name)
      requests.append(self.api.addresses.delete(
          project=address_context['project'],
          region=address_context['region'],
          address=address_context['address']))
    results, exceptions = self.ExecuteRequests(requests)
    return (self.MakeListResult(results, 'operationList'), exceptions)


class ListAddresses(AddressCommand, command_base.GoogleComputeListCommand):
  """List the IP addresses for a project."""

  def IsZoneLevelCollection(self):
    return False

  def IsRegionLevelCollection(self):
    return True

  def IsGlobalLevelCollection(self):
    return False

  def __init__(self, name, flag_values):
    super(ListAddresses, self).__init__(name, flag_values)

  def ListFunc(self):
    """Returns the function for listing addresses."""
    return None

  def ListRegionFunc(self):
    """Returns the function for listing addresses in a region."""
    return self.api.addresses.list

  def ListAggregatedFunc(self):
    """Returns the function for listing addresses across all regions."""
    return self.api.addresses.aggregatedList


def AddCommands():
  appcommands.AddCmd('reserveaddress', ReserveAddress)
  appcommands.AddCmd('getaddress', GetAddress)
  appcommands.AddCmd('releaseaddress', ReleaseAddress)
  appcommands.AddCmd('listaddresses', ListAddresses)
