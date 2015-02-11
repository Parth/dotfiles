# Copyright 2014 Google Inc. All Rights Reserved.

"""Implements the command for SSHing into an instance."""
import getpass

from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import ssh_utils
from googlecloudsdk.compute.lib import utils


class SSH(ssh_utils.BaseSSHCLICommand):
  """SSH into a virtual machine instance."""

  @staticmethod
  def Args(parser):
    ssh_utils.BaseSSHCLICommand.Args(parser)

    parser.add_argument(
        '--command',
        help='A command to run on the virtual machine.')

    ssh_flags = parser.add_argument(
        '--ssh-flag',
        action='append',
        help='Additional flags to be passed to ssh.')
    ssh_flags.detailed_help = """\
        Additional flags to be passed to *ssh(1)*. It is recommended that flags
        be passed using an assignment operator and quotes. This flag will
        replace occurences of ``%USER%'' and ``%INSTANCE%'' with their
        dereferenced values. Example:

          $ {command} example-instance --zone us-central1-a --ssh-flag="-vvv" --ssh-flag="-L 80:%INSTANCE%:80"

        is equivalent to passing the flags ``--vvv'' and ``-L
        80:162.222.181.197:80'' to *ssh(1)* if the external IP address of
        'example-instance' is 162.222.181.197.
        """

    parser.add_argument(
        '--container',
        help="""\
            The name of a container inside of the virtual machine instance to
            connect to. This only applies to virtual machines that are using
            a Google container virtual machine image. For more information,
            see link:https://developers.google.com/compute/docs/containers[].
            """)

    user_host = parser.add_argument(
        'user_host',
        help='Specifies the instance to SSH into.',
        metavar='[USER@]INSTANCE')
    user_host.detailed_help = """\
        Specifies the instance to SSH into.

        ``USER'' specifies the username with which to SSH. If omitted,
        $USER from the environment is selected.
        """

    utils.AddZoneFlag(
        parser,
        resource_type='instance',
        operation_type='connect to')

  def Run(self, args):
    super(SSH, self).Run(args)
    parts = args.user_host.split('@')
    if len(parts) == 1:
      user = getpass.getuser()
      instance = parts[0]
    elif len(parts) == 2:
      user, instance = parts
    else:
      raise exceptions.ToolException(
          'Expected argument of the form [USER@]INSTANCE; received [{0}].'
          .format(args.user_host))

    instance_ref = self.CreateZonalReference(instance, args.zone)
    external_ip_address = self.GetInstanceExternalIpAddress(instance_ref)

    ssh_args = [self.ssh_executable]
    if not args.plain:
      ssh_args.extend(self.GetDefaultFlags())
      # Allocates a tty if no command was provided and a container was provided.
      if args.container and not args.command:
        ssh_args.append('-t')

    if args.ssh_flag:
      for flag in args.ssh_flag:
        dereferenced_flag = (
            flag.replace('%USER%', user)
            .replace('%INSTANCE%', external_ip_address))
        ssh_args.append(dereferenced_flag)

    ssh_args.append(ssh_utils.UserHost(user, external_ip_address))

    interactive_ssh = False
    if args.container:
      ssh_args.append('--')
      ssh_args.append('container_exec')
      ssh_args.append(args.container)
      # Runs the given command inside the given container if --command was
      # specified, otherwise runs /bin/sh.
      if args.command:
        ssh_args.append(args.command)
      else:
        ssh_args.append('/bin/sh')

    elif args.command:
      ssh_args.append('--')
      ssh_args.append(args.command)

    else:
      interactive_ssh = True

    self.ActuallyRun(args, ssh_args, user, external_ip_address,
                     interactive_ssh=interactive_ssh)


SSH.detailed_help = {
    'brief': 'SSH into a virtual machine instance',
    'DESCRIPTION': """\
        *{command}* is a thin wrapper around the *ssh(1)* command that
        takes care of authentication and the translation of the
        instance name into an IP address.

        This command ensures that the user's public SSH key is present
        in the project's metadata. If the user does not have a public
        SSH key, one is generated using *ssh-keygen(1)*.
        """,
    'EXAMPLES': """\
        To SSH into 'example-instance' in zone ``us-central1-a'', run:

          $ {command} example-instance --zone us-central1-a

        You can also run a command on the virtual machine. For
        example, to get a snapshot of the guest's process tree, run:

          $ {command} example-instance --zone us-central1-a --command "ps -ejH"

        If you are using the Google container virtual machine image, you
        can SSH into one of your containers with:

          $ {command} example-instance --zone us-central1-a --container CONTAINER
        """,
}
