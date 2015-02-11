# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for adding a backend to a backend service."""
import copy

from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import backend_services_utils
from googlecloudsdk.compute.lib import base_classes


class AddBackend(base_classes.ReadWriteCommand):
  """Add a backend to a backend service."""

  @staticmethod
  def Args(parser):
    backend_services_utils.AddUpdatableBackendArgs(parser)
    parser.add_argument(
        'name',
        help='The name of the backend service.')

  @property
  def service(self):
    return self.compute.backendServices

  @property
  def resource_type(self):
    return 'backendServices'

  def CreateReference(self, args):
    return self.CreateGlobalReference(args.name)

  def GetGetRequest(self, args):
    return (self.service,
            'Get',
            self.messages.ComputeBackendServicesGetRequest(
                backendService=self.ref.Name(),
                project=self.project))

  def GetSetRequest(self, args, replacement, existing):
    return (self.service,
            'Update',
            self.messages.ComputeBackendServicesUpdateRequest(
                backendService=self.ref.Name(),
                backendServiceResource=replacement,
                project=self.project))

  def Modify(self, args, existing):
    replacement = copy.deepcopy(existing)

    group_ref = self.CreateZonalReference(
        args.group, args.zone, resource_type='zoneViews')
    group_uri = group_ref.SelfLink()

    for backend in existing.backends:
      if group_uri == backend.group:
        raise exceptions.ToolException(
            'Backend [{0}] in zone [{1}] already exists in backend service '
            '[{2}].'.format(args.group, args.zone, args.name))

    if args.balancing_mode:
      balancing_mode = self.messages.Backend.BalancingModeValueValuesEnum(
          args.balancing_mode)
    else:
      balancing_mode = None

    backend = self.messages.Backend(
        balancingMode=balancing_mode,
        capacityScaler=args.capacity_scaler,
        description=args.description,
        group=group_uri,
        maxRate=args.max_rate,
        maxRatePerInstance=args.max_rate_per_instance,
        maxUtilization=args.max_utilization)

    replacement.backends.append(backend)
    return replacement


AddBackend.detailed_help = {
    'brief': 'Add a backend to a backend service',
    'DESCRIPTION': """
        *{command}* is used to add a backend to a backend service. A
        backend is a group of tasks that can handle requests sent to a
        backend service. Currently, the group of tasks can be one or
        more Google Compute Engine virtual machine instances grouped
        together using a resource view.

        Traffic is first spread evenly across all virtual machines in
        the group. When the group is full, traffic is sent to the next
        nearest group(s) that still have remaining capacity.

        To modify the parameters of a backend after it has been added
        to the backend service, use 'gcloud compute backend-services
        update-backend' or 'gcloud compute backend-services edit'.
        """,
}
