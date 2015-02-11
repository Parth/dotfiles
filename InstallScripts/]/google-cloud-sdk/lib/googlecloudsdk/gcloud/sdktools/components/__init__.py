# Copyright 2013 Google Inc. All Rights Reserved.

"""The super-group for the update manager."""

import argparse
import os
import textwrap

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import config
from googlecloudsdk.core import log
from googlecloudsdk.core.updater import update_manager
from googlecloudsdk.core.util import platforms


class Components(base.Group):
  """List, install, update, or remove Google Cloud SDK components or packages.
  """

  detailed_help = {
      'DESCRIPTION': textwrap.dedent("""\
          {description}

          Because you might need only some of the tools in the Cloud SDK to do
          your work, you can control which tools are installed on your
          workstation. You can install new tools on your workstation when you
          find that you need them, and remove tools that you no longer need.
          The gcloud command regularly checks whether updates are available for
          the tools you already have installed, and gives you the opportunity
          to upgrade to the latest version.

          Tools can be installed as individual components or as preconfigured
          _packages_ of components that are typically all used together to
          perform a particular task (such as developing a PHP application on
          App Engine).

          Certain components _depend_ on other components. When you install a
          component that you need, all components upon which it directly or
          indirectly depends, and that are not already present on your
          workstation, are installed automatically. When you remove a
          component, all components that depend on the removed component are
          also removed.
      """),
  }

  @staticmethod
  def Args(parser):
    """Sets args for gcloud components."""
    # An override for the location to install components into.
    parser.add_argument('--sdk-root-override', required=False,
                        help=argparse.SUPPRESS)
    # A different URL to look at instead of the default.
    parser.add_argument('--snapshot-url-override', required=False,
                        help=argparse.SUPPRESS)
    # This is not a commonly used option.  You can use this flag to create a
    # Cloud SDK install for an OS other than the one you are running on.
    # Running the updater multiple times for different operating systems could
    # result in an inconsistent install.
    parser.add_argument('--operating-system-override', required=False,
                        help=argparse.SUPPRESS)
    # This is not a commonly used option.  You can use this flag to create a
    # Cloud SDK install for a processor architecture other than that of your
    # current machine.  Running the updater multiple times for different
    # architectures could result in an inconsistent install.
    parser.add_argument('--architecture-override', required=False,
                        help=argparse.SUPPRESS)

  # pylint:disable=g-missing-docstring
  @exceptions.RaiseToolExceptionInsteadOf(platforms.InvalidEnumValue)
  def Filter(self, unused_tool_context, args):

    if config.INSTALLATION_CONFIG.IsAlternateReleaseChannel():
      log.warning('You are using alternate release channel: [%s]',
                  config.INSTALLATION_CONFIG.release_channel)
      # Always show the URL if using a non standard release channel.
      log.warning('Snapshot URL for this release channel is: [%s]',
                  config.INSTALLATION_CONFIG.snapshot_url)

    os_override = platforms.OperatingSystem.FromId(
        args.operating_system_override)
    arch_override = platforms.Architecture.FromId(args.architecture_override)

    platform = platforms.Platform.Current(os_override, arch_override)
    root = (os.path.expanduser(args.sdk_root_override)
            if args.sdk_root_override else None)
    url = (os.path.expanduser(args.snapshot_url_override)
           if args.snapshot_url_override else None)

    self.update_manager = update_manager.UpdateManager(
        sdk_root=root, url=url, platform_filter=platform)
