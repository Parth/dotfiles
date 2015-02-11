# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for adding a host rule to a URL map."""
import copy

from googlecloudsdk.compute.lib import base_classes


class AddHostRule(base_classes.ReadWriteCommand):
  """Add a rule to a URL map to map hosts to a path matcher."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--description',
        help='An optional, textual description for the host rule.')

    hosts = parser.add_argument(
        '--hosts',
        nargs='+',
        required=True,
        help='The set of hosts to match requests against.')
    hosts.detailed_help = """\
        The set of hosts to match requests against. Each host must be
        a fully qualified domain name (FQDN) with the exception that
        the host can begin with a ``*'' or ``*-''. ``*'' acts as a
        glob and will match any string of atoms to the left where an
        atom is separated by dots (``.'') or dashes (``-'').
        """

    path_matcher = parser.add_argument(
        '--path-matcher-name',
        required=True,
        help=('The name of the patch matcher to use if a request matches this '
              'host rule.'))
    path_matcher.detailed_help = """\
        The name of the patch matcher to use if a request matches this
        host rule. The patch matcher must already exist in the URL map
        (see 'gcloud compute url-maps add-path-matcher').
        """

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

    new_host_rule = self.messages.HostRule(
        description=args.description,
        hosts=sorted(args.hosts),
        pathMatcher=args.path_matcher_name)

    replacement.hostRules.append(new_host_rule)

    return replacement


AddHostRule.detailed_help = {
    'brief': 'Add a rule to a URL map to map hosts to a path matcher',
    'DESCRIPTION': """\
        *{command}* is used to add a mapping of hosts to a patch
        matcher in a URL map. The mapping will match the host
        component of HTTP requests to path matchers which in turn map
        the request to a backend service. Before adding a host rule,
        at least one path matcher must exist in the URL map to take
        care of the path component of the requests. 'gcloud compute
        url-maps add-path-matcher' or 'gcloud compute url-maps edit'
        can be used to add path matchers.
        """,
    'EXAMPLES': """\
        To create a host rule mapping the ``*-foo.google.com'' and
        ``google.com'' hosts to the ``www'' path matcher, run:

          $ {command} MY-URL-MAP --hosts *-foo.google.com google.com --path-matcher-name www
        """,
}
