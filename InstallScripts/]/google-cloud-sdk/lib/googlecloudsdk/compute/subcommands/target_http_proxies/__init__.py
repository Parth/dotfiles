# Copyright 2014 Google Inc. All Rights Reserved.
"""Commands for reading and manipulating target HTTP proxies."""

from googlecloudsdk.calliope import base


class TargetHTTPProxies(base.Group):
  """List, create, and delete target HTTP proxies."""


TargetHTTPProxies.detailed_help = {
    'brief': 'List, create, and delete target HTTP proxies',
}
