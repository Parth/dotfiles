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

import os
import sys


def InitSysPath():

  libs_dir = os.path.dirname(
      os.path.dirname(
          os.path.dirname(os.path.realpath(__file__))))
  libs = [os.path.join(libs_dir, lib) for lib in os.listdir(libs_dir)]

  # Removes entries from libs that are already on the path.
  libs = list(set(libs) - set(sys.path))

  sys.path = libs + sys.path
