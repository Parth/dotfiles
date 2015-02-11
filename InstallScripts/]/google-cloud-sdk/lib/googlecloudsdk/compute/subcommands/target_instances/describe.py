# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing target instances."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.ZonalDescriber):
  """Describe a target instance."""

  @staticmethod
  def Args(parser):
    base_classes.ZonalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'targetInstances')

  @property
  def service(self):
    return self.compute.targetInstances

  @property
  def resource_type(self):
    return 'targetInstances'


Describe.detailed_help = {
    'brief': 'Describe a target instance',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Google Compute
        Engine target instance in a project.
        """,
}
