# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating target instances."""

from googlecloudsdk.calliope import base


class TargetInstances(base.Group):
  """Read and manipulate Google Compute Engine virtual target instances."""


TargetInstances.detailed_help = {
    'brief': (
        'Read and manipulate Google Compute Engine virtual target instances'),
}
