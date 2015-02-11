# Copyright 2013 Google Inc. All Rights Reserved.

"""The super-group for the cloud CLI."""

import argparse
import os
import textwrap

from googlecloudsdk.calliope import actions
from googlecloudsdk.calliope import base
from googlecloudsdk.core import properties


class Gcloud(base.Group):
  """Manage Google Cloud Platform resources and developer workflow.

  The *gcloud* CLI manages authentication, local configuration, developer
  workflow, and interactions with the Google Cloud Platform APIs.
  """

  @staticmethod
  def Args(parser):
    project_arg = parser.add_argument(
        '--project',
        metavar='PROJECT_ID',
        dest='project',
        help='Google Cloud Platform project ID to use for this invocation.',
        action=actions.StoreProperty(properties.VALUES.core.project))
    project_arg.detailed_help = """\
        The Google Cloud Platform project name to use for this invocation. If
        omitted then the current project is assumed.
        """
    # Must have a None default so properties are not always overridden when the
    # arg is not provided.
    quiet_arg = parser.add_argument(
        '--quiet',
        '-q',
        default=None,
        help='Disable all interactive prompts.',
        action=actions.StoreConstProperty(
            properties.VALUES.core.disable_prompts, True))
    quiet_arg.detailed_help = """\
        Disable all interactive prompts when running gcloud commands. If input
        is required, defaults will be used, or an error will be raised.
        """

    trace_group = parser.add_mutually_exclusive_group()
    trace_group.add_argument(
        '--trace-token',
        default=None,
        help='Token used to route traces of service requests for investigation'
        ' of issues.')
