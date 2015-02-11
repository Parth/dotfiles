# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing target pools."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.RegionalDescriber):
  """Describe a target pool."""

  @staticmethod
  def Args(parser):
    base_classes.RegionalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'targetPools')

  @property
  def service(self):
    return self.compute.targetPools

  @property
  def resource_type(self):
    return 'targetPools'


Describe.detailed_help = {
    'brief': 'Describe a Google Compute Engine target pool',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Google Compute
        Engine target pool in a project.
        """,
}
