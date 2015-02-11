# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating operations."""

from googlecloudsdk.calliope import base


class Operations(base.Group):
  """Read and manipulate Google Compute Engine operations."""


Operations.detailed_help = {
    'brief': 'Read and manipulate Google Compute Engine operations',
}
