# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for getting health status of backend(s) in a backend service."""

from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import request_helper
from googlecloudsdk.compute.lib import utils


class GetHealth(base_classes.BaseCommand):
  """Get health status of backend(s) in an backend service."""

  @staticmethod
  def Args(parser):
    base_classes.AddFieldsFlag(parser, 'backendServiceGroupHealth')

    parser.add_argument(
        'name',
        help='The name of the backend service.')

  @property
  def service(self):
    return self.compute.backendServices

  @property
  def resource_type(self):
    return 'backendServiceGroupHealth'

  def GetBackendService(self, _):
    """Fetches the backend service resource."""
    errors = []
    objects = list(request_helper.MakeRequests(
        requests=[(self.service,
                   'Get',
                   self.messages.ComputeBackendServicesGetRequest(
                       project=self.project,
                       backendService=self.backend_service_ref.Name()
                   ))],
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None))
    if errors:
      utils.RaiseToolException(
          errors,
          error_message='Could not fetch backend service:')
    return objects[0]

  def Run(self, args):
    """Returns a list of backendServiceGroupHealth objects."""
    self.backend_service_ref = self.CreateGlobalReference(
        args.name, resource_type='backendServices')
    backend_service = self.GetBackendService(args)
    if not backend_service.backends:
      return

    # Call GetHealth for each group in the backend service
    requests = []
    for backend in backend_service.backends:
      request_message = self.messages.ComputeBackendServicesGetHealthRequest(
          resourceGroupReference=self.messages.ResourceGroupReference(
              group=backend.group),
          project=self.project,
          backendService=self.backend_service_ref.Name())
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
          error_message='Could not get health for some groups:')


GetHealth.detailed_help = {
    'brief': 'Get backend health statuses from a backend service',
    'DESCRIPTION': """\
        *{command}* is used to request the current health status of
        instances in a backend service. Every group in the service
        is checked and the health status of each configured instance
        is printed.

        If a group contains names of instances that don't exist or
        instances that haven't yet been pushed to the load-balancing
        system, they will not show up. Those that are listed as
        ``HEALTHY'' are able to receive load-balanced traffic. Those that
        are marked as ``UNHEALTHY'' are either failing the configured
        health-check or not responding to it.

        Since the health checks are performed continuously and in
        a distributed manner, the state returned by this command is
        the most recent result of a vote of several redundant health
        checks. Backend services that do not have a valid global
        forwarding rule referencing it will not be health checked and
        so will have no health status.
        """,
}
