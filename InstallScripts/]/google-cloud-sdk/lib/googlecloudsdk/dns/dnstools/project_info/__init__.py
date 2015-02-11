# Copyright 2013 Google Inc. All Rights Reserved.

"""Cloud DNS project group."""

from googlecloudsdk.calliope import base


class ProjectInfo(base.Group):
  """Manage Cloud DNS information for a project."""

  @staticmethod
  def Args(parser):
    """Set arguments for the project group."""
