# Copyright 2013 Google Inc. All Rights Reserved.

"""Cloud DNS managed-zone group."""

from googlecloudsdk.calliope import base


class ManagedZone(base.Group):
  """Manage Cloud DNS zones."""

  @staticmethod
  def Args(parser):
    """Set arguments for the managed-zone group."""


