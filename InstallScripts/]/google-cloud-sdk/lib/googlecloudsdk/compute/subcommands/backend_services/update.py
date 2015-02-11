# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for updating backend services."""
import copy

from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import backend_services_utils
from googlecloudsdk.compute.lib import base_classes


class Update(base_classes.ReadWriteCommand):
  """Update a backend service."""

  @staticmethod
  def Args(parser):
    backend_services_utils.AddUpdatableArgs(
        parser,
        default_protocol=None,
        default_timeout=None)

    parser.add_argument(
        'name',
        help='The name of the backend service to update.')

  @property
  def service(self):
    return self.compute.backendServices

  @property
  def resource_type(self):
    return 'backendServices'

  def CreateReference(self, args):
    return self.CreateGlobalReference(args.name)

  def GetGetRequest(self, args):
    return (
        self.service,
        'Get',
        self.messages.ComputeBackendServicesGetRequest(
            project=self.project,
            backendService=self.ref.Name()))

  def GetSetRequest(self, args, replacement, _):
    return (
        self.service,
        'Update',
        self.messages.ComputeBackendServicesUpdateRequest(
            project=self.project,
            backendService=self.ref.Name(),
            backendServiceResource=replacement))

  def Modify(self, args, existing):
    replacement = copy.deepcopy(existing)

    if args.description:
      replacement.description = args.description
    elif args.description is not None:
      replacement.description = None

    health_checks = backend_services_utils.GetHealthChecks(args, self)
    if health_checks:
      replacement.healthChecks = health_checks

    if args.timeout:
      replacement.timeoutSec = args.timeout

    if args.port:
      replacement.port = args.port

    if args.port_name:
      replacement.portName = args.port_name

    if args.protocol:
      replacement.protocol = (self.messages.BackendService
                              .ProtocolValueValuesEnum(args.protocol))

    return replacement

  def Run(self, args):
    if not any([
        args.protocol,
        args.description is not None,
        args.http_health_checks,
        args.timeout is not None,
        args.port,
        args.port_name,
    ]):
      raise exceptions.ToolException('At least one property must be modified.')

    return super(Update, self).Run(args)


Update.detailed_help = {
    'brief': 'Update a backend service',
    'DESCRIPTION': """
        *{command}* is used to update backend services.
        """,
}
