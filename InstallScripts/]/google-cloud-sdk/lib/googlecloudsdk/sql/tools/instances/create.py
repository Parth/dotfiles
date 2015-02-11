# Copyright 2013 Google Inc. All Rights Reserved.

"""Creates a new Cloud SQL instance."""
import argparse

from googlecloudapis.apitools.base import py as apitools_base
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core.util import console_io
from googlecloudsdk.core.util import list_printer
from googlecloudsdk.sql import util


class Create(base.Command):
  """Creates a new Cloud SQL instance."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Please add arguments in alphabetical order except for no- or a clear-
    pair for that argument which can follow the argument itself.
    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument(
        '--activation-policy',
        required=False,
        choices=['ALWAYS', 'NEVER', 'ON_DEMAND'],
        default=None,
        help='The activation policy for this instance. This specifies when the '
        'instance should be activated and is applicable only when the '
        'instance state is RUNNABLE.')
    parser.add_argument(
        '--assign-ip',
        required=False,
        action='store_true',
        help='Specified if the instance must be assigned an IP address.')
    parser.add_argument(
        '--authorized-gae-apps',
        required=False,
        nargs='+',
        type=str,
        default=[],
        help='List of App Engine app IDs that can access this instance.')
    parser.add_argument(
        '--authorized-networks',
        required=False,
        nargs='+',
        type=str,
        default=[],
        help='The list of external networks that are allowed to connect to the'
        ' instance. Specified in CIDR notation, also known as \'slash\' '
        'notation (e.g. 192.168.100.0/24).')
    parser.add_argument(
        '--backup-start-time',
        required=False,
        help='The start time of daily backups, specified in the 24 hour format '
        '- HH:MM, in the UTC timezone.')
    parser.add_argument(
        '--no-backup',
        required=False,
        action='store_true',
        help='Specified if daily backup should be disabled.')
    parser.add_argument(
        '--database-version',
        required=False,
        choices=['MYSQL_5_5', 'MYSQL_5_6'],
        default='MYSQL_5_5',
        help='The database engine type and version. Can be MYSQL_5_5 or '
        'MYSQL_5_6.')
    parser.add_argument(
        '--enable-bin-log',
        required=False,
        action='store_true',
        help='Specified if binary log should be enabled. If backup '
        'configuration is disabled, binary log must be disabled as well.')
    parser.add_argument(
        '--follow-gae-app',
        required=False,
        help='The App Engine app this instance should follow. It must be in '
        'the same region as the instance.')
    parser.add_argument(
        '--gce-zone',
        required=False,
        help='The preferred Compute Engine zone (e.g. us-central1-a, '
        'us-central1-b, etc.).')
    parser.add_argument(
        'instance',
        help='Cloud SQL instance ID.')
    parser.add_argument(
        '--master-instance-name',
        required=False,
        help='Name of the instance which will act as master in the replication '
        'setup. The newly created instance will be a read replica of the '
        'specified master instance.')
    parser.add_argument(
        '--pricing-plan',
        '-p',
        required=False,
        choices=['PER_USE', 'PACKAGE'],
        default='PER_USE',
        help='The pricing plan for this instance.')
    parser.add_argument(
        '--region',
        required=False,
        choices=['asia-east1', 'europe-west1', 'us-central', 'us-east1'],
        default='us-central',
        help='The geographical region. Can be asia-east1, europe-west1, '
        'or us-central.')
    parser.add_argument(
        '--replication',
        required=False,
        choices=['SYNCHRONOUS', 'ASYNCHRONOUS'],
        default=None,
        help='The type of replication this instance uses.')
    parser.add_argument(
        '--require-ssl',
        required=False,
        action='store_true',
        help='Specified if users connecting over IP must use SSL.')
    parser.add_argument(
        '--tier',
        '-t',
        required=False,
        default='D1',
        help='The tier of service for this instance, for example D0, D1.')
    parser.add_argument(
        '--database-flags',
        required=False,
        nargs='+',
        action=arg_parsers.AssociativeList(),
        help='A space-separated list of database flags to set on the instance. '
        'Use an equals sign to separate flag name and value. Flags without '
        'values, like skip_grant_tables, can be written out without a value '
        'after, e.g., `skip_grant_tables=`. Use on/off for '
        'booleans. View the Instance Resource API for allowed flags. '
        '(e.g., `--database-flags max_allowed_packet=55555 skip_grant_tables= '
        'log_output=1`)')
    parser.add_argument(
        '--async',
        action='store_true',
        help='Do not wait for the operation to complete.')

  def Run(self, args):
    """Creates a new Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the create
      operation if the create was successful.
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

    instance_resource = util.ConstructInstanceFromArgs(sql_messages, args)

    if args.master_instance_name:
      replication = 'ASYNCHRONOUS'
      activation_policy = 'ALWAYS'
    else:
      replication = 'SYNCHRONOUS'
      activation_policy = 'ON_DEMAND'
    if not args.replication:
      instance_resource.settings.replicationType = replication
    if not args.activation_policy:
      instance_resource.settings.activationPolicy = activation_policy

    instance_resource.project = instance_ref.project
    instance_resource.instance = instance_ref.instance

    if args.pricing_plan == 'PACKAGE':
      if not console_io.PromptContinue(
          'Charges will begin accruing immediately. Really create Cloud '
          'SQL instance?'):
        raise exceptions.ToolException('canceled by the user.')

    try:
      result = sql_client.instances.Insert(instance_resource)

      operation_ref = resources.Create(
          'sql.operations',
          operation=result.operation,
          project=instance_ref.project,
          instance=instance_ref.instance,
      )

      if args.async:
        return sql_client.operations.Get(operation_ref.Request())

      util.WaitForOperation(
          sql_client, operation_ref, 'Creating Cloud SQL instance')

      log.CreatedResource(instance_ref)

      return sql_client.instances.Get(instance_ref.Request())
    except apitools_base.HttpError as error:
      raise exceptions.HttpException(util.GetErrorMessage(error))

  def Display(self, unused_args, result):
    """Display prints information about what just happened to stdout.

    Args:
      unused_args: The same as the args in Run.
      result: The database created, or the operation if async.
    """
    if result.kind == 'sql#instance':
      list_printer.PrintResourceList('sql.instances', [result])
    else:
      self.format(result)
