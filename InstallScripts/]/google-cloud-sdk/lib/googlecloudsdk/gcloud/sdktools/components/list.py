# Copyright 2013 Google Inc. All Rights Reserved.

"""The command to list installed/available gcloud components."""

import textwrap

from googlecloudsdk.calliope import base


class List(base.Command):
  """List the status of all Cloud SDK components.

  List all packages and individual components in the Cloud SDK and provide
  information such as whether the component is installed on the local
  workstation, whether a newer version is available, the size of the component,
  and the ID used to refer to the component in commands.
  """
  detailed_help = {
      'DESCRIPTION': textwrap.dedent("""\
          This command lists all the tools in the Cloud SDK (both individual
          components and preconfigured packages of components). For each
          component, the command lists the following information:

          * Status on your local workstation: not installed, installed (and
            up to date), and update available (installed, but not up to date)
          * Name of the component (a description)
          * ID of the component (used to refer to the component in other
            [{parent_command}] commands)
          * Size of the component

          In addition, if the `--show-versions` flag is specified, the command
          lists the currently installed version (if any) and the latest
          available version of each individual component.
      """),
      'EXAMPLES': textwrap.dedent("""\
            $ gcloud components list

            $ gcloud components list --show-versions
      """),
  }

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--show-versions', required=False, action='store_true',
        help='Show installed and available versions of all components.')

  def Run(self, args):
    """Runs the list command."""
    self.group.update_manager.List(show_versions=args.show_versions)
