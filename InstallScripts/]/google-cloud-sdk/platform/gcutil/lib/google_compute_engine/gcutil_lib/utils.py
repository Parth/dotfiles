# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A set of utility functions."""

import cStringIO
import httplib
import numbers
import socket
import sys
import apiclient
import httplib2
import yaml




# The discovery doc specifies that we may get no more than 500 results from any
# list command at a time.
MAX_PAGE_SIZE = 500


def GetHttp():
  """Configure an httplib2 object using the user's proxy, if necessary.

  This should be used everywhere in gcutil where an Http object is needed.

  Returns:
    An httplib2.Http object.
  """
  proxy_info = httplib2.proxy_info_from_environment()
  if proxy_info:
    proxy_info.proxy_rdns = True

  return httplib2.Http(proxy_info=proxy_info)


def SimpleName(entity):
  if entity is None:
    return ''

  elif isinstance(entity, basestring):
    if 'projects/google/' in entity:
      return 'google/' + entity.split('/')[-1]
    else:
      return entity.split('/')[-1]

  elif isinstance(entity, numbers.Number):
    return str(entity)

  raise ValueError('Expected number or string: ' + str(entity))


def FlattenList(list):
  """Flattens a list of lists."""
  return [item for sublist in list for item in sublist]


def CombineRegexes(regexes):
  """Combines a list of regular expressions to one regex using '|'.

  Args:
    regexes: A list of regular expressions to use for matching
      resource names. Since resource names cannot contain whitespace
      characters, regular expressions are split on whitespace (e.g.,
      '[a-z]+ [0-9]+' will be treated as two separate regular expressions).

  Returns:
    Combined regular expression that matches input iff any of the provided
    regular rexpressions match.
  """
  if not regexes:
    return None
  return '|'.join(FlattenList(regex.split() for regex in regexes))


def SimplePrint(text, *args, **kwargs):
  """Prints the given text without a new-line character at the end."""
  print text.format(*args, **kwargs),
  sys.stdout.flush()


def ListStrings(strings, prefix='  '):
  """Returns a string containing each item in strings on its own line.

  Args:
    strings: The list of strings to place in the result.
    prefix: A string to place before each name.

  Returns:
    A string containing the names.
  """
  strings = sorted(strings)
  buf = cStringIO.StringIO()
  for string in strings:
    buf.write(prefix + str(string) + '\n')
  return buf.getvalue().rstrip()


def ParseProtocol(protocol_string):
  """Attempt to parse a protocol number from a string.

  Args:
    protocol_string: The string to parse.

  Returns:
    The corresponding protocol number.

  Raises:
    ValueError: If the protocol_string is not a valid protocol string.
  """
  try:
    protocol = socket.getprotobyname(protocol_string)
  except (socket.error, TypeError):
    try:
      protocol = int(protocol_string)
    except (ValueError, TypeError):
      raise ValueError('Invalid protocol: %s' % protocol_string)

  return protocol


def ReplacePortNames(port_range_string):
  """Replace port names with port numbers in a port-range string.

  Args:
    port_range_string: The string to parse.

  Returns:
    A port range string specifying ports only by number.

  Raises:
    ValueError: If the port_range_string is the wrong type or malformed.
  """
  if not isinstance(port_range_string, basestring):
    raise ValueError('Invalid port range: %s' % port_range_string)

  ports = port_range_string.split('-')
  if len(ports) not in [1, 2]:
    raise ValueError('Invalid port range: %s' % port_range_string)

  try:
    low_port = socket.getservbyname(ports[0])
  except socket.error:
    low_port = int(ports[0])

  try:
    high_port = socket.getservbyname(ports[-1])
  except socket.error:
    high_port = int(ports[-1])

  if low_port == high_port:
    return '%d' % low_port
  else:
    return '%d-%d' % (low_port, high_port)


def Singularize(string):
  """A naive function for singularizing Compute Engine collection names."""
  if string.endswith('sses'):
    return string[:len(string) - 2]
  elif string.endswith('ies'):
    return string[:len(string) - 3] + 'y'
  elif string.endswith('s'):
    return string[:len(string) - 1]
  return string


def All(func, project_or_list, max_results=None, filter=None, zone=None,
        region=None, skip_if_not_found=False):
  """Calls the given list function while taking care of paging logic.

  Args:
    func: A Google Compute Engine list function.
    project_or_list: The project (or list of projects) to query.
    max_results: The maximum number of items to return. If None,
        all resources are returned.
    filter: The filter expression to plumb through.
    zone: The zone for list functions that require a zone.
    region: The region for list functions that require a region.
    skip_if_not_found: Skips the project without raising an error if the
        function raises a 404 HttpError

  Returns:
    A list of the resources.
  """
  if isinstance(project_or_list, basestring):
    projects_list = [project_or_list]
  else:
    projects_list = project_or_list

  results = {'items': []}
  kind = None
  for project in projects_list:
    params = {'project': project, 'filter': filter}

    if zone:
      params['zone'] = zone
    elif region:
      params['region'] = region

    items = []
    while True:
      # Compute how many results to ask for.
      params['maxResults'] = MAX_PAGE_SIZE
      if max_results is not None:
        if len(results['items']) + len(items) >= max_results:
          break
        if (max_results - len(items) - len(results['items']) <
            MAX_PAGE_SIZE):
          params['maxResults'] = (
              max_results - len(results['items']) -  len(items))

      try:
        res = func(**params).execute()
      except apiclient.errors.HttpError as e:
        if skip_if_not_found and e.resp.status == httplib.NOT_FOUND:
          break
        else:
          raise
      kind = res.get('kind')
      items.extend(res.get('items', []))
      next_page_token = res.get('nextPageToken')
      if not next_page_token:
        break
      params['pageToken'] = next_page_token
    results = CombineListResults(results, {'kind': kind, 'items': items})

  if max_results is not None:
    results['items'] = results['items'][:max_results]
  return results


