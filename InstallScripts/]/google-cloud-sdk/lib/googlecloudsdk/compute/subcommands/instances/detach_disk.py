# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for detaching a disk from an instance."""
import copy

from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import utils


class DetachDisk(base_classes.ReadWriteCommand):
  """Detach disks from Google Compute Engine virtual machine instances."""

  @staticmethod
  def Args(parser):
    disk_group = parser.add_mutually_exclusive_group(required=True)

    disk_name = disk_group.add_argument(
        '--disk',
        help='Specify a disk to remove by persistent disk name.')
    disk_name.detailed_help = """\
        Specifies a disk to detach by its resource name. If you specify a
        disk to remove by persistent disk name, then you must not specify its
        device name using the ``--device-name'' flag.
        """

    device_name = disk_group.add_argument(
        '--device-name',
        help=('Specify a disk to remove by the name the guest operating '
              'system sees.'))
    device_name.detailed_help = """\
        Specifies a disk to detach by its device name, which is the name
        that the guest operating system sees. The device name is set
        at the time that the disk is attached to the instance, and needs not be
        the same as the persistent disk name. If the disk's device name is
        specified, then its persistent disk name must not be specified
        using the ``--disk'' flag.
        """

    parser.add_argument(
        'name',
        metavar='NAME',
        help='The name of the instance to detach the disk from.')

    utils.AddZoneFlag(
        parser,
        resource_type='instance',
        operation_type='detach a disk from')

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
    removed_disk = list(
        set(disk.deviceName for disk in existing.disks) -
        set(disk.deviceName for disk in replacement.disks))[0]

    return (self.service,
            'DetachDisk',
            self.messages.ComputeInstancesDetachDiskRequest(
                deviceName=removed_disk,
                instance=self.ref.Name(),
                project=self.project,
                zone=self.ref.zone))

  def Modify(self, args, existing):
    replacement = copy.deepcopy(existing)

    if args.disk:
      disk_ref = self.CreateZonalReference(
          args.disk, self.ref.zone, resource_type='disks')
      replacement.disks = [disk for disk in existing.disks
                           if disk.source != disk_ref.SelfLink()]

      if len(existing.disks) == len(replacement.disks):
        raise exceptions.ToolException(
            'Disk [{0}] is not attached to instance [{1}] in zone [{2}].'
            .format(disk_ref.Name(), self.ref.Name(), self.ref.zone))

    else:
      replacement.disks = [disk for disk in existing.disks
                           if disk.deviceName != args.device_name]

      if len(existing.disks) == len(replacement.disks):
        raise exceptions.ToolException(
            'No disk with device name [{0}] is attached to instance [{1}] in '
            'zone [{2}].'
            .format(args.device_name, self.ref.Name(), self.ref.zone))

    return replacement


DetachDisk.detailed_help = {
    'brief': 'Detach disks from Compute Engine virtual machine instances',
    'DESCRIPTION': """\
        *{command}* is used to detach disks from virtual machines.

        Detaching a disk without first unmounting it may result in
        incomplete I/O operations and data corruption.
        To unmount a persistent disk on a Linux-based image,
        ssh into the instance and run:

          $ sudo umount /dev/disk/by-id/google-DEVICE_NAME
        """,
}
