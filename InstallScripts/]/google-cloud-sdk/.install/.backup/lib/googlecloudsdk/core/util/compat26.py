# Copyright 2014 Google Inc. All Rights Reserved.

"""Utilities for accessing python 2.7 functionality from 2.6."""

import subprocess as _subprocess


# Don't warn that subprocess doesn't start with a capital letter.  This
# allows compat26.subprocess.- to look like subprocess.-.
# pylint: disable=invalid-name
class subprocess(object):

  """subprocess.check_output simulates the python 2.7 library function.

  This implementation takes a subset of the flags allowed in
  python 2.7 library, but is otherwise intended to have the same
  behavior.
  """

  @staticmethod
  def check_output(cmd, stdin=None, stderr=None,
                   shell=False, universal_newlines=False, cwd=None):
    p = _subprocess.Popen(cmd, stdin=stdin, stderr=stderr,
                          stdout=_subprocess.PIPE, shell=shell,
                          universal_newlines=universal_newlines, cwd=cwd)
    (stdout_data, _) = p.communicate()
    assert type(p.returncode) is int  # communicate() should ensure non-None
    if p.returncode == 0:
      return stdout_data
    else:
      raise _subprocess.CalledProcessError(p.returncode, cmd, stdout_data)
