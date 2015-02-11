# Copyright 2013 Google Inc. All Rights Reserved.

"""A calliope command that calls a help function."""

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import cli
from googlecloudsdk.calliope import exceptions as c_exc
from googlecloudsdk.core import log


class Help(base.Command):
  """Prints detailed help messages for the specified commands.

  This command prints a detailed help message for the commands specified
  after the ``help`' operand.
  """

  @staticmethod
  def Args(parser):
    command_arg = parser.add_argument(
        'command',
        nargs='*',
        help='The commands to get help for.')
    command_arg.detailed_help = """\
        A sequence of group and command names with no flags.
        """

  @c_exc.RaiseToolExceptionInsteadOf(cli.NoHelpFoundError)
  def Run(self, args):
    # pylint: disable=protected-access
    help_func = self.cli._HelpFunc()

    def RaiseError():
      raise c_exc.ToolException(
          'Unknown command: {command}'.format(command='.'.join(args.command)))

    def ShowShortHelp():
      """Print short help text."""
      segments = [segment.replace('-', '_') for segment in args.command]
      # pylint: disable=protected-access
      current_element = self.cli._TopElement()

      for segment in segments:
        current_element = current_element.LoadSubElement(segment)
        if not current_element:
          RaiseError()
      log.out.write((current_element.GetShortHelp()))

    if not help_func:
      ShowShortHelp()
    else:
      try:
        # pylint: disable=protected-access
        help_func([self.cli._TopElement().name] + (args.command or []))
      except cli.NoHelpFoundError:
        ShowShortHelp()
