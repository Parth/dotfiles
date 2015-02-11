# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating snapshots."""

from googlecloudsdk.calliope import base


class Snapshots(base.Group):
  """List, describe, and delete Google Compute Engine snapshots."""


Snapshots.detailed_help = {
    'brief': 'List, describe, and delete Google Compute Engine snapshots',
}
