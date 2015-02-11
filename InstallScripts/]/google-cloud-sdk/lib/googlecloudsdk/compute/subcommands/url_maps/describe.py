# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing url maps."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.GlobalDescriber):
  """Describe a URL map."""

  @staticmethod
  def Args(parser):
    base_classes.GlobalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'urlMaps')

  @property
  def service(self):
    return self.compute.urlMaps

  @property
  def resource_type(self):
    return 'urlMaps'


Describe.detailed_help = {
    'brief': 'Describe a URL map',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a URL map in a
        project.
        """,
}
