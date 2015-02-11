# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing firewall rules."""
from googlecloudsdk.compute.lib import base_classes


class List(base_classes.GlobalLister):
  """List Google Compute Engine firewall rules."""

  @property
  def service(self):
    return self.compute.firewalls

  @property
  def resource_type(self):
    return 'firewalls'

List.detailed_help = {
    'brief': 'List Google Compute Engine firewall rules',
    'DESCRIPTION': """\
        *{command}* lists summary information for the firewall rules
        in a project. The ``--uri'' option can be used to display
        the URIs of the firewall rules in the project.
        Users who want to see more data should use 'gcloud compute
        firewall-rules describe'.
        """,
}
