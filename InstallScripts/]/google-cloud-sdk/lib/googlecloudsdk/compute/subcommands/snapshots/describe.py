# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing snapshots."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.GlobalDescriber):
  """Describe a Google Compute Engine snapshot."""

  @staticmethod
  def Args(parser):
    base_classes.GlobalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'snapshots')

  @property
  def service(self):
    return self.compute.snapshots

  @property
  def resource_type(self):
    return 'snapshots'


Describe.detailed_help = {
    'brief': 'Describe a Google Compute Engine snapshot',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Google Compute
        Engine snapshot in a project.
        """,
}
