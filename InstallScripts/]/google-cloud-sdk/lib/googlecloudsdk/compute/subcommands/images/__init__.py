# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating images."""

from googlecloudsdk.calliope import base


class Images(base.Group):
  """List, create, and delete Google Compute Engine images."""


Images.detailed_help = {
    'brief': 'List, create, and delete Google Compute Engine images',
}
