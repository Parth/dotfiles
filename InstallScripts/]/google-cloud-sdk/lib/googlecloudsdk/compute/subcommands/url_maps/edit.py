# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for modifying URL maps."""

from googlecloudsdk.compute.lib import base_classes


class Edit(base_classes.BaseEdit):
  """Modify URL maps."""

  @staticmethod
  def Args(parser):
    base_classes.BaseEdit.Args(parser)
    parser.add_argument(
        'name',
        help='The name of the URL map to modify.')

  @property
  def service(self):
    return self.compute.urlMaps

  @property
  def resource_type(self):
    return 'urlMaps'

  @property
  def example_resource(self):
    uri_prefix = ('https://www.googleapis.com/compute/v1/projects/'
                  'my-project/global/backendServices/')
    return self.messages.UrlMap(
        name='site-map',
        defaultService=uri_prefix + 'default-service',
        hostRules=[
            self.messages.HostRule(
                hosts=['*.google.com', 'google.com'],
                pathMatcher='www'),
            self.messages.HostRule(
                hosts=['*.youtube.com', 'youtube.com', '*-youtube.com'],
                pathMatcher='youtube'),
        ],
        pathMatchers=[
            self.messages.PathMatcher(
                name='www',
                defaultService=uri_prefix + 'www-default',
                pathRules=[
                    self.messages.PathRule(
                        paths=['/search', '/search/*'],
                        service=uri_prefix + 'search'),
                    self.messages.PathRule(
                        paths=['/search/ads', '/search/ads/*'],
                        service=uri_prefix + 'ads'),
                    self.messages.PathRule(
                        paths=['/images'],
                        service=uri_prefix + 'images'),
                ]),
            self.messages.PathMatcher(
                name='youtube',
                defaultService=uri_prefix + 'youtube-default',
                pathRules=[
                    self.messages.PathRule(
                        paths=['/search', '/search/*'],
                        service=uri_prefix + 'youtube-search'),
                    self.messages.PathRule(
                        paths=['/watch', '/view', '/preview'],
                        service=uri_prefix + 'youtube-watch'),
                ]),
        ],
        tests=[
            self.messages.UrlMapTest(
                host='www.google.com',
                path='/search/ads/inline?q=flowers',
                service=uri_prefix + 'ads'),
            self.messages.UrlMapTest(
                host='youtube.com',
                path='/watch/this',
                service=uri_prefix + 'youtube-default'),
        ],
    )

  def CreateReference(self, args):
    return self.CreateGlobalReference(args.name)

  @property
  def reference_normalizers(self):
    def NormalizeBackendService(value):
      return self.CreateGlobalReference(
          value, resource_type='backendServices').SelfLink()

    return [
        ('defaultService', NormalizeBackendService),
        ('pathMatchers[].defaultService', NormalizeBackendService),
        ('pathMatchers[].pathRules[].service', NormalizeBackendService),
        ('tests[].service', NormalizeBackendService),
    ]

  def GetGetRequest(self, args):
    return (
        self.service,
        'Get',
        self.messages.ComputeUrlMapsGetRequest(
            project=self.project,
            urlMap=args.name))

  def GetSetRequest(self, args, replacement, _):
    return (
        self.service,
        'Update',
        self.messages.ComputeUrlMapsUpdateRequest(
            project=self.project,
            urlMap=args.name,
            urlMapResource=replacement))


Edit.detailed_help = {
    'brief': 'Modify URL maps',
    'DESCRIPTION': """\
        *{command}* can be used to modify a URL map. The URL map
        resource is fetched from the server and presented in a text
        editor. After the file is saved and closed, this command will
        update the resource. Only fields that can be modified are
        displayed in the editor.

        The editor used to modify the resource is chosen by inspecting
        the ``EDITOR'' environment variable.
        """,
}
