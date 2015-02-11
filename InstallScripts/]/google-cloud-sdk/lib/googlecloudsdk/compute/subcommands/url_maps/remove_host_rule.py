# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for removing a host rule from a URL map."""
import copy

from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes


class RemoveHostRule(base_classes.ReadWriteCommand):
  """Remove a host rule from a URL map."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--host',
        required=True,
        help='One of the hosts in the host rule to remove.')

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

    path_matcher_to_remove = None
    new_host_rules = []
    for host_rule in existing.hostRules:
      if args.host in host_rule.hosts:
        path_matcher_to_remove = host_rule.pathMatcher
      else:
        new_host_rules.append(host_rule)

    if not path_matcher_to_remove:
      raise exceptions.ToolException(
          'No host rule contains the host [{0}].'.format(args.host))

    replacement.hostRules = new_host_rules

    path_matcher_is_used_by_other_rules = False
    for host_rule in replacement.hostRules:
      if host_rule.pathMatcher == path_matcher_to_remove:
        path_matcher_is_used_by_other_rules = True
        break

    if not path_matcher_is_used_by_other_rules:
      if args.delete_orphaned_path_matcher:
        replacement.pathMatchers = [
            path_matcher for path_matcher in existing.pathMatchers
            if path_matcher.name != path_matcher_to_remove]
      else:
        raise exceptions.ToolException(
            'This operation will orphan the path matcher [{0}]. To '
            'delete the orphan path matcher, rerun this command with '
            '[--delete-orphaned-path-matcher] or use [gcloud compute '
            'url-maps edit] to modify the URL map by hand.'.format(
                host_rule.pathMatcher))

    return replacement


RemoveHostRule.detailed_help = {
    'brief': 'Remove a host rule from a URL map',
    'DESCRIPTION': """\
        *{command}* is used to remove a host rule from a URL map. When
         a host rule is removed, its path matcher is only removed if
         it is not referenced by any other host rules and
         ``--delete-orphaned-path-matcher'' is provided.
        """,
    'EXAMPLES': """\
        To remove a host rule that contains the host ``google.com''
        from the URL map named ``MY-URL-MAP'', you can use this
        command:

          $ {command} MY-URL-MAP --host google.com
        """,
}
