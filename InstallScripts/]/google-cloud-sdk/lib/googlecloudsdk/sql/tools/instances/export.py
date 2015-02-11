# Copyright 2013 Google Inc. All Rights Reserved.

"""Exports data from a Cloud SQL instance.

Exports data from a Cloud SQL instance to a Google Cloud Storage bucket as
a MySQL dump file.
"""

from googlecloudapis.apitools.base import py as apitools_base
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import remote_completion
from googlecloudsdk.sql import util


class Export(base.Command):
  """Exports data from a Cloud SQL instance.

  Exports data from a Cloud SQL instance to a Google Cloud Storage
  bucket as a MySQL dump file.
  """

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
    cli = Export.GetCLIGenerator()
    instance.completer = (remote_completion.RemoteCompletion.
                          GetCompleterForResource('sql.instances', cli))
    parser.add_argument(
        'uri',
        help='The path to the file in Google Cloud Storage where the export '
        'will be stored. The URI is in the form gs://bucketName/fileName. '
        'If the file already exists, the operation fails. If the filename '
        'ends with .gz, the contents are compressed.')
    parser.add_argument(
        '--database',
        '-d',
        required=False,
        nargs='+',
        type=str,
        help='Database (for example, guestbook) from which the export is made.'
        ' If unspecified, all databases are exported.')
    parser.add_argument(
        '--table',
        '-t',
        required=False,
        nargs='+',
        type=str,
        help='Tables to export from the specified database. If you specify '
        'tables, specify one and only one database.')
    parser.add_argument(
        '--async',
        action='store_true',
        help='Do not wait for the operation to complete.')

  def Run(self, args):
    """Exports data from a Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the export
      operation if the export was successful.
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

    export_request = sql_messages.SqlInstancesExportRequest(
        instance=instance_ref.instance,
        project=instance_ref.project,
        instancesExportRequest=sql_messages.InstancesExportRequest(
            exportContext=sql_messages.ExportContext(
                uri=args.uri,
                database=args.database or [],
                table=args.table or [],
            ),
        ),
    )

    try:
      result = sql_client.instances.Export(export_request)

      operation_ref = resources.Create(
          'sql.operations',
          operation=result.operation,
          project=instance_ref.project,
          instance=instance_ref.instance,
      )

      if args.async:
        return sql_client.operations.Get(operation_ref.Request())

      util.WaitForOperation(sql_client, operation_ref,
                            'Exporting Cloud SQL instance')

      log.status.write('Exported [{instance}] to [{bucket}].\n'.format(
          instance=instance_ref, bucket=args.uri))

      return None
    except apitools_base.HttpError as error:
      raise exceptions.HttpException(util.GetErrorMessage(error))

  def Display(self, unused_args, result):
    """Display prints information about what just happened to stdout.

    Args:
      unused_args: The same as the args in Run.
      result: A dict object representing the operations resource describing the
          export operation if the export was successful.
    """
    if result:
      self.format(result)

