# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating firewall rules."""

from googlecloudsdk.calliope import base


class FirewallRules(base.Group):
  """List, create, and delete Google Compute Engine firewall rules."""


FirewallRules.detailed_help = {
    'brief': 'List, create, and delete Google Compute Engine firewall rules',
}
