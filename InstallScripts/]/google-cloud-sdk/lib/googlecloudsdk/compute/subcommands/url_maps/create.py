# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for creating URL maps."""

from googlecloudsdk.compute.lib import base_classes


class Create(base_classes.BaseAsyncCreator):
  """Create a URL map."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--default-service',
        required=True,
        help=('A backend service that will be used for requests for which this '
              'URL map has no mappings.'))
    parser.add_argument(
        '--description',
        help='An optional, textual description for the URL map.')

    parser.add_argument(
        'name',
        help='The name of the URL map.')

  @property
  def service(self):
    return self.compute.urlMaps

  @property
  def method(self):
    return 'Insert'

  @property
  def resource_type(self):
    return 'urlMaps'

  def CreateRequests(self, args):
    default_service_uri = self.CreateGlobalReference(
        args.default_service, resource_type='backendServices').SelfLink()

    url_map_ref = self.CreateGlobalReference(args.name)

    request = self.messages.ComputeUrlMapsInsertRequest(
        project=self.project,
        urlMap=self.messages.UrlMap(
            defaultService=default_service_uri,
            description=args.description,
            name=url_map_ref.Name()))
    return [request]


Create.detailed_help = {
    'brief': 'Create a URL map',
    'DESCRIPTION': """
        *{command}* is used to create URL maps which map HTTP and
        HTTPS request URLs to backend services. Mappings are done
        using a longest-match strategy.

        There are two components to a mapping: a host rule and a path
        matcher. A host rule maps one or more hosts to a path
        matcher. A path matcher maps request paths to backend
        services. For example, a host rule can map the hosts
        ``*.google.com'' and ``google.com'' to a path matcher called
        ``www''. The ``www'' path matcher in turn can map the path
        ``/search/*'' to the search backend service and everything
        else to a default backend service.

        Host rules and patch matchers can be added to the URL map
        after the map is created by using 'gcloud compute url-maps
        edit' or by using 'gcloud compute url-maps add-path-matcher'
        and 'gcloud compute url-maps add-host-rule'.
        """,
}
