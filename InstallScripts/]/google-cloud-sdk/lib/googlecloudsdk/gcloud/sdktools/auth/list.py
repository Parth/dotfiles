# Copyright 2013 Google Inc. All Rights Reserved.

"""Command to list the available accounts."""

import collections
import textwrap

from googlecloudsdk.calliope import base
from googlecloudsdk.core import log
from googlecloudsdk.core.credentials import store as c_store
from googlecloudsdk.core.util import console_io


class List(base.Command):
  """List the accounts for known credentials."""

  @staticmethod
  def Args(parser):
    parser.add_argument('--account',
                        help='List only credentials for one account.')

  def Run(self, args):
    """List the account for known credentials."""
    accounts = c_store.AvailableAccounts()

    active_account = c_store.ActiveAccount()

    if args.account:
      if args.account in accounts:
        accounts = [args.account]
      else:
        accounts = []

    auth_info = collections.namedtuple(
        'auth_info',
        ['active_account', 'accounts'])
    return auth_info(active_account, accounts)

  def Display(self, unused_args, result):
    if result.accounts:
      lp = console_io.ListPrinter('Credentialed accounts:')
      lp.Print([account +
                (' (active)' if account == result.active_account else '')
                for account in result.accounts])
      log.err.Print(textwrap.dedent("""
          To set the active account, run:
            $ gcloud config set account ``ACCOUNT''
          """))
    else:
      log.err.Print(textwrap.dedent("""\
          No credentialed accounts.

          To login, run:
            $ gcloud auth login ``ACCOUNT''
          """))
