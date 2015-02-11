#!/usr/bin/env python
#
# Copyright 2013 Google Inc. All Rights Reserved.
#

"""A convenience wrapper for starting bq."""

import sys

import bootstrapping

from googlecloudsdk.core import config
from googlecloudsdk.core.credentials import gce


def main():
  """Launches bq."""

  project, account = bootstrapping.GetActiveProjectAndAccount()
  json_path = config.Paths().LegacyCredentialsJSONPath(account)

  gce_metadata = gce.Metadata()
  if gce_metadata and account in gce_metadata.Accounts():
    args = ['--use_gce_service_account']
  else:
    args = ['--credential_file', json_path]
  if project:
    args += ['--project', project]

  bootstrapping.ExecutePythonTool(
      'platform/bq', 'bq.py', *args)


if __name__ == '__main__':
  bootstrapping.CommandStart('bq', component_id='bq')
  blacklist = {
      'init': 'To authenticate, run gcloud auth.',
  }
  bootstrapping.CheckForBlacklistedCommand(sys.argv, blacklist,
                                           warn=True, die=True)
  bootstrapping.PrerunChecks(can_be_gce=True)
  main()
