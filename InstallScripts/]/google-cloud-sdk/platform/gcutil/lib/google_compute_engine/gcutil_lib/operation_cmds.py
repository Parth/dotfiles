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

"""Commands for interacting with Google Compute Engine operations."""



from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base
from gcutil_lib import gcutil_logging
from gcutil_lib import utils

FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER


class OperationCommand(command_base.GoogleComputeCommand):
  """Base command for working with the operations collection.

  Attributes:
    print_spec: A specification describing how to print Operation resources.
    resource_collection_name: The name of the REST API collection handled by
        this command type.
  """

  print_spec = command_base.GoogleComputeCommand.operation_print_spec

  resource_collection_name = 'operations'

  def __init__(self, name, flag_values):
    super(OperationCommand, self).__init__(name, flag_values)
    flags.DEFINE_bool('global',
                      None,
                      'List global operations.',
                      flag_values=flag_values)
    flags.DEFINE_string('region',
                        None,
                        'Specifies the region for which to list operations.',
                        flag_values=flag_values)
    flags.DEFINE_string('zone',
                        None,
                        'Specifies the zone for which to list operations.',
                        flag_values=flag_values)

  def GetPrintSpec(self):
    return self.print_spec

  def _InferOperationType(self, operation_name):
    """Infer the object type from a possibly fully qualified operation name.

    Args:
      operation_name: The name of the operation.

    Returns:
      The type of operation, inferred first from path and second from flags.
    """
    inferred_object_type = self._context_parser.IdentifyObjectTypeFromPath(
        operation_name)

    if inferred_object_type:
      return inferred_object_type
    elif self._flags.zone:
      if self._flags.zone == command_base.GLOBAL_SCOPE_NAME:
        LOGGER.warn(
            '--zone \'%s\' flag is deprecated; use --global instead' %
            command_base.GLOBAL_SCOPE_NAME)
        return 'globalOperations'
      return 'zoneOperations'
    elif self._flags.region:
      return 'regionOperations'
    else:
      # If we still haven't figured out what operation type this is, then
      # operation_name is really ambiguous. Get the base name.
      operation = operation_name.split('/')[-1]

      # Search for the item in the master list of all items.
      filter_expression = ('name eq %s' % operation)

      aggregated_items = utils.AllAggregated(
          self.api.global_operations.aggregatedList, self._project,
          max_results=2, filter=filter_expression)

      for item in aggregated_items['items']:
        if 'operations' in aggregated_items['items'][item]:
          if item == 'global':
            return 'globalOperations'
          elif item.startswith('regions/'):
            return 'regionOperations'
          elif item.startswith('zones/'):
            return 'zoneOperations'

      # Complete failure to detect anything. Guess region.
      return 'globalOperations'

  def _AutoDetectZoneOrRegion(self):
    """Instruct this command to auto detect zone/region for operations."""
    def _GetScope(project, operation):
      """Get scope for operation in a specified project.

      Args:
        project:  The project.
        operation:  The operation name.

      Returns:
        Scope if detected, otherwise None.
      """

      filter_expression = ('name eq %s' % operation)

      aggregated_items = utils.AllAggregated(
          self.api.global_operations.aggregatedList, project,
          max_results=2, filter=filter_expression)

      for item in aggregated_items['items']:
        if 'operations' in aggregated_items['items'][item]:
          return item.split('/')[-1]

      # Not found.  Return none.
      return None

    def _GetZoneContext(unused_object_type, context):
      if self._flags.zone:
        return self.DenormalizeResourceName(self._flags.zone)
      else:
        return _GetScope(context['project'], context['operation'])

    def _GetRegionContext(unused_object_type, context):
      if self._flags.region:
        return self.DenormalizeResourceName(self._flags.region)
      else:
        return _GetScope(context['project'], context['operation'])

    self._context_parser.context_prompt_fxns['zone'] = _GetZoneContext
    self._context_parser.context_prompt_fxns['region'] = _GetRegionContext

  def _GetApiFromOperationType(self, operation_type):
    """Gets the api based on the operation type.

    Args:
      operation_type: The type of the operation.

    Returns:
      The relevant API.
    """
    operation_types_to_methods = {
        'globalOperations': self.api.global_operations,
        'regionOperations': self.api.region_operations,
        'zoneOperations': self.api.zone_operations
    }
    return operation_types_to_methods[operation_type]

  def _PrepareRequestArgs(self, operation_context):
    """Get the arguments for the request based on the specified context.

    Args:
      operation_context:  A context dict for this request.

    Returns:
      A dict with the required keyword args.
    """
    kwargs = {
        'project': operation_context['project'],
        'operation': operation_context['operation']
    }

    if 'zone' in operation_context:
      kwargs['zone'] = operation_context['zone']
    if 'region' in operation_context:
      kwargs['region'] = operation_context['region']

    return kwargs


class GetOperation(OperationCommand):
  """Get an operation."""

  positional_args = '<operation-name>'

  def Handle(self, operation_name):
    """Get the specified operation.

    Args:
      operation_name: The name of the operation to get.

    Returns:
      The json formatted object resulting from retrieving the operation
      resource.
    """
    # Force asynchronous mode so the caller doesn't wait for this operation
    # to complete before returning.
    self._flags.synchronous_mode = False

    self._AutoDetectZoneOrRegion()

    operation_type = self._InferOperationType(operation_name)
    api = self._GetApiFromOperationType(operation_type)
    method = api.get
    operation_context = self._context_parser.ParseContextOrPrompt(
        operation_type, operation_name)

    request = method(**self._PrepareRequestArgs(operation_context))

    return request.execute()


class DeleteOperation(OperationCommand):
  """Delete one or more operations."""

  positional_args = '<operation-name-1> ... <operation-name-n>'
  safety_prompt = 'Delete operation'

  def Handle(self, *operation_names):
    """Delete the specified operations.

    Args:
      *operation_names: The names of the operations to delete.

    Returns:
      Tuple (results, exceptions) - results of deleting the operations.
    """
    requests = []

    self._AutoDetectZoneOrRegion()

    for operation_name in operation_names:
      operation_type = self._InferOperationType(operation_name)
      api = self._GetApiFromOperationType(operation_type)
      method = api.delete
      operation_context = self._context_parser.ParseContextOrPrompt(
          operation_type, operation_name)

      request = method(**self._PrepareRequestArgs(operation_context))
      requests.append(request)

    _, exceptions = self.ExecuteRequests(requests)
    return '', exceptions


class ListOperations(OperationCommand, command_base.GoogleComputeListCommand):
  """List the operations for a project."""

  is_global_level_collection = True
  is_zone_level_collection = True

  def IsZoneLevelCollection(self):
    return True

  def IsRegionLevelCollection(self):
    return True

  def IsGlobalLevelCollection(self):
    return True

  def __init__(self, name, flag_values):
    super(ListOperations, self).__init__(name, flag_values)

  def ListFunc(self):
    """Returns the function for listing global operations."""
    return self.api.global_operations.list

  def ListRegionFunc(self):
    return self.api.region_operations.list

  def ListZoneFunc(self):
    """Returns the function for listing operations in a zone."""
    return self.api.zone_operations.list

  def ListAggregatedFunc(self):
    """Returns the function for listing operations across all scopes."""
    return self.api.global_operations.aggregatedList


def AddCommands():
  appcommands.AddCmd('getoperation', GetOperation)
  appcommands.AddCmd('deleteoperation', DeleteOperation)
  appcommands.AddCmd('listoperations', ListOperations)
