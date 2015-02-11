# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for resetting an instance."""
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import utils


class Reset(base_classes.NoOutputAsyncMutator):
  """Reset a virtual machine instance."""

  @staticmethod
  def Args(parser):
    utils.AddZoneFlag(
        parser,
        resource_type='instance',
        operation_type='reset')

    parser.add_argument(
        'name',
        nargs='+',
        help='The names of the instances to reset.')

  @property
  def service(self):
    return self.compute.instances

  @property
  def method(self):
    return 'Reset'

  @property
  def resource_type(self):
    return 'instances'

  def CreateRequests(self, args):
    request_list = []
    for name in args.name:
      instance_ref = self.CreateZonalReference(name, args.zone)

      request = self.messages.ComputeInstancesResetRequest(
          instance=instance_ref.Name(),
          project=self.project,
          zone=instance_ref.zone)

      request_list.append(request)
    return request_list

  def Display(self, _, resources):
    # There is no need to display anything when resetting an
    # instance. Instead, we consume the generator returned from Run()
    # to invoke the logic that waits for the reset to complete.
    list(resources)


Reset.detailed_help = {
    'brief': 'Reset a virtual machine instance',
    'DESCRIPTION': """\
        *{command}* is used to perform a hard reset on a Google
        Compute Engine virtual machine.
        """,
}
