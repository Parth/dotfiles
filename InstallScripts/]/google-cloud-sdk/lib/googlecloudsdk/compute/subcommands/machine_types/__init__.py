# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading machine types."""

from googlecloudsdk.calliope import base


class MachineTypes(base.Group):
  """Read Google Compute Engine virtual machine types."""


MachineTypes.detailed_help = {
    'brief': 'Read Google Compute Engine virtual machine types',
}
