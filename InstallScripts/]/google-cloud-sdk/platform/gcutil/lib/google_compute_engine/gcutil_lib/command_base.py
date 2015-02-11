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

"""Base command types for interacting with Google Compute Engine."""



import collections
import datetime
import httplib
import inspect
import json
import os
import re
import sys
import time
import traceback


from apiclient import errors
import httplib2
import iso8601
import oauth2client.client as oauth2_client
import yaml


from google.apputils import app
from google.apputils import appcommands
import gflags as flags

from gcutil_lib import api_context_parser
from gcutil_lib import auth_helper
from gcutil_lib import flags_cache
from gcutil_lib import gce_api
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_flags
from gcutil_lib import gcutil_logging
from gcutil_lib import metadata_lib
from gcutil_lib import scopes
from gcutil_lib import thread_pool
from gcutil_lib import utils
from gcutil_lib import version
from gcutil_lib.table import table


FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER
CLIENT_ID = 'google-api-client-python-compute-cmdline/1.0'

CURRENT_VERSION = version.DEFAULT_API_VERSION
SUPPORTED_VERSIONS = version.SUPPORTED_API_VERSIONS

GLOBAL_SCOPE_NAME = 'global'

# The ordering to impose on machine types when prompting the user for
# a machine type choice.
MACHINE_TYPE_ORDERING = ['standard', 'highcpu', 'highmem']


gcutil_flags.DEFINE_case_insensitive_enum(
    'service_version',
    CURRENT_VERSION,
    SUPPORTED_VERSIONS,
    'Google computation service version.')
flags.DEFINE_string(
    'api_host',
    'https://www.googleapis.com/',
    'API host name')
flags.DEFINE_string(
    'project',
    None,
    'The name of the Google Compute Engine project.')
flags.DEFINE_string(
    'project_id',
    None,
    'The name of the Google Compute Engine project. '
    'Deprecated, use --project instead.')
flags.DEFINE_bool(
    'print_json',
    False,
    'Output JSON instead of tabular format. Deprecated, use --format=json.')
gcutil_flags.DEFINE_case_insensitive_enum(
    'format', 'table',
    ('table', 'sparse', 'json', 'csv', 'names', 'yaml'),
    'Format for command output. Options include:'
    '\n table: formatted table output'
    '\n sparse: simpler table output'
    '\n json: raw json output (formerly --print_json)'
    '\n csv: csv format with header'
    '\n names: list of resource names only, no header'
    '\n yaml: output formatted as YAML')
flags.DEFINE_bool(
    'respect_terminal_width',
    True,
    'If true, the user\'s terminal width is respected when outputting tables.')
gcutil_flags.DEFINE_case_insensitive_enum(
    'long_values_display_format',
    None,
    ['elided', 'full'],
    '[Deprecated] The display preference for long table values.')
flags.DEFINE_bool(
    'fetch_discovery',
    False,
    'If true, grab the API description from the discovery API.')
flags.DEFINE_bool(
    'synchronous_mode',
    True,
    'If false, return immediately after posting a request.')
flags.DEFINE_integer(
    'sleep_between_polls',
    3,
    'The time to sleep between polls to the server in seconds.',
    1, 600)
flags.DEFINE_integer(
    'max_wait_time',
    240,
    'The maximum time to wait for an asynchronous operation to complete in '
    'seconds.',
    lower_bound=30,
    upper_bound=2400)
flags.DEFINE_string(
    'trace_token',
    None,
    'Trace the API requests using a trace token provided by Google.')
flags.DEFINE_integer(
    'concurrent_operations',
    10,
    'The maximum number of concurrent operations to have in progress at once. '
    'Increasing this number will probably result in hitting rate limits.',
    1, 20)
flags.DEFINE_bool(
    'require_tty',
    True,
    'Fail if stdin is not a tty.')

# Named tuple to represent print information for a given resource.
ResourcePrintSpec = collections.namedtuple(
    'ResourcePrintSpec', ['summary', 'field_mappings', 'detail', 'sort_by'])

# Named tuple to merge dated resources.
DatedResourceEntry = collections.namedtuple(
    'DatedResourceEntry', ['date', 'resource'])


WINDOWS_IMAGE_PROJECTS = ['windows-cloud']
STANDARD_IMAGE_PROJECTS = ['debian-cloud',
                           'centos-cloud',
                           'coreos-cloud',
                           'rhel-cloud',
                           'suse-cloud',
                           'opensuse-cloud'] + WINDOWS_IMAGE_PROJECTS


def NewestResourcesFilter(resource_list):
  """Filter out all images that are not the 'newest'.

  Args:
    resource_list: A list of json resource objects.
  Returns:
    Only the newest images (in same sort order).
  """
  # selfLinks for resources we want to keep.
  accepted_selflinks = set()

  versioned_resources = {}
  for resource in resource_list:
    match = re.match(r'^(.*\D)(\d{8}$)', resource['selfLink'])
    if not match:
      # Not versioned, just show it.
      accepted_selflinks.add(resource['selfLink'])
      continue

    # Strip the -v from the base name since some images do not have this.
    base_name = match.group(1).rstrip('v').rstrip('-')
    resource_date = match.group(2)

    # Filter out deprecated images from the standard projects.
    if 'deprecated' in resource:
      continue

    # Remove the date from the resource to group them.  Remember only
    # the newest one.
    if base_name not in versioned_resources:
      versioned_resources[base_name] = DatedResourceEntry(
          resource_date, resource)
      continue

    # If this version is newer than the last version, keep it.
    if cmp(resource_date, versioned_resources[base_name].date) > 0:
      versioned_resources[base_name] = DatedResourceEntry(
          resource_date, resource)

  for entry in versioned_resources.values():
    accepted_selflinks.add(entry.resource['selfLink'])

  # Rebuild the resources list, in its native order, filtering out all resources
  # we didn't want.
  return [
      rsrc for rsrc in resource_list if rsrc['selfLink'] in accepted_selflinks]


def NewestImagesFilter(flag_values, images):
  """Filter out all images that are not newest, governed by flags."""
  if 'old_images' not in flag_values:
    return images
  if flag_values.old_images:
    return images
  return NewestResourcesFilter(images)


def ResolveImageTrackOrImageToResource(
    images_api, project, image_name, presenter):
  if not image_name:
    return image_name

  def EnsureOneChoice(choices):
    """Throw an exception if there is more than one choice."""
    if len(choices) > 1:
      LOGGER.warn(
          'Could not disambiguate %s from %s. Proceeding with provided name %s.'
          % (image_name, [presenter(choice) for choice in choices], image_name))
      return None
    return choices[0]

  def ResolveResult(choices, prefix_match):
    """Look for matching choices in choices."""
    exact_choices = [
        image for image in choices if image['name'] == image_name]
    if exact_choices:
      return EnsureOneChoice(exact_choices)

    if prefix_match:
      prefix_choices = [
          image for image in choices if image['name'].startswith(image_name)]
      if prefix_choices:
        return EnsureOneChoice(prefix_choices)

    return None

  # Try first for an exact match on the customer project.
  results = utils.All(images_api.list, project)
  choice = ResolveResult(results['items'], False)

  if not choice:
    results = utils.All(images_api.list, STANDARD_IMAGE_PROJECTS,
                        skip_if_not_found=True)

    # Get the list of all image tracks mapped to the newest image in the track.
    newest_images = NewestResourcesFilter(results['items'])

    # If the user's choice prefix-matches exactly one unique result from that
    # list, then give the user that option.
    choice = ResolveResult(newest_images, True)

    # Otherwise, if the user's choice matches any result exactly, give them that
    # option.
    if not choice:
      choice = ResolveResult(results['items'], False)

  if choice:
    LOGGER.info('Resolved %s to %s', image_name, presenter(choice))
  return choice


def ResolveImageTrackOrImage(images_api, project, image_name, presenter):
  """Resolve the image or track name to the newest version of the given image.

      It is similar to ResolveImageTrackOrImageToResource, but returns the
      selfLink of the image instead of the image resource.

  Args:
    images_api: The images api.
    project: The customer project.
    image_name: The image name.
    presenter: Present the image resource.

  Returns:
    The selfLink of image resource.

  Raises:
    CommandError: If we find multiple matches for the input image_name.
  """
  choice = ResolveImageTrackOrImageToResource(
      images_api, project, image_name, presenter)
  if not choice:
    # Looks like we couldn't find the user's image.  Just pass along what
    # they gave us.
    return image_name

  return choice['selfLink']


