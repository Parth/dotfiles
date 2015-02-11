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

"""Unit tests for the instance commands."""

from __future__ import with_statement

import path_initializer
path_initializer.InitSysPath()



import base64
import collections
import copy
import json
import logging
import os
from StringIO import StringIO
import sys
import tempfile

from google.apputils import app
import gflags as flags
import unittest

from gcutil_lib import command_base
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_logging
from gcutil_lib import gcutil_unittest
from gcutil_lib import instance_cmds
from gcutil_lib import metadata as metadata_module
from gcutil_lib import mock_api
from gcutil_lib import mock_lists
from gcutil_lib import mock_timer
from gcutil_lib import old_mock_api
from gcutil_lib import windows_password


FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER

_LicenseReference = collections.namedtuple(
    'LicenseReference', ('project', 'name'))


class InstanceCmdsTest(gcutil_unittest.GcutilTestCase):
  # The number of instances used in the tests.
  NUMBER_OF_INSTANCES = 30

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)
    gcutil_logging.SetupLogging()

  def testUnicodeInSerialOutput(self):
    set_flags = {
        'project': 'irrelevant',
    }

    command = self._CreateAndInitializeCommand(
        instance_cmds.GetSerialPortOutput,
        'getserialportoutput', self.version, set_flags)

    # This test should fail if there is a problem with encoding
    # the contents.
    command.PrintResult({'contents': u'Nasty character: \ufffd'})

    # It also works fine with JSON format.
    set_flags['format'] = 'json'

    command = self._CreateAndInitializeCommand(
        instance_cmds.GetSerialPortOutput,
        'getserialportoutput', self.version, set_flags)

    command.PrintResult({'contents': u'Nasty character: \ufffd'})

  def testDeprecatedFlagsInAddInstance(self):
    set_flags = {
        'project': 'cool-project',
        'persistent_boot_disk': False,
    }

    command = self._CreateAndInitializeCommand(
        instance_cmds.AddInstance, 'addinstance', self.version, set_flags)

    self.assertRaises(gcutil_errors.UnsupportedCommand,
                      command.Handle, 'some-instance')

  def testResetInstanceGeneratesCorrectRequest(self):
    set_flags = {
        'project': 'my-project',
        'zone': 'my-zone',
    }

    command = self._CreateAndInitializeCommand(
        instance_cmds.ResetInstance, 'resetinstance', self.version, set_flags)

    call = self.mock.Respond(
        'compute.instances.reset',
        {
            'kind': 'compute#operation',
            'name': 'my-reset-operation'
        })

    result = command.Handle('my-reset-instance')
    self.assertEqual('compute#operation', result['kind'])
    self.assertEqual('my-reset-operation', result['name'])

    # Validate request
    request = call.GetRequest()
    self.assertTrue(request.body is None)
    parameters = request.parameters
    self.assertEqual('my-project', parameters['project'])
    self.assertEqual('my-zone', parameters['zone'])
    self.assertEqual('my-reset-instance', parameters['instance'])

  def testSetInstanceDiskAutoDeleteGeneratesCorrectRequest(self):
    set_flags = {
        'project': 'my-project',
        'zone': 'my-zone',
        'auto_delete': True,
        'device_name': 'mydevice',
    }

    command = self._CreateAndInitializeCommand(
        instance_cmds.SetInstanceDiskAutoDelete, 'setinstancediskautodelete',
        self.version, set_flags)

    call = self.mock.Respond(
        'compute.instances.setDiskAutoDelete',
        {
            'kind': 'compute#operation',
            'name': 'my-operation'
        })

    result = command.Handle('my-instance')
    self.assertEqual('compute#operation', result['kind'])
    self.assertEqual('my-operation', result['name'])

    # Validate request
    request = call.GetRequest()
    self.assertTrue(request.body is None)
    parameters = request.parameters
    self.assertEqual('my-project', parameters['project'])
    self.assertEqual('my-zone', parameters['zone'])
    self.assertEqual('my-instance', parameters['instance'])
    self.assertEqual('mydevice', parameters['deviceName'])
    self.assertEqual('true', parameters['autoDelete'])

  def testDeleteInstanceWithNoInstancesFails(self):
    expected_project = 'fail-project'
    expected_zone = 'copernicus-moon-base'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        }

    command = self._CreateAndInitializeCommand(
        instance_cmds.DeleteInstance, 'deleteinstance', self.version, set_flags)

    self.assertRaises(app.UsageError, command.Handle)

  def testDeleteInstanceWithFullyQualifiedPath(self):
    expected_project = 'cool-project'
    expected_zone = 'danger-zone'
    expected_instance = 'for-instance'

    set_flags = {
        'project': 'wrong-project',
        'delete_boot_pd': False
        }

    command = self._CreateAndInitializeCommand(
        instance_cmds.DeleteInstance, 'deleteinstance', self.version, set_flags)

    qualified_path = command.NormalizeResourceName(expected_project,
                                                   'zones/%s' % expected_zone,
                                                   'instances',
                                                   expected_instance)

    unused_instancelist = mock_lists.GetSampleInstanceListCall(
        command, self.mock, 1, [expected_instance], [], [])

    def DeleteResponse(unused_uri, unused_http_method, parameters,
                       unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'name': parameters['instance'],
              'operationType': 'delete',
              'status': 'DONE',
          },
          False)

    instancecall = self.mock.RespondF('compute.instances.delete',
                                      DeleteResponse)

    command.Handle(qualified_path)

    requests = instancecall.GetAllRequests()
    self.assertEquals(1, len(requests))

    request = requests[0]

    self.assertEquals(expected_project, request.parameters['project'])
    self.assertEquals(expected_zone, request.parameters['zone'])
    self.assertEquals(expected_instance, request.parameters['instance'])

  def testForcedDeleteInstanceRequiresPersistentDiskFlag(self):
    expected_project = 'cool-project'
    expected_description = 'This deletion will fail.'
    expected_instance = 'cool-instance'
    expected_disk = 'cool-disk'
    expected_device_name = 'device-name'
    expected_zone = 'copernicus-moon-base'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        'synchronous_mode': False,
        'force': True
        }

    command = self._CreateAndInitializeCommand(
        instance_cmds.DeleteInstance, 'deleteinstance', self.version, set_flags)

    # An attached disk will be detected first.
    attached_disk = [{
        'deviceName': expected_device_name,
        'type': 'PERSISTENT',
        'boot': True,
        'kind': 'compute#attachedDisk',
        'mode': 'READ_WRITE',
        'source': command.NormalizePerZoneResourceName(expected_project,
                                                       expected_zone,
                                                       'disks',
                                                       expected_disk)
        }]

    unused_instancelist = mock_lists.GetSampleInstanceListCall(
        command, self.mock, 1, [expected_instance], [expected_description],
        [attached_disk])

    self.assertRaises(app.UsageError, command.Handle, expected_instance)

  def testDeleteInstanceGeneratesCorrectRequest(self):
    expected_project = 'test-project'
    expected_instance = 'test-instance'
    expected_zone = 'copernicus-moon-base'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        'delete_boot_pd': False
        }

    command = self._CreateAndInitializeCommand(
        instance_cmds.DeleteInstance, 'deleteinstance', self.version, set_flags)

    unused_instancelist = mock_lists.GetSampleInstanceListCall(
        command, self.mock, 1, [expected_instance], [], [])

    def DeleteResponse(unused_uri, unused_http_method, parameters,
                       unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'name': parameters['instance'],
              'operationType': 'delete',
              'status': 'DONE',
              'targetLink': command.NormalizeResourceName(
                  parameters['project'],
                  'zones/%s' % parameters['zone'],
                  'instances',
                  parameters['instance']),
              'zone': command.NormalizeGlobalResourceName(
                  expected_project,
                  'zones',
                  parameters['zone'])
          },
          False)

    instancecall = self.mock.RespondF('compute.instances.delete',
                                      DeleteResponse)

    (unused_results, exceptions) = command.Handle(expected_instance)
    self.assertEquals(exceptions, [])
    requests = instancecall.GetAllRequests()
    self.assertEquals(1, len(requests))

    request = requests[0]

    self.assertEquals(expected_project, request.parameters['project'])
    self.assertEquals(expected_zone, request.parameters['zone'])
    self.assertEquals(expected_instance, request.parameters['instance'])

  def testDeleteInstanceDetectsZone(self):
    expected_project = 'test-project'
    expected_instance = 'test-instance'
    expected_zone = 'copernicus-moon-base'

    set_flags = {
        'project': expected_project,
        'delete_boot_pd': False
        }

    command = self._CreateAndInitializeCommand(
        instance_cmds.DeleteInstance, 'deleteinstance', self.version, set_flags)

    unused_instancelist = mock_lists.GetSampleInstanceListCall(
        command, self.mock, 1, [expected_instance], [], [])

    expected_selflink = (
        'https://www.googleapis.com/compute/v1/'
        'projects/%s/zones/%s/instances/%s') % (
            expected_project, expected_zone, expected_instance)

    aggregated_list_response = {
        'items': {
            ('zones/%s' % expected_zone): {
                'instances': [{
                    'kind': 'compute#instance',
                    'name': expected_instance,
                    'description': '',
                    'selfLink': expected_selflink
                    }],
            },
            'zones/empty-zone': {
                'warning': {
                    'code': 'NO_RESULTS_ON_PAGE',
                    'data': [{
                        'key': 'scope',
                        'value': 'zones/empty-zone',
                    }],
                    'message': ('There are no results for scope '
                                '\'zones/empty-zone\' on this page.')
                }
            }
        },
    }

    self.mock.Respond('compute.instances.aggregatedList',
                      aggregated_list_response)

    instance_call = self.mock.Respond('compute.instances.delete', {})

    requests, exceptions = command.Handle(expected_instance)
    self.assertEquals(exceptions, [])
    requests = instance_call.GetAllRequests()
    self.assertEquals(1, len(requests))

    request = requests[0]

    self.assertEquals(expected_project, request.parameters['project'])
    self.assertEquals(expected_zone, request.parameters['zone'])
    self.assertEquals(expected_instance, request.parameters['instance'])

  def testDeleteMultipleInstances(self):
    expected_project = 'test-project'
    expected_instances = ['test-instance-%02d' % i for i in
                          range(self.NUMBER_OF_INSTANCES)]
    expected_zone = 'zone-a'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        'delete_boot_pd': False
        }

    command = self._CreateAndInitializeCommand(
        instance_cmds.DeleteInstance, 'deleteinstance', self.version, set_flags)

    for instance in expected_instances:
      unused_instancelist = mock_lists.GetSampleInstanceListCall(
          command, self.mock, 1, instance, [], [])

    def DeleteResponse(unused_uri, unused_http_method, parameters,
                       unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'name': parameters['instance'],
              'operationType': 'delete',
              'status': 'DONE',
              'targetLink': command.NormalizeGlobalResourceName(
                  parameters['project'],
                  'instances',
                  parameters['instance']),
              'zone': command.NormalizeGlobalResourceName(
                  expected_project,
                  'zones',
                  parameters['zone'])
          },
          False)

    instancecall = self.mock.RespondF('compute.instances.delete',
                                      DeleteResponse)

    (unused_results, exceptions) = command.Handle(*expected_instances)
    self.assertEqual(exceptions, [])

    requests = instancecall.GetAllRequests()
    self.assertEqual(len(requests), len(expected_instances))

    for request in requests:
      parameters = request.parameters
      self.assertEqual(expected_project, parameters['project'])
      self.assertEqual(expected_zone, parameters['zone'])
      expected_instances.remove(parameters['instance'])

  def testAddInstanceWithSpecifiedBootDisk(self):
    expected_project = 'cool-project'
    expected_instance = 'cool-instance'
    expected_zone = 'the-danger-zone'
    expected_machine_type = 'party-machine'
    disk_name = 'win1'
    disk_flag = ['%s,boot' % disk_name]

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        'disk': disk_flag,
        'machine_type': expected_machine_type,
        'add_compute_key_to_project': False,
        'auto_delete_boot_disk': True,
        }

    command = self._CreateAndInitializeCommand(
        instance_cmds.AddInstance, 'addinstance', self.version, set_flags)

    # A call to _GetZone occurrs for the given zone.
    unused_zonecall = self.mock.Respond(
        'compute.zones.get',
        {
            'kind': 'compute#zone',
            'name': expected_zone,
            'status': 'UP',
            'selfLink': command.NormalizeGlobalResourceName(expected_project,
                                                            'zones',
                                                            expected_zone)
        })

    # Also a call to compute.projects.get.
    unused_projectcall = self.mock.Respond(
        'compute.projects.get',
        {
            'kind': 'compute#project',
            'name': expected_project,
            'description': 'the expected project',
            'selfLink': command.NormalizeGlobalResourceName(expected_project,
                                                            'projects',
                                                            expected_project)
        })

    # And set metadata.
    unused_metadatacall = self.mock.Respond(
        'compute.projects.setCommonInstanceMetadata',
        {
            'kind': 'compute#operation',
            'status': 'DONE'
        })

    # Simulate some non-windows license on the disk.  It allows us to test
    # that the code does not mistake non-windows license for windows
    # license.
    licenses = [
        _LicenseReference('project1', 'license1'),
        _LicenseReference('project2', 'license2'),
    ]
    self._MockDiskGet(command,
                      expected_project,
                      expected_zone,
                      disk_name,
                      licenses)

    # The instance call will succeed.
    def InstanceInsertResponse(unused_uri, unused_http_method, parameters,
                               body):
      return self.mock.MOCK_RESPONSE(
          {
              'disks': json.loads(body)['disks'],
              'kind': 'compute#operation',
              'name': json.loads(body)['name'],
              'operationType': 'insert',
              'status': 'DONE',
              'targetLink': command.NormalizeGlobalResourceName(
                  expected_project,
                  'projects',
                  json.loads(body)['name']),
              'zone': command.NormalizeGlobalResourceName(
                  parameters['project'],
                  'zones',
                  parameters['zone'])
          },
          True)

    # Now the user will choose to create the instance, reusing the disk.
    instancecall = self.mock.RespondF('compute.instances.insert',
                                      InstanceInsertResponse)

    # Handle the command.
    (unused_results, exceptions) = command.Handle(expected_instance)
    self.assertEquals(exceptions, [])

    # Check the request.
    instance_requests = instancecall.GetAllRequests()
    self.assertEquals(1, len(instance_requests))
    instance_request_body = json.loads(instance_requests[0].body)
    instance_request_parameters = instance_requests[0].parameters
    self.assertEquals(expected_zone, instance_request_parameters['zone'])
    self.assertEquals(expected_project, instance_request_parameters['project'])
    self.assertEquals(expected_instance, instance_request_body['name'])
    self.assertFalse(
        self._GetMetadataInRequest(
            instancecall,
            metadata_module.INITIAL_WINDOWS_USER_METADATA_NAME))
    self.assertFalse(
        self._GetMetadataInRequest(
            instancecall,
            metadata_module.INITIAL_WINDOWS_PASSWORD_METADATA_NAME))

    # Disk is constructed by AddInstance.
    expected_disks = [{
        u'source': command.NormalizePerZoneResourceName(
            expected_project,
            expected_zone,
            'disks',
            disk_name),
        u'type': u'PERSISTENT',
        u'deviceName': disk_name,
        u'boot': True,
        u'mode': u'READ_WRITE',
        u'autoDelete': True}]

    self.assertEquals(expected_disks, instance_request_body['disks'])

  def testAddInstanceAndWaitUntilComplete(self):
    expected_project = 'cool-project'
    expected_instance = 'fail-instance'
    expected_zone = 'the-danger-zone'
    expected_machine = 'party-machine'
    expected_image = 'imagination'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        'add_compute_key_to_project': False,
        'machine_type': expected_machine,
        'image': expected_image
        }

    boot_disk_name = 'cool-disk'
    set_flags['disk'] = ['{0},boot'.format(boot_disk_name)]

    command = self._CreateAndInitializeCommand(
        instance_cmds.AddInstance, 'addinstance', self.version, set_flags)

    # gcutil checks to see whether the image is on any known list.
    mock_lists.MockImageListForCustomerAndStandardProjects(command, self.mock)

    self._MockDiskGet(command,
                      expected_project,
                      expected_zone,
                      boot_disk_name)

    # The instance call will succeed.
    def InstanceInsertResponse(unused_uri, unused_http_method, parameters,
                               body):
      return self.mock.MOCK_RESPONSE(
          {
              'disks': json.loads(body)['disks'],
              'kind': 'compute#operation',
              'name': json.loads(body)['name'],
              'operationType': 'insert',
              'status': 'DONE',
              'targetLink': command.NormalizePerZoneResourceName(
                  expected_project,
                  parameters['zone'],
                  'instances',
                  json.loads(body)['name']),
              'zone': command.NormalizeGlobalResourceName(
                  parameters['project'],
                  'zones',
                  parameters['zone'])
          },
          True)

    # Create the instance.
    self.mock.RespondF('compute.instances.insert', InstanceInsertResponse)

    # Now the instances.get call goes through.
    def InstanceGetResponse(unused_uri, unused_http_method, parameters,
                            unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'name': parameters['name'],
              'status': 'RUNNING',
              'selfLink': command.NormalizePerZoneResourceName(
                  expected_project,
                  parameters['zone'],
                  'instances',
                  parameters['name']),
              'zone': command.NormalizeGlobalResourceName(
                  parameters['project'],
                  'zones',
                  parameters['zone'])
          },
          True)

    # Check that the instance is running.
    self.mock.RespondF('compute.instances.get', InstanceGetResponse)

    # Handle the command.
    (unused_results, exceptions) = command.Handle(expected_instance)
    self.assertEquals(exceptions, [])

    # Parameter validation occurs elsewhere.  If this code path does not crash,
    # then the test was successful.

  def testAddInstanceWithWindowsImageNoInitialUserAndPassword(self):
    """Test AddInstance with a Windows image, and user or password not provided.
    """
    expected_instance = 'my-instance'
    expected_user_name = 'cool-project'  # same as project id.
    command, instancecall = self._SetUpAddInstanceUsingWindowsImage()

    (unused_results, exceptions) = command.Handle(expected_instance)
    self.assertEquals(exceptions, [])

    # Validate that the metadata contains the user name based on project name.
    self._ValidateMetadataContains(
        instancecall,
        metadata_module.INITIAL_WINDOWS_USER_METADATA_NAME,
        expected_user_name)

    # Validate that the metadata contains some randomly generated password.
    password = self._GetMetadataInRequest(
        instancecall,
        metadata_module.INITIAL_WINDOWS_PASSWORD_METADATA_NAME)
    LOGGER.info('Generated password: ' + password)
    windows_password.ValidateStrongPasswordRequirement(
        password,
        expected_user_name)

  def testAddInstanceWithWindowsImageWithInitialUserAndPassword(self):
    """Test AddInstance with a Windows image, and user and password provided.
    """
    expected_password = 'Pa$$w0rd'
    expected_user_name = 'adminuser'
    expected_instance = 'my-instance'
    handle, path = tempfile.mkstemp()
    try:
      with os.fdopen(handle, 'w') as metadata_file:
        metadata_file.write(expected_password)
        command, instancecall = self._SetUpAddInstanceUsingWindowsImage(
            expected_user_name, path)

      # Handle the command.
      (unused_results, exceptions) = command.Handle(expected_instance)
      self.assertEquals(exceptions, [])
    finally:
      os.remove(path)

    # Validate that the meta data contains the user name and password
    self._ValidateMetadataContains(
        instancecall,
        metadata_module.INITIAL_WINDOWS_USER_METADATA_NAME,
        expected_user_name)
    self._ValidateMetadataContains(
        instancecall,
        metadata_module.INITIAL_WINDOWS_PASSWORD_METADATA_NAME,
        expected_password)

  def _GetMetadataInRequest(self, instancecall, key):
    instance_requests = instancecall.GetAllRequests()
    request = instance_requests[0]
    body = json.loads(request.body)
    metadata = body['metadata']['items']
    return metadata_module.GetMetadataValue(metadata, key)

  def _ValidateMetadataContains(
      self, instancecall, key, expected_value):
    self.assertEqual(expected_value,
                     self._GetMetadataInRequest(instancecall, key))

  def _SetUpAddInstanceUsingWindowsImage(
      self, user_name=None, password_file=None):
    expected_project = 'cool-project'
    expected_zone = 'the-danger-zone'
    expected_machine = 'party-machine'
    expected_image = 'windows-image'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        'add_compute_key_to_project': False,
        'machine_type': expected_machine,
        'image': expected_image,
        'synchronous_mode': False,
    }

    if user_name:
      set_flags['metadata'] = [
          metadata_module.INITIAL_WINDOWS_USER_METADATA_NAME + ':' +
          user_name]
    if password_file:
      set_flags['metadata_from_file'] = [
          metadata_module.INITIAL_WINDOWS_PASSWORD_METADATA_NAME + ':' +
          password_file]
    disk_name = 'cool-disk'
    set_flags['disk'] = [disk_name + ',boot']

    command = self._CreateAndInitializeCommand(
        instance_cmds.AddInstance, 'addinstance', self.version, set_flags)

    # gcutil checks to see whether the image is on any known list.
    mock_lists.MockImageListForCustomerAndStandardProjects(command, self.mock)

    # Include windows license.
    licenses = [
        _LicenseReference('test-project', 'test-license'),
        _LicenseReference(
            command_base.WINDOWS_IMAGE_PROJECTS[0], 'windows-2008')
    ]
    self._MockDiskGet(command,
                      expected_project,
                      expected_zone,
                      disk_name,
                      licenses)

    # The instance call will succeed.
    def InstanceInsertResponse(unused_uri, unused_http_method, parameters,
                               body):
      return self.mock.MOCK_RESPONSE(
          {
              'disks': json.loads(body)['disks'],
              'kind': 'compute#operation',
              'name': json.loads(body)['name'],
              'operationType': 'insert',
              'status': 'DONE',
              'targetLink': command.NormalizePerZoneResourceName(
                  expected_project,
                  parameters['zone'],
                  'instances',
                  json.loads(body)['name']),
              'zone': command.NormalizeGlobalResourceName(
                  parameters['project'],
                  'zones',
                  parameters['zone'])
          },
          True)

    # Create the instance.
    instancecall = self.mock.RespondF('compute.instances.insert',
                                      InstanceInsertResponse)
    return (command, instancecall)

  def testAddInstanceWithPersistentBootDisk(self):
    expected_project = 'cool-project'
    expected_instance = 'cool-instance'
    expected_zone = 'the-danger-zone'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        'add_compute_key_to_project': False
        }

    expected_disk_type = 'pd-ssd'
    set_flags['boot_disk_type'] = expected_disk_type

    # Capture I/O.
    oldin = sys.stdin
    sys.stdin = StringIO('1\ny\n2\n')

    command = self._CreateAndInitializeCommand(
        instance_cmds.AddInstance, 'addinstance', self.version, set_flags)

    # First, the user will be prompted to select a machine type.
    unused_machinetypecall = (
        mock_lists.GetSampleMachineTypeListCall(
            command, self.mock, 2))

    # Next, the user will be prompted to select an image.
    mock_lists.MockImageListForCustomerAndStandardProjects(
        command,
        self.mock,
        ((), ('bad_image', 'my_image')))

    # We also do an image.get call.
    unused_imagegetcall = self.mock.Respond(
        'compute.images.get',
        {
            'kind': 'compute#image',
            'description': 'mock image',
            'name': 'image',
            'status': 'READY',
            'selfLink': command.NormalizeGlobalResourceName(
                expected_project,
                'images',
                'image')
        })

    # No problem, the disk is created.
    def DiskInsertResponse(unused_uri, unused_http_method, parameters, body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'name': json.loads(body)['name'],
              'operationType': 'insert',
              'status': 'DONE',
              'targetLink': command.NormalizeGlobalResourceName(
                  expected_project,
                  'projects',
                  json.loads(body)['name']),
              'zone': command.NormalizeGlobalResourceName(expected_project,
                                                          'zones',
                                                          parameters['zone'])
          },
          True)

    diskcall = self.mock.RespondF('compute.disks.insert',
                                  DiskInsertResponse)

    # A call to _GetZone occurrs for the given zone.
    unused_zonecall = self.mock.Respond(
        'compute.zones.get',
        {
            'kind': 'compute#zone',
            'name': expected_zone,
            'status': 'UP',
            'selfLink': command.NormalizeGlobalResourceName(expected_project,
                                                            'zones',
                                                            expected_zone)
        })

    # Also a call to compute.projects.get.
    unused_projectcall = self.mock.Respond(
        'compute.projects.get',
        {
            'kind': 'compute#project',
            'name': expected_project,
            'description': 'the expected project',
            'selfLink': command.NormalizeGlobalResourceName(expected_project,
                                                            'projects',
                                                            expected_project)
        })

    # And set metadata.
    unused_metadatacall = self.mock.Respond(
        'compute.projects.setCommonInstanceMetadata',
        {
            'kind': 'compute#operation',
            'status': 'DONE'
        })

    # The instance call will succeed.
    def InstanceInsertResponse(unused_uri, unused_http_method, parameters,
                               body):
      return self.mock.MOCK_RESPONSE(
          {
              'disks': json.loads(body)['disks'],
              'kind': 'compute#operation',
              'name': json.loads(body)['name'],
              'operationType': 'insert',
              'status': 'DONE',
              'targetLink': command.NormalizeGlobalResourceName(
                  expected_project,
                  'projects',
                  json.loads(body)['name']),
              'zone': command.NormalizeGlobalResourceName(
                  parameters['project'],
                  'zones',
                  parameters['zone'])
          },
          True)

    # Now the user will choose to create the instance, reusing the disk.
    instancecall = self.mock.RespondF('compute.instances.insert',
                                      InstanceInsertResponse)

    # Handle the command.
    (unused_results, exceptions) = command.Handle(expected_instance)
    self.assertEquals(exceptions, [])

    # Check some things here.

    # An image was selected and passed along to the disk creation request.
    disk_requests = diskcall.GetAllRequests()
    instance_requests = instancecall.GetAllRequests()
    self.assertEquals(1, len(instance_requests))
    instance_request_body = json.loads(instance_requests[0].body)
    instance_request_parameters = instance_requests[0].parameters
    self.assertEquals(0, len(disk_requests))
    disks = instance_request_body['disks']
    self.assertEquals(command.NormalizeGlobalResourceName(expected_project,
                                                          'images',
                                                          'my_image'),
                      str(disks[0]['initializeParams']['sourceImage']))
    expected_normalized_disk_type = command.NormalizePerZoneResourceName(
        expected_project,
        expected_zone,
        'diskTypes',
        expected_disk_type)
    self.assertEquals(expected_normalized_disk_type,
                      str(disks[0]['initializeParams']['diskType']))

    self.assertEquals(expected_zone, instance_request_parameters['zone'])
    self.assertEquals(expected_project, instance_request_parameters['project'])
    self.assertEquals(expected_instance, instance_request_body['name'])

    # Reset I/O
    sys.stdin = oldin

  def testAddInstanceWithScheduling(self):
    expected_project = 'cool-project'
    expected_instance = 'cool-instance'
    expected_zone = 'the-danger-zone'
    expected_machine_type = 'party-machine'
    disk_name = 'win1'
    disk_flag = ['%s,boot' % disk_name]
    expected_on_host_maintenance = 'migrate'
    expected_automatic_restart = True

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        'disk': disk_flag,
        'machine_type': expected_machine_type,
        'add_compute_key_to_project': False,
        'on_host_maintenance': expected_on_host_maintenance,
        'automatic_restart': expected_automatic_restart,
        }

    command = self._CreateAndInitializeCommand(
        instance_cmds.AddInstance, 'addinstance', self.version, set_flags)

    # A call to _GetZone occurs for the given zone.
    unused_zonecall = self.mock.Respond(
        'compute.zones.get',
        {
            'kind': 'compute#zone',
            'name': expected_zone,
            'status': 'UP',
            'selfLink': command.NormalizeGlobalResourceName(expected_project,
                                                            'zones',
                                                            expected_zone)
        })

    # Also a call to compute.projects.get.
    unused_projectcall = self.mock.Respond(
        'compute.projects.get',
        {
            'kind': 'compute#project',
            'name': expected_project,
            'description': 'the expected project',
            'selfLink': command.NormalizeGlobalResourceName(expected_project,
                                                            'projects',
                                                            expected_project)
        })

    # And set metadata.
    unused_metadatacall = self.mock.Respond(
        'compute.projects.setCommonInstanceMetadata',
        {
            'kind': 'compute#operation',
            'status': 'DONE'
        })

    self._MockDiskGet(command,
                      expected_project,
                      expected_zone,
                      disk_name)

    # The instance call will succeed.
    def InstanceInsertResponse(unused_uri, unused_http_method, parameters,
                               body):
      return self.mock.MOCK_RESPONSE(
          {
              'disks': json.loads(body)['disks'],
              'kind': 'compute#operation',
              'name': json.loads(body)['name'],
              'operationType': 'insert',
              'status': 'DONE',
              'targetLink': command.NormalizeGlobalResourceName(
                  expected_project,
                  'projects',
                  json.loads(body)['name']),
              'zone': command.NormalizeGlobalResourceName(
                  parameters['project'],
                  'zones',
                  parameters['zone'])
          },
          True)

    # Now the user will choose to create the instance, reusing the disk.
    instancecall = self.mock.RespondF('compute.instances.insert',
                                      InstanceInsertResponse)

    # Handle the command.
    (unused_results, exceptions) = command.Handle(expected_instance)
    self.assertEquals(exceptions, [])

    # Check the request.
    instance_requests = instancecall.GetAllRequests()
    self.assertEquals(1, len(instance_requests))
    instance_request_body = json.loads(instance_requests[0].body)
    self.assertEquals(
        expected_on_host_maintenance,
        instance_request_body['scheduling']['onHostMaintenance'])
    self.assertEquals(
        expected_automatic_restart,
        instance_request_body['scheduling']['automaticRestart'])

  def testSetScheduling(self):
    expected_project = 'test-project'
    expected_zone = 'test-zone'
    expected_on_host_maintenance = 'test-on-host-maintenance'
    expected_automatic_restart = True
    expected_instance = 'test-instance'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        'on_host_maintenance': expected_on_host_maintenance,
        'automatic_restart': expected_automatic_restart,
    }

    command = self._CreateAndInitializeCommand(
        instance_cmds.SetScheduling, 'setscheduling', self.version, set_flags)

    call = self.mock.Respond(
        'compute.instances.setScheduling',
        {
            'kind': 'compute#operation',
            'name': 'my-setscheduling-operation'
        })

    command.Handle(expected_instance)

    # Validate request
    request = call.GetRequest()
    parameters = request.parameters
    self.assertEqual(expected_project, parameters['project'])
    self.assertEqual(expected_zone, parameters['zone'])
    self.assertEqual(expected_instance, parameters['instance'])
    instance_request_body = json.loads(request.body)
    self.assertEquals(
        expected_on_host_maintenance,
        instance_request_body['onHostMaintenance'])
    self.assertEquals(
        expected_automatic_restart,
        instance_request_body['automaticRestart'])

  def testDeleteInstanceWithExistingPersistentNonBootDisk(self):
    expected_project = 'cool-project'
    expected_instance = 'uncool-instance'
    expected_description = 'This instance is cool, no deleting it.'
    expected_disk = 'cool-disk'
    expected_zone = 'copernicus-moon-base'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        'delete_boot_pd': True,
        'synchronous_mode': False,
        }

    command = self._CreateAndInitializeCommand(
        instance_cmds.DeleteInstance, 'deleteinstance', self.version, set_flags)

    # The instance has an attached persistent, not-boot disk.
    # I hope it will not be deleted.
    attached_disk = [{
        'deviceName': expected_disk,
        'type': 'PERSISTENT',
        'kind': 'compute#attachedDisk',
        'mode': 'READ_WRITE',
        'source': command.NormalizePerZoneResourceName(expected_project,
                                                       expected_zone,
                                                       'disks',
                                                       expected_disk)
        }]

    unused_instancelist = mock_lists.GetSampleInstanceListCall(
        command, self.mock, 1, [expected_instance], [expected_description],
        [attached_disk])

    # The instance deletion goes through.  Don't keep checking.
    def InstanceDeleteResponse(unused_uri, unused_http_method, parameters,
                               unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'name': parameters['instance'],
              'operationType': 'delete',
              'status': 'PENDING',
              'selfLink': command.NormalizeGlobalResourceName(
                  expected_project,
                  'operations',
                  expected_instance),
              'targetLink': command.NormalizeGlobalResourceName(
                  parameters['project'],
                  'instances',
                  parameters['instance']),
              'zone': command.NormalizeGlobalResourceName(
                  expected_project,
                  'zones',
                  parameters['zone'])
          },
          True)

    instancecall = self.mock.RespondF('compute.instances.delete',
                                      InstanceDeleteResponse)

    # Handle the command.
    (unused_results, exceptions) = command.Handle(expected_instance)
    self.assertEquals(exceptions, [])

    # Validate requests.
    instance_requests = instancecall.GetAllRequests()
    self.assertEquals(1, len(instance_requests))
    instance_request_parameters = instance_requests[0].parameters
    self.assertEquals(expected_zone, instance_request_parameters['zone'])
    self.assertEquals(expected_project, instance_request_parameters['project'])
    self.assertEquals(expected_instance,
                      instance_request_parameters['instance'])

  def testDeleteInstanceButNotAttachedPersistentDisk(self):
    expected_project = 'cool-project'
    expected_instance = 'uncool-instance'
    expected_description = 'This instance is uncool, delete it.'
    expected_disk = 'cool-disk'
    expected_zone = 'copernicus-moon-base'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        }

    # Capture I/O.
    oldin = sys.stdin
    sys.stdin = StringIO('n\n')

    command = self._CreateAndInitializeCommand(
        instance_cmds.DeleteInstance, 'deleteinstance', self.version, set_flags)

    # Since the user didn't specify a persistent boot disk flag, determine
    # whether or not this instance has a persistent boot disk.  It does,
    # but do not delete it.
    attached_disk = [{
        'deviceName': expected_disk,
        'type': 'PERSISTENT',
        'boot': True,
        'kind': 'compute#attachedDisk',
        'mode': 'READ_WRITE',
        'autoDelete': True,
        'source': command.NormalizePerZoneResourceName(expected_project,
                                                       expected_zone,
                                                       'disks',
                                                       expected_disk)
        }]

    unused_instancelist = mock_lists.GetSampleInstanceListCall(
        command, self.mock, 1, [expected_instance], [expected_description],
        [attached_disk])

    # The instance deletion goes through first.
    def InstanceDeleteResponse(unused_uri, unused_http_method, parameters,
                               unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'name': parameters['instance'],
              'operationType': 'delete',
              'status': 'DONE',
              'selfLink': command.NormalizeGlobalResourceName(
                  expected_project,
                  'operations',
                  expected_instance),
              'targetLink': command.NormalizeGlobalResourceName(
                  parameters['project'],
                  'instances',
                  parameters['instance']),
              'zone': command.NormalizeGlobalResourceName(
                  expected_project,
                  'zones',
                  parameters['zone'])
          },
          True)

    instancecall = self.mock.RespondF('compute.instances.delete',
                                      InstanceDeleteResponse)

    def InstanceSetDiskAutoDeleteResponse(unused_uri, unused_http_method,
                                          parameters, unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'name': parameters['instance'],
              'operationType': 'delete',
              'status': 'DONE',
              'selfLink': command.NormalizeGlobalResourceName(
                  expected_project,
                  'operations',
                  expected_instance),
              'targetLink': command.NormalizeGlobalResourceName(
                  parameters['project'],
                  'instances',
                  parameters['instance']),
              'zone': command.NormalizeGlobalResourceName(
                  expected_project,
                  'zones',
                  parameters['zone'])
          },
          True)

    autodeletecall = self.mock.RespondF('compute.instances.setDiskAutoDelete',
                                        InstanceSetDiskAutoDeleteResponse)
    # Handle the command.
    (unused_results, exceptions) = command.Handle(expected_instance)
    self.assertEquals(exceptions, [])

    # Validate requests.
    instance_requests = instancecall.GetAllRequests()
    self.assertEquals(1, len(instance_requests))
    instance_request_parameters = instance_requests[0].parameters
    self.assertEquals(expected_zone, instance_request_parameters['zone'])
    self.assertEquals(expected_project, instance_request_parameters['project'])
    self.assertEquals(expected_instance,
                      instance_request_parameters['instance'])

    # Make sure we disabled auto-delete on the disk before deleting instance.
    set_auto_delete_requests = autodeletecall.GetAllRequests()
    self.assertEquals(1, len(set_auto_delete_requests))
    params = set_auto_delete_requests[0].parameters
    self.assertEquals(expected_zone, params['zone'])
    self.assertEquals(expected_project, params['project'])
    self.assertEquals(expected_instance, params['instance'])
    self.assertEquals(expected_disk, params['deviceName'])
    self.assertEquals('false', params['autoDelete'])

    # Reset I/O
    sys.stdin = oldin

  def testDeleteInstanceWithExistingPersistentBootDisk(self):
    expected_project = 'cool-project'
    expected_instance = 'uncool-instance'
    expected_description = 'This instance is uncool, delete it.'
    expected_disk = 'uncool-disk'
    expected_device_name = 'device-name'
    expected_zone = 'copernicus-moon-base'

    set_flags = {
        'project': expected_project,
        'zone': expected_zone,
        'synchronous_mode': False,
        }

    # Capture I/O.
    oldin = sys.stdin
    sys.stdin = StringIO('y\n')

    command = self._CreateAndInitializeCommand(
        instance_cmds.DeleteInstance, 'deleteinstance', self.version, set_flags)

    # Since the user didn't specify a persistent boot disk flag, determine
    # whether or not this instance has a persistent boot disk.  It will.
    attached_disk = [{
        'deviceName': expected_device_name,
        'type': 'PERSISTENT',
        'boot': True,
        'kind': 'compute#attachedDisk',
        'mode': 'READ_WRITE',
        'autoDelete': False,
        'source': command.NormalizePerZoneResourceName(expected_project,
                                                       expected_zone,
                                                       'disks',
                                                       expected_disk)
        }]

    unused_instancelist = mock_lists.GetSampleInstanceListCall(
        command, self.mock, 1, [expected_instance], [expected_description],
        [attached_disk])

    # The instance deletion goes through first, but is pending the first time.
    def InstanceDeleteResponse(unused_uri, unused_http_method, parameters,
                               unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'name': parameters['instance'],
              'operationType': 'delete',
              'status': 'PENDING',
              'selfLink': command.NormalizeGlobalResourceName(
                  expected_project,
                  'operations',
                  expected_instance),
              'targetLink': command.NormalizeGlobalResourceName(
                  parameters['project'],
                  'instances',
                  parameters['instance']),
              'zone': command.NormalizeGlobalResourceName(
                  expected_project,
                  'zones',
                  parameters['zone'])
          },
          True)

    instancecall = self.mock.RespondF('compute.instances.delete',
                                      InstanceDeleteResponse)

    # A call to global operations happens to see if the instance is deleted.
    opscall = self.mock.Respond(
        'compute.globalOperations.get',
        {
            'kind': 'compute#operation',
            'name': expected_instance,
            'operationType': 'delete',
            'status': 'DONE',
            'selfLink': command.NormalizeGlobalResourceName(
                expected_project,
                'operations',
                expected_instance),
            'targetLink': command.NormalizeGlobalResourceName(
                expected_project,
                'instances',
                expected_instance),
            'zone': command.NormalizeGlobalResourceName(
                expected_project,
                'zones',
                expected_zone)
        })

    # The disk deletions go through next.
    def DiskDeleteResponse(unused_uri, unused_http_method, parameters,
                           unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'name': parameters['disk'],
              'operationType': 'delete',
              'project': parameters['project'],
              'status': 'DONE',
              'targetLink': command.NormalizeGlobalResourceName(
                  expected_project,
                  'projects',
                  parameters['disk']),
              'zone': command.NormalizeGlobalResourceName(expected_project,
                                                          'zones',
                                                          parameters['zone'])
          },
          True)
    self.mock.RespondF('compute.disks.delete', DiskDeleteResponse)

    def InstanceSetDiskAutoDeleteResponse(unused_uri, unused_http_method,
                                          parameters, unused_body):
      return self.mock.MOCK_RESPONSE(
          {
              'kind': 'compute#operation',
              'name': parameters['instance'],
              'operationType': 'delete',
              'status': 'DONE',
              'selfLink': command.NormalizeGlobalResourceName(
                  expected_project,
                  'operations',
                  expected_instance),
              'targetLink': command.NormalizeGlobalResourceName(
                  parameters['project'],
                  'instances',
                  parameters['instance']),
              'zone': command.NormalizeGlobalResourceName(
                  expected_project,
                  'zones',
                  parameters['zone'])
          },
          True)

    autodeletecall = self.mock.RespondF('compute.instances.setDiskAutoDelete',
                                        InstanceSetDiskAutoDeleteResponse)
    # Handle the command.
    (unused_results, exceptions) = command.Handle(expected_instance)
    self.assertEquals(exceptions, [])

    # Validate requests.
    # No need to specifically wait for instances before deleting disks
    # since this happens in one shot.
    expected_ops_requests = 0

    ops_requests = opscall.GetAllRequests()
    self.assertEquals(expected_ops_requests, len(ops_requests))

    instance_requests = instancecall.GetAllRequests()
    self.assertEquals(1, len(instance_requests))
    instance_request_parameters = instance_requests[0].parameters
    self.assertEquals(expected_zone, instance_request_parameters['zone'])
    self.assertEquals(expected_project, instance_request_parameters['project'])
    self.assertEquals(expected_instance,
                      instance_request_parameters['instance'])

    # Make sure we enabled auto-delete on the disk before deleting instance.
    set_auto_delete_requests = autodeletecall.GetAllRequests()
    self.assertEquals(1, len(set_auto_delete_requests))
    params = set_auto_delete_requests[0].parameters
    self.assertEquals(expected_zone, params['zone'])
    self.assertEquals(expected_project, params['project'])
    self.assertEquals(expected_instance, params['instance'])
    self.assertEquals(expected_device_name, params['deviceName'])
    self.assertEquals('true', params['autoDelete'])

    # Reset I/O
    sys.stdin = oldin

  def testAddInstanceGeneratesCorrectRequest(self):
    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_description = 'test instance'
    submitted_image = 'expected_image'
    submitted_machine_type = 'goes_to_11'
    submitted_zone = 'copernicus-moon-base'
    expected_authorized_ssh_keys = []

    set_flags = {
        'project': expected_project,
        'zone': submitted_zone,
        'machine_type': submitted_machine_type,
        'description': expected_description,
        'image': submitted_image,
        'use_compute_key': False,
        'authorized_ssh_keys': expected_authorized_ssh_keys,
        'add_compute_key_to_project': False,
        'synchronous_mode': False
        }

    boot_disk_name = 'cool-disk'
    set_flags['disk'] = [boot_disk_name + ',boot']

    command = self._CreateAndInitializeCommand(
        instance_cmds.AddInstance, 'addinstance', self.version, set_flags)

    def InstanceInsertResponse(unused_uri, unused_http_method, parameters,
                               body):
      response_body = {
          'disks': json.loads(body)['disks'],
          'kind': 'compute#operation',
          'name': json.loads(body)['name'],
          'operationType': 'insert',
          'status': 'DONE',
          'targetLink': command.NormalizeGlobalResourceName(
              expected_project,
              'projects',
              json.loads(body)['name']),
          'zone': command.NormalizeGlobalResourceName(
              parameters['project'],
              'zones',
              parameters['zone'])
          }
      return self.mock.MOCK_RESPONSE(response_body, True)

    instancecall = self.mock.RespondF('compute.instances.insert',
                                      InstanceInsertResponse)

    unused_zonecall = self.mock.Respond(
        'compute.zones.get',
        {
            'kind': 'compute#zone',
            'name': submitted_zone,
            'status': 'UP',
            'selfLink': command.NormalizeGlobalResourceName(expected_project,
                                                            'zones',
                                                            submitted_zone)
        })

    unused_imagecall = mock_lists.GetSampleImageListCall(command,
                                                         self.mock,
                                                         1,
                                                         [submitted_image])

    self._MockDiskGet(command,
                      expected_project,
                      submitted_zone,
                      boot_disk_name)

    (unused_results, exceptions) = command.Handle(expected_instance)

    self.assertEqual(exceptions, [])

    instance_requests = instancecall.GetAllRequests()
    self.assertEquals(1, len(instance_requests))
    request = instance_requests[0]

    expected_kind = command._GetResourceApiKind('instance')

    parameters = request.parameters
    body = json.loads(request.body)
    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(body['kind'], expected_kind)
    self.assertEqual(body['name'], expected_instance)
    self.assertEqual(body['description'], expected_description)

    self.assertFalse(
        'natIP' in body['networkInterfaces'][0]['accessConfigs'][0])

    self.assertEqual(body['metadata'], {
        'kind': 'compute#metadata',
        'items': []})

    instance_tags = body.get('tags', {}).get('items', [])
    self.assertEqual(instance_tags, [])

    self.assertFalse('canIpForward' in body)
    self.assertEqual(submitted_zone, parameters['zone'])
    self.assertFalse('zone' in body)

  def _MockImageGet(self, command, project, image_name, licenses=()):
    response = {
        'kind': 'compute#image',
        'description': 'mock image',
        'name': image_name,
        'status': 'READY',
        'selfLink': command.NormalizeGlobalResourceName(
            project,
            'images',
            image_name)
    }
    self._AddLicenseUrlsToResponse(command, response, licenses)
    self.mock.Respond('compute.images.get', response)

  def _MockDiskGet(self, command, project, zone, disk_name, licenses=()):
    response = {
        'kind': 'compute#disk',
        'description': 'mock disk',
        'name': disk_name,
        'zone': command.NormalizeGlobalResourceName(
            project,
            'zones',
            zone),
        'status': 'READY',
        'selfLink': command.NormalizeGlobalResourceName(
            project,
            'disk',
            disk_name)
    }
    self._AddLicenseUrlsToResponse(command, response, licenses)
    self.mock.Respond('compute.disks.get', response)

  def _AddLicenseUrlsToResponse(self, command, response, licenses):
    if licenses:
      urls = [command.NormalizeGlobalResourceName(
          lic.project,
          'licenses',
          lic.name) for lic in licenses]
      response['licenses'] = urls


