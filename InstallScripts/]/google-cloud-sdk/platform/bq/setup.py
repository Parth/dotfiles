#!/usr/bin/env python
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Setup configuration."""

import platform

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup  # pylint: disable=g-import-not-at-top

# Configure the required packages and scripts to install, depending on
# Python version and OS.
REQUIRED_PACKAGES = [
    'google-apputils',
    'python-gflags',
    'google-api-python-client==1.2',
    'oauth2client==1.2',
    'httplib2',
    ]
CONSOLE_SCRIPTS = [
    'bq = bq:run_main',
    ]

if platform.system() == 'Windows':
  REQUIRED_PACKAGES.append('pyreadline')

py_version = platform.python_version()
if py_version < '2.6.5' or py_version >= '3':
  raise ValueError('BigQuery requires Python >= 2.6.5.')

_BQ_VERSION = '2.0.18'

setup(name='bigquery',
      version=_BQ_VERSION,
      description='BigQuery command-line tool',
      url='http://code.google.com/p/google-bigquery-tools/',
      author='Google Inc.',
      author_email='bigquery-team@google.com',
      # Contained modules and scripts.
      py_modules=[
          'bq',
          'bq_flags',
          'bigquery_client',
          'table_formatter',
          ],
      entry_points={
          'console_scripts': CONSOLE_SCRIPTS,
          },
      install_requires=REQUIRED_PACKAGES,
      provides=[
          'bigquery (%s)' % (_BQ_VERSION,),
          ],
      # Information for packaging of the discovery document.
      include_package_data=True,
      packages=['discovery'],
      package_data={
          'discovery': ['*'],
          },
      # PyPI package information.
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.7',
          'Topic :: Database :: Front-Ends',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      license='Apache 2.0',
      keywords='google bigquery library',
     )
