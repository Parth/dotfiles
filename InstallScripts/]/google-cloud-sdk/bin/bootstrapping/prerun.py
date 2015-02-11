#!/usr/bin/env python

# Copyright 2013 Google Inc. All Rights Reserved.

"""Convenience tool for non .py Cloud SDK commands.

Allows non .py Cloud SDK CLIs to easily check for updates and credentials.
"""

# pylint: disable=g-bad-import-order, Import this first so the python version
# check happens before anything else.
import bootstrapping

import argparse


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--check-credentials',
                      required=False, action='store_true')
  parser.add_argument('--check-updates',
                      required=False, action='store_true')
  parser.add_argument('--command-name', required=True)
  parser.add_argument('--component-id')
  args = parser.parse_args()

  bootstrapping.CommandStart(args.command_name, component_id=args.component_id)
  if args.check_credentials:
    bootstrapping.CheckCredOrExit()
  if args.check_updates:
    bootstrapping.CheckUpdates()


if __name__ == '__main__':
  main()
