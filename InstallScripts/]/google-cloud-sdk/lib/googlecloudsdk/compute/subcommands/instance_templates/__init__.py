# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating instance templates."""

from googlecloudsdk.calliope import base


class InstanceTemplates(base.Group):
  """Read and manipulate Google Compute Engine instance templates."""


InstanceTemplates.detailed_help = {
    'brief': (
        'Read and manipulate Google Compute Engine instances templates'),
}
