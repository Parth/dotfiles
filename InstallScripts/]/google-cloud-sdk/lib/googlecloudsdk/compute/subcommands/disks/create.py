# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for creating disks."""
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import image_utils
from googlecloudsdk.compute.lib import utils
from googlecloudsdk.compute.lib import zone_utils


class Create(base_classes.BaseAsyncCreator, image_utils.ImageExpander,
             zone_utils.ZoneResourceFetcher):
  """Create Google Compute Engine persistent disks."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--description',
        help=(
            'An optional, textual description for the disks being created.'))

    size = parser.add_argument(
        '--size',
        type=arg_parsers.BinarySize(lower_bound='1GB'),
        help='Indicates the size of the disks.')
    size.detailed_help = """\
        Indicates the size of the disks. The value must be a whole
        number followed by a size unit of ``KB'' for kilobyte, ``MB''
        for megabyte, ``GB'' for gigabyte, or ``TB'' for terabyte. For
        example, ``10GB'' will produce 10 gigabyte disks. If omitted,
        a default size of 500 GB is used for standard disks and 200GB
        for SSD disks. The minimum size a disk can
        have is 1 GB. Disk size must be a multiple of 10 GB.
        """

    parser.add_argument(
        'names',
        metavar='NAME',
        nargs='+',
        help='The names of the disks to create.')

    source_group = parser.add_mutually_exclusive_group()

    def AddImageHelp():
      return """\
          An image to apply to the disks being created. When using
          this option, the size of the disks must be at least as large as
          the image size. Use ``--size'' to adjust the size of the disks.

          {alias_table}

          This flag is mutually exclusive with ``--source-snapshot''.
          """.format(alias_table=image_utils.GetImageAliasTable())

    image = source_group.add_argument(
        '--image',
        help='An image to apply to the disks being created.')
    image.detailed_help = AddImageHelp

    image_utils.AddImageProjectFlag(parser)

    source_snapshot = source_group.add_argument(
        '--source-snapshot',
        help='A source snapshot used to create the disks.')
    source_snapshot.detailed_help = """\
        A source snapshot used to create the disks. It is safe to
        delete a snapshot after a disk has been created from the
        snapshot. In such cases, the disks will no longer reference
        the deleted snapshot. To get a list of snapshots in your
        current project, run `gcloud compute snapshots list`. A
        snapshot from an existing disk can be created using the
        'gcloud compute disks snapshot' command. This flag is mutually
        exclusive with ``--image''.

        When using this option, the size of the disks must be at least
        as large as the snapshot size. Use ``--size'' to adjust the
        size of the disks.
        """

    disk_type = parser.add_argument(
        '--type',
        help='Specifies the type of disk to create.')
    disk_type.detailed_help = """\
        Specifies the type of disk to create. To get a
        list of available disk types, run 'gcloud compute
        disk-types list'. The default disk type is pd-standard.
        """

    utils.AddZoneFlag(
        parser,
        resource_type='disks',
        operation_type='create')

  @property
  def service(self):
    return self.compute.disks

  @property
  def method(self):
    return 'Insert'

  @property
  def resource_type(self):
    return 'disks'

  def CreateRequests(self, args):
    """Returns a list of requests necessary for adding disks."""
    size_gb = utils.BytesToGb(args.size)

    if not size_gb and not args.source_snapshot and not args.image:
      if args.type and 'pd-ssd' in args.type:
        size_gb = constants.DEFAULT_SSD_DISK_SIZE_GB
      else:
        size_gb = constants.DEFAULT_STANDARD_DISK_SIZE_GB

    utils.WarnIfDiskSizeIsTooSmall(size_gb, args.type)

    requests = []

    disk_refs = self.CreateZonalReferences(args.names, args.zone)

    # Check if the zone is deprecated or has maintenance coming.
    self.WarnForZonalCreation(disk_refs)

    if args.image:
      source_image_uri, _ = self.ExpandImageFlag(
          args, return_image_resource=False)
    else:
      source_image_uri = None

    if args.source_snapshot:
      snapshot_ref = self.CreateGlobalReference(
          args.source_snapshot, resource_type='snapshots')
      snapshot_uri = snapshot_ref.SelfLink()
    else:
      snapshot_uri = None

    for disk_ref in disk_refs:
      if args.type:
        type_ref = self.CreateZonalReference(
            args.type, disk_ref.zone,
            resource_type='diskTypes')
        type_uri = type_ref.SelfLink()
      else:
        type_uri = None

      request = self.messages.ComputeDisksInsertRequest(
          disk=self.messages.Disk(
              name=disk_ref.Name(),
              description=args.description,
              sizeGb=size_gb,
              sourceSnapshot=snapshot_uri,
              type=type_uri),
          project=self.project,
          sourceImage=source_image_uri,
          zone=disk_ref.zone)
      requests.append(request)

    return requests


Create.detailed_help = {
    'brief': 'Create Google Compute Engine persistent disks',
    'DESCRIPTION': """\
        *{command}* creates one or more Google Compute Engine
        persistent disks. When creating virtual machine instances,
        disks can be attached to the instances through the
        'gcloud compute instances create' command. Disks can also be
        attached to instances that are already running using
        'gloud compute instances attach-disk'.

        Disks are zonal resources, so they reside in a particular zone
        for their entire lifetime. The contents of a disk can be moved
        to a different zone by snapshotting the disk (using
        'gcloud compute disks snapshot') and creating a new disk using
        ``--source-snapshot'' in the desired zone. The contents of a
        disk can also be moved across project or zone by creating an
        image (using 'gcloud compute images create') and creating a
        new disk using ``--image'' in the desired project and/or
        zone.

        When creating disks, be sure to include the ``--zone'' option:

          $ {command} my-disk-1 my-disk-2 --zone us-east1-a
        """,
}
