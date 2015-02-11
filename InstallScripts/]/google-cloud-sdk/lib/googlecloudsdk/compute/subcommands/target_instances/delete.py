# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deleting target instances."""
from googlecloudsdk.compute.lib import base_classes


class Delete(base_classes.ZonalDeleter):
  """Delete target instances."""

  @property
  def service(self):
    return self.compute.targetInstances

  @property
  def resource_type(self):
    return 'targetInstances'


Delete.detailed_help = {
    'brief': 'Delete target instances',
    'DESCRIPTION': """\
        *{command}* deletes one or more Google Compute Engine target
        instances. Target instances can be deleted only if they are
        not being used by any other resources like forwarding rules.
        """,
}
