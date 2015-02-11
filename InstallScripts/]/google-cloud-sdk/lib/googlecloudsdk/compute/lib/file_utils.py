# Copyright 2014 Google Inc. All Rights Reserved.
"""Convenience functions for dealing with files."""
from googlecloudsdk.calliope import exceptions


def ReadFile(file_path, data_name):
  try:
    return open(file_path).read()
  except IOError as e:
    raise exceptions.ToolException(
        'Could not read {0} from file [{1}]: {2}'.format(
            data_name, file_path, e.strerror))
