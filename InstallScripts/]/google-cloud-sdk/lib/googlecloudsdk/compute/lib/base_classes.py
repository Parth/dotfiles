# Copyright 2014 Google Inc. All Rights Reserved.
"""Base classes for abstracting away common logic."""
import abc
import argparse
import collections
import copy
import cStringIO
import itertools
import json
import sys
import textwrap


import protorpc.messages
import yaml

from googlecloudapis.apitools.base.py import encoding
from googlecloudapis.compute.v1 import compute_v1_messages
from googlecloudsdk.calliope import actions
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import lister
from googlecloudsdk.compute.lib import metadata_utils
from googlecloudsdk.compute.lib import property_selector
from googlecloudsdk.compute.lib import request_helper
from googlecloudsdk.compute.lib import resource_specs
from googlecloudsdk.compute.lib import scope_prompter
from googlecloudsdk.compute.lib import utils
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources as resource_exceptions
from googlecloudsdk.core.util import console_io
from googlecloudsdk.core.util import edit
from googlecloudsdk.core.util import resource_printer


def PrintTable(resources, table_cols):
  """Prints a table of the given resources."""
  printer = resource_printer.TablePrinter(out=log.out)

  header = []
  for name, _ in table_cols:
    header.append(name)
  printer.AddRow(header)

  try:
    for resource in resources:
      row = []
      for _, action in table_cols:
        if isinstance(action, property_selector.PropertyGetter):
          row.append(action.Get(resource) or '')
        elif callable(action):
          row.append(action(resource))
      printer.AddRow(row)
  finally:
    printer.Print()


class BaseCommand(base.Command, scope_prompter.ScopePrompter):
  """Base class for all compute subcommands."""

  __metaclass__ = abc.ABCMeta

  def __init__(self, *args, **kwargs):
    super(BaseCommand, self).__init__(*args, **kwargs)

    # Set the default project for resource resolution

    if self.resource_type:
      # Constructing the spec can be potentially expensive (e.g.,
      # generating the set of valid fields from the protobuf message),
      # so we fetch it once in the constructor.
      self._resource_spec = resource_specs.GetSpec(
          self.resource_type, self.messages)
    else:
      self._resource_spec = None

  @property
  def transformations(self):
    if self._resource_spec:
      return self._resource_spec.transformations
    else:
      return None

  @property
  def resource_type(self):
    """Specifies the name of the collection that should be printed."""
    return None

  @property
  def http(self):
    """Specifies the http client to be used for requests."""
    return self.context['http']

  @property
  def project(self):
    """Specifies the user's project."""
    return self.context['project']

  @property
  def batch_url(self):
    """Specifies the API batch URL."""
    return self.context['batch-url']

  @property
  def compute(self):
    """Specifies the compute client."""
    return self.context['compute']

  @property
  def resources(self):
    """Specifies the resources parser for compute resources."""
    return self.context['resources']

  @property
  def messages(self):
    """Specifies the API message classes."""
    return self.compute.MESSAGES_MODULE

  def Display(self, args, resources):
    """Prints the given resources."""
    if resources:
      resource_printer.Print(
          resources=resources,
          print_format='yaml',
          out=log.out)


