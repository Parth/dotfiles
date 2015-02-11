# Copyright 2013 Google Inc. All Rights Reserved.

"""The super-group for the DNS CLI."""

import argparse
import inspect
import json
import os

import apiclient.errors as errors

import httplib2

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exc
from googlecloudsdk.core import config
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.credentials import store as c_store


class DNS(base.Group):
  """Manage Cloud DNS."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--api_version', required=False, help='API version.  Optional.')
    parser.add_argument(
        '--log_http', required=False, help='If true, log http requests.')
    parser.add_argument(
        '--trace_token', required=False, help='Token for tracing API requests')
    parser.add_argument(
        '--http_timeout',
        required=False, help='Timeout for HTTP network requests')

  @c_exc.RaiseToolExceptionInsteadOf(c_store.Error)
  def Filter(self, context, args):
    """Context() is a filter function that can update the context.

    Args:
      context: The current context.
      args: The argparse namespace that was specified on the CLI or API.

    Returns:
      The updated context.
    """

    api_server = properties.VALUES.core.api_host.Get()
    api_version = args.api_version
    if api_version is None:
      api_version = 'v1beta1'

    timeout = None
    if args.http_timeout is not None:
      timeout = float(args.http_timeout)
    http = self.Http(timeout=timeout)
    if args.log_http is not None:
      httplib2.debuglevel = 4

    dns = self.LoadApi(http, api_server, api_version, args)
    context['dns'] = dns

    return context

  @c_exc.RaiseToolExceptionInsteadOf(errors.InvalidJsonError)
  def LoadApi(self, http, api_server, api_version, args):
    """Load an API either from a discovery document or a local file.

    Args:
      http: An httplib2.Http object for making HTTP requests.
      api_server: The location of the http server.
      api_version: The api_version to load.
      args: The args object from the CLI.

    Returns:
      The newly created DNS API Service Object.

    Raises:
      ToolException: If an error occurs in loading the API service object.
    """

    # pylint: disable=g-import-not-at-top, Only load these modules as needed.
    import apiclient.discovery as discovery
    import apiclient.model as model

    # Load the discovery document.
    discovery_document = None

    # Try to download the discovery document
    url = '{server}/discovery/v1/apis/dns/{version}/rest'.format(
        server=api_server.rstrip('/'),
        version=api_version)
    response, content = http.request(url)

    if response.status == 200:
      discovery_document = content
    if discovery_document is None:
      raise c_exc.ToolException('Couldn\'t load discovery')

    try:
      discovery_document = json.loads(discovery_document)
    except ValueError:
      raise errors.InvalidJsonError()


    api = discovery.build_from_document(
        discovery_document,
        http=http,
        model=model.JsonModel())
    return WrapApiIfNeeded(api, args)


# A wrapper around an Api that adds a trace keyword to the Api.
class TracedApi(object):
  """Wrap an Api to add a trace keyword argument."""

  def __init__(self, obj, trace_token):
    def Wrap(func):
      def _Wrapped(*args, **kwargs):
        # Add a trace= URL parameter to the method call.
        if trace_token:
          kwargs['trace'] = trace_token
        return func(*args, **kwargs)
      return _Wrapped

    # Find all public methods and interpose them.
    for method in inspect.getmembers(obj, (inspect.ismethod)):
      if not method[0].startswith('__'):
        setattr(self, method[0], Wrap(method[1]))


class TracedDnsApi(object):
  """Wrap a DnsApi object to return TracedApis."""

  def __init__(self, obj, trace_token):
    def Wrap(func):
      def _Wrapped(*args, **kwargs):
        ret = func(*args, **kwargs)
        if ret:
          ret = TracedApi(ret, trace_token)
        return ret
      return _Wrapped

    # Find all our public methods and interpose them.
    for method in inspect.getmembers(obj, (inspect.ismethod)):
      if not method[0].startswith('__'):
        setattr(self, method[0], Wrap(method[1]))


def WrapApiIfNeeded(api, args):
  """Wraps the API to enable logging or tracing."""
  if args.trace_token:
    return TracedDnsApi(api, 'token:%s' % (args.trace_token))
  return api
