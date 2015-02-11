# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deleting routes."""
from googlecloudsdk.compute.lib import base_classes


class Delete(base_classes.GlobalDeleter):
  """Delete routes."""

  @property
  def service(self):
    return self.compute.routes

  @property
  def resource_type(self):
    return 'routes'


Delete.detailed_help = {
    'brief': 'Delete routes',
    'DESCRIPTION': """\
        *{command}* deletes one or more Google Compute Engine routes.
        """,
}
