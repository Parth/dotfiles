# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for creating images."""
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import utils


class Create(base_classes.BaseAsyncCreator):
  """Create Google Compute Engine images."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--description',
        help=('An optional, textual description for the image being created.'))

    source_group = parser.add_mutually_exclusive_group(required=True)

    source_uri = source_group.add_argument(
        '--source-uri',
        help=('The full Google Cloud Storage URI where the disk image is '
              'stored.'))
    source_uri.detailed_help = """\
        The full Google Cloud Storage URI where the disk image is stored.
        This file must be a gzip-compressed tarball whose name ends in
        ``.tar.gz''.

        This flag is mutually exclusive with ``--source-disk''.
        """

    source_disk = source_group.add_argument(
        '--source-disk',
        help='A source disk to create the image from.')
    source_disk.detailed_help = """\
        A source disk to create the image from. The value for this option can be
        the name of a disk with the zone specified via ``--source-disk-zone''
        flag.

        This flag is mutually exclusive with ``--source-uri''.
        """

    source_disk_zone = parser.add_argument(
        '--source-disk-zone',
        help='The zone of the disk specified by --source-disk.')
    source_disk_zone.detailed_help = ("""\
        The zone of the disk specified by --source-disk.
        """ + constants.ZONE_PROPERTY_EXPLANATION)

    parser.add_argument(
        'name',
        metavar='NAME',
        help='The name of the image to create.')

  @property
  def service(self):
    return self.compute.images

  @property
  def method(self):
    return 'Insert'

  @property
  def resource_type(self):
    return 'images'

  def CreateRequests(self, args):
    """Returns a list of requests necessary for adding images."""

    image = self.messages.Image(
        name=args.name,
        description=args.description,
        sourceType=self.messages.Image.SourceTypeValueValuesEnum.RAW)

    # Validate parameters.
    if args.source_disk_zone and not args.source_disk:
      raise exceptions.ToolException(
          'You cannot specify [--source-disk-zone] unless you are specifying '
          '[--source-disk].')

    if args.source_uri:
      source_uri = utils.NormalizeGoogleStorageUri(args.source_uri)
      image.rawDisk = self.messages.Image.RawDiskValue(source=source_uri)
    else:
      source_disk_ref = self.CreateZonalReference(
          args.source_disk,
          args.source_disk_zone,
          flag_names=['--source-disk-zone'],
          resource_type='disks')
      image.sourceDisk = source_disk_ref.SelfLink()

    request = self.messages.ComputeImagesInsertRequest(
        image=image,
        project=self.project)

    return [request]


Create.detailed_help = {
    'brief': 'Create Google Compute Engine images',
    'DESCRIPTION': """\
        *{command}* is used to create custom disk images.
        The resulting image can be provided during instance or disk creation
        so that the instance attached to the resulting disks has access
        to a known set of software or files from the image.

        Images can be created from gzipped compressed tarball containing raw
        disk data or from existing disks in any zone.

        Images are global resources, so they can be used across zones and
        projects.

        To learn more about creating image tarballs, visit
        link:https://developers.google.com/compute/docs/images[].
        """,
}
