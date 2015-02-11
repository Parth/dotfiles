# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating URL maps."""

from googlecloudsdk.calliope import base


class URLMaps(base.Group):
  """List, create, and delete URL maps."""


URLMaps.detailed_help = {
    'brief': 'List, create, and delete URL maps',
}
