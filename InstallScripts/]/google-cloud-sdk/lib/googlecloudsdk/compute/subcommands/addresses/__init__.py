# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating addresses."""

from googlecloudsdk.calliope import base


class Addresses(base.Group):
  """Read and manipulate Google Compute Engine addresses."""


Addresses.detailed_help = {
    'brief': 'Read and manipulate Google Compute Engine addresses',
}
