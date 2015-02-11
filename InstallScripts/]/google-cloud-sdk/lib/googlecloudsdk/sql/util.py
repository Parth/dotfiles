# Copyright 2013 Google Inc. All Rights Reserved.

"""Common utility functions for sql tool."""
import json
import time

from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core.util import console_io


class OperationError(exceptions.ToolException):
  pass


def GetCertRefFromName(
    sql_client, sql_messages, resources, instance_ref, common_name):
  """Get a cert reference for a particular instance, given its common name.

  Args:
    sql_client: apitools.BaseApiClient, A working client for the sql version to
        be used.
    sql_messages: module, The module that defines the messages for the sql
        version to be used.
    resources: resources.Registry, The registry that can create resource refs
        for the sql version to be used.
    instance_ref: resources.Resource, The instance whos ssl cert is being
        fetched.
    common_name: str, The common name of the ssl cert to be fetched.

  Returns:
    resources.Resource, A ref for the ssl cert being fetched. Or None if it
    could not be found.
  """
  cert = GetCertFromName(sql_client, sql_messages, instance_ref, common_name)

  if not cert:
    return None

  return resources.Create(
      collection='sql.sslCerts',
      project=instance_ref.project,
      instance=instance_ref.instance,
      sha1Fingerprint=cert.sha1Fingerprint)


def GetCertFromName(
    sql_client, sql_messages, instance_ref, common_name):
  """Get a cert for a particular instance, given its common name.

  In versions of the SQL API up to at least v1beta3, the last parameter of the
  URL is the sha1fingerprint, which is not something writeable or readable by
  humans. Instead, the CLI will ask for the common name. To allow this, we first
  query all the ssl certs for the instance, and iterate through them to find the
  one with the correct common name.

  Args:
    sql_client: apitools.BaseApiClient, A working client for the sql version to
        be used.
    sql_messages: module, The module that defines the messages for the sql
        version to be used.
    instance_ref: resources.Resource, The instance whos ssl cert is being
        fetched.
    common_name: str, The common name of the ssl cert to be fetched.

  Returns:
    resources.Resource, A ref for the ssl cert being fetched. Or None if it
    could not be found.
  """
  certs = sql_client.sslCerts.List(
      sql_messages.SqlSslCertsListRequest(
          project=instance_ref.project,
          instance=instance_ref.instance))
  for cert in certs.items:
    if cert.commonName == common_name:
      return cert

  return None


def WaitForOperation(sql_client, operation_ref, message):
  """Wait for a Cloud SQL operation to complete.

  Args:
    sql_client: apitools.BaseApiClient, The client used to make requests.
    operation_ref: resources.Resource, A reference for the operation to poll.
    message: str, The string to print while polling.

  Returns:
    True if the operation succeeded without error.

  Raises:
    OperationError: If the operation has an error code.
  """

  with console_io.ProgressTracker(message, autotick=False) as pt:
    while True:
      op = sql_client.operations.Get(operation_ref.Request())
      if op.error:
        raise OperationError(op.error[0].code)
      pt.Tick()
      if op.state == 'DONE':
        return True
      if op.state == 'UNKNOWN':
        return False
      # TODO(user): As the cloud sql people for the best retry schedule.
      time.sleep(2)


def GetErrorMessage(error):
  content_obj = json.loads(error.content)
  return content_obj.get('error', {}).get('message', '')


