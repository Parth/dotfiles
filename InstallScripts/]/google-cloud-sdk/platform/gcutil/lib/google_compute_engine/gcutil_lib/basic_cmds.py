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

"""Commands for interacting with Google Compute Engine."""



import json


from google.apputils import appcommands
import gflags as flags

from gcutil_lib import auth_helper
from gcutil_lib import command_base
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_logging
from gcutil_lib import metadata
from gcutil_lib import scopes
from gcutil_lib import utils
from gcutil_lib import version


FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER


class AuthCommand(command_base.GoogleComputeCommand):
  """Class for forcing client authorization."""

  def __init__(self, name, flag_values):
    super(AuthCommand, self).__init__(name, flag_values)
    flags.DEFINE_boolean('force_reauth',
                         True,
                         'If True, will force user to reauthorize',
                         flag_values=flag_values)
    flags.DEFINE_boolean('just_check_auth',
                         False,
                         'If True, just check if auth exists',
                         flag_values=flag_values)
    flags.DEFINE_boolean('confirm_email',
                         True,
                         'Get info about the user and echo the email',
                         flag_values=flag_values)

  def DenormalizeProjectName(self, flag_values):
    # Auth command doesn't require project.
    pass

  def RunWithFlagsAndPositionalArgs(self,
                                    flag_values,
                                    unused_pos_arg_values):
    """Run the command, returning the result.

    Args:
      flag_values: The parsed FlagValues instance.
      unused_pos_arg_values: The positional args.

    Raises:
      gcutil_errors.CommandError: If valid credentials cannot be retrieved.

    Returns:
      0 if the command completes successfully, otherwise 1.

    Raises:
      CommandError: if valid credentials are not located.
    """
    cred = auth_helper.GetCredentialFromStore(
        scopes.DEFAULT_AUTH_SCOPES,
        ask_user=not flag_values.just_check_auth,
        force_reauth=flag_values.force_reauth)
    if not cred:
      raise gcutil_errors.CommandError(
          'Could not get valid credentials for API.')

    if flag_values.confirm_email:
      http = self._AuthenticateWrapper(utils.GetHttp())
      resp, content = http.request('https://www.googleapis.com/userinfo/v2/me')
      if resp.status != 200:
        LOGGER.info('Could not get user info for token.  <%d %s>',
                    resp.status, resp.reason)
      userinfo = json.loads(content)
      if 'email' in userinfo and userinfo['email']:
        LOGGER.info('Authorization succeeded for user %s', userinfo['email'])
      else:
        LOGGER.info('Could not get email for token.')
    else:
      LOGGER.info('Authentication succeeded.')
    return (None, [])

  def PrintResult(self, result):
    """Print the result of the authentication command.

    Args:
      result: The result of the authentication command.
    """
    pass


class GetVersion(command_base.GoogleComputeCommand):
  """Get the current version of this command."""

  def __init__(self, name, flag_values):
    super(GetVersion, self).__init__(name, flag_values)

  def Run(self, unused_argv):
    """Return the current version information.

    Args:
      None expected.

    Returns:
      Version of this command.
    """
    print version.__version__
    return 0


def AddCommands():
  appcommands.AddCmd('auth', AuthCommand)
  appcommands.AddCmd('config', AuthCommand)  # So we look and feel like gsutil.
  appcommands.AddCmd('version', GetVersion)
