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

"""A simple thread pool class for doing multiple concurrent API operations."""



import logging
import Queue
import sys
import threading
import time
import traceback

LOGGER = logging.getLogger('gcutil-logs')


class ThreadPoolError(Exception):
  """An error occurred in this module."""
  pass


class Operation(object):
  """An operation to be executed by the threadpool.

  Override this and implement the Run() method.
  """

  def __init__(self):
    """Initializer."""
    self._result = None
    self._raised_exception = False

  def Run(self):
    """Override this method to execute this operation."""
    raise NotImplementedError('pure virtual method called')

  def _DoOperation(self):
    """Internal runner that captures result."""
    try:
      self._result = self.Run()
    except:  # pylint: disable=bare-except
      self._raised_exception = True
      a = sys.exc_info()
      # If a string was thrown, a[1] is None.  In Python 2.5, if an exception
      # was thrown without a message, a is a 1-tuple.  Otherwise, the exception
      # object is in a[1].
      if len(a) < 2 or a[1] is None:
        self._result = a[0]
      else:
        self._result = a[1]
      LOGGER.debug(traceback.format_exc())

  def Result(self):
    """Get the operation's result.

    If the operation is incomplete the return value will be None.  If the
    operation raised an exception, the return value will be the exception
    object.

    Returns:
      The operation's result.
    """
    return self._result

  def RaisedException(self):
    """Did the operation raise an exception?

    Will be False if the operation has not yet completed.

    Returns:
      True if an exception was raised by the operation.
    """
    return self._raised_exception


class Worker(threading.Thread):
  """Thread executing tasks from a given tasks queue."""

  def __init__(self, queue):
    threading.Thread.__init__(self)
    self._queue = queue
    self.daemon = True
    self.start()

  def run(self):
    # pylint: disable=protected-access
    while True:
      op = self._queue.get()
      if op is None:
        self._queue.task_done()
        break
      op._DoOperation()  # pylint: disable=protected-access
      self._queue.task_done()


class ThreadPool(object):
  """Pool of threads consuming tasks from a queue.

  Note that operations on the thread pool itself (submitting, waiting,
  shutdown) are not, themselves, multithread safe.
  """

  # States
  _NOT_RUNNING = 0
  _RUNNING = 1
  _TERMINATING = 3
  _TERMINATED = 4

  def __init__(self, num_threads, sleep_time):
    """Constructor for ThreadPool object.

    Args:
      num_threads:  The number of concurrent threads allowed in the
        thread pool.
      sleep_time:  The amount of time to wait between polls for the
        queue to empty.
    """
    self._queue = Queue.Queue()
    self._num_threads = num_threads
    self._state = self._NOT_RUNNING
    self._sleep_time = sleep_time

    self._workers = []
    for _ in range(num_threads):
      self._workers.append(Worker(self._queue))
    self._state = self._RUNNING

  def __del__(self):
    # Shut down everything so that we don't leak memory.
    if self._state == self._RUNNING:
      self.WaitShutdown()

  def Add(self, op):
    """Add an operation to the queue.

    Note that this is not thread safe.

    Args:
      op: An Operation object to add to the thread pool queue

    Raises:
      ThreadPoolError: if not in running state.
      ValueError: if op isn't an Operation object
    """
    if self._state != self._RUNNING:
      raise ThreadPoolError('ThreadPool not running')
    if not isinstance(op, Operation):
      raise ValueError('Nonoperation argument to AddOperation')
    self._queue.put(op)

  def _InternalWait(self):
    """Wait for all items to clear.

    This will come up for air once in a while so that we can capture
    keyboard interrupt.  Unfortunately Queue.join() isn't
    interruptable.
    """
    while not self._queue.empty():
      time.sleep(self._sleep_time)

  def WaitAll(self):
    """Wait for completion of all the tasks in the queue.

    Note that this is not thread safe.

    Raises:
      ThreadPoolError: if not in running state.
    """
    if self._state != self._RUNNING:
      raise ThreadPoolError('ThreadPool not running')
    self._InternalWait()

  def WaitShutdown(self):
    """Wait for completion of all tasks and shut down the ThreadPool.

    Note that this is not thread safe.
    """
    if self._state != self._RUNNING:
      raise ThreadPoolError('ThreadPool not running')
    self._state = self._TERMINATING
    # Inject a set of sentinal values to have the workers exit.
    for _ in range(self._num_threads):
      self._queue.put(None)
    self._InternalWait()
    self._state = self._TERMINATED
