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

"""Common code for logging across gcutil."""

import logging

from apiclient import model
import gflags as flags

from gcutil_lib import gcutil_flags

FLAGS = flags.FLAGS

_LOG_ROOT = 'gcutil-logs'
LOGGER = logging.getLogger(_LOG_ROOT)

CRITICAL = logging.CRITICAL
FATAL = logging.FATAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG

_LOG_LEVELS = (DEBUG, INFO, WARNING, ERROR, CRITICAL)
_LOG_LEVEL_NAMES = tuple(map(logging.getLevelName, _LOG_LEVELS))


gcutil_flags.DEFINE_case_insensitive_enum(
    'log_level',
    logging.getLevelName(logging.INFO),
    _LOG_LEVEL_NAMES,
    'Logging output level for core Google Compute Engine messages.  '
    'For logging output from other libraries, use library_log_level.')
gcutil_flags.DEFINE_case_insensitive_enum(
    'library_log_level',
    logging.getLevelName(logging.WARN),
    _LOG_LEVEL_NAMES,
    'Logging output level for libraries.')
if hasattr(model, 'dump_request_response'):
  flags.DEFINE_boolean(
      'dump_request_response',
      False,
      'Dump all http server requests and responses. ')


def SetupLogging():
  """Set up a logger that will have its own logging level."""
  gc_handler = logging.StreamHandler()
  gc_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
  LOGGER.addHandler(gc_handler)
  LOGGER.propagate = False

  log_level_map = dict(
      [(logging.getLevelName(level), level) for level in _LOG_LEVELS])

  # Update library_log_level to INFO if user wants to see
  # dump_request_response.
  if hasattr(model, 'dump_request_response'):
    model.dump_request_response = FLAGS.dump_request_response
  if FLAGS.dump_request_response:
    if (not FLAGS['library_log_level'].present and
        not logging.getLogger().isEnabledFor(logging.INFO)):
      FLAGS.library_log_level = 'INFO'

  LOGGER.setLevel(log_level_map[FLAGS.log_level])
  logging.getLogger().setLevel(log_level_map[FLAGS.library_log_level])
