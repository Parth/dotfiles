# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating project-level data."""

from googlecloudsdk.calliope import base


class ProjectInfo(base.Group):
  """Read and manipulate project-level data like quotas and metadata."""


ProjectInfo.detailed_help = {
    'brief': 'Read and manipulate project-level data like quotas and metadata',
}
