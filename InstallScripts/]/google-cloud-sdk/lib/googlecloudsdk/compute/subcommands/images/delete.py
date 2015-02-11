# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deleting networks."""
from googlecloudsdk.compute.lib import base_classes


class Delete(base_classes.GlobalDeleter):
  """Delete Google Compute Engine images."""

  @property
  def service(self):
    return self.compute.images

  @property
  def resource_type(self):
    return 'images'


Delete.detailed_help = {
    'brief': 'Delete Google Compute Engine images',
    'DESCRIPTION': """\
        *{command}* deletes one or more Google Compute Engine images.
        """,
}