class BaseLister(BaseCommand):
  """Base class for the list subcommands."""

  __metaclass__ = abc.ABCMeta

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--limit',
        type=arg_parsers.BoundedInt(1, sys.maxint),
        help='The maximum number of results.')

    sort_by = parser.add_argument(
        '--sort-by',
        help='A field to sort by.')
    sort_by.detailed_help = """\
        A field to sort by. To perform a descending-order sort, prefix
        the value of this flag with a tilde (``~'').
        """

    parser.add_argument(
        'names',
        metavar='NAME',
        nargs='*',
        default=[],
        help=('If provided, show details for the specified names and/or URIs '
              'of resources.'))

    uri = parser.add_argument(
        '--uri',
        action='store_true',
        help='If provided, a list of URIs is printed instead of a table.')
    uri.detailed_help = """\
        If provided, the list command will only print URIs for the
        resources returned.  If this flag is not provided, the list
        command will print a human-readable table of useful resource
        data.
        """

    regexp = parser.add_argument(
        '--regexp', '-r',
        help='A regular expression to filter the names of the results on.')
    regexp.detailed_help = """\
        A regular expression to filter the names of the results on. Any names
        that do not match the entire regular expression will be filtered out.
        """

  @property
  def allowed_filtering_types(self):
    """The list of resource types that can be provided to filtering."""
    return [self.resource_type]

  @abc.abstractmethod
  def GetResources(self, args, errors):
    """Returns a generator of JSON-serializable resource dicts."""

  def GetFilterExpr(self, args):
    """Returns a filter expression if --regexp is provided."""
    if args.regexp:
      return 'name eq {0}'.format(args.regexp)
    else:
      return None

  def PopulateResourceFilteringStructures(self, args):
    """Processes the positional arguments for later filtering."""
    allowed_collections = ['compute.{0}'.format(resource_type)
                           for resource_type in self.allowed_filtering_types]
    for name in args.names:
      try:
        ref = self.resources.Parse(name)

        if ref.Collection() not in allowed_collections:
          raise calliope_exceptions.ToolException(
              'Resource URI must be of type {0}. Received [{1}].'.format(
                  ' or '.join('[{0}]'.format(collection)
                              for collection in allowed_collections),
                  ref.Collection()))

        self.self_links.add(ref.SelfLink())
        self.resource_refs.append(ref)
        continue
      except resource_exceptions.UserError:
        pass

      self.names.add(name)

  def FilterResults(self, args, items):
    """Filters the list results by name and URI."""
    for item in items:
      # If no positional arguments were given, do no filtering.
      if not args.names:
        yield item

      # At this point, we have to do filtering because there was at
      # least one positional argument.
      elif item.selfLink in self.self_links or item.name in self.names:
        yield item

  def Run(self, args):
    """Yields JSON-serializable dicts of resources or self links."""
    # Data structures used to perform client-side filtering of
    # resources by their names and/or URIs.
    self.self_links = set()
    self.names = set()
    self.resource_refs = []

    if args.uri:
      field_selector = None
    else:
      # The field selector should be constructed before any resources
      # are fetched, so if there are any syntactic errors with the
      # fields, we can fail fast.
      field_selector = property_selector.PropertySelector(
          properties=None,
          transformations=self.transformations)

    if args.sort_by:
      if args.sort_by.startswith('~'):
        sort_by = args.sort_by[1:]
        descending = True
      else:
        sort_by = args.sort_by
        descending = False

      for col_name, path in self._resource_spec.table_cols:
        if sort_by == col_name:
          sort_by = path
          break

      if isinstance(sort_by, property_selector.PropertyGetter):
        property_getter = sort_by
      else:
        property_getter = property_selector.PropertyGetter(sort_by)
      sort_key_fn = property_getter.Get

    else:
      sort_key_fn = None
      descending = False

    errors = []

    self.PopulateResourceFilteringStructures(args)
    items = self.FilterResults(args, self.GetResources(args, errors))
    items = lister.ProcessResults(
        resources=items,
        field_selector=field_selector,
        sort_key_fn=sort_key_fn,
        reverse_sort=descending,
        limit=args.limit)

    for item in items:
      if args.uri:
        yield item['selfLink']
      else:
        yield item

    if errors:
      utils.RaiseToolException(errors)

  def Display(self, args, resources):
    """Prints the given resources."""
    if args.uri:
      for resource in resources:
        log.out.Print(resource)
    else:
      PrintTable(resources, self._resource_spec.table_cols)


class GlobalLister(BaseLister):
  """Base class for listing global resources."""

  def GetResources(self, args, errors):
    return lister.GetGlobalResources(
        service=self.service,
        project=self.project,
        filter_expr=self.GetFilterExpr(args),
        http=self.http,
        batch_url=self.batch_url,
        errors=errors)


class RegionalLister(BaseLister):
  """Base class for listing regional resources."""

  @staticmethod
  def Args(parser):
    BaseLister.Args(parser)
    parser.add_argument(
        '--regions',
        metavar='REGION',
        help='If provided, only resources from the given regions are queried.',
        nargs='+',
        default=[])

  def GetResources(self, args, errors):
    region_names = [
        self.CreateGlobalReference(region, resource_type='regions').Name()
        for region in args.regions]

    return lister.GetRegionalResources(
        service=self.service,
        project=self.project,
        requested_regions=region_names,
        filter_expr=self.GetFilterExpr(args),
        http=self.http,
        batch_url=self.batch_url,
        errors=errors)


