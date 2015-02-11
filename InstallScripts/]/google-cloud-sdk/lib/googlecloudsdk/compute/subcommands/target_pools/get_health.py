# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for getting a target pool's health."""
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import request_helper
from googlecloudsdk.compute.lib import utils


class GetHealth(base_classes.BaseCommand):
  """Get the health of instances in a target pool."""

  @staticmethod
  def Args(parser):
    base_classes.AddFieldsFlag(parser, 'targetPoolInstanceHealth')

    utils.AddRegionFlag(
        parser,
        resource_type='target pool',
        operation_type='get health information for')

    parser.add_argument(
        'name',
        help='The name of the target pool.')

  @property
  def service(self):
    return self.compute.targetPools

  @property
  def resource_type(self):
    return 'targetPoolInstanceHealth'

  def GetTargetPool(self):
    """Fetches the target pool resource."""
    errors = []
    objects = list(request_helper.MakeRequests(
        requests=[(self.service,
                   'Get',
                   self.messages.ComputeTargetPoolsGetRequest(
                       project=self.project,
                       region=self.target_pool_ref.region,
                       targetPool=self.target_pool_ref.Name()))],
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None))
    if errors:
      utils.RaiseToolException(
          errors,
          error_message='Could not fetch target pool:')
    return objects[0]

  def Run(self, args):
    """Returns a list of TargetPoolInstanceHealth objects."""
    self.target_pool_ref = self.CreateRegionalReference(
        args.name, args.region, resource_type='targetPools')
    target_pool = self.GetTargetPool()
    instances = target_pool.instances

    # If the target pool has no instances, we should return an empty
    # list.
    if not instances:
      return

    requests = []
    for instance in instances:
      request_message = self.messages.ComputeTargetPoolsGetHealthRequest(
          instanceReference=self.messages.InstanceReference(
              instance=instance),
          project=self.project,
          region=self.target_pool_ref.region,
          targetPool=self.target_pool_ref.Name())
      requests.append((self.service, 'GetHealth', request_message))

    errors = []
    resources = request_helper.MakeRequests(
        requests=requests,
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None)

    for resource in resources:
      yield resource

    if errors:
      utils.RaiseToolException(
          errors,
          error_message='Could not get health for some targets:')


GetHealth.detailed_help = {
    'brief': 'Get the health of instances in a target pool',
    'DESCRIPTION': """\
        *{command}* displays the health of instances in a target pool.
        """,
}
