# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for removing tags from instances."""
import copy

from googlecloudsdk.compute.lib import base_classes


class RemoveTags(base_classes.InstanceTagsMutatorMixin,
                 base_classes.ReadWriteCommand):
  """Remove tags from Google Compute Engine virtual machine instances."""

  @staticmethod
  def Args(parser):
    tags_group = parser.add_mutually_exclusive_group(required=True)
    tags = tags_group.add_argument(
        '--tags',
        help='Tags to remove from the instance.',
        metavar='TAG',
        nargs='+')
    tags.detailed_help = """\
        Specifies strings to be removed from the instance tags.
        Multiple tags can be removed by repeating this flag.
        """
    tags_group.add_argument(
        '--all',
        action='store_true',
        default=False,
        help='Remove all tags from the instance.')

    base_classes.InstanceTagsMutatorMixin.Args(parser)

  def Modify(self, args, existing):
    new_object = copy.deepcopy(existing)
    if args.all:
      new_object.tags.items = []
    else:
      new_object.tags.items = sorted(
          set(new_object.tags.items) - set(args.tags))
    return new_object


RemoveTags.detailed_help = {
    'brief': 'Remove tags from Google Compute Engine virtual machine instances',
    'DESCRIPTION': """\
        *{command}* is used to remove tags to Google Compute Engine virtual
        machine instances.  For example:

          $ {command} example-instance --tags tag-1 tag-2

        will remove tags ``tag-1'' and ``tag-2'' from the existing tags of
        'example-instance'.

        Tags can be used to identify instances when adding network
        firewall rules. Tags can also be used to get firewall rules that already
        exist to be applied to the instance. See
        gcloud_compute_firewall-rules_create(1) for more details.
        """,
}
