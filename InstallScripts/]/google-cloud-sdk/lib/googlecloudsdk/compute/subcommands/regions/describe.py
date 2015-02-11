# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing regions."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.GlobalDescriber):
  """Describe a Google Compute Engine region."""

  @staticmethod
  def Args(parser):
    base_classes.GlobalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'regions')

  @property
  def service(self):
    return self.compute.regions

  @property
  def resource_type(self):
    return 'regions'


Describe.detailed_help = {
    'brief': 'Describe a Google Compute Engine region',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Google Compute
        Engine region.
        """,
}