class ZonalLister(BaseLister):
  """Base class for listing zonal resources."""

  @staticmethod
  def Args(parser):
    BaseLister.Args(parser)
    parser.add_argument(
        '--zones',
        metavar='ZONE',
        help='If provided, only resources from the given zones are queried.',
        nargs='+',
        default=[])

  def GetResources(self, args, errors):
    zone_names = [
        self.CreateGlobalReference(zone, resource_type='zones').Name()
        for zone in args.zones]

    return lister.GetZonalResources(
        service=self.service,
        project=self.project,
        requested_zones=zone_names,
        filter_expr=self.GetFilterExpr(args),
        http=self.http,
        batch_url=self.batch_url,
        errors=errors)


class GlobalRegionalLister(BaseLister):
  """Base class for listing global and regional resources."""

  __metaclass__ = abc.ABCMeta

  @staticmethod
  def Args(parser):
    BaseLister.Args(parser)

    scope = parser.add_mutually_exclusive_group()

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

  @abc.abstractproperty
  def global_service(self):
    """The service used to list global resources."""

  @abc.abstractproperty
  def regional_service(self):
    """The service used to list regional resources."""

  def GetResources(self, args, errors):
    """Yields regional and/or global resources."""
    # This is true if the user provided no flags indicating scope
    no_scope_flags = args.regions is None and not getattr(args, 'global')

    requests = []
    filter_expr = self.GetFilterExpr(args)
    max_results = constants.MAX_RESULTS_PER_PAGE
    project = self.project

    # If --global is present OR no scope flags are present then we have to fetch
    # the global resources.
    if getattr(args, 'global') or no_scope_flags:
      requests.append(
          (self.global_service,
           'List',
           self.global_service.GetRequestType('List')(
               filter=filter_expr,
               maxResults=max_results,
               project=project)))

    # If --regions is present with no arguments OR no scope flags are present
    # then we have to do an aggregated list
    if args.regions == [] or no_scope_flags:
      requests.append(
          (self.regional_service,
           'AggregatedList',
           self.regional_service.GetRequestType('AggregatedList')(
               filter=filter_expr,
               maxResults=max_results,
               project=project)))
    # Else if some regions were provided then only list within them
    elif args.regions:
      region_names = set(
          self.CreateGlobalReference(region, resource_type='regions').Name()
          for region in args.regions)
      for region_name in sorted(region_names):
        requests.append(
            (self.regional_service,
             'List',
             self.regional_service.GetRequestType('List')(
                 filter=filter_expr,
                 maxResults=max_results,
                 region=region_name,
                 project=project)))

    return request_helper.MakeRequests(
        requests=requests,
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None)


class BaseDescriber(BaseCommand):
  """Base class for the describe subcommands."""

  __metaclass__ = abc.ABCMeta

  @staticmethod
  def Args(parser):
    parser.add_argument(
        'name',
        metavar='NAME',
        help='The name of the resource to fetch.')

  @property
  def method(self):
    return 'Get'

  def ScopeRequest(self, ref, request):
    """Adds a zone or region to the request object if necessary."""

  @abc.abstractmethod
  def CreateReference(self, args):
    pass

  def SetNameField(self, ref, request):
    """Sets the field in the request that corresponds to the object name."""
    name_field = self.service.GetMethodConfig(self.method).ordered_params[-1]
    setattr(request, name_field, ref.Name())

  def Run(self, args):
    """Yields JSON-serializable dicts of resources."""
    # The field selector should be constructed before any resources
    # are fetched, so if there are any syntactic errors with the
    # fields, we can fail fast.
    field_selector = property_selector.PropertySelector(properties=args.fields)
    ref = self.CreateReference(args)

    get_request_class = self.service.GetRequestType(self.method)

    request = get_request_class(project=self.project)
    self.SetNameField(ref, request)
    self.ScopeRequest(ref, request)

    get_request = (self.service, self.method, request)

    errors = []
    objects = request_helper.MakeRequests(
        requests=[get_request],
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None)

    resources = list(lister.ProcessResults(objects, field_selector))

    if errors:
      utils.RaiseToolException(
          errors,
          error_message='Could not fetch resource:')
    return resources[0]


class GlobalDescriber(BaseDescriber):
  """Base class for describing global resources."""

  def CreateReference(self, args):
    return self.CreateGlobalReference(args.name)


class RegionalDescriber(BaseDescriber):
  """Base class for describing regional resources."""

  @staticmethod
  def Args(parser):
    BaseDescriber.Args(parser)
    utils.AddRegionFlag(
        parser,
        resource_type='resource',
        operation_type='fetch')

  def CreateReference(self, args):
    return self.CreateRegionalReference(args.name, args.region)

  def ScopeRequest(self, ref, request):
    request.region = ref.region


