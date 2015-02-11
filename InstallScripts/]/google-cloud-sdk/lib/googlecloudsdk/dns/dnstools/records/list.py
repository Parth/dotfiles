# Copyright 2013 Google Inc. All Rights Reserved.

"""'dns resource-record-sets list' command."""

from apiclient import errors

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import properties
from googlecloudsdk.dns.lib import util


class List(base.Command):
  """List Cloud DNS resource record sets."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument('--name', required=False,
                        help='Restrict to only list records with this fully '
                        'qualified domain name.')
    parser.add_argument('--type', required=False,
                        help='Restrict to only list records of this type. '
                        'If present, the name parameter must also be present.')

  def Run(self, args):
    """Run 'dns resource-record-sets list'.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A list of records for this zone.
    """
    dns = self.context['dns']
    project = properties.VALUES.core.project.Get(required=True)

    request = dns.resourceRecordSets().list(
        project=project, managedZone=args.zone, name=args.name,
        type=args.type)

    try:
      result_list = []
      result = request.execute()
      result_list.extend(result['rrsets'])
      while 'nextPageToken' in result and result['nextPageToken'] is not None:
        request = dns.resourceRecordSets().list(
            project=project,
            managedZone=args.zone,
            pageToken=result['nextPageToken'])
        result = request.execute()
        result_list.extend(result['rrsets'])
      return result_list
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
