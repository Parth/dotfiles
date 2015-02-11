# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for creating instance templates."""
import collections

from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import image_utils
from googlecloudsdk.compute.lib import instance_utils
from googlecloudsdk.compute.lib import metadata_utils
from googlecloudsdk.compute.lib import utils


DISK_METAVAR = (
    'name=NAME [mode={ro,rw}] [boot={yes,no}] [device-name=DEVICE_NAME] '
    '[auto-delete={yes,no}]')


class Create(base_classes.BaseAsyncCreator, image_utils.ImageExpander):
  """Create Google Compute Engine virtual machine instance templates."""

  @staticmethod
  def Args(parser):
    metadata_utils.AddMetadataArgs(parser)
    instance_utils.AddDiskArgs(parser)
    instance_utils.AddLocalSsdArgs(parser)
    instance_utils.AddImageArgs(parser)
    instance_utils.AddCanIpForwardArgs(parser)
    instance_utils.AddAddressArgs(parser, instances=False)
    instance_utils.AddMachineTypeArgs(parser)
    instance_utils.AddMaintenancePolicyArgs(parser)
    instance_utils.AddNetworkArgs(parser)
    instance_utils.AddNoRestartOnFailureArgs(parser)
    instance_utils.AddScopeArgs(parser)
    instance_utils.AddTagsArgs(parser)

    parser.add_argument(
        '--description',
        help='Specifies a textual description for the instance template.')

    parser.add_argument(
        'name',
        metavar='NAME',
        help='The name of the instance template to create.')

  @property
  def service(self):
    return self.compute.instanceTemplates

  @property
  def method(self):
    return 'Insert'

  @property
  def resource_type(self):
    return 'instanceTemplates'

  def ValidateDiskFlags(self, args):
    """Validates the values of all disk-related flags.

    Args:
      args: the argparse arguments that this command was invoked with.

    Raises:
      ToolException: if any of the disk flags are invalid.
    """
    boot_disk_specified = False

    for disk in args.disk or []:
      disk_name = disk.get('name')
      if not disk_name:
        raise exceptions.ToolException(
            '[name] is missing in [--disk]. [--disk] value must be of the form '
            '[{0}].'.format(DISK_METAVAR))

      mode_value = disk.get('mode')
      if mode_value and mode_value not in ('rw', 'ro'):
        raise exceptions.ToolException(
            'Value for [mode] in [--disk] must be [rw] or [ro], not [{0}].'
            .format(mode_value))

      boot_value = disk.get('boot')
      if boot_value and boot_value not in ('yes', 'no'):
        raise exceptions.ToolException(
            'Value for [boot] in [--disk] must be [yes] or [no], not [{0}].'
            .format(boot_value))

      auto_delete_value = disk.get('auto-delete')
      if auto_delete_value and auto_delete_value not in ('yes', 'no'):
        raise exceptions.ToolException(
            'Value for [auto-delete] in [--disk] must be [yes] or [no], not '
            '[{0}].'.format(auto_delete_value))

      # If this is a boot disk and we have already seen a boot disk,
      # we need to fail because only one boot disk can be attached.
      if boot_value == 'yes':
        if boot_disk_specified:
          raise exceptions.ToolException(
              'Each instance can have exactly one boot disk. At least two '
              'boot disks were specified through [--disk].')
        else:
          boot_disk_specified = True

    if args.image and boot_disk_specified:
      raise exceptions.ToolException(
          'Each instance can have exactly one boot disk. One boot disk '
          'was specified through [--disk] and another through [--image].')

    if boot_disk_specified:
      if args.boot_disk_device_name:
        raise exceptions.ToolException(
            '[--boot-disk-device-name] can only be used when creating a new '
            'boot disk.')

      if args.boot_disk_type:
        raise exceptions.ToolException(
            '[--boot-disk-type] can only be used when creating a new boot '
            'disk.')

      if args.boot_disk_size:
        raise exceptions.ToolException(
            '[--boot-disk-size] can only be used when creating a new boot '
            'disk.')

      if args.no_boot_disk_auto_delete:
        raise exceptions.ToolException(
            '[--no-boot-disk-auto-delete] can only be used when creating a '
            'new boot disk.')

  def UseExistingBootDisk(self, args):
    """Returns True if the user has specified an existing boot disk.

    Args:
      args: the argparse arguments that this command was invoked with.

    Returns:
      bool: True if an existing boot disk is to be used, False otherwise.
    """
    return any(disk.get('boot') == 'yes' for disk in args.disk or [])

  def CreateAttachedPersistentDiskMessages(self, args):
    """Returns a list of AttachedDisk messages based on command-line args.

    Args:
      args: the argparse arguments that this command was invoked with.

    Returns:
      disks: a list of AttachedDisk message objects
    """
    disks = []

    for disk in args.disk or []:
      name = disk['name']

      # Resolves the mode.
      mode_value = disk.get('mode', 'rw')
      if mode_value == 'rw':
        mode = self.messages.AttachedDisk.ModeValueValuesEnum.READ_WRITE
      else:
        mode = self.messages.AttachedDisk.ModeValueValuesEnum.READ_ONLY

      boot = disk.get('boot') == 'yes'
      auto_delete = disk.get('auto-delete') == 'yes'

      attached_disk = self.messages.AttachedDisk(
          autoDelete=auto_delete,
          boot=boot,
          deviceName=disk.get('device-name'),
          mode=mode,
          source=name,
          type=self.messages.AttachedDisk.TypeValueValuesEnum.PERSISTENT)

      # The boot disk must end up at index 0.
      if boot:
        disks = [attached_disk] + disks
      else:
        disks.append(attached_disk)

    return disks

  def CreateDefaultBootAttachedDiskMessage(
      self, args, boot_disk_size_gb, image_uri):
    """Returns an AttachedDisk message for creating a new boot disk.

    Args:
      args: the argparse arguments that this command was invoked with.
      boot_disk_size_gb: size of the boot disk in GBs
      image_uri: the source image URI

    Returns:
      disk: an AttachedDisk message object
    """
    disk_type = None
    if args.boot_disk_type:
      disk_type = args.boot_disk_type

    return self.messages.AttachedDisk(
        autoDelete=not args.no_boot_disk_auto_delete,
        boot=True,
        deviceName=args.boot_disk_device_name,
        initializeParams=self.messages.AttachedDiskInitializeParams(
            sourceImage=image_uri,
            diskSizeGb=boot_disk_size_gb,
            diskType=disk_type),
        mode=self.messages.AttachedDisk.ModeValueValuesEnum.READ_WRITE,
        type=self.messages.AttachedDisk.TypeValueValuesEnum.PERSISTENT)

  def CreateServiceAccountMessages(self, args):
    """Returns a list of ServiceAccount messages corresponding to --scopes.

    Args:
      args: the argparse arguments that this command was invoked with.

    Returns:
      res: a list of ServiceAccount message objects

    Raises:
      ToolException: if the scopes are provided in an invalid format.
    """
    if args.no_scopes:
      scopes = []
    else:
      scopes = args.scopes or constants.DEFAULT_SCOPES

    accounts_to_scopes = collections.defaultdict(list)
    for scope in scopes:
      parts = scope.split('=')
      if len(parts) == 1:
        account = 'default'
        scope_uri = scope
      elif len(parts) == 2:
        account, scope_uri = parts
      else:
        raise exceptions.ToolException(
            '[{0}] is an illegal value for [--scopes]. Values must be of the '
            'form [SCOPE] or [ACCOUNT=SCOPE].'.format(scope))

      # Expands the scope if the user provided an alias like
      # "compute-rw".
      scope_uri = constants.SCOPES.get(scope_uri, scope_uri)

      accounts_to_scopes[account].append(scope_uri)

    res = []
    for account, scopes in sorted(accounts_to_scopes.iteritems()):
      res.append(self.messages.ServiceAccount(
          email=account,
          scopes=sorted(scopes)))
    return res

  def CreateNetworkInterfaceMessage(self, args):
    """Creates and returns a new NetworkInterface message.

    Args:
      args: the argparse arguments that this command was invoked with.

    Returns:
      network_interface: a NetworkInterface message object
    """
    network_ref = self.CreateGlobalReference(
        args.network, resource_type='networks')
    network_interface = self.messages.NetworkInterface(
        network=network_ref.SelfLink())

    if not args.no_address:
      access_config = self.messages.AccessConfig(
          name=constants.DEFAULT_ACCESS_CONFIG_NAME,
          type=self.messages.AccessConfig.TypeValueValuesEnum.ONE_TO_ONE_NAT)

      # If the user provided an external IP, populate the access
      # config with it.
      if args.address:
        access_config.natIP = args.address

      network_interface.accessConfigs = [access_config]

    return network_interface

  def CreateRequests(self, args):
    """Creates and returns an InstanceTemplates.Insert request.

    Args:
      args: the argparse arguments that this command was invoked with.

    Returns:
      request: a ComputeInstanceTemplatesInsertRequest message object
    """
    self.ValidateDiskFlags(args)
    instance_utils.ValidateLocalSsdFlags(args)

    boot_disk_size_gb = utils.BytesToGb(args.boot_disk_size)
    utils.WarnIfDiskSizeIsTooSmall(boot_disk_size_gb, args.boot_disk_type)

    instance_template_ref = self.CreateGlobalReference(args.name)

    metadata = metadata_utils.ConstructMetadataMessage(
        self.messages,
        metadata=args.metadata,
        metadata_from_file=args.metadata_from_file)

    network_interface = self.CreateNetworkInterfaceMessage(args)

    if args.maintenance_policy:
      on_host_maintenance = (
          self.messages.Scheduling.OnHostMaintenanceValueValuesEnum(
              args.maintenance_policy))
    else:
      on_host_maintenance = None

    scheduling = self.messages.Scheduling(
        automaticRestart=not args.no_restart_on_failure,
        onHostMaintenance=on_host_maintenance)

    service_accounts = self.CreateServiceAccountMessages(args)

    create_boot_disk = not self.UseExistingBootDisk(args)
    if create_boot_disk:
      image_uri, _ = self.ExpandImageFlag(
          args,
          return_image_resource=True)
    else:
      image_uri = None

    if args.tags:
      tags = self.messages.Tags(items=args.tags)
    else:
      tags = None

    persistent_disks = self.CreateAttachedPersistentDiskMessages(args)
    if create_boot_disk:
      boot_disk_list = [self.CreateDefaultBootAttachedDiskMessage(
          args, boot_disk_size_gb, image_uri)]
    else:
      boot_disk_list = []

    local_ssds = [
        instance_utils.CreateLocalSsdMessage(
            self, x.get('device-name'), x.get('interface'))
        for x in args.local_ssd or []]

    disks = boot_disk_list + persistent_disks + local_ssds

    request = self.messages.ComputeInstanceTemplatesInsertRequest(
        instanceTemplate=self.messages.InstanceTemplate(
            properties=self.messages.InstanceProperties(
                machineType=args.machine_type,
                disks=disks,
                canIpForward=args.can_ip_forward,
                metadata=metadata,
                networkInterfaces=[network_interface],
                serviceAccounts=service_accounts,
                scheduling=scheduling,
                tags=tags,
            ),
            description=args.description,
            name=instance_template_ref.Name(),
        ),
        project=self.context['project'])

    return [request]


Create.detailed_help = {
    'brief': 'Create a Compute Engine virtual machine instance template',
    'DESCRIPTION': """\
        *{command}* facilitates the creation of Google Compute Engine
        virtual machine instance templates. For example, running:

          $ {command} INSTANCE-TEMPLATE

        will create one instance templates called 'INSTANCE-TEMPLATE'.

        Instance templates are global resources, and can be used to create
        instances in any zone.
        """,
}
