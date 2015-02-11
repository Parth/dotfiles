# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading regions."""

from googlecloudsdk.calliope import base


class Regions(base.Group):
  """List Google Compute Engine regions."""


Regions.detailed_help = {
    'brief': 'List Google Compute Engine regions',
}