class Presenter(object):
  """Presentation for resources and resource queries."""

  def __init__(self, flag_values, is_using_at_least_api_version):
    self._flags = flag_values
    self._is_using_at_least_api_version = is_using_at_least_api_version

  def PromptForChoice(self, choices, collection_name, auto_select=True,
                      extract_resource_prompt=None, additional_key_func=None,
                      allow_none=False):
    """Prompts user to select one of the resources from the choices list.

    The function will create list of prompts from the list of choices. If caller
    passed extract_resource_prompt function, the extract_resource_prompt will be
    called on each resource to generate appropriate prompt text.

    Prompt strings are sorted alphabetically and offered to the user to select
    the desired option. The selected resource is then returned to the caller.

    If the list of choices is empty, None is returned.
    If there is only one available choice and auto_select is True, user is not
    prompted but rather, the only available option is returned.

    If allow_none is True and the user chooses None, None will be returned.

    Args:
      choices: List of Google Compute Engine resources from which user should
        choose.
      collection_name: Name of the collection to present to the user.
      auto_select: Boolean. If set to True and only one resource is available in
        the list of choices, user will not be prompted but rather, the only
        available option will be chosen.
      extract_resource_prompt: Lambda resource -> string. If supplied, this
        function will be called on each resource to generate the prompt string
        for the resource. If the lambda returns empty string, then the choice
        will be omitted from the prompt entirely.
      additional_key_func: Lambda resource -> key. If supplied, this
        function will be used as the first sort key of the name.
      allow_none:  If True, None will be presented as the last option in the
        list.

    Returns:
      The resource user selected. Returns the actual resource as the JSON object
      model represented as Python dictionary.
    """
    if not extract_resource_prompt:

      def ExtractResourcePrompt(resource):
        return self.PresentElement(resource['selfLink'])

      extract_resource_prompt = ExtractResourcePrompt

    if not choices:
      return None

    if auto_select and len(choices) == 1 and not allow_none:
      print 'Selecting the only available %s: %s' % (
          collection_name, choices[0]['name'])
      if 'deprecated' in choices[0]:
        LOGGER.warn('Warning: %s is deprecated!', str(choices[0]['name']))
      return choices[0]

    deprecated_choices = [(extract_resource_prompt(ch) + ' (DEPRECATED)', ch)
                          for ch in choices if 'deprecated' in ch
                          and ch['deprecated']['state'] == 'DEPRECATED' and
                          extract_resource_prompt(ch)]
    deprecated_choices.sort(key=lambda pair: pair[0])
    choices = [(extract_resource_prompt(ch), ch) for ch in choices
               if 'deprecated' not in ch and extract_resource_prompt(ch)]

    if additional_key_func:
      key_func = lambda pair: (additional_key_func(pair[1]), pair[0])
    else:
      key_func = lambda pair: pair[0]

    choices.sort(key=key_func)
    choices.extend(deprecated_choices)

    if allow_none:
      choices.append(('None', None))

    for i, (short_name, unused_choice) in enumerate(choices):
      print '%d: %s' % (i + 1, short_name)

    selection = self._ReadInSelectedItem(choices, collection_name + 's')
    return choices[selection - 1][1]

  def PromptForImage(self, images_api):
    """Prompt the user to select an image from the current list.

    Args:
      images_api: The image api.
    Returns:
      An image resource as selected by the user.
    """
    projects = sorted(set([self._flags.project] + STANDARD_IMAGE_PROJECTS))
    choices = sum((utils.All(images_api.list,
                             project,
                             skip_if_not_found=True)['items']
                   for project in projects), [])
    choices = NewestImagesFilter(self._flags, choices)
    print 'Select an image:'
    return self.PromptForChoice(choices, 'image')

  def PromptForRegion(self, regions_api):
    """Prompt the user to select a region from the current list.

    Args:
      regions_api: The regions api.
    Returns:
      A region resource as selected by the user.
    """
    def GetRegionSecondarySortScore(region):
      return 0 if region.get('status', 'DOWN') == 'UP' else 1

    choices = self._List(regions_api, self._flags.project)['items']
    print 'Select a region:'
    return self.PromptForChoice(choices, 'region',
                                additional_key_func=GetRegionSecondarySortScore)

  def PromptForZone(self, zones_api):
    """Prompt the user to select a zone from the current list.

    Args:
      zones_api: The zones api.
    Returns:
      A zone resource as selected by the user.
    """
    now = datetime.datetime.utcnow()

    def ExtractZonePrompt(zone):
      """Creates a text prompt for a zone resource.

      Includes maintenance information for zones that enter maintenance in less
      than two weeks.

      Args:
        zone: The Google Compute Engine zone resource.

      Returns:
        string to represent a specific zone choice to present to the user.
      """
      name = self.PresentElement(zone['name'])
      maintenance = GoogleComputeCommand.GetNextMaintenanceStart(zone, now)
      if maintenance is not None:
        if maintenance < now:
          return ''
        else:
          delta = maintenance - now
          if delta.days < 1:
            msg = 'maintenance starts in less than 24 hours'
          elif delta.days == 1:
            msg = 'maintenance starts in 1 day'
          else:
            msg = 'maintenance starts in %s days' % delta.days
        if msg:
          return '%s  (%s)' % (name, msg)
      return name

    def GetZoneSecondarySortScore(zone):
      return 0 if zone.get('status', 'DOWN') == 'UP' else 1

    choices = self._List(zones_api, self._flags.project, per_zone=True)['items']
    print 'Select a zone:'
    return self.PromptForChoice(
        choices, 'zone',
        extract_resource_prompt=ExtractZonePrompt,
        additional_key_func=GetZoneSecondarySortScore)

  def PromptForDisk(self, disks_api):
    """Prompt the user to select a disk from the current list.

    Args:
      disks_api: The disks api.
    Returns:
      A disk resource as selected by the user.
    """
    choices = self._List(disks_api, self._flags.project, per_zone=True)['items']
    print 'Select a disk:'
    return self.PromptForChoice(choices, 'disk', auto_select=False)

  def PromptForMachineType(self, machine_types_api, for_test_auto_select=False):
    """Prompt the user to select a machine type from the current list.

    Args:
      machine_types_api: The machine_types disks api.
      for_test_auto_select: Auto select if only one result (for test only).
    Returns:
      A machine_types resource as selected by the user.
    """

    def GetMachineTypeSecondarySortScore(value):
      """Returns a score for the given machine type to be used in sorting.

      This is used to ensure that the lower cost machine types are the
      first ones displayed to the user.

      Args:
        value: The machine type resource.

      Returns:
        An integer that defines a sort order.
      """
      name = value.get('name', '')
      for i in range(len(MACHINE_TYPE_ORDERING)):
        if MACHINE_TYPE_ORDERING[i] in name:
          return i
      return len(MACHINE_TYPE_ORDERING)

    def MachineTypePrompt(resource):
      _, _, name = resource['selfLink'].rpartition('/')
      return '%s\t%s' % (name, resource['description'])

    choices = self._List(machine_types_api, self._flags.project,
                         per_zone=True)['items']

    choices = [choice for choice in choices if
               choice.get('deprecated', {}).get('state') != 'DEPRECATED']

    print 'Select a machine type:'
    return self.PromptForChoice(
        choices, 'machine type', auto_select=for_test_auto_select,
        extract_resource_prompt=MachineTypePrompt,
        additional_key_func=GetMachineTypeSecondarySortScore)

  def _List(self, api, project, per_zone=False):
    kwargs = {}
    if per_zone and hasattr(self._flags, 'zone'):
      kwargs['zone'] = self._flags.zone
    return utils.All(api.list, project, **kwargs)

  def _ReadInSelectedItem(self, choices, menu_name):
    if not sys.stdin.isatty() and self._flags.require_tty:
      raise IOError('Cannot read from stdin: not a tty. You may override '
                    'this error by providing --norequire_tty.')
    while True:
      userinput = raw_input('>>> ').strip()

      # Hopefully, the user decided to user the numeric prompts.
      if userinput.isdigit():
        selection = int(userinput)
        if selection in xrange(1, len(choices) + 1):
          return selection

      # Perhaps the user decided to enter the text from one of the prompts.
      # To protect against typos, recognize only the first word of the prompt
      # and only accept if the first word is unique among the choices.
      for i, (short_name, _) in enumerate(choices):
        first_word = short_name.split()[0]
        if userinput == first_word:
          if (len([choice for choice in choices
                   if choice[0].split()[0] == first_word]) == 1):
            return i + 1

      print 'Invalid selection, please choose one of the listed ' + menu_name

  def PresentElement(self, field_value):
    """Format a json value for tabular display.

    Strips off the project qualifier if present and elides the value
    if it won't fit inside of a max column size of 64 characters.

    Args:
      field_value: The json field value to be formatted.

    Returns:
      The formatted json value.
    """
    if not isinstance(field_value, basestring):
      return field_value

    field_value = self.AbbreviateURL(field_value)
    return field_value

  def AbbreviateURL(self, field_value):
    """Format a resource URL for human consumption by removing uneeded parts.

    Args:
      field_value: The URL string to be formatted.

    Returns:
      The formatted value.
    """

    # If the field_value is a URL, strip off the base parts.
    field_value = self.StripBaseUrl(field_value)

    # If not in our project, keep the whole thing.
    if not field_value.startswith('projects/' + self._flags.project):
      return field_value

    field_value = field_value.strip('/')
    # Path has a format: projects/<project>[/...]
    parts = field_value.split('/')

    # We know there is '/' in the string so there are at least 2 parts.
    if len(parts) == 2:
      # projects/<project>
      # return <project>
      return parts[-1]

    if len(parts) >= 5 and parts[2] == 'global':
      # projects/<project>/global/<collection>/<resource>
      # return <resource>[...]
      return '/'.join(parts[4:])

    if (not (len(parts) >= 4 and
             parts[2] in ('zones', 'regions'))):
      # Old style url. projects/<project>/<type>/...
      return '/'.join(parts[3:])

    # projects/<project>/(zones|regions)/<zone|region>
    # [/<collection>/<resource>]

    if len(parts) == 4:
      # projects/<project>/(zones|regions)/<zone|region>
      # Return region/zone name only.
      return parts[-1]

    if len(parts) < 6:
      # projects/<project>/(zones|regions)/<zone|region>/<collection>
      # Return <zone|region>/<collection>
      return '.'.join(parts[3:])

    # projects/<project>/(zones|regions)/<zone|region>/<collection>/<resource>

    scope_type = parts[2].rstrip('s')  # 'zone' or 'region'
    if hasattr(self._flags, scope_type):
      scope_name = self._flags[scope_type].value or ''
      # rpartition returns (prefix, separator, suffix)
      scope_name = scope_name.rpartition('/')[2]
      if scope_name == parts[3]:
        # Field is in the same zone/region as our flags.
        # Return <collection>/<resource>, since resource need not be unique.
        return '/'.join(parts[4:])

    # PD diskTypes
    if len(parts) == 6 and parts[4] == 'diskTypes':
      return parts[-1]

    # Not in the same zone|region as our flags, so leave the zone|region there.
    # Return <zone|region>/<collection>/<resource>[...]
    return '/'.join(parts[3:])

  def StripBaseUrl(self, value):
    """Removes the a base URL from the string if it exists.

    Note that right now the server may not return exactly the right
    base URL so we strip off stuff that looks like a base URL.

    Args:
      value: The string to strip the base URL from.

    Returns:
      A string without the base URL.
    """
    pattern = '^' + re.escape(self._flags.api_host) + r'compute/\w*/'
    return re.sub(pattern, '', value)


