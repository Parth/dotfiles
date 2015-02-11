# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for adding tags to instances."""
import copy

from googlecloudsdk.compute.lib import base_classes


class InstancesAddTags(base_classes.InstanceTagsMutatorMixin,
                       base_classes.ReadWriteCommand):
  """Add tags to Google Compute Engine virtual machine instances."""

  @staticmethod
  def Args(parser):
    base_classes.InstanceTagsMutatorMixin.Args(parser)
    tags = parser.add_argument(
        '--tags',
        help='A list of tags to attach to the instance.',
        metavar='TAG',
        nargs='+')
    tags.detailed_help = """\
        Specifies strings to be attached to the instance for later
        identifying the instance when adding network firewall rules.
        Multiple tags can be attached by repeating this flag.
        """

  def Modify(self, args, existing):
    new_object = copy.deepcopy(existing)

    # Do not re-order the items if the object won't change, or the objects
    # will not be considered equal and an unnecessary API call will be made.
    new_tags = set(new_object.tags.items + args.tags)
    if new_tags != set(new_object.tags.items):
      new_object.tags.items = sorted(new_tags)

    return new_object


InstancesAddTags.detailed_help = {
    'brief': 'Add tags to Google Compute Engine virtual machine instances',
    'DESCRIPTION': """\
        *{command}* is used to add tags to Google Compute Engine virtual
        machine instances. For example, running:

          $ {command} example-instance --tags tag-1 tag-2

        will add tags ``tag-1'' and ``tag-2'' to 'example-instance'.

        Tags can be used to identify the instances when adding network
        firewall rules. Tags can also be used to get firewall rules that
        already exist to be applied to the instance. See
        gcloud_compute_firewall-rules_create(1) for more details.
        """,
}
