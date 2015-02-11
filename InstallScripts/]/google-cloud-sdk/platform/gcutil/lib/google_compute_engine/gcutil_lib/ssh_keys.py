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

"""Utility class for creating/storing SSH keys."""

from __future__ import with_statement



import base64
import errno
import getpass
import os
import struct
import subprocess


import gflags as flags

from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_logging


PRIVATE_KEY_FILE = 'google_compute_engine'
PUBLIC_KEY_FILE = PRIVATE_KEY_FILE + '.pub'
HOME_DIRECTORY = os.path.expanduser('~')

flags.DEFINE_string(
    'public_key_file',
    os.path.join(HOME_DIRECTORY, '.ssh', PUBLIC_KEY_FILE),
    'The location of the default (generated) public ssh key for use '
    'with Google Cloud Compute instances.')

flags.DEFINE_string(
    'private_key_file',
    os.path.join(HOME_DIRECTORY, '.ssh', PRIVATE_KEY_FILE),
    'The location of the default (generated) private ssh key for use '
    'with Google Cloud Compute instances.')

flags.DEFINE_string(
    'ssh_user',
    getpass.getuser(),
    'The default ssh user for the instance.')

flags.DEFINE_boolean(
    'permit_root_ssh',
    False,
    'Disable safety check which prevents ssh to instances as root.')


FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER


class Error(Exception):
  pass


class UserSetupError(Error):
  """Raised the users environment isn't set up correctly."""

  def __init__(self, msg):
    Error.__init__(self)
    self.msg = msg

  def __str__(self):
    return self.msg


