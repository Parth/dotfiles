# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deleting HTTP health checks."""
from googlecloudsdk.compute.lib import base_classes


class Delete(base_classes.GlobalDeleter):
  """Delete HTTP health checks."""

  @property
  def service(self):
    return self.compute.httpHealthChecks

  @property
  def resource_type(self):
    return 'httpHealthChecks'


Delete.detailed_help = {
    'brief': 'Delete HTTP health checks',
    'DESCRIPTION': """\
        *{command}* deletes one or more Google Compute Engine
        HTTP health checks.
        """,
}
