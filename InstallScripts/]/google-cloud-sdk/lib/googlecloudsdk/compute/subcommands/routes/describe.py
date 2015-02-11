# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing routes."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.GlobalDescriber):
  """Describe a route."""

  @staticmethod
  def Args(parser):
    base_classes.GlobalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'routes')

  @property
  def service(self):
    return self.compute.routes

  @property
  def resource_type(self):
    return 'routes'


Describe.detailed_help = {
    'brief': 'Describe a route',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Google Compute
        Engine route in a project.
        """,
}
