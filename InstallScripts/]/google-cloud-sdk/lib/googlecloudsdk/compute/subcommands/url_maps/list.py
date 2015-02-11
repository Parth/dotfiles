# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing URL maps."""
from googlecloudsdk.compute.lib import base_classes


class List(base_classes.GlobalLister):
  """List URL maps."""

  @property
  def service(self):
    return self.compute.urlMaps

  @property
  def resource_type(self):
    return 'urlMaps'


List.detailed_help = {
    'brief': 'List URL maps',
    'DESCRIPTION': """\
        *{command}* lists summary information for the URL maps in a
        project. The ``--uri'' option can be used to display the
        URIs of the URL maps.
        """,
}
