# Copyright 2013 Google Inc. All Rights Reserved.

"""Utilities for extracting values from nested structures.

An attrpath is a string that provides an instruction on how to get a specific
value from an arbitrary python object, using python-like syntax, with the
exception of dict keys, which look like attributes.

If the attrpath fails to look up the value in the object, for any reason, it
will return None - all exceptions are thrown when the attrpath is parsed, using
the Selector class, rather than when it is applied, using the Selector's
.__call__() method.

Examples: See tests/attrpath_test.py for extensive examples. A few
representative attrpaths are listed here.

Given an object
 key applied to {'key': ['val1', 'val2']} gets ['val1', 'val2'].
 key[1] applied to {'key': ['val1', 'val2']} gets 'val2'.
 key1.key2 applied to {'key1': {'key2': 'value'}} gets 'value'.

"""

from googlecloudsdk.calliope import tokenizer


class Error(Exception):
  """Base class for exceptions raised by this module."""


class IllegalProperty(Error):
  """Raised for properties that are syntactically incorrect."""


class _Key(str):
  """A path token that represents keying into a dict or object."""
  pass


class _Index(int):
  """A path token that represents indexing into a list."""
  pass


def _Parse(prop):
  """Parses the given tokens that represent a property."""
  tokens = tokenizer.Tokenize(prop, ['[', ']', '.'])
  tokens = [token for token in tokens if token]
  if not tokens:
    raise IllegalProperty('illegal property: {0}'.format(prop))

  res = []

  while tokens:
    if not isinstance(tokens[0], tokenizer.Literal):
      raise IllegalProperty('illegal property: {0}'.format(prop))

    res.append(_Key(tokens[0]))
    tokens = tokens[1:]

    # At this point, we expect to be either at the end of the input
    # stream or we expect to see a "." or "[".

    # We've reached the end of the input stream.
    if not tokens:
      break

    if not isinstance(tokens[0], tokenizer.Separator):
      raise IllegalProperty('illegal property: {0}'.format(prop))

    if isinstance(tokens[0], tokenizer.Separator) and tokens[0] == '[':
      if len(tokens) < 2:
        raise IllegalProperty('illegal property: {0}'.format(prop))

      tokens = tokens[1:]

      # Handles index accesses (e.g., "[1]").
      if (isinstance(tokens[0], tokenizer.Literal) and
          tokens[0].isdigit() and
          len(tokens) >= 2 and
          isinstance(tokens[1], tokenizer.Separator) and
          tokens[1] == ']'):
        res.append(_Index(tokens[0]))
        tokens = tokens[2:]

      else:
        raise IllegalProperty('illegal property: {0}'.format(prop))

    # We've reached the end of input.
    if not tokens:
      break

    # We expect a "."; we also expect that the "." is not the last
    # token in the input.
    if (len(tokens) > 1 and
        isinstance(tokens[0], tokenizer.Separator) and
        tokens[0] == '.'):
      tokens = tokens[1:]
      continue
    else:
      raise IllegalProperty('illegal property: {0}'.format(prop))

  return res


def _GetProperty(obj, components):
  """Grabs a property from obj."""
  if obj is None:
    return None

  elif not components:
    return obj

  elif (isinstance(components[0], _Key) and
        isinstance(obj, dict)):
    return _GetProperty(obj.get(components[0]), components[1:])

  elif (isinstance(components[0], _Index) and isinstance(obj, list) and
        components[0] < len(obj)):
    return _GetProperty(obj[components[0]], components[1:])

  elif isinstance(components[0], _Key):
    return _GetProperty(getattr(obj, components[0], None), components[1:])

  else:
    return None


class Selector(object):
  """A selector that, given a path, will pull things out of objects."""

  def __init__(self, path):
    self.__path = path
    self.__components = None

  def __call__(self, obj):
    # Ensure that the parsing is only done once, and only on-demand.
    self.__components = self.__components or _Parse(self.__path)
    found_obj = _GetProperty(obj, self.__components)
    return found_obj
