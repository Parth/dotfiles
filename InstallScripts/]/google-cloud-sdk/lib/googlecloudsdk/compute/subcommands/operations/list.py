# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing operations."""
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import request_helper


class List(base_classes.BaseLister):
  """List Google Compute Engine operations."""

  @staticmethod
  def Args(parser):
    base_classes.BaseLister.Args(parser)

    scope = parser.add_mutually_exclusive_group()

    scope.add_argument(
        '--zones',
        metavar='ZONE',
        help=('If provided, only zonal resources are shown. '
              'If arguments are provided, only resources from the given '
              'zones are shown.'),
        nargs='*')
    scope.add_argument(
        '--regions',
        metavar='REGION',
        help=('If provided, only regional resources are shown. '
              'If arguments are provided, only resources from the given '
              'regions are shown.'),
        nargs='*')
    scope.add_argument(
        '--global',
        action='store_true',
        help='If provided, only global resources are shown.',
        default=False)

  @property
  def global_service(self):
    return self.compute.globalOperations

  @property
  def regional_service(self):
    return self.compute.regionOperations

  @property
  def zonal_service(self):
    return self.compute.zoneOperations

  @property
  def resource_type(self):
    return 'operations'

  @property
  def allowed_filtering_types(self):
    return ['globalOperations', 'regionOperations', 'zoneOperations']

  def GetResources(self, args, errors):
    """Yields zonal, regional, and/or global resources."""
    # This is True if the user provided no flags indicating scope.
    no_scope_flags = (args.zones is None and args.regions is None and
                      not getattr(args, 'global'))

    requests = []
    filter_expr = self.GetFilterExpr(args)
    max_results = constants.MAX_RESULTS_PER_PAGE
    project = self.project

    if no_scope_flags:
      requests.append(
          (self.global_service,
           'AggregatedList',
           self.global_service.GetRequestType('AggregatedList')(
               filter=filter_expr,
               maxResults=max_results,
               project=project)))
    elif getattr(args, 'global'):
      requests.append(
          (self.global_service,
           'List',
           self.global_service.GetRequestType('List')(
               filter=filter_expr,
               maxResults=max_results,
               project=project)))
    elif args.regions is not None:
      args_region_names = [
          self.CreateGlobalReference(region, resource_type='regions').Name()
          for region in args.regions or []]
      # If no regions were provided by the user, fetch a list.
      region_names = (
          args_region_names or [res.name for res in self.FetchChoiceResources(
              attribute='region',
              service=self.compute.regions,
              flag_names=['--regions'])])
      for region_name in region_names:
        requests.append(
            (self.regional_service,
             'List',
             self.regional_service.GetRequestType('List')(
                 filter=filter_expr,
                 maxResults=constants.MAX_RESULTS_PER_PAGE,
                 region=region_name,
                 project=self.project)))
    elif args.zones is not None:
      args_zone_names = [
          self.CreateGlobalReference(zone, resource_type='regions').Name()
          for zone in args.zones or []]
      # If no zones were provided by the user, fetch a list.
      zone_names = (
          args_zone_names or [res.name for res in self.FetchChoiceResources(
              attribute='zone',
              service=self.compute.zones,
              flag_names=['--zones'])])
      for zone_name in zone_names:
        requests.append(
            (self.zonal_service,
             'List',
             self.zonal_service.GetRequestType('List')(
                 filter=filter_expr,
                 maxResults=constants.MAX_RESULTS_PER_PAGE,
                 zone=zone_name,
                 project=self.project)))

    return request_helper.MakeRequests(
        requests=requests,
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None)


List.detailed_help = {
    'brief': 'List operations',
    'DESCRIPTION': """\
        *{command}* lists summary information of operations in a
        project. The ``--uri'' option can be used to display URIs
        instead. Users who want to see more data should use 'gcloud
        compute operations describe'.

        By default, global operations and operations from all regions are
        listed. The results can be narrowed down by providing the ``--zones'',
        ``--regions'', or ``--global'' flag.
        """,
    'EXAMPLES': """\
        To list all operations in a project in table form, run:

          $ {command}

        To list the URIs of all operations in a project, run:

          $ {command} --uri

        To list all of the global operations in a project, run:

          $ {command} --global

        To list all of the regional operations in a project, run:

          $ {command} --regions

        To list all of the operations from the ``us-central1'' and the
        ``europe-west1'' regions, run:

          $ {command} --regions us-central1 europe-west1
        """,

}
