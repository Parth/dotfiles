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

"""Commands for interacting with Google Compute Engine VM networks."""





from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base


FLAGS = flags.FLAGS


class NetworkCommand(command_base.GoogleComputeCommand):
  """Base command for working with the networks collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'addresses', 'gateway'],
      field_mappings=(
          ('name', 'name'),
          ('description', 'description'),
          ('addresses', 'IPv4Range'),
          ('gateway', 'gatewayIPv4')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('addresses', 'IPv4Range'),
          ('gateway', 'gatewayIPv4')),
      sort_by='name')

  resource_collection_name = 'networks'

  def __init__(self, name, flag_values):
    super(NetworkCommand, self).__init__(name, flag_values)


class AddNetwork(NetworkCommand):
  """Create a new virtual network."""

  positional_args = '<network-name>'

  def __init__(self, name, flag_values):
    super(AddNetwork, self).__init__(name, flag_values)

    flags.DEFINE_string('description',
                        '',
                        'An optional network description.',
                        flag_values=flag_values)
    flags.DEFINE_string('range',
                        '10.0.0.0/8',
                        'Specifies the IPv4 address range of this network. '
                        'By default, this is \'10.0.0.0/8\'.',
                        flag_values=flag_values)
    flags.DEFINE_string('gateway',
                        None,
                        'Specifies the IPv4 address of the gateway within '
                        'the network. This is by default the first address in '
                        'the range that does not end with \'.0\'.',
                        flag_values=flag_values)

  def Handle(self, network_name):
    """Add the specified network.

    Args:
      network_name: The name of the network to add.

    Returns:
      The result of adding the network.
    """
    network_context = self._context_parser.ParseContextOrPrompt('networks',
                                                                network_name)

    network_resource = {
        'kind': self._GetResourceApiKind('network'),
        'name': network_context['network'],
        'description': self._flags.description,
        'IPv4Range': self._flags.range,
        }

    if self._flags.gateway:
      network_resource['gatewayIPv4'] = self._flags.gateway

    network_request = self.api.networks.insert(
        project=network_context['project'], body=network_resource)

    return network_request.execute()


class GetNetwork(NetworkCommand):
  """Get a virtual network."""

  positional_args = '<network-name>'

  def __init__(self, name, flag_values):
    super(GetNetwork, self).__init__(name, flag_values)

  def Handle(self, network_name):
    """Get the specified network.

    Args:
      network_name: The name of the network to get.

    Returns:
      The result of getting the network.
    """
    network_context = self._context_parser.ParseContextOrPrompt('networks',
                                                                network_name)

    network_request = self.api.networks.get(
        project=network_context['project'],
        network=network_context['network'])

    return network_request.execute()


class DeleteNetwork(NetworkCommand):
  """Delete one or more virtual networks.

  If multiple network names are specified, the networks will be deleted in
  parallel.
  """

  positional_args = '<network-name-1> ... <network-name-n>'
  safety_prompt = 'Delete network'

  def __init__(self, name, flag_values):
    super(DeleteNetwork, self).__init__(name, flag_values)

  def Handle(self, *network_names):
    """Delete the specified networks.

    Args:
      *network_names: The names of the networks to delete.

    Returns:
      Tuple (results, exceptions) - results of deleting the networks.
    """
    requests = []
    for network_name in network_names:
      network_context = self._context_parser.ParseContextOrPrompt('networks',
                                                                  network_name)
      requests.append(self.api.networks.delete(
          project=network_context['project'],
          network=network_context['network']))
    results, exceptions = self.ExecuteRequests(requests)
    return self.MakeListResult(results, 'operationList'), exceptions


class ListNetworks(NetworkCommand, command_base.GoogleComputeListCommand):
  """List the virtual networks for a project."""

  def ListFunc(self):
    return self.api.networks.list


def AddCommands():
  appcommands.AddCmd('addnetwork', AddNetwork)
  appcommands.AddCmd('getnetwork', GetNetwork)
  appcommands.AddCmd('deletenetwork', DeleteNetwork)
  appcommands.AddCmd('listnetworks', ListNetworks)
