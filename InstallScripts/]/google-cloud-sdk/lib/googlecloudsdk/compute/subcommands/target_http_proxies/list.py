# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing target HTTP proxies."""
from googlecloudsdk.compute.lib import base_classes


class List(base_classes.GlobalLister):
  """List target HTTP proxies."""

  @property
  def service(self):
    return self.compute.targetHttpProxies

  @property
  def resource_type(self):
    return 'targetHttpProxies'


List.detailed_help = {
    'brief': 'List targetHttpProxies',
    'DESCRIPTION': """\
        *{command}* lists summary information for the target HTTP proxies
        in a project.  The ``--uri'' option can be used to display the
        URIs for the target HTTP proxies.
        """,
}
