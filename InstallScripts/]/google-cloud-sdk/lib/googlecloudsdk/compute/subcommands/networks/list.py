# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing networks."""
from googlecloudsdk.compute.lib import base_classes


class List(base_classes.GlobalLister):
  """List Google Compute Engine networks."""

  @property
  def service(self):
    return self.compute.networks

  @property
  def resource_type(self):
    return 'networks'


List.detailed_help = {
    'brief': 'List Google Compute Engine networks',
    'DESCRIPTION': """\
       *{command}* lists summary information for the networks in
       a project. The ``--uri'' option can be used to display the
       URIs of the networks in the project.
       """,
}
