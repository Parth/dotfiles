# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating HTTP health checks."""

from googlecloudsdk.calliope import base


class HttpHealthChecks(base.Group):
  """Read and manipulate HTTP health checks for load balanced instances."""


HttpHealthChecks.detailed_help = {
    'brief': ('Read and manipulate HTTP health checks for load balanced '
              'instances')
}
