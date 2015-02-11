# Copyright 2013 Google Inc. All Rights Reserved.

"""A hidden command that prints access tokens.
"""

from oauth2client import client

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exc
from googlecloudsdk.core import log
from googlecloudsdk.core.credentials import store as c_store


@base.Hidden
class PrintRefreshToken(base.Command):
  """A command that prints the access token for the current account."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        'account', nargs='?',
        help=('The account to get the access token for. Leave empty for the '
              'active account.'))

  @c_exc.RaiseToolExceptionInsteadOf(c_store.Error, client.Error)
  def Run(self, args):
    """Run the helper command."""

    cred = c_store.Load(args.account)

    if not cred.refresh_token:
      raise c_exc.ToolException(
          'No access token could be obtained from the current credentials.')
    return cred.refresh_token

  def Display(self, args, token):
    log.Print(token)
