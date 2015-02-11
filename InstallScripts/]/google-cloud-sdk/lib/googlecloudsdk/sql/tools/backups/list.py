# Copyright 2013 Google Inc. All Rights Reserved.

"""Lists all backups associated with a given instance.

Lists all backups associated with a given instance and configuration
in the reverse chronological order of the enqueued time.
"""
from googlecloudapis.apitools.base import py as apitools_base
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core.util import list_printer
from googlecloudsdk.sql import util


class List(base.Command):
  """Lists all backups associated with a given instance.

  Lists all backups associated with a given Cloud SQL instance and
  configuration in the reverse chronological order of the enqueued time.
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use it to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument(
        '--limit',
        type=int,
        required=False,
        default=None,
        help='Maximum number of backups to list.')

  def Run(self, args):
    """Lists all backups associated with a given instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object that has the list of backup run resources if the command ran
      successfully.
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

    instance_resource = sql_client.instances.Get(instance_ref.Request())
    config_id = instance_resource.settings.backupConfiguration[0].id

    try:
      return apitools_base.YieldFromList(
          sql_client.backupRuns,
          sql_messages.SqlBackupRunsListRequest(
              project=instance_ref.project,
              instance=instance_ref.instance,
              # At this point we support only one backup-config. So, we just use
              # that id.
              backupConfiguration=config_id),
          args.limit)
    except apitools_base.HttpError as error:
      raise exceptions.HttpException(util.GetErrorMessage(error))

  def Display(self, unused_args, result):
    list_printer.PrintResourceList('sql.backupRuns', result)

