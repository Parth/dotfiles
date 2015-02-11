# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading disk types."""

from googlecloudsdk.calliope import base


class DiskTypes(base.Group):
  """Read Google Compute Engine virtual disk types."""


DiskTypes.detailed_help = {
    'brief': 'Read Google Compute Engine virtual disk types',
}
