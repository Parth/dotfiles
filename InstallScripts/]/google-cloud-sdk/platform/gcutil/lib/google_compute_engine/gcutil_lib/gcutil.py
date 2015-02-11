#!/usr/bin/python
#
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

"""Command line tool for interacting with Google Compute Engine.

Please refer to http://developers.google.com/compute/docs/gcutil/tips for
more information about gcutil usage.
"""




import atexit
import logging
import sys


from google.apputils import appcommands
import gflags as flags

from gcutil_lib import address_cmds
from gcutil_lib import basic_cmds
from gcutil_lib import command_base
from gcutil_lib import disk_cmds
from gcutil_lib import disk_type_cmds
from gcutil_lib import firewall_cmds
from gcutil_lib import forwarding_rule_cmds
from gcutil_lib import http_health_check_cmds
from gcutil_lib import image_cmds
from gcutil_lib import instance_cmds
from gcutil_lib import machine_type_cmds
from gcutil_lib import move_cmds
from gcutil_lib import network_cmds
from gcutil_lib import operation_cmds
from gcutil_lib import project_cmds
from gcutil_lib import region_cmds
from gcutil_lib import route_cmds
from gcutil_lib import snapshot_cmds
from gcutil_lib import target_instance_cmds
from gcutil_lib import target_pool_cmds
from gcutil_lib import version_checker
from gcutil_lib import whoami
from gcutil_lib import zone_cmds


FLAGS = flags.FLAGS

# This utility will often be run in a VM and the local web server
# behavior can be annoying there.
FLAGS.SetDefault('auth_local_webserver', False)

# Ensure that the help will show global flags from command_base.
flags.ADOPT_module_key_flags(command_base)


def main(unused_argv):
  # The real work is performed by the appcommands.Run() method, which
  # first invokes this method, and then runs the specified command.

  # Set up early logging configuration
  format_string = '%(levelname)s: %(message)s'
  logging.basicConfig(stream=sys.stderr, format=format_string)

  # Next, register all the commands.
  address_cmds.AddCommands()
  basic_cmds.AddCommands()
  disk_cmds.AddCommands()
  disk_type_cmds.AddCommands()
  firewall_cmds.AddCommands()
  image_cmds.AddCommands()
  instance_cmds.AddCommands()
  machine_type_cmds.AddCommands()
  move_cmds.AddCommands()
  network_cmds.AddCommands()
  operation_cmds.AddCommands()
  project_cmds.AddCommands()
  route_cmds.AddCommands()
  snapshot_cmds.AddCommands()
  whoami.AddCommands()
  zone_cmds.AddCommands()

  target_pool_cmds.AddCommands()
  forwarding_rule_cmds.AddCommands()
  http_health_check_cmds.AddCommands()
  target_instance_cmds.AddCommands()

  region_cmds.AddCommands()

  # Registers the version checker.
  vc = version_checker.VersionChecker()
  atexit.register(vc.CheckForNewVersion)


def Run():
  sys.modules['__main__'] = sys.modules[__name__]
  appcommands.Run()


if __name__ == '__main__':
  Run()
