# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing addresses."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.GlobalRegionalDescriber):
  """Display detailed information about an address."""

  @staticmethod
  def Args(parser):
    base_classes.GlobalRegionalDescriber.Args(parser, 'addresses')

  @property
  def global_service(self):
    return self.compute.globalAddresses

  @property
  def regional_service(self):
    return self.compute.addresses

  @property
  def global_resource_type(self):
    return 'globalAddresses'

  @property
  def regional_resource_type(self):
    return 'addresses'

Describe.detailed_help = {
    'brief': 'Display detailed information about an address',
    'DESCRIPTION': """\
        *{command}* displays all data associated with an address in a project.
        """,
    'EXAMPLES': """\
        To get details about a global address, run:

          $ {command} ADDRESS --global

        To get details about a regional address, run:

          $ {command} ADDRESS --region us-central1
        """,
}
