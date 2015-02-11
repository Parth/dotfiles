# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for adding project-wide metadata."""

from googlecloudsdk.compute.lib import base_classes


class AddMetadata(base_classes.ProjectMetadataMutatorMixin,
                  base_classes.BaseMetadataAdder):
  """Add or update project-wide metadata."""

  @staticmethod
  def Args(parser):
    base_classes.BaseMetadataAdder.Args(parser)


AddMetadata.detailed_help = {
    'brief': 'Add or update project-wide metadata',
    'DESCRIPTION': """\
        *{command}* can be used to add or update project-wide
        metadata. Every instance has access to a metadata server that
        can be used to query metadata that has been set through this
        tool. Project-wide metadata entries are visible to all
        instances. To set metadata for individual instances, use
        'gcloud compute instances add-metadata'. For information on
        metadata, see
        https://developers.google.com/compute/docs/metadata.

        Only metadata keys that are provided are mutated. Existing
        metadata entries will remain unaffected.
        """,
}
