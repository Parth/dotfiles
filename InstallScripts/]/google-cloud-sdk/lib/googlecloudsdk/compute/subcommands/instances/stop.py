# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for stopping an instance."""
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import utils


class Stop(base_classes.NoOutputAsyncMutator):
  """Stop a virtual machine instance."""

  @staticmethod
  def Args(parser):
    utils.AddZoneFlag(
        parser,
        resource_type='instance',
        operation_type='stop')

    parser.add_argument(
        'name',
        nargs='+',
        help='The names of the instances to stop.')

  @property
  def service(self):
    return self.compute.instances

  @property
  def method(self):
    return 'Stop'

  @property
  def resource_type(self):
    return 'instances'

  def CreateRequests(self, args):
    request_list = []
    for name in args.name:
      instance_ref = self.CreateZonalReference(name, args.zone)

      request = self.messages.ComputeInstancesStopRequest(
          instance=instance_ref.Name(),
          project=self.project,
          zone=instance_ref.zone)

      request_list.append(request)
    return request_list

  def Display(self, _, resources):
    # There is no need to display anything when stopping an
    # instance. Instead, we consume the generator returned from Run()
    # to invoke the logic that waits for the stop to complete.
    list(resources)


Stop.detailed_help = {
    'brief': 'Stop a virtual machine instance',
    'DESCRIPTION': """\
        *{command}* is used stop a Google Compute Engine virtual machine.
        Stopping a VM performs a clean shutdown, much like invoking the shutdown
        functionality of a workstation or laptop. Stopping an SSD-attached VM is
        not supported and will result in an API error.
        """,
}