class SshKeys(object):
  """Collection of methods that work with Google Compute Engine SSH Keys."""

  @staticmethod
  def GetAuthorizedUserKeys(use_compute_key=True,
                            authorized_ssh_keys=None):
    """Get a typical list of ssh user/key dictionaries.

    Args:
      use_compute_key: authorize using ~/.ssh/compute.pub
      authorized_ssh_keys: key string user1:keyfile1,user2:keyfile2...

    Returns:
      A list of {'user': ..., 'key': ...} dictionaries.
    """
    user_keys = []

    if use_compute_key:
      user_keys.append(SshKeys.GetPublicKey())

    if authorized_ssh_keys:
      for user_key_file_pair in authorized_ssh_keys:
        split = user_key_file_pair.split(':', 1)
        if len(split) != 2:
          LOGGER.warn(
              'Skipping invalid public ssh key file: %s' % user_key_file_pair)
          continue

        user_keys.append({'user': split[0],
                          'key': SshKeys.GetKeyFromFile(split[1])})
    return user_keys

  @staticmethod
  def GetAuthorizedUserKeysFromMetadata(metadata):
    """Get the set of authorized user keys from the given metadata.

    Args:
      metadata: list of {'key': ..., 'value': ...} dictionaries.
    Returns:
      A list of {'user': ..., 'key':...} dictionaries.
    """

    def GetAuthorizedUserKeyFromLine(line):
      line_parts = line.split(':', 1)
      return {'user': line_parts[0], 'key': line_parts[1]}

    for metadata_entry in metadata:
      key = metadata_entry['key']
      value = metadata_entry['value']
      if key == 'sshKeys':
        lines = value.split('\n')
        return [GetAuthorizedUserKeyFromLine(line)
                for line in lines if ':' in line]
    return []

  @staticmethod
  def SetAuthorizedUserKeysInMetadata(metadata, authorized_user_keys):
    """Add the authorized public ssh keys to the given metadata.

    Args:
      metadata: A list of {'key': ..., 'value': ...} dictionaries.
      authorized_user_keys: A list of {'user': ..., 'key':...} dictionaries.
    Returns:
      The metadata updated to include exactly one 'sshKeys' entry that
      matches the given authorized user keys.
    """

    all_user_keys_string = '\n'.join(
        ['%(user)s:%(key)s' % user_keys for user_keys in authorized_user_keys])
    for metadata_entry in metadata:
      if metadata_entry['key'] == 'sshKeys':
        metadata_entry['value'] = all_user_keys_string
        return
    metadata.append({'key': 'sshKeys', 'value': all_user_keys_string})

  @staticmethod
  def GetPublicKey():
    """Returns the standard Compute key for the current user.

    If the key doesn't exist, it will be created and will
    interactively prompt the user.

    Returns:
      A dictionary of an user/key pair for the user's ssh key.

    Raises:
      gcutil_errors.CommandError:  Requires --permit_root_ssh flag to log in
      as root.
    """
    if FLAGS.ssh_user == 'root' and not FLAGS.permit_root_ssh:
      raise gcutil_errors.CommandError(
          'Logging into instances as root is not recommended. If you actually '
          'wish to log in as root, you must provide the --permit_root_ssh '
          'flag.')

    SshKeys.EnsureSshKeyCreated()

    return {'user': FLAGS.ssh_user,
            'key': SshKeys.GetKeyFromFile(FLAGS.public_key_file)}

  @staticmethod
  def EnsureSshKeyCreated():
    """Ensures that the ssh key actually exists.

    This will create a public/private key pair if no existing
    key pair is found.

    Raises:
      UserSetupError: Error when generating the ssh key
    """
    if (os.path.exists(FLAGS.public_key_file) and
        os.path.exists(FLAGS.private_key_file)):
      return

    LOGGER.warn('You don\'t have an ssh key for Google Compute Engine. '
                'Creating one now...')
    ssh_directory = os.path.dirname(FLAGS.private_key_file)
    try:
      os.mkdir(ssh_directory, 0700)
    except OSError as e:
      if e.errno != errno.EEXIST:
        raise UserSetupError(
            'Error creating ssh key directory %s: %s.' % (ssh_directory, e))
      elif not os.path.isdir(ssh_directory):
        raise UserSetupError('%s must be a directory %s.' % ssh_directory)
    command_line = [
        'ssh-keygen',
        '-t', 'rsa',
        '-q',
        '-f', FLAGS.private_key_file,
    ]

    LOGGER.debug(' '.join(command_line))
    try:
      process = subprocess.Popen(command_line)
      process.communicate()
      if process.wait() != 0:
        raise UserSetupError('Error generating compute ssh key.')
    except OSError as e:
      raise UserSetupError('There was a problem running ssh-keygen: %s' % e)

  @staticmethod
  def GetKeyFromFile(key_file):
    """Read an ssh key from key_file, and return it.

    Args:
      key_file: the file containing the ssh key

    Returns:
      A the ssh key stored in the file.
    """
    key_file = os.path.expanduser(key_file)
    with open(key_file) as f:
      return SshKeys._ValidateSshKey(f.read().strip(), key_file)

  @staticmethod
  def _ValidateSshKey(key, key_file):
    """Validates the public ssh key format (OpenSSH).

    Args:
      key: string containing the public ssh key.
      key_file: filename whence the key cometh.

    Returns:
      the ssh key value (value of key parameter) if validation has passed.

    Raises:
      UserSetupError: if the key validation fails.
    """
    if not key:
      raise UserSetupError(
          'Public key file (%s) doesn\'t contain a key.' % key_file)
    if '\n' in key:
      raise UserSetupError(
          'Public key file (%s) has invalid format. '
          'It must only contain single line.\n%s' % (key_file, key))
    # Validate the OpenSSH key format
    parts = key.split(None, 2)
    if len(parts) < 2:
      raise UserSetupError(
          'Public key file (%s) doesn\'t contain an OpenSSH public key. '
          'The key must consist of at least two space separated parts.\n%s' %
          (key_file, key))

    key_type, key_value = parts[0:2]

    try:
      key_value = base64.b64decode(key_value)
    except TypeError:
      raise UserSetupError(
          'Public key file (%s) doesn\'t contain an OpenSSH public key. '
          'The key is not a valid base64 encoded value.\n%s' %
          (key_file, key))

    if len(key_value) < 4:
      raise UserSetupError(
          'Public key file (%s) doesn\'t contain an OpenSSH public key. '
          'The key has invalid length.\n%s' %
          (key_file, key))

    # First 4 bytes is the length of key type.
    decoded_length = struct.unpack_from('>I', key_value)[0]
    if len(key_value) < 4 + decoded_length:
      raise UserSetupError(
          'Public key file (%s) doesn\'t contain an OpenSSH public key. '
          'The key doesn\'t have a valid type.\n%s' %
          (key_file, key))

    decoded_type = key_value[4:4 + decoded_length]
    if key_type != decoded_type:
      raise UserSetupError(
          'Public key file (%s) doesn\'t contain an OpenSSH public key. '
          'The decoded key type doesn\'t match.\n%s' %
          (key_file, key))

    return key
