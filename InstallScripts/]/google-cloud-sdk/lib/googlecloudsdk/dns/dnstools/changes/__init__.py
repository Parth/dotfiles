# Copyright 2013 Google Inc. All Rights Reserved.

"""Cloud DNS changes group."""

from googlecloudsdk.calliope import base


class Changes(base.Group):
  """Manage Cloud DNS resource record set changes."""

  @staticmethod
  def Args(parser):
    """Set arguments for the changes group."""
    parser.add_argument(
        '--zone',
        '-z',
        required=True,
        help='Managed Zone name.')

