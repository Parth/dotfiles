# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating backend services."""

from googlecloudsdk.calliope import base


class BackendServices(base.Group):
  """List, create, and delete backend services."""


BackendServices.detailed_help = {
    'brief': 'List, create, and delete backend services',
}
