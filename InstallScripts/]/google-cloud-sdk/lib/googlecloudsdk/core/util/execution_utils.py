# Copyright 2013 Google Inc. All Rights Reserved.

"""Functions to help with shelling out to other commands."""

import os
import signal
import subprocess
import sys


from googlecloudsdk.core import config
from googlecloudsdk.core import log


def GetPythonExecutable():
  """Gets the path to the Python interpreter that should be used."""
  cloudsdk_python = os.environ.get('CLOUDSDK_PYTHON')
  if cloudsdk_python:
    return cloudsdk_python
  python_bin = sys.executable
  if not python_bin:
    raise ValueError('Could not find Python executable.')
  return python_bin


def GetShellExecutable():
  """Gets the path to the Shell that should be used."""
  shell = os.getenv('SHELL', None)

  shells = ['/bin/bash', '/bin/sh']
  if shell:
    shells.insert(0, shell)

  for s in shells:
    if os.path.isfile(s):
      return s

  raise ValueError("You must set your 'SHELL' environment variable to a "
                   "valid shell executable to use this tool.")


def _GetToolArgs(interpreter, interpreter_args, executable_path, *args):
  tool_args = []
  if interpreter:
    tool_args.append(interpreter)
  if interpreter_args:
    tool_args.extend(interpreter_args)
  tool_args.append(executable_path)
  tool_args.extend(list(args))
  return tool_args


def ArgsForPythonTool(executable_path, *args):
  """Constructs an argument list for calling the Python interpreter.

  Args:
    executable_path: str, The full path to the Python main file.
    *args: args for the command

  Returns:
    An argument list to execute the Python interpreter
  """
  python_executable = GetPythonExecutable()
  python_args_str = os.environ.get('CLOUDSDK_PYTHON_ARGS', '')
  python_args = python_args_str.split()
  return _GetToolArgs(
      python_executable, python_args, executable_path, *args)


def ArgsForShellTool(executable_path, *args):
  """Constructs an argument list for calling the bash interpreter.

  Args:
    executable_path: str, The full path to the shell script.
    *args: args for the command

  Returns:
    An argument list to execute the bash interpreter
  """
  shell_bin = GetShellExecutable()
  return _GetToolArgs(shell_bin, [], executable_path, *args)


def ArgsForCMDTool(executable_path, *args):
  """Constructs an argument list for calling the cmd interpreter.

  Args:
    executable_path: str, The full path to the cmd script.
    *args: args for the command

  Returns:
    An argument list to execute the cmd interpreter
  """
  return _GetToolArgs('cmd', ['/c'], executable_path, *args)


def ArgsForBinaryTool(executable_path, *args):
  """Constructs an argument list for calling a native binary.

  Args:
    executable_path: str, The full path to the binary.
    *args: args for the command

  Returns:
    An argument list to execute the native binary
  """
  return _GetToolArgs(None, None, executable_path, *args)


class _ProcessHolder(object):
  PROCESS = None

  @staticmethod
  # pylint: disable=unused-argument
  def Handler(signum, frame):
    if _ProcessHolder.PROCESS:
      _ProcessHolder.PROCESS.terminate()
      ret_val = _ProcessHolder.PROCESS.wait()
    sys.exit(ret_val)


def Exec(args, env=None, no_exit=False):
  """Emulates the os.exec* set of commands, but uses subprocess.

  This executes the given command, waits for it to finish, and then exits this
  process with the exit code of the child process.

  Args:
    args: [str], The arguments to execute.  The first argument is the command.
    env: {str: str}, An optional environment for the child process.
    no_exit: bool, True to just return the exit code of the child instead of
      exiting.

  Returns:
    int, The exit code of the child if no_exit is True, else this method does
    not return.
  """
  # We use subprocess instead of execv because windows does not support process
  # replacement.  The result of execv on windows is that a new processes is
  # started and the original is killed.  When running in a shell, the prompt
  # returns as soon as the parent is killed even though the child is still
  # running.  subprocess waits for the new process to finish before returning.
  signal.signal(signal.SIGTERM, _ProcessHolder.Handler)
  p = subprocess.Popen(args, env=env)
  _ProcessHolder.PROCESS = p
  ret_val = p.wait()
  if no_exit:
    return ret_val
  sys.exit(ret_val)


def RestartGcloud():
  """Calls gcloud again with the same arguments as this invocation and exit."""
  gcloud = config.Paths().gcloud_path
  gcloud_args = sys.argv[1:]
  args = ArgsForPythonTool(gcloud, *tuple(gcloud_args))

  log.status.Print('Restarting gcloud command:\n  $ gcloud {args}'.format(
      args=' '.join(gcloud_args)))
  log.debug('Restarting gcloud: %s', args)
  log.out.flush()
  log.err.flush()

  Exec(args)
