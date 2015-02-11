# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading zones."""

from googlecloudsdk.calliope import base


class Zones(base.Group):
  """List Google Compute Engine zones."""


Zones.detailed_help = {
    'brief': 'List Google Compute Engine zones'
}
