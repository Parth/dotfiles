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

"""Commands for interacting with Google Compute Engine HTTP health checks."""



from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base

FLAGS = flags.FLAGS


class HttpHealthCheckCommand(command_base.GoogleComputeCommand):
  """Base command for working with the HTTP health check collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'host', 'port'],
      field_mappings=(
          ('name', 'name'),
          ('description', 'description'),
          ('host', 'host'),
          ('port', 'port'),
          ('request-path', 'requestPath')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('host', 'host'),
          ('port', 'port'),
          ('request-path', 'requestPath'),
          ('check-interval-sec', 'checkIntervalSec'),
          ('check-timeout-sec', 'timeoutSec'),
          ('unhealthy-threshold', 'unhealthyThreshold'),
          ('healthy-threshold', 'healthyThreshold')),
      sort_by='name')

  resource_collection_name = 'httpHealthChecks'

  # The default health check host.
  DEFAULT_HOST = ''

  # The default health check port.
  DEFAULT_PORT = 80

  # The default health check request path.
  DEFAULT_REQUEST_PATH = '/'

  # The default health check interval in seconds.
  DEFAULT_CHECK_INTERVAL_SEC = 5

  # The default health check timeout in seconds.
  DEFAULT_CHECK_TIMEOUT_SEC = 5

  # The default number of failures before marking a VM unhealthy.
  DEFAULT_UNHEALTHY_THRESHOLD = 2

  # The default number of successes before marking a VM healthy.
  DEFAULT_HEALTHY_THRESHOLD = 2

  def __init__(self, name, flag_values):
    super(HttpHealthCheckCommand, self).__init__(name, flag_values)


class AddHttpHealthCheck(HttpHealthCheckCommand):
  """Create a new HTTP health check to handle network load balancing."""

  positional_args = '<http-health-check-name>'

  def __init__(self, name, flag_values):
    super(AddHttpHealthCheck, self).__init__(name, flag_values)
    flags.DEFINE_string('description',
                        '',
                        'An optional HTTP health check description.',
                        flag_values=flag_values)
    flags.DEFINE_string('host',
                        self.DEFAULT_HOST,
                        'Specifies the value of the host header used in this '
                        'HTTP health check request. The default value is the '
                        'external IP address of the forwarding rule '
                        'associated with this target pool.',
                        flag_values=flag_values)
    flags.DEFINE_string('request_path',
                        self.DEFAULT_REQUEST_PATH,
                        'Specifies the request path of the HTTP health check '
                        'request. The default path is \'/\'.',
                        flag_values=flag_values)
    flags.DEFINE_string('port',
                        self.DEFAULT_PORT,
                        'Specifies the TCP port of the HTTP health check '
                        'request. The default port is \'80\'.',
                        flag_values=flag_values)
    flags.DEFINE_integer('check_interval_sec',
                         self.DEFAULT_CHECK_INTERVAL_SEC,
                         'Specifies how often, in seconds, to send a health '
                         'check. The default is 5 seconds.',
                         flag_values=flag_values)
    flags.DEFINE_integer('check_timeout_sec',
                         self.DEFAULT_CHECK_TIMEOUT_SEC,
                         'Specifies how long to wait, in seconds, before '
                         'the health check is considered a failure for each '
                         'individual instance. The default is 5 seconds. ',
                         flag_values=flag_values)
    flags.DEFINE_integer('unhealthy_threshold',
                         self.DEFAULT_UNHEALTHY_THRESHOLD,
                         'Specifies how many consecutive health check '
                         'failures must happen before a previously healthy '
                         'VM is marked unhealthy. The default is 2.',
                         flag_values=flag_values)
    flags.DEFINE_integer('healthy_threshold',
                         self.DEFAULT_HEALTHY_THRESHOLD,
                         'Specifies how many consecutive health check '
                         'successes must happen before a previously unhealthy '
                         'VM will be marked healthy. The default is 2.',
                         flag_values=flag_values)

  def Handle(self, http_health_check_name):
    """Add the specified HTTP health check.

    Args:
      http_health_check_name: The name of the HTTP health check to add.

    Returns:
      The result of inserting the HTTP health check.
    """
    http_health_check_context = self._context_parser.ParseContextOrPrompt(
        'httpHealthChecks', http_health_check_name)

    http_health_check_resource = {
        'kind': self._GetResourceApiKind('httpHealthCheck'),
        'name': http_health_check_context['httpHealthCheck'],
        'description': self._flags.description,
        'host': self._flags.host,
        'requestPath': self._flags.request_path,
        'port': self._flags.port,
        'checkIntervalSec': self._flags.check_interval_sec,
        'timeoutSec': self._flags.check_timeout_sec,
        'unhealthyThreshold': self._flags.unhealthy_threshold,
        'healthyThreshold': self._flags.healthy_threshold,
        }

    http_health_check_request = (self.api.http_health_checks.insert(
        project=http_health_check_context['project'],
        body=http_health_check_resource))
    return http_health_check_request.execute()


class UpdateHttpHealthCheck(HttpHealthCheckCommand):
  """Update an HTTP health check to handle network load balancing.

  Any fields left unset will be keep their original value.
  """

  positional_args = '<http-health-check-name>'
  safety_prompt = 'Update HTTP health check'

  def __init__(self, name, flag_values):
    super(UpdateHttpHealthCheck, self).__init__(name, flag_values)
    flags.DEFINE_string('description',
                        None,
                        'An optional HTTP health check description.',
                        flag_values=flag_values)
    flags.DEFINE_string('host',
                        None,
                        'Specifies a new value of the host header used in '
                        'this HTTP health check request.',
                        flag_values=flag_values)
    flags.DEFINE_string('request_path',
                        None,
                        'Specifies a new request path of the HTTP health '
                        'check request.',
                        flag_values=flag_values)
    flags.DEFINE_string('port',
                        None,
                        'Specifies a new TCP port of the HTTP health check '
                        'request.',
                        flag_values=flag_values)
    flags.DEFINE_integer('check_interval_sec',
                         None,
                         'Specifies how often, in seconds, to send a health '
                         'check.',
                         flag_values=flag_values)
    flags.DEFINE_integer('check_timeout_sec',
                         None,
                         'Specifies how long to wait, in seconds, before '
                         'the health check is considered a failure for each '
                         'individual instance.',
                         flag_values=flag_values)
    flags.DEFINE_integer('unhealthy_threshold',
                         None,
                         'Specifies how many consecutive health check '
                         'failures must happen before a previously healthy VM '
                         'is marked unhealthy.',
                         flag_values=flag_values)
    flags.DEFINE_integer('healthy_threshold',
                         None,
                         'Specifies how many consecutive health check '
                         'successes must happen before a previously unhealthy '
                         'VM will be marked healthy.',
                         flag_values=flag_values)

  def Handle(self, http_health_check_name):
    """Modify the specified HTTP health check.

    Args:
      http_health_check_name: The name of the HTTP health check to modify.

    Returns:
      The result of modifying the HTTP health check.
    """
    http_health_check_context = self._context_parser.ParseContextOrPrompt(
        'httpHealthChecks', http_health_check_name)

    http_hc_resource = {
        'kind': self._GetResourceApiKind('httpHealthCheck'),
        }
    if self._flags.description is not None:
      http_hc_resource['description'] = self._flags.description
    if self._flags.host is not None:
      http_hc_resource['host'] = self._flags.host
    if self._flags.request_path is not None:
      http_hc_resource['requestPath'] = self._flags.request_path
    if self._flags.port is not None:
      http_hc_resource['port'] = self._flags.port
    if self._flags.check_interval_sec is not None:
      http_hc_resource['checkIntervalSec'] = self._flags.check_interval_sec
    if self._flags.check_timeout_sec is not None:
      http_hc_resource['timeoutSec'] = self._flags.check_timeout_sec
    if self._flags.unhealthy_threshold is not None:
      http_hc_resource['unhealthyThreshold'] = self._flags.unhealthy_threshold
    if self._flags.healthy_threshold is not None:
      http_hc_resource['healthyThreshold'] = self._flags.healthy_threshold

    http_health_check_request = (self.api.http_health_checks.patch(
        httpHealthCheck=http_health_check_context['httpHealthCheck'],
        project=http_health_check_context['project'], body=http_hc_resource))
    return http_health_check_request.execute()


class GetHttpHealthCheck(HttpHealthCheckCommand):
  """Get an HTTP health check."""

  positional_args = '<http-health-check-name>'

  def __init__(self, name, flag_values):
    super(GetHttpHealthCheck, self).__init__(name, flag_values)

  def Handle(self, http_health_check_name):
    """Get the specified HTTP health check.

    Args:
      http_health_check_name: The name of the HTTP health check to get.

    Returns:
      The result of getting the HTTP health check.
    """
    http_health_check_context = self._context_parser.ParseContextOrPrompt(
        'httpHealthChecks', http_health_check_name)

    http_health_check_request = self.api.http_health_checks.get(
        project=http_health_check_context['project'],
        httpHealthCheck=http_health_check_context['httpHealthCheck'])

    return http_health_check_request.execute()


class DeleteHttpHealthCheck(HttpHealthCheckCommand):
  """Delete one or more HTTP health checks.

  If multiple HTTP health check names are specified, the HTTP health checks
  will be deleted in parallel.
  """

  positional_args = '<http-health-check-name-1> ... <http-health-check-name-n>'
  safety_prompt = 'Delete HTTP health check'

  def __init__(self, name, flag_values):
    super(DeleteHttpHealthCheck, self).__init__(name, flag_values)

  def Handle(self, *http_health_check_names):
    """Delete the specified HTTP health checks.

    Args:
      *http_health_check_names: The names of the HTTP health checks to delete.

    Returns:
      Tuple (results, exceptions) - results of deleting the HTTP health checks.
    """
    requests = []
    for name in http_health_check_names:
      http_health_check_context = self._context_parser.ParseContextOrPrompt(
          'httpHealthChecks', name)
      requests.append(self.api.http_health_checks.delete(
          project=http_health_check_context['project'],
          httpHealthCheck=http_health_check_context['httpHealthCheck']))
    results, exceptions = self.ExecuteRequests(requests)
    return (self.MakeListResult(results, 'operationList'), exceptions)


class ListHttpHealthChecks(HttpHealthCheckCommand,
                           command_base.GoogleComputeListCommand):
  """List the HTTP health checks for a project."""

  def ListFunc(self):
    """Returns the function for listing HTTP health checks."""
    return self.api.http_health_checks.list


def AddCommands():
  appcommands.AddCmd('addhttphealthcheck', AddHttpHealthCheck)
  appcommands.AddCmd('gethttphealthcheck', GetHttpHealthCheck)
  appcommands.AddCmd('deletehttphealthcheck', DeleteHttpHealthCheck)
  appcommands.AddCmd('listhttphealthchecks', ListHttpHealthChecks)
  appcommands.AddCmd('updatehttphealthcheck', UpdateHttpHealthCheck)
