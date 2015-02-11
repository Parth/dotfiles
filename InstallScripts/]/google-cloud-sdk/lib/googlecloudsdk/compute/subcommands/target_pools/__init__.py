# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating target pools."""

from googlecloudsdk.calliope import base


class TargetPools(base.Group):
  """Read and manipulate Google Compute Engine target pools."""


TargetPools.detailed_help = {
    'brief': 'Read and manipulate Google Compute Engine target pools'
             'to handle network load balancing',
}
