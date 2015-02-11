# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for removing metadata."""

from googlecloudsdk.compute.lib import base_classes


class InstancesRemoveMetadata(base_classes.InstanceMetadataMutatorMixin,
                              base_classes.BaseMetadataRemover):
  """Remove instance metadata."""

  @staticmethod
  def Args(parser):
    base_classes.InstanceMetadataMutatorMixin.Args(parser)
    base_classes.BaseMetadataRemover.Args(parser)


InstancesRemoveMetadata.detailed_help = {
    'brief': 'Remove instance metadata',
    'DESCRIPTION': """\
        {command} can be used to remove instance metadata entries.
        """,
}
