# Copyright 2013 Google Inc. All Rights Reserved.

"""A module that provides parsing utilities for argparse.

For details of how argparse argument pasers work, see:

  http://docs.python.org/dev/library/argparse.html#type

Example usage:

  import argparse
  import arg_parsers

  parser = argparse.ArgumentParser()

  parser.add_argument(
      'metadata',
      nargs='+',
      action=arg_parsers.AssociativeList())
  parser.add_argument(
      '--delay',
      default='5s',
      type=arg_parsers.Duration(lower_bound='1s', upper_bound='10s')
  parser.add_argument(
      '--disk-size',
      default='10GB',
      type=arg_parsers.BinarySize(lower_bound='1GB', upper_bound='10TB')

  res = parser.parse_args(
      '--names --metadata x=y a=b --delay 1s --disk-size 10gb'.split())

  assert res.metadata == {'a': 'b', 'x': 'y'}
  assert res.delay == 1
  assert res.disk_size == 10737418240

"""

import argparse
import re

from googlecloudsdk.calliope import tokenizer

__all__ = ['AssociativeList', 'Duration', 'BinarySize']


class Error(Exception):
  """Exceptions that are defined by this module."""


class ArgumentTypeError(Error, argparse.ArgumentTypeError):
  """Exceptions for parsers that are used as argparse types."""


class ArgumentParsingError(Error, argparse.ArgumentError):
  """Raised when there is a problem with user input.

  argparse.ArgumentError takes both the action and a message as constructor
  parameters.
  """


def _GenerateErrorMessage(error, user_input=None, error_idx=None):
  """Constructs an error message for an exception.

  Args:
    error: str, The error message that should be displayed. This
      message should not end with any punctuation--the full error
      message is constructed by appending more information to error.
    user_input: str, The user input that caused the error.
    error_idx: int, The index at which the error occurred. If None,
      the index will not be printed in the error message.

  Returns:
    str: The message to use for the exception.
  """
  if user_input is None:
    return error
  elif not user_input:  # Is input empty?
    return error + '; received empty string'
  elif error_idx is None:
    return error + '; received: ' + user_input
  return ('{error_message} at index {error_idx}: {user_input}'
          .format(error_message=error, user_input=user_input,
                  error_idx=error_idx))


_VALUE_PATTERN = r"""
    ^                       # Beginning of input marker.
    (?P<amount>\d+)         # Amount.
    ((?P<unit>[a-zA-Z]+))?  # Optional unit.
    $                       # End of input marker.
"""

_SECOND = 1
_MINUTE = 60 * _SECOND
_HOUR = 60 * _MINUTE
_DAY = 24 * _HOUR

# The units are adopted from sleep(1):
#   http://linux.die.net/man/1/sleep
_DURATION_SCALES = {
    's': _SECOND,
    'm': _MINUTE,
    'h': _HOUR,
    'd': _DAY,
}

_BINARY_SIZE_SCALES = {
    'B': 1,
    'KB': 1 << 10,
    'MB': 1 << 20,
    'GB': 1 << 30,
    'TB': 1 << 40,
    'PB': 1 << 50,
    'KiB': 1 << 10,
    'MiB': 1 << 20,
    'GiB': 1 << 30,
    'TiB': 1 << 40,
    'PiB': 1 << 50,
}


