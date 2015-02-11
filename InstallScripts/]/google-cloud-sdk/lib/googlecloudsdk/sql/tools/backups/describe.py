# Copyright 2013 Google Inc. All Rights Reserved.
"""Retrieves information about a backup."""

from googlecloudapis.apitools.base import py as apitools_base
from googlecloudapis.sqladmin import v1beta3 as sqladmin_v1beta3
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.sql import util


class Describe(base.Command):
  """Retrieves information about a backup.

  Retrieves information about a backup.
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument(
        'due_time',
        help='The time when this run is due to start in RFC 3339 format, for '
        'example 2012-11-15T16:19:00.094Z.')

  def Run(self, args):
    """Retrieves information about a backup.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object that has the backup run resource if the command ran
      successfully.
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

    try:
      instance = sql_client.instances.Get(instance_ref.Request())
      # At this point we support only one backup-config. So, just use that id.
      backup_config = instance.settings.backupConfiguration[0].id
      request = sqladmin_v1beta3.SqlBackupRunsGetRequest(
          project=instance_ref.project,
          instance=instance_ref.instance,
          backupConfiguration=backup_config,
          dueTime=args.due_time)
      return sql_client.backupRuns.Get(request)
    except apitools_base.HttpError as error:
      raise exceptions.HttpException(util.GetErrorMessage(error))

  def Display(self, unused_args, result):
    """Display prints information about what just happened to stdout.

    Args:
      unused_args: The same as the args in Run.
      result: A dict object that has the backupRun resource.
    """
    self.format(result)
