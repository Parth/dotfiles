# Copyright 2013 Google Inc. All Rights Reserved.

"""Provide commands for managing SSL certificates of Cloud SQL instances."""


from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import remote_completion


class SslCerts(base.Group):
  """Provide commands for managing SSL certificates of Cloud SQL instances.

  Provide commands for managing SSL certificates of Cloud SQL instances,
  including creating, deleting, listing, and getting information about
  certificates.
  """

  @staticmethod
  def Args(parser):
    instance = parser.add_argument(
        '--instance',
        '-i',
        help='Cloud SQL instance ID.')
    cli = SslCerts.GetCLIGenerator()
    instance.completer = (remote_completion.RemoteCompletion.
                          GetCompleterForResource('sql.instances', cli))

  def Filter(self, tool_context, args):
    if not args.instance:
      raise exceptions.ToolException('argument --instance/-i is required')
