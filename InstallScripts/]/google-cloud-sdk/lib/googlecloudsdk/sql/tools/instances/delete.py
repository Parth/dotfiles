# Copyright 2013 Google Inc. All Rights Reserved.
"""Deletes a Cloud SQL instance."""

from googlecloudapis.apitools.base import py as apitools_base
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import remote_completion
from googlecloudsdk.core.util import console_io
from googlecloudsdk.sql import util


class Delete(base.Command):
  """Deletes a Cloud SQL instance."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    delete = parser.add_argument(
        'instance',
        help='Cloud SQL instance ID.')
    cli = Delete.GetCLIGenerator()
    delete.completer = (remote_completion.RemoteCompletion.
                        GetCompleterForResource('sql.instances', cli))

  def Run(self, args):
    """Deletes a Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the delete
      operation if the delete was successful.
    Raises:
      HttpException: A http error response was received while executing api
          request.
      ToolException: An error other than http error occured while executing the
          command.
    """
    sql_client = self.context['sql_client']
    sql_messages = self.context['sql_messages']
    resources = self.context['registry']

    util.ValidateInstanceName(args.instance)
    instance_ref = resources.Parse(args.instance, collection='sql.instances')

    if not console_io.PromptContinue(
        'All of the instance data will be lost when the instance is deleted.'):
      return None
    try:
      result = sql_client.instances.Delete(
          sql_messages.SqlInstancesDeleteRequest(
              instance=instance_ref.instance,
              project=instance_ref.project))

      operation_ref = resources.Create(
          'sql.operations',
          operation=result.operation,
          project=instance_ref.project,
          instance=instance_ref.instance,
      )

      unused_operation = sql_client.operations.Get(operation_ref.Request())

      log.DeletedResource(instance_ref)

    except apitools_base.HttpError as error:
      raise exceptions.HttpException(util.GetErrorMessage(error))

  def Display(self, unused_args, result):
    """Display prints information about what just happened to stdout.

    Args:
      unused_args: The same as the args in Run.
      result: A dict object representing the operations resource describing the
          delete operation if the delete was successful.
    """
    self.format(result)

