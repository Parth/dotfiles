#!/usr/bin/env python
"""Setup module for gcutil.

To install gcutil, run:

  $ [sudo] python setup.py install
"""

import os
import sys
import textwrap

try:
  import setuptools
except ImportError:
  sys.stderr.write(textwrap.dedent("""\
      You must install setuptools before being able to install gcutil:
        https://pypi.python.org/pypi/setuptools
      """))
  sys.exit(1)


ROOT = os.path.dirname(os.path.realpath(__file__))

REQUIREMENTS = [
    'google-api-python-client==1.2',
    'google-apputils==0.4.0',
    'httplib2==0.8',
    'ipaddr==2.1.10',
    'iso8601==0.1.4',
    'python-gflags==2.0'
]

try:
  import argparse
except ImportError:
  REQUIREMENTS.append('argparse==1.2.1')


def GetVersion():
  with open(os.path.join(ROOT, 'VERSION')) as f:
    return f.read().strip()


if __name__ == '__main__':
  setuptools.setup(
      name='gcutil',
      description=(
          'Command-line tool for interacting with Google Compute Engine.'),
      url='https://code.google.com/p/google-compute-engine-tools',
      license='Apache 2.0',
      author='Google',
      author_email='gc-team@google.com',
      version=GetVersion(),
      install_requires=REQUIREMENTS,
      packages=['gcutil_lib', 'gcutil_lib.table'],
      package_dir={
          '': os.path.join('lib', 'google_compute_engine'),
      },
      package_data={
          'gcutil_lib': [os.path.join('compute', '*.json')],
      },
      entry_points={
          'console_scripts': [
              'gcutil = gcutil_lib.gcutil:Run',
          ],
      },
  )
