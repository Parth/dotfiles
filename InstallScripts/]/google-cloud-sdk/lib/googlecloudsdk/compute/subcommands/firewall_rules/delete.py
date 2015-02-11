# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deleting firewall rules."""
from googlecloudsdk.compute.lib import base_classes


class Delete(base_classes.GlobalDeleter):
  """Delete Google Compute Engine firewall rules."""

  @property
  def service(self):
    return self.compute.firewalls

  @property
  def resource_type(self):
    return 'firewalls'


Delete.detailed_help = {
    'brief': 'Delete Google Compute Engine firewall rules',
    'DESCRIPTION': """\
        *{command}* deletes one or more Google Compute Engine firewall
         rules.
        """,
}
