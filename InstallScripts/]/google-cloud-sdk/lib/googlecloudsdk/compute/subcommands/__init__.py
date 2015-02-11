# Copyright 2014 Google Inc. All Rights Reserved.
"""The super-group for the compute CLI."""
import argparse

from googlecloudsdk.calliope import base
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import utils
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import properties
from googlecloudsdk.core import resolvers
from googlecloudsdk.core import resources


class Compute(base.Group):
  """Read and manipulate Google Compute Engine resources."""


  def Filter(self, context, args):
    http = self.Http()
    core_values = properties.VALUES.core
    compute_values = properties.VALUES.compute
    context['http'] = http
    context['project'] = core_values.project.Get(required=True)

    for api, param, prop in (
        ('compute', 'project', core_values.project),
        ('resourceviews', 'projectName', core_values.project),
        ('compute', 'zone', compute_values.zone),
        ('resourceviews', 'zone', compute_values.zone),
        ('compute', 'region', compute_values.region),
        ('resourceviews', 'region', compute_values.region)):
      resources.SetParamDefault(
          api=api,
          collection=None,
          param=param,
          resolver=resolvers.FromProperty(prop))

    utils.UpdateContextEndpointEntries(context,
                                      )

Compute.detailed_help = {
    'brief': 'Read and manipulate Google Compute Engine resources',
}
