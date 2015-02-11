# Copyright 2013 Google Inc. All Rights Reserved.

"""The command to list installed/available gcloud components."""

from googlecloudsdk.calliope import base
from googlecloudsdk.core import log
from googlecloudsdk.core.updater import snapshots
from googlecloudsdk.core.updater import update_manager
from googlecloudsdk.core.util import console_io


class List(base.Command):
  """List any Trusted Tester component repositories you have registered.
  """
  detailed_help = {
      'DESCRIPTION': """\
          List all Trusted Tester component repositories that are registered
          with the component manager.  If you have additional repositories, the
          component manager will look at them to discover additional components
          to install, or different versions of existing components that are
          available.
      """,
  }

  @staticmethod
  def _LastUpdate(repo):
    try:
      snapshot = snapshots.ComponentSnapshot.FromURLs(repo)
      return snapshot.sdk_definition.LastUpdatedString()
    # pylint: disable=bare-except, We should always print a table even if we
    # can't calculate the date.
    except:
      return 'Unknown'

  def Run(self, args):
    """Runs the list command."""
    repos = update_manager.UpdateManager.GetAdditionalRepositories()
    return repos if repos else []

  def Display(self, unused_args, repos):
    if repos:
      console_io.PrintExtendedList(
          repos,
          [('REPOSITORY', lambda x: x), ('LAST_UPDATE', List._LastUpdate)])
    else:
      log.status.write(
          'You have no registered component repositories.  To add one, run:\n'
          '  $ gcloud components repositories add URL\n\n')
