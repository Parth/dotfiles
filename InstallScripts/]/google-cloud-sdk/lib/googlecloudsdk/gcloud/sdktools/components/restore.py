# Copyright 2013 Google Inc. All Rights Reserved.

"""The command to restore a backup of a Cloud SDK installation."""

from googlecloudsdk.calliope import base


class Restore(base.Command):
  """Restore the Cloud SDK installation to its previous state.

  This is an undo operation, which restores the Cloud SDK installation on the
  local workstation to the state it was in just before the most recent
  `{parent_command} update` or `{parent_command} remove` command. Only the
  state before the most recent such state is remembered, so it is impossible
  to restore the state that existed before the two most recent `update`
  commands, for example. A `restore` command does not undo a previous `restore`
  command.
  """

  @staticmethod
  def Args(_):
    pass

  def Run(self, unused_args):
    """Runs the list command."""
    self.group.update_manager.Restore()
