# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing instances."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.ZonalDescriber):
  """Describe a virtual machine instance."""

  @staticmethod
  def Args(parser):
    base_classes.ZonalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'instances')

  @property
  def service(self):
    return self.compute.instances

  @property
  def resource_type(self):
    return 'instances'


Describe.detailed_help = {
    'brief': 'Describe a virtual machine instance',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Google Compute
        Engine virtual machine instance.
        """,
}
