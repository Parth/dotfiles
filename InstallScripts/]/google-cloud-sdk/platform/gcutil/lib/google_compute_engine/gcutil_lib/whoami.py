# Copyright 2013 Google Inc. All Rights Reserved.
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

"""Commands for determining the authenticated user in gcutil."""

import sys


from google.apputils import appcommands

from gcutil_lib import auth_helper
from gcutil_lib import gcutil_logging
from gcutil_lib import scopes


LOGGER = gcutil_logging.LOGGER


class WhoAmI(appcommands.Cmd):
  """Identify the authenticated user."""

  def __init__(self, name, flag_values):
    super(WhoAmI, self).__init__(name, flag_values)

  def Run(self, unused_argv):
    """Identifies the authenticated user."""

    LOGGER.warn('This command is deprecated and will be removed in a '
                'later version. Please use "gcloud auth" for your '
                'authentication needs and "gcloud config list" to determine '
                'the currently logged-in user.')

    credential = auth_helper.GetCredentialFromStore(
        scopes.DEFAULT_AUTH_SCOPES, ask_user=False)

    if credential and credential.id_token:
      print credential.id_token['email']
      return 0
    elif (credential and
          (not credential.id_token or 'email' not in credential.id_token)):
      sys.stderr.write('You are authenticated, but the user id has not been '
                       'logged. Try re-authenticating using "gcloud auth".\n')
      return 1
    else:
      sys.stderr.write(
          'You haven\'t set up your account yet. Please run "gcloud auth".\n')
      return 1


def AddCommands():
  appcommands.AddCmd('whoami', WhoAmI)
