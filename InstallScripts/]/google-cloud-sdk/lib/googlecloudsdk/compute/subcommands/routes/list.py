# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing routes."""
from googlecloudsdk.compute.lib import base_classes


class List(base_classes.GlobalLister):
  """List routes."""

  @property
  def service(self):
    return self.compute.routes

  @property
  def resource_type(self):
    return 'routes'


List.detailed_help = {
    'brief': 'List routes.',
    'DESCRIPTION': """\
        *{command}* lists summary information for the routes in a
        project. The ``--uri'' option can be used to display the
        URIs for the routes. Users who want to see more data should use
        'gcloud compute routes describe'.
        """,
}
