# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for adding metadata."""

from googlecloudsdk.compute.lib import base_classes


class InstancesAddMetadata(base_classes.InstanceMetadataMutatorMixin,
                           base_classes.BaseMetadataAdder):
  """Add or update instance metadata."""

  @staticmethod
  def Args(parser):
    base_classes.InstanceMetadataMutatorMixin.Args(parser)
    base_classes.BaseMetadataAdder.Args(parser)


InstancesAddMetadata.detailed_help = {
    'brief': 'Add or update instance metadata',
    'DESCRIPTION': """\
        {command} can be used to add or update the metadata of a
        virtual machine instance. Every instance has access to a
        metadata server that can be used to query metadata that has
        been set through this tool. For information on metadata, see
        https://developers.google.com/compute/docs/metadata.

        Only metadata keys that are provided are mutated. Existing
        metadata entries will remain unaffected.
        """,
}
