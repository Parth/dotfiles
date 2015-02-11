# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for removing a path matcher from a URL map."""
import copy

from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes


class RemovePathMatcher(base_classes.ReadWriteCommand):
  """Remove a path matcher from a URL map."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--path-matcher-name',
        required=True,
        help='The name of the path matcher to remove.')

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

    # Removes the path matcher.
    new_path_matchers = []
    path_matcher_found = False
    for path_matcher in existing.pathMatchers:
      if path_matcher.name == args.path_matcher_name:
        path_matcher_found = True
      else:
        new_path_matchers.append(path_matcher)

    if not path_matcher_found:
      raise exceptions.ToolException(
          'No path matcher with the name [{0}] was found.'.format(
              args.path_matcher_name))

    replacement.pathMatchers = new_path_matchers

    # Removes all host rules that refer to the path matcher.
    new_host_rules = []
    for host_rule in existing.hostRules:
      if host_rule.pathMatcher != args.path_matcher_name:
        new_host_rules.append(host_rule)
    replacement.hostRules = new_host_rules

    return replacement


RemovePathMatcher.detailed_help = {
    'brief': 'Remove a path matcher from a URL map',
    'DESCRIPTION': """\
        *{command}* is used to remove a path matcher from a URL
         map. When a path matcher is removed, all host rules that
         refer to the path matcher are also removed.
        """,
    'EXAMPLES': """\
        To remove the path matcher named ``MY-MATCHER'' from the URL map named
        ``MY-URL-MAP'', you can use this command:

          $ {command} MY-URL-MAP --path-matcher MY-MATCHER
        """,
}
