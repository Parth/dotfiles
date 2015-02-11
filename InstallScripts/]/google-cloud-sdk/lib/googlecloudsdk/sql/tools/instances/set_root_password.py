# Copyright 2013 Google Inc. All Rights Reserved.

"""Sets the password of the MySQL root user."""

from googlecloudapis.apitools.base import py as apitools_base
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.sql import util


class SetRootPassword(base.Command):
  """Sets the password of the MySQL root user."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument(
        'instance',
        help='Cloud SQL instance ID.')
    password_group = parser.add_mutually_exclusive_group(required=True)
    password_group.add_argument(
        '--password',
        '-p',
        help='The password for the root user. WARNING: Setting password using '
        'this option can potentially expose the password to other users '
        'of this machine. Instead, you can use --password-file to get the'
        ' password from a file.')
    password_group.add_argument(
        '--password-file',
        help='The path to the filename which has the password to be set. The '
        'first line of the file will be interpreted as the password to be set.')
    parser.add_argument(
        '--async',
        action='store_true',
        help='Do not wait for the operation to complete.')

  def Run(self, args):
    """Sets the password of the MySQL root user.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the
      setRootPassword operation if the setRootPassword was successful.
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
      if args.password_file:
        with open(args.password_file) as f:
          password = f.readline()
      else:
        password = args.password

      result = sql_client.instances.SetRootPassword(
          sql_messages.SqlInstancesSetRootPasswordRequest(
              project=instance_ref.project,
              instance=instance_ref.instance,
              instanceSetRootPasswordRequest=(
                  sql_messages.InstanceSetRootPasswordRequest(
                      setRootPasswordContext=(
                          sql_messages.SetRootPasswordContext(
                              password=password))))))

      operation_ref = resources.Create(
          'sql.operations',
          operation=result.operation,
          project=instance_ref.project,
          instance=instance_ref.instance,
      )

      if args.async:
        return sql_client.operations.Get(operation_ref.Request())

      util.WaitForOperation(
          sql_client, operation_ref, 'Setting Cloud SQL instance password')

      log.status.write('Set password for [{instance}].\n'.format(
          instance=instance_ref))

      return None
    except apitools_base.HttpError as error:
      raise exceptions.HttpException(util.GetErrorMessage(error))

  # pylint: disable=unused-argument
  def Display(self, args, result):
    """Display prints information about what just happened to stdout.

    Args:
      args: The same as the args in Run.
      result: A dict object representing the operations resource describing the
          set-root-password operation if the set-root-password was successful.
    """
    self.format(result)
