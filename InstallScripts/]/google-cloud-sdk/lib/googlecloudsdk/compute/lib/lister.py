# Copyright 2014 Google Inc. All Rights Reserved.
"""Facilities for getting a list of Cloud resources."""
import itertools

from googlecloudapis.apitools.base.py import encoding
from googlecloudsdk.compute.lib import constants
from googlecloudsdk.compute.lib import request_helper


def _ConvertProtobufsToDicts(resources):
  for resource in resources:
    if resource is None:
      continue

    yield encoding.MessageToDict(resource)


def ProcessResults(resources, field_selector, sort_key_fn=None,
                   reverse_sort=False, limit=None):
  resources = _ConvertProtobufsToDicts(resources)
  if sort_key_fn:
    resources = sorted(resources, key=sort_key_fn, reverse=reverse_sort)

  if limit > 0:
    resources = itertools.islice(resources, limit)

  for resource in resources:
    if field_selector:
      yield field_selector.Apply(resource)
    else:
      yield resource


def _GetResources(service, project, scopes, scope_name,
                  filter_expr, http, batch_url, errors):
  """Helper for the Get{Zonal,Regional,Global}Resources functions."""
  requests = []

  if scopes:
    for scope in scopes:
      request = service.GetRequestType('List')(
          filter=filter_expr,
          project=project,
          maxResults=constants.MAX_RESULTS_PER_PAGE)
      setattr(request, scope_name, scope)
      requests.append((service, 'List', request))

  elif not scope_name:
    requests.append((
        service,
        'List',
        service.GetRequestType('List')(
            filter=filter_expr,
            project=project,
            maxResults=constants.MAX_RESULTS_PER_PAGE)))

  else:
    requests.append((
        service,
        'AggregatedList',
        service.GetRequestType('AggregatedList')(
            filter=filter_expr,
            project=project,
            maxResults=constants.MAX_RESULTS_PER_PAGE)))

  return request_helper.MakeRequests(
      requests=requests,
      http=http,
      batch_url=batch_url,
      errors=errors,
      custom_get_requests=None)


def GetZonalResources(service, project, requested_zones,
                      filter_expr, http, batch_url, errors):
  """Lists resources that are scoped by zone.

  Args:
    service: An apitools service object.
    project: The Compute Engine project name for which listing should be
      performed.
    requested_zones: A list of zone names that can be used to control
      the scope of the list call.
    filter_expr: A filter to pass to the list API calls.
    http: An httplib2.Http-like object.
    batch_url: The handler for making batch requests.
    errors: A list for capturing errors.

  Returns:
    A generator that yields JSON-serializable dicts representing the results.
  """
  return _GetResources(
      service=service,
      project=project,
      scopes=requested_zones,
      scope_name='zone',
      filter_expr=filter_expr,
      http=http,
      batch_url=batch_url,
      errors=errors)


def GetRegionalResources(service, project, requested_regions,
                         filter_expr, http, batch_url, errors):
  """Lists resources that are scoped by region.

  Args:
    service: An apitools service object.
    project: The Compute Engine project name for which listing should be
      performed.
    requested_regions: A list of region names that can be used to
      control the scope of the list call.
    filter_expr: A filter to pass to the list API calls.
    http: An httplib2.Http-like object.
    batch_url: The handler for making batch requests.
    errors: A list for capturing errors.

  Returns:
    A generator that yields JSON-serializable dicts representing the results.
  """
  return _GetResources(
      service=service,
      project=project,
      scopes=requested_regions,
      scope_name='region',
      filter_expr=filter_expr,
      http=http,
      batch_url=batch_url,
      errors=errors)


def GetGlobalResources(service, project, filter_expr, http,
                       batch_url, errors):
  """Lists resources in the global scope.

  Args:
    service: An apitools service object.
    project: The Compute Engine project name for which listing should be
      performed.
    filter_expr: A filter to pass to the list API calls.
    http: An httplib2.Http-like object.
    batch_url: The handler for making batch requests.
    errors: A list for capturing errors.

  Returns:
    A generator that yields JSON-serializable dicts representing the results.
  """
  return _GetResources(
      service=service,
      project=project,
      scopes=None,
      scope_name=None,
      filter_expr=filter_expr,
      http=http,
      batch_url=batch_url,
      errors=errors)
