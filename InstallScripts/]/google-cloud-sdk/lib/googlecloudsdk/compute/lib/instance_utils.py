# Copyright 2014 Google Inc. All Rights Reserved.
"""Convenience functions for dealing with instances and instance templates."""

from googlecloudapis.compute.v1 import compute_v1_messages
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import image_utils

MIGRATION_OPTIONS = sorted(
    compute_v1_messages.Scheduling
    .OnHostMaintenanceValueValuesEnum.to_dict().keys())

LOCAL_SSD_INTERFACES = sorted(
    compute_v1_messages.AttachedDisk
    .InterfaceValueValuesEnum.to_dict().keys())

DEFAULT_LOCAL_SSD_INTERFACE = str(
    compute_v1_messages.AttachedDisk.InterfaceValueValuesEnum.SCSI)


def AddImageArgs(parser):
  """Adds arguments related to images for instances and instance-templates."""

  def AddImageHelp():
    return """
          Specifies the boot image for the instances. For each
          instance, a new boot disk will be created from the given
          image. Each boot disk will have the same name as the
          instance.

          {alias_table}

          When using this option, ``--boot-disk-device-name'' and
          ``--boot-disk-size'' can be used to override the boot disk's
          device name and size, respectively.

          By default, ``{default_image}'' is assumed for this flag.
          """.format(
              alias_table=image_utils.GetImageAliasTable(),
              default_image=constants.DEFAULT_IMAGE)

  image_choices = ['IMAGE'] + sorted(constants.IMAGE_ALIASES.keys())
  image = parser.add_argument(
      '--image',
      help='The image that the boot disk will be initialized with.',
      metavar=' | '.join(image_choices))
  image.detailed_help = AddImageHelp
  image_utils.AddImageProjectFlag(parser)


def AddCanIpForwardArgs(parser):
  parser.add_argument(
      '--can-ip-forward',
      action='store_true',
      help=('If provided, allows the instances to send and receive packets '
            'with non-matching destination or source IP addresses.'))


def AddLocalSsdArgs(parser):
  """Adds local SSD argument for instances and instance-templates."""

  local_ssd = parser.add_argument(
      '--local-ssd',
      action=arg_parsers.AssociativeList(spec={
          'device-name': str,
          'interface': (lambda x: x.upper()),
      }, append=True),
      help='(BETA) Specifies instances with attached local SSDs.',
      metavar='PROPERTY=VALUE',
      nargs='*')
  local_ssd.detailed_help = """
      Attaches a local SSD to the instances.

      This flag is currently in BETA and may change without notice.

      *device-name*::: Optional. A name that indicates the disk name
      the guest operating system will see.  If omitted, a device name
      of the form ``local-ssd-N'' will be used.

      *interface*::: Optional. The kind of disk interface exposed to the VM
      for this SSD.  Valid values are ``SCSI'' and ``NVME''.  SCSI is
      the default and is supported by more guest operating systems.  NVME
      may provide higher performance.
      """


