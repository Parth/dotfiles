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

"""Unit tests for the machine image commands."""



import path_initializer
path_initializer.InitSysPath()

import copy
import json

from google.apputils import app
import gflags as flags
import unittest

from gcutil_lib import command_base
from gcutil_lib import gcutil_unittest
from gcutil_lib import image_cmds
from gcutil_lib import mock_api
from gcutil_lib import old_mock_api
from gcutil_lib import version

FLAGS = flags.FLAGS


class ImageCmdsTest(gcutil_unittest.GcutilTestCase):

  def setUp(self):
    self.mock, self.api = mock_api.CreateApi(self.version)

  def testCreateImageWithNoSourceThrowsUsageError(self):

    set_flags = {
        'project': 'test',
        'description': 'description',
    }

    command = self._CreateAndInitializeCommand(
        image_cmds.AddImage, 'addimage', self.version, set_flags)

    self.assertRaises(app.UsageError,
                      command.Handle, 'image')

  def testCreateImageFromArchiveAndDiskThrowsUsageError(self):

    if self.version < version.get('v1'):
      return
    set_flags = {
        'project': 'test',
        'description': 'description',
        'source_disk': 'disk',
        'zone': 'zone',
    }

    command = self._CreateAndInitializeCommand(
        image_cmds.AddImage, 'addimage', self.version, set_flags)

    self.assertRaises(app.UsageError,
                      command.Handle, 'image', 'source')

  def testAddImageFromDiskGeneratesCorrectRequest(self):
    if self.version < version.get('v1'):
      return
    test_cases = [{
        'requested_image': 'test_image',
        'expected_image': 'test_image',
        'project_flag': 'test_project',
        'expected_project': 'test_project',
        'source_disk': 'test_disk',
        'expected_source_disk': (
            'https://www.googleapis.com/compute/' + self.version +
            '/projects/test_project/zones/dev-central1-std/disks/test_disk'),
        'zone': 'dev-central1-std',
    }]

    for test_case in test_cases:
      self._DoTestAddImageFromDiskGeneratesCorrectRequest(**test_case)

  def _DoTestAddImageFromDiskGeneratesCorrectRequest(
      self, requested_image, expected_image, project_flag,
      expected_project, source_disk, expected_source_disk, zone):

    expected_description = 'test image'
    expected_type = 'RAW'

    set_flags = {
        'project': project_flag,
        'description': expected_description,
        'source_disk': source_disk,
        'zone': zone,
    }

    command = self._CreateAndInitializeCommand(
        image_cmds.AddImage, 'addimage', self.version, set_flags)

    call = self.mock.Respond(
        'compute.images.insert',
        {
            'kind': 'compute#operation',
        })

    unused_result = command.Handle(requested_image)
    request = call.GetRequest()

    self.assertEquals('POST', request.method)

    parameters = request.parameters
    body = json.loads(request.body)

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(body['name'], expected_image)
    self.assertEqual(body['description'], expected_description)

    self.assertNotIn('rawDisk', body)
    self.assertEqual(body['sourceType'], expected_type)
    self.assertEqual(body['sourceDisk'], expected_source_disk)

  def _DoTestAddImageFromSourceTarballGeneratesCorrectRequest(
      self, requested_source, expected_source, requested_image,
      expected_image, project_flag, expected_project):

    expected_description = 'test image'
    expected_type = 'RAW'

    set_flags = {
        'project': project_flag,
        'description': expected_description,
    }

    command = self._CreateAndInitializeCommand(
        image_cmds.AddImage, 'addimage', self.version, set_flags)

    call = self.mock.Respond(
        'compute.images.insert',
        {
            'kind': 'compute#operation',
        })

    unused_result = command.Handle(requested_image, requested_source)
    request = call.GetRequest()

    self.assertEquals('POST', request.method)

    parameters = request.parameters
    body = json.loads(request.body)

    self.assertEqual(parameters['project'], expected_project)
    self.assertEqual(body['name'], expected_image)
    self.assertEqual(body['description'], expected_description)

    self.assertEqual(body['sourceType'], expected_type)
    self.assertEqual(body['rawDisk']['source'], expected_source)

  def testAddImageGeneratesCorrectRequest(self):
    test_cases = [{
        'requested_source': 'http://test.source',
        'expected_source': 'http://test.source',
        'requested_image': 'test_image',
        'expected_image': 'test_image',
        'project_flag': 'test_project',
        'expected_project': 'test_project'
    }, {
        'requested_source': 'gs://test_bucket/source',
        'expected_source': 'http://storage.googleapis.com/test_bucket/source',
        'requested_image': 'test_image',
        'expected_image': 'test_image',
        'project_flag': 'test_project',
        'expected_project': 'test_project'
    }, {
        'requested_source': 'http://example.com/source',
        'expected_source': 'http://example.com/source',
        'requested_image': (
            'https://www.googleapis.com/compute/' + self.version +
            '/projects/right_project/global/images/test_image'),
        'expected_image': 'test_image',
        'project_flag': 'wrong_project',
        'expected_project': 'right_project'
    }]

    for test_case in test_cases:
      self._DoTestAddImageFromSourceTarballGeneratesCorrectRequest(**test_case)

  def testSkipProjectsNotFound(self):
    flag_values = copy.deepcopy(FLAGS)
    command = image_cmds.ListImages('listimages', flag_values)
    self.assertEqual(True, command.skip_projects_not_found)

  def testUndeprecate(self):
    expected_project = 'manhattan'
    expected_image = 'entire_internet'

    set_flags = {
        'project': expected_project,
        'state': 'ACTIVE',
    }

    command = self._CreateAndInitializeCommand(
        image_cmds.Deprecate, 'deprecate', self.version, set_flags)

    call = self.mock.Respond(
        'compute.images.deprecate',
        {
            'kind': 'compute#operation',
        })

    command.Handle(expected_image)

    request = call.GetRequest()

    self.assertEqual(expected_project, request.parameters['project'])
    self.assertEqual(expected_image, request.parameters['image'])
    self.assertEqual('{}', request.body)