def AllNames(func, project_or_list, max_results=None, filter=None, zone=None,
             region=None):
  """Like All, except returns a list of the names of the resources."""
  list_res = All(
      func, project_or_list, max_results=max_results, filter=filter, zone=zone,
      region=region)
  return [resource.get('name') for resource in list_res.get('items', [])]


def AllAggregated(func, project_or_list, max_results=None, filter=None,
                  skip_if_not_found=False):
  """Like All, except it works with aggregated list requests."""
  aggregated_list = {}
  aggregated_list['items'] = {}
  if isinstance(project_or_list, basestring):
    project_list = [project_or_list]
  else:
    project_list = project_or_list

  for project in project_list:
    params = {'project': project, 'filter': filter}

    remaining_results = max_results
    while True:
      if remaining_results is None:
        params['maxResults'] = MAX_PAGE_SIZE
      else:
        params['maxResults'] = min(remaining_results, MAX_PAGE_SIZE)
        remaining_results -= params['maxResults']

      try:
        res = func(**params).execute()
        kind = res.get('kind')
      except apiclient.errors.HttpError as e:
        if skip_if_not_found and e.resp.status == httplib.NOT_FOUND:
          break
        else:
          raise

      if 'items' in res:
        for scope, contents in res['items'].iteritems():
          if scope not in aggregated_list['items']:
            aggregated_list['items'][scope] = {}
          for collection in contents:
            if collection == 'warning':
              aggregated_list['items'][scope]['warning'] = (
                  contents['warning'])
            else:
              if collection not in aggregated_list['items'][scope]:
                aggregated_list['items'][scope][collection] = []
              aggregated_list['items'][scope][collection] += (
                  contents[collection])

      aggregated_list['kind'] = kind

      next_page_token = res.get('nextPageToken')
      if not next_page_token or remaining_results == 0:
        break

      params['pageToken'] = next_page_token

  return aggregated_list


def IsAnyScopeFlagSpecified(flag_values):
  """Returns True if any scope related flags are present, False otherwise."""

  if 'zone' in flag_values and flag_values['zone'].present:
    return True
  if 'region' in flag_values and flag_values['region'].present:
    return True
  if 'global' in flag_values and flag_values['global'].present:
    return True

  return False


def CombineListResults(result1, result2):
  """Combines two outputs of list operations into one.

  Either result can be None, or JSON dictionary representing result of list
  operation.

  Args:
    result1: First list result to combine, or None
    result2: Second list result to combine, or None

  Returns:
    Combined result containing resources from both result1 and result2.
  """

  if result1 is None:
    return result2
  if result2 is None:
    return result1

  items = []
  items.extend(result1.get('items', []))
  items.extend(result2.get('items', []))

  kind = result1.get('kind') or result2.get('kind')

  return {'kind': kind, 'items': items}


def PrintYaml(resource, out=sys.stdout):
  """Print a resource key/value pair into a yaml file.

  Args:
    resource: set of serializable resource to print.
    out: the output stream.
  """
  yaml.safe_dump(
      resource,
      stream=out,
      default_flow_style=False,
      indent=2,
      explicit_start=True)


def ParseYaml(filename=None):
  """Parse a yaml file.

  Args:
    filename: the name of the yaml file to parse.

  Returns:
    key/value pair in json format.
  """
  with open(filename) as f:
    return yaml.load(f)


def GetProjectId(project_id_or_number, api):
  """Gets the project ID given the project ID or numeric project number.

  Args:
    project_id_or_number: The string that is project ID or project number.
    api: The Google Compute Engine API client.

  Returns:
    The project ID.  If numeric project number is passed in, a call to
    server is made to look up the project ID.  If the input
    project_id_or_number is non-numeric, it is returned as project ID.
  """
  # Project ID must start with a letter, so if the string is all digit,
  # it must be the numeric project number.
  is_numeric_project_number = project_id_or_number.isdigit()
  if is_numeric_project_number:
    # If the user gives the numeric project number, we will convert it to the
    # string project ID by querying the server.
    project = api.projects.get(project=project_id_or_number).execute()
    project_id = project.get('name')
  else:
    project_id = project_id_or_number
  return project_id
