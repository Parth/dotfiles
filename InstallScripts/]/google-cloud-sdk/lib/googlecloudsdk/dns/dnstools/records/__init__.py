# Copyright 2013 Google Inc. All Rights Reserved.

"""Cloud DNS resource-record-sets group."""

from googlecloudsdk.calliope import base


class Records(base.Group):
  """Manage Cloud DNS resource record sets."""

  @staticmethod
  def Args(parser):
    """Set arguments for the resource-record-sets group."""
    parser.add_argument(
        '--zone',
        '-z',
        required=True,
        help='Managed Zone name.')


