# Copyright 2014 Google Inc. All Rights Reserved.
"""Simplify fully-qualified paths for compute."""


def Name(uri):
  """Get just the name of the object the uri refers to."""

  # Since the path is assumed valid, we can just take the last piece.
  return uri.split('/')[-1]


def ScopedSuffix(uri):
  """Get just the scoped part of the object the uri refers to."""

  # The path is assumed valid.
  if '/zones/' in uri:
    # This is zonally scoped. Return the part after zone/.
    return uri.split('/zones/')[-1]
  elif '/regions/' in uri:
    # This is regionally scoped. Return the part after regions/.
    return uri.split('/regions/')[-1]
  else:
    # This is globally scoped. Return the name.
    return Name(uri)


def ProjectSuffix(uri):
  """Get the entire relative path of the object the uri refers to."""

  # Get the part after projects. The argument is assumed valid.
  return uri.split('/projects/')[-1]