def _ValueParser(scales, default_unit, lower_bound=None, upper_bound=None):
  """A helper that returns a function that can parse values with units.

  Casing for all units matters.

  Args:
    scales: {str: int}, A dictionary mapping units to their magnitudes in
      relation to the lowest magnitude unit in the dict.
    default_unit: str, The default unit to use if the user's input is
      missing unit.
    lower_bound: str, An inclusive lower bound.
    upper_bound: str, An inclusive upper bound.

  Returns:
    A function that can parse values.
  """

  def UnitsByMagnitude():
    """Returns a list of the units in scales sorted by magnitude."""
    return [key for key, _
            in sorted(scales.iteritems(), key=lambda value: value[1])]

  def Parse(value):
    """Parses value that can contain a unit."""
    match = re.match(_VALUE_PATTERN, value, re.VERBOSE)
    if not match:
      raise ArgumentTypeError(_GenerateErrorMessage(
          'given value must be of the form INTEGER[UNIT] where units '
          'can be one of {0}'
          .format(', '.join(UnitsByMagnitude())),
          user_input=value))

    amount = int(match.group('amount'))
    unit = match.group('unit')
    if unit is None:
      return amount * scales[default_unit]
    elif unit in scales:
      return amount * scales[unit]
    else:
      raise ArgumentTypeError(_GenerateErrorMessage(
          'unit must be one of {0}'.format(', '.join(UnitsByMagnitude())),
          user_input=unit))

  if lower_bound is None:
    parsed_lower_bound = None
  else:
    parsed_lower_bound = Parse(lower_bound)

  if upper_bound is None:
    parsed_upper_bound = None
  else:
    parsed_upper_bound = Parse(upper_bound)

  def ParseWithBoundsChecking(value):
    """Same as Parse except bound checking is performed."""
    if value is None:
      return None
    else:
      parsed_value = Parse(value)
      if parsed_lower_bound is not None and parsed_value < parsed_lower_bound:
        raise ArgumentTypeError(_GenerateErrorMessage(
            'value must be greater than or equal to {0}'.format(lower_bound),
            user_input=value))
      elif parsed_upper_bound is not None and parsed_value > parsed_upper_bound:
        raise ArgumentTypeError(_GenerateErrorMessage(
            'value must be less than or equal to {0}'.format(upper_bound),
            user_input=value))
      else:
        return parsed_value

  return ParseWithBoundsChecking


def Duration(lower_bound=None, upper_bound=None):
  """Returns a function that can parse time durations.

  Input to the parsing function must be a string of the form:

    INTEGER[UNIT]

  The integer must be non-negative. Valid units are "s", "m", "h", and
  "d" for seconds, seconds, minutes, hours, and days,
  respectively. The casing of the units matters.

  If the unit is omitted, seconds is assumed.

  The result is parsed in seconds. For example:

    parser = Duration()
    assert parser('10s') == 10

  Args:
    lower_bound: str, An inclusive lower bound for values.
    upper_bound: str, An inclusive upper bound for values.

  Raises:
    ArgumentTypeError: If either the lower_bound or upper_bound
      cannot be parsed. The returned function will also raise this
      error if it cannot parse its input. This exception is also
      raised if the returned function receives an out-of-bounds
      input.

  Returns:
    A function that accepts a single time duration as input to be
      parsed.
  """
  return _ValueParser(_DURATION_SCALES, default_unit='s',
                      lower_bound=lower_bound, upper_bound=upper_bound)


def BinarySize(lower_bound=None, upper_bound=None):
  """Returns a function that can parse binary sizes.

  Binary sizes are defined as base-2 values representing number of
  bytes.

  Input to the parsing function must be a string of the form:

    INTEGER[UNIT]

  The integer must be non-negative. Valid units are "B", "KB", "MB",
  "GB", "TB", "KiB", "MiB", "GiB", "TiB", "PiB".  If the unit is
  omitted, GB is assumed.

  The result is parsed in bytes. For example:

    parser = BinarySize()
    assert parser('10GB') == 1073741824

  Args:
    lower_bound: str, An inclusive lower bound for values.
    upper_bound: str, An inclusive upper bound for values.

  Raises:
    ArgumentTypeError: If either the lower_bound or upper_bound
      cannot be parsed. The returned function will also raise this
      error if it cannot parse its input. This exception is also
      raised if the returned function receives an out-of-bounds
      input.

  Returns:
    A function that accepts a single binary size as input to be
      parsed.
  """
  return _ValueParser(_BINARY_SIZE_SCALES, default_unit='GB',
                      lower_bound=lower_bound, upper_bound=upper_bound)


