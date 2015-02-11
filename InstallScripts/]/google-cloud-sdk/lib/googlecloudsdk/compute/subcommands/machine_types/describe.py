# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing machine types."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.ZonalDescriber):
  """Describe a Google Compute Engine machine type."""

  @staticmethod
  def Args(parser):
    base_classes.ZonalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'machineTypes')

  @property
  def service(self):
    return self.compute.machineTypes

  @property
  def resource_type(self):
    return 'machineTypes'


Describe.detailed_help = {
    'brief': 'Describe a Google Compute Engine machine type',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Google Compute
        Engine machine type.
        """,
}