class ZonalDescriber(BaseDescriber):
  """Base class for describing zonal resources."""

  @staticmethod
  def Args(parser):
    BaseDescriber.Args(parser)
    utils.AddZoneFlag(
        parser,
        resource_type='resource',
        operation_type='fetch')

  def CreateReference(self, args):
    return self.CreateZonalReference(args.name, args.zone)

  def ScopeRequest(self, ref, request):
    request.zone = ref.zone


class GlobalRegionalDescriber(BaseDescriber):
  """Base class for describing global or regional resources."""

  __metaclass__ = abc.ABCMeta

  @staticmethod
  def Args(parser, resource_type):
    BaseDescriber.Args(parser)
    AddFieldsFlag(parser, resource_type)

    scope = parser.add_mutually_exclusive_group()

    scope.add_argument(
        '--region',
        help='The region of the resource to fetch.',
        action=actions.StoreProperty(properties.VALUES.compute.region))

    scope.add_argument(
        '--global',
        action='store_true',
        help=('If provided, it is assumed that the requested resource is '
              'global.'))

  @abc.abstractproperty
  def global_service(self):
    """The service used to list global resources."""

  @abc.abstractproperty
  def regional_service(self):
    """The service used to list regional resources."""

  @abc.abstractproperty
  def global_resource_type(self):
    """The type of global resources."""

  @abc.abstractproperty
  def regional_resource_type(self):
    """The type of regional resources."""

  @property
  def service(self):
    return self._service

  def CreateReference(self, args):
    try:
      ref = self.resources.Parse(args.name, params={'region': args.region})
    except resource_exceptions.UnknownCollectionException:
      if getattr(args, 'global'):
        ref = self.CreateGlobalReference(
            args.name, resource_type=self.global_resource_type)
      else:
        ref = self.CreateRegionalReference(
            args.name, args.region, resource_type=self.regional_resource_type)

    if ref.Collection() not in (
        'compute.{0}'.format(self.regional_resource_type),
        'compute.{0}'.format(self.global_resource_type)):
      raise calliope_exceptions.ToolException(
          'You must pass in a reference to a global or regional resource.')

    ref_resource_type = utils.CollectionToResourceType(ref.Collection())
    if ref_resource_type == self.global_resource_type:
      self._service = self.global_service
    else:
      self._service = self.regional_service
    return ref

  def ScopeRequest(self, ref, request):
    if ref.Collection() == 'compute.{0}'.format(self.regional_resource_type):
      request.region = ref.region


def AddFieldsFlag(parser, resource_type):
  """Adds the --fields flag to the given parser.

  This function is to be called from implementations of describe/list
  subcommands. The resulting help text of --fields will contain all
  valid values for the flag. We need this function becasue Args() is a
  static method so the only way to communicate the resource type is by
  having the subclass pass it in.

  Args:
    parser: The parser to add --fields to.
    resource_type: The resource type as defined in the resource_specs
      module.
  """

  def GenerateDetailedHelp():
    return ('Fields to display. Possible values are:\n+\n  ' +
            '\n  '.join(resource_specs.GetSpec(
                resource_type, compute_v1_messages).fields))

  fields = parser.add_argument(
      '--fields',
      nargs='+',

      help=argparse.SUPPRESS)

  # Note that we do not actually call GenerateDetailedHelp, the help
  # generator does that. This is important because getting the set of
  # fields is a potentially expensive operation, so we only want to do
  # it when needed.
  fields.detailed_help = GenerateDetailedHelp


