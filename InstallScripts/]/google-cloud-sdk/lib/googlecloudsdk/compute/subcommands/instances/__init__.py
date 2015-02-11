# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating instances."""

from googlecloudsdk.calliope import base


class Instances(base.Group):
  """Read and manipulate Google Compute Engine virtual machine instances."""


Instances.detailed_help = {
    'brief': (
        'Read and manipulate Google Compute Engine virtual machine instances'),
}
