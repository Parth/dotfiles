# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating disks."""

from googlecloudsdk.calliope import base


class Disks(base.Group):
  """Read and manipulate Google Compute Engine disks."""


Disks.detailed_help = {
    'brief': 'Read and manipulate Google Compute Engine disks',
}