class BaseAsyncMutator(BaseCommand):
  """Base class for subcommands that mutate resources."""

  __metaclass__ = abc.ABCMeta

  @abc.abstractproperty
  def service(self):
    """The service that can mutate resources."""

  @property
  def custom_get_requests(self):
    """Returns request objects for getting the mutated resources.

    This should be a dict mapping operation targetLink names to
    requests that can be passed to batch_helper. This is useful for
    verbs whose operations do not point to the resources being mutated
    (e.g., Disks.createSnapshot).

    If None, the operations' targetLinks are used to fetch the mutated
    resources.
    """
    return None

  @abc.abstractproperty
  def method(self):
    """The method name on the service as a string."""

  @abc.abstractmethod
  def CreateRequests(self, args):
    """Creates the requests that perform the mutation.

    It is okay for this method to make calls to the API as long as the
    calls originating from this method do not cause any mutations.

    Args:
      args: The command-line arguments.

    Returns:
      A list of request protobufs.
    """

  def Run(self, args):
    request_protobufs = self.CreateRequests(args)
    requests = []
    # If a method is not passed as part of a tuple then use the self.method
    # default
    for request in request_protobufs:
      if isinstance(request, tuple):
        method = request[0]
        proto = request[1]
      else:
        method = self.method
        proto = request
      requests.append((self.service, method, proto))

    errors = []
    resources = request_helper.MakeRequests(
        requests=requests,
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=self.custom_get_requests)

    resources = lister.ProcessResults(
        resources=resources,
        field_selector=property_selector.PropertySelector(
            properties=None,
            transformations=self.transformations))
    for resource in resources:
      yield resource

    if errors:
      utils.RaiseToolException(errors)

  def Display(self, _, resources):
    """Prints the given resources."""
    # The following try/except ensures that we only call
    # resource_printer.Print if there is as least one item in the
    # resources generator.
    try:
      head = next(resources)
      resources = itertools.chain([head], resources)
      resource_printer.Print(
          resources=resources,
          print_format='yaml',
          out=log.out)
    except StopIteration:
      pass


class NoOutputAsyncMutator(BaseAsyncMutator):
  """Base class for mutating subcommands that don't display resources."""

  def Display(self, _, resources):
    # We want to consume the generator here, but don't want to actully display
    # the resources unless --format is called (which skips this method).
    list(resources)


class ListOutputMixin(object):
  """Mixin class to display a list by default."""

  def Display(self, _, resources):
    PrintTable(resources, self._resource_spec.table_cols)


class BaseAsyncCreator(ListOutputMixin, BaseAsyncMutator):
  """Base class for subcommands that create resources."""