def AddDiskArgs(parser):
  """Adds arguments related to disks for instances and instance-templates."""

  boot_disk_device_name = parser.add_argument(
      '--boot-disk-device-name',
      help='The name the guest operating system will see the boot disk as.')
  boot_disk_device_name.detailed_help = """\
      The name the guest operating system will see for the boot disk as.  This
      option can only be specified if a new boot disk is being created (as
      opposed to mounting an existing persistent disk).
      """
  boot_disk_size = parser.add_argument(
      '--boot-disk-size',
      type=arg_parsers.BinarySize(lower_bound='10GB'),
      help='The size of the boot disk.')
  boot_disk_size.detailed_help = """\
      The size of the boot disk. This option can only be specified if a new
      boot disk is being created (as opposed to mounting an existing
      persistent disk). The value must be a whole number followed by a size
      unit of ``KB'' for kilobyte, ``MB'' for megabyte, ``GB'' for gigabyte,
      or ``TB'' for terabyte. For example, ``10GB'' will produce a 10 gigabyte
      disk. If omitted, a default size of 200 GB is used. The minimum size a
      boot disk can have is 10 GB. Disk size must be a multiple of 1 GB.
      """

  boot_disk_type = parser.add_argument(
      '--boot-disk-type',
      help='The type of the boot disk.')
  boot_disk_type.detailed_help = """\
      The type of the boot disk. This option can only be specified if a new boot
      disk is being created (as opposed to mounting an existing persistent
      disk). To get a list of available disk types, run
      `$ gcloud compute disk-types list`.
      """

  parser.add_argument(
      '--no-boot-disk-auto-delete',
      action='store_true',
      help=('If provided, boot disks will not be automatically deleted '
            'when their instances are deleted.'))

  disk = parser.add_argument(
      '--disk',
      action=arg_parsers.AssociativeList(spec={
          'name': str,
          'mode': str,
          'boot': str,
          'device-name': str,
          'auto-delete': str,
      }, append=True),
      help='Attaches persistent disks to the instances.',
      metavar='PROPERTY=VALUE',
      nargs='+')
  disk.detailed_help = """
      Attaches persistent disks to the instances. The disks
      specified must already exist.

      *name*::: The disk to attach to the instances. When creating
      more than one instance and using this property, the only valid
      mode for attaching the disk is read-only (see *mode* below).

      *mode*::: Specifies the mode of the disk. Supported options
      are ``ro'' for read-only and ``rw'' for read-write. If
      omitted, ``rw'' is used as a default. It is an error for mode
      to be ``rw'' when creating more than one instance because
      read-write disks can only be attached to a single instance.

      *boot*::: If ``yes'', indicates that this is a boot disk. The
      virtual machines will use the first partition of the disk for
      their root file systems. The default value for this is ``no''.

      *device-name*::: An optional name that indicates the disk name
      the guest operating system will see. If omitted, a device name
      of the form ``persistent-disk-N'' will be used.

      *auto-delete*::: If ``yes'',  this persistent disk will be
      automatically deleted when the instance is deleted. However,
      if the disk is later detached from the instance, this option
      won't apply. The default value for this is ``no''.
      """


def AddAddressArgs(parser, instances=True):
  """Adds address arguments for instances and instance-templates."""
  addresses = parser.add_mutually_exclusive_group()
  addresses.add_argument(
      '--no-address',
      action='store_true',
      help=('If provided, the instances will not be assigned external IP '
            'addresses.'))
  address = addresses.add_argument(
      '--address',
      help='Assigns the given external address to the instance that is '
      'created.')
  if instances:
    address.detailed_help = """\
        Assigns the given external address to the instance that is created.
        The address may be an IP address or the name or URI of an address
        resource. This option can only be used when creating a single instance.
        """
  else:
    address.detailed_help = """\
        Assigns the given external IP address to the instance that is created.
        This option can only be used when creating a single instance.
        """


def AddMachineTypeArgs(parser):
  machine_type = parser.add_argument(
      '--machine-type',
      help='Specifies the machine type used for the instances.',
      default=constants.DEFAULT_MACHINE_TYPE)
  machine_type.detailed_help = """\
      Specifies the machine type used for the instances. To get a
      list of available machine types, run 'gcloud compute
      machine-types list'.
      """


def AddNetworkArgs(parser):
  network = parser.add_argument(
      '--network',
      default=constants.DEFAULT_NETWORK,
      help='Specifies the network that the instances will be part of.')
  network.detailed_help = """\
      Specifies the network that the instances will be part of. If
      omitted, the ``default'' network is used.
      """


