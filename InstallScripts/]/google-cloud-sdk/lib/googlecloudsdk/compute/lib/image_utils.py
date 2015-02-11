# Copyright 2014 Google Inc. All Rights Reserved.
"""Common classes and functions for images."""
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import request_helper
from googlecloudsdk.compute.lib import utils
from googlecloudsdk.core import log
from googlecloudsdk.core.util import console_io


class ImageResourceFetcher(object):
  """Mixin class for displaying images."""


class ImageExpander(object):
  """Mixin class for expanding image aliases."""

  def GetMatchingImages(self, image, alias, errors):
    """Yields images from a public image project and the user's project."""
    service = self.compute.images
    requests = [
        (service,
         'List',
         self.messages.ComputeImagesListRequest(
             filter='name eq ^{0}(-.+)*-v.+'.format(alias.name_prefix),
             maxResults=constants.MAX_RESULTS_PER_PAGE,
             project=alias.project)),
        (service,
         'List',
         self.messages.ComputeImagesListRequest(
             filter='name eq ^{0}$'.format(image),
             maxResults=constants.MAX_RESULTS_PER_PAGE,
             project=self.project)),
    ]

    return request_helper.MakeRequests(
        requests=requests,
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None)

  def GetImage(self, image_ref):
    """Returns the image resource corresponding to the given reference."""
    errors = []
    res = list(request_helper.MakeRequests(
        requests=[(self.compute.images,
                   'Get',
                   self.messages.ComputeImagesGetRequest(
                       image=image_ref.Name(),
                       project=image_ref.project))],
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None))
    if errors:
      utils.RaiseToolException(
          errors,
          error_message='Could not fetch image resource:')
    return res[0]

  def ExpandImageFlag(self, args, return_image_resource=False):
    """Resolves the --image flag value.

    If the value of --image is one of the aliases defined in the
    constants module, both the user's project and the public image
    project for the alias are queried. Otherwise, only the user's
    project is queried. If --image is an alias and --image-project is
    provided, only the given project is queried.

    Args:
      args: The command-line flags. The flags accessed are --image and
        --image-project.
      return_image_resource: If True, always makes an API call to also
        fetch the image resource.

    Returns:
      A tuple where the first element is the self link of the image. If
        return_image_resource is False, the second element is None, otherwise
        it is the image resource.
    """
    image_ref = self.resources.Parse(
        args.image or constants.DEFAULT_IMAGE,
        collection='compute.images',
        resolve=False)

    # If an image project was specified, then assume that image refers
    # to an image in that project.
    if args.image_project:
      image_project_ref = self.resources.Parse(
          args.image_project,
          collection='compute.projects')
      image_ref.project = image_project_ref.Name()
      image_ref.Resolve()
      return (image_ref.SelfLink(),
              self.GetImage(image_ref) if return_image_resource else None)

    image_ref.Resolve()
    alias = constants.IMAGE_ALIASES.get(image_ref.Name())

    # If the image name given is not an alias and no image project was
    # provided, then assume that the image value refers to an image in
    # the user's project.
    if not alias:
      return (image_ref.SelfLink(),
              self.GetImage(image_ref) if return_image_resource else None)

    # At this point, the image is an alias and now we have to find the
    # latest one among the public image project and the user's
    # project.

    errors = []
    images = self.GetMatchingImages(image_ref.Name(), alias, errors)

    user_image = None
    public_images = []

    for image in images:
      if image.deprecated:
        continue
      if '/projects/{0}/'.format(self.project) in image.selfLink:
        user_image = image
      else:
        public_images.append(image)

    if errors or not public_images:
      utils.RaiseToolException(
          errors,
          'Failed to find image for alias [{0}] in public image project [{1}].'
          .format(image_ref.Name(), alias.project))

    def GetVersion(image):
      """Extracts the "20140718" from an image name like "debian-v20140718"."""
      parts = image.name.rsplit('v', 1)
      if len(parts) != 2:
        log.debug('Skipping image with malformed name [%s].', image.name)
        return None
      return parts[1]

    public_candidate = max(public_images, key=GetVersion)
    if user_image:
      options = [user_image, public_candidate]

      idx = console_io.PromptChoice(
          options=[image.selfLink for image in options],
          default=0,
          message=('Found two possible choices for [--image] value [{0}].'
                   .format(image_ref.Name())))

      res = options[idx]

    else:
      res = public_candidate

    log.debug('Image resolved to [%s].', res.selfLink)
    return (res.selfLink, res if return_image_resource else None)


def HasWindowsLicense(resource, resource_parser):
  """Returns True if the given image or disk has a Windows license."""
  for license_uri in resource.licenses:
    license_ref = resource_parser.Parse(
        license_uri, collection='compute.licenses')
    if license_ref.project == constants.WINDOWS_IMAGE_PROJECT:
      return True
  return False


def AddImageProjectFlag(parser):
  """Adds the --image flag to the given parser."""
  image_project = parser.add_argument(
      '--image-project',
      help='The project against which all image references will be resolved.')
  image_project.detailed_help = """\
      The project against which all image references will be
      resolved. See ``--image'' for more details.
      """


def GetImageAliasTable():
  """Returns help text that explains the image aliases."""
  # Note: The leading spaces are very important in this string. The
  # final help text is dedented, so if the leading spaces are off, the
  # help will not be generated properly.
  return """The value for this option can be the name of an image or an
          alias from the table below.

          [options="header",format="csv",grid="none",frame="none"]
          |========
          Alias,Project,Image Name
          {0}
          |========

          When the value is an alias, this tool will query the public
          image project that contains the image type to find the
          latest image matching the alias. The user's project is also
          queried for an image with the same name as the alias. If a
          conflict exists, the user will be prompted to resolve the
          conflict.

          To specify an image in another project for which there is no
          alias, use ``--image-project''. When ``--image-project'' is
          present, no API calls are made to resolve the image. This
          property is useful for scripts.""".format(
              '\n          '.join(
                  ','.join([alias, project, image_name])
                  for alias, (project, image_name) in
                  sorted(constants.IMAGE_ALIASES.iteritems())))
