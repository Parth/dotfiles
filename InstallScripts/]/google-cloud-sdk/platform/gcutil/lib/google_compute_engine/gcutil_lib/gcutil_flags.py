# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Adds a case-insensitive enum flag for gcutil."""


import gflags as flags


FLAGS = flags.FLAGS


class CaseInsensitiveEnumParser(flags.EnumParser):
  """Case Insensitive Enum Parser."""

  def __init__(self, enum_values=None):
    super(CaseInsensitiveEnumParser, self).__init__(enum_values)

  def Parse(self, argument):
    """Parser for case-insensitive enums.

    Args:
      argument: The user choice provided in the flag.

    Returns:
      The element from enum_values matching the argument, or argument if
      enum_values is empty.

    Raises:
      ValueError:  If enum_values is not empty and argument matches none of
        them.
    """
    if not self.enum_values:
      return argument

    if (self.enum_values and
        argument.upper() not in [value.upper() for value in self.enum_values]):
      raise ValueError('value should be one of <%s>' %
                       '|'.join(self.enum_values))
    else:
      return [value for value in self.enum_values
              if value.upper() == argument.upper()][0]


class CaseInsensitiveEnumFlag(flags.EnumFlag):
  """Basic enum flag; its value can be any string from list of enum_values."""

  def __init__(self, name, default, help, enum_values=None,
               short_name=None, **args):
    enum_values = enum_values or []

    p = CaseInsensitiveEnumParser(enum_values)
    g = flags.ArgumentSerializer()
    flags.Flag.__init__(self, p, g, name, default, help, short_name, **args)
    if not self.help: self.help = 'an enum string'
    self.help = '<%s>: %s' % ('|'.join(enum_values), self.help)


def DEFINE_case_insensitive_enum(  # pylint: disable=g-bad-name
    name, default, enum_values, help, flag_values=FLAGS, **args):
  """Register a flag whose value is any case insensitive item from enum_values.

  Args:
    name: A string, the flag name.
    default: The default value of the flag.
    enum_values: A list of strings with the possible values for the flag.
    help: A help string.
    flag_values: FlagValues object with which the flag will be registered.
    **args: Dictionary with extra keyword args that are passes to the
        Flag __init__.
  """
  flags.DEFINE_flag(
      CaseInsensitiveEnumFlag(name, default, help, enum_values, **args),
      flag_values)
