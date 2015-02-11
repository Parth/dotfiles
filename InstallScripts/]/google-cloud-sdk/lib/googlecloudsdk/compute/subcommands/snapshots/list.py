# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing snapshots."""
from googlecloudsdk.compute.lib import base_classes


class List(base_classes.GlobalLister):
  """List Google Compute Engine snapshots."""

  @property
  def service(self):
    return self.compute.snapshots

  @property
  def resource_type(self):
    return 'snapshots'
