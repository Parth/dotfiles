# Copyright 2013 Google Inc. All Rights Reserved.
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

"""Commands for interacting with Google Compute Engine routes."""



from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base


FLAGS = flags.FLAGS


class RouteCommand(command_base.GoogleComputeCommand):
  """Base command for working with the routes collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'network', 'destination-range', 'priority'],
      field_mappings=(
          ('name', 'name'),
          ('network', 'network'),
          ('tags', 'tags'),
          ('destination-range', 'destRange'),
          ('next-hop-instance', 'nextHopInstance'),
          ('next-hop-ip', 'nextHopIp'),
          ('next-hop-gateway', 'nextHopGateway'),
          ('next-hop-network', 'nextHopNetwork'),
          ('priority', 'priority'),
          ('warning', 'warnings.code')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('network', 'network'),
          ('tags', 'tags'),
          ('destination-range', 'destRange'),
          ('next-hop-instance', 'nextHopInstance'),
          ('next-hop-ip', 'nextHopIp'),
          ('next-hop-gateway', 'nextHopGateway'),
          ('next-hop-network', 'nextHopNetwork'),
          ('priority', 'priority'),
          ('warning', 'warnings.code'),
          ('warning-message', 'warnings.message')),
      sort_by='name')

  resource_collection_name = 'routes'

  def __init__(self, name, flag_values):
    super(RouteCommand, self).__init__(name, flag_values)


class AddRoute(RouteCommand):
  """Create a new routing rule.

  A route is a rule that specifies how matching packets should be handled by a
  virtual network.
  """
  positional_args = '<route-name> <destination-address-range>'

  def __init__(self, name, flag_values):
    super(AddRoute, self).__init__(name, flag_values)
    flags.DEFINE_string(
        'description',
        None,
        'An optional route description.',
        flag_values=flag_values)
    flags.DEFINE_string(
        'network',
        'default',
        'Specifies which network to apply the route to. By default, this is '
        'the \'default\' network.',
        flag_values=flag_values)
    flags.DEFINE_list(
        'tags',
        [],
        'Specifies a comma-separated set of tagged instances to which the '
        'route will apply. If no tags are specified, this route applies to '
        'all instances within the specified network.',
        flag_values=flag_values)
    flags.DEFINE_integer(
        'priority',
        1000,
        'Specifies the priority of this route relative to other routes with '
        'the same specificity. The lower the number, the higher the '
        'priority. The default priority is 1000.',
        lower_bound=0,
        upper_bound=2 ** 32 - 1,
        flag_values=flag_values)
    flags.DEFINE_string(
        'next_hop_instance',
        None,
        'Specifies the name of an instance that should handle matching '
        'packets. You must provide exactly one hop, specified by one of '
        '\'--next_hop_instance\', \'--next_hop_ip\', or '
        '\'--next_hop_gateway\'. To specify \'--next_hop_instance\', '
        'provide the full URL to the instance. e.g. '
        '\'https://www.googleapis.com/compute/<api-version>/projects/'
        '<project-id>/zones/<zone-name>/instances/<instance-name>\'.',
        flag_values=flag_values)
    flags.DEFINE_string(
        'next_hop_ip',
        None,
        'Specifies the IP address of an instance that should handle '
        'matching packets. You must provide exactly one hop, specified by '
        'one of \'--next_hop_instance\', \'--next_hop_ip\', or '
        '\'--next_hop_gateway\'. To specify an IP address of an instance, '
        'the IP must already exist and have IP forwarding enabled.',
        flag_values=flag_values)
    flags.DEFINE_string(
        'next_hop_gateway',
        None,
        'Specifies the gateway that should handle matching packets. You '
        'must provide exactly one hop, specified by one of '
        '\'--next_hop_instance\', \'--next_hop_ip\', or '
        '\'--next_hop_gateway\'. Currently, you can only specify the '
        'Internet gateway: '
        '\'/projects/<project-id>/global/gateways/default-internet\'.',
        flag_values=flag_values)

  def Handle(self, route_name, dest_range):
    """Add the specified route.

    Args:
      route_name: The name of the route to add.
      dest_range: Specifies which packets will be routed by destination
                  address.

    Returns:
      The result of inserting the route.
    """

    route_context = self._context_parser.ParseContextOrPrompt('routes',
                                                              route_name)

    route_resource = {
        'kind': self._GetResourceApiKind('route'),
        'name': route_context['route'],
        'destRange': dest_range,
        'tags': self._flags.tags,
        'priority': self._flags.priority,
        }

    if self._flags.description:
      route_resource['description'] = self._flags.description

    if self._flags.network:
      route_resource['network'] = self._context_parser.NormalizeOrPrompt(
          'networks', self._flags.network)

    if self._flags.next_hop_instance:
      route_resource['nextHopInstance'] = (
          self._context_parser.NormalizeOrPrompt(
              'instances', self._flags.next_hop_instance))
    if self._flags.next_hop_ip:
      route_resource['nextHopIp'] = self._flags.next_hop_ip
    if self._flags.next_hop_gateway:
      route_resource['nextHopGateway'] = (
          self._context_parser.NormalizeOrPrompt(
              'gateways', self._flags.next_hop_gateway))

    route_request = self.api.routes.insert(project=route_context['project'],
                                           body=route_resource)
    return route_request.execute()


class GetRoute(RouteCommand):
  """Get a routing rule."""

  positional_args = '<route-name>'

  def __init__(self, name, flag_values):
    super(GetRoute, self).__init__(name, flag_values)

  def Handle(self, route_name):
    """Get the specified route.

    Args:
      route_name: The name of the route to get.

    Returns:
      The result of getting the route.
    """

    route_context = self._context_parser.ParseContextOrPrompt('routes',
                                                              route_name)

    route_request = self.api.routes.get(
        project=route_context['project'],
        route=route_context['route'])
    return route_request.execute()


class DeleteRoute(RouteCommand):
  """Delete one or more routing rules.

  Specify multiple rules as multiple arguments. Multiple rules will be
  deleted in parallel.
  """

  positional_args = '<route-name-1> ... <route-name-n>'
  safety_prompt = 'Delete route'

  def __init__(self, name, flag_values):
    super(DeleteRoute, self).__init__(name, flag_values)

  def Handle(self, *route_names):
    """Delete the specified route.

    Args:
      *route_names: The names of the routes to delete.

    Returns:
      Tuple (results, exceptions) - results of deleting the routes.
    """
    requests = []
    for name in route_names:
      route_context = self._context_parser.ParseContextOrPrompt('routes', name)

      requests.append(self.api.routes.delete(
          project=route_context['project'],
          route=route_context['route']))
    results, exceptions = self.ExecuteRequests(requests)
    return self.MakeListResult(results, 'operationList'), exceptions


class ListRoutes(RouteCommand, command_base.GoogleComputeListCommand):
  """List the routing rules for a project."""

  def ListFunc(self):
    """Returns the function for listing routes."""
    return self.api.routes.list


def AddCommands():
  appcommands.AddCmd('addroute', AddRoute)
  appcommands.AddCmd('getroute', GetRoute)
  appcommands.AddCmd('deleteroute', DeleteRoute)
  appcommands.AddCmd('listroutes', ListRoutes)
