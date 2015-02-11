# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing HTTP health checks."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.GlobalDescriber):
  """Display detailed information about an HTTP health check."""

  @staticmethod
  def Args(parser):
    base_classes.GlobalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'httpHealthChecks')

  @property
  def service(self):
    return self.compute.httpHealthChecks

  @property
  def resource_type(self):
    return 'httpHealthChecks'


Describe.detailed_help = {
    'brief': 'Display detailed information about an HTTP health check',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a Google Compute
        Engine HTTP health check in a project.
        """,
}
