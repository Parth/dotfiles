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

all:
	true

# This is designed to work with dh_make and dpkg-buildpackage to
# create gcutil Debian packages.  It can also be used to install
# locally in /usr/...
install:
	mkdir -p $(DESTDIR)/usr/bin $(DESTDIR)/usr/share/google/gcutil
	cp -r lib $(DESTDIR)/usr/share/google/gcutil
	install -m 755 gcutil $(DESTDIR)/usr/share/google/gcutil
	ln -sf ../share/google/gcutil/gcutil $(DESTDIR)/usr/bin/gcutil
