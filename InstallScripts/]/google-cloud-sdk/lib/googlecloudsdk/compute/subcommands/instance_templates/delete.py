# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deleting instance templates."""
from googlecloudsdk.compute.lib import base_classes


class Delete(base_classes.GlobalDeleter):
  """Delete Google Compute Engine virtual machine instance templates."""

  @property
  def service(self):
    return self.compute.instanceTemplates

  @property
  def resource_type(self):
    return 'instanceTemplates'


Delete.detailed_help = {
    'brief': 'Delete Google Compute Engine virtual machine instance templates',
    'DESCRIPTION': """\
        *{command}* deletes one or more Google Compute Engine virtual machine
        instance templates.
        """,
}
