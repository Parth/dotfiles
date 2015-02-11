# Copyright 2013 Google Inc. All Rights Reserved.

"""'dns resource-record-sets edit' command."""

import copy
import json

from googlecloudsdk.calliope import base
from googlecloudsdk.core import properties
from googlecloudsdk.core.util import edit
from googlecloudsdk.dns.lib import util


class Edit(base.Command):
  """Edit Cloud DNS resource record sets."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """

  def Run(self, args):
    """Run 'dns resource-record-sets edit'.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      The result of the edit operation, or None if it is cancelled.
    """
    dns = self.context['dns']
    project = properties.VALUES.core.project.Get(required=True)
    soa_rr_set = self.GetSoaResourceRecordSet(dns, project, args.zone)

    next_soa_rr_set = copy.copy(soa_rr_set)
    next_soa_rr_set['rrdatas'] = [self._BumpVersion(soa_rr_set['rrdatas'][0])]

    changes = {}
    changes['deletions'] = [soa_rr_set]
    changes['additions'] = [next_soa_rr_set]

    try:
      new_change = edit.OnlineEdit(util.PrettyPrintString(changes))
    except edit.NoSaveException:
      new_change = None
    if new_change is not None:
      change = json.loads(new_change)
      request = dns.changes().create(
          project=project, managedZone=args.zone, body=change)
      return request.execute()

    return None

  def Display(self, unused_args, result):
    """Display prints information about what just happened to stdout.

    Args:
      unused_args: The same as the args in Run.
      result: The results of the Run() method.
    """
    if result is None:
      return
    util.PrettyPrint(result)

  def GetSoaResourceRecordSet(self, dns, project, zone):
    """Get the SOA ResourceRecordSet for a project.

    Args:
      dns: The DNS API endpoint.
      project: The project id.
      zone: The name of the zone.

    Returns:
      A list of SOA records.

    Raises:
      RuntimeError: if the SOA listing doesn't work correctly.
    """
    request = dns.managedZones().get(
        project=project, managedZone=zone)
    data = request.execute()
    list_request = dns.resourceRecordSets().list(
        project=project, managedZone=zone, name=data['dnsName'], type='SOA')
    list_response = list_request.execute()
    if not list_response['rrsets']:
      raise RuntimeError('unexpected soa list response: %s' % list_response)

    return list_response['rrsets'][0]

  def _BumpVersion(self, version):
    parts = version.split()
    parts[2] = str((long(parts[2]) + 1) % (1L << 32))
    return ' '.join(parts)


