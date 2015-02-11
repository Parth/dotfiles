# Copyright 2013 Google Inc. All Rights Reserved.

"""Updates the settings of a Cloud SQL instance."""
from googlecloudapis.apitools.base import py as apitools_base
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import remote_completion
from googlecloudsdk.core.util import console_io
from googlecloudsdk.core.util import resource_printer
from googlecloudsdk.sql import util


class Patch(base.Command):
  """Updates the settings of a Cloud SQL instance."""

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
        help='The activation policy for this instance. This specifies when the '
        'instance should be activated and is applicable only when the '
        'instance state is RUNNABLE.')
    assign_ip_group = parser.add_mutually_exclusive_group()
    assign_ip_group.add_argument(
        '--assign-ip',
        required=False,
        action='store_true',
        help='Specified if the instance must be assigned an IP address.')
    assign_ip_group.add_argument(
        '--no-assign-ip',
        required=False,
        action='store_true',
        help='Specified if the assigned IP address must be revoked.')
    gae_apps_group = parser.add_mutually_exclusive_group()
    gae_apps_group.add_argument(
        '--authorized-gae-apps',
        required=False,
        nargs='+',
        type=str,
        help='A list of App Engine app IDs that can access this instance.')
    gae_apps_group.add_argument(
        '--clear-gae-apps',
        required=False,
        action='store_true',
        help=('Specified to clear the list of App Engine apps that can access '
              'this instance.'))
    networks_group = parser.add_mutually_exclusive_group()
    networks_group.add_argument(
        '--authorized-networks',
        required=False,
        nargs='+',
        type=str,
        help='The list of external networks that are allowed to connect to the '
        'instance. Specified in CIDR notation, also known as \'slash\' '
        'notation (e.g. 192.168.100.0/24).')
    networks_group.add_argument(
        '--clear-authorized-networks',
        required=False,
        action='store_true',
        help='Clear the list of external networks that are allowed to connect '
        'to the instance.')
    backups_group = parser.add_mutually_exclusive_group()
    backups_group.add_argument(
        '--backup-start-time',
        required=False,
        help='The start time of daily backups, specified in the 24 hour format '
        '- HH:MM, in the UTC timezone.')
    backups_group.add_argument(
        '--no-backup',
        required=False,
        action='store_true',
        help='Specified if daily backup should be disabled.')
    database_flags_group = parser.add_mutually_exclusive_group()
    database_flags_group.add_argument(
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
    database_flags_group.add_argument(
        '--clear-database-flags',
        required=False,
        action='store_true',
        help='Clear the database flags set on the instance. '
        'WARNING: Instance will be restarted.')
    bin_log_group = parser.add_mutually_exclusive_group()
    bin_log_group.add_argument(
        '--enable-bin-log',
        required=False,
        action='store_true',
        help='Specified if binary log should be enabled. If backup '
        'configuration is disabled, binary log should be disabled as well.')
    bin_log_group.add_argument(
        '--no-enable-bin-log',
        required=False,
        action='store_true',
        help='Specified if binary log should be disabled.')
    parser.add_argument(
        '--follow-gae-app',
        required=False,
        help='The App Engine app this instance should follow. It must be in '
        'the same region as the instance. '
        'WARNING: Instance may be restarted.')
    parser.add_argument(
        '--gce-zone',
        required=False,
        help='The preferred Compute Engine zone (e.g. us-central1-a, '
        'us-central1-b, etc.). '
        'WARNING: Instance may be restarted.')
    instance = parser.add_argument(
        'instance',
        help='Cloud SQL instance ID.')
    cli = Patch.GetCLIGenerator()
    instance.completer = (remote_completion.RemoteCompletion.
                          GetCompleterForResource('sql.instances', cli))
    parser.add_argument(
        '--pricing-plan',
        '-p',
        required=False,
        choices=['PER_USE', 'PACKAGE'],
        help='The pricing plan for this instance.')
    parser.add_argument(
        '--replication',
        required=False,
        choices=['SYNCHRONOUS', 'ASYNCHRONOUS'],
        help='The type of replication this instance uses.')
    require_ssl_group = parser.add_mutually_exclusive_group()
    require_ssl_group.add_argument(
        '--require-ssl',
        required=False,
        action='store_true',
        help='Specified if the mysqld should default to \'REQUIRE X509\' for '
        'users connecting over IP.')
    require_ssl_group.add_argument(
        '--no-require-ssl',
        required=False,
        action='store_true',
        help='Specified if the mysqld should not default to \'REQUIRE X509\' '
        'for users connecting over IP.')
    parser.add_argument(
        '--tier',
        '-t',
        required=False,
        help='The tier of service for this instance, for example D0, D1. '
        'WARNING: Instance will be restarted.')
    database_replication_group = parser.add_mutually_exclusive_group()
    database_replication_group.add_argument(
        '--enable-database-replication',
        required=False,
        action='store_true',
        help='Specified if database replication is enabled. Applicable only '
        'for read replica instance(s). WARNING: Instance will be restarted.')
    database_replication_group.add_argument(
        '--no-enable-database-replication',
        required=False,
        action='store_true',
        help='Specified if database replication is disabled. Applicable only '
        'for read replica instance(s). WARNING: Instance will be restarted.')
    parser.add_argument(
        '--async',
        action='store_true',
        help='Do not wait for the operation to complete.')
    parser.add_argument(
        '--diff',
        action='store_true',
        help='Show what changed as a result of the update.')

  def PrintAndConfirmWarningMessage(self, args):
    """Print and confirm warning indicating the effect of applying the patch."""
    continue_msg = None
    if any([args.tier, args.database_flags, args.clear_database_flags,
            args.enable_database_replication,
            args.no_enable_database_replication]):
      continue_msg = ('WARNING: This patch modifies a value that requires '
                      'your instance to be restarted. Submitting this patch '
                      'will immediately restart your instance if it\'s running.'
                     )
    else:
      if any([args.follow_gae_app, args.gce_zone]):
        continue_msg = ('WARNING: This patch modifies the zone your instance '
                        'is set to run in, which may require it to be moved. '
                        'Submitting this patch will restart your instance '
                        'if it is running in a different zone.')

    if continue_msg and not console_io.PromptContinue(continue_msg):
      raise exceptions.ToolException('canceled by the user.')

  def Run(self, args):
    """Updates settings of a Cloud SQL instance using the patch api method.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the patch
      operation if the patch was successful.
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
      original_instance_resource = sql_client.instances.Get(
          instance_ref.Request())
    except apitools_base.HttpError as error:
      raise exceptions.HttpException(util.GetErrorMessage(error))

    cleared_fields = []

    if args.clear_gae_apps:
      cleared_fields.append('settings.authorizedGaeApplications')
    if args.clear_authorized_networks:
      cleared_fields.append('settings.ipConfiguration.authorizedNetworks')
    if args.clear_database_flags:
      cleared_fields.append('settings.databaseFlags')

    patch_instance = util.ConstructInstanceFromArgs(
        sql_messages, args, original=original_instance_resource)
    patch_instance.project = instance_ref.project
    patch_instance.instance = instance_ref.instance

    log.status.write(
        'The following message will be used for the patch API method.\n')
    log.status.write(
        apitools_base.MessageToJson(
            patch_instance, include_fields=cleared_fields)+'\n')

    self.PrintAndConfirmWarningMessage(args)

    try:
      with sql_client.IncludeFields(cleared_fields):
        result = sql_client.instances.Patch(patch_instance)

      operation_ref = resources.Create(
          'sql.operations',
          operation=result.operation,
          project=instance_ref.project,
          instance=instance_ref.instance,
      )

      if args.async:
        return sql_client.operations.Get(operation_ref.Request())

      util.WaitForOperation(
          sql_client, operation_ref, 'Patching Cloud SQL instance')

      log.UpdatedResource(instance_ref)

      if args.diff:
        try:
          changed_instance_resource = sql_client.instances.Get(
              instance_ref.Request())
        except apitools_base.HttpError as error:
          raise exceptions.HttpException(util.GetErrorMessage(error))
        return resource_printer.ResourceDiff(
            original_instance_resource, changed_instance_resource)

      return sql_client.instances.Get(instance_ref.Request())

    except apitools_base.HttpError as error:
      raise exceptions.HttpException(util.GetErrorMessage(error))

  def Display(self, args, result):
    """Display prints information about what just happened to stdout.

    Args:
      args: The same as the args in Run.
      result: A dict object representing the operations resource describing the
      patch operation if the patch was successful.
    """
    if args.diff:
      resource_printer.Print(result, 'text')
