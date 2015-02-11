# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing images."""
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import request_helper


class List(base_classes.BaseLister):
  """List Google Compute Engine images."""

  @staticmethod
  def Args(parser):
    base_classes.BaseLister.Args(parser)

    parser.add_argument(
        '--show-deprecated',
        action='store_true',
        help='If provided, deprecated images are shown.')

    if constants.PREVIEW_IMAGE_PROJECTS:
      preview_image_projects = (
          '{0}.'.format(', '.join(constants.PREVIEW_IMAGE_PROJECTS)))
    else:
      preview_image_projects = '(none)'
    show_preview_images = parser.add_argument(
        '--show-preview-images',
        action='store_true',
        help='If provided, images in limited preview are shown.')
    show_preview_images.detailed_help = """\
       If provided, images in limited preview are shown. The preview image
       projects are: {0}
       """.format(preview_image_projects)

    no_standard_images = parser.add_argument(
        '--no-standard-images',
        action='store_true',
        help="""\
            If provided, images from well-known image projects are not
            shown.
            """)
    no_standard_images.detailed_help = """\
       If provided, images from well-known image projects are not
       shown. The well known image projects are: {0}.
       """.format(', '.join(constants.PUBLIC_IMAGE_PROJECTS))

  @property
  def service(self):
    return self.compute.images

  @property
  def resource_type(self):
    return 'images'

  def GetResources(self, args, errors):
    """Yields images from (potentially) multiple projects."""
    filter_expr = self.GetFilterExpr(args)

    image_projects = [self.project]

    if not args.no_standard_images:
      image_projects.extend(constants.PUBLIC_IMAGE_PROJECTS)

    if args.show_preview_images:
      image_projects.extend(constants.PREVIEW_IMAGE_PROJECTS)

    requests = []
    for project in image_projects:
      requests.append(
          (self.service,
           'List',
           self.messages.ComputeImagesListRequest(
               filter=filter_expr,
               maxResults=constants.MAX_RESULTS_PER_PAGE,
               project=project)))

    images = request_helper.MakeRequests(
        requests=requests,
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None)

    for image in images:
      if not image.deprecated or args.show_deprecated:
        yield image
