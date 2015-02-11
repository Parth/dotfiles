#!/usr/bin/env python
#
# Copyright 2013 Google Inc. All Rights Reserved.
#

"""A convenience wrapper for starting gcutil."""

import sys

import bootstrapping

from googlecloudsdk.core import config
from googlecloudsdk.core.credentials import gce as c_gce


def main():
  """Launches gcutil."""

  args = []

  project, account = bootstrapping.GetActiveProjectAndAccount()

  if account:
    if account in c_gce.Metadata().Accounts():
      args += ['--auth_service_account', account]
    else:
      ms_path = config.Paths().LegacyCredentialsMultistorePath(account)
      args += ['--credentials_file', ms_path]
      args += ['--auth_service_account=']

  if project:
    args += ['--project', project]

  args.append('--nocheck_for_new_version')

  bootstrapping.ExecutePythonTool(
      'platform/gcutil', 'gcutil', *args)


if __name__ == '__main__':
  bootstrapping.CommandStart('gcutil', component_id='gcutil')
  blacklist = {
      'auth': 'To authenticate, run: gcloud auth login',
  }
  bootstrapping.CheckForBlacklistedCommand(sys.argv, blacklist, warn=True,
                                           die=True)
  bootstrapping.PrerunChecks(can_be_gce=True)
  main()
