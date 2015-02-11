# Copyright 2013 Google Inc. All Rights Reserved.

"""Revoke credentials being used by the CloudSDK."""


from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exc
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.credentials import store as c_store


class Revoke(base.Command):
  """Revoke authorization for credentials.

  Revoke credentials. If no account is provided, the currently active account is
  used.
  """

  @staticmethod
  def Args(parser):
    parser.add_argument('accounts', nargs='*',
                        help='Accounts whose credentials shall be revoked.')
    parser.add_argument('--all', action='store_true',
                        help='Revoke all known credentials.')

  @c_exc.RaiseToolExceptionInsteadOf(c_store.Error)
  def Run(self, args):
    """Revoke credentials and update active account."""
    accounts = args.accounts or []
    if type(accounts) is str:
      accounts = [accounts]
    available_accounts = c_store.AvailableAccounts()
    unknown_accounts = set(accounts) - set(available_accounts)
    if unknown_accounts:
      raise c_exc.UnknownArgumentException(
          'accounts', ' '.join(unknown_accounts))
    if args.all:
      accounts = available_accounts

    active_account = properties.VALUES.core.account.Get()

    if not accounts and active_account:
      accounts = [active_account]

    if not accounts:
      raise c_exc.InvalidArgumentException(
          'accounts', 'No credentials available to revoke.')

    for account in accounts:
      if active_account == account:
        properties.PersistProperty(properties.VALUES.core.account, None)
      c_store.Revoke(account)
    return accounts

  def Display(self, unused_args, result):
    if result:
      log.Print('Revoked credentials for {account}.'.format(
          account=', '.join(result)))
      self.ExecuteCommand(['auth', 'list'])
