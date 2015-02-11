# Copyright 2013 Google Inc. All Rights Reserved.

"""config command group."""

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exc
from googlecloudsdk.core import config
from googlecloudsdk.core import properties


class Config(base.Group):
  """View and edit Google Cloud SDK properties."""

  SCOPE_FLAG = base.Argument(
      '--scope',
      required=False,
      choices=properties.Scope.AllScopeNames(),
      help='The configuration location in which to update the property. '
      '({scopes})'.format(scopes=', '.join(properties.Scope.AllScopeNames())),
      detailed_help="""\
The scope flag determines which configuration file is modified by this
operation.  The files are read (and take precedence) in the following
order:

{scope_help}
""".format(scope_help=properties.Scope.GetHelpString())
  )

  @staticmethod
  def PropertiesCompleter(prefix, parsed_args, **unused_kwargs):
    """Properties commmand completion helper."""
    all_sections = properties.VALUES.AllSections()
    options = []

    if '/' in prefix:
      # Section has been specified, only return properties under that section.
      parts = prefix.split('/', 1)
      section = parts[0]
      prefix = parts[1]
      if section in all_sections:
        section_str = section + '/'
        props = properties.VALUES.Section(section).AllProperties()
        options.extend([section_str + p for p in props if p.startswith(prefix)])
    else:
      # No section.  Return matching sections and properties in the default
      # group.
      options.extend([s + '/' for s in all_sections if s.startswith(prefix)])
      section = properties.VALUES.default_section.name
      props = properties.VALUES.Section(section).AllProperties()
      options.extend([p for p in props if p.startswith(prefix)])

    return options

  def ParsePropertyString(self, property_string):
    """Parses a string into a section and property name.

    Args:
      property_string: str, The property string in the format section/property.

    Returns:
      (str, str), The section and property.  Both will be none if the input
      string is empty.  Property can be None if the string ends with a slash.
    """
    if not property_string:
      return None, None

    if '/' in property_string:
      section, prop = tuple(property_string.split('/', 1))
    else:
      section = None
      prop = property_string

    section = section or properties.VALUES.default_section.name
    prop = prop or None
    return section, prop

  def PropertyFromString(self, property_string):
    """Gets the property object corresponding the given string.

    Args:
      property_string: str, The string to parse.  It can be in the format
        section/property, or just property if the section is the default one.

    Raises:
      InvalidArgumentException: For invalid arguments.

    Returns:
      properties.Property, The property.
    """
    section, prop = self.ParsePropertyString(property_string)
    if not prop:
      raise c_exc.InvalidArgumentException(
          'property', 'Must be in the form: [SECTION/]PROPERTY')
    return properties.VALUES.Section(section).Property(prop)
