# Copyright 2013 Google Inc. All Rights Reserved.
"""Clones a Cloud SQL instance."""

from googlecloudapis.apitools.base import py as apitools_base
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import remote_completion
from googlecloudsdk.core.util import list_printer
from googlecloudsdk.sql import util


class Clone(base.Command):
  """Clones a Cloud SQL instance."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    source = parser.add_argument(
        'source',
        help='Cloud SQL instance ID of the source.')
    cli = Clone.GetCLIGenerator()
    source.completer = (remote_completion.RemoteCompletion.
                        GetCompleterForResource('sql.instances', cli))
    parser.add_argument(
        'destination',
        help='Cloud SQL instance ID of the clone.')
    filename_arg = parser.add_argument(
        '--bin-log-file-name',
        required=False,
        help='Binary log file for the source instance.')
    filename_arg.detailed_help = """\
        Represents the position (offset) inside the binary log file created by
        the source instance if it has binary logs enabled.
        If specified, is the point up to which the source instance is cloned.
        It must be specified along with --bin-log-file to form a valid binary
        log coordinates.
        e.g., 123 (a numeric value)
        """
    position_arg = parser.add_argument(
        '--bin-log-position',
        type=int,
        required=False,
        help='Position within the binary log file that represents the point'
        ' up to which the source is cloned.')
    position_arg.detailed_help = """\
        Represents the name of the binary log file created by the source
        instance if it has binary logs enabled.
        If specified, is the point up to which the source instance is cloned.
        It must be specified along with --bin-log-position to form a valid
        binary log coordinates.
        e.g., mysql-bin.000001
        """
    parser.add_argument(
        '--async',
        action='store_true',
        help='Do not wait for the operation to complete.')

  def Run(self, args):
    """Clones a Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the
      clone operation if the clone was successful.
    Raises:
      InvalidArgumentException: If one of the simulateneously required arguments
          is not specified.
      HttpException: A http error response was received while executing api
          request.
      ToolException: An error other than http error occured while executing the
          command.
    """
    sql_client = self.context['sql_client']
    sql_messages = self.context['sql_messages']
    resources = self.context['registry']

    util.ValidateInstanceName(args.source)
    util.ValidateInstanceName(args.destination)
    source_instance_ref = resources.Parse(
        args.source, collection='sql.instances')
    destination_instance_ref = resources.Parse(
        args.destination, collection='sql.instances')

    if source_instance_ref.project != destination_instance_ref.project:
      raise exceptions.ToolException(
          'The source and the clone instance must belong to the same project:'
          ' "{src}" != "{dest}".' . format(
              src=source_instance_ref.project,
              dest=destination_instance_ref.project))

    request = sql_messages.SqlInstancesCloneRequest(
        project=source_instance_ref.project,
        instancesCloneRequest=sql_messages.InstancesCloneRequest(
            cloneContext=sql_messages.CloneContext(
                sourceInstanceName=source_instance_ref.instance,
                destinationInstanceName=destination_instance_ref.instance)))

    if args.bin_log_file_name and args.bin_log_position:
      request.cloneContext.binLogCoordinates = sql_messages.BinLogCoordinates(
          binLogFileName=args.bin_log_file_name,
          binLogPosition=args.bin_log_position)
    elif args.bin_log_file_name or args.bin_log_position:
      raise exceptions.ToolException(
          'Both --bin-log-file and --bin-log-file-name must be specified to'
          ' represent a valid binary log coordinate up to which the source is'
          ' cloned.')

    try:
      result = sql_client.instances.Clone(request)

      operation_ref = resources.Create(
          'sql.operations',
          operation=result.operation,
          project=destination_instance_ref.project,
          instance=destination_instance_ref.instance,
      )

      if args.async:
        return sql_client.operations.Get(operation_ref.Request())

      util.WaitForOperation(sql_client, operation_ref,
                            'Cloning Cloud SQL instance')
      log.CreatedResource(destination_instance_ref)
      return sql_client.instances.Get(destination_instance_ref.Request())
    except apitools_base.HttpError as error:
      raise exceptions.HttpException(util.GetErrorMessage(error))

  def Display(self, unused_args, result):
    """Display prints information about what just happened to stdout.

    Args:
      unused_args: The same as the args in Run.
      result: A dict object representing the operations resource describing the
      clone operation if the clone was successful.
    """
    if result.kind == 'sql#instance':
      list_printer.PrintResourceList('sql.instances', [result])
    else:
      self.format(result)

  detailed_help = {
      'DESCRIPTION': """\
Creates a clone of the Cloud SQL instance. The source and the destination
instances must be in the same project. The clone once created will be
an independent Cloud SQL instance.

The binary log coordinates, if specified, act as the point up to which the
source instance is cloned. If not specified, the source instance is
cloned up to the most recent binary log coordintes at the time the command is
executed.
""",
      'EXAMPLES': """\
  ${command} myproject:instance-foo myproject:instance-bar
OR
  ${command} myproject:instance-foo myproject:instance-bar
        --bin-log-file mysql-bin.000020 --bin-log-position 170
""",
  }
