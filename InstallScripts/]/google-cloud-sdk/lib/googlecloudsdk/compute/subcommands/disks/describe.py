# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing disks."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.ZonalDescriber):
  """Describe a Google Compute Engine disk."""

  @staticmethod
  def Args(parser):
    base_classes.ZonalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'disks')

  @property
  def service(self):
    return self.compute.disks

  @property
  def resource_type(self):
    return 'disks'


Describe.detailed_help = {
    'brief': 'Describe a Google Compute Engine disk',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Google Compute
        Engine disk in a project.
        """,
}
