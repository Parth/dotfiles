# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for adding a path matcher to a URL map."""
import collections
import copy

from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes


class AddPathMatcher(base_classes.ReadWriteCommand):
  """Add a path matcher to a URL map."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--default-service',
        required=True,
        help=('A backend service that will be used for requests that the path '
              'matcher cannot match.'))

    parser.add_argument(
        '--description',
        help='An optional, textual description for the path matcher.')

    parser.add_argument(
        '--path-matcher-name',
        required=True,
        help='The name to assign to the path matcher.')

    parser.add_argument(
        '--path-rules',
        action=arg_parsers.AssociativeList(),
        default={},
        metavar='PATH=SERVICE',
        nargs='+',
        help='Rules for mapping request paths to services.')

    host_rule = parser.add_mutually_exclusive_group()

    host_rule.add_argument(
        '--new-hosts',
        metavar='NEW_HOST',
        nargs='+',
        help=('If specified, a new host rule with the given hosts is created'
              'and the path matcher is tied to the new host rule.'))

    existing_host = host_rule.add_argument(
        '--existing-host',
        help='An existing host rule to tie the new path matcher to.')
    existing_host.detailed_help = """\
        An existing host rule to tie the new path matcher to. Although
        host rules can contain more than one host, only a single host
        is needed to uniquely identify the host rule.
        """

    parser.add_argument(
        '--delete-orphaned-path-matcher',
        action='store_true',
        default=False,
        help=('If provided and a path matcher is orphaned as a result of this '
              'command, the command removes the orphaned path matcher instead '
              'of failing.'))

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

    if not args.new_hosts and not args.existing_host:
      new_hosts = ['*']
    else:
      new_hosts = args.new_hosts

    # If --new-hosts is given, we check to make sure none of those
    # hosts already exist and once the check succeeds, we create the
    # new host rule.
    if new_hosts:
      new_hosts = set(new_hosts)
      for host_rule in existing.hostRules:
        for host in host_rule.hosts:
          if host in new_hosts:
            raise exceptions.ToolException(
                'Cannot create a new host rule with host [{0}] because the '
                'host is already part of a host rule that references the path '
                'matcher [{1}].'.format(host, host_rule.pathMatcher))

      replacement.hostRules.append(self.messages.HostRule(
          hosts=sorted(new_hosts),
          pathMatcher=args.path_matcher_name))

    # If --existing-host is given, we check to make sure that the
    # corresponding host rule will not render a patch matcher
    # orphan. If the check succeeds, we change the path matcher of the
    # host rule. If the check fails, we remove the path matcher if
    # --delete-orphaned-path-matcher is given otherwise we fail.
    else:
      target_host_rule = None
      for host_rule in existing.hostRules:
        for host in host_rule.hosts:
          if host == args.existing_host:
            target_host_rule = host_rule
            break
        if target_host_rule:
          break

      if not target_host_rule:
        raise exceptions.ToolException(
            'No host rule with host [{0}] exists. Check your spelling or '
            'use [--new-hosts] to create a new host rule.'
            .format(args.existing_host))

      path_matcher_orphaned = True
      for host_rule in replacement.hostRules:
        if host_rule == target_host_rule:
          host_rule.pathMatcher = args.path_matcher_name
          continue

        if host_rule.pathMatcher == target_host_rule.pathMatcher:
          path_matcher_orphaned = False
          break

      if path_matcher_orphaned:
        # A path matcher will be orphaned, so now we determine whether
        # we should delete the path matcher or report an error.
        if args.delete_orphaned_path_matcher:
          replacement.pathMatchers = [
              path_matcher for path_matcher in existing.pathMatchers
              if path_matcher.name != target_host_rule.pathMatcher]
        else:
          raise exceptions.ToolException(
              'This operation will orphan the path matcher [{0}]. To '
              'delete the orphan path matcher, rerun this command with '
              '[--delete-orphaned-path-matcher] or use [gcloud compute '
              'url-maps edit] to modify the URL map by hand.'.format(
                  host_rule.pathMatcher))

    # Creates PathRule objects from --path-rules.
    service_map = collections.defaultdict(set)
    for path, service in args.path_rules.iteritems():
      service_map[service].add(path)
    path_rules = []
    for service, paths in sorted(service_map.iteritems()):
      path_rules.append(self.messages.PathRule(
          paths=sorted(paths),
          service=self.CreateGlobalReference(
              service, resource_type='backendServices').SelfLink()))

    new_path_matcher = self.messages.PathMatcher(
        defaultService=self.CreateGlobalReference(
            args.default_service, resource_type='backendServices').SelfLink(),
        description=args.description,
        name=args.path_matcher_name,
        pathRules=path_rules)

    replacement.pathMatchers.append(new_path_matcher)
    return replacement


AddPathMatcher.detailed_help = {
    'brief': 'Add a path matcher to a URL map',
    'DESCRIPTION': """\
        *{command}* is used to add a path matcher to a URL map. A path
        matcher maps HTTP request paths to backend services. Each path
        matcher must be referenced by at least one host rule. This
        command can create a new host rule through the ``--new-hosts''
        flag or it can reconfigure an existing host rule to point to
        the newly added path matcher using ``--existing-host''. In the
        latter case, if a path matcher is orphaned as a result of the
        operation, this command will fail unless
        ``--delete-orphaned-path-matcher'' is provided.
        """,
    'EXAMPLES': """\
        To create a rule for mapping the paths ``/search'' and
        ``/search/*'' to the hypothetical ``search-service'' and
        ``/images/*'' to the ``images-service'' under the hosts
        ``google.com'' and ``*.google.com'', run:

          $ {command} MY-URL-MAP --path-matcher-name MY-MATCHER --default-service MY-DEFAULT-SERVICE --path-rules /search=search-service /search/*=search_service /images/*=images-service --new-hosts google.com "*.google.com"

        Note that a default service must be provided to handle paths
        for which there is no mapping.
        """,
}
