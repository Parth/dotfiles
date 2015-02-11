# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for updating target HTTP proxies."""

from googlecloudsdk.compute.lib import base_classes


class Update(base_classes.NoOutputAsyncMutator):
  """Update a target HTTP proxy."""

  @staticmethod
  def Args(parser):
    url_map = parser.add_argument(
        '--url-map',
        required=True,
        help=('A reference to a URL map resource that will define the mapping '
              ' of URLs to backend services.'))
    url_map.detailed_help = """\
        A reference to a URL map resource that will define the mapping of
        URLs to backend services. The URL map must exist and cannot be
        deleted while referenced by a target HTTP proxy.
        """

    parser.add_argument(
        'name',
        help='The name of the target HTTP proxy.')

  @property
  def service(self):
    return self.compute.targetHttpProxies

  @property
  def method(self):
    return 'SetUrlMap'

  @property
  def resource_type(self):
    return 'targetHttpProxies'

  def CreateRequests(self, args):
    url_map_ref = self.CreateGlobalReference(
        args.url_map, resource_type='urlMaps')

    target_http_proxy_ref = self.CreateGlobalReference(
        args.name, resource_type='targetHttpProxies')

    request = self.messages.ComputeTargetHttpProxiesSetUrlMapRequest(
        project=self.project,
        targetHttpProxy=target_http_proxy_ref.Name(),
        urlMapReference=self.messages.UrlMapReference(
            urlMap=url_map_ref.SelfLink()))

    return [request]


Update.detailed_help = {
    'brief': 'Update a target HTTP proxy',
    'DESCRIPTION': """\
        *{command}* is used to change the URL map of existing
        target HTTP proxies. A target HTTP proxy is referenced
        by one or more forwarding rules which
        define which packets the proxy is responsible for routing. The
        target HTTP proxy in turn points to a URL map that defines the rules
        for routing the requests. The URL map's job is to map URLs to
        backend services which handle the actual requests.
        """,
}
