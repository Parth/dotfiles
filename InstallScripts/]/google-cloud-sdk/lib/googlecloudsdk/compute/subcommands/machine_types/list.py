# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing machine types."""
from googlecloudsdk.compute.lib import base_classes


class List(base_classes.ZonalLister):
  """List Google Compute Engine machine types."""

  @property
  def service(self):
    return self.compute.machineTypes

  @property
  def resource_type(self):
    return 'machineTypes'
