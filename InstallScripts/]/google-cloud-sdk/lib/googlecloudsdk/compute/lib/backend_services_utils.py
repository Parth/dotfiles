# Copyright 2014 Google Inc. All Rights Reserved.
"""Code that's shared between multiple backend-services subcommands."""
import argparse

from googlecloudapis.compute.v1 import compute_v1_messages
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.compute.lib import utils

BALANCING_MODES = sorted(
    compute_v1_messages.Backend
    .BalancingModeValueValuesEnum.to_dict().keys())

PROTOCOL_OPTIONS = sorted(
    compute_v1_messages.BackendService.ProtocolValueValuesEnum.to_dict().keys())


def AddUpdatableArgs(parser,
                     default_protocol='HTTP',
                     default_timeout='30s'):
  """Adds top-level backend service arguments that can be updated."""
  parser.add_argument(
      '--description',
      help='An optional, textual description for the backend service.')

  http_health_checks = parser.add_argument(
      '--http-health-checks',
      metavar='HTTP_HEALTH_CHECK',
      nargs='+',
      help=('Specifies a list of HTTP health check objects for checking the '
            'health of the backend service.'))
  http_health_checks.detailed_help = """\
      Specifies a list of HTTP health check objects for checking the health
      of the backend service.
      """

  timeout = parser.add_argument(
      '--timeout',
      default=default_timeout,
      type=arg_parsers.Duration(),
      help=('The amount of time to wait for a backend to respond to a '
            'request before considering the request failed.'))
  timeout.detailed_help = """\
      The amount of time to wait for a backend to respond to a request
      before considering the request failed. For example, specifying
      ``10s'' will give backends 10 seconds to respond to
      requests. Valid units for this flag are ``s'' for seconds, ``m''
      for minutes, and ``h'' for hours.
      """
  parser.add_argument(
      '--port',
      type=int,
      help=('The TCP port to use when connecting to the backend. '
            '--port is being deprecated in favor of --port-name.'))

  port_name = parser.add_argument(
      '--port-name',
      help=('A user-defined port name used to resolve which port to use on '
            'each backend.'))
  port_name.detailed_help = """\
      The name of a service that has been added to an instance group
      in this backend. Instance group services map a name to a port
      number which is used by the load balancing service.
      Only one ``port-name'' may be added to a backend service, and that
      name must exist as a service on all instance groups that are a
      part of this backend service. The port number associated with the
      name may differ between instances. If you do not specify
      this flag, your instance groups must have a service named ``http''
      configured. See *gcloud preview instance-groups add-service(1)*
      for details.
      """

  parser.add_argument(
      '--protocol',
      choices=PROTOCOL_OPTIONS,
      default=default_protocol,
      type=lambda x: x.upper(),
      help='The protocol for incoming requests.')


def AddUpdatableBackendArgs(parser):
  """Adds arguments for manipulating backends in a backend service."""
  parser.add_argument(
      '--description',
      help='An optional, textual description for the backend.')

  parser.add_argument(
      '--group',
      required=True,
      help=('The name or URI of a Google Cloud Resource View that can receive '
            'traffic.'))

  utils.AddZoneFlag(
      parser,
      resource_type='resource view',
      operation_type='add to the backend service')

  balancing_mode = parser.add_argument(
      '--balancing-mode',
      choices=BALANCING_MODES,
      type=lambda x: x.upper(),
      help='Defines the strategy for balancing load.')
  balancing_mode.detailed_help = """\
      Defines the strategy for balancing load. ``UTILIZATION'' will
      rely on the CPU utilization of the tasks in the group when
      balancing load. When using ``UTILIZATION'',
      ``--max-utilization'' can be used to set a maximum target CPU
      utilization for each task. ``RATE'' will spread load based on
      how many requests per second (RPS) the group can handle. There
      are two ways to specify max RPS: ``--max-rate'' which defines
      the max RPS for the whole group or ``--max-rate-per-task'' which
      defines the max RPS on a per-task basis.

      In ``UTILIZATION'', you can optionally limit based on RPS in
      addition to CPU by setting either ``--max-rate-per-task'' or
      ``--max-rate''.
      """

  max_utilization = parser.add_argument(
      '--max-utilization',
      type=float,
      help=('The target CPU utilization of the group as a '
            'float in the range [0, 1e6].'))
  max_utilization.detailed_help = """\
      The target CPU utilization for the group as a float in the range
      [0, 1e6]. This flag can only be provided when the balancing
      mode is ``UTILIZATION''.
      """

  rate_group = parser.add_mutually_exclusive_group()

  rate_group.add_argument(
      '--max-rate',
      type=int,
      help='Maximum requests per second (RPS) that the group can handle.')

  rate_group.add_argument(
      '--max-rate-per-instance',
      type=float,
      help='The maximum per-instance requests per second (RPS).')

  capacity_scaler = parser.add_argument(
      '--capacity-scaler',
      type=float,
      help=('A float in the range [0.0, 1.0] that scales the maximum '
            'parameters for the group (e.g., max rate).'))
  capacity_scaler.detailed_help = """\
      A float in the range [0.0, 1.0] that scales the maximum
      parameters for the group (e.g., max rate). A value of 0.0 will
      cause no requests to be sent to the group (i.e., it adds the
      group in a ``drained'' state). The default is 1.0.
      """


def GetHealthChecks(args, resource_parser):
  """Returns health check URIs from arguments."""
  health_check_refs = []

  if args.http_health_checks:
    health_check_refs.extend(resource_parser.CreateGlobalReferences(
        args.http_health_checks, resource_type='httpHealthChecks'))


  return [health_check_ref.SelfLink() for health_check_ref in health_check_refs]
