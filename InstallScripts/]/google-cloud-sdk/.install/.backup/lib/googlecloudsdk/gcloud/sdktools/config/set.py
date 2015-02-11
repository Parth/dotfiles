# Copyright 2013 Google Inc. All Rights Reserved.

"""Command to set properties."""

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exc
from googlecloudsdk.core import properties


class Set(base.Command):
  """Edit Google Cloud SDK properties.

  Set the value for an option, so that Cloud SDK tools can use them as
  configuration.
  """

  detailed_help = {
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
          To set the project property in the core section, run:

            $ {command} project myProject

          To set the zone property in the compute section, run:

            $ {command} compute/zone zone3
          """,
  }

  @staticmethod
  def Args(parser):
    """Adds args for this command."""
    Set.group_class.SCOPE_FLAG.AddToParser(parser)
    property_arg = parser.add_argument(
        'property',
        metavar='SECTION/PROPERTY',
        help='The property to be set. Note that SECTION/ is optional while '
        'referring to properties in the core section.')
    property_arg.completer = Set.group_class.PropertiesCompleter
    parser.add_argument(
        'value',
        help='The value to be set.')

  @c_exc.RaiseToolExceptionInsteadOf(properties.Error)
  def Run(self, args):
    """Runs this command."""
    prop = self.group.PropertyFromString(args.property)
    properties.PersistProperty(prop, args.value,
                               scope=properties.Scope.FromId(args.scope))
