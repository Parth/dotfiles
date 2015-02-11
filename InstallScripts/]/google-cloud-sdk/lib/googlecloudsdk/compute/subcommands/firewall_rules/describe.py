# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing firewall rules."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.GlobalDescriber):
  """Describe Google Compute Engine firewall rule."""

  @staticmethod
  def Args(parser):
    base_classes.GlobalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'firewalls')

  @property
  def service(self):
    return self.compute.firewalls

  @property
  def resource_type(self):
    return 'firewalls'


Describe.detailed_help = {
    'brief': 'Describe a Google Compute Engine firewall rule',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Google Compute
        Engine firewall rule in a project.
        """,
}
