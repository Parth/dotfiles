# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for removing project-wide metadata."""

from googlecloudsdk.compute.lib import base_classes


class RemoveMetadata(base_classes.ProjectMetadataMutatorMixin,
                     base_classes.BaseMetadataRemover):
  """Remove project-wide metadata entries."""

  @staticmethod
  def Args(parser):
    base_classes.BaseMetadataRemover.Args(parser)


RemoveMetadata.detailed_help = {
    'brief': 'Remove project-wide metadata entries',
    'DESCRIPTION': """\
        *{command}* can be used to remove project-wide metadata entries.
        """,
}
