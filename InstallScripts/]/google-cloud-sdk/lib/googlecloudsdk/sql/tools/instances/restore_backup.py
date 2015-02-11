# Copyright 2013 Google Inc. All Rights Reserved.

"""Restores a backup of a Cloud SQL instance."""
from googlecloudapis.apitools.base import py as apitools_base
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import remote_completion
from googlecloudsdk.sql import util


class RestoreBackup(base.Command):
  """Restores a backup of a Cloud SQL instance."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    instance = parser.add_argument(
        'instance',
        help='Cloud SQL instance ID.')
    cli = RestoreBackup.GetCLIGenerator()
    instance.completer = (remote_completion.RemoteCompletion.
                          GetCompleterForResource('sql.instances', cli))
    parser.add_argument(
        '--due-time',
        '-d',
        required=True,
        help='The time when this run was due to start in RFC 3339 format, for '
        'example 2012-11-15T16:19:00.094Z.')
    parser.add_argument(
        '--async',
        action='store_true',
        help='Do not wait for the operation to complete.')

  def Run(self, args):
    """Restores a backup of a Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the
      restoreBackup operation if the restoreBackup was successful.
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

    try:
      instance_resource = sql_client.instances.Get(
          instance_ref.Request())
      # At this point we support only one backup-config. So, just use that id.
      backup_config = instance_resource.settings.backupConfiguration[0].id

      result = sql_client.instances.RestoreBackup(
          sql_messages.SqlInstancesRestoreBackupRequest(
              project=instance_ref.project,
              instance=instance_ref.instance,
              backupConfiguration=backup_config,
              dueTime=args.due_time))

      operation_ref = resources.Create(
          'sql.operations',
          operation=result.operation,
          project=instance_ref.project,
          instance=instance_ref.instance,
      )

      if args.async:
        return sql_client.operations.Get(operation_ref.Request())

      util.WaitForOperation(
          sql_client, operation_ref, 'Restoring Cloud SQL instance')

      log.status.write('Restored [{instance}].\n'.format(
          instance=instance_ref))

      return None
    except apitools_base.HttpError as error:
      raise exceptions.HttpException(util.GetErrorMessage(error))

  def Display(self, unused_args, result):
    """Display prints information about what just happened to stdout.

    Args:
      unused_args: The same as the args in Run.
      result: A dict object representing the operations resource describing the
      restoreBackup operation if the restoreBackup was successful.
    """
    self.format(result)
