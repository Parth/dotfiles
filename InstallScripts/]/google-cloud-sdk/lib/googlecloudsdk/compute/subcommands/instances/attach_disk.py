# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for attaching a disk to an instance."""
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import utils

MODE_OPTIONS = ['ro', 'rw']


class AttachDisk(base_classes.NoOutputAsyncMutator):
  """Attaches a disk to an instance."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        'name',
        metavar='INSTANCE',
        help='The name of the instance to attach the disk to.')

    parser.add_argument(
        '--device-name',
        help=('An optional name that indicates the disk name the guest '
              'operating system will see.'))

    parser.add_argument(
        '--disk',
        help='The name of the disk to attach to the instance.',
        required=True)

    mode = parser.add_argument(
        '--mode',
        choices=MODE_OPTIONS,
        default='rw',
        help='Specifies the mode of the disk.')
    mode.detailed_help = """\
        Specifies the mode of the disk. Supported options are ``ro'' for
        read-only and ``rw'' for read-write. If omitted, ``rw'' is used as
        a default. It is an error to attach a disk in read-write mode to
        more than one instance.
        """

    utils.AddZoneFlag(
        parser,
        resource_type='instance',
        operation_type='attach a disk to')

  @property
  def service(self):
    return self.compute.instances

  @property
  def method(self):
    return 'AttachDisk'

  @property
  def resource_type(self):
    return 'instances'

  def CreateRequests(self, args):
    """Returns a request for attaching a disk to an instance."""
    instance_ref = self.CreateZonalReference(args.name, args.zone)
    disk_ref = self.CreateZonalReference(
        args.disk, instance_ref.zone, resource_type='disks')

    if args.mode == 'rw':
      mode = self.messages.AttachedDisk.ModeValueValuesEnum.READ_WRITE
    else:
      mode = self.messages.AttachedDisk.ModeValueValuesEnum.READ_ONLY

    request = self.messages.ComputeInstancesAttachDiskRequest(
        instance=instance_ref.Name(),
        project=self.project,
        attachedDisk=self.messages.AttachedDisk(
            deviceName=args.device_name,
            mode=mode,
            source=disk_ref.SelfLink(),
            type=self.messages.AttachedDisk.TypeValueValuesEnum.PERSISTENT),
        zone=instance_ref.zone)

    return [request]


AttachDisk.detailed_help = {
    'brief': ('Attach a disk to an instance'),
    'DESCRIPTION': """\
        *{command}* is used to attach a disk to an instance. For example,

          $ gcloud compute instances attach-disk example-instance --disk DISK --zone us-central1-a

        attaches the disk named 'DISK' to the instance named
        'example-instance' in zone ``us-central1-a''.
        """,
}
