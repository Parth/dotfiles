# Copyright 2014 Google Inc. All Rights Reserved.
"""A module for capturing time-related functions.

This makes mocking for time-related functionality easier.
"""
import time


def CurrentTimeSec():
  """Returns a float of the current time in seconds."""
  return time.time()


def Sleep(duration_sec):
  """Sleeps for the given duration."""
  time.sleep(duration_sec)
