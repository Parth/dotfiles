# Copyright 2013 Google Inc. All Rights Reserved.

"""Lists all available service tiers for Google Cloud SQL."""

from googlecloudapis.apitools.base import py as apitools_base
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import properties
from googlecloudsdk.core.util import list_printer
from googlecloudsdk.sql import util


class List(base.Command):
  """Lists all available service tiers for Google Cloud SQL."""

  def Run(self, unused_args):
    """Lists all available service tiers for Google Cloud SQL.

    Args:
      unused_args: argparse.Namespace, The arguments that this command was
          invoked with.

    Returns:
      A dict object that has the list of tier resources if the command ran
      successfully.
    Raises:
      HttpException: A http error response was received while executing api
          request.
      ToolException: An error other than http error occured while executing the
          command.
    """
    sql_client = self.context['sql_client']
    sql_messages = self.context['sql_messages']

    try:
      result = sql_client.tiers.List(sql_messages.SqlTiersListRequest(
          project=properties.VALUES.core.project.Get(required=True)))
      return iter(result.items)
    except apitools_base.HttpError as error:
      raise exceptions.HttpException(util.GetErrorMessage(error))

  def Display(self, unused_args, result):
    list_printer.PrintResourceList('sql.tiers', result)
