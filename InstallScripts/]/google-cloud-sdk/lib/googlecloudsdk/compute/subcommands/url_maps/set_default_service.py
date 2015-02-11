# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for changing the default service of a URL map."""
import copy

from googlecloudsdk.compute.lib import base_classes


class SetDefaultService(base_classes.ReadWriteCommand):
  """Change the default service of a URL map."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--default-service',
        required=True,
        help=('A backend service that will be used for requests for which this '
              'URL map has no mappings.'))

    parser.add_argument(
        'name',
        help='The name of the URL map.')

  @property
  def service(self):
    return self.compute.urlMaps

  @property
  def resource_type(self):
    return 'urlMaps'

  def CreateReference(self, args):
    return self.CreateGlobalReference(args.name)

  def GetGetRequest(self, args):
    """Returns the request for the existing URL map resource."""
    return (self.service,
            'Get',
            self.messages.ComputeUrlMapsGetRequest(
                urlMap=self.ref.Name(),
                project=self.project))

  def GetSetRequest(self, args, replacement, existing):
    return (self.service,
            'Update',
            self.messages.ComputeUrlMapsUpdateRequest(
                urlMap=self.ref.Name(),
                urlMapResource=replacement,
                project=self.project))

  def Modify(self, args, existing):
    """Returns a modified URL map message."""
    replacement = copy.deepcopy(existing)

    default_service_uri = self.CreateGlobalReference(
        args.default_service, resource_type='backendServices').SelfLink()
    replacement.defaultService = default_service_uri

    return replacement


SetDefaultService.detailed_help = {
    'brief': 'Change the default service of a URL map',
    'DESCRIPTION': """\
        *{command}* is used to change the default service of a URL
        map. The default service is used for any requests for which
        there is no mapping in the URL map.
        """,
}
