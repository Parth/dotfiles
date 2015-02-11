# Copyright 2014 Google Inc. All Rights Reserved.
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

"""Helper module for initial Windows user account name."""

from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_logging
from gcutil_lib import metadata
from gcutil_lib import utils

LOGGER = gcutil_logging.LOGGER

_MAX_USER_NAME_LENGTH = 20
_INVALID_USER_NAME_CHARS = set(r'"/\[]:;|=,+*?<>@')
_BUILTIN_ADMINISTRATOR = 'administrator'


def GenerateLocalUserNameBasedOnProject(project_id_or_number, api):
  """Generates the Windows user account name based on the project ID.

  Args:
    project_id_or_number: The string that is project ID or project number.
    api: The Google Compute Engine API client.

  Returns:
    Generated user account name.
  """
  project_id = utils.GetProjectId(project_id_or_number, api)

  # We first remove the domain part in the project ID, and then take up to
  # the first 20 chars in the remaining project ID as the user name.
  # (Windows local user name should not be more than 20 char long.)
  user_name = project_id.split(':')[-1][:_MAX_USER_NAME_LENGTH]

  # Char set for project id is more restrictive than Windows user name, but we
  # still do the check just in case.
  try:
    ValidateUserName(user_name)
  except gcutil_errors.CommandError as e:
    raise gcutil_errors.CommandError(
        'The user name %s generated from project id %s is invalid. '
        'This is unexpected.  Please double check the project id. '
        'Error: %s' % (user_name, project_id, e.message))

  return user_name


def ValidateUserName(user_name):
  """Validates the initial user account name.

  Args:
    user_name: The user account name to be validated.

  Raises:
    CommandError: The user name is invalid.
  """
  # Validates according to
  # http://technet.microsoft.com/en-us/library/cc770642.aspx
  # We also ban the builtin administrator account name.
  if not user_name:
    raise gcutil_errors.CommandError('The user name is missing.')
  if user_name.lower() == _BUILTIN_ADMINISTRATOR:
    raise gcutil_errors.CommandError(
        'Using "%s" as initial user name is not allowed. '
        'Please choose a different user name by setting metadata entry %s.'
        % (_BUILTIN_ADMINISTRATOR, metadata.INITIAL_WINDOWS_USER_METADATA_NAME))
  if len(user_name) > _MAX_USER_NAME_LENGTH:
    raise gcutil_errors.CommandError(
        'User name length must not exceed %d characters: %s'
        % (_MAX_USER_NAME_LENGTH, user_name))
  if any(c in _INVALID_USER_NAME_CHARS for c in user_name):
    raise gcutil_errors.CommandError(
        'User name %s contains invalid characters.' % user_name)
  if all(c in ' .' for c in user_name):
    raise gcutil_errors.CommandError(
        'User name cannot consist solely of periods or spaces.')
