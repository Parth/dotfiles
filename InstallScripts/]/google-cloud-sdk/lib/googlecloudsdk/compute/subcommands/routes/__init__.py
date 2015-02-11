# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating routes."""

from googlecloudsdk.calliope import base


class Routes(base.Group):
  """Read and manipulate routes."""


Routes.detailed_help = {
    'brief': 'Read and manipulate routes',
}
