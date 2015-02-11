# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deleting networks."""
from googlecloudsdk.compute.lib import base_classes


class Delete(base_classes.GlobalDeleter):
  """Delete Google Compute Engine networks."""

  @property
  def service(self):
    return self.compute.networks

  @property
  def resource_type(self):
    return 'networks'


Delete.detailed_help = {
    'brief': 'Delete Google Compute Engine networks',
    'DESCRIPTION': """\
        *{command}* deletes one or more Google Compute Engine
        networks. Networks can only be deleted when no other resources
        (e.g., virtual machine instances) refer to them.
        """,
}
