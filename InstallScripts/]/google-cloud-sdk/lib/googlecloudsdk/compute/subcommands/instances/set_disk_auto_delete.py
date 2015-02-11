# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for setting whether to auto-delete a disk."""
import copy

from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import utils


class SetDiskAutoDelete(base_classes.ReadWriteCommand):
  """Set auto-delete behavior for disks."""

  @staticmethod
  def Args(parser):
    utils.AddZoneFlag(
        parser,
        resource_type='instance',
        operation_type='configure disk auto-delete for')

    parser.add_argument(
        'name',
        metavar='INSTANCE',
        help=('The name of the instance for which to configure disk '
              'auto-deletion.'))

    auto_delete_group = parser.add_mutually_exclusive_group(required=True)

    auto_delete_group.add_argument(
        '--auto-delete',
        action='store_true',
        help='Set auto-delete for the given disk to true.')

    auto_delete_group.add_argument(
        '--no-auto-delete',
        action='store_true',
        help='Set auto-delete for the given disk to false.')

    disk_group = parser.add_mutually_exclusive_group(required=True)

    disk = disk_group.add_argument(
        '--disk',
        help=('Specify a disk to set auto-delete for by persistent disk '
              'name.'))
    disk.detailed_help = """\
        Specifies a disk to set auto-delete for by its resource name. If
        you specify a disk to set auto-delete for by persistent disk name,
        then you must not specify its device name using the
        ``--device-name'' flag.
        """

    device_name = disk_group.add_argument(
        '--device-name',
        help=('Specify a disk to set auto-delete for by the name the '
              'guest operating system sees.'))
    device_name.detailed_help = """\
        Specifies a disk to set auto-delete for by its device name,
        which is the name that the guest operating system sees. The
        device name is set at the time that the disk is attached to the
        instance, and need not be the same as the persistent disk name.
        If the disk's device name is specified, then its persistent disk
        name must not be specified using the ``--disk'' flag.
        """

  @property
  def service(self):
    return self.compute.instances

  @property
  def resource_type(self):
    return 'instances'

  def CreateReference(self, args):
    return self.CreateZonalReference(args.name, args.zone)

  def GetGetRequest(self, args):
    return (self.service,
            'Get',
            self.messages.ComputeInstancesGetRequest(
                instance=self.ref.Name(),
                project=self.project,
                zone=self.ref.zone))

  def GetSetRequest(self, args, replacement, existing):
    # Our protocol buffers are mutable, so they cannot be
    # hashed. Because of this, we cannot do a set subraction on the
    # lists of disks. Instead, the task of finding the changed disk is
    # relegated to a for-loop.
    for existing_disk, replacement_disk in zip(
        existing.disks, replacement.disks):
      if existing_disk != replacement_disk:
        changed_disk = replacement_disk

    return (self.service,
            'SetDiskAutoDelete',
            self.messages.ComputeInstancesSetDiskAutoDeleteRequest(
                deviceName=changed_disk.deviceName,
                instance=self.ref.Name(),
                project=self.project,
                zone=self.ref.zone,
                autoDelete=changed_disk.autoDelete))

  def Modify(self, args, existing):
    replacement = copy.deepcopy(existing)
    disk_found = False

    if args.disk:
      disk_ref = self.CreateZonalReference(
          args.disk, self.ref.zone,
          resource_type='disks')

      for disk in replacement.disks:
        if disk.source == disk_ref.SelfLink():
          disk.autoDelete = args.auto_delete
          disk_found = True

      if not disk_found:
        raise exceptions.ToolException(
            'Disk [{0}] is not attached to instance [{1}] in zone [{2}].'
            .format(disk_ref.Name(), self.ref.Name(), self.ref.zone))

    else:
      for disk in replacement.disks:
        if disk.deviceName == args.device_name:
          disk.autoDelete = args.auto_delete
          disk_found = True

      if not disk_found:
        raise exceptions.ToolException(
            'No disk with device name [{0}] is attached to instance [{1}] '
            'in zone [{2}].'
            .format(args.device_name, self.ref.Name(), self.ref.zone))

    return replacement


SetDiskAutoDelete.detailed_help = {
    'brief': 'Set auto-delete behavior for disks',
    'DESCRIPTION': """\
        *${command}* is used to configure the auto-delete behavior for disks
        attached to Google Compute Engine virtual machines. When
        auto-delete is on, the persistent disk is deleted when the
        instance it is attached to is deleted.
        """,
}
