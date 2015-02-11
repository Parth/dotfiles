# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing regions."""
from googlecloudsdk.compute.lib import base_classes


class List(base_classes.GlobalLister):
  """List Google Compute Engine regions."""

  @property
  def service(self):
    return self.compute.regions

  @property
  def resource_type(self):
    return 'regions'
