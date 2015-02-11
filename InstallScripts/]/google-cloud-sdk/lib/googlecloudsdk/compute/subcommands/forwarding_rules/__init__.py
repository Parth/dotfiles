# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating forwarding rules."""

from googlecloudsdk.calliope import base


class ForwardingRules(base.Group):
  """Read and manipulate forwarding rules to send traffic to load balancers."""


ForwardingRules.detailed_help = {
    'brief': ('Read and manipulate forwarding rules to send traffic to load '
              'balancers'),
}
