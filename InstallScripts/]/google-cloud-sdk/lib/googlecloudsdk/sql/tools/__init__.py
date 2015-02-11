# Copyright 2013 Google Inc. All Rights Reserved.

"""The super-group for the sql CLI.

The fact that this is a directory with
an __init__.py in it makes it a command group. The methods written below will
all be called by calliope (though they are all optional).
"""
import argparse
import os
import re


from googlecloudapis.sqladmin import v1beta1 as sql_v1beta1
from googlecloudapis.sqladmin import v1beta3 as sql_v1beta3
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import config
from googlecloudsdk.core import properties
from googlecloudsdk.core import resolvers
from googlecloudsdk.core import resources as cloud_resources
from googlecloudsdk.core.credentials import store as c_store
from googlecloudsdk.sql import util as util


_ACTIVE_VERSIONS = [
    'v1beta3',
    'v1beta1',
]


class SQL(base.Group):
  """Manage Cloud SQL databases."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--api-version', choices=_ACTIVE_VERSIONS, default='v1beta3',
        help=argparse.SUPPRESS)

  @exceptions.RaiseToolExceptionInsteadOf(c_store.Error)
  def Filter(self, context, args):
    """Context() is a filter function that can update the context.

    Args:
      context: The current context.
      args: The argparse namespace that was specified on the CLI or API.

    Returns:
      The updated context.
    """

    cloud_resources.SetParamDefault(
        api='sql', collection=None, param='project',
        resolver=resolvers.FromProperty(properties.VALUES.core.project))

    url = '/'.join([properties.VALUES.core.api_host.Get(), 'sql'])
    http = self.Http()

    context['sql_client-v1beta3'] = sql_v1beta3.SqladminV1beta3(
        get_credentials=False, url='/'.join([url, 'v1beta3']), http=http)
    context['sql_messages-v1beta3'] = sql_v1beta3
    context['registry-v1beta3'] = cloud_resources.REGISTRY.CloneAndSwitchAPIs(
        context['sql_client-v1beta3'])

    context['sql_client-v1beta1'] = sql_v1beta1.SqladminV1beta1(
        get_credentials=False, url='/'.join([url, 'v1beta1']), http=http)
    context['sql_messages-v1beta1'] = sql_v1beta1
    context['registry-v1beta1'] = cloud_resources.REGISTRY.CloneAndSwitchAPIs(
        context['sql_client-v1beta1'])


    context['sql_client'] = context['sql_client-'+args.api_version]
    context['sql_messages'] = context['sql_messages-'+args.api_version]
    context['registry'] = context['registry-'+args.api_version]

    return context