class BaseDeleter(BaseAsyncMutator):
  """Base class for deleting resources."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        'names',
        metavar='NAME',
        nargs='+',
        help='The resources to delete.')

  @abc.abstractproperty
  def resource_type(self):
    """The name of the collection that we will delete from."""

  @abc.abstractproperty
  def reference_creator(self):
    """A function that can construct resource reference objects."""

  @abc.abstractproperty
  def scope_name(self):
    """The name of the scope of the resource references."""

  @property
  def method(self):
    return 'Delete'

  @property
  def custom_prompt(self):
    """Allows subclasses to override the delete confirmation message."""
    return None

  def ScopeRequest(self, args, request):
    """Adds a zone or region to the request object if necessary."""

  def CreateRequests(self, args):
    """Returns a list of delete request protobufs."""
    delete_request_class = self.service.GetRequestType(self.method)
    name_field = self.service.GetMethodConfig(self.method).ordered_params[-1]

    refs = self.reference_creator(args.names, args)
    utils.PromptForDeletion(
        refs, self.scope_name, prompt_title=self.custom_prompt)

    requests = []
    for ref in refs:
      request = delete_request_class(project=self.project)
      setattr(request, name_field, ref.Name())
      self.ScopeRequest(ref, request)
      requests.append(request)
    return requests


class ZonalDeleter(BaseDeleter):
  """Base class for deleting zonal resources."""

  @staticmethod
  def Args(parser):
    BaseDeleter.Args(parser)
    utils.AddZoneFlag(
        parser, resource_type='resources', operation_type='delete')

  @property
  def reference_creator(self):
    return (lambda names, args: self.CreateZonalReferences(names, args.zone))

  def ScopeRequest(self, ref, request):
    request.zone = ref.zone

  @property
  def scope_name(self):
    return 'zone'


class RegionalDeleter(BaseDeleter):
  """Base class for deleting regional resources."""

  @staticmethod
  def Args(parser):
    BaseDeleter.Args(parser)
    utils.AddRegionFlag(
        parser, resource_type='resources', operation_type='delete')

  @property
  def reference_creator(self):
    return (
        lambda names, args: self.CreateRegionalReferences(names, args.region))

  def ScopeRequest(self, ref, request):
    request.region = ref.region

  @property
  def scope_name(self):
    return 'region'


class GlobalDeleter(BaseDeleter):
  """Base class for deleting global resources."""

  @property
  def reference_creator(self):
    return (lambda names, _: self.CreateGlobalReferences(names))

  @property
  def scope_name(self):
    return None


class ReadWriteCommand(BaseCommand):
  """Base class for read->update->write subcommands."""

  __metaclass__ = abc.ABCMeta

  @abc.abstractproperty
  def service(self):
    pass

  def CreateReference(self, args):
    """Returns a resources.Resource object for the object being mutated."""

  @abc.abstractmethod
  def GetGetRequest(self, args):
    """Returns a request for fetching the resource."""

  @abc.abstractmethod
  def GetSetRequest(self, args, replacement, existing):
    """Returns a request for setting the resource."""

  @abc.abstractmethod
  def Modify(self, args, existing):
    """Returns a modified resource."""

  def Run(self, args):
    self.ref = self.CreateReference(args)
    get_request = self.GetGetRequest(args)

    errors = []
    objects = list(request_helper.MakeRequests(
        requests=[get_request],
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None))
    if errors:
      utils.RaiseToolException(
          errors,
          error_message='There was a problem fetching the resource:')

    new_object = self.Modify(args, objects[0])

    # If existing object is equal to the proposed object or if
    # Modify() returns None, then there is no work to be done, so we
    # print the resource and return.
    if not new_object or objects[0] == new_object:
      for resource in lister.ProcessResults(
          resources=[objects[0]],
          field_selector=property_selector.PropertySelector(
              properties=None,
              transformations=self.transformations)):
        yield resource
      return

    resources = request_helper.MakeRequests(
        requests=[self.GetSetRequest(args, new_object, objects[0])],
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None)

    resources = lister.ProcessResults(
        resources=resources,
        field_selector=property_selector.PropertySelector(
            properties=None,
            transformations=self.transformations))
    for resource in resources:
      yield resource

    if errors:
      utils.RaiseToolException(
          errors,
          error_message='There was a problem modifying the resource:')

  def Display(self, _, resources):
    # We want to consume the generator here, but don't want to actully display
    # the resources unless --format is called (which skips this method).
    list(resources)


class BaseMetadataAdder(ReadWriteCommand):
  """Base class for adding or modifying metadata entries."""

  @staticmethod
  def Args(parser):
    metadata_utils.AddMetadataArgs(parser)

  def Modify(self, args, existing):
    new_object = copy.deepcopy(existing)
    existing_metadata = getattr(existing, self.metadata_field, None)
    setattr(
        new_object,
        self.metadata_field,
        metadata_utils.ConstructMetadataMessage(
            self.messages,
            metadata=args.metadata,
            metadata_from_file=args.metadata_from_file,
            existing_metadata=existing_metadata))

    if metadata_utils.MetadataEqual(
        existing_metadata,
        getattr(new_object, self.metadata_field, None)):
      return None
    else:
      return new_object

  def Run(self, args):
    if not args.metadata and not args.metadata_from_file:
      raise calliope_exceptions.ToolException(
          'At least one of [--metadata] or [--metadata-from-file] must be '
          'provided.')

    return super(BaseMetadataAdder, self).Run(args)


class BaseMetadataRemover(ReadWriteCommand):
  """Base class for removing metadata entries."""

  @staticmethod
  def Args(parser):
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--all',
        action='store_true',
        default=False,
        help='If provided, all metadata entries are removed.')
    group.add_argument(
        '--keys',
        help='The keys of the entries to remove.',
        metavar='KEY',
        nargs='+')

  def Modify(self, args, existing):
    new_object = copy.deepcopy(existing)
    existing_metadata = getattr(existing, self.metadata_field, None)
    setattr(new_object,
            self.metadata_field,
            metadata_utils.RemoveEntries(
                self.messages,
                existing_metadata=existing_metadata,
                keys=args.keys,
                remove_all=args.all))

    if metadata_utils.MetadataEqual(
        existing_metadata,
        getattr(new_object, self.metadata_field, None)):
      return None
    else:
      return new_object

  def Run(self, args):
    if not args.all and not args.keys:
      raise calliope_exceptions.ToolException(
          'One of [--all] or [--keys] must be provided.')

    return super(BaseMetadataRemover, self).Run(args)


class InstanceMetadataMutatorMixin(ReadWriteCommand):
  """Mixin for mutating instance metadata."""

  @staticmethod
  def Args(parser):
    utils.AddZoneFlag(
        parser,
        resource_type='instance',
        operation_type='set metadata on')
    parser.add_argument(
        'name',
        metavar='NAME',
        help='The name of the instance whose metadata should be modified.')

  @property
  def resource_type(self):
    return 'instances'

  @property
  def service(self):
    return self.compute.instances

  @property
  def metadata_field(self):
    return 'metadata'

  def CreateReference(self, args):
    return self.CreateZonalReference(args.name, args.zone)

  def GetGetRequest(self, args):
    return (self.service,
            'Get',
            self.messages.ComputeInstancesGetRequest(
                instance=self.ref.Name(),
                project=self.project,
                zone=self.ref.zone))

  def GetSetRequest(self, args, replacement, existing):
    return (self.service,
            'SetMetadata',
            self.messages.ComputeInstancesSetMetadataRequest(
                instance=self.ref.Name(),
                metadata=replacement.metadata,
                project=self.project,
                zone=self.ref.zone))


class InstanceTagsMutatorMixin(ReadWriteCommand):
  """Mixin for mutating instance tags."""

  @staticmethod
  def Args(parser):
    utils.AddZoneFlag(
        parser,
        resource_type='instance',
        operation_type='set tags on')
    parser.add_argument(
        'name',
        metavar='NAME',
        help='The name of the instance whose tags should be modified.')

  @property
  def resource_type(self):
    return 'instances'

  @property
  def service(self):
    return self.compute.instances

  def CreateReference(self, args):
    return self.CreateZonalReference(args.name, args.zone)

  def GetGetRequest(self, args):
    return (self.service,
            'Get',
            self.messages.ComputeInstancesGetRequest(
                instance=self.ref.Name(),
                project=self.project,
                zone=self.ref.zone))

  def GetSetRequest(self, args, replacement, existing):
    return (self.service,
            'SetTags',
            self.messages.ComputeInstancesSetTagsRequest(
                instance=self.ref.Name(),
                tags=replacement.tags,
                project=self.project,
                zone=self.ref.zone))


class ProjectMetadataMutatorMixin(ReadWriteCommand):
  """Mixin for mutating project-level metadata."""

  @property
  def service(self):
    return self.compute.projects

  @property
  def metadata_field(self):
    return 'commonInstanceMetadata'

  def GetGetRequest(self, args):
    return (self.service,
            'Get',
            self.messages.ComputeProjectsGetRequest(
                project=self.project))

  def GetSetRequest(self, args, replacement, existing):
    return (self.service,
            'SetCommonInstanceMetadata',
            self.messages.ComputeProjectsSetCommonInstanceMetadataRequest(
                metadata=replacement.commonInstanceMetadata,
                project=self.project))


_HELP = textwrap.dedent("""\
    You can edit the resource below. Lines beginning with "#" are
    ignored.

    If you introduce a syntactic error, you will be given the
    opportunity to edit the file again. You can abort by closing this
    file without saving it.

    At the bottom of this file, you will find an example resource.

    Only fields that can be modified are shown. The original resource
    with all of its fields is reproduced in the comment section at the
    bottom of this document.
    """)


def _SerializeDict(value, fmt):
  """Serializes value to either JSON or YAML."""
  if fmt == 'json':
    return json.dumps(
        value,
        indent=2,
        sort_keys=True,
        separators=(',', ': '))
  else:
    yaml.add_representer(
        collections.OrderedDict,
        yaml.dumper.SafeRepresenter.represent_dict,
        Dumper=yaml.dumper.SafeDumper)
    return yaml.safe_dump(
        value,
        indent=2,
        default_flow_style=False,
        width=70)


def _DeserializeValue(value, fmt):
  """Parses the given JSON or YAML value."""
  if fmt == 'json':
    return json.loads(value)
  else:
    return yaml.load(value)


def _WriteResourceInCommentBlock(serialized_resource, title, buf):
  """Outputs a comment block with the given serialized resource."""
  buf.write('# ')
  buf.write(title)
  buf.write('\n# ')
  buf.write('-' * len(title))
  buf.write('\n#\n')
  for line in serialized_resource.splitlines():
    buf.write('#')
    if line:
      buf.write('   ')
      buf.write(line)
      buf.write('\n')


class BaseEdit(BaseCommand):
  """Base class for modifying resources using $EDITOR."""

  __metaclass__ = abc.ABCMeta

  DEFAULT_FORMAT = 'yaml'

  @abc.abstractmethod
  def CreateReference(self, args):
    """Returns a resources.Resource object for the object being mutated."""

  @abc.abstractproperty
  def reference_normalizers(self):
    """Defines how to normalize resource references."""

  @abc.abstractproperty
  def service(self):
    pass

  @abc.abstractmethod
  def GetGetRequest(self, args):
    """Returns a request for fetching the resource."""

  @abc.abstractmethod
  def GetSetRequest(self, args, replacement, existing):
    """Returns a request for setting the resource."""

  @abc.abstractproperty
  def example_resource(self):
    pass

  def ProcessEditedResource(self, file_contents, args):
    """Returns an updated resource that was edited by the user."""

    # It's very important that we replace the characters of comment
    # lines with spaces instead of removing the comment lines
    # entirely. JSON and YAML deserialization give error messages
    # containing line, column, and the character offset of where the
    # error occurred. If the deserialization fails; we want to make
    # sure those numbers map back to what the user actually had in
    # front of him or her otherwise the errors will not be very
    # useful.
    non_comment_lines = '\n'.join(
        ' ' * len(line) if line.startswith('#') else line
        for line in file_contents.splitlines())

    modified_record = _DeserializeValue(non_comment_lines,
                                        args.format or BaseEdit.DEFAULT_FORMAT)

    # Normalizes all of the fields that refer to other
    # resource. (i.e., translates short names to URIs)
    reference_normalizer = property_selector.PropertySelector(
        transformations=self.reference_normalizers)
    modified_record = reference_normalizer.Apply(modified_record)

    if self.modifiable_record == modified_record:
      new_object = None

    else:
      modified_record['name'] = self.original_record['name']
      fingerprint = self.original_record.get('fingerprint')
      if fingerprint:
        modified_record['fingerprint'] = fingerprint

      new_object = encoding.DictToMessage(
          modified_record, self._resource_spec.message_class)

    # If existing object is equal to the proposed object or if
    # there is no new object, then there is no work to be done, so we
    # return the original object.
    if not new_object or self.original_object == new_object:
      return [self.original_object]

    errors = []
    resources = list(request_helper.MakeRequests(
        requests=[self.GetSetRequest(args, new_object, self.original_object)],
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None))
    if errors:
      utils.RaiseToolException(
          errors,
          error_message='Could not update resource:')

    return resources

  def Run(self, args):
    self.ref = self.CreateReference(args)
    get_request = self.GetGetRequest(args)

    errors = []
    objects = list(request_helper.MakeRequests(
        requests=[get_request],
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None))
    if errors:
      utils.RaiseToolException(
          errors,
          error_message='Could not fetch resource:')

    self.original_object = objects[0]
    self.original_record = encoding.MessageToDict(self.original_object)

    # Selects only the fields that can be modified.
    field_selector = property_selector.PropertySelector(
        properties=self._resource_spec.editables)
    self.modifiable_record = field_selector.Apply(self.original_record)

    buf = cStringIO.StringIO()
    for line in _HELP.splitlines():
      buf.write('#')
      if line:
        buf.write(' ')
      buf.write(line)
      buf.write('\n')

    buf.write('\n')
    buf.write(_SerializeDict(self.modifiable_record,
                             args.format or BaseEdit.DEFAULT_FORMAT))
    buf.write('\n')

    example = _SerializeDict(
        encoding.MessageToDict(self.example_resource),
        args.format or BaseEdit.DEFAULT_FORMAT)
    _WriteResourceInCommentBlock(example, 'Example resource:', buf)

    buf.write('#\n')

    original = _SerializeDict(self.original_record,
                              args.format or BaseEdit.DEFAULT_FORMAT)
    _WriteResourceInCommentBlock(original, 'Original resource:', buf)

    file_contents = buf.getvalue()
    while True:
      file_contents = edit.OnlineEdit(file_contents)
      try:
        resources = self.ProcessEditedResource(file_contents, args)
        break
      except (ValueError, yaml.error.YAMLError,
              protorpc.messages.ValidationError,
              calliope_exceptions.ToolException) as e:
        if isinstance(e, ValueError):
          message = e.message
        else:
          message = str(e)

        if isinstance(e, calliope_exceptions.ToolException):
          problem_type = 'applying'
        else:
          problem_type = 'parsing'

        message = ('There was a problem {0} your changes: {1}'
                   .format(problem_type, message))
        if not console_io.PromptContinue(
            message=message,
            prompt_string='Would you like to edit the resource again?'):
          raise calliope_exceptions.ToolException('Edit aborted by user.')

    resources = lister.ProcessResults(
        resources=resources,
        field_selector=property_selector.PropertySelector(
            properties=None,
            transformations=self.transformations))
    for resource in resources:
      yield resource

  def Display(self, _, resources):
    resource_printer.Print(
        resources=resources,
        print_format='yaml',
        out=log.out)
