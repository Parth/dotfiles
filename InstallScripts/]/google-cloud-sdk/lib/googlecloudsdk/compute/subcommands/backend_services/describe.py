# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing backend services."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.GlobalDescriber):
  """Describe a backend service."""

  @staticmethod
  def Args(parser):
    base_classes.GlobalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'backendServices')

  @property
  def service(self):
    return self.compute.backendServices

  @property
  def resource_type(self):
    return 'backendServices'


Describe.detailed_help = {
    'brief': 'Describe a backend service',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a backend service in a
        project.
        """,
}