def AddScopeArgs(parser):
  """Adds scope arguments for instances and instance-templates."""
  scopes_group = parser.add_mutually_exclusive_group()

  def AddScopesHelp():
    return """\
        Specifies service accounts and scopes for the
        instances. Service accounts generate access tokens that can be
        accessed through the instance metadata server and used to
        authenticate applications on the instance. The account can be
        either an email address or an alias corresponding to a
        service account. If account is omitted, the project's default
        service account is used. The default service account can be
        specified explicitly by using the alias ``default''. Example:

          $ {{command}} example-instance --scopes compute-rw me@project.gserviceaccount.com=storage-rw

        If this flag is not provided, the ``storage-ro'' scope is
        added to the instances. To create instances with no scopes,
        use ``--no-scopes'':

          $ {{command}} example-instance --no-scopes

        SCOPE can be either the full URI of the scope or an
        alias. Available aliases are:

        [options="header",format="csv",grid="none",frame="none"]
        |========
        Alias,URI
        {aliases}
        |========
        """.format(
            aliases='\n        '.join(
                ','.join(value) for value in
                sorted(constants.SCOPES.iteritems())))
  scopes = scopes_group.add_argument(
      '--scopes',
      help='Specifies service accounts and scopes for the instances.',
      metavar='[ACCOUNT=]SCOPE',
      nargs='+')
  scopes.detailed_help = AddScopesHelp

  scopes_group.add_argument(
      '--no-scopes',
      action='store_true',
      help=('If provided, the default scopes ({scopes}) are not added to the '
            'instances.'.format(scopes=', '.join(constants.DEFAULT_SCOPES))))


def AddTagsArgs(parser):
  tags = parser.add_argument(
      '--tags',
      help='A list of tags to apply to the instances.',
      metavar='TAG',
      nargs='+')
  tags.detailed_help = """\
      Specifies a list of tags to apply to the instances for
      identifying the instances to which network firewall rules will
      apply. See gcloud_compute_firewall-rules_create(1) for more
      details.
      """


def AddNoRestartOnFailureArgs(parser):
  no_restart_on_failure = parser.add_argument(
      '--no-restart-on-failure',
      action='store_true',
      default=False,
      help=('If provided, the instances are not restarted if they are '
            'terminated by Compute Engine.'))
  no_restart_on_failure.detailed_help = """\
      If provided, the instances will not be restarted if they are
      terminated by Compute Engine. By default, failed instances will be
      restarted. This does not affect terminations performed by the user.
  """


def AddMaintenancePolicyArgs(parser):
  maintenance_policy = parser.add_argument(
      '--maintenance-policy',
      choices=MIGRATION_OPTIONS,
      type=lambda x: x.upper(),
      help=('Specifies the behavior of the instances when their host '
            'machines undergo maintenance.'))
  maintenance_policy.detailed_help = """\
      Specifies the behavior of the instances when their host machines
      undergo maintenance. ``TERMINATE'' indicates that the instances
      should be terminated. ``MIGRATE'' indicates that the instances
      should be migrated to a new host. Choosing ``MIGRATE'' will
      temporarily impact the performance of instances during a
      migration event. If omitted, ``MIGRATE'' is assumed.
      """


def ValidateLocalSsdFlags(args):

  for local_ssd in args.local_ssd or []:
    interface = local_ssd.get('interface')
    if interface and interface not in LOCAL_SSD_INTERFACES:
      raise exceptions.ToolException(
          'Unexpected local SSD interface: [{given}]. '
          'Legal values are [{ok}].'
          .format(given=interface,
                  ok=', '.join(LOCAL_SSD_INTERFACES)))


def CreateLocalSsdMessage(command, device_name, interface, zone=None):
  """Create a message representing a local ssd."""

  if zone:
    disk_type_ref = command.CreateZonalReference('local-ssd', zone,
                                                 resource_type='diskTypes')
    disk_type = disk_type_ref.SelfLink()
  else:
    disk_type = 'local-ssd'

  maybe_interface_enum = (
      command.messages.AttachedDisk.InterfaceValueValuesEnum(interface)
      if interface else None)

  return command.messages.AttachedDisk(
      type=command.messages.AttachedDisk.TypeValueValuesEnum.SCRATCH,
      autoDelete=True,
      deviceName=device_name,
      interface=maybe_interface_enum,
      mode=command.messages.AttachedDisk.ModeValueValuesEnum.READ_WRITE,
      initializeParams=command.messages.AttachedDiskInitializeParams(
          diskType=disk_type),
      )
