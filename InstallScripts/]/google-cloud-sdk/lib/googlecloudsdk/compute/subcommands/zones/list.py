# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing zones."""
from googlecloudsdk.compute.lib import base_classes


class List(base_classes.GlobalLister):
  """List Google Compute Engine zones."""

  @property
  def service(self):
    return self.compute.zones

  @property
  def resource_type(self):
    return 'zones'
