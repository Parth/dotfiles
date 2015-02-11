#!/usr/bin/env python

# Copyright 2013 Google Inc. All Rights Reserved.

"""Convenience tool for non .py Cloud SDK commands.

Reads a property from config and prints it to stdout.
"""

# pylint: disable=g-bad-import-order, Import this first so the python version
# check happens before anything else.
import bootstrapping

import argparse
import sys

from googlecloudsdk.core import config


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('item')
  args = parser.parse_args()

  project, account = bootstrapping.GetActiveProjectAndAccount()

  # pylint:disable=superfluous-parens
  if args.item == 'multistore_path':
    print(config.Paths().LegacyCredentialsMultistorePath(account))
  elif args.item == 'json_path':
    print(config.Paths().LegacyCredentialsJSONPath(account))
  elif args.item == 'gae_java_path':
    print(config.Paths().LegacyCredentialsGAEJavaPath(account))
  elif args.item == 'project':
    print(project)
  else:
    print('Valid keys are multistore_path, json_path, gae_java_path, or '
          'project.')
    sys.exit(1)


if __name__ == '__main__':
  main()
