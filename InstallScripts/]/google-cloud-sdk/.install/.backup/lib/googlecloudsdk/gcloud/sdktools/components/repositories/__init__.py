# Copyright 2013 Google Inc. All Rights Reserved.

"""The super-group for the update manager."""

import argparse
import os

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import config
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.updater import update_manager
from googlecloudsdk.core.util import platforms


class Repositories(base.Group):
  """Manage additional component repositories for Trusted Tester programs."""

  detailed_help = {
      'DESCRIPTION': """\
          List, add, and remove component repositories for Trusted Tester
          programs.  If you are not participating in a Trusted Tester program,
          these commands are not necessary for updating your Cloud SDK
          installation.

          If you are participating in a Trusted Tester program, you will be
          instructed on the location of repositories that you should add.
          These commands allow you to manage the set of repositories you have
          registered.

          Once you have a repository registered, the component manager will use
          that location to locate new Cloud SDK components that are available,
          or possibly different versions of existing components that can be
          installed.

          If you want to revert to a standard version of the Cloud SDK at any
          time, you may remove all repositories and then run:

            $ gcloud components update

          to revert to a standard installation.
      """,
  }

  @staticmethod
  def RepoCompleter(prefix, parsed_args, **unused_kwargs):
    repos = update_manager.UpdateManager.GetAdditionalRepositories()
    return [r for r in repos if r.startswith(prefix)]
