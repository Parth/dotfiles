# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing instance templates."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.GlobalDescriber):
  """Describe a virtual machine instance template."""

  @staticmethod
  def Args(parser):
    base_classes.GlobalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'instanceTemplates')

  @property
  def service(self):
    return self.compute.instanceTemplates

  @property
  def resource_type(self):
    return 'instanceTemplates'


Describe.detailed_help = {
    'brief': 'Describe a virtual machine instance template',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Google Compute
        Engine virtual machine instance template.
        """,
}
