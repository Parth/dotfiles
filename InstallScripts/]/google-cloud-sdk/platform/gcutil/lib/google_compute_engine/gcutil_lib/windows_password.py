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

"""Helper module to manage initial password for Windows images."""

import random
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_logging

LOGGER = gcutil_logging.LOGGER

MIN_PASSWORD_LENGTH = 8
NON_ALPHA_NUM_CHARS = '~!@#$%^&*_-+=`|\\(){}[]:;"\'<>,.?/'
MIN_CHAR_CATEGORIES = 3

# Max number of attempts to generate password.
_MAX_GENERATION_ATTEMPT = 15

# The character set that we will generate password from.
# Some characters are excluded because they may be confusing
# on display.
_CANDIDATES_UPPER = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
_CANDIDATES_LOWER = 'abcdefghijkmnopqrstuvwxyz'
_CANDIDATES_DIGIT = '123456789'
_CANDIDATES_ALPHA_NUM = (_CANDIDATES_UPPER + _CANDIDATES_LOWER
                         + _CANDIDATES_DIGIT)
_CANDIDATES_NON_ALPHA_NUM = '~!@#$%^&*_-+=`\\(){}[]:;"\'<>,.?/'


def GeneratePassword(user_account_name):
  """Generates a random password for Windows user account.

  Args:
    user_account_name: The user account name that we generate password for.

  Returns:
    The generated password.
  """
  r = random.SystemRandom()
  for _ in xrange(_MAX_GENERATION_ATTEMPT):
    # First pick 12 chars randomly from letters and digits.
    char_list = list(r.choice(_CANDIDATES_ALPHA_NUM)
                     for _ in xrange(12))
    # Split the list into 3 groups of 4 chars each.
    # Add a random non-alpha-num char between the groups.
    char_list.insert(4, r.choice(_CANDIDATES_NON_ALPHA_NUM))
    char_list.insert(9, r.choice(_CANDIDATES_NON_ALPHA_NUM))
    password = ''.join(char_list)

    try:
      ValidateStrongPasswordRequirement(password, user_account_name)
      return password
    except gcutil_errors.CommandError:
      pass
  raise gcutil_errors.CommandError(
      'Failed to generate password after %d attempts.'
      % _MAX_GENERATION_ATTEMPT)


def ValidateStrongPasswordRequirement(password, user_account_name):
  """Validates that a password meets strong password requirement.

  The strong password must be at least 8 chars long and meet the
  Windows password complexity requirement documented at
  http://technet.microsoft.com/en-us/library/cc786468(v=ws.10).aspx

  Args:
    password: Password to be validated.
    user_account_name: The user account name.

  Raises:
    CommandError: The password does not meet the strong password requirement.
  """
  if not password or len(password) < MIN_PASSWORD_LENGTH:
    raise gcutil_errors.CommandError(
        'Windows password must be at least %d characters long.' %
        MIN_PASSWORD_LENGTH)

  categories = 0
  uppercase = False
  lowercase = False
  digit = False
  nonalphanum = False
  alpha = False
  for x in password:
    if x.isupper():
      uppercase = True
    elif x.islower():
      lowercase = True
    elif x.isdigit():
      digit = True
    elif x in NON_ALPHA_NUM_CHARS:
      nonalphanum = True
    elif x.isalpha():
      alpha = True
    categories = uppercase + lowercase + digit + nonalphanum + alpha
    if categories >= MIN_CHAR_CATEGORIES:
      break
  if categories < MIN_CHAR_CATEGORIES:
    raise gcutil_errors.CommandError(
        'Windows password must contain at least 3 types of characters. See '
        'http://technet.microsoft.com/en-us/library/cc786468(v=ws.10).aspx')

  # Currently, we do not set the user display name.  So we only need to
  # check and make sure that the password does not contain the user account
  # name.
  if (len(user_account_name) >= 3
      and user_account_name.lower() in password.lower()):
    raise gcutil_errors.CommandError(
        'Windows password cannot contain the user account name: %s.' %
        user_account_name)
