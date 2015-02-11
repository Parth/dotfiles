# Copyright 2014 Google Inc. All Rights Reserved.

"""Retrieves information about a Cloud SQL instance operation."""

from googlecloudapis.apitools.base import py as apitools_base
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core.util import list_printer
from googlecloudsdk.sql import util


class Wait(base.Command):
  """Waits for one or more operations to complete."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use it to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument(
        'operation',
        nargs='+',
        help='An identifier that uniquely identifies the operation.')

  def Run(self, args):
    """Wait for a Cloud SQL instance operation.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Yields:
      Operations that were waited for.
    Raises:
      HttpException: A http error response was received while executing api
          request.
      ToolException: An error other than http error occured while executing the
          command.
    """
    sql_client = self.context['sql_client']
    resources = self.context['registry']

    util.ValidateInstanceName(args.instance)
    instance_ref = resources.Parse(args.instance, collection='sql.instances')

    for op in args.operation:
      operation_ref = resources.Parse(
          op, collection='sql.operations',
          params={'project': instance_ref.project,
                  'instance': instance_ref.instance})
      try:
        util.WaitForOperation(
            sql_client, operation_ref,
            'Waiting for [{operation}]'.format(operation=operation_ref))
        yield sql_client.operations.Get(operation_ref.Request())
      except apitools_base.HttpError as error:
        raise exceptions.HttpException(util.GetErrorMessage(error))

  def Display(self, unused_args, result):
    list_printer.PrintResourceList('sql.operations', result)