class ApiThreadPoolOperation(thread_pool.Operation):
  """A Thread pool operation that will execute an API request.

  This will wait for the operation to complete, if appropriate.  The
  result from the object will be the last operation object returned.
  """

  def __init__(self, request, command, wait_for_operation,
               timeout_seconds, sleep_between_polls_seconds, timer=time,
               collection_name=None):
    """Initializer."""
    super(ApiThreadPoolOperation, self).__init__()
    self._request = request
    self._command = command
    self._wait_for_operation = wait_for_operation
    self._timeout_seconds = timeout_seconds
    self._sleep_between_polls_seconds = sleep_between_polls_seconds
    self._collection_name = collection_name
    self._timer = timer

  def Run(self):
    """Execute the request on a separate thread."""
    # Note that the httplib2.Http command isn't thread safe.  As such,
    # we need to create a new Http object here.
    http = self._command.CreateHttp()
    result = self._request.execute(http=http)
    if self._wait_for_operation:
      result = self._command.WaitForOperation(
          self._timeout_seconds, self._sleep_between_polls_seconds,
          self._timer, result, http=http,
          collection_name=self._collection_name)
    return result


class GoogleComputeCommand(appcommands.Cmd):
  """Base class for commands that interact with the Google Compute Engine API.

  Overriding classes must override the Handle method.

  Attributes:
    GOOGLE_PROJECT_PATH: The common 'google' project used for storage of shared
        images.
    operation_print_spec: A resource print specification describing how to print
        an operation resource.
    safety_prompt: A boolean indicating whether the command requires user
        confirmation prior to executing.
  """

  GOOGLE_PROJECT_PATH = 'projects/google'
  THREAD_POOL_WAIT_TIME = 0.2
  _timer = time

  operation_print_spec = ResourcePrintSpec(
      summary=['name', 'status', 'operation-type', 'insert-time'],
      field_mappings=(
          ('name', 'name'),
          ('region', 'region'),
          ('zone', 'zone'),
          ('status', 'status'),
          ('status-message', 'statusMessage'),
          ('target', 'targetLink'),
          ('insert-time', 'insertTime'),
          ('operation-type', 'operationType'),
          ('error', 'error.errors.code'),
          ('error-message', 'error.errors.message'),
          ('warning', 'warnings.code')),
      detail=(
          ('name', 'name'),
          ('region', 'region'),
          ('zone', 'zone'),
          ('creation-time', 'creationTimestamp'),
          ('status', 'status'),
          ('progress', 'progress'),
          ('status-message', 'statusMessage'),
          ('target', 'targetLink'),
          ('target-id', 'targetId'),
          ('client-operation-id', 'clientOperationId'),
          ('insert-time', 'insertTime'),
          ('user', 'user'),
          ('start-time', 'startTime'),
          ('end-time', 'endTime'),
          ('operation-type', 'operationType'),
          ('error-code', 'httpErrorStatusCode'),
          ('error-message', 'httpErrorMessage'),
          ('warning', 'warnings.code'),
          ('warning-message', 'warnings.message')),
      sort_by='insert-time')

  _warning_print_spec = ResourcePrintSpec(
      summary=['code'],
      field_mappings=(
          ('code', 'code')),
      detail=(
          ('code', 'code'),
          ('message', 'message')),
      sort_by=None)

  # If this is set to True then the arguments and flags for this
  # command are sorted such that everything that looks like a flag is
  # pulled out of the arguments.  If a command needs unparsed flags
  # after positional arguments (like ssh) then set this to False.
  sort_args_and_flags = True

  def __init__(self, name, flag_values):
    """Initializes a new instance of a GoogleComputeCommand.

    Args:
      name: The name of the command.
      flag_values: The values of command line flags to be used by the command.
    """
    super(GoogleComputeCommand, self).__init__(name, flag_values)
    self._credential = None
    self._context_parser = None

    # When listing all commands, just show the first line of the docstring to
    # avoid flooding the user's terminal, unless the command already has its
    # own terse "_all_commands_help".
    if hasattr(self, '__doc__') and self.__doc__:
      self._all_commands_help = self.__doc__.split('\n', 1)[0]
    if hasattr(self, 'safety_prompt'):
      flags.DEFINE_bool('force',
                        False,
                        'Override the "%s" prompt' % self.safety_prompt,
                        flag_values=flag_values,
                        short_name='f')

  def GetOperationPrintSpec(self):
    return self.operation_print_spec

  @staticmethod
  def GetNextMaintenanceStart(zone, now=None):
    """Get the next maintenance window."""

    def ParseDate(date):
      # Removes the timezone awareness from the timestamp we get back
      # from the server. This is necessary because utcnow() is
      # timezone unaware and it's much easier to remove timezone
      # awareness than to add it in. The latter option requires more
      # code and possibly other libraries.
      return iso8601.parse_date(date).replace(tzinfo=None)

    if now is None:
      now = datetime.datetime.utcnow()
    maintenance = zone.get('maintenanceWindows')
    next_window = None
    if maintenance:
      # Find the next maintenance window.
      for mw in maintenance:
        # Is it already past?
        end = mw.get('endTime')
        if end:
          end = ParseDate(end)
          if end < now:
            # Skip maintenance because it has occurred in the past.
            continue

        begin = mw.get('beginTime')
        if begin:
          begin = ParseDate(begin)
          if next_window is None or begin < next_window:
            next_window = begin
    return next_window

  def _GetZone(self, zone=None):
    """Notifies the user if the given zone will enter maintenance soon.

    The given zone can be None in which case the user is prompted for
    a zone. This method is intended to provide a warning to the user
    if he or she seeks to create a disk or instance in a zone that
    will enter maintenance in less than two weeks.

    Args:
      zone: The name of the zone chosen, or None.

    Returns:
      The given zone or the zone chosen through the prompt.
    """
    if zone is None:
      zone_resource = self._presenter.PromptForZone(self.api.zones)
      zone = zone_resource['name']
    else:
      zone = zone.split('/')[-1]
      zone_resource = self.api.zones.get(
          project=self._project, zone=zone).execute()

      # Warns the user if there is an upcoming maintenance for the
      # chosen zone. Times returned from the server are in UTC.
      now = datetime.datetime.utcnow()
      next_win = GoogleComputeCommand.GetNextMaintenanceStart(
          zone_resource, now)
      if next_win is not None:
        if next_win < now:
          msg = 'is unavailable due to maintenance'
        else:
          delta = next_win - now
          if delta >= datetime.timedelta(weeks=2):
            msg = None
          elif delta.days < 1:
            msg = 'less than 24 hours'
          elif delta.days == 1:
            msg = '1 day'
          else:
            msg = '%s days' % delta.days
          if msg:
            msg = 'will become unavailable due to maintenance in %s' % msg
        if msg:
          LOGGER.warn('%s %s.', str(zone), str(msg))
    return zone

  def _GetRegions(self):
    """Retrieves the full list of regions available to this project.

    Returns:
      List of regions available to this project.
    """
    return utils.AllNames(self.api.regions.list, self._project)

  def _GetZones(self):
    """Retrieves the full list of zones available to this project.

    Returns:
      List of zones available to this project.
    """
    return utils.AllNames(self.api.zones.list, self._project)

  def _AuthenticateWrapper(self, http):
    """Adds the OAuth token into http request.

    Args:
      http: An instance of httplib2.Http or something that acts like it.

    Returns:
      httplib2.Http like object.

    Raises:
      CommandError: If the credentials can't be found.
    """
    if not self._credential:
      self._credential = auth_helper.GetCredentialFromStore(
          self.__GetRequiredAuthScopes())
      if not self._credential:
        raise gcutil_errors.CommandError(
            'Could not get valid credentials for API.')
    return self._credential.authorize(http)


  def _ParseArgumentsAndFlags(self, flag_values, argv):
    """Parses the command line arguments for the command.

    This method matches up positional arguments based on the
    signature of the Handle method.  It also parses the flags
    found on the command line.

    argv will contain, <main python file>, positional-arguments, flags...

    Args:
      flag_values: The flags list to update
      argv: The command line argument list

    Returns:
      The list of position arguments for the given command.

    Raises:
      CommandError: If any problems occur with parsing the commands (e.g.,
          type mistmatches, out of bounds, unknown commands, ...).
    """
    # If we are sorting args and flags, kick the flag parser into gnu
    # mode and parse some more.  argv will be all of the unparsed args
    # after this.
    if self.sort_args_and_flags:
      try:
        old_gnu_mode = flag_values.IsGnuGetOpt()
        flag_values.UseGnuGetOpt(True)
        argv = flag_values(argv)
      except (flags.IllegalFlagValue, flags.UnrecognizedFlagError) as e:
        raise gcutil_errors.CommandError(e)
      finally:
        flag_values.UseGnuGetOpt(old_gnu_mode)

    # We use the same positional arguments used by the command's Handle method.
    # For AddDisk this will be, ['self', 'disk_name'].
    argspec = inspect.getargspec(self.Handle)

    # Skip the implicit argument 'self' and take the list of
    # positional command args.
    default_count = len(argspec.defaults) if argspec.defaults else 0
    pos_arg_names = argspec.args[1:]

    # We then parse off values for those positional arguments from argv.
    # Note that we skip the first argument, as that is the command path.
    pos_arg_values = argv[1:len(pos_arg_names) + 1]

    # Take all the arguments past the positional arguments. If there
    # is a var_arg on the command this will get passed in.
    unparsed_args = argv[len(pos_arg_names) + 1:]

    # If we did not get enough positional argument values print error and exit.
    if len(pos_arg_names) - default_count > len(pos_arg_values):
      missing_args = pos_arg_names[len(pos_arg_values):]
      missing_args = ['"%s"' % a for a in missing_args]
      raise gcutil_errors.CommandError(
          'Positional argument %s is missing.' % ', '.join(missing_args))

    # If users specified flags in place of positional argument values,
    # print error and exit.
    for (name, value) in zip(pos_arg_names, pos_arg_values):
      if value.startswith('--'):
        raise gcutil_errors.CommandError(
            'Invalid positional argument value \'%s\' for argument \'%s\'\n' % (
                value, name))

    # If there are any unparsed args and the command is not expecting
    # varargs, print error and exit.
    if (unparsed_args and

        not getattr(self, 'has_varargs', False) and

        not argspec.varargs):
      unparsed_args = ['"%s"' % a for a in unparsed_args]
      raise gcutil_errors.CommandError(
          'Unknown argument: %s' % ', '.join(unparsed_args))

    # Warn about any deprecated and unused flags.
    if flag_values.long_values_display_format:
      LOGGER.warn('--long_values_display_format is deprecated and ignored.')

    return argv[1:]

  @staticmethod
  def DenormalizeResourceName(resource_name):
    """Return the relative name for the given resource.

    Args:
      resource_name: The name of the resource. This can be either relative or
          absolute.

    Returns:
      The name of the resource relative to its enclosing collection.
    """
    if resource_name:
      return resource_name.strip('/').rpartition('/')[2]
    else:
      return ''

  @staticmethod
  def DenormalizeProjectName(flag_values):
    """Denormalize the 'project' entry in the given FlagValues instance.

    Args:
      flag_values: The FlagValues instance to update.

    Raises:
      CommandError: If the project is missing or malformed.
    """
    project = flag_values.project or flag_values.project_id

    if not project:
      raise gcutil_errors.CommandError(
          'You must specify a project name using the "--project" flag.')
    elif project.lower() != project:
      raise gcutil_errors.CommandError(
          'Characters in project name must be lowercase: %s.' % project)

    project = GoogleComputeCommand.DenormalizeResourceName(project)

    flag_values.project = project
    flag_values.project_id = None

  def _GetBaseApiUrl(self):
    """Get the base API URL given the current flag_values.

    Returns:
      The base API URL.  For example,
      https://www.googleapis.com/compute/v1.
    """
    return '%scompute/%s' % (self._flags.api_host, self._flags.service_version)

  def _AddBaseUrlIfNecessary(self, resource_path):
    """Add the base URL to a resource_path if required by the service_version.

    Args:
      resource_path: The resource path to add the URL to.

    Returns:
      A full API-usable reference to the given resource_path.
    """
    if self._GetBaseApiUrl() not in resource_path:
      return '%s/%s' % (self._GetBaseApiUrl(), resource_path)
    return resource_path

  def NormalizeResourceName(self, project, scope_name, collection_name,
                            resource_name):
    """Return the full name for the given resource.

    Args:
      project: The name of the project containing the resource.
      scope_name: The scope of the collection containing the resource.
      collection_name: The name of the collection containing the resource.
      resource_name: The name of the resource. This can be either relative
          or absolute.

    Returns:
      The full URL of the resource.
    """
    if not resource_name:
      return ''
    resource_name = resource_name.strip('/')

    if (resource_name.startswith('projects/') or
        resource_name.startswith(collection_name + '/') or
        resource_name.startswith(self._flags.api_host)):
      # This does not appear to be a relative name.
      return self._AddBaseUrlIfNecessary(resource_name)

    absolute_name = 'projects/%s/%s/%s' % (project,
                                           collection_name,
                                           resource_name)

    if scope_name:
      absolute_name = 'projects/%s/%s/%s/%s' % (project,
                                                scope_name,
                                                collection_name,
                                                resource_name)
    return self._AddBaseUrlIfNecessary(absolute_name)

  def NormalizeTopLevelResourceName(self, project, collection, resource):
    """Return the full name for the given resource.

    Args:
      project: The name of the project containing the resource.
      collection: The name of the collection containing the resource.
      resource: The name of the resource. This can be either relative or
          absolute.

    Returns:
      The full URL of the resource.
    """
    return self.NormalizeResourceName(project,
                                      None,
                                      collection,
                                      resource)

  def NormalizeGlobalResourceName(self, project, collection, resource):
    """Return the full name for the given resource.

    Args:
      project: The name of the project containing the resource.
      collection: The name of the collection containing the resource.
      resource: The name of the resource. This can be either relative or
          absolute.

    Returns:
      The full URL of the resource.
    """
    return self.NormalizeResourceName(project,
                                      'global',
                                      collection,
                                      resource)

  def NormalizePerRegionResourceName(self, project, region, collection,
                                     resource):
    """Return the full name for the given resource.

    Args:
      project: The name of the project containing the resource.
      region: The name of the region containing the resource.
      collection: The name of the collection containing the resource.
      resource: The name of the resource. This can be either relative or
          absolute.

    Returns:
      The full URL of the resource.
    """
    return self.NormalizeResourceName(project,
                                      'regions/%s' % region,
                                      collection,
                                      resource)

  def NormalizePerZoneResourceName(self, project, zone, collection, resource):
    """Return the full name for the given resource.

    Args:
      project: The name of the project containing the resource.
      zone: The name of the zone containing the resource.
      collection: The name of the collection containing the resource.
      resource: The name of the resource. This can be either relative or
          absolute.

    Returns:
      The full URL of the resource.
    """
    return self.NormalizeResourceName(project,
                                      'zones/%s' % zone,
                                      collection,
                                      resource)

  def NormalizeMachineTypeResourceName(self, project, zone, collection,
                                       resource):
    """Return the full name for the given machine type.

    Args:
      project:  The name of the project containing the resource.
      zone:  The name of the zone containing the resource.
      collection:  The name of the collection containing the resource.
      resource:  The name of the resource.  This can be either relative or
          absolute

    Returns:
      The full URL of the resource.
    """
    if zone:
      return self.NormalizePerZoneResourceName(project, zone, collection,
                                               resource)
    return self.NormalizeGlobalResourceName(project, collection, resource)

  def GetRegionForResource(self, api, resource_name, fail_if_not_found=True,
                           project=None):
    """Gets the unqualified region name for a given resource.

    The function first tries to use 'region' parameter if set, but falls back
    to searching for the resource name across regions.

    Args:
      api: The API service that must expose 'list' method.
      resource_name: Name of the resource to find.
      fail_if_not_found: Raise an error when the resource is not found.
      project: Project for the resource

    Returns:
      Unqualified name of the region the resource belongs to.

    Raises:
      CommandError: If the region for the resource cannot be resolved.
    """
    # If the resource is already project- and region-qualified, use the region.
    if not resource_name:
      return None

    if not project:
      project = self._project

    resource_name_parts = self._presenter.StripBaseUrl(resource_name).split('/')
    if (len(resource_name_parts) > 3 and
        resource_name_parts[0] == 'projects' and
        resource_name_parts[2] == 'regions'):
      return resource_name_parts[3]

    if self._flags.region == GLOBAL_SCOPE_NAME:
      return None

    if self._flags.region:
      return self._flags.region

    filter_expression = ('name eq %s' %
                         self.DenormalizeResourceName(resource_name))

    items = []

    # Limiting the number of results to 2, since zero results means that we
    # failed to find the resource and 2 means that it is duplicated somehow.
    aggregated_items = utils.AllAggregated(
        api.aggregatedList, project, max_results=2,
        filter=filter_expression)

    for scope in aggregated_items['items']:
      for collection in aggregated_items['items'][scope]:
        if collection != 'warning':
          items += aggregated_items['items'][scope][collection]

    if len(items) == 1:
      region = self._GetRegionFromSelfLink(items[0]['selfLink'])
      LOGGER.info('Region for %s detected as %s.', str(resource_name),
                  str(region) or GLOBAL_SCOPE_NAME)
      LOGGER.warning('Consider passing \'--region=%s\' to avoid the unnecessary'
                     ' region lookup which requires extra API calls.',
                     str(region) or GLOBAL_SCOPE_NAME)
      return region

    if fail_if_not_found:
      raise gcutil_errors.CommandError(
          'Resource not found: %s' % resource_name)
    else:
      return None

  def GetListResultForResourceWithZone(
      self, api, resource_name, fail_if_not_found=True, zone=None,
      project=None):
    """Gets the result of api.list for a given resource, with zone.

    The function first tries to use 'zone' flag if set, but falls back
    to searching for the resource name across zones.

    Args:
      api: The API service that must expose 'list' method.
      resource_name: Name of the resource to find.
      fail_if_not_found: Raise an error when the resource is not found.
      zone: Zone to check.
      project:  Project to check.

    Returns:
      List result for the given resource, with all relevant information.

    Raises:
      CommandError: If the zone for the resource cannot be resolved.
    """
    # If the resource is already project- and zone-qualified, use the zone.
    if not resource_name:
      return None

    filter_expression = ('name eq %s' %
                         self.DenormalizeResourceName(resource_name))

    if not project:
      project = self._project

    items = []
    # In each case, limit the number of results to 2.  Anything more than 1 is
    # an error.
    if zone:
      sub_result = utils.All(api.list,
                             project,
                             max_results=2,
                             filter=filter_expression,
                             zone=zone)
      items.extend(sub_result.get('items', []))
    else:
      for search_zone in self._GetZones():
        sub_result = utils.All(api.list,
                               project,
                               max_results=2,
                               filter=filter_expression,
                               zone=search_zone)
        sub_items = sub_result.get('items', [])
        if sub_items:
          LOGGER.warning('Consider passing \'--zone=%s\' to avoid the '
                         'unnecessary zone lookup which requires extra API '
                         'calls.', str(search_zone))
        items.extend(sub_items)

    if len(items) > 1:
      raise gcutil_errors.CommandError(
          'More than one result found for resource \'%s\'.' %
          str(resource_name))
    elif len(items) == 1:
      return items[0]
    elif fail_if_not_found:
      raise gcutil_errors.CommandError(
          'Resource \'%s\' not found.' % str(resource_name))
    else:
      return None

  def GetZoneForResource(self, api, resource_name, fail_if_not_found=True,
                         project=None):
    """Gets the unqualified zone name for a given resource.

    The function first tries to use 'zone' flag if set, but falls back
    to searching for the resource name across zones.

    Args:
      api: The API service that must expose 'list' method.
      resource_name: Name of the resource to find.
      fail_if_not_found: Raise an error when the resource is not found.
      project: Project to use.

    Returns:
      Unqualified name of the zone the resource belongs to.

    Raises:
      CommandError: If the zone for the resource cannot be resolved.
    """
    # If the resource is already project- and zone-qualified, use the zone.
    if not resource_name:
      return None

    if not project:
      project = self._project

    resource_name_parts = self._presenter.StripBaseUrl(resource_name).split('/')
    if (len(resource_name_parts) > 3 and
        resource_name_parts[0] == 'projects' and
        resource_name_parts[2] == 'zones'):
      return resource_name_parts[3]

    if hasattr(self._flags, 'zone') and self._flags.zone:
      return self._flags.zone

    items = []
    filter_expression = ('name eq %s' %
                         self.DenormalizeResourceName(resource_name))

    # Limiting the number of results to 2, since zero results means that we
    # failed to find the resource and 2 means that it is duplicated somehow.
    aggregated_items = utils.AllAggregated(
        api.aggregatedList, project, max_results=2,
        filter=filter_expression)

    for scope in aggregated_items['items']:
      for collection in aggregated_items['items'][scope]:
        if collection != 'warning':
          items += aggregated_items['items'][scope][collection]

    if len(items) == 1:
      zone = self._GetZoneFromSelfLink(items[0]['selfLink'])
      LOGGER.info('Zone for %s detected as %s.', str(resource_name),
                  str(zone or GLOBAL_SCOPE_NAME))
      return zone

    if not items:
      if fail_if_not_found:
        raise gcutil_errors.CommandError(
            'The zone could not be determined for resource: %s' % resource_name)
      else:
        return None
    else:
      raise gcutil_errors.CommandError(
          'Multiple results found for resource: %s' % resource_name)

  def _GetRegionFromSelfLink(self, self_link):
    (scope_type, scope_name) = self._GetScopeFromSelfLink(self_link)
    if scope_type == 'regions':
      return scope_name
    return None

  def _GetZoneFromSelfLink(self, self_link):
    """Parses the given self-link and returns per-project zone name."""
    (scope_type, scope_name) = self._GetScopeFromSelfLink(self_link)
    if scope_type == 'zones':
      return scope_name
    return None

  def _GetScopeFromSelfLink(self, self_link):
    """Parses the given self-link and returns the scope name and type."""
    allowed_scope_types = ('zones', 'regions')
    resource_name = self._presenter.StripBaseUrl(self_link)
    parts = resource_name.split('/')
    # projects/<project>/<scope>
    if len(parts) >= 3 and parts[0] == 'projects':
      if parts[2] == 'global':
        return ('global', '')
      elif len(parts) > 3 and parts[2] in allowed_scope_types:
        return (parts[2], parts[3])

    return (None, None)

  def _HandleSafetyPrompt(self, positional_arguments):
    """If a safety prompt is present on the class, handle it now.

    By defining a field 'safety_prompt', derived classes can request
    that the user confirm a dangerous operation prior to execution,
    e.g. deleting a resource.  Users may override this check by
    passing the --force flag on the command line.

    Args:
      positional_arguments: A list of positional argument strings.

    Returns:
      True if the command should continue, False if not.
    """
    if hasattr(self, 'safety_prompt'):
      if not self._flags.force:
        prompt = self.safety_prompt
        if positional_arguments:
          prompt = '%s %s' % (prompt, ', '.join(positional_arguments))
        return self._PresentSafetyPrompt(prompt)

    return True

  def _PresentSafetyPrompt(self, prompt, default=None):
    """Present a safety prompt to the user.

    Present a custom safety prompt to the user.  May be used
    independent of flags or presence of a safety_prompt field.

    Args:
      prompt: The prompt to present.
      default: Default value to return if --force is specified.
               If none, it will ask anyway.

    Returns:
      True if the user selected yes, False if the user selected no.

    Raises:
      IOError: If stdin is not a tty, and input is required.
    """
    if default is not None and self._flags.force:
      return default

    print '%s? [y/n]' % prompt

    userinput = None

    if not sys.stdin.isatty() and self._flags.require_tty:
      raise IOError('Cannot read from stdin: not a tty. '
                    'Use --force to override prompts.')

    while userinput != 'y' and userinput != 'n':
      userinput = raw_input('>>> ')
      userinput = userinput.lstrip()[:1].lower()

    return userinput == 'y'

  def _IsUsingAtLeastApiVersion(self, required_version):
    """Determine if in-use API version is at least the specified version.

    Args:
      required_version: The API version to test.

    Returns:
      True if the given API version is equal or newer than the in-use
      API version, False otherwise.
    """
    return self.api.version >= required_version

  def _GetResourceApiKind(self, resource):
    """Determine the API version driven resource 'kind'.

    Args:
      resource: The resource type to generate a 'kind' string for.

    Returns:
      A string containing the API 'kind'
    """
    return 'compute#%s' % resource

  def _ErrorInResult(self, result):
    """Return True if a result should be considered an error."""
    ops = []
    if self.IsResultAnOperation(result):
      ops = [result]
    elif self.IsResultAggregatedList(result):
      return 'errors' in result
    elif self.IsResultAList(result):
      ops = result.get('items', [])
    for op in ops:
      # If op contains errors, it will be of the form:
      #   {'error': {'errors': [...]}, ...}
      if (self._flags.synchronous_mode and
          op.get('error', {}).get('errors', [])):
        return True
    return False

  def _ErrorsInResultList(self, result_list):
    """Returns True if list of results contains an operation with error."""
    if result_list:
      for result in result_list:
        if (self.IsResultAnOperation(result) and
            result.get('error', {}).get('errors', [])):
          return True
    return False

  def _InitializeContextParser(self):
    """Initializes the context_parser for this command and service version."""
    self._context_parser = api_context_parser.ApiContextParser(
        self._flags.service_version, self._flags.api_host)

    def _GetProjectContext(unused_object_type, unused_context):
      if self._flags.project:
        return self.DenormalizeResourceName(self._flags.project)
      raise app.UsageError(
          'Please specify a project by using a fully-specified path '
          'or the --project flag.')

    def _GetRegionContext(unused_object_type, unused_context):
      if self._flags.region:
        return self.DenormalizeResourceName(self._flags.region)
      return self._presenter.PromptForRegion(self.api.regions)['name']

    def _GetZoneContext(unused_object_type, unused_context):
      if self._flags.zone:
        return self.DenormalizeResourceName(self._flags.zone)
      return self._presenter.PromptForZone(self.api.zones)['name']

    self._context_parser.context_prompt_fxns['project'] = _GetProjectContext
    self._context_parser.context_prompt_fxns['region'] = _GetRegionContext
    self._context_parser.context_prompt_fxns['zone'] = _GetZoneContext

  def Run(self, argv):
    """Run the command, printing the result.

    Args:
      argv: The arguments to the command.

    Returns:
      0 if the command completes successfully, otherwise 1.
    """
    try:
      pos_arg_values = self._ParseArgumentsAndFlags(FLAGS, argv)
      gcutil_logging.SetupLogging()

      # Synchronize the flags with any cached values present.
      flags_cache_obj = flags_cache.FlagsCache()
      flags_cache_obj.SynchronizeFlags()


      self.SetFlagDefaults()
      self.DenormalizeProjectName(FLAGS)
      self.SetFlags(FLAGS)
      self._InitializeContextParser()

      has_errors = True

      for attempt in ('initial', 'auth_retry'):
        try:
          result, exceptions = self.RunWithFlagsAndPositionalArgs(
              self._flags, pos_arg_values)

          has_errors = bool(exceptions or self._ErrorInResult(result))
          self.PrintResult(result)
          self.LogExceptions(exceptions)

          # If we just have an AccessTokenRefreshError raise it so
          # that we retry.
          token_errors = [e for e in exceptions if
                          isinstance(e, oauth2_client.AccessTokenRefreshError)]
          if token_errors:
            if not result:
              raise token_errors[0]
            LOGGER.warning(
                'Refresh error when running multiple operations. Not '
                'automatically retrying as some requests succeeded.')

          # If nothing has been raised, we're done.
          break
        except oauth2_client.AccessTokenRefreshError, e:
          if attempt == 'auth_retry':
            raise
          # Retrying the operation will induce OAuth2 reauthentication and
          # creation of the new refresh token.
          LOGGER.info('OAuth2 token refresh error (%s), retrying.\n', e)

      # Updates the flags cache file only when the command exits with
      # a non-zero error code.
      if not has_errors:
        flags_cache_obj.UpdateCacheFile()

      return has_errors
    except errors.HttpError, http_error:
      self.LogHttpError(http_error)
      return 1
    except app.UsageError:
      raise
    except SystemExit as e:
      return e.code
    except:
      sys.stderr.write('%s\n' % '\n'.join(
          traceback.format_exception_only(sys.exc_type, sys.exc_value)))
      LOGGER.debug(traceback.format_exc())
      return 1

  def CreateHttp(self):
    """Construct an HTTP object to use with an API call.

    This is useful when doing multithreaded work as httplib2 Http
    objects aren't threadsafe.

    Returns:
      An object that implements the httplib2.Http interface
    """
    http = utils.GetHttp()

    http = self._AuthenticateWrapper(http)
    return http

  def RunWithFlagsAndPositionalArgs(self, flag_values, pos_arg_values):
    """Run the command with the parsed flags and positional arguments.

    This method is what a subclass should override if they do not want
    to use the REST API.

    Args:
      flag_values: The parsed FlagValues instance.
      pos_arg_values: The positional arguments for the Handle method.

    Raises:
      CommandError: If user choses to not proceed with the command at safety
          prompt.

    Returns:
      A tuple (result, exceptions) where results is a
      JSON-serializable result and exceptions is a list of exceptions
      that were thrown when running this command.
    """
    http = self.CreateHttp()
    self.api = gce_api.CreateComputeApi(
        http, flag_values.service_version, flag_values.fetch_discovery,
        flag_values.api_host)

    if not self._HandleSafetyPrompt(pos_arg_values):
      raise gcutil_errors.CommandError('Operation aborted')

    exceptions = []
    result = self.Handle(*pos_arg_values)
    if isinstance(result, tuple):
      result, exceptions = result
    if self._flags.synchronous_mode:
      result = self.WaitForOperation(
          flag_values.max_wait_time, flag_values.sleep_between_polls,
          self._timer, result)
    if isinstance(result, list):
      result = self.MakeListResult(result, 'operationList')

    return result, exceptions

  def IsResultAnOperation(self, result):
    """Determine if the result object is an operation."""
    try:
      return ('kind' in result
              and result['kind'].endswith('#operation'))
    except TypeError:
      return False

  def IsResultAList(self, result):
    """Determine if the result object is a list of some sort."""
    try:
      return ('kind' in result
              and result['kind'].endswith('List'))
    except TypeError:
      return False

  def IsResultAggregatedList(self, result):
    """Determine if the result object is an aggregated list."""
    try:
      return ('kind' in result
              and result['kind'].endswith('AggregatedList'))
    except TypeError:
      return False

  def MakeListResult(self, results, kind_base):
    """Given an array of results, create an list object for those results.

    Args:
      results: The list of results.
      kind_base: The kind of list to create

    Returns:
      A synthetic list resource created from the list of individual results.
    """
    return {
        'kind': self._GetResourceApiKind(kind_base),
        'items': results,
        'note': ('This JSON result is based on multiple API calls. This '
                 'object was created in the client.')
        }

  def ExecuteRequests(self, requests, wait_for_operations=None,
                      timeout_seconds=None, sleep_between_polls_seconds=None,
                      collection_name=None):
    """Execute a list of requests in a thread pool.

    Args:
      requests: A list of requests objects to execute.
      wait_for_operations: Wait for asynchronous operations to complete.
      timeout_seconds: Total number of seconds to wait for the operation to
          complete. If negative, waits indefinitely.
          If set to None, default of _flags.max_wait_time will be used.
      sleep_between_polls_seconds: Number of seconds to wait between polling the
          asynchronous operation.
          If set to None, default of _flags.sleep_between_polls will be used.
      collection_name: The name of the collection. This is optional and is
          useful for subclasses that mutate more than one resource type.

    Returns:
      A tuple with (results, exceptions) where result list is the list
      of all results and exceptions is any exceptions that were
      raised.
    """
    if wait_for_operations is None:
      wait_for_operations = self._flags.synchronous_mode
    if timeout_seconds is None:
      timeout_seconds = self._flags.max_wait_time
    if sleep_between_polls_seconds is None:
      sleep_between_polls_seconds = self._flags.sleep_between_polls

    tp = thread_pool.ThreadPool(self._flags.concurrent_operations,
                                self.THREAD_POOL_WAIT_TIME)
    ops = []
    for request in requests:
      op = ApiThreadPoolOperation(
          request, self, wait_for_operations,
          timeout_seconds, sleep_between_polls_seconds, timer=self._timer,
          collection_name=collection_name)
      ops.append(op)
      tp.Add(op)
    tp.WaitShutdown()
    results = []
    exceptions = []
    for op in ops:
      if op.RaisedException():
        exceptions.append(op.Result())
      else:
        if isinstance(op.Result(), list):
          results.extend(op.Result())
        else:
          results.append(op.Result())
    return (results, exceptions)

  def WaitForOperation(self, timeout_seconds, sleep_between_polls_seconds,
                       timer, result, http=None, collection_name=None,
                       max_retries=3):
    """Wait for a potentially asynchronous operation to complete.

    Args:
      timeout_seconds: Total number of seconds to wait for the operation to
          complete. If negative, waits indefinitely.
      sleep_between_polls_seconds: Number of seconds to wait between polling the
          asynchronous operation.
      timer: An implementation of the time object, providing time and sleep
          methods.
      result: The result of the request, potentially containing an operation.
      http: An optional httplib2.Http object to use for requests.
      collection_name: The name of the collection.
      max_retries: The maximum number of times to retry a failed http request.

    Returns:
      The synchronous return value, usually an operation object.
    """
    resource = None
    if not self.IsResultAnOperation(result):
      return result

    start_time = timer.time()
    operation_type = result['operationType']
    target = result['targetLink'].split('/')[-1]

    while result['status'] != 'DONE':
      if timeout_seconds >= 0 and timer.time() - start_time >= timeout_seconds:
        LOGGER.warn('Timeout reached. %s of %s has not yet completed. '
                    'The operation (%s) is still %s.',
                    str(operation_type), str(target), str(result['name']),
                    str(result['status']))
        break  # Timeout

      collection_name = (collection_name
                         or getattr(self, 'resource_collection_name', None))
      if collection_name:
        singular_collection_name = utils.Singularize(collection_name)
        qualified_name = '%s %s' % (singular_collection_name, target)
      else:
        qualified_name = target

      LOGGER.info('Waiting for %s of %s. Sleeping for %ss.',
                  str(operation_type),
                  str(qualified_name),
                  str(sleep_between_polls_seconds))
      timer.sleep(sleep_between_polls_seconds)

      kwargs = {
          'project': self._project,
          'operation': result['name'],
      }

      poll_api = self.api.global_operations

      (scope_type, scope_name) = self._GetScopeFromSelfLink(
          result['selfLink'])
      if scope_type == 'zones':
        kwargs['zone'] = scope_name
        poll_api = self.api.zone_operations
      elif scope_type == 'regions':
        kwargs['region'] = scope_name
        poll_api = self.api.region_operations

      # Poll the operation for status.
      request = poll_api.get(**kwargs)
      result = request.execute(http=http)
    else:
      if result['operationType'] != 'delete' and 'error' not in result:
        # We are going to replace the operation with its resulting resource.
        # Save the operation to return as well.
        target_link = result['targetLink']
        http = self.CreateHttp()
        for i in xrange(max_retries):
          try:
            response, data = http.request(target_link, method='GET')
            if 200 <= response.status <= 299:
              resource = json.loads(data)
            break
          except httplib.BadStatusLine:
            LOGGER.warn('Transient error, retrying in %ss.' % 2 ** i)
            time.sleep(2 ** i)
    if resource is not None:
      results = []
      results.append(result)
      results.append(resource)
      return results
    return result

  def CommandGetHelp(self, unused_argv, cmd_names=None):
    """Get help for command.

    Args:
      unused_argv: Remaining command line flags and arguments after parsing
                   command (that is a copy of sys.argv at the time of the
                   function call with all parsed flags removed); unused in this
                   implementation.
      cmd_names:   By default, if help is being shown for more than one command,
                   and this command defines _all_commands_help, then
                   _all_commands_help will be displayed instead of the class
                   doc. cmd_names is used to determine the number of commands
                   being displayed and if only a single command is display then
                   the class doc is returned.

    Returns:
      __doc__ property for command function or a message stating there is no
      help.
    """
    help_str = super(
        GoogleComputeCommand, self).CommandGetHelp(unused_argv, cmd_names)

    # Do not flood the terminal with the usage blocks if the user is asking
    # for a list of several commands.
    if cmd_names and len(cmd_names) > 1:
      return help_str
    return '%s\n\nUsage: %s' % (help_str, self._GetUsage())

  def _GetUsage(self):
    """Get the usage string for the command, used to print help messages.

    Returns:
      The usage string for the command.
    """
    res = '%s [--global_flags] %s [--command_flags]' % (
        os.path.basename(sys.argv[0]), self._command_name)

    args = getattr(self, 'positional_args', None)
    if args:
      res = '%s %s' % (res, args)

    return res

  def Handle(self):
    """Actual implementation of the command.

    Derived classes override this method, adding positional arguments
    to this method as required.

    Returns:
      Either a single JSON-serializable result or a tuple of a result
      and a list of exceptions that are thrown.
    """
    raise NotImplementedError()

  def SetFlags(self, flag_values):
    """Set the flags to be used by the command.

    Args:
      flag_values: The parsed flags values.
    """
    self._flags = flag_values
    self._project = self._flags.project
    self._presenter = Presenter(
        flag_values=flag_values,
        is_using_at_least_api_version=self._IsUsingAtLeastApiVersion)

  def GetFlags(self):
    """Get the flags object used by the command."""
    return self._flags

  def GetPrintSpec(self):
    """Returns collection specific resource print specification.

    By default, returns value of print_spec attribute or an empty spec.
    Override for version specific behavior or more advanced customization.

    Returns:
        The ResourcePrintSpec object for the resource type.
    """
    print_spec = getattr(self, 'print_spec', None)
    if print_spec is None:
      print_spec = ResourcePrintSpec([], tuple(), tuple(), None)
    return print_spec

  def SetApi(self, api):
    self.api = api

  def _FlattenObjectToList(self, instance_json, name_map):
    """Convert a json instance to a dictionary for output.

    Args:
      instance_json: A JSON object represented as a python dict.
      name_map: A list of key, json-path object tuples where the
          json-path object is either a string or a list of strings.
          ('name', 'container.id') or
          ('name', ['container.id.new', 'container.id.old'])

    Returns:
      A list of extracted values selected by the associated JSON path.  In
      addition, names are simplified to their shortest path components.
    """

    def ExtractSubKeys(json_object, subkey):
      """Extract and flatten a (possibly-repeated) field in a json object.

      Args:
        json_object: A JSON object represented as a python dict.
        subkey: a list of path elements, e.g. ['container', 'id'].

      Returns:
        [element1, element2, ...] or [] if the subkey could not be found.
      """
      if not subkey:
        return [self._presenter.PresentElement(json_object)]
      if subkey[0] in json_object:
        element = json_object[subkey[0]]
        if isinstance(element, list):
          return sum([ExtractSubKeys(x, subkey[1:]) for x in element], [])
        return ExtractSubKeys(element, subkey[1:])
      return []

    ret = []
    for unused_key, paths in name_map:
      # There may be multiple possible paths indicating the field name due to
      # versioning changes.  Walk through them in order until one is found.
      if isinstance(paths, basestring):
        elements = ExtractSubKeys(instance_json, paths.split('.'))
      else:
        for path in paths:
          elements = ExtractSubKeys(instance_json, path.split('.'))
          if elements:
            break

      ret.append(','.join([str(x) for x in elements]))
    return ret

  def GetErrorsForOperation(self, result):
    """Returns an associative list of all errors in the result.

    Args:
      result: The dict returned by the server.

    Returns:
      A list.
    """
    if 'error' not in result:
      return []

    data = []
    for error in result['error']['errors']:
      error_info = []
      error_info.append(('error', error['code']))
      error_info.append(('message', error['message']))
      data.append(('error', error_info))

    return data

  def LogExceptions(self, exceptions):
    """Log a list of exceptions returned in multithreaded operation."""
    for exception in exceptions:
      if isinstance(exception, errors.HttpError):
        self.LogHttpError(exception)
      elif isinstance(exception, Exception):
        sys.stderr.write('%s\n' % '\n'.join(traceback.format_exception_only(
            type(exception).__name__, exception)))

  def LogHttpError(self, http_error):
    """Do specific logging when we hit an HttpError."""

    def AddMessage(messages, error):
      msg = error.get('message')
      if msg:
        messages.add(msg)

    message = http_error.resp.reason
    try:
      data = json.loads(http_error.content)
      messages = set()
      if isinstance(data, dict):
        error = data.get('error', {})
        AddMessage(messages, error)
        for error in error.get('errors', []):
          AddMessage(messages, error)
      message = '\n'.join(messages)
    except ValueError:
      pass

    sys.stderr.write('Error: %s\n' % message)
    # Log the full error response for debugging purposes.
    LOGGER.debug(http_error.resp)
    LOGGER.debug(http_error.content)

  def PrintResult(self, result):
    """Pretty-print the result of the command.

    If a class defines a list of ('title', 'json.field.path') values named
    'fields', this list will be used to print a table of results using
    prettytable.  If self.fields does not exist, result will be printed as
    pretty JSON.

    Note that if the result is either an Operations object or an
    OperationsList, it will be special cased and formatted
    appropriately.

    Args:
      result: A JSON-serializable object to print.
    """
    if self._flags.print_json or self._flags.format == 'json':
      # We could have used the pprint module, but it produces
      # noisy output due to all of our keys and values being
      # unicode strings rather than simply ascii.
      print json.dumps(result, sort_keys=True, indent=2)
      return

    if self._flags.format == 'yaml':
      yaml.add_representer(
          collections.OrderedDict,
          yaml.dumper.SafeRepresenter.represent_dict,
          Dumper=yaml.dumper.SafeDumper)
      yaml.safe_dump(
          result,
          stream=sys.stdout,
          default_flow_style=False,
          indent=2,
          explicit_start=True)
      return

    if result:
      # Warn the user about errors.
      self._WarnAboutErrors(result)

      if self._flags.format == 'names':
        self._PrintNamesOnly(result)
      elif self.IsResultAggregatedList(result):
        self._PrintAggregatedList(result)
      elif self.IsResultAList(result):
        self._PrintList(result)
      else:
        self._PrintDetail(result)

  AGGREGATED_TYPES = {
      'compute#instanceAggregatedList': 'instances',
      'compute#machineTypeAggregatedList': 'machineTypes',
      'compute#operationAggregatedList': 'operations',
      'compute#addressAggregatedList': 'addresses',
      'compute#diskAggregatedList': 'disks',
      'compute#diskTypeAggregatedList': 'diskTypes',
      }

  def _WarnAboutErrors(self, result):
    """Logs any errors that appear in the result."""
    def PrintWarning(item):
      for error in item.get('error', {}).get('errors', []):
        LOGGER.error('{0}: {1}'.format(
            error.get('code', '<no error code returned>'),
            error.get('message', '<no message returned>')))

      for warning in item.get('warnings', []):
        LOGGER.warn('{0}: {1}'.format(
            warning.get('code', '<no warning code returned>'),
            warning.get('message', '<no message returned>')))

    if self.IsResultAList(result):
      if isinstance(result.get('items', []), dict):
        for item in result.get('items', []).values():
          PrintWarning(item)
      else:
        for item in result.get('items', []):
          PrintWarning(item)
    else:
      PrintWarning(result)

  def _PrintNamesOnly(self, result):
    """Prints only names of the resources returned by Google Compute Engine API.

    Args:
      result: A GCE List resource to print.
    Raises:
      CommandError: if the List resource is an unknown kind of aggregated list.
    """

    if self.IsResultAList(result):
      kind = result.get('kind', '')
      if 'AggregatedList' in kind:
        aggregated_resource_type = self.AGGREGATED_TYPES.get(kind)
        if aggregated_resource_type:
          items_by_scope = result.get('items', [])
          results = []
          for value in items_by_scope.itervalues():
            results.extend(value.get(aggregated_resource_type, []))
          results = [self._presenter.AbbreviateURL(item.get('selfLink', ''))
                     for item in results]
        else:
          raise gcutil_errors.CommandError(
              'Unrecognized kind of aggregated list.')
      else:
        results = [r.get('name', '') for r in result.get('items', [])]
    else:
      results = [result.get('name', '')]

    for result in results:
      print result

  def _CreateFormatter(self):
    table_format = self._flags.format

    # For backwards compatibility.
    if self._flags.format == 'sparse':
      table_format = 'table'

    return table.CreateTable(
        table_format,
        width=None if FLAGS.respect_terminal_width else -1)

  def _PartitionResults(self, result):
    """Partitions results into operations and non-operation resources."""
    res = []
    ops = []
    for obj in result.get('items', []):
      if self.IsResultAnOperation(obj):
        ops.append(obj)
      else:
        res.append(obj)
    return res, ops

  def _PrintList(self, result):
    """Prints a result which is a Google Compute Engine List resource.

    For the result of batch operations, splits the result list into
    operations and other resources and possibly prints two tables. The
    operations typically represent errors (unless printing results of
    listoperations command) whereas the real resources typically
    represent successfully completed operations.

    Args:
      result: A GCE List resource to print.
    """
    # Split results into operations and the rest of resources.
    res, ops = self._PartitionResults(result)
    if res and ops:
      res_header = '\nTable of resources:\n'
      ops_header = '\nTable of operations:\n'
    else:
      res_header = ops_header = None

    if res or not ops:
      self._CreateAndPrintTable(res, res_header, self.GetPrintSpec().summary,
                                self.GetPrintSpec().field_mappings)

    if ops:
      self._CreateAndPrintTable(ops, ops_header,
                                self.GetOperationPrintSpec().summary,
                                self.GetOperationPrintSpec().field_mappings)

  def _CreateAndPrintTable(self, values, header, summary_fields, all_fields):
    """Creates a table representation of the list of resources and prints it.

    Args:
      values: List of resources to display.
      header: A header to print before the table (can be None).
      summary_fields: Summary field definition for the table.
      all_fields: Complete field definition for the table.
    """
    fields = [x for x in all_fields if x[0] in summary_fields]
    rows = [self._FlattenObjectToList(row, fields) for row in values]

    t = self._CreateFormatter()
    t.SetColumns(name for name, _ in fields)
    t.AppendRows(rows)

    if header:
      print header
    t.Write()

  def _PrintDetail(self, result):
    """Prints a detail view of the result which is an individual resource.

    Args:
      result: A resource to print.
    """
    if self.IsResultAnOperation(result):
      print_spec = self.GetOperationPrintSpec()
    else:
      print_spec = self.GetPrintSpec()

    if not print_spec or not print_spec.detail:
      return

    row_names = [x[0] for x in print_spec.detail]
    property_bag = self._FlattenObjectToList(result, print_spec.detail)

    data = []
    for i, v in enumerate(property_bag):
      data.append((row_names[i], v))

    # Handle customized printing of this result.
    # Operations are special cased here.
    if self.IsResultAnOperation(result):
      data += self.GetErrorsForOperation(result)
    elif hasattr(self, 'GetDetailRow'):
      data += self.GetDetailRow(result)

    t = table.CreateTable(table.Format.DETAILED)
    header, row = zip(*data)
    t.SetColumns(header)
    t.AppendRow(row)
    t.Write()

  def __GetRequiredAuthScopes(self):
    """Returns a list of scopes required for this command."""
    return scopes.DEFAULT_AUTH_SCOPES

  def SetFlagDefaults(self):
    if 'project' in FLAGS.FlagDict() and not FLAGS['project'].present:
      try:
        metadata = metadata_lib.Metadata()
        setattr(FLAGS, 'project', metadata.GetProjectId())
      except metadata_lib.MetadataError:
        pass



