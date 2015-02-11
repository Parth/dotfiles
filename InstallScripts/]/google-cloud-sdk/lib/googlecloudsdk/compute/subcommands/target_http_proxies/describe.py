# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing target HTTP proxies."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.GlobalDescriber):
  """Display detailed information about a target HTTP proxy."""

  @staticmethod
  def Args(parser):
    base_classes.GlobalDescriber.Args(parser)
    base_classes.AddFieldsFlag(parser, 'targetHttpProxies')

  @property
  def service(self):
    return self.compute.targetHttpProxies

  @property
  def resource_type(self):
    return 'targetHttpProxies'


Describe.detailed_help = {
    'brief': 'Display detailed information about a target HTTP proxy',
    'DESCRIPTION': """\
        *{command}* displays all data associated with a target HTTP proxy
        in a project.
        """,
}
