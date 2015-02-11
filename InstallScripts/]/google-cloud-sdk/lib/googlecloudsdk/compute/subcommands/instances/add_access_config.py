# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for adding access configs to virtual machine instances."""
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import utils


class AddAccessConfigInstances(base_classes.NoOutputAsyncMutator):
  """Add access configs to Google Compute Engine virtual machine instances."""

  @staticmethod
  def Args(parser):
    access_config_name = parser.add_argument(
        '--access-config-name',
        default=constants.DEFAULT_ACCESS_CONFIG_NAME,
        help='Specifies the name of the new access configuration.')
    access_config_name.detailed_help = """\
        Specifies the name of the new access configuration. ``{0}''
        is used as the default if this flag is not provided.
        """.format(constants.DEFAULT_ACCESS_CONFIG_NAME)

    address = parser.add_argument(
        '--address',
        help=('Specifies the external IP address of the new access '
              'configuration.'))
    address.detailed_help = """\
        Specifies the external IP address of the new access
        configuration. If this is not specified, then the service will
        choose an available ephemeral IP address. If an explicit IP
        address is given, then that IP address must be reserved by the
        project and not be in use by another resource.
        """

    network_interface = parser.add_argument(
        '--network-interface',
        default='nic0',
        help=('Specifies the name of the network interface on which to add '
              'the new access configuration.'))
    network_interface.detailed_help = """\
        Specifies the name of the network interface on which to add the new
        access configuration. If this is not provided, then "nic0" is used
        as the default.
        """

    parser.add_argument(
        'name',
        help='The name of the instance to add the access configuration to.')

    utils.AddZoneFlag(
        parser,
        resource_type='instance',
        operation_type='add an access config to')

  @property
  def service(self):
    return self.compute.instances

  @property
  def method(self):
    return 'AddAccessConfig'

  @property
  def resource_type(self):
    return 'instances'

  def CreateRequests(self, args):
    """Returns a list of request necessary for adding an access config."""
    instance_ref = self.CreateZonalReference(args.name, args.zone)

    request = self.messages.ComputeInstancesAddAccessConfigRequest(
        accessConfig=self.messages.AccessConfig(
            name=args.access_config_name,
            natIP=args.address,
            type=self.messages.AccessConfig.TypeValueValuesEnum.ONE_TO_ONE_NAT),
        instance=instance_ref.Name(),
        networkInterface=args.network_interface,
        project=self.project,
        zone=instance_ref.zone)

    return [request]


AddAccessConfigInstances.detailed_help = {
    'brief': ('Create an access configuration for the network interface of a '
              'Google Compute Engine virtual machine'),
    'DESCRIPTION': """\
        *{command}* is used to create access configurations for network
        interfaces of Google Compute Engine virtual machines.
        """,
}
