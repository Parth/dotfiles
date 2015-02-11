# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deleting target pools."""
from googlecloudsdk.compute.lib import base_classes


class Delete(base_classes.RegionalDeleter):
  """Delete target pools."""

  @property
  def service(self):
    return self.compute.targetPools

  @property
  def resource_type(self):
    return 'targetPools'


Delete.detailed_help = {
    'brief': 'Delete target pools',
    'DESCRIPTION': """\
        *{command}* deletes one or more Google Compute Engine target pools.
        """,
}