_KV_PAIR_DELIMITER = '='


def AssociativeList(spec=None, append=False):
  """A parser for parsing sequences of key/value pairs.

  The argument can contain zero or more values. Each value must be of
  the form:

    KEY=VALUE

  Keys and values can be arbitrary strings as long as any occurrence
  of "=" in the key or value is escaped with a single preceding "\".

  Args:
    spec: {str: function}, A mapping of expected keys to functions.
      The functions are applied to the values. If None, an arbitrary
      set of keys will be accepted. If not None, it is an error for the
      user to supply a key that is not in the spec.
    append: bool, If True, repeated invocations of a flag with this action
      will cause the results to be collected into a list. If False, in
      repeated invocations, the last flag wins. This is behavior is similar
      to the 'store' and 'append' actions of argparse.

  Returns:
    argparse.Action, An action for parsing key/value pairs.
  """

  class Action(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
      if not isinstance(values, list):
        values = [values]
      res = self._Parse(values)
      if append:
        current_list = getattr(namespace, self.dest, None)
        if current_list:
          current_list.append(res)
        else:
          setattr(namespace, self.dest, [res])
      else:
        setattr(namespace, self.dest, res)

    def _Parse(self, pairs):
      res = {}
      for pair in pairs:
        try:
          parts = tokenizer.Tokenize(pair, [_KV_PAIR_DELIMITER])
        except ValueError as e:
          raise ArgumentParsingError(self, e.message)
        if len(parts) != 3 or parts[1] != tokenizer.Separator(
            _KV_PAIR_DELIMITER):
          raise ArgumentParsingError(
              self, _GenerateErrorMessage(
                  'key/value pair must be of the form KEY{0}VALUE'.format(
                      _KV_PAIR_DELIMITER),
                  user_input=pair))

        key, value = parts[0], parts[2]
        if key in res:
          raise ArgumentParsingError(
              self, _GenerateErrorMessage('duplicate key', user_input=key))
        res[key] = self.ApplySpec(key, value)

      return res

    def ApplySpec(self, key, value):
      if spec is None:
        return value
      else:
        if key in spec:
          return spec[key](value)
        else:
          raise ArgumentParsingError(
              self, _GenerateErrorMessage(
                  'valid keys are {0}'.format(', '.join(sorted(spec.keys()))),
                  user_input=key))

  return Action


class HostPort(object):
  """A class for holding host and port information."""

  def __init__(self, host, port):
    self.host = host
    self.port = port

  @staticmethod
  def Parse(s):
    """Parse the given string into a HostPort object.

    This can be used as an argparse type.

    Args:
      s: str, The string to parse.

    Raises:
      ArgumentTypeError: If the string is not valid.

    Returns:
      HostPort, The parsed object.
    """
    if not s:
      return HostPort(None, None)
    if ':' not in s:
      return HostPort(s, None)
    parts = s.split(':')
    if len(parts) > 2:
      raise ArgumentTypeError(
          _GenerateErrorMessage('Failed to parse host and port', user_input=s))
    return HostPort(parts[0] or None, parts[1] or None)


def BoundedInt(lower_bound=None, upper_bound=None):
  """Returns a function that can parse integers within some bound."""

  def _Parse(value):
    """Parses value as an int, raising ArgumentTypeError if out of bounds."""
    v = int(value)

    if lower_bound is not None and v < lower_bound:
      raise ArgumentTypeError(
          _GenerateErrorMessage(
              'Value must be greater than or equal to {0}'.format(lower_bound),
              user_input=value))

    if upper_bound is not None and upper_bound < v:
      raise ArgumentTypeError(
          _GenerateErrorMessage(
              'Value must be less than or equal to {0}'.format(upper_bound),
              user_input=value))

    return v

  return _Parse
