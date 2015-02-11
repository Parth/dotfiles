# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating networks."""

from googlecloudsdk.calliope import base


class Networks(base.Group):
  """List, create, and delete Google Compute Engine networks."""


Networks.detailed_help = {
    'brief': 'List, create, and delete Google Compute Engine networks',
}
