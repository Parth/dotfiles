# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing zones."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.GlobalDescriber):
  """Describe a Google Compute Engine zone."""

  @staticmethod
  def Args(parser):
    base_classes.GlobalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'zones')

  @property
  def service(self):
    return self.compute.zones

  @property
  def resource_type(self):
    return 'zones'


Describe.detailed_help = {
    'brief': 'Describe a Google Compute Engine zone',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Google Compute
        Engine zone.
        """,
}
