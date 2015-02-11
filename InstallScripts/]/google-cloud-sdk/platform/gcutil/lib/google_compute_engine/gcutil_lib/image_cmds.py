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

"""Commands for interacting with Google Compute Engine machine images."""




from google.apputils import app
from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base
from gcutil_lib import gcutil_flags
from gcutil_lib import version


FLAGS = flags.FLAGS



def RegisterCommonImageFlags(flag_values):
  """Register common image flags."""
  flags.DEFINE_boolean('old_images',
                       False,
                       'List all versions of images',
                       flag_values=flag_values)
  flags.DEFINE_boolean('standard_images',
                       True,
                       'Include images in all well-known image projects.',
                       flag_values=flag_values)


class ImageCommand(command_base.GoogleComputeCommand):
  """Base command for working with the images collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'deprecation', 'status'],
      field_mappings=(
          ('name', 'selfLink'),
          ('description', 'description'),
          ('deprecation', 'deprecated.state'),
          ('status', 'status')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('deprecation', 'deprecated.state'),
          ('replacement', 'deprecated.replacement'),
          ('status', 'status'),
          ('disk-size-gb', 'diskSizeGb'),
          ('archive-size-bytes', 'archiveSizeBytes')),
      sort_by='name')

  resource_collection_name = 'images'

  def __init__(self, name, flag_values):
    super(ImageCommand, self).__init__(name, flag_values)

  def _AutoDetectZone(self):
    """Causes this command to auto detect zone."""
    def _GetZoneContext(unused_object_type, context):
      return self.GetZoneForResource(
          self.api.disks, context['disk'], context['project'])

    self._context_parser.context_prompt_fxns['zone'] = _GetZoneContext


class AddImage(ImageCommand):
  """Create a new machine image.

  The root_source_tarball parameter must point to a tar file containing the
  contents of the desired root directory. The tar file must be stored
  in Google Cloud Storage.
  """

  positional_args = '<image-name> <root-source-tarball>'

  def __init__(self, name, flag_values):
    super(AddImage, self).__init__(name, flag_values)
    flags.DEFINE_string('description',
                        '',
                        'An optional image description.',
                        flag_values=flag_values)
    flags.DEFINE_string('source_disk',
                        None,
                        'Specifies the source disk from which to '
                        'create the image from. For example, "--source_disk='
                        'my-disk" --zone="us-central1-a".',
                        flag_values=flag_values)
    flags.DEFINE_string('zone',
                        None,
                        'The zone of the disk.',
                        flag_values=flag_values)

  def Handle(self,
             image_name,
             root_source_tarball=None):
    """Add the specified image.

    Args:
      image_name: The name of the image to add.
      root_source_tarball: Tarball in Google Storage containing the
        desired root directory for the resulting image.

    Returns:
      The result of inserting the image.
    """

    image_context = self._context_parser.ParseContextOrPrompt('images',
                                                              image_name)

    # Source Tarball and Source Disk are mutually exclusive parameters.
    if self.api.version >= version.get('v1'):
      if root_source_tarball and self._flags.source_disk:
        raise app.UsageError('You cannot specify both root_source_tarball and '
                             'source_disk. Only one or the other.')

      if not root_source_tarball and not self._flags.source_disk:
        raise app.UsageError('You must specify either a root_source_tarball or '
                             'a source_disk.')
    elif not root_source_tarball:
      raise app.UsageError('You must specify a root_source_tarball.')

    image_resource = {
        'kind': self._GetResourceApiKind('image'),
        'name': image_context['image'],
        'description': self._flags.description,
        'sourceType': 'RAW',
    }

    if root_source_tarball:
      # Accept gs:// URLs.
      if root_source_tarball.startswith('gs://'):
        root_source_tarball = ('http://storage.googleapis.com/' +
                               root_source_tarball[len('gs://'):])
      image_resource['rawDisk'] = {
          'source': root_source_tarball,
          'containerType': 'TAR',
      }
    elif self._flags.source_disk:
      self._AutoDetectZone()
      disk_url = self._context_parser.NormalizeOrPrompt(
          'disks', self._flags.source_disk)
      image_resource['sourceDisk'] = disk_url

    image_request = self.api.images.insert(project=image_context['project'],
                                           body=image_resource)
    return image_request.execute()


class GetImage(ImageCommand):
  """Get a machine image."""

  positional_args = '<image-name>'

  def __init__(self, name, flag_values):
    super(GetImage, self).__init__(name, flag_values)

  def Handle(self, image_name):
    """GSet the specified image.

    Args:
      image_name: The name of the image to get.

    Returns:
      The result of getting the image.
    """
    image_context = self._context_parser.ParseContextOrPrompt('images',
                                                              image_name)

    image_request = self.api.images.get(
        project=image_context['project'],
        image=image_context['image'])

    return image_request.execute()


class DeleteImage(ImageCommand):
  """Delete one or more machine images.

  Specify multiple images as multiple arguments. The images will be deleted
  in parallel.
  """

  positional_args = '<image-name-1> ... <image-name-n>'
  safety_prompt = 'Delete image'

  def __init__(self, name, flag_values):
    super(DeleteImage, self).__init__(name, flag_values)

  def Handle(self, *image_names):
    """Delete the specified images.

    Args:
      *image_names: The names of the images to delete.

    Returns:
      Tuple (results, exceptions) - results of deleting the images.
    """
    requests = []
    for name in image_names:
      image_context = self._context_parser.ParseContextOrPrompt('images', name)
      requests.append(self.api.images.delete(
          project=image_context['project'],
          image=image_context['image']))
    results, exceptions = self.ExecuteRequests(requests)
    return (self.MakeListResult(results, 'operationList'), exceptions)


class ListImages(ImageCommand, command_base.GoogleComputeListCommand):
  """List the images for a project."""

  def __init__(self, name, flag_values):
    super(ListImages, self).__init__(name, flag_values)
    RegisterCommonImageFlags(flag_values)

  def GetProjects(self):
    projects = super(ListImages, self).GetProjects()
    if self._flags.standard_images:
      # Add the standard image projects.
      projects += command_base.STANDARD_IMAGE_PROJECTS
    # Deduplicate the list.
    return list(set(projects))

  def FilterResults(self, results):
    results['items'] = command_base.NewestImagesFilter(
        self._flags, results['items'])
    return results

  @property
  def skip_projects_not_found(self):
    return True

  def ListFunc(self):
    """Returns the function for listing images."""
    return self.api.images.list


class Deprecate(ImageCommand):
  """Sets the deprecation status for an image."""

  positional_args = '<image-name>'

  def __init__(self, name, flag_values):
    super(Deprecate, self).__init__(name, flag_values)
    gcutil_flags.DEFINE_case_insensitive_enum(
        'state',
        'ACTIVE',
        ['ACTIVE', 'DEPRECATED', 'OBSOLETE', 'DELETED'],
        '[Required] Sets the deprecation state for this '
        'image. Valid values are \'ACTIVE\',\'DEPRECATED\', '
        '\'OBSOLETE\', and \'DELETED\'. \'DEPRECATED\' '
        'resources can still be used in requests, but a '
        'warning is returned. \'OBSOLETE\'and \'DELETED\' '
        'resources cannot be used to create new resources '
        'but existing resources can still use the image. '
        '\'ACTIVE\' means that the resource is no longer '
        'deprecated. Note that an image with a \'DELETED\' '
        'deprecation state won\'t automatically be deleted. '
        'You must still make a request to delete the image '
        'to remove it from the image list.',
        flag_values=flag_values)
    flags.DEFINE_string('replacement',
                        None,
                        '[Required] Specifies a Compute Engine image as a '
                        'replacement for this image. Users of the deprecated '
                        'image will be advised to switch to this replacement.'
                        'For example, \'--replacement=my-custom-image\' or '
                        '\'--replacement=projects/google/global/images/'
                        '<image-name>\'.',
                        flag_values=flag_values)
    flags.DEFINE_string('deprecated_on',
                        None,
                        'Specifies a valid RFC 3339 full-date or date-time '
                        'on which the state of this resource became or will '
                        'become DEPRECATED. For example: '
                        '\'2020-01-02T00:00:00Z\' for midnight on January '
                        '2nd, 2020.',
                        flag_values=flag_values)
    flags.DEFINE_string('obsolete_on',
                        None,
                        'Specifies a valid RFC 3339 full-date or date-time '
                        'on which the state of this resource became or will '
                        'become OBSOLETE. For example: '
                        '\'2020-01-02T00:00:00Z\' for midnight on January '
                        '2nd, 2020.',
                        flag_values=flag_values)
    flags.DEFINE_string('deleted_on',
                        None,
                        'Specifies a valid RFC 3339 full-date or date-time '
                        'on which the state of this resource became or will '
                        'become DELETED. For example: 2020-01-02T00:00:00Z '
                        'for midnight on January 2nd, 2020.',
                        flag_values=flag_values)

  def _BuildRequest(self, image_name):
    """Build a request to set deprecation status for the given image."""
    image_context = self._context_parser.ParseContextOrPrompt('images',
                                                              image_name)

    if self._flags.state == 'ACTIVE':
      deprecation_status = {}
    else:
      deprecation_status = {
          'state': self._flags.state,
          'replacement': self._context_parser.NormalizeOrPrompt(
              'images', self._flags.replacement),
          'deprecated': self._flags.deprecated_on,
          'obsolete': self._flags.obsolete_on,
          'deleted': self._flags.deleted_on,
          }

    return self.api.images.deprecate(
        project=image_context['project'],
        image=image_context['image'],
        body=deprecation_status)

  def Handle(self, image_name):
    """Sets deprecation status on an image.

    Args:
      image_name: the name of the image for which deprecation will be set.

    Returns:
      An operation resource.
    """
    set_deprecation_request = self._BuildRequest(image_name)
    return set_deprecation_request.execute()


def AddCommands():
  appcommands.AddCmd('addimage', AddImage)
  appcommands.AddCmd('getimage', GetImage)
  appcommands.AddCmd('deleteimage', DeleteImage)
  appcommands.AddCmd('listimages', ListImages)
  appcommands.AddCmd('deprecateimage', Deprecate)
