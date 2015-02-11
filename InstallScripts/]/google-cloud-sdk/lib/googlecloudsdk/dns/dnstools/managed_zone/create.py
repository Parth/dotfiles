# Copyright 2013 Google Inc. All Rights Reserved.

"""'dns managed-zone create' command."""

from apiclient import errors

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import properties
from googlecloudsdk.core.util import console_io
from googlecloudsdk.dns.lib import util


class Create(base.Command):
  """Create a new Cloud DNS managed zone."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument(
        'zone',
        help='Managed Zone name.')
    parser.add_argument(
        '--description',
        required=True,
        help='Human readable description of this zone.  Optional.')

    parser.add_argument(
        '--dns_name',
        required=True,
        help='A domain name spec, for example "foo.bar.com.".')

  def Run(self, args):
    """Run 'dns managed-zone create'.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.
    Returns:
      A dict object representing the changes resource obtained by the create
      operation if the create was successful.
    """
    project = properties.VALUES.core.project.Get(required=True)
    zone = {}
    zone['dnsName'] = args.dns_name
    zone['name'] = args.zone
    zone['description'] = args.description

    really = console_io.PromptContinue('Creating %s in %s' % (zone, project))
    if not really:
      return

    dns = self.context['dns']
    request = dns.managedZones().create(project=project, body=zone)
    try:
      result = request.execute()
      return result
    except errors.HttpError as error:
      raise exceptions.HttpException(util.GetError(error))
    except errors.Error as error:
      raise exceptions.ToolException(error)

  def Display(self, unused_args, result):
    """Display prints information about what just happened to stdout.

    Args:
      unused_args: The same as the args in Run.
      result: The results of the Run() method.
    """
    util.PrettyPrint(result)
