# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deprecating images."""
import datetime

from googlecloudapis.compute.v1 import compute_v1_messages
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.compute.lib import base_classes


DEPRECATION_STATUSES = sorted(
    ['ACTIVE'] +
    compute_v1_messages.DeprecationStatus.StateValueValuesEnum.to_dict().keys())


def _ResolveTime(absolute, relative_sec, current_time):
  """Get the RFC 3339 time string for a provided absolute or relative time."""
  if absolute:
    return absolute
  elif relative_sec:
    return (
        current_time + datetime.timedelta(seconds=relative_sec)
    ).replace(microsecond=0).isoformat()
  else:
    return None


class DeprecateImages(base_classes.NoOutputAsyncMutator):
  """Deprecate Google Compute Engine images."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        'name',
        metavar='NAME',
        help='The name of the image to set deprecation status of.')

    state = parser.add_argument(
        '--state',
        choices=DEPRECATION_STATUSES,
        type=lambda x: x.upper(),
        required=True,
        help='The deprecation state to set on the image.')
    state.detailed_help = """\
       The deprecation state to set on the image.
       An image's default state is ``ACTIVE'', suggesting that the image is
       currently supported. Operations which create a new
       resource using a ``DEPRECATED'' image
       return successfully, but with a warning indicating that the image
       is deprecated and recommending its replacement. New uses of ``OBSOLETE'' or
       ``DELETED'' images result in an error. Note that setting the
       deprecation state to ``DELETED'' will not automatically delete the
       image. You must still make a request to delete the image to remove it
       from the image list.
       """

    replacement = parser.add_argument(
        '--replacement',
        help='Specifies a Compute Engine image as a replacement.')
    replacement.detailed_help = """\
       Specifies a Compute Engine image as a replacement for the image
       being phased out. Users of the deprecated image will be advised to switch
       to this replacement. For example, ``--replacement example-image'' or
       ``--replacement projects/google/global/images/example-image''. This
       flag is required when setting the image state to anything other than
       ``ACTIVE'' or when --delete-in, --delete-on, --obsolete-in, or
       --obsolete-on is provided.
       """

    delete_group = parser.add_mutually_exclusive_group()

    delete_on = delete_group.add_argument(
        '--delete-on',
        help=('Specifies the date and time when the state of this image '
              'will become DELETED.'))
    delete_on.detailed_help = """\
       Similar to --delete-in, but specifies an absolute time when the status
       should be set to DELETED. The date and time
       specified must be a valid RFC 3339 full-date or date-time.
       For times in UTC, this looks like ``YYYY-MM-DDTHH:MM:SSZ''. For example:
       2020-01-02T00:00:00Z for midnight on January 2, 2020 in UTC.
       This flag is mutually exclusive with --delete-in.
       """

    delete_in = delete_group.add_argument(
        '--delete-in',
        help=('Specifies the amount of time until this image should become '
              'DELETED.'),
        type=arg_parsers.Duration())
    delete_in.detailed_help = """\
       Specifies the amount of time until the image's status should be set
       to DELETED. For instance, specifying ``30d'' will set the status to
       DELETED in 30 days from the current system time. Valid units for this
       flag are ``s'' for seconds, ``m'' for minutes, ``h'' for hours and
       ``d'' for days. If no unit is specified, seconds is assumed.

       Note that the image will not be deleted automatically. The image will
       only be marked as deleted. An explicit request to delete the image must
       be made in order to remove it from the image list.
       This flag is mutually exclusive with --delete-on.
       """

    obsolete_group = parser.add_mutually_exclusive_group()

    obsolete_on = obsolete_group.add_argument(
        '--obsolete-on',
        help=('Specifies the date and time when the state of this image '
              'will become OBSOLETE.'))
    obsolete_on.detailed_help = """\
       Specifies time (in the same format as --delete-on) when this image's
       status should become OBSOLETE.
       This flag is mutually exclusive with --obsolete-in.
       """

    obsolete_in = obsolete_group.add_argument(
        '--obsolete-in',
        help=('Specifies the amount of time until this image should become '
              'OBSOLETE.'),
        type=arg_parsers.Duration())
    obsolete_in.detailed_help = """\
       Specifies time (in the same format as --delete-in) until this image's
       status should become OBSOLETE. Obsolete images will cause an error
       whenever an attempt is made to apply the image to a new disk.
       This flag is mutually exclusive with --obsolete-on.
       """

  @property
  def service(self):
    return self.compute.images

  @property
  def method(self):
    return 'Deprecate'

  @property
  def resource_type(self):
    return 'images'

  def CreateRequests(self, args):
    """Returns a list of requests necessary for deprecating images."""

    if (any([args.delete_on, args.delete_in, args.obsolete_on, args.obsolete_in,
             args.replacement]) and args.state == 'ACTIVE'):
      raise calliope_exceptions.ToolException(
          'If the state is set to [ACTIVE] then none of [--delete-on], '
          '[--delete-in], [--obsolete-on], [--obsolete-in], or [--replacement] '
          'may be provided.')
    elif not args.replacement and args.state != 'ACTIVE':
      raise calliope_exceptions.ToolException(
          '[--replacement] is required when deprecation, obsoletion or '
          'deletion status is set or scheduled.')

    # Determine the date and time to deprecate for each flag set.
    current_time = datetime.datetime.now()
    delete_time = _ResolveTime(args.delete_on, args.delete_in, current_time)
    obsolete_time = _ResolveTime(
        args.obsolete_on, args.obsolete_in, current_time)

    # ACTIVE is not actually an option in the state enum.
    if args.state == 'ACTIVE':
      state = None
    else:
      state = self.messages.DeprecationStatus.StateValueValuesEnum(args.state)

    if args.replacement:
      replacement_uri = self.CreateGlobalReference(args.replacement).SelfLink()
    else:
      replacement_uri = None

    image_ref = self.CreateGlobalReference(args.name)

    request = self.messages.ComputeImagesDeprecateRequest(
        deprecationStatus=self.messages.DeprecationStatus(
            state=state,
            deleted=delete_time,
            obsolete=obsolete_time,
            replacement=replacement_uri),
        image=image_ref.Name(),
        project=self.project)

    return [request]


DeprecateImages.detailed_help = {
    'brief': 'Manage deprecation status of Google Compute Engine images',
    'DESCRIPTION': """\
        *{command}* is used to deprecate images.
        """,
    'EXAMPLES': """\
        To deprecate an image called 'IMAGE' immediately, mark it as
        obsolete in one day, and mark it as deleted in two days, use:

          $ {command} IMAGE --status DEPRECATED --obsolete-in 1d --delete-in 2d

        To un-deprecate an image called 'IMAGE', use:

          $ {command} IMAGE --status ACTIVE
        """,
}