class OldInstanceCmdsTest(unittest.TestCase):

  # The number of instances used in the tests.
  NUMBER_OF_INSTANCES = 30

  def setUp(self):
    self._projects = old_mock_api.MockProjectsApi()
    self._instances = old_mock_api.MockInstancesApi()
    self._machine_types = old_mock_api.MockMachineTypesApi()
    self._zones = old_mock_api.MockZonesApi()
    self._disks = old_mock_api.MockDisksApi()
    self._images = old_mock_api.MockImagesApi()

    self._projects.get = old_mock_api.CommandExecutor(
        {'externalIpAddresses': ['192.0.2.2', '192.0.2.3', '192.0.2.4']})

    self._zones.list = old_mock_api.CommandExecutor(
        {'kind': 'compute#zoneList',
         'items': [{'name': 'zone1'},
                   {'name': 'zone2'}]})

    # This response is used for 'instances.list' on certain add calls.
    self._instance_list = {
        'items': [
            {'name': 'foo',
             'networkInterfaces': [{'accessConfigs': [{'type': 'ONE_TO_ONE_NAT',
                                                       'natIP': '192.0.2.2'}]}]
            },
            {'name': 'bar',
             'networkInterfaces': [{'accessConfigs': [{'type': 'ONE_TO_ONE_NAT',
                                                       'natIP': '192.0.2.3'}]}]
            },
            ]}

  # This is a stop-gap until the old tests are converted over to the new
  # framework.  This is handled more elegantly in the new framework.
  def _DoNotPauseForCommand(self, command):
    command._timer = mock_timer.MockTimer()
    command.THREAD_POOL_WAIT_TIME = 0

  def _DoTestAddMultipleInstances(self, service_version):
    flag_values = copy.deepcopy(FLAGS)

    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project = 'test_project'
    expected_instances = ['test-instance-%02d' % i for i in
                          xrange(self.NUMBER_OF_INSTANCES)]
    expected_description = 'test instance'
    submitted_image = 'expected_image'
    submitted_machine_type = 'goes_to_11'
    submitted_zone = 'copernicus-moon-base'

    expected_authorized_ssh_keys = []
    flag_values.service_version = service_version
    flag_values.zone = submitted_zone
    flag_values.machine_type = submitted_machine_type
    flag_values.project = expected_project
    flag_values.description = expected_description
    flag_values.image = submitted_image
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = expected_authorized_ssh_keys
    flag_values.add_compute_key_to_project = False

    self._instances.list = old_mock_api.CommandExecutor(self._instance_list)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    expected_image = command.NormalizeGlobalResourceName(expected_project,
                                                         'images',
                                                         submitted_image)

    (results, exceptions) = command.Handle(*expected_instances)

    self.assertEqual(exceptions, [])
    results = results['items']
    self.assertEqual(len(results), len(expected_instances))

    for (expected_instance, result) in zip(expected_instances, results):
      expected_kind = command._GetResourceApiKind('instance')

      self.assertEqual(result['project'], expected_project)
      self.assertEqual(result['body']['kind'], expected_kind)
      self.assertEqual(result['body']['name'], expected_instance)
      self.assertEqual(result['body']['description'], expected_description)
      self.assertEqual(
          result['body']['disks'][0]['deviceName'],
          expected_instance)
      self.assertEqual(
          result['body']['disks'][0]['initializeParams']['diskName'],
          expected_instance)
      self.assertEqual(
          result['body']['disks'][0]['initializeParams']['sourceImage'],
          expected_image)
      self.assertFalse(
          'natIP' in result['body']['networkInterfaces'][0]['accessConfigs'][0],
          result)

      self.assertEqual(result['body'].get('metadata'), {
          'kind': 'compute#metadata',
          'items': []})

      instance_tags = result['body'].get('tags', [])
      instance_tags = result['body'].get('tags', {}).get('items', [])
      self.assertFalse('zone' in result['body'])
      self.assertEqual(instance_tags, [])

  def testAddMultipleInstances(self):
    for ver in command_base.SUPPORTED_VERSIONS:
      self._DoTestAddMultipleInstances(ver)

  def testAddInstanceWithCanIpForwardGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    flag_values.service_version = 'v1'
    flag_values.zone = 'happy_zone'
    flag_values.machine_type = 'machinetype1'
    flag_values.project = 'test_project'
    flag_values.description = 'description'
    flag_values.image = 'myimage'
    flag_values['can_ip_forward'].Parse('true')
    flag_values.add_compute_key_to_project = False

    self._instances.list = old_mock_api.CommandExecutor(self._instance_list)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    (results, exceptions) = command.Handle('test_instance')
    self.assertEqual(exceptions, [])
    result = results['items'][0]
    self.assertEqual(result['body']['canIpForward'], True)

  def testAddInstanceWithDiskOptionsGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'myproject'
    flag_values.service_version = 'v1'

    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    expected_instance = 'test_instance'
    submitted_image = 'image-foo'
    submitted_zone = 'copernicus-moon-base'
    submitted_disk_old_name = 'disk123:name123'
    submitted_disk_name = 'disk234,deviceName=name234'
    submitted_disk_read_only = 'disk345,mode=READ_ONLY'
    submitted_disk_read_write = 'disk456,mode=READ_WRITE'
    submitted_disk_name_read_only = 'disk567,deviceName=name567,mode=READ_ONLY'
    submitted_disk_no_name = 'disk678'
    submitted_disk_full_name = (
        'https://www.googleapis.com/compute/v1/'
        'projects/google.com:test/zones/my-zone/disks/disk789')
    submitted_disk_ro = 'disk890,mode=ro'
    submitted_disk_rw = 'disk90A,mode=rw'
    submitted_machine_type = 'goes_to_11'

    expected_authorized_ssh_keys = []

    flag_values.disk = [submitted_disk_old_name,
                        submitted_disk_name,
                        submitted_disk_read_only,
                        submitted_disk_read_write,
                        submitted_disk_name_read_only,
                        submitted_disk_no_name,
                        submitted_disk_full_name + ',mode=READ_WRITE',
                        submitted_disk_ro,
                        submitted_disk_rw]
    flag_values.machine_type = submitted_machine_type
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = expected_authorized_ssh_keys
    flag_values.add_compute_key_to_project = False
    flag_values.image = submitted_image
    flag_values.zone = submitted_zone

    disk_zone = 'zones/copernicus-moon-base'

    self._disks.get = old_mock_api.CommandExecutor(
        {'zone': disk_zone})
    self._instances.list = old_mock_api.CommandExecutor(self._instance_list)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.disks = self._disks
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    (results, exceptions) = command.Handle(expected_instance)
    result = results['items'][0]

    # Auto-created boot disk is first.
    disk = result['body']['disks'][0]
    self.assertEqual(disk['deviceName'], expected_instance)
    self.assertEqual(disk['mode'], 'READ_WRITE')

    # And now the data disks.
    disk = result['body']['disks'][1]
    self.assertEqual(disk['deviceName'], 'name123')
    self.assertEqual(disk['mode'], 'READ_WRITE')
    disk = result['body']['disks'][2]
    self.assertEqual(disk['deviceName'], 'name234')
    self.assertEqual(disk['mode'], 'READ_WRITE')
    disk = result['body']['disks'][3]
    self.assertEqual(disk['deviceName'], 'disk345')
    self.assertEqual(disk['mode'], 'READ_ONLY')
    disk = result['body']['disks'][4]
    self.assertEqual(disk['deviceName'], 'disk456')
    self.assertEqual(disk['mode'], 'READ_WRITE')
    disk = result['body']['disks'][5]
    self.assertEqual(disk['deviceName'], 'name567')
    self.assertEqual(disk['mode'], 'READ_ONLY')
    disk = result['body']['disks'][6]
    self.assertEqual(disk['deviceName'], submitted_disk_no_name)
    self.assertEqual(disk['mode'], 'READ_WRITE')
    disk = result['body']['disks'][7]
    self.assertEqual(disk['deviceName'], submitted_disk_full_name)
    self.assertEqual(disk['mode'], 'READ_WRITE')
    disk = result['body']['disks'][8]
    self.assertEqual(disk['deviceName'], 'disk890')
    self.assertEqual(disk['mode'], 'READ_ONLY')
    disk = result['body']['disks'][9]
    self.assertEqual(disk['deviceName'], 'disk90A')
    self.assertEqual(disk['mode'], 'READ_WRITE')
    self.assertEqual(exceptions, [])

  def testAddInstanceWithBootDiskOptionsGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'myproject'

    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    service_version = 'v1'
    expected_instance = 'test_instance'
    submitted_boot_disk_unqualified = 'diskA,boot'
    submitted_boot_disk_ro = 'diskB,mode=ro,boot'
    submitted_boot_disk_rw = 'diskC,mode=rw,boot'
    submitted_non_boot_disk = 'diskD'
    submitted_machine_type = 'goes_to_11'

    expected_authorized_ssh_keys = []
    flag_values.service_version = service_version

    flag_values.disk = [submitted_boot_disk_unqualified,
                        submitted_boot_disk_ro,
                        submitted_boot_disk_rw,
                        submitted_non_boot_disk]
    flag_values.machine_type = submitted_machine_type
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = expected_authorized_ssh_keys
    flag_values.add_compute_key_to_project = False

    self._instances.list = old_mock_api.CommandExecutor(self._instance_list)

    # When no zone is provided, GCUtil will do a list
    disk_zone = 'zone1'

    # Override to return a single zone so that we don't find multiple
    # disks with the same name
    self._zones.list = old_mock_api.CommandExecutor(
        {'kind': 'compute#zoneList',
         'items': [{'name': 'zone1'}]})

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.disks = self._disks
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    (results, exceptions) = command.Handle(expected_instance)
    result = results['items'][0]

    disk = result['body']['disks'][0]
    self.assertEqual(disk['deviceName'], 'diskA')
    self.assertEqual(disk['mode'], 'READ_WRITE')
    self.assertEqual(disk['boot'], True)

    disk = result['body']['disks'][1]
    self.assertEqual(disk['deviceName'], 'diskB')
    self.assertEqual(disk['mode'], 'READ_ONLY')
    self.assertEqual(disk['boot'], True)

    disk = result['body']['disks'][2]
    self.assertEqual(disk['deviceName'], 'diskC')
    self.assertEqual(disk['mode'], 'READ_WRITE')
    self.assertEqual(disk['boot'], True)

    disk = result['body']['disks'][3]
    self.assertEqual(disk['deviceName'], 'diskD')
    self.assertEqual(disk['mode'], 'READ_WRITE')
    self.assertEqual(disk['boot'], False)
    self.assertEqual(exceptions, [])

    self.assertEqual(disk_zone, result['zone'])

  def testPersistentBootDisk(self):
    flag_values = copy.deepcopy(FLAGS)

    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    service_version = 'v1'
    expected_instance = 'test_instance'
    submitted_machine_type = 'machine-type1'
    submitted_zone = 'zone1'
    submitted_image = 'projects/google/global/images/some-image'
    submitted_project = 'test_project_name'

    expected_authorized_ssh_keys = []
    flag_values.service_version = service_version
    flag_values.project = submitted_project
    flag_values.machine_type = submitted_machine_type
    flag_values.zone = submitted_zone
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = expected_authorized_ssh_keys
    flag_values.add_compute_key_to_project = False
    flag_values.image = submitted_image

    self._images.get = old_mock_api.CommandExecutor({})
    self._instances.list = old_mock_api.CommandExecutor(self._instance_list)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.disks = self._disks
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    (results, exceptions) = command.Handle(expected_instance)
    result = results['items'][0]

    # Make sure the auto-created boot disk was attached to the instance.
    disk = result['body']['disks'][0]
    self.assertEqual(disk['deviceName'],
                     command._GetDefaultBootDiskName(expected_instance))
    self.assertEqual(disk['mode'], 'READ_WRITE')
    self.assertEqual(disk['boot'], True)
    self.assertEqual(exceptions, [])

    # Make sure image was not set.
    self.assertFalse('image' in result['body'])

  def testAddInstanceWithDiskGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)

    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    service_version = command_base.CURRENT_VERSION

    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_description = 'test instance'
    submitted_image = 'expected_image'
    submitted_disk = 'disk123'
    submitted_machine_type = 'goes_to_11'
    submitted_zone = 'copernicus-moon-base'

    expected_authorized_ssh_keys = []
    flag_values.service_version = service_version
    flag_values.disk = [submitted_disk]
    flag_values.project = expected_project
    flag_values.description = expected_description
    flag_values.image = submitted_image
    flag_values.machine_type = submitted_machine_type
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = expected_authorized_ssh_keys
    flag_values.add_compute_key_to_project = False

    self._instances.list = old_mock_api.CommandExecutor(self._instance_list)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.disks = self._disks
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    selfLink = (
        'https://www.googleapis.com/compute/%s/projects/%s/zones/%s/disks/%s' %
        (service_version, expected_project, submitted_zone, submitted_disk))

    self._disks.list = old_mock_api.CommandExecutor(
        {
            'items': [{
                'name': submitted_disk,
                'zone': submitted_zone,
                'selfLink': selfLink
                }]
        })

    self._zones.list = old_mock_api.CommandExecutor(
        {'kind': 'compute#zoneList',
         'items': [{'name': submitted_zone}]})

    expected_metadata = {'kind': 'compute#metadata',
                         'items': []}

    expected_image = command.NormalizeGlobalResourceName(expected_project,
                                                         'images',
                                                         submitted_image)

    expected_disk = command.NormalizePerZoneResourceName(expected_project,
                                                         submitted_zone,
                                                         'disks',
                                                         submitted_disk)

    (results, exceptions) = command.Handle(expected_instance)
    result = results['items'][0]

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['body']['name'], expected_instance)
    self.assertEqual(result['body']['description'], expected_description)
    self.assertEqual(
        result['body']['disks'][0]['deviceName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['diskName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['sourceImage'],
        expected_image)
    self.assertEqual(result['body']['disks'][1]['source'], expected_disk)
    self.assertFalse(
        'natIP' in result['body']['networkInterfaces'][0]['accessConfigs'][0],
        result)
    self.assertEqual(result['body'].get('metadata', {}), expected_metadata)
    instance_tags = result['body'].get('tags', {}).get('items', [])
    self.assertEqual(submitted_zone, result['zone'])
    self.assertFalse('zone' in result['body'])
    self.assertEqual(instance_tags, [])
    self.assertEqual(exceptions, [])

  def testAddInstanceGeneratesEphemeralIpRequestForProjectWithNoIps(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    service_version = command_base.CURRENT_VERSION
    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_description = 'test instance'
    submitted_image = 'expected_image'
    submitted_machine_type = 'goes_to_11'
    submitted_zone = 'copernicus-moon-base'

    expected_authorized_ssh_keys = []
    flag_values.service_version = service_version
    flag_values.zone = submitted_zone
    flag_values.project = expected_project
    flag_values.description = expected_description
    flag_values.image = submitted_image
    flag_values.machine_type = submitted_machine_type
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = expected_authorized_ssh_keys
    flag_values.add_compute_key_to_project = False

    self._projects.get = old_mock_api.CommandExecutor(
        {'externalIpAddresses': []})
    self._instances.list = old_mock_api.CommandExecutor({'items': []})

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    expected_metadata = {'kind': 'compute#metadata',
                         'items': []}

    expected_image = command.NormalizeGlobalResourceName(expected_project,
                                                         'images',
                                                         submitted_image)

    (results, exceptions) = command.Handle(expected_instance)
    result = results['items'][0]

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['body']['name'], expected_instance)
    self.assertEqual(result['body']['description'], expected_description)
    self.assertEqual(
        result['body']['disks'][0]['deviceName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['diskName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['sourceImage'],
        expected_image)
    self.assertFalse('natIP' in
                     result['body']['networkInterfaces'][0]['accessConfigs'][0],
                     result)
    self.assertEqual(result['body'].get('metadata'), expected_metadata)

    instance_tags = result['body'].get('tags', {}).get('items', [])
    self.assertEqual(submitted_zone, result['zone'])
    self.assertFalse('zone' in result['body'])
    self.assertEqual(instance_tags, [])
    self.assertEqual(exceptions, [])

  def testAddInstanceNoExistingVmsRequest(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    service_version = command_base.CURRENT_VERSION
    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_description = 'test instance'
    submitted_image = 'expected_image'
    submitted_machine_type = 'goes_to_11'
    submitted_zone = 'copernicus-moon-base'

    expected_authorized_ssh_keys = []
    flag_values.service_version = service_version
    flag_values.zone = submitted_zone
    flag_values.project = expected_project
    flag_values.description = expected_description
    flag_values.image = submitted_image
    flag_values.machine_type = submitted_machine_type
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = expected_authorized_ssh_keys
    flag_values.add_compute_key_to_project = False

    self._projects.get = old_mock_api.CommandExecutor(
        {'externalIpAddresses': ['192.0.2.2', '192.0.2.3']})
    self._instances.list = old_mock_api.CommandExecutor(
        {'kind': 'cloud#instances'})

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    expected_metadata = {'kind': 'compute#metadata',
                         'items': []}

    expected_image = command.NormalizeGlobalResourceName(expected_project,
                                                         'images',
                                                         submitted_image)

    (results, exceptions) = command.Handle(expected_instance)
    result = results['items'][0]

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['body']['name'], expected_instance)
    self.assertEqual(result['body']['description'], expected_description)
    self.assertEqual(
        result['body']['disks'][0]['deviceName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['diskName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['sourceImage'],
        expected_image)

    self.assertFalse(
        'natIP' in result['body']['networkInterfaces'][0]['accessConfigs'][0],
        result)
    instance_tags = result['body'].get('tags', {}).get('items', [])
    self.assertEqual(submitted_zone, result['zone'])
    self.assertFalse('zone' in result['body'])
    self.assertEqual(result['body'].get('metadata'), expected_metadata)
    self.assertEqual(instance_tags, [])
    self.assertEqual(exceptions, [])

  def testAddInstanceWithSpecifiedInternalAddress(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    service_version = command_base.CURRENT_VERSION
    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_description = 'test instance'
    submitted_image = 'expected_image'
    submitted_machine_type = 'goes_to_11'
    submitted_zone = 'copernicus-moon-base'

    expected_authorized_ssh_keys = []
    flag_values.service_version = service_version
    flag_values.zone = submitted_zone
    flag_values.project = expected_project
    flag_values.description = expected_description
    flag_values.image = submitted_image
    flag_values.machine_type = submitted_machine_type
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = expected_authorized_ssh_keys
    flag_values.add_compute_key_to_project = False

    self._instances.list = old_mock_api.CommandExecutor(self._instance_list)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    expected_metadata = {'kind': 'compute#metadata',
                         'items': []}

    expected_image = command.NormalizeGlobalResourceName(expected_project,
                                                         'images',
                                                         submitted_image)

    (results, exceptions) = command.Handle(expected_instance)
    result = results['items'][0]

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['body']['name'], expected_instance)
    self.assertEqual(result['body']['description'], expected_description)
    self.assertEqual(
        result['body']['disks'][0]['deviceName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['diskName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['sourceImage'],
        expected_image)
    self.assertTrue('networkIP' not in result['body']['networkInterfaces'][0])
    instance_tags = result['body'].get('tags', {}).get('items', [])
    self.assertEqual(submitted_zone, result['zone'])
    self.assertFalse('zone' in result['body'])
    self.assertEqual(result['body'].get('metadata'), expected_metadata)
    self.assertEqual(instance_tags, [])
    self.assertEqual(exceptions, [])

  def testAddInstanceGeneratesNewIpRequest(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    service_version = command_base.CURRENT_VERSION
    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_description = 'test instance'
    submitted_image = 'expected_image'
    submitted_machine_type = 'goes_to_11'
    submitted_zone = 'copernicus-moon-base'

    expected_authorized_ssh_keys = []
    flag_values.service_version = service_version
    flag_values.zone = submitted_zone
    flag_values.project = expected_project
    flag_values.description = expected_description
    flag_values.image = submitted_image
    flag_values.external_ip_address = 'ephemeral'
    flag_values.machine_type = submitted_machine_type
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = expected_authorized_ssh_keys
    flag_values.add_compute_key_to_project = False

    self._instances.list = old_mock_api.CommandExecutor(self._instance_list)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    expected_metadata = {'kind': 'compute#metadata',
                         'items': []}

    expected_image = command.NormalizeGlobalResourceName(expected_project,
                                                         'images',
                                                         submitted_image)

    (results, exceptions) = command.Handle(expected_instance)
    result = results['items'][0]

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['body']['name'], expected_instance)
    self.assertEqual(result['body']['description'], expected_description)
    self.assertEqual(
        result['body']['disks'][0]['deviceName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['diskName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['sourceImage'],
        expected_image)
    self.assertFalse('natIP' in
                     result['body']['networkInterfaces'][0]['accessConfigs'][0])
    instance_tags = result['body'].get('tags', {}).get('items', [])
    self.assertEqual(submitted_zone, result['zone'])
    self.assertFalse('zone' in result['body'])
    self.assertEqual(result['body'].get('metadata'), expected_metadata)
    self.assertEqual(instance_tags, [])
    self.assertEqual(exceptions, [])

  def testAddInstanceGeneratesNoExternalIpRequest(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    service_version = command_base.CURRENT_VERSION
    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_description = 'test instance'
    submitted_image = 'expected_image'
    submitted_machine_type = 'goes_to_11'
    submitted_zone = 'copernicus-moon-base'

    expected_authorized_ssh_keys = []
    flag_values.service_version = service_version
    flag_values.zone = submitted_zone
    flag_values.project = expected_project
    flag_values.description = expected_description
    flag_values.image = submitted_image
    flag_values.external_ip_address = 'None'
    flag_values.machine_type = submitted_machine_type
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = expected_authorized_ssh_keys
    flag_values.add_compute_key_to_project = False

    self._instances.list = old_mock_api.CommandExecutor(self._instance_list)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    expected_metadata = {'kind': 'compute#metadata',
                         'items': []}

    expected_image = command.NormalizeGlobalResourceName(expected_project,
                                                         'images',
                                                         submitted_image)

    (results, exceptions) = command.Handle(expected_instance)
    result = results['items'][0]

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['body']['name'], expected_instance)
    self.assertEqual(result['body']['description'], expected_description)
    self.assertEqual(
        result['body']['disks'][0]['deviceName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['diskName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['sourceImage'],
        expected_image)
    self.assertFalse('accessConfigs' in result['body']['networkInterfaces'][0])
    instance_tags = result['body'].get('tags', {}).get('items', [])
    self.assertEqual(submitted_zone, result['zone'])
    self.assertFalse('zone' in result['body'])
    self.assertEqual(result['body'].get('metadata'), expected_metadata)
    self.assertEqual(instance_tags, [])
    self.assertEqual(exceptions, [])

  def testAddInstanceRequiresZone(self):
    flag_values = copy.deepcopy(FLAGS)

    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    service_version = command_base.CURRENT_VERSION
    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_description = 'test instance'
    submitted_image = 'expected_image'
    submitted_machine_type = 'goes_to_11'
    submitted_zone = 'us-east-a'
    expected_authorized_ssh_keys = []
    flag_values.service_version = service_version
    flag_values.project = expected_project
    flag_values.description = expected_description
    flag_values.image = submitted_image
    flag_values.machine_type = submitted_machine_type
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = expected_authorized_ssh_keys
    flag_values.add_compute_key_to_project = False
    flag_values.require_tty = False

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command._credential = old_mock_api.MockCredential()

    with gcutil_unittest.CaptureStandardIO('1\n\r'):

      def GetZonePath(part_one, part_two, part_three):
        return '%s-%s-%s' % (part_one, part_two, part_three)

      self._instances.list = old_mock_api.CommandExecutor(self._instance_list)
      self._zones.list = old_mock_api.CommandExecutor(
          {'items': [
              {'name': GetZonePath('us', 'east', 'a')},
              {'name': GetZonePath('us', 'east', 'b')},
              {'name': GetZonePath('us', 'east', 'c')},
              {'name': GetZonePath('us', 'west', 'a')}]})

      command.api.projects = self._projects
      command.api.images = self._images
      command.api.instances = self._instances
      command.api.zones = self._zones

      (results, exceptions) = command.Handle(expected_instance)
      result = results['items'][0]

      self.assertEqual(submitted_zone, result['zone'])
      self.assertFalse('zone' in result['body'])
      self.assertEqual(exceptions, [])

  def _DoTestAddInstanceWithServiceAccounts(self,
                                            expected_service_account,
                                            expected_scopes,
                                            should_succeed):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_description = 'test instance'
    submitted_image = 'expected_image'
    service_version = 'v1'
    submitted_machine_type = 'goes_to_11'
    submitted_zone = 'copernicus-moon-base'
    expected_authorized_ssh_keys = []
    flag_values.service_version = service_version
    flag_values.zone = submitted_zone
    flag_values.project = expected_project
    flag_values.description = expected_description
    flag_values.image = submitted_image
    flag_values.external_ip_address = 'None'
    flag_values.machine_type = submitted_machine_type
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = expected_authorized_ssh_keys
    if expected_service_account:
      # addinstance command checks whether --service_account is explicitly
      # given, so in this case, set the present flag along with the value.
      flag_values['service_account'].present = True
      flag_values.service_account = expected_service_account
    else:
      # The default 'default' will be expected after command.Handle.
      expected_service_account = 'default'
    if expected_scopes:
      flag_values.service_account_scopes = expected_scopes
    else:
      # The default [] will be expected after command.Handle.
      expected_scopes = []
    flag_values.add_compute_key_to_project = False

    self._instances.list = old_mock_api.CommandExecutor(self._instance_list)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    expected_metadata = {'kind': 'compute#metadata',
                         'items': []}

    expected_image = command.NormalizeGlobalResourceName(expected_project,
                                                         'images',
                                                         submitted_image)

    if not should_succeed:
      self.assertRaises(app.UsageError,
                        command.Handle,
                        expected_instance)
    else:
      (results, exceptions) = command.Handle(expected_instance)
      result = results['items'][0]

      self.assertEqual(result['project'], expected_project)
      self.assertEqual(result['body']['name'], expected_instance)
      self.assertEqual(result['body']['description'], expected_description)
      self.assertEqual(
          result['body']['disks'][0]['deviceName'],
          expected_instance)
      self.assertEqual(
          result['body']['disks'][0]['initializeParams']['diskName'],
          expected_instance)
      self.assertEqual(
          result['body']['disks'][0]['initializeParams']['sourceImage'],
          expected_image)
      self.assertFalse('accessConfigs' in
                       result['body']['networkInterfaces'][0])
      self.assertEqual(result['body'].get('metadata'), expected_metadata)
      instance_tags = result['body'].get('tags', {}).get('items', [])
      self.assertEqual(submitted_zone, result['zone'])
      self.assertFalse('zone' in result['body'])
      self.assertEqual(instance_tags, [])
      self.assertEqual(result['body']['serviceAccounts'][0]['email'],
                       expected_service_account)
      self.assertEqual(result['body']['serviceAccounts'][0]['scopes'],
                       sorted(expected_scopes))
      self.assertEqual(exceptions, [])

  def testAddInstanceWithServiceAccounts(self):
    email = 'random.default@developer.googleusercontent.com'
    scope1 = 'https://www.googleapis.com/auth/fake.product1'
    scope2 = 'https://www.googleapis.com/auth/fake.product2'

    self._DoTestAddInstanceWithServiceAccounts(None, [scope1], True)
    self._DoTestAddInstanceWithServiceAccounts(email, [scope1], True)
    self._DoTestAddInstanceWithServiceAccounts(email, [scope1, scope2], True)
    self._DoTestAddInstanceWithServiceAccounts(email, None, False)

  def testAddInstanceWithUnknownKeyFile(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    submitted_machine_type = 'goes_to_11'
    submitted_zone = 'copernicus-moon-base'
    expected_instance = 'test_instance'
    flag_values.project = 'test_project'
    flag_values.zone = submitted_zone
    flag_values.description = 'test instance'
    flag_values.image = 'expected_image'
    flag_values.machine_type = submitted_machine_type
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = ['user:unknown-file']
    flag_values.add_compute_key_to_project = False

    self._instances.list = old_mock_api.CommandExecutor(self._instance_list)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    self.assertRaises(IOError,
                      command.Handle,
                      expected_instance)

  def testAddAuthorizedUserKeyToProject(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.service_version = 'v1'
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    class SetCommonInstanceMetadata(object):

      def __init__(self, record):
        self.record = record

      def __call__(self, project, body):
        self.record['project'] = project
        self.record['body'] = body
        return self

      def execute(self):
        pass

    ssh_keys = ''
    self._projects.get = old_mock_api.CommandExecutor(
        {'commonInstanceMetadata': {
            'kind': 'compute#metadata',
            'items': [{'key': 'sshKeys', 'value': ssh_keys}]}})
    call_record = {}
    self._projects.setCommonInstanceMetadata = SetCommonInstanceMetadata(
        call_record)
    expected_project = 'test_project'

    flag_values.service_version = 'v1'
    flag_values.project = expected_project
    command.SetApi(old_mock_api.CreateMockApi())
    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command._credential = old_mock_api.MockCredential()

    result = command._AddAuthorizedUserKeyToProject(
        {'user': 'foo', 'key': 'bar'})
    self.assertTrue(result)
    self.assertEquals(expected_project, call_record['project'])
    self.assertEquals(
        {'kind': 'compute#metadata',
         'items': [{'key': 'sshKeys', 'value': 'foo:bar'}]},
        call_record['body'])

  def testAddAuthorizedUserKeyAlreadyInProject(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.service_version = 'v1'
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    class SetCommonInstanceMetadata(object):

      def __init__(self, record):
        self.record = record

      def __call__(self, project, body):
        self.record['project'] = project
        self.record['body'] = body
        return self

      def execute(self):
        pass

    ssh_keys = 'baz:bat\nfoo:bar\ni:j'
    self._projects.get = old_mock_api.CommandExecutor(
        {'commonInstanceMetadata': {
            'kind': 'compute#metadata',
            'items': [{'key': 'sshKeys', 'value': ssh_keys}]}})
    call_record = {}
    self._projects.setCommonInstanceMetadata = SetCommonInstanceMetadata(
        call_record)
    expected_project = 'test_project'

    flag_values.service_version = 'v1'
    flag_values.project = expected_project
    command.SetApi(old_mock_api.CreateMockApi())
    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command._credential = old_mock_api.MockCredential()

    result = command._AddAuthorizedUserKeyToProject(
        {'user': 'foo', 'key': 'bar'})
    self.assertFalse(result)

  def _testAddSshKeysToMetadataHelper(self,
                                      test_ssh_key_through_file,
                                      test_ssh_key_through_flags):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    flag_values.use_compute_key = False
    ssh_rsa_key = ('ssh-rsa ' +
                   base64.b64encode('\00\00\00\07ssh-rsa the ssh key') +
                   ' comment')

    metadata_handle, metadata_path = tempfile.mkstemp()
    ssh_key_handle, ssh_key_path = tempfile.mkstemp()
    metadata_file = os.fdopen(metadata_handle, 'w')
    ssh_key_file = os.fdopen(ssh_key_handle, 'w')

    try:
      metadata_file.write('metadata file content')
      metadata_file.flush()
      flag_values.metadata_from_file = ['bar_file:%s' % metadata_path]

      flag_values.metadata = ['bar:baz']

      if test_ssh_key_through_file:
        ssh_key_file.write(ssh_rsa_key)
        ssh_key_file.flush()
        flag_values.authorized_ssh_keys = ['user:%s' % ssh_key_path]

      if test_ssh_key_through_flags:
        flag_values.metadata.append('sshKeys:user2:flags ssh key')

      command.SetFlags(flag_values)
      command._InitializeContextParser()
      metadata_flags_processor = command._metadata_flags_processor
      extended_metadata = command._AddSshKeysToMetadata(
          metadata_flags_processor.GatherMetadata())
    finally:
      metadata_file.close()
      ssh_key_file.close()
      os.remove(metadata_path)
      os.remove(ssh_key_path)

    self.assertTrue(len(extended_metadata) >= 2)
    self.assertEqual(extended_metadata[0]['key'], 'bar')
    self.assertEqual(extended_metadata[0]['value'], 'baz')
    self.assertEqual(extended_metadata[1]['key'], 'bar_file')
    self.assertEqual(extended_metadata[1]['value'], 'metadata file content')

    ssh_keys = []
    if test_ssh_key_through_flags:
      ssh_keys.append('user2:flags ssh key')
    if test_ssh_key_through_file:
      ssh_keys.append('user:' + ssh_rsa_key)

    if test_ssh_key_through_flags or test_ssh_key_through_file:
      self.assertEqual(len(extended_metadata), 3)
      self.assertEqual(extended_metadata[2]['key'], 'sshKeys')
      self.assertEqual(extended_metadata[2]['value'],
                       '\n'.join(ssh_keys))

  def testGatherMetadata(self):
    self._testAddSshKeysToMetadataHelper(False, False)
    self._testAddSshKeysToMetadataHelper(False, True)
    self._testAddSshKeysToMetadataHelper(True, False)
    self._testAddSshKeysToMetadataHelper(True, True)

  def testBuildInstanceRequestWithMetadataAndDisk(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project = 'test_project'
    expected_description = 'test instance'
    expected_instance = 'test_instance'
    submitted_image = 'expected_image'
    submitted_zone = 'copernicus-moon-base'
    expected_context = {
        'instance': expected_instance,
        'project': expected_project,
        'zone': submitted_zone
    }
    flag_values.service_version = 'v1'
    flag_values.project = expected_project
    flag_values.zone = submitted_zone
    flag_values.description = expected_description
    flag_values.image = submitted_image
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = []
    flag_values.add_compute_key_to_project = False
    metadata = [{'key': 'foo', 'value': 'bar'}]
    disks = [{'source': ('https://www.googleapis.com/compute/v1/projects/'
                         'google.com:test/disks/disk789'),
              'deviceName': 'disk789', 'mode': 'READ_WRITE',
              'type': 'PERSISTENT', 'boot': False}]

    expected_metadata = {'kind': 'compute#metadata',
                         'items': metadata}

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())

    result = command._BuildRequestWithMetadata(
        expected_context, metadata, disks).execute()

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['body']['name'], expected_instance)
    self.assertEqual(result['body']['description'], expected_description)
    self.assertEqual(result['body']['metadata'], expected_metadata)
    self.assertEqual(result['body']['disks'], disks)

  def testBuildInstanceRequestWithTag(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    service_version = 'v1'
    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_description = 'test instance'
    submitted_image = 'expected_image'
    submitted_machine_type = 'goes_to_11'
    submitted_zone = 'copernicus-moon-base'
    expected_tags = ['tag0', 'tag1', 'tag2']

    flag_values.service_version = service_version
    flag_values.project = expected_project
    flag_values.zone = submitted_zone
    flag_values.description = expected_description
    flag_values.image = submitted_image
    flag_values.machine_type = submitted_machine_type
    flag_values.use_compute_key = False
    flag_values.authorized_ssh_keys = []
    flag_values.tags = expected_tags * 2  # Create duplicates.
    flag_values.add_compute_key_to_project = False

    self._instances.list = old_mock_api.CommandExecutor(self._instance_list)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.projects = self._projects
    command.api.images = self._images
    command.api.instances = self._instances
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    expected_metadata = {'kind': 'compute#metadata',
                         'items': []}

    expected_image = command.NormalizeGlobalResourceName(expected_project,
                                                         'images',
                                                         submitted_image)

    (results, exceptions) = command.Handle(expected_instance)
    result = results['items'][0]

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['body']['name'], expected_instance)
    self.assertEqual(result['body']['description'], expected_description)
    self.assertEqual(
        result['body']['disks'][0]['deviceName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['diskName'],
        expected_instance)
    self.assertEqual(
        result['body']['disks'][0]['initializeParams']['sourceImage'],
        expected_image)
    self.assertFalse(
        'natIP' in result['body']['networkInterfaces'][0]['accessConfigs'][0],
        result)
    self.assertEqual(result['body'].get('metadata'), expected_metadata)
    instance_tags = result['body'].get('tags', {}).get('items', [])
    self.assertEqual(submitted_zone, result['zone'])
    self.assertFalse('zone' in result['body'])
    self.assertEqual(instance_tags, expected_tags)
    self.assertEqual(exceptions, [])

  def testGetInstanceGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.GetInstance('getinstance', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project = 'test_project'
    expected_instance = 'test_instance'
    flag_values.project = expected_project
    flag_values.zone = 'zone-a'

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command._credential = old_mock_api.MockCredential()

    result = command.Handle(expected_instance)

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['instance'], expected_instance)

  def _DoTestAddAccessConfigGeneratesCorrectRequest(self, service_version):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AddAccessConfig('addaccessconfig', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project_name = 'test_project_name'
    expected_instance_name = 'test_instance_name'
    expected_network_interface_name = 'test_network_interface_name'
    expected_access_config_name = 'test_access_config_name'
    expected_access_config_type = 'test_access_config_type'
    expected_access_config_nat_ip = 'test_access_config_nat_ip'

    flag_values.project = expected_project_name
    flag_values.network_interface_name = expected_network_interface_name
    flag_values.access_config_name = expected_access_config_name
    flag_values.access_config_type = expected_access_config_type
    flag_values.access_config_nat_ip = expected_access_config_nat_ip
    flag_values.service_version = service_version
    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command._credential = old_mock_api.MockCredential()
    submitted_zone = 'copernicus-moon-base'
    flag_values.zone = submitted_zone

    result = command.Handle(expected_instance_name)

    self.assertEqual(result['project'], expected_project_name)
    self.assertEqual(result['instance'], expected_instance_name)
    network_interface = 'networkInterface'
    self.assertEqual(result[network_interface], expected_network_interface_name)
    self.assertEqual(result['body']['name'], expected_access_config_name)
    self.assertEqual(result['body']['type'], expected_access_config_type)
    self.assertEqual(result['body']['natIP'], expected_access_config_nat_ip)
    self.assertEqual(submitted_zone, result['zone'])

  def testAddAccessConfigGeneratesCorrectRequest(self):
    for ver in command_base.SUPPORTED_VERSIONS:
      self._DoTestAddAccessConfigGeneratesCorrectRequest(ver)

  def _DoTestDeleteAccessConfigGeneratesCorrectRequest(self, service_version):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.DeleteAccessConfig('deleteaccessconfig',
                                               flag_values)
    self._DoNotPauseForCommand(command)

    expected_project_name = 'test_project_name'
    expected_instance_name = 'test_instance_name'
    expected_network_interface_name = 'test_network_interface_name'
    expected_access_config_name = 'test_access_config_name'

    flag_values.project = expected_project_name
    flag_values.network_interface_name = expected_network_interface_name
    flag_values.access_config_name = expected_access_config_name
    flag_values.service_version = service_version
    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()
    submitted_zone = 'copernicus-moon-base'
    flag_values.zone = submitted_zone

    result = command.Handle(expected_instance_name)

    self.assertEqual(result['project'], expected_project_name)
    self.assertEqual(result['instance'], expected_instance_name)

    network_interface = 'networkInterface'
    access_config = 'accessConfig'

    self.assertEqual(result[network_interface], expected_network_interface_name)
    self.assertEqual(result[access_config], expected_access_config_name)
    self.assertEqual(submitted_zone, result['zone'])

  def testDeleteAccessConfigGeneratesCorrectRequest(self):
    for ver in command_base.SUPPORTED_VERSIONS:
      self._DoTestDeleteAccessConfigGeneratesCorrectRequest(ver)

  def testSetInstanceMetadataGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SetMetadata('setinstancemetadata', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_fingerprint = 'asdfg'
    submitted_zone = 'zone-a'
    flag_values.project = expected_project
    flag_values.fingerprint = expected_fingerprint
    flag_values.zone = submitted_zone

    handle, path = tempfile.mkstemp()
    metadata_file = os.fdopen(handle, 'w')
    try:
      metadata_file.write('foo:bar')
      metadata_file.flush()
      flag_values.metadata_from_file = ['sshKeys:%s' % path]

      command.SetFlags(flag_values)
      command._InitializeContextParser()
      command.SetApi(old_mock_api.CreateMockApi())
      command.api.instances.get = old_mock_api.CommandExecutor(
          {'metadata': {'kind': 'compute#metadata',
                        'items': [{'key': 'sshKeys', 'value': ''}]}})
      command.api.projects.get = old_mock_api.CommandExecutor(
          {'commonInstanceMetadata': {'kind': 'compute#metadata',
                                      'items': [{'key': 'sshKeys',
                                                 'value': ''}]}})
      command.api.zones = self._zones

      result = command.Handle(expected_instance)
      self.assertEquals(expected_project, result['project'])
      self.assertEquals(expected_instance, result['instance'])
      self.assertEquals(
          {'kind': 'compute#metadata',
           'fingerprint': expected_fingerprint,
           'items': [{'key': 'sshKeys', 'value': 'foo:bar'}]},
          result['body'])
    finally:
      metadata_file.close()
      os.remove(path)

  def testSetMetadataChecksSshKeys(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SetMetadata(
        'setinstancemetadata', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_zone = 'danger_zone'
    expected_fingerprint = 'asdfg'
    flag_values.project = expected_project
    flag_values.zone = expected_zone
    flag_values.fingerprint = expected_fingerprint

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.instances.get = old_mock_api.CommandExecutor(
        {'metadata': {'kind': 'compute#metadata',
                      'items': [{'key': 'sshKeys', 'value': 'xyz'}]}})
    command.api.projects.get = old_mock_api.CommandExecutor(
        {'commonInstanceMetadata': {'kind': 'compute#metadata',
                                    'items': [{'key': 'noSshKey',
                                               'value': 'none'}]}})
    command.api.zones = self._zones

    self.assertRaises(gcutil_errors.CommandError,
                      command.Handle, expected_instance)

  def testSetMetadataFailsWithNofingerprint(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SetMetadata('setinstancemetadata', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project = 'test_project'
    expected_instance = 'test_instance'
    submitted_zone = 'zone-a'
    flag_values.project = expected_project
    flag_values.zone = submitted_zone

    with tempfile.NamedTemporaryFile() as metadata_file:
      metadata_file.write('foo:bar')
      metadata_file.flush()
      flag_values.metadata_from_file = ['sshKeys:%s' % metadata_file.name]

      command.SetFlags(flag_values)
      command._InitializeContextParser()
      command.SetApi(old_mock_api.CreateMockApi())
      command.api.instances.get = old_mock_api.CommandExecutor(
          {'metadata': {'kind': 'compute#metadata',
                        'items': [{'key': 'sshKeys', 'value': ''}]}})
      command.api.projects.get = old_mock_api.CommandExecutor(
          {'commonInstanceMetadata': {'kind': 'compute#metadata',
                                      'items': [{'key': 'sshKeys',
                                                 'value': ''}]}})
      command.api.zones = self._zones
      self.assertRaises(app.UsageError, command.Handle, expected_instance)

  def testSetTagsGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SetTags('settags', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_fingerprint = 'test-hash'
    expected_tags = ['tag0', 'tag1', 'tag2']
    submitted_zone = 'zone-a'
    flag_values.project = expected_project
    flag_values.fingerprint = expected_fingerprint
    flag_values.tags = expected_tags
    flag_values.zone = submitted_zone

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.zones = self._zones

    result = command.Handle(expected_instance)

    self.assertEqual(result['instance'], expected_instance)
    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['body'].get('fingerprint'), expected_fingerprint)
    self.assertEqual(result['body'].get('items'), expected_tags)

  def testSetTagsFailsWithNoFingerprint(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SetTags('settags', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project = 'test_project'
    expected_instance = 'test_instance'
    expected_tags = ['tag0', 'tag1', 'tag2']
    submitted_zone = 'zone-a'
    flag_values.project = expected_project
    flag_values.tags = expected_tags
    flag_values.zone = submitted_zone

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.zones = self._zones

    self.assertRaises(app.UsageError, command.Handle, expected_instance)

  def testAttachDiskGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AttachDisk('attachdisk', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project_name = 'test_project_name'
    expected_instance_name = 'test_instance_name'

    expected_disk_names = ['disk1', 'disk2']
    expected_disk_device_names = ['diskOne', 'diskTwo']
    expected_disk_modes = ['READ_ONLY', 'READ_WRITE']

    submitted_zone = 'copernicus-moon-base'

    submitted_disks = []
    for (expected_disk_name, expected_disk_device_name,
         expected_disk_mode) in zip(expected_disk_names,
                                    expected_disk_device_names,
                                    expected_disk_modes):
      submitted_disks.append('%s,deviceName=%s,mode=%s' %
                             (expected_disk_name,
                              expected_disk_device_name,
                              expected_disk_mode))

    flag_values.project = expected_project_name
    flag_values.disk = submitted_disks
    flag_values.zone = submitted_zone
    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command.api.zones = self._zones
    command._credential = old_mock_api.MockCredential()

    results, _ = command.Handle(expected_instance_name)

    expected_disks = []
    for expected_disk_name in expected_disk_names:
      expected_disks.append(
          command.NormalizePerZoneResourceName(
              expected_project_name,
              submitted_zone,
              'disks',
              expected_disk_name))

    for (result, expected_disk, expected_disk_mode,
         expected_disk_device_name) in zip(results, expected_disks,
                                           expected_disk_modes,
                                           expected_disk_device_names):
      self.assertEqual(result['project'], expected_project_name)
      self.assertEqual(result['instance'], expected_instance_name)
      self.assertEqual(result['body']['type'], 'PERSISTENT')
      self.assertEqual(result['body']['source'], expected_disk)
      self.assertEqual(result['body']['mode'], expected_disk_mode)
      self.assertEqual(result['body']['deviceName'], expected_disk_device_name)

  def testDetachDiskGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.DetachDisk('detachdisk', flag_values)
    self._DoNotPauseForCommand(command)

    submitted_zone = 'zone-a'
    expected_project_name = 'test_project_name'
    expected_instance_name = 'test_instance_name'
    expected_device_name = 'diskOne'

    flag_values.project = expected_project_name
    flag_values.device_name = [expected_device_name]
    flag_values.zone = submitted_zone
    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())
    command._credential = old_mock_api.MockCredential()

    results, _ = command.Handle(expected_instance_name)

    result = results[0]

    self.assertEqual(result['project'], expected_project_name)
    self.assertEqual(result['instance'], expected_instance_name)
    self.assertEqual(result['deviceName'], expected_device_name)

  def testGetSshAddressChecksForNetworkInterfaces(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SshInstanceBase('test', flag_values)
    self._DoNotPauseForCommand(command)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    mock_instance = {'someFieldOtherThanNetworkInterfaces': [],
                     'status': 'RUNNING'}

    self.assertRaises(gcutil_errors.CommandError,
                      command._GetSshAddress,
                      mock_instance)

  def testGetSshAddressChecksForNonEmptyNetworkInterfaces(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SshInstanceBase('test', flag_values)
    self._DoNotPauseForCommand(command)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    mock_instance = {'networkInterfaces': [], 'status': 'RUNNING'}

    self.assertRaises(gcutil_errors.CommandError,
                      command._GetSshAddress,
                      mock_instance)

  def testGetSshAddressChecksForAccessConfigs(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SshInstanceBase('test', flag_values)
    self._DoNotPauseForCommand(command)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    mock_instance = {'networkInterfaces': [{}]}

    self.assertRaises(gcutil_errors.CommandError,
                      command._GetSshAddress,
                      mock_instance)

  def testGetSshAddressChecksForNonEmptyAccessConfigs(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SshInstanceBase('test', flag_values)
    self._DoNotPauseForCommand(command)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    mock_instance = {'networkInterfaces': [{'accessConfigs': []}],
                     'status': 'RUNNING'}

    self.assertRaises(gcutil_errors.CommandError,
                      command._GetSshAddress,
                      mock_instance)

  def testGetSshAddressChecksForNatIp(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SshInstanceBase('test', flag_values)
    self._DoNotPauseForCommand(command)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    mock_instance = {'networkInterfaces': [{'accessConfigs': [{}]}],
                     'status': 'RUNNING'}

    self.assertRaises(gcutil_errors.CommandError,
                      command._GetSshAddress,
                      mock_instance)

  def testEnsureSshableChecksForSshKeysInTheInstance(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SshInstanceBase('test', flag_values)
    self._DoNotPauseForCommand(command)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    mock_instance = {'networkInterfaces': [{'accessConfigs': [{}]}],
                     'status': 'RUNNING',
                     'metadata': {u'kind': u'compute#metadata',
                                  u'items': [{u'key': u'sshKeys',
                                              u'value': ''}]}}

    def MockAddComputeKeyToProject():
      self.fail('Unexpected call to _AddComputeKeyToProject')

    command._AddComputeKeyToProject = MockAddComputeKeyToProject
    with command._EnsureSshable(mock_instance):
      pass

  def testEnsureSshableChecksForNonRunningInstance(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SshInstanceBase('test', flag_values)
    self._DoNotPauseForCommand(command)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    mock_instance = {'networkInterfaces': [{'accessConfigs': [{}]}],
                     'status': 'STAGING'}
    sshable_context_manager = command._EnsureSshable(mock_instance)

    self.assertRaises(gcutil_errors.CommandError,
                      sshable_context_manager.__enter__)

  def testSshGeneratesCorrectArguments(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SshToInstance('ssh', flag_values)
    self._DoNotPauseForCommand(command)

    argv = ['arg1', '%arg2', 'arg3']
    expected_arg_list = ['-A', '-p', '%(port)d', '%(user)s@%(host)s',
                         '--', 'arg1', '%%arg2', 'arg3']

    arg_list = command._GenerateSshArgs(*argv)

    self.assertEqual(expected_arg_list, arg_list)

  def testSshPassesThroughSshArg(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SshToInstance('ssh', flag_values)
    self._DoNotPauseForCommand(command)

    ssh_arg = '--passedSshArgKey=passedSshArgValue'
    flag_values.ssh_arg = [ssh_arg]
    command.SetFlags(flag_values)
    command._InitializeContextParser()
    ssh_args = command._GenerateSshArgs(*[])
    mock_instance_resource = {
        'networkInterfaces': [{'accessConfigs': [{'type': 'ONE_TO_ONE_NAT',
                                                  'natIP': '0.0.0.0'}]}],
        'status': 'RUNNING'}
    command_line = command._BuildSshCmd(mock_instance_resource, 'ssh', ssh_args)
    self.assertTrue(ssh_arg in command_line)

  def testSshPassesThroughTwoSshArgs(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SshToInstance('ssh', flag_values)
    self._DoNotPauseForCommand(command)

    ssh_arg1 = '--k1=v1'
    ssh_arg2 = '--k2=v2'
    flag_values.ssh_arg = [ssh_arg1, ssh_arg2]
    command.SetFlags(flag_values)
    command._InitializeContextParser()
    ssh_args = command._GenerateSshArgs(*[])
    mock_instance_resource = {
        'networkInterfaces': [{'accessConfigs': [{'type': 'ONE_TO_ONE_NAT',
                                                  'natIP': '0.0.0.0'}]}],
        'status': 'RUNNING'}
    command_line = command._BuildSshCmd(mock_instance_resource, 'ssh', ssh_args)

    self.assertTrue(ssh_arg1 in command_line)
    self.assertTrue(ssh_arg2 in command_line)

  def testSshGeneratesCorrectCommand(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.SshToInstance('ssh', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project = 'test_project'
    expected_ip = '1.1.1.1'
    expected_port = 22
    expected_user = 'test_user'
    expected_ssh_file = 'test_file'
    flag_values.project = expected_project
    flag_values.ssh_port = expected_port
    flag_values.ssh_user = expected_user
    flag_values.private_key_file = expected_ssh_file

    ssh_args = ['-A', '-p', '%(port)d', '%(user)s@%(host)s', '--']

    expected_command = [
        'ssh', '-o', 'UserKnownHostsFile=/dev/null',
        '-o', 'CheckHostIP=no',
        '-o', 'StrictHostKeyChecking=no',
        '-i', expected_ssh_file,
        '-A', '-p', str(expected_port),
        '%s@%s' % (expected_user, expected_ip),
        '--']

    if LOGGER.level <= logging.DEBUG:
      expected_command.insert(-5, '-v')

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    mock_instance_resource = {
        'networkInterfaces': [{'accessConfigs': [{'type': 'ONE_TO_ONE_NAT',
                                                  'natIP': expected_ip}]}],
        'status': 'RUNNING'}
    command_line = command._BuildSshCmd(mock_instance_resource, 'ssh', ssh_args)

    self.assertEqual(expected_command, command_line)

  def testScpPushGeneratesCorrectArguments(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.PushToInstance('push', flag_values)
    self._DoNotPauseForCommand(command)

    argv = ['file1', '%file2', 'destination']
    expected_arg_list = ['-r', '-P', '%(port)d', '--',
                         'file1',
                         '%%file2',
                         '%(user)s@%(host)s:destination']

    arg_list = command._GenerateScpArgs(*argv)

    self.assertEqual(expected_arg_list, arg_list)

  def testScpPushGeneratesCorrectCommand(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.PushToInstance('push', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project = 'test_project'
    expected_ip = '1.1.1.1'
    expected_port = 22
    expected_user = 'test_user'
    expected_ssh_file = 'test_file'
    expected_local_file = 'test_source'
    expected_remote_file = 'test_remote'
    flag_values.project = expected_project
    flag_values.ssh_port = expected_port
    flag_values.ssh_user = expected_user
    flag_values.private_key_file = expected_ssh_file

    scp_args = ['-P', '%(port)d', '--']
    unused_argv = ('', expected_local_file, expected_remote_file)

    escaped_args = [a.replace('%', '%%') for a in unused_argv]
    scp_args.extend(escaped_args[1:-1])
    scp_args.append('%(user)s@%(host)s:' + escaped_args[-1])

    expected_command = [
        'scp',
        '-o', 'UserKnownHostsFile=/dev/null',
        '-o', 'CheckHostIP=no',
        '-o', 'StrictHostKeyChecking=no',
        '-i', expected_ssh_file,
        '-P', str(expected_port),
        '--', expected_local_file,
        '%s@%s:%s' % (expected_user, expected_ip, expected_remote_file)]

    if LOGGER.level <= logging.DEBUG:
      expected_command.insert(-5, '-v')

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    mock_instance_resource = {
        'networkInterfaces': [{'accessConfigs': [{'type': 'ONE_TO_ONE_NAT',
                                                  'natIP': expected_ip}]}],
        'status': 'RUNNING'}

    command_line = command._BuildSshCmd(mock_instance_resource, 'scp', scp_args)

    self.assertEqual(expected_command, command_line)

  def testScpPullGeneratesCorrectArguments(self):
    class MockGetApi(object):

      def __init__(self, nat_ip='0.0.0.0'):
        self._nat_ip = nat_ip

      def instances(self):
        return self

      def get(self, *unused_args, **unused_kwargs):
        return self

      def execute(self):
        return {'status': 'RUNNING'}

    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.PullFromInstance('pull', flag_values)
    self._DoNotPauseForCommand(command)

    command.SetApi(old_mock_api.CreateMockApi())
    command.api.instances = MockGetApi()

    argv = ['file1', '%file2', 'destination']
    expected_arg_list = ['-r', '-P', '%(port)d', '--',
                         '%(user)s@%(host)s:file1',
                         '%(user)s@%(host)s:%%file2',
                         'destination']

    arg_list = command._GenerateScpArgs(*argv)

    self.assertEqual(expected_arg_list, arg_list)

  def testScpPullGeneratesCorrectCommand(self):
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.PushToInstance('push', flag_values)
    self._DoNotPauseForCommand(command)

    expected_project = 'test_project'
    expected_ip = '1.1.1.1'
    expected_port = 22
    expected_user = 'test_user'
    expected_ssh_file = 'test_file'
    expected_local_file = 'test_source'
    expected_remote_file = 'test_remote'
    flag_values.project = expected_project
    flag_values.ssh_port = expected_port
    flag_values.ssh_user = expected_user
    flag_values.private_key_file = expected_ssh_file

    scp_args = ['-P', '%(port)d', '--']
    unused_argv = ('', expected_remote_file, expected_local_file)

    escaped_args = [a.replace('%', '%%') for a in unused_argv]
    for arg in escaped_args[1:-1]:
      scp_args.append('%(user)s@%(host)s:' + arg)
    scp_args.append(escaped_args[-1])

    expected_command = [
        'scp',
        '-o', 'UserKnownHostsFile=/dev/null',
        '-o', 'CheckHostIP=no',
        '-o', 'StrictHostKeyChecking=no',
        '-i', expected_ssh_file,
        '-P', str(expected_port),
        '--', '%s@%s:%s' % (expected_user, expected_ip, expected_remote_file),
        expected_local_file]

    if LOGGER.level <= logging.DEBUG:
      expected_command.insert(-5, '-v')

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    mock_instance_resource = {
        'networkInterfaces': [{'accessConfigs': [{'type': 'ONE_TO_ONE_NAT',
                                                  'natIP': expected_ip}]}],
        'status': 'RUNNING'}

    command_line = command._BuildSshCmd(mock_instance_resource, 'scp', scp_args)
    self.assertEqual(expected_command, command_line)

  def testImageFlagsRegistered(self):
    """Make sure we set up image flags for addinstance."""
    flag_values = copy.deepcopy(FLAGS)
    command = instance_cmds.AddInstance('addinstance', flag_values)
    self._DoNotPauseForCommand(command)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    flag_values.old_images = True
    flag_values.standard_images = False

  def _DoTestInstancesCollectionScope(self, flag_values):
    command = instance_cmds.ListInstances('instances', flag_values)
    self._DoNotPauseForCommand(command)

    command.SetFlags(flag_values)
    command._InitializeContextParser()
    command.SetApi(old_mock_api.CreateMockApi())

    self.assertFalse(command.IsGlobalLevelCollection())
    self.assertTrue(command.IsZoneLevelCollection())

    self.assertTrue(command.ListFunc() is not None)
    self.assertTrue(command.ListZoneFunc() is not None)

  def testInstancesCollectionScope(self):
    for ver in command_base.SUPPORTED_VERSIONS:
      flag_values = copy.deepcopy(FLAGS)
      flag_values.service_version = ver
      self._DoTestInstancesCollectionScope(flag_values)

  def testIsInstanceRootDiskPersistentForPersistentDiskCase(self):
    flag_values = copy.deepcopy(FLAGS)
    api_result = {}
    api_result['disks'] = [{'boot': True, 'type': 'PERSISTENT'}]
    api_result['id'] = '123456789'
    api_result['kind'] = 'compute#instance'
    api_result['name'] = 'test_instance'

    ssh = instance_cmds.SshInstanceBase('test', flag_values)

    actual_result = ssh._IsInstanceRootDiskPersistent(api_result)

    self.assertTrue(actual_result)

  def testIsInstanceRootDiskPersistentForEphemeralDiskCase(self):
    flag_values = copy.deepcopy(FLAGS)
    api_result = {}
    api_result['disks'] = [{'index': 0, 'type': 'SCRATCH'}]
    api_result['id'] = '123456789'
    api_result['kind'] = 'compute#instance'
    api_result['name'] = 'test_instance'

    ssh = instance_cmds.SshInstanceBase('test', flag_values)
    actual_result = ssh._IsInstanceRootDiskPersistent(api_result)

    self.assertFalse(actual_result)

if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
