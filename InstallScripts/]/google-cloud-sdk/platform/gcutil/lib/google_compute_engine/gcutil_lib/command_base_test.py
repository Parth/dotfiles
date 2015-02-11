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

"""Unit tests for the base command classes."""

from __future__ import with_statement



import path_initializer
path_initializer.InitSysPath()

import copy
import datetime
import json
import os
from StringIO import StringIO
import sys
import tempfile
import textwrap


import oauth2client.client as oauth2_client


from google.apputils import app

import gflags as flags
import unittest

from gcutil_lib import command_base
from gcutil_lib import disk_cmds
from gcutil_lib import gce_api
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_logging
from gcutil_lib import gcutil_unittest
from gcutil_lib import instance_cmds
from gcutil_lib import mock_api
from gcutil_lib import mock_lists
from gcutil_lib import mock_timer
from gcutil_lib import network_cmds
from gcutil_lib import old_mock_api
from gcutil_lib import version


FLAGS = flags.FLAGS


class CommandBaseTest(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)

  def testReadInSelectedItem(self):
    test_choices = [('unique first word', 'unique'),
                    ('duplicate first word', 'duplicate-1'),
                    ('duplicate first word two', 'duplicate-2'),
                    ('word', 'word'),
                    ('wordy', 'wordy')]

    set_flags = {
        'project': 'irrelevant',
        }

    command = self._CreateAndInitializeCommand(
        instance_cmds.AddInstance, 'addinstance', self.version,
        set_flags=set_flags)

    for i in range(1, len(test_choices)+1):
      with gcutil_unittest.CaptureStandardIO('%s\n' % i):
        result = command._presenter._ReadInSelectedItem(test_choices, 'choices')
        self.assertEquals(result, i)

    with gcutil_unittest.CaptureStandardIO('0\n3\n'):
      result = command._presenter._ReadInSelectedItem(test_choices, 'choices')
      self.assertEquals(result, 3)

    with gcutil_unittest.CaptureStandardIO('duplicate\nword\n'):
      result = command._presenter._ReadInSelectedItem(test_choices, 'choices')
      self.assertEquals(result, 4)

    with gcutil_unittest.CaptureStandardIO('unique\n'):
      result = command._presenter._ReadInSelectedItem(test_choices, 'choices')
      self.assertEquals(result, 1)

    with gcutil_unittest.CaptureStandardIO('word\n'):
      result = command._presenter._ReadInSelectedItem(test_choices, 'choices')
      self.assertEquals(result, 4)

    with gcutil_unittest.CaptureStandardIO('uni\nwordy\n'):
      result = command._presenter._ReadInSelectedItem(test_choices, 'choices')
      self.assertEquals(result, 5)

  def testPromptForZoneDoesNotListZonesInMaintenance(self):
    expected_project = 'test_project'
    expected_disk = 'test_disk'
    selected_zone = 1

    set_flags = {
        'project': expected_project,
        }

    command = self._CreateAndInitializeCommand(
        disk_cmds.AddDisk, 'adddisk', self.version, set_flags=set_flags)

    now = datetime.datetime.utcnow()

    zones = ['recently', 'none', 'soon', 'tomorrow', 'next_week']
    maintenance = [
        mock_lists.GetSampleMaintenanceWindows(
            1, ref_time=now + datetime.timedelta(minutes=-30)),
        mock_lists.GetSampleMaintenanceWindows(0),
        mock_lists.GetSampleMaintenanceWindows(
            1, ref_time=now + datetime.timedelta(hours=1)),
        mock_lists.GetSampleMaintenanceWindows(
            1, ref_time=now + datetime.timedelta(days=1, hours=1)),
        mock_lists.GetSampleMaintenanceWindows(
            1, ref_time=now + datetime.timedelta(weeks=1))]

    mock_lists.GetSampleZoneListCall(command, self.mock, len(zones),
                                     name=zones,
                                     maintenanceWindows=maintenance)

    def ZoneResponse(unused_uri, unused_http_method, parameters, unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#zone',
              'name': parameters['zone'],
          },
          False)

    self.mock.RespondF('compute.zones.get', ZoneResponse)

    def DiskResponse(unused_uri, unused_http_method, parameters, body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#disk',
              'name': json.loads(body)['name'],
              'zone': command.NormalizeGlobalResourceName(expected_project,
                                                          'zones',
                                                          parameters['zone'])
          },
          False)

    self.mock.RespondF('compute.disks.insert', DiskResponse)

    with gcutil_unittest.CaptureStandardIO('%s\n' % selected_zone) as stdio:
      command.Handle(expected_disk)

      output = stdio.stdout.getvalue()

      # The zone in maintenance is not listed.
      self.assertFalse('recently' in output)

      # The others are.
      self.assertTrue('none' in output)
      self.assertTrue('soon' in output)
      self.assertTrue('tomorrow' in output)
      self.assertTrue('next_week' in output)

  def testPrintAggregatedLists(self):
    """Test printing of aggregated lists."""

    set_flags = {
        'project': 'user',
        'columns': ['name', 'zone'],
    }

    command = self._CreateAndInitializeCommand(
        instance_cmds.ListInstances, 'listinstances', self.version, set_flags)

    self.mock.Respond('compute.instances.aggregatedList', {
        'kind': 'compute#instanceAggregatedList',
        'items': {
            'zones/danger-a': {
                'warning': {
                    'code': 'TOO_DANGEROUS',
                    'message': 'You\'re in the danger zone!',
                },
            },
            'zones/twilight-a': {
                'instances': [
                    {
                        'name': 'foo',
                        'zone': 'twilight-a',
                    },
                    {
                        'name': 'bar',
                        'zone': 'twilight-a',
                    },
                ],
            },
            'zones/cool-a': {
                'instances': [
                    {
                        'name': 'bot',
                        'zone': 'cool-a',
                    },
                ],
            },
        },})

    result = command.Handle()

    expected_output = textwrap.dedent("""\
        +------+------------+
        | name | zone       |
        +------+------------+
        | bar  | twilight-a |
        +------+------------+
        | bot  | cool-a     |
        +------+------------+
        | foo  | twilight-a |
        +------+------------+
        """)

    with gcutil_unittest.CaptureStandardIO() as stdio:
      command._PrintAggregatedList(result)
      self.assertEquals(expected_output, stdio.stdout.getvalue())

  def testPromptsFailIfNotTty(self):
    class MockNotTty(object):
      def isatty(self):
        return False

    oldin = sys.stdin
    sys.stdin = MockNotTty()

    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

      def SetApi(self, api):
        pass

    set_flags = {
        'project': 'user',
        'require_tty': True,
        }
    command = self._CreateAndInitializeCommand(MockCommand,
                                               'mock_command',
                                               self.version,
                                               set_flags)

    self.assertRaises(
        IOError, command._presenter._ReadInSelectedItem, 'foo', 'bar')
    self.assertRaises(
        IOError, command._PresentSafetyPrompt, 'bot')

    sys.stdin = oldin

  def testResolveImageTrack(self):
    """Make sure ResolveImageTrackOrImage works as desired."""

    def BuildMockImage(name):
      return {
          'name': name,
          'selfLink': 'http://server/service/%s' % name,
      }

    class MockImages(object):
      """Mock api for test images."""

      def list(self, *unused_args, **kwargs):
        project = kwargs['project']
        return {
            'userproject': old_mock_api.MockRequest({
                'kind': 'compute#image',
                'items': [
                    BuildMockImage('customer-img1-v20120401'),
                    BuildMockImage('customer-img1-v20120402'),
                    BuildMockImage('customer-img1-v20120404'),
                    BuildMockImage('debian-6-blahblah'),
                ]
            }),
            'centos-cloud': old_mock_api.MockRequest({
                'kind': 'compute#image',
                'items': [
                    BuildMockImage('centos-6-v20130101'),
                    BuildMockImage('centos-6-v20130102'),
                    BuildMockImage('centos-6-v20130103'),
                ]
            }),
            'coreos-cloud': old_mock_api.MockRequest({
                'kind': 'compute#image',
                'items': [
                    BuildMockImage('coreos-alpha-367-0-0-v20140703'),
                    BuildMockImage('coreos-beta-353-0-0-v20140625'),
                ]}),
            'debian-cloud': old_mock_api.MockRequest({
                'kind': 'compute#image',
                'items': [
                    BuildMockImage('debian-6-squeeze-v20130101'),
                    BuildMockImage('debian-6-squeeze-v20130102'),
                    BuildMockImage('debian-7-wheezy-v20130103'),
                    BuildMockImage('debian-7-wheezy-v20130104'),
                ]}),
            'google': old_mock_api.MockRequest({
                'kind': 'compute#image',
                'items': [
                    BuildMockImage('gcel-12-04-v20120101'),
                    BuildMockImage('gcel-12-04-v20120701'),
                    BuildMockImage('gcel-12-04-v20120702'),
                ]}),
            'rhel-cloud': old_mock_api.MockRequest({
                'kind': 'compute#image',
                'items': [
                    BuildMockImage('rhel-6-4-v20131204'),
                ]}),
            'suse-cloud': old_mock_api.MockRequest({
                'kind': 'compute#image',
                'items': [
                    BuildMockImage('sles11-sp3-v20131209'),
                ]}),
            'opensuse-cloud': old_mock_api.MockRequest({
                'kind': 'compute#image',
                'items': [
                    BuildMockImage('opensuse131-20140227'),
                    BuildMockImage('opensuse131-v20140417'),
                ]}),
            'windows-cloud': old_mock_api.MockRequest({
                'kind': 'compute#image',
                'items': [
                    BuildMockImage('windows-server-2008-r2-dc-v20140219'),
                ]}),
        }[project]

    presenter = lambda image: image['selfLink']
    self._images = MockImages()

    resolver = command_base.ResolveImageTrackOrImage

    # An image resolves to itself.
    self.assertTrue(
        resolver(self._images, 'userproject', 'customer-img1-v20120401',
                 presenter).endswith('/customer-img1-v20120401'))

    # Pass through bad image names too.
    self.assertEquals(
        'BadImagename',
        resolver(self._images, 'userproject', 'BadImagename', presenter))

    # Also pass through fully qualified names.
    self.assertEquals(
        'https://example.com/foo',
        resolver(self._images, 'userproject', 'https://example.com/foo',
                 presenter))

    # Lookups work correctly when fully specified.
    self.assertTrue(
        resolver(self._images, 'userproject', 'debian-7-wheezy-v20130103',
                 presenter).endswith('/debian-7-wheezy-v20130103'))

    # Fancy resolution does not happen in customer projects.
    self.assertTrue(
        resolver(self._images, 'userproject', 'debian-6', presenter).endswith(
            '/debian-6-squeeze-v20130102'))

    # Lookups on abbreviated image names resolve to the newest image in
    # the track.
    self.assertTrue(
        resolver(self._images, 'userproject', 'debian-7', presenter).endswith(
            '/debian-7-wheezy-v20130104'))

    # If you abbreviate an image to the point of ambiguity, we just pass the
    # result through.
    self.assertEquals(
        'debian',
        resolver(self._images, 'userproject', 'debian', presenter))

    # Opensuse's naming inconsistency is accounted for. (missing -v in date).
    self.assertTrue(
        resolver(self._images, 'userproject', 'opensuse',
                 presenter).endswith('/opensuse131-v20140417'))

    # CoreOS is prefixed on coreos instead of coreos-beta-353-0-0.
    self.assertTrue(
        resolver(self._images, 'userproject', 'coreos-beta',
                 presenter).endswith('/coreos-beta-353-0-0-v20140625'))

  def testWarnAboutErrors(self):
    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

      def SetApi(self, api):
        pass

    example_result = {
        'error': {
            'errors': [{
                'code': 'MOCK_ERROR',
                'message': 'A mock error.'
            }]
        },
        'kind': 'compute#thing',
    }

    example_list_result = {
        'items': [example_result],
        'kind': 'compute#thingList'
    }

    example_no_error_result = {
        'name': 'successful-thing',
        'kind': 'compute#thing',
    }

    example_no_error_list_result = {
        'items': [example_no_error_result],
        'kind': 'compute#thingList'
    }

    example_bogus_error_result = {
        'error': {},
        'kind': 'compute#thing',
    }

    command = self._CreateAndInitializeCommand(MockCommand, 'command')

    with gcutil_unittest.CaptureStandardIO() as stdio:
      command._WarnAboutErrors(example_result)
      self.assertTrue('MOCK_ERROR' in stdio.stderr.getvalue())

    with gcutil_unittest.CaptureStandardIO() as stdio:
      command._WarnAboutErrors(example_list_result)
      self.assertTrue('MOCK_ERROR' in stdio.stderr.getvalue())

    with gcutil_unittest.CaptureStandardIO() as stdio:
      command._WarnAboutErrors(example_no_error_result)
      self.assertEqual('', stdio.stderr.getvalue())

    with gcutil_unittest.CaptureStandardIO() as stdio:
      command._WarnAboutErrors(example_no_error_list_result)
      self.assertEqual('', stdio.stderr.getvalue())

    with gcutil_unittest.CaptureStandardIO() as stdio:
      command._WarnAboutErrors(example_bogus_error_result)
      self.assertEqual('', stdio.stderr.getvalue())

  def testAuthRetries(self):
    class MockAuthCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockAuthCommand, self).__init__(name, flag_values)
        self.refresh_errors_to_throw = 0
        self.run_calls = 0

      def Reset(self):
        self.refresh_errors_to_throw = 0
        self.run_calls = 0

      def SetApi(self, api):
        pass

      def RunWithFlagsAndPositionalArgs(self, unused_flags, unused_args):
        self.run_calls += 1
        if self.refresh_errors_to_throw:
          self.refresh_errors_to_throw -= 1
          raise oauth2_client.AccessTokenRefreshError()
        return {}, []

    FLAGS.project = 'someproject'

    command = self._CreateAndInitializeCommand(MockAuthCommand, 'auth')

    self.assertEqual(0, command.Run([]))
    self.assertEqual(1, command.run_calls)
    command.Reset()

    command.refresh_errors_to_throw = 1
    self.assertEqual(0, command.Run([]))
    self.assertEqual(2, command.run_calls)
    command.Reset()

    command.refresh_errors_to_throw = 2
    self.assertEqual(1, command.Run([]))
    self.assertEqual(2, command.run_calls)
    command.Reset()

    FLAGS.Reset()

  def testPrintNamesOnlyDoesNotElideString(self):
    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

      def SetApi(self, api):
        pass

    set_flags = {
        'project': 'user',
        }

    command = self._CreateAndInitializeCommand(MockCommand,
                                               'mock_command',
                                               self.version,
                                               set_flags)

    name = 'some-test-instance-with-a-super-long-name-at-a-stunning-64-chars'
    path = ('https://www.googleapis.com/compute/v1/projects/user/zones'
            '/danger-a/instances/{0}'.format(name))

    result = {
        'kind': 'compute#instanceAggregatedList',
        'items': {
            'zones/danger-a': {
                'instances': [{
                    'name': name,
                    'kind': 'compute#instance',
                    'selfLink': path
                }]
            }
        }
    }

    with gcutil_unittest.CaptureStandardIO() as stdio:
      command._PrintNamesOnly(result)

      self.assertEqual(stdio.stdout.getvalue(),
                       'danger-a/instances/{0}\n'.format(name))

  def testPresentElement(self):
    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

      def SetApi(self, api):
        pass

    set_flags = {
        'project': 'user',
        'long_values_display_format': 'elided',
        }
    command = self._CreateAndInitializeCommand(MockCommand,
                                               'mock_command',
                                               self.version,
                                               set_flags)

    self.assertEqual(
        'user',
        command._presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/user'))
    self.assertEqual(
        'user',
        command._presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/user/'))
    self.assertEqual('user', command._presenter.PresentElement('projects/user'))
    self.assertEqual(
        'user', command._presenter.PresentElement('projects/user/'))
    self.assertEqual(
        'standard-2-cpu',
        command._presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/'
            'projects/user/machineTypes/standard-2-cpu'))
    self.assertEqual(
        'standard-2-cpu',
        command._presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/'
            'projects/user/machineTypes/standard-2-cpu/'))
    self.assertEqual(
        'standard-2-cpu',
        command._presenter.PresentElement(
            'projects/user/machineTypes/standard-2-cpu'))
    self.assertEqual(
        'standard-2-cpu',
        command._presenter.PresentElement(
            'projects/user/machineTypes/standard-2-cpu/'))
    self.assertEqual(
        'foo/bar/baz',
        command._presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/'
            'projects/user/shared-fate-zones/foo/bar/baz'))
    self.assertEqual(
        'foo/bar/baz',
        command._presenter.PresentElement(
            'projects/user/shared-fate-zones/foo/bar/baz'))
    self.assertEqual(
        'foo/bar/baz', command._presenter.PresentElement('foo/bar/baz'))

    self.assertEqual(
        'the-zone1/instances/the-instance1', command._presenter.PresentElement(
            'projects/user/zones/the-zone1/instances/the-instance1'))

    # Tests eliding feature
    test_str = ('I am the very model of a modern Major-General. I\'ve '
                'information vegetable, animal, and mineral. I know the kings '
                'of England and quote the fights historical; from Marathon to '
                'Waterloo in order categorical.')
    self.assertEqual(
        test_str,
        command._presenter.PresentElement(test_str))

    set_flags = {
        'project': 'user',
        'long_values_display_format': 'full'
        }
    command = self._CreateAndInitializeCommand(MockCommand,
                                               'auth',
                                               self.version,
                                               set_flags)

    self.assertEqual(test_str, command._presenter.PresentElement(test_str))

  def testDenormalizeResourceName(self):
    denormalize = command_base.GoogleComputeCommand.DenormalizeResourceName
    self.assertEqual('dual-cpu',
                     denormalize('projects/google/machineTypes/dual-cpu'))
    self.assertEqual('dual-cpu',
                     denormalize('/projects/google/machineTypes/dual-cpu'))
    self.assertEqual('dual-cpu',
                     denormalize('projects/google/machineTypes/dual-cpu/'))
    self.assertEqual('dual-cpu',
                     denormalize('/projects/google/machineTypes/dual-cpu/'))
    self.assertEqual('dual-cpu',
                     denormalize('//projects/google/machineTypes/dual-cpu//'))
    self.assertEqual('dual-cpu',
                     denormalize('dual-cpu'))
    self.assertEqual('dual-cpu',
                     denormalize('/dual-cpu'))
    self.assertEqual('dual-cpu',
                     denormalize('dual-cpu/'))
    self.assertEqual('dual-cpu',
                     denormalize('/dual-cpu/'))

  def testNormalizeResourceName(self):
    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

      def SetApi(self, api):
        pass

    set_flags = {
        'project': 'google'
    }
    command = self._CreateAndInitializeCommand(MockCommand,
                                               'mock_command',
                                               self.version,
                                               set_flags)

    prefix = 'https://www.googleapis.com/compute/%s' % self.version
    expected = '%s/projects/google/machineTypes/dual-cpu' % prefix

    self.assertEqual(
        expected,
        command.NormalizeResourceName('google', None, 'machineTypes',
                                      'dual-cpu'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName('google', None, 'machineTypes',
                                      '/dual-cpu'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName('google', None, 'machineTypes',
                                      'dual-cpu/'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName('google', None, 'machineTypes',
                                      '/dual-cpu/'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName(
            'google',
            None,
            'machineTypes',
            'projects/google/machineTypes/dual-cpu'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName(
            'google',
            None,
            'machineTypes',
            '/projects/google/machineTypes/dual-cpu'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName(
            'google',
            None,
            'machineTypes',
            'projects/google/machineTypes/dual-cpu/'))
    self.assertEqual(
        expected,
        command.NormalizeResourceName(
            'google',
            None,
            'machineTypes',
            '/projects/google/machineTypes/dual-cpu/'))

  def testNormalizeScopedResourceName(self):
    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

      def SetApi(self, api):
        pass

    set_flags = {
        'project': 'my-project'
    }
    command = self._CreateAndInitializeCommand(MockCommand,
                                               'mock_command',
                                               self.version,
                                               set_flags)

    prefix = 'https://www.googleapis.com/compute/%s' % self.version

    # Validate helper wrappers
    expected = '%s/projects/my-project/objects/foo-bar' % prefix
    self.assertEqual(
        expected,
        command.NormalizeTopLevelResourceName('my-project', 'objects',
                                              'foo-bar'))

    expected = '%s/projects/my-project/global/objects/foo-bar' % prefix
    self.assertEqual(
        expected,
        command.NormalizeGlobalResourceName('my-project', 'objects',
                                            'foo-bar'))

    expected = '%s/projects/my-project/zones/zone-a/objects/foo-bar' % prefix
    self.assertEqual(
        expected,
        command.NormalizePerZoneResourceName('my-project', 'zone-a', 'objects',
                                             'foo-bar'))

  def testFlattenToDict(self):
    class TestClass(command_base.GoogleComputeCommand):
      fields = (('name', 'id'),
                ('simple', 'path.to.object'),
                ('multiple', 'more.elements'),
                ('multiple', 'even_more.elements'),
                ('repeated', 'things'),
                ('long', 'l'),
                ('does not exist', 'dne'),
                ('partial match', 'path.to.nowhere'),
               )

      def SetApi(self, api):
        pass

    data = {'id': ('https://www.googleapis.com/compute/v1beta1/'
                   'projects/test/object/foo'),
            'path': {'to': {'object': 'bar'}},
            'more': [{'elements': 'a'}, {'elements': 'b'}],
            'even_more': [{'elements': 800}, {'elements': 800}],
            'things': [1, 2, 3],
            'l': 'n' * 80}
    expected_result = ['foo', 'bar', 'a,b', '800,800', '1,2,3',
                       'n' * 80, '', '']
    set_flags = {
        'project': 'test'
    }
    command = self._CreateAndInitializeCommand(TestClass,
                                               'foo',
                                               self.version,
                                               set_flags)

    flattened = command._FlattenObjectToList(data, command.fields)
    self.assertEquals(flattened, expected_result)

  def testFlattenToDictWithMultipleTargets(self):
    class TestClass(command_base.GoogleComputeCommand):
      fields = (('name', ('name', 'id')),
                ('simple', ('path.to.object', 'foo')),
                ('multiple', 'more.elements'),
                ('multiple', 'even_more.elements'),
                ('repeated', 'things'),
                ('long', ('l', 'longer')),
                ('does not exist', 'dne'),
                ('partial match', 'path.to.nowhere'),
               )

      def SetApi(self, api):
        pass

    data = {'name': ('https://www.googleapis.com/compute/v1beta1/'
                     'projects/test/object/foo'),
            'path': {'to': {'object': 'bar'}},
            'more': [{'elements': 'a'}, {'elements': 'b'}],
            'even_more': [{'elements': 800}, {'elements': 800}],
            'things': [1, 2, 3],
            'longer': 'n' * 80}
    expected_result = ['foo', 'bar', 'a,b', '800,800', '1,2,3',
                       'n' * 80, '', '']

    set_flags = {
        'project': 'test'
    }
    command = self._CreateAndInitializeCommand(TestClass,
                                               'foo',
                                               self.version,
                                               set_flags)

    flattened = command._FlattenObjectToList(data, command.fields)
    self.assertEquals(flattened, expected_result)

  def testPositionArgumentParsing(self):
    class MockCommand(command_base.GoogleComputeCommand):

      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)
        flags.DEFINE_string('mockflag',
                            'wrong_mock_flag',
                            'Mock Flag',
                            flag_values=flag_values)

      def Handle(self, arg1, arg2, arg3):
        pass

    flag_values = copy.deepcopy(FLAGS)
    command = MockCommand('mock_command', flag_values)

    expected_arg1 = 'foo'
    expected_arg2 = 'bar'
    expected_arg3 = 'baz'
    expected_flagvalue = 'wow'

    command_line = ['mock_command', expected_arg1, expected_arg2,
                    expected_arg3, '--mockflag=' + expected_flagvalue]

    # Verify the positional argument parser correctly identifies the parameters
    # and flags.
    result = command._ParseArgumentsAndFlags(flag_values, command_line)

    self.assertEqual(result[0], expected_arg1)
    self.assertEqual(result[1], expected_arg2)
    self.assertEqual(result[2], expected_arg3)
    self.assertEqual(flag_values.mockflag, expected_flagvalue)

  def testErroneousKeyWordArgumentParsing(self):

    class MockCommand(command_base.GoogleComputeCommand):

      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)
        flags.DEFINE_integer('mockflag',
                             10,
                             'Mock Flag',
                             flag_values=flag_values,
                             lower_bound=0)

      def Handle(self, arg1, arg2, arg3):
        pass

    flag_values = copy.deepcopy(FLAGS)
    command = MockCommand('mock_command', flag_values)

    # Ensures that a type mistmatch for a keyword argument causes a
    # CommandError to be raised.
    bad_values = [-100, -2, 0.2, .30, 100.1]
    for val in bad_values:
      command_line = ['mock_command', '--mockflag=%s' % val]
      self.assertRaises(gcutil_errors.CommandError,
                        command._ParseArgumentsAndFlags,
                        flag_values, command_line)

    # Ensures that passing a nonexistent keyword argument also causes
    # a CommandError to be raised.
    command_line = ['mock_command', '--nonexistent_flag=boo!']
    self.assertRaises(gcutil_errors.CommandError,
                      command._ParseArgumentsAndFlags,
                      flag_values, command_line)

  class MockSafetyCommand(command_base.GoogleComputeCommand):

    safety_prompt = 'Take scary action'

    def __init__(self, name, flag_values):
      super(CommandBaseTest.MockSafetyCommand, self).__init__(name, flag_values)

    def SetApi(self, api):
      pass

    def Handle(self):
      pass

  class MockSafetyCommandWithArgs(MockSafetyCommand):
    safety_prompt = 'Act on'

    def Handle(self, argument, arg2):
      pass

  class FakeExit(object):
    """A fake version of exit to capture exit status."""

    def __init__(self):
      self.__status__ = []

    def __call__(self, value):
      self.__status__.append(value)

    def GetStatuses(self):
      return self.__status__

  def testSafetyPromptYes(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.require_tty = False
    command_line = ['mock_command']

    command = CommandBaseTest.MockSafetyCommand('mock_command', flag_values)
    args = command._ParseArgumentsAndFlags(flag_values, command_line)
    command.SetFlags(flag_values)

    with gcutil_unittest.CaptureStandardIO('Y\n\r') as stdio:
      result = command._HandleSafetyPrompt(args)

      self.assertEqual(stdio.stdout.getvalue(),
                       'Take scary action? [y/n]\n>>> ')
      self.assertEqual(result, True)

  def testSafetyPromptWithArgsYes(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.require_tty = False
    command_line = ['mock_cmd', 'arg1', 'arg2']

    command = CommandBaseTest.MockSafetyCommandWithArgs('mock_cmd',
                                                        flag_values)
    args = command._ParseArgumentsAndFlags(flag_values, command_line)
    command.SetFlags(flag_values)

    with gcutil_unittest.CaptureStandardIO('Y\n\r') as stdio:
      result = command._HandleSafetyPrompt(args)

      self.assertEqual(stdio.stdout.getvalue(),
                       'Act on arg1, arg2? [y/n]\n>>> ')
      self.assertEqual(result, True)

  def testSafetyPromptMissingArgs(self):
    flag_values = copy.deepcopy(FLAGS)
    command_line = ['mock_cmd', 'arg1']

    command = CommandBaseTest.MockSafetyCommandWithArgs('mock_cmd',
                                                        flag_values)

    command_base.sys.exit = CommandBaseTest.FakeExit()
    sys.stderr = StringIO()

    gcutil_logging.SetupLogging()
    self.assertRaises(gcutil_errors.CommandError,
                      command._ParseArgumentsAndFlags,
                      flag_values, command_line)

  def testSafetyPromptExtraArgs(self):
    flag_values = copy.deepcopy(FLAGS)
    command_line = ['mock_cmd', 'arg1', 'arg2', 'arg3']

    command = CommandBaseTest.MockSafetyCommandWithArgs('mock_cmd',
                                                        flag_values)

    command_base.sys.exit = CommandBaseTest.FakeExit()
    sys.stderr = StringIO()

    gcutil_logging.SetupLogging()
    self.assertRaises(gcutil_errors.CommandError,
                      command._ParseArgumentsAndFlags,
                      flag_values, command_line)

  def testSafetyPromptNo(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.require_tty = False
    command_line = ['mock_command']

    command = CommandBaseTest.MockSafetyCommand('mock_command', flag_values)
    args = command._ParseArgumentsAndFlags(flag_values, command_line)
    command.SetFlags(flag_values)

    with gcutil_unittest.CaptureStandardIO('n\n\r') as stdio:
      result = command._HandleSafetyPrompt(args)

      self.assertEqual(stdio.stdout.getvalue(),
                       'Take scary action? [y/n]\n>>> ')
      self.assertEqual(result, False)

  def testSafetyPromptForce(self):
    flag_values = copy.deepcopy(FLAGS)
    command_line = ['mock_command', '--force']

    command = CommandBaseTest.MockSafetyCommand('mock_command', flag_values)
    args = command._ParseArgumentsAndFlags(flag_values, command_line)
    command.SetFlags(flag_values)

    with gcutil_unittest.CaptureStandardIO() as stdio:
      result = command._HandleSafetyPrompt(args)

      self.assertEqual(stdio.stdout.getvalue(), '')
      self.assertEqual(result, True)

  def testPromptForChoicesWithOneDeprecatedItem(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'p'

    command = command_base.GoogleComputeCommand('mock_command', flag_values)
    command.SetFlags(flag_values)

    with gcutil_unittest.CaptureStandardIO() as stdio:
      result = command._presenter.PromptForChoice(
          [{'name': 'item-1', 'deprecated': {'state': 'DEPRECATED'}}],
          'collection')

      self.assertEqual(
          stdio.stdout.getvalue(),
          'Selecting the only available collection: item-1\n')
      self.assertEqual(result, {'name': 'item-1', 'deprecated':
                                {'state': 'DEPRECATED'}})

  def testPromptForChoiceWithZone(self):
    """Test case to make sure the correct zone is used in prompt lists."""

    expected_zone = 'z'

    set_flags = {
        'project': 'p',
        'zone': expected_zone
        }

    command = self._CreateAndInitializeCommand(instance_cmds.ListInstances,
                                               'instancelist_command',
                                               self.version,
                                               set_flags)

    machinetypecall = mock_lists.GetSampleMachineTypeListCall(command,
                                                                self.mock)

    with gcutil_unittest.CaptureStandardIO('1\n\r') as unused_stdio:
      command._presenter.PromptForMachineType(self.api.machine_types,
                                              for_test_auto_select=True)

      requests = machinetypecall.GetAllRequests()

      self.assertEquals(1, len(requests))
      self.assertEquals(expected_zone, requests[0].parameters['zone'])

  def testPromptForChoiceWithNone(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'p'
    flag_values.require_tty = False

    command = command_base.GoogleComputeCommand('mock_command', flag_values)
    command.SetFlags(flag_values)

    with gcutil_unittest.CaptureStandardIO('3\n') as _:
      result = command._presenter.PromptForChoice(
          [{'name': 'item1', 'selfLink': 'http://item1'},
           {'name': 'item2', 'selfLink': 'http://item2'}],
          'collection',
          allow_none=True)

      self.assertEqual(None, result)

  class MockDetailCommand(command_base.GoogleComputeCommand):

    print_spec = command_base.ResourcePrintSpec(
        summary=['name', 'id', 'description', 'additional'],
        field_mappings=(
            ('name', 'id'),
            ('id', 'number'),
            ('description', 'description'),
            ('additional', 'moreStuff')),
        detail=(
            ('name', 'id'),
            ('id', 'number'),
            ('description', 'description'),
            ('additional', 'moreStuff')),
        sort_by='name')

    def __init__(self, name, flag_values):
      super(CommandBaseTest.MockDetailCommand, self).__init__(name, flag_values)

    def SetApi(self, api):
      pass

    def Handle(self):
      return {'description': 'Object C',
              'id': 'projects/user/objects/my-object-c',
              'kind': 'cloud#object',
              'number': 123,
              'moreStuff': 'foo'}

  def testDetailOutput(self):
    set_flags = {
        'project': 'user',
        }

    command = self._CreateAndInitializeCommand(
        CommandBaseTest.MockDetailCommand, 'mock_command', self.version,
        set_flags)

    expected_output = textwrap.dedent("""\
        +-------------+-------------+
        | name        | my-object-c |
        | id          | 123         |
        | description | Object C    |
        | additional  | foo         |
        +-------------+-------------+
        """)

    with gcutil_unittest.CaptureStandardIO() as stdio:
      result = command.Handle()
      command.PrintResult(result)
      self.assertEqual(stdio.stdout.getvalue(), expected_output)

  def testDetailOutputYaml(self):
    set_flags = {
        'project': 'user',
        'format': 'yaml',
        }

    command = self._CreateAndInitializeCommand(
        CommandBaseTest.MockDetailCommand, 'mock_command', self.version,
        set_flags)

    expected_output = textwrap.dedent("""\
        ---
        description: Object C
        id: projects/user/objects/my-object-c
        kind: cloud#object
        moreStuff: foo
        number: 123
        """)

    with gcutil_unittest.CaptureStandardIO() as stdio:
      result = command.Handle()
      command.PrintResult(result)
      self.assertEqual(stdio.stdout.getvalue(), expected_output)

  def testEmptyListAndAllColumns(self):
    set_flags = {
        'project': 'user',
        'columns': ['all'],
        }

    command = self._CreateAndInitializeCommand(network_cmds.ListNetworks,
                                               'empty_list_networks',
                                               self.version,
                                               set_flags)

    mock_lists.GetSampleNetworkListCall(command, self.mock, 0)

    expected_output = textwrap.dedent("""\
        +------+-------------+-----------+---------+
        | name | description | addresses | gateway |
        +------+-------------+-----------+---------+
        """)

    with gcutil_unittest.CaptureStandardIO() as stdio:
      result = command.Handle()
      command.PrintResult(result)

      self.assertEqual(stdio.stdout.getvalue(), expected_output)

  sample_names = ['test-network-1',
                  'test-network-2',
                  'test-network-3',
                  'test-network-0']

  sample_descriptions = ['one', 'two', 'three', 'zero']

  def testSortingNone(self):
    set_flags = {
        'project': 'user',
        'sort_by': 'none',
        'columns': ['name', 'description', 'addresses', 'gateway'],
        }

    command = self._CreateAndInitializeCommand(network_cmds.ListNetworks,
                                               'list_networks',
                                               self.version,
                                               set_flags)

    mock_lists.GetSampleNetworkListCall(
        command,
        self.mock,
        4,
        name=self.sample_names,
        description=self.sample_descriptions)

    expected_output = textwrap.dedent("""\
        +----------------+-------------+-----------+---------+
        | name           | description | addresses | gateway |
        +----------------+-------------+-----------+---------+
        | test-network-1 | one         |           |         |
        +----------------+-------------+-----------+---------+
        | test-network-2 | two         |           |         |
        +----------------+-------------+-----------+---------+
        | test-network-3 | three       |           |         |
        +----------------+-------------+-----------+---------+
        | test-network-0 | zero        |           |         |
        +----------------+-------------+-----------+---------+
        """)

    with gcutil_unittest.CaptureStandardIO() as stdio:
      result = command.Handle()
      command.PrintResult(result)

      self.assertEqual(stdio.stdout.getvalue(), expected_output)

  def testSortingDefault(self):
    set_flags = {
        'project': 'user',
        }

    command = self._CreateAndInitializeCommand(network_cmds.ListNetworks,
                                               'list_networks',
                                               self.version,
                                               set_flags)

    mock_lists.GetSampleNetworkListCall(
        command,
        self.mock,
        4,
        name=self.sample_names,
        description=self.sample_descriptions)

    expected_output = textwrap.dedent("""\
        +----------------+-----------+---------+
        | name           | addresses | gateway |
        +----------------+-----------+---------+
        | test-network-0 |           |         |
        +----------------+-----------+---------+
        | test-network-1 |           |         |
        +----------------+-----------+---------+
        | test-network-2 |           |         |
        +----------------+-----------+---------+
        | test-network-3 |           |         |
        +----------------+-----------+---------+
        """)

    with gcutil_unittest.CaptureStandardIO() as stdio:
      result = command.Handle()
      command.PrintResult(result)

      self.assertEqual(stdio.stdout.getvalue(), expected_output)

  def testSelectColumns(self):
    set_flags = {
        'project': 'user',
        'columns': ['description', 'description', 'name'],
        }

    command = self._CreateAndInitializeCommand(network_cmds.ListNetworks,
                                               'list_networks',
                                               self.version,
                                               set_flags)

    mock_lists.GetSampleNetworkListCall(
        command,
        self.mock,
        4,
        name=self.sample_names,
        description=self.sample_descriptions)

    expected_output = textwrap.dedent("""\
        +-------------+-------------+----------------+
        | description | description | name           |
        +-------------+-------------+----------------+
        | zero        | zero        | test-network-0 |
        +-------------+-------------+----------------+
        | one         | one         | test-network-1 |
        +-------------+-------------+----------------+
        | two         | two         | test-network-2 |
        +-------------+-------------+----------------+
        | three       | three       | test-network-3 |
        +-------------+-------------+----------------+
        """)

    with gcutil_unittest.CaptureStandardIO() as stdio:
      result = command.Handle()
      command.PrintResult(result)

      self.assertEqual(stdio.stdout.getvalue(), expected_output)

  def testBadColumnCausesError(self):
    set_flags = {
        'project': 'user',
        'columns': 'description,description,nonexistent-field,name',
        }

    command = self._CreateAndInitializeCommand(network_cmds.ListNetworks,
                                               'list_networks',
                                               self.version,
                                               set_flags)

    mock_lists.GetSampleNetworkListCall(
        command,
        self.mock,
        4,
        name=self.sample_names,
        description=self.sample_descriptions)

    result = command.Handle()
    self.assertRaises(app.UsageError, command.PrintResult, result)

  def testSortingSpecifiedInAscendingOrder(self):
    set_flags = {
        'project': 'user',
        'sort_by': 'description',
        'columns': ['name', 'description', 'addresses', 'gateway'],
        }

    command = self._CreateAndInitializeCommand(network_cmds.ListNetworks,
                                               'list_networks',
                                               self.version,
                                               set_flags)

    mock_lists.GetSampleNetworkListCall(
        command,
        self.mock,
        4,
        name=self.sample_names,
        description=self.sample_descriptions)

    expected_output = textwrap.dedent("""\
        +----------------+-------------+-----------+---------+
        | name           | description | addresses | gateway |
        +----------------+-------------+-----------+---------+
        | test-network-1 | one         |           |         |
        +----------------+-------------+-----------+---------+
        | test-network-3 | three       |           |         |
        +----------------+-------------+-----------+---------+
        | test-network-2 | two         |           |         |
        +----------------+-------------+-----------+---------+
        | test-network-0 | zero        |           |         |
        +----------------+-------------+-----------+---------+
        """)

    with gcutil_unittest.CaptureStandardIO() as stdio:
      result = command.Handle()
      command.PrintResult(result)

      self.assertEqual(stdio.stdout.getvalue(), expected_output)

  def testSortingSpecifiedInDescendingOrder(self):
    set_flags = {
        'project': 'user',
        'sort_by': '-description',
        'columns': ['name', 'description', 'addresses', 'gateway'],
        }

    command = self._CreateAndInitializeCommand(network_cmds.ListNetworks,
                                               'list_networks',
                                               self.version,
                                               set_flags)

    mock_lists.GetSampleNetworkListCall(
        'compute.networks.list',
        self.mock,
        4,
        name=self.sample_names,
        description=self.sample_descriptions)

    expected_output = textwrap.dedent("""\
        +----------------+-------------+-----------+---------+
        | name           | description | addresses | gateway |
        +----------------+-------------+-----------+---------+
        | test-network-0 | zero        |           |         |
        +----------------+-------------+-----------+---------+
        | test-network-2 | two         |           |         |
        +----------------+-------------+-----------+---------+
        | test-network-3 | three       |           |         |
        +----------------+-------------+-----------+---------+
        | test-network-1 | one         |           |         |
        +----------------+-------------+-----------+---------+
        """)

    with gcutil_unittest.CaptureStandardIO() as stdio:
      result = command.Handle()
      command.PrintResult(result)

      self.assertEqual(stdio.stdout.getvalue(), expected_output)

  def testGracefulHandlingOfInvalidSortField(self):
    set_flags = {
        'project': 'user',
        'sort_by': 'invalid-sort-field',
        'columns': ['name', 'description', 'addresses', 'gateway'],
        }

    command = self._CreateAndInitializeCommand(network_cmds.ListNetworks,
                                               'list_networks',
                                               self.version,
                                               set_flags)

    mock_lists.GetSampleNetworkListCall(
        command,
        self.mock,
        4,
        name=self.sample_names,
        description=self.sample_descriptions)

    expected_output = textwrap.dedent("""\
        +----------------+-------------+-----------+---------+
        | name           | description | addresses | gateway |
        +----------------+-------------+-----------+---------+
        | test-network-1 | one         |           |         |
        +----------------+-------------+-----------+---------+
        | test-network-2 | two         |           |         |
        +----------------+-------------+-----------+---------+
        | test-network-3 | three       |           |         |
        +----------------+-------------+-----------+---------+
        | test-network-0 | zero        |           |         |
        +----------------+-------------+-----------+---------+
        """)

    with gcutil_unittest.CaptureStandardIO() as stdio:
      result = command.Handle()
      command.PrintResult(result)

      self.assertEqual(stdio.stdout.getvalue(), expected_output)

  def testTracing(self):
    class MockComputeApi(object):
      def __init__(self, trace_calls):
        self._trace_calls = trace_calls

      def Disks(self):
        class MockDisksApi(object):
          def __init__(self, trace_calls):
            self._trace_calls = trace_calls

          def Insert(self, trace=None):
            if trace:
              self._trace_calls.append(trace)

        return MockDisksApi(self._trace_calls)

    # Expect no tracing if flag is not set.
    trace_calls = []
    compute = gce_api.WrapApiIfNeeded(
        MockComputeApi(trace_calls))
    compute.Disks().Insert()
    self.assertEqual(0, len(trace_calls))

    # Expect tracing if trace_token flag is set.
    trace_calls = []
    FLAGS.trace_token = 'THE_TOKEN'
    compute = gce_api.WrapApiIfNeeded(
        MockComputeApi(trace_calls))
    compute.Disks().Insert()
    self.assertEqual(1, len(trace_calls))
    self.assertEqual('token:THE_TOKEN', trace_calls[0])
    FLAGS.trace_token = ''


  def testGetZone(self):
    set_flags = {
        'project': 'p'
    }

    command = self._CreateAndInitializeCommand(instance_cmds.AddInstance,
                                               'instance_command',
                                               self.version,
                                               set_flags)

    zonecall = self.mock.Respond(
        'compute.zones.get',
        {
            'kind': 'compute#zone',
            'name': 'us-west-a'
        })

    self.assertEqual('us-west-a', command._GetZone('us-west-a'))
    request = zonecall.GetRequest()

    self.assertEquals('GET', request.method)
    self.assertEquals(None, request.body)

    parameters = request.parameters
    self.assertTrue('project' in parameters)
    self.assertEquals('p', parameters['project'])
    self.assertTrue('zone' in parameters)
    self.assertEquals('us-west-a', parameters['zone'])

    unused_zone_listcall = mock_lists.GetSampleZoneListCall(command,
                                                            self.mock,
                                                            2)

    with gcutil_unittest.CaptureStandardIO('1\n\r') as unused_stdio:
      self.assertEqual('test-zone-0', command._GetZone(None))

  def testGetNextMaintenanceStart(self):
    zone = {
        'kind': 'compute#zone',
        'name': 'zone',
        'maintenanceWindows': [
            {
                'name': 'january',
                'beginTime': '2013-01-01T00:00:00.000',
                'endTime': '2013-01-31T00:00:00.000'
                },
            {
                'name': 'march',
                'beginTime': '2013-03-01T00:00:00.000',
                'endTime': '2013-03-31T00:00:00.000'
                },
            ]
        }

    gnms = command_base.GoogleComputeCommand.GetNextMaintenanceStart
    start = gnms(zone, datetime.datetime(2012, 12, 1))
    self.assertEqual(start, datetime.datetime(2013, 1, 1))
    start = gnms(zone, datetime.datetime(2013, 2, 14))
    self.assertEqual(start, datetime.datetime(2013, 3, 1))
    start = gnms(zone, datetime.datetime(2013, 3, 15))
    self.assertEqual(start, datetime.datetime(2013, 3, 1))

  def testGetZoneForResource(self):
    set_flags = {
        'project': 'google'
    }

    command = self._CreateAndInitializeCommand(instance_cmds.DeleteInstance,
                                               'instance_command',
                                               self.version,
                                               set_flags)

    # Project-qualified name.
    self.assertEqual(
        command.GetZoneForResource(None, 'projects/foo/zones/bar'), 'bar')

    # Zone name explicitly set.
    set_flags = {
        'project': 'google',
        'zone': 'explicitly-set-zone'
    }

    command = self._CreateAndInitializeCommand(instance_cmds.DeleteInstance,
                                               'instance_command',
                                               self.version,
                                               set_flags)

    self.assertEqual(
        command.GetZoneForResource(None, 'some-resource'),
        'explicitly-set-zone')

  def testGetUsageWithPositionalArgs(self):

    class MockCommand(command_base.GoogleComputeCommand):
      positional_args = '<arg-1> ... <arg-n>'

    flag_values = copy.deepcopy(FLAGS)
    command = MockCommand('mock_command', flag_values)
    self.assertTrue(command._GetUsage().endswith(
        ' [--global_flags] mock_command [--command_flags] <arg-1> ... <arg-n>'))

  def testGetUsageWithNoPositionalArgs(self):

    class MockCommand(command_base.GoogleComputeCommand):
      pass

    flag_values = copy.deepcopy(FLAGS)
    command = MockCommand('mock_command', flag_values)
    self.assertTrue(command._GetUsage().endswith(
        ' [--global_flags] mock_command [--command_flags]'))


  def testGoogleComputeListCommandPerZone(self):
    # Test single zone.
    set_flags = {
        'project': 'foo',
        'zone': 'bar'
    }

    command = self._CreateAndInitializeCommand(instance_cmds.ListInstances,
                                               'instance_command',
                                               self.version,
                                               set_flags)

    listcall = mock_lists.GetSampleInstanceListCall(command,
                                                    self.mock,
                                                    2)

    unused_result = command.Handle()
    request = listcall.GetRequest()

    self.assertEquals('GET', request.method)
    self.assertEquals(None, request.body)

    parameters = request.parameters
    self.assertTrue('project' in parameters)
    self.assertEquals('foo', parameters['project'])
    self.assertTrue('zone' in parameters)
    self.assertEquals('bar', parameters['zone'])

    # Test all zones.
    set_flags = {
        'project': 'foo'
    }

    command = self._CreateAndInitializeCommand(instance_cmds.ListInstances,
                                               'instance_command',
                                               self.version,
                                               set_flags)

    listcall = self.mock.Respond(
        'compute.instances.aggregatedList', {
            'items': {
                'zones/somewhere': {
                    'instances': [{
                        'name': 'test-instance',
                        'kind': 'compute#instance'
                    }]
                }
            },
            'kind': 'compute#aggregatedlist'
        })

    unused_result = command.Handle()

    request = listcall.GetRequest()
    self.assertEquals('GET', request.method)
    self.assertEquals(None, request.body)
    parameters = request.parameters
    self.assertTrue('project' in parameters)
    self.assertEquals('foo', parameters['project'])


class OldCommandBaseTest(unittest.TestCase):

  class ListMockCommandBase(command_base.GoogleComputeListCommand):
    """A list mock command that specifies no default sort field."""

    print_spec = command_base.ResourcePrintSpec(
        summary=['name', 'id', 'description'],
        field_mappings=(
            ('name', 'id'),
            ('id', 'number'),
            ('description', 'description')),
        detail=(
            ('name', 'id'),
            ('id', 'number'),
            ('description', 'description')),
        sort_by=None)

    def __init__(self, name, flag_values):
      super(OldCommandBaseTest.ListMockCommandBase, self).__init__(
          name, flag_values)

    def SetApi(self, api):
      pass

    def ListFunc(self):

      # pylint: disable=unused-argument,redefined-builtin,g-bad-name
      def Func(project=None, maxResults=None, filter=None, pageToken=None):
        return old_mock_api.MockRequest(
            {'items': [{'description': 'Object C',
                        'id': 'projects/user/objects/my-object-c',
                        'kind': 'cloud#object',
                        'number': 123},
                       {'description': 'Object A',
                        'id': 'projects/user/objects/my-object-a',
                        'kind': 'cloud#object',
                        'number': 789},
                       {'description': 'Object B',
                        'id': 'projects/user/objects/my-object-b',
                        'kind': 'cloud#object',
                        'number': 456},
                       {'description': 'Object D',
                        'id': 'projects/user/objects/my-object-d',
                        'kind': 'cloud#object',
                        'number': 999}],
             'kind': 'cloud#objectList'})

      return Func

  class ListMockCommand(ListMockCommandBase):
    """A list mock command that specifies a default sort field."""
    print_spec = command_base.ResourcePrintSpec(
        summary=['name', 'id', 'description'],
        field_mappings=(
            ('name', 'id'),
            ('id', 'number'),
            ('description', 'description')),
        detail=(
            ('name', 'id'),
            ('id', 'number'),
            ('description', 'description')),
        sort_by='name')

    def __init__(self, name, flag_values):
      super(OldCommandBaseTest.ListMockCommand, self).__init__(name,
                                                               flag_values)

  class CaptureOutput(object):

    def __init__(self):
      self._capture_text = ''

    # Purposefully name this 'write' to mock an output stream
    # pylint: disable=g-bad-name
    def write(self, text):
      self._capture_text += text

    # Purposefully name this 'flush' to mock an output stream
    # pylint: disable=g-bad-name
    def flush(self):
      pass

    def GetCapturedText(self):
      return self._capture_text

  class MockInput(object):

    def __init__(self, input_string):
      self._input_string = input_string

    # Purposefully name this 'readline' to mock an input stream
    # pylint: disable=g-bad-name
    def readline(self):
      return self._input_string

  def testDenormalizeProjectName(self):
    denormalize = command_base.GoogleComputeCommand.DenormalizeProjectName
    flag_values = flags.FlagValues()
    flags.DEFINE_string('project',
                        None,
                        'Project Name',
                        flag_values=flag_values)
    flags.DEFINE_string('project_id',
                        None,
                        'Obsolete Project Name',
                        flag_values=flag_values)

    self.assertRaises(gcutil_errors.CommandError,
                      denormalize,
                      flag_values)

    flag_values.project = 'projects/google'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project = '/google'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project = 'google/'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project = '/google/'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project = '/projects/google'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project = 'projects/google/'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project = '/projects/google/'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'google')

    flag_values.project_id = 'my-obsolete-project-1'
    flag_values.project = 'my-new-project-1'
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'my-new-project-1')
    self.assertEqual(flag_values.project_id, None)

    flag_values.project_id = 'my-new-project-2'
    flag_values.project = None
    denormalize(flag_values)
    self.assertEqual(flag_values.project, 'my-new-project-2')
    self.assertEqual(flag_values.project_id, None)

    flag_values.project_id = 'MyUppercaseProject-1'
    flag_values.project = None
    self.assertRaises(gcutil_errors.CommandError, denormalize, flag_values)

    flag_values.project = 'MyUppercaseProject-2'
    flag_values.project_id = None
    self.assertRaises(gcutil_errors.CommandError, denormalize, flag_values)

  def testWaitForOperation(self):
    complete_name = 'operation-complete'
    running_name = 'operation-running'
    pending_name = 'operation-pending'
    stuck_name = 'operation-stuck'

    base_operation = {'kind': 'cloud#operation',
                      'targetLink': ('https://www.googleapis.com/compute/'
                                     'v1beta100/projects/p/instances/i1'),
                      'operationType': 'insert',
                      'selfLink': ('https://www.googleapis.com/compute/'
                                   'v1beta100/projects/p/operations/op')}

    completed_operation = dict(base_operation)
    completed_operation.update({'name': complete_name,
                                'status': 'DONE'})
    running_operation = dict(base_operation)
    running_operation.update({'name': running_name,
                              'status': 'RUNNING'})
    pending_operation = dict(base_operation)
    pending_operation.update({'name': pending_name,
                              'status': 'PENDING'})
    stuck_operation = dict(base_operation)
    stuck_operation.update({'name': stuck_name,
                            'status': 'PENDING'})

    next_operation = {complete_name: completed_operation,
                      running_name: completed_operation,
                      pending_name: running_operation,
                      stuck_name: stuck_operation}

    class MockHttpResponse(object):
      def __init__(self, status, reason):
        self.status = status
        self.reason = reason

    class MockHttp(object):

      # pylint: disable=unused-argument
      def request(self, url, method='GET', body=None, headers=None):
        response = MockHttpResponse(200, 'OK')
        data = '{ "kind": "compute#instance", "name": "i1" }'
        return response, data

    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

      def SetApi(self, api):
        pass

      def Handle(self):
        pass

      def CreateHttp(self):
        return MockHttp()

    class LocalMockOperationsApi(object):
      def __init__(self):
        self._get_call_count = 0

      def GetCallCount(self):
        return self._get_call_count

      def get(self, project='unused project', operation='operation'):
        unused_project = project
        self._get_call_count += 1
        return old_mock_api.MockRequest(next_operation[operation])

    flag_values = copy.deepcopy(FLAGS)
    flag_values.sleep_between_polls = 1
    flag_values.max_wait_time = 30
    flag_values.service_version = 'v1'
    flag_values.synchronous_mode = False
    flag_values.project = 'test'

    # Ensure a synchronous result returns immediately.
    timer = mock_timer.MockTimer()
    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)
    command.api = old_mock_api.CreateMockApi()
    command.api.global_operations = LocalMockOperationsApi()
    diskResult = {'kind': 'cloud#disk'}
    result = command.WaitForOperation(
        flag_values.max_wait_time, flag_values.sleep_between_polls,
        timer, diskResult)
    self.assertEqual(0, command.api.global_operations.GetCallCount())

    # Ensure an asynchronous result loops until complete.
    timer = mock_timer.MockTimer()
    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)
    command.api = old_mock_api.CreateMockApi()
    command.api.global_operations = LocalMockOperationsApi()
    result = command.WaitForOperation(
        flag_values.max_wait_time, flag_values.sleep_between_polls,
        timer, pending_operation)
    self.assertEqual(2, command.api.global_operations.GetCallCount())

    # Ensure an asynchronous result eventually times out
    timer = mock_timer.MockTimer()
    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)
    command.api = old_mock_api.CreateMockApi()
    command.api.global_operations = LocalMockOperationsApi()
    result = command.WaitForOperation(
        flag_values.max_wait_time, flag_values.sleep_between_polls,
        timer, stuck_operation)
    self.assertEqual(30, command.api.global_operations.GetCallCount())
    self.assertEqual(result['status'], 'PENDING')


  def testGoogleComputeListCommandZoneAndGlobal(self):
    flag_values = copy.deepcopy(FLAGS)
    expected_project = 'foo'
    flag_values.project = expected_project
    flag_values.service_version = 'v1'

    object_a = {'description': 'Object A',
                'id': 'projects/user/zones/a/objects/my-object-a',
                'kind': 'cloud#object'}
    object_b = {'description': 'Object B',
                'id': 'projects/user/zones/b/objects/my-object-b',
                'kind': 'cloud#object'}
    object_c = {'description': 'Object C',
                'id': 'projects/user/objects/my-object-c',
                'kind': 'cloud#object'}
    list_global = {'items': [object_c],
                   'kind': 'cloud#objectList'}
    list_a = {'items': [object_a],
              'kind': 'cloud#objectList'}
    list_b = {'items': [object_b],
              'kind': 'cloud#objectList'}
    list_all = {'items': [object_a, object_b, object_c],
                'kind': 'cloud#objectList'}

    class LocalMockZonesApi(object):

      # pylint: disable=unused-argument,redefined-builtin
      def list(self, project='unused project', maxResults='unused',
               filter='unused'):
        return old_mock_api.MockRequest(
            {'items': [{'name': 'a'}, {'name': 'b'}]})

    class GlobalAndZoneListMockCommand(OldCommandBaseTest.ListMockCommandBase):
      """A list mock command that represents a zone-scoped collection."""

      def IsZoneLevelCollection(self):
        return True

      def IsGlobalLevelCollection(self):
        return True

      def __init__(self, name, flag_values):
        super(OldCommandBaseTest.ListMockCommandBase, self).__init__(
            name, flag_values)
        flags.DEFINE_string('zone',
                            None,
                            'The zone to list.',
                            flag_values=flag_values)

      def ListZoneFunc(self):
        # pylint: disable=unused-argument
        # pylint: disable=redefined-builtin
        def Func(project=None, maxResults=None, filter=None, pageToken=None,
                 zone=None):
          if zone == 'a':
            return old_mock_api.MockRequest(list_a)
          else:
            return old_mock_api.MockRequest(list_b)
        return Func

      def ListFunc(self):

        # pylint: disable=unused-argument,redefined-builtin
        def Func(project=None, maxResults=None, filter=None, pageToken=None):
          return old_mock_api.MockRequest(list_global)
        return Func

    command = GlobalAndZoneListMockCommand('mock_command', flag_values)
    command.api = old_mock_api.CreateMockApi()
    command.api.zones = LocalMockZonesApi()

    # Test single zone
    flag_values['zone'].value = 'a'
    flag_values['zone'].present = 1
    command.SetFlags(flag_values)
    self.assertEqual(list_a, command.Handle())

    # Test 'global' zone
    flag_values.zone = 'global'
    command.SetFlags(flag_values)
    self.assertEqual(list_global, command.Handle())

    # Test all
    flag_values['zone'].value = None
    flag_values['zone'].present = 0
    command.SetFlags(flag_values)
    self.assertEqual(list_all, command.Handle())

  def testOperationPrintSpecVersions(self):
    class MockCommand(OldCommandBaseTest.ListMockCommand):
      def __init__(self, name, flag_values):
        super(MockCommand, self).__init__(name, flag_values)

    flag_values = copy.deepcopy(FLAGS)

    command = MockCommand('mock_command', flag_values)
    command.supported_versions = ['v1']

    command.SetFlags(flag_values)
    command.api = old_mock_api.CreateMockApi()

  def testGoogleComputeListCommandZoneRegionGlobal(self):
    flag_values = copy.deepcopy(FLAGS)
    expected_project = 'foo'
    flag_values.project = expected_project
    flag_values.service_version = 'v1'

    def CreateObjects(scope):
      return (
          {'description': 'Object A - %s' % scope,
           'id': 'projects/user/%s/object-a' % scope,
           'kind': 'cloud#object'},
          {'description': 'Object B - %s' % scope,
           'id': 'projects/user/%s/object-b' % scope,
           'kind': 'cloud#object'}
          )

    def CreateList(*elements):
      return {'items': elements, 'kind': 'cloud#objectList'}

    # Global objects
    global_object_a, global_object_b = CreateObjects('global')
    global_list = CreateList(global_object_a, global_object_b)
    # Zone M
    zone_m_object_a, zone_m_object_b = CreateObjects('zones/zone-m')
    zone_m_list = CreateList(zone_m_object_a, zone_m_object_b)
    # Zone N
    zone_n_object_a, zone_n_object_b = CreateObjects('zones/zone-n')
    zone_n_list = CreateList(zone_n_object_a, zone_n_object_b)
    # Region R
    region_r_object_a, region_r_object_b = CreateObjects('regions/region-r')
    region_r_list = CreateList(region_r_object_a, region_r_object_b)
    # Region S
    region_s_object_a, region_s_object_b = CreateObjects('regions/region-s')
    region_s_list = CreateList(region_s_object_a, region_s_object_b)

    class LocalMockZonesApi(object):

      # pylint: disable=unused-argument,redefined-builtin
      def list(self, project='unused project', maxResults='unused',
               filter='unused'):
        return old_mock_api.MockRequest(
            {'items': [{'name': 'zone-m'}, {'name': 'zone-n'}]})

    class LocalMockRegionsApi(object):

      # pylint: disable=unused-argument,redefined-builtin
      def list(self, project='unused project', maxResults='unused',
               filter='unused'):
        return old_mock_api.MockRequest(
            {'items': [{'name': 'region-r'}, {'name': 'region-s'}]})

    class ListMockCommand(OldCommandBaseTest.ListMockCommandBase):
      """A list mock command that represents a multi-scoped collection."""

      def IsZoneLevelCollection(self):
        return True

      def IsGlobalLevelCollection(self):
        return True

      def IsRegionLevelCollection(self):
        return True

      def __init__(self, name, flag_values):
        super(OldCommandBaseTest.ListMockCommandBase, self).__init__(
            name, flag_values)

        flags.DEFINE_bool(
            'global',
            None,
            'Operations in global scope.',
            flag_values=flag_values)
        flags.DEFINE_string(
            'region',
            None,
            'The name of the region scope for region operations.',
            flag_values=flag_values)
        flags.DEFINE_string(
            'zone',
            None,
            'The name of the zone scope for zone operations.',
            flag_values=flag_values)

      def ListZoneFunc(self):
        # pylint: disable=unused-argument,redefined-builtin
        def Func(project=None, maxResults=None, filter=None, pageToken=None,
                 zone=None):
          assert zone in ('zone-m', 'zone-n')
          return old_mock_api.MockRequest(
              zone_m_list if zone == 'zone-m' else zone_n_list)
        return Func

      def ListRegionFunc(self):
        # pylint: disable=unused-argument,redefined-builtin
        def Func(project=None, maxResults=None, filter=None, pageToken=None,
                 region=None):
          assert region in ('region-r', 'region-s')
          return old_mock_api.MockRequest(
              region_r_list if region == 'region-r' else region_s_list)
        return Func

      def ListFunc(self):
        # pylint: disable=unused-argument,redefined-builtin
        def Func(project=None, maxResults=None, filter=None, pageToken=None):
          return old_mock_api.MockRequest(global_list)
        return Func

    command = ListMockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)
    command.api = old_mock_api.CreateMockApi()
    command.api.zones = LocalMockZonesApi()
    command.api.regions = LocalMockRegionsApi()

    def SetFlag(name, value):
      flag_values[name].value = value
      flag_values[name].present = 1

    def ClearFlag(name):
      flag_values[name].value = flag_values[name].default
      flag_values[name].present = 0

    command.api.version = version.v1
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [zone_m_object_a, zone_m_object_b,
                   zone_n_object_a, zone_n_object_b,
                   region_r_object_a, region_r_object_b,
                   region_s_object_a, region_s_object_b,
                   global_object_a, global_object_b]},
        command.Handle())

    # Ask for a specific zone. Should only list that zone.
    SetFlag('zone', 'zone-n')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [zone_n_object_a, zone_n_object_b]},
        command.Handle())

    # Ask for a specific region. Should only list that region.
    ClearFlag('zone')
    SetFlag('region', 'region-s')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [region_s_object_a, region_s_object_b]},
        command.Handle())

    # Ask for global only. Should only list global objects.
    ClearFlag('region')
    SetFlag('global', True)
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [global_object_a, global_object_b]},
        command.Handle())

    # Ask for zone and region. Should only list those.
    SetFlag('zone', 'zone-m')
    SetFlag('region', 'region-r')
    ClearFlag('global')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [zone_m_object_a, zone_m_object_b,
                   region_r_object_a, region_r_object_b]},
        command.Handle())

    # Ask for zone and global.
    SetFlag('zone', 'zone-n')
    SetFlag('global', True)
    ClearFlag('region')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [zone_n_object_a, zone_n_object_b,
                   global_object_a, global_object_b]},
        command.Handle())

    # Ask for region and global.
    ClearFlag('zone')
    SetFlag('region', 'region-s')
    SetFlag('global', True)
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [region_s_object_a, region_s_object_b,
                   global_object_a, global_object_b]},
        command.Handle())

    # Specify global, zone and region. Should only return data from specified
    # collections (not all zones, regions, only specified ones).
    SetFlag('zone', 'zone-m')
    SetFlag('region', 'region-r')
    SetFlag('global', True)
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [zone_m_object_a, zone_m_object_b,
                   region_r_object_a, region_r_object_b,
                   global_object_a, global_object_b]},
        command.Handle())

    # Deprecated behavior. Specify global zone.
    SetFlag('zone', 'global')
    ClearFlag('region')
    ClearFlag('global')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [global_object_a, global_object_b]},
        command.Handle())

    # Deprecated behavior. Specify global zone and --global.
    # Get data only once.
    SetFlag('zone', 'global')
    SetFlag('global', True)
    ClearFlag('region')
    self.assertEqual(
        {'kind': 'cloud#objectList',
         'items': [global_object_a, global_object_b]},
        command.Handle())

  def _DoTestGetScopeFromSelfLink(self, api_version):
    class MockCommand(command_base.GoogleComputeCommand):
      pass

    base = 'https://www.googleapis.com/compute/'

    flag_values = copy.deepcopy(FLAGS)
    flag_values.api_host = 'https://www.googleapis.com/'
    flag_values.service_version = api_version

    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)

    tests = (
        (base + 'v1/projects/my-project/global/networks/net',
         ('global', '')),

        (base + 'v1/projects/my-project/zones/zone1/instances/inst',
         ('zones', 'zone1')),

        (base + 'v1/projects/my-project/zones/zone2',
         ('zones', 'zone2')),

        # No suffix
        ('https://www.googleapis.com/',
         (None, None)),

        # just base URL
        (base,
         (None, None)),

        # missing projects
        (base + 'v1/global/networks/net',
         (None, None)),

        # missing project
        (base + 'v1/projects/global/networks/network',
         (None, None)),

        (base + 'v1/projects/my-project/regions/region1/ips/ip',
         ('regions', 'region1')),

        # bad regions
        (base + 'v1/projects/my-project/regins/region1/ips/ip',
         (None, None)),
    )

    for url, result in tests:
      scope = command._GetScopeFromSelfLink(url)
      error = ('Extracting scope from selfLink \'%s\' failed\n'
               '%s != %s') % (url, result, scope)
      self.assertEqual(result, scope, error)

  def testGetScopeFromSelfLink(self):
    for supported_version in command_base.SUPPORTED_VERSIONS:
      self._DoTestGetScopeFromSelfLink(supported_version)

  def testErrorInResultList(self):
    class MockCommand(command_base.GoogleComputeCommand):
      pass

    flag_values = copy.deepcopy(FLAGS)
    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)

    self.assertFalse(command._ErrorsInResultList(None))
    self.assertFalse(command._ErrorsInResultList([]))

    operation = {
        'kind': 'compute#operation',
        'id': '9811220201106278825',
        'name': 'my-operation',
        'operationType': 'insert',
        'progress': 100,
        'selfLink': ('https://www.googleapis.com/compute/v1/projects/'
                     'project/zones/my-zone/operations/my-operation'),
        'status': 'DONE'
        }

    self.assertTrue(command.IsResultAnOperation(operation))
    self.assertFalse(command._ErrorsInResultList([operation]))
    self.assertFalse(command._ErrorsInResultList([operation] * 10))

    error_operation = {
        'kind': 'compute#operation',
        'id': '9811220201106278825',
        'name': 'my-operation',
        'operationType': 'insert',
        'progress': 100,
        'selfLink': ('https://www.googleapis.com/compute/v1/projects/'
                     'my-project/zones/my-zone/operations/my-operation'),
        'status': 'DONE',
        'error': {
            'errors': [{
                'code': 'RESOURCE_ALREADY_EXISTS',
                'message': ('The resource projects/my-project/instances/'
                            'my-instance already exists')
                }]
            }
        }

    self.assertTrue(command.IsResultAnOperation(error_operation))
    self.assertTrue(command._ErrorsInResultList([error_operation]))
    self.assertTrue(command._ErrorsInResultList(
        [operation] * 10 + [error_operation] + [operation] * 10))

  def testPresenterPresentElement(self):

    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(command_base.GoogleComputeCommand, self).__init__(
            name, flag_values)

        flags.DEFINE_string('zone',
                            None,
                            'The zone to use.',
                            flag_values=flag_values)

    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'myproject'
    flag_values.api_host = 'https://www.googleapis.com/'
    flag_values.service_version = 'v1'

    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)
    presenter = command._presenter

    self.assertEquals(
        'us-central1-a/machineTypes/n1-standard-2-d',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/myproject'
            '/zones/us-central1-a/machineTypes/n1-standard-2-d'))

    #
    # Top level resource types.
    #
    self.assertEquals(
        'europe-west1-a',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/myproject'
            '/zones/europe-west1-a'))

    #
    # Global resource types.
    #

    # Image in your own project returns 'imagename'. (Global resource type).
    self.assertEquals(
        'imagename',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/myproject'
            '/global/images/imagename'))

    # Image in some other project returns reasonable path.
    self.assertEquals(
        'projects/yourproject/global/images/imagename',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/yourproject'
            '/global/images/imagename'))

    #
    # Zone resource types.
    #
    flag_values.zone = 'europe-west1-a'
    command.SetFlags(flag_values)

    # Truncate the type if zone is specified.
    self.assertEquals(
        'us-central1-a/machineTypes/n1-standard-2-d',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/myproject'
            '/zones/us-central1-a/machineTypes/n1-standard-2-d'))

    self.assertEquals(
        'us-central1-a',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/myproject'
            '/zones/us-central1-a'))

    # Truncate the zone if zone is specified.
    self.assertEquals(
        'machineTypes/n1-standard-2-d',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/myproject'
            '/zones/europe-west1-a/machineTypes/n1-standard-2-d'))

    # If the user specifies a long-form zone, it still works.
    flag_values.zone = (
        'https://www.googleapis.com/compute/v1/projects/myproject'
        '/zones/europe-west1-a')
    command.SetFlags(flag_values)

    self.assertEquals(
        'machineTypes/n1-standard-2-d',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/myproject'
            '/zones/europe-west1-a/machineTypes/n1-standard-2-d'))

  def testPresenterPresentRegionElement(self):

    class MockCommand(command_base.GoogleComputeCommand):
      def __init__(self, name, flag_values):
        super(command_base.GoogleComputeCommand, self).__init__(
            name, flag_values)

        flags.DEFINE_string('region',
                            None,
                            'The zone to use.',
                            flag_values=flag_values)

    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'myproject'
    flag_values.api_host = 'https://www.googleapis.com/'
    flag_values.service_version = 'v1'

    command = MockCommand('mock_command', flag_values)
    command.SetFlags(flag_values)
    presenter = command._presenter

    self.assertEquals(
        'my-region/addresses/my-address',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/myproject'
            '/regions/my-region/addresses/my-address'))

    #
    # Top level resource types.
    #
    self.assertEquals(
        'europe-west',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/myproject'
            '/regions/europe-west'))

    #
    # Region resource types.
    #
    flag_values.region = 'europe-west'
    command.SetFlags(flag_values)

    # Truncate the type if region is specified.
    self.assertEquals(
        'us-central/addresses/my-address',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/myproject'
            '/regions/us-central/addresses/my-address'))

    self.assertEquals(
        'us-central',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/myproject'
            '/regions/us-central'))

    # Truncate the region if region is specified.
    self.assertEquals(
        'addresses/my-address',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/myproject'
            '/regions/europe-west/addresses/my-address'))

    # If the user specifies a long-form region, it still works.
    flag_values.region = (
        'https://www.googleapis.com/compute/v1/projects/myproject'
        '/regions/europe-west')
    command.SetFlags(flag_values)

    self.assertEquals(
        'addresses/my-address',
        presenter.PresentElement(
            'https://www.googleapis.com/compute/v1/projects/myproject'
            '/regions/europe-west/addresses/my-address'))


if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