class GoogleComputeListCommand(GoogleComputeCommand):
  """Base class for list commands."""

  # Overload these values in derived classes if they represent collections
  # at non-global scopes.
  def IsZoneLevelCollection(self):
    return False

  def IsRegionLevelCollection(self):
    return False

  def IsGlobalLevelCollection(self):
    return True

  @property
  def skip_projects_not_found(self):
    return False

  def GetProjects(self):
    """List of projects to iterate list command over."""
    return [self._project]

  def FilterResults(self, results):
    """Filter results before returning them to user.

    Args:
      results: A dict of kind and items.
    Returns:
      A dict of kind and items.
    """
    return results

  def __init__(self, name, flag_values):
    """Initializes a new instance of a GoogleComputeListCommand.

    Args:
      name: The name of the command.
      flag_values: The values of command line flags to be used by the command.
    """
    super(GoogleComputeListCommand, self).__init__(name, flag_values)

    # Call the base class GetPrintSpec to extract the print specification
    # Because flags haven't been fully initialized, rely on the base behavior
    # only.
    print_spec = GoogleComputeCommand.GetPrintSpec(self)
    summary_fields = print_spec.summary

    if summary_fields:
      sort_fields = []
      for field in summary_fields:
        sort_fields.append(field)
        sort_fields.append('-' + field)

      gcutil_flags.DEFINE_case_insensitive_enum(
          'sort_by',
          None,
          sort_fields,
          'Sort output results by the given field name. Field '
          'names starting with a "-" will lead to a descending '
          'order.',
          flag_values=flag_values)

    flags.DEFINE_integer('max_results',
                         None,
                         'Maximum number of items to list [Default is to fetch'
                         ' all].',
                         lower_bound=1,
                         flag_values=flag_values)
    flags.DEFINE_string('filter',
                        None,
                        'Filter expression for filtering listed resources. '
                        'See gcutil documentation for syntax of the filter '
                        'expression here: http://developers.google.com'
                        '/compute/docs/gcutil/tips#filtering',
                        flag_values=flag_values)
    flags.DEFINE_bool('fetch_all_pages',
                      True,
                      'Deprecated flag.',
                      flag_values=flag_values)

    if hasattr(self, 'print_spec'):
      allowed_fields = '|'.join(
          ['all'] + [spec[0] for spec in self.print_spec.field_mappings])

      flags.DEFINE_list('columns',
                        None,
                        'A comma-separated list of the desired columns '
                        'to display. If \'all\' is specified, then '
                        'all possible columns will be included. '
                        'Valid columns are <%s>.' % allowed_fields,
                        flag_values=flag_values)

  def Handle(self):
    """Returns the result of list on a resource type."""
    if self._flags['fetch_all_pages'].present:
      LOGGER.warn('--fetch_all_pages has been deprecated')

    max_results = None
    if not self._flags.sort_by or self._flags.max_results:
      max_results = self._flags.max_results

    # Aggregated list.
    if (hasattr(self, 'ListAggregatedFunc') and
        not utils.IsAnyScopeFlagSpecified(self._flags)):
      return self.FilterResults(utils.AllAggregated(
          self.ListAggregatedFunc(),
          self.GetProjects(),
          max_results=max_results,
          filter=self._flags.filter,
          skip_if_not_found=self.skip_projects_not_found))

    # Accumulate results.
    results = None
    # Query zone level collection if appropriate.
    if self.IsZoneLevelCollection():
      results = utils.CombineListResults(
          results, self._ListZoneLevelCollection(max_results))

    # Query region level collection if appropriate.
    if self.IsRegionLevelCollection():
      results = utils.CombineListResults(
          results, self._ListRegionLevelCollection(max_results))

    # Query global collection if appropriate.
    if self._ShouldQueryGlobalCollection():
      results = utils.CombineListResults(
          results, utils.All(
              self.ListFunc(),
              self.GetProjects(),
              max_results=max_results,
              filter=self._flags.filter,
              skip_if_not_found=self.skip_projects_not_found))
    return self.FilterResults(results)

  def _ShouldQueryGlobalCollection(self):
    """Determines whether the command should query global level collection."""
    if not self.IsGlobalLevelCollection():
      # Cannot query global collection if it is not global.
      return False
    elif not utils.IsAnyScopeFlagSpecified(self._flags):
      # Global collection and no constraint was specified. Query it.
      return True

    # Global and region-level collection
    if self.IsRegionLevelCollection():
      # Global/Region collection and --global was specified.
      if 'global' in self._flags and self._flags['global'].value:
        return True

    if self.IsZoneLevelCollection():
      # Global/Zone collection and --global was specified.
      if 'global' in self._flags and self._flags['global'].value:
        return True

      # Zone was specified. If it is 'global' we query global collection,
      # Otherwise we don't (specific zone being specified and --global is not).
      if 'zone' in self._flags:
        if self._flags.zone == GLOBAL_SCOPE_NAME:
          # Deprecated behavior --zone global
          LOGGER.warn(
              '--zone \'%s\' flag is deprecated; use --global instead' %
              GLOBAL_SCOPE_NAME)
          return True

    # Scope has been specified and it is not --global in accepted scenarios.
    return False

  def _ListZoneLevelCollection(self, max_results=None):
    """Returns the result of zone-scoped list on a resource type.

    If zone was specified via --zone flag, only that zone will be listed.
    If no zone was specified, list all resources in all zones.

    Args:
      max_results: Maximum results to return.

    Returns:
      Result of the zone-scoped list operation.
    """
    zones = []  # Zones to query.
    if 'zone' in self._flags and self._flags.zone:
      if not (self.IsGlobalLevelCollection() and
              self._flags.zone == GLOBAL_SCOPE_NAME):
        zones.append(self.DenormalizeResourceName(self._flags.zone))
    elif not utils.IsAnyScopeFlagSpecified(self._flags):
      zones.extend(self._GetZones())

    results = None  # Accumulate results.
    list_func = self.ListZoneFunc()
    for zone in zones:
      results = utils.CombineListResults(
          results, utils.All(list_func,
                             self.GetProjects(),
                             max_results,
                             self._flags.filter,
                             zone=zone))
    return results

  def _ListRegionLevelCollection(self, max_results=None):
    """Returns the result of region-scoped list on a resource type.

    If region was specified via --region flag, only list resources in that
    region.
    If no region was specified, list all resources in all regions.

    Args:
      max_results: Maximum results to return.

    Returns:
      Result of the region-scoped list operation.
    """
    regions = []
    if 'region' in self._flags and self._flags.region:
      regions.append(self.DenormalizeResourceName(self._flags.region))
    elif not utils.IsAnyScopeFlagSpecified(self._flags):
      regions.extend(self._GetRegions())

    results = None  # Accumulate results.
    list_func = self.ListRegionFunc()
    for region in regions:
      results = utils.CombineListResults(
          results, utils.All(list_func,
                             self.GetProjects(),
                             max_results,
                             self._flags.filter,
                             region=region))
    return results

  def _GetDesiredColumnsAndSpecs(self, default_print_spec, master_print_spec):
    """Get the print specs for this operation given the specified flags.

    Args:
      default_print_spec: The default print spec to use, if the flag is
        unspecified.
      master_print_spec: A list of all possible columns and associated fields.

    Returns:
      A tuple (column_names, print_specs), corresponding to column names and
      the associated row fields.

    Raises:
      UsageError: Invalid field given.
    """
    if self._flags.columns and 'all' in self._flags.columns:
      column_names = [x[0] for x in master_print_spec]
    elif self._flags.columns:
      column_names = self._flags.columns
    else:
      column_names = [x for x in default_print_spec]

    # Pull the desired print specs out of the master list.
    desired_specs = []
    for col in column_names:
      specs = [spec for spec in master_print_spec if spec[0] == col]
      if specs:
        desired_specs.extend(specs)
      else:
        raise app.UsageError(
            'Invalid field: %s. Valid columns are <%s>.' %
            (col, '|'.join(spec[0] for spec in master_print_spec)))

    return column_names, desired_specs

  def _PrintAggregatedList(self, result):
    """Prints a result which is a GCE Aggregated List resource."""
    # Confirm that the user has selected valid columns before printing.

    self._GetDesiredColumnsAndSpecs(
        self.GetPrintSpec().summary, self.GetPrintSpec().field_mappings)

    if 'items' in result:
      all_items = []
      for obj in result['items'].values():
        collection_name = self.resource_collection_name
        if collection_name in obj:
          all_items += obj[collection_name]
        if ('warning' in obj and
            obj['warning']['code'] != 'NO_RESULTS_ON_PAGE'):
          LOGGER.warn(obj['warning']['message'])

      self._PrintList({'items': all_items})

  def _PrintList(self, result):
    """Prints a table for the given resources."""
    items = result.get('items', [])
    print_spec = self.GetPrintSpec()

    column_names, row_spec = self._GetDesiredColumnsAndSpecs(
        print_spec.summary, print_spec.field_mappings)

    rows = [self._FlattenObjectToList(row, row_spec)
            for row in items]

    sort_col = self._flags.sort_by
    if not sort_col:
      sort_col = print_spec.sort_by
    if sort_col:
      reverse = False
      if sort_col.startswith('-'):
        reverse = True
        sort_col = sort_col[1:]

      if sort_col in column_names:
        sort_col_idx = column_names.index(sort_col)
        rows = sorted(rows, key=(lambda row: row[sort_col_idx]),
                      reverse=reverse)
      else:
        LOGGER.warn('Invalid sort column: ' + str(sort_col))

    if self._flags.max_results is not None:
      rows = rows[:self._flags.max_results]

    t = self._CreateFormatter()
    t.SetColumns(column_names)
    t.AppendRows(rows)
    t.Write()
