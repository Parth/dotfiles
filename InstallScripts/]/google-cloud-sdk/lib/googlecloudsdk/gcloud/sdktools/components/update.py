# Copyright 2013 Google Inc. All Rights Reserved.

"""The command to install/update gcloud components."""

import argparse
import textwrap

from googlecloudsdk.calliope import base


class Update(base.Command):
  """Update or install one or more Cloud SDK components or packages.

  Ensure that the latest version of each specified component, and the latest
  version of all components upon which the specified components directly or
  indirectly depend, is installed on the local workstation. If the command
  includes one or more names of components or packages, the specified components
  are the named components and the components contained in the named packages;
  if the command does not name any components or packages, the specified
  components are all installed components.
  """
  detailed_help = {
      'DESCRIPTION': textwrap.dedent("""\
          {description}

          The items may be individual components or preconfigured packages. If a
          downloaded component was not previously installed, the downloaded
          version is installed. If an earlier version of the component was
          previously installed, that version is replaced by the downloaded
          version.

          If, for example, the component ``UNICORN-FACTORY'' depends on the
          component ``HORN-FACTORY'', installing the latest version of
          ``UNICORN-FACTORY'' will cause the version of ``HORN-FACTORY'' upon
          which it depends to be installed as well, if it is not already
          installed. The command lists all components it is about to install,
          and asks for confirmation before proceeding.
      """),
      'EXAMPLES': textwrap.dedent("""\
          The following command ensures that the latest version is installed for
          ``COMPONENT-1'', ``COMPONENT-2'', and all components that depend,
          directly or indirectly, on either ``COMPONENT-1'' or ``COMPONENT-2'':

            $ gcloud components update COMPONENT-1 COMPONENT-2
      """),
  }

  @staticmethod
  def Args(parser):
    parser.add_argument(
        'component_ids',
        metavar='COMPONENT-IDS',
        nargs='*',
        help='The IDs of the components to be updated or installed.')
    parser.add_argument(
        '--allow-no-backup',
        required=False,
        action='store_true',
        help=argparse.SUPPRESS)

  def Run(self, args):
    """Runs the list command."""
    self.group.update_manager.Update(
        args.component_ids, allow_no_backup=args.allow_no_backup)