class OldImageCmdsTest(unittest.TestCase):

  def testGetImageGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)

    command = image_cmds.GetImage('getimage', flag_values)

    expected_project = 'test_project'
    expected_image = 'test_image'
    flag_values.project = expected_project

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()

    result = command.Handle(expected_image)

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['image'], expected_image)

  def testDeleteImageGeneratesCorrectRequest(self):
    flag_values = copy.deepcopy(FLAGS)

    command = image_cmds.DeleteImage('deleteimage', flag_values)

    expected_project = 'test_project'
    expected_image = 'test_image'
    flag_values.project = expected_project

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._credential = old_mock_api.MockCredential()
    command._InitializeContextParser()

    results, exceptions = command.Handle(expected_image)
    self.assertEqual(exceptions, [])
    self.assertEqual(len(results['items']), 1)
    result = results['items'][0]

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['image'], expected_image)

  def testDeleteMultipleImages(self):
    flag_values = copy.deepcopy(FLAGS)
    command = image_cmds.DeleteImage('deleteimage', flag_values)

    expected_project = 'test_project'
    expected_images = ['test-image-%02d' % x for x in xrange(100)]
    flag_values.project = expected_project

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._credential = old_mock_api.MockCredential()
    command._InitializeContextParser()

    results, exceptions = command.Handle(*expected_images)
    self.assertEqual(exceptions, [])
    results = results['items']
    self.assertEqual(len(results), len(expected_images))

    for expected_image, result in zip(expected_images, results):
      self.assertEqual(result['project'], expected_project)
      self.assertEqual(result['image'], expected_image)

  def testDeprecate(self):
    flag_values = copy.deepcopy(FLAGS)

    command = image_cmds.Deprecate('deprecateimage', flag_values)

    expected_project = 'test_project'
    expected_image = 'test_image'
    expected_state = 'DEPRECATED'
    expected_replacement = 'replacement_image'
    expected_obsolete_timestamp = '1970-01-01T00:00:00Z'
    expected_deleted_timestamp = '1980-01-01T00:00:00.000Z'
    flag_values.project = expected_project
    flag_values.state = expected_state
    flag_values.replacement = expected_replacement
    flag_values.obsolete_on = expected_obsolete_timestamp
    flag_values.deleted_on = expected_deleted_timestamp

    command.SetFlags(flag_values)
    command.SetApi(old_mock_api.CreateMockApi())
    command._InitializeContextParser()

    result = command.Handle(expected_image)

    self.assertEqual(result['project'], expected_project)
    self.assertEqual(result['image'], expected_image)
    self.assertEqual(result['body']['state'], expected_state)
    self.assertEqual(result['body']['replacement'],
                     command.NormalizeGlobalResourceName(
                         expected_project, 'images', expected_replacement))
    self.assertEqual(result['body']['obsolete'], expected_obsolete_timestamp)
    self.assertEqual(result['body']['deleted'], expected_deleted_timestamp)

  def testNewestImagesFilter(self):
    flag_values = copy.deepcopy(FLAGS)
    command = image_cmds.ListImages('listimages', flag_values)
    command.SetFlags(flag_values)

    def ImageSelfLink(name):
      return ('https://www.googleapis.com/compute/v1/projects/'
              'google.com:myproject/global/images/%s') % name

    images = [
        {'selfLink': ImageSelfLink('versionlessimage1')},
        {'selfLink': ImageSelfLink('image-v20130408')},
        {'selfLink': ImageSelfLink('image-v20130410')},
        {'selfLink': ImageSelfLink('image-v20130409')},
        {'selfLink': ImageSelfLink('versionlessimage2')},
    ]

    flag_values.old_images = False
    validate_images = command_base.NewestImagesFilter(flag_values, images)
    self.assertEqual(3, len(validate_images))
    self.assertEqual(
        ImageSelfLink('versionlessimage1'), validate_images[0]['selfLink'])
    self.assertEqual(
        ImageSelfLink('image-v20130410'), validate_images[1]['selfLink'])
    self.assertEqual(
        ImageSelfLink('versionlessimage2'), validate_images[2]['selfLink'])

    flag_values.old_images = True
    validate_images = command_base.NewestImagesFilter(flag_values, images)
    self.assertEqual(5, len(validate_images))
    for i in range(len(images)):
      self.assertEqual(images[i]['selfLink'], validate_images[i]['selfLink'])

  def testPromptForImages(self):
    flag_values = copy.deepcopy(FLAGS)
    flag_values.project = 'myproject'
    command = image_cmds.AddImage('addimage', flag_values)
    command.SetFlags(flag_values)

    class MockListApi(object):
      def __init__(self):
        self.projects = set()
        self.calls = 0

      # pylint: disable=unused-argument
      # pylint: disable=redefined-builtin
      def list(self, project=None, maxResults=None, filter=None,
               pageToken=None):
        self.projects.add(project)
        self.calls += 1
        return old_mock_api.MockRequest({'items': []})

    list_api = MockListApi()
    command._presenter.PromptForImage(list_api)

    expected_projects = command_base.STANDARD_IMAGE_PROJECTS + ['myproject']
    self.assertEquals(len(expected_projects), list_api.calls)
    for project in expected_projects:
      self.assertTrue(project in list_api.projects)


if __name__ == '__main__':
  unittest.main(testLoader=gcutil_unittest.GcutilLoader())