def _ConstructSettingsFromArgs(sql_messages, args):
  """Constructs instance settings from the command line arguments.

  Args:
    sql_messages: module, The messages module that should be used.
    args: argparse.Namespace, The arguments that this command was invoked
        with.

  Returns:
    A settings object representing the instance settings.

  Raises:
    ToolException: An error other than http error occured while executing the
        command.
  """
  settings = sql_messages.Settings(
      tier=args.tier,
      pricingPlan=args.pricing_plan,
      replicationType=args.replication,
      activationPolicy=args.activation_policy)

  # these args are only present for the patch command
  no_assign_ip = getattr(args, 'no_assign_ip', False)
  no_require_ssl = getattr(args, 'no_require_ssl', False)
  clear_authorized_networks = getattr(args, 'clear_authorized_networks', False)
  clear_gae_apps = getattr(args, 'clear_gae_apps', False)

  if args.authorized_gae_apps:
    settings.authorizedGaeApplications = args.authorized_gae_apps
  elif clear_gae_apps:
    settings.authorizedGaeApplications = []

  if any([args.assign_ip, args.require_ssl, args.authorized_networks,
          no_assign_ip, no_require_ssl, clear_authorized_networks]):
    settings.ipConfiguration = sql_messages.IpConfiguration()
    if args.assign_ip:
      settings.ipConfiguration.enabled = True
    elif no_assign_ip:
      settings.ipConfiguration.enabled = False

    if args.authorized_networks:
      settings.ipConfiguration.authorizedNetworks = args.authorized_networks
    if clear_authorized_networks:
      # For patch requests, this field needs to be labeled explicitly cleared.
      settings.ipConfiguration.authorizedNetworks = []

    if args.require_ssl:
      settings.ipConfiguration.requireSsl = True
    if no_require_ssl:
      settings.ipConfiguration.requireSsl = False

  if any([args.follow_gae_app, args.gce_zone]):
    settings.locationPreference = sql_messages.LocationPreference(
        followGaeApplication=args.follow_gae_app,
        zone=args.gce_zone)

  enable_database_replication = getattr(
      args, 'enable_database_replication', False)
  no_enable_database_replication = getattr(
      args, 'no_enable_database_replication', False)
  if enable_database_replication:
    settings.databaseReplicationEnabled = True
  if no_enable_database_replication:
    settings.databaseReplicationEnabled = False

  return settings


def _SetDatabaseFlags(sql_messages, settings, args):
  if args.database_flags:
    settings.databaseFlags = []
    for (name, value) in args.database_flags.items():
      settings.databaseFlags.append(sql_messages.DatabaseFlags(
          name=name,
          value=value))
  elif getattr(args, 'clear_database_flags', False):
    settings.databaseFlags = []


def _SetBackupConfiguration(sql_messages, settings, args, original):
  """Sets the backup configuration for the instance."""
  # these args are only present for the patch command
  no_backup = getattr(args, 'no_backup', False)
  no_enable_bin_log = getattr(args, 'no_enable_bin_log', False)

  if original and (
      any([args.backup_start_time, args.enable_bin_log,
           no_backup, no_enable_bin_log])):
    if original.settings.backupConfiguration:
      backup_config = original.settings.backupConfiguration[0]
    else:
      backup_config = sql_messages.BackupConfiguration(
          startTime='00:00',
          enabled=False),
  elif not any([args.backup_start_time, args.enable_bin_log,
                no_backup, no_enable_bin_log]):
    return

  if not original:
    backup_config = sql_messages.BackupConfiguration(
        startTime='00:00',
        enabled=False)

  if args.backup_start_time:
    backup_config.startTime = args.backup_start_time
    backup_config.enabled = True
  if no_backup:
    if args.backup_start_time or args.enable_bin_log:
      raise exceptions.ToolException(
          ('Argument --no-backup not allowed with'
           ' --backup-start-time or --enable_bin_log'))
    backup_config.enabled = False

  if args.enable_bin_log:
    backup_config.binaryLogEnabled = True
  if no_enable_bin_log:
    backup_config.binaryLogEnabled = False

  settings.backupConfiguration = [backup_config]


def ConstructInstanceFromArgs(sql_messages, args, original=None):
  """Construct a Cloud SQL instance from command line args.

  Args:
    sql_messages: module, The messages module that should be used.
    args: argparse.Namespace, The CLI arg namespace.
    original: sql_messages.DatabaseInstance, The original instance, if some of
        it might be used to fill fields in the new one.

  Returns:
    sql_messages.DatabaseInstance, The constructed (and possibly partial)
    database instance.

  Raises:
    ToolException: An error other than http error occured while executing the
        command.
  """
  settings = _ConstructSettingsFromArgs(sql_messages, args)
  _SetBackupConfiguration(sql_messages, settings, args, original)
  _SetDatabaseFlags(sql_messages, settings, args)


  # these flags are only present for the create command
  region = getattr(args, 'region', None)
  database_version = getattr(args, 'database_version', None)

  instance_resource = sql_messages.DatabaseInstance(
      region=region,
      databaseVersion=database_version,
      masterInstanceName=getattr(args, 'master_instance_name', None),
      settings=settings)

  return instance_resource


def ValidateInstanceName(instance_name):
  if ':' in instance_name:
    possible_project = instance_name[:instance_name.rindex(':')]
    possible_instance = instance_name[instance_name.rindex(':')+1:]
    raise exceptions.ToolException("""\
Instance names cannot contain the ':' character. If you meant to indicate the
project for [{instance}], use only '{instance}' for the argument, and either add
'--project {project}' to the command line or first run
  $ gcloud config set project {project}
""".format(project=possible_project, instance=possible_instance))
