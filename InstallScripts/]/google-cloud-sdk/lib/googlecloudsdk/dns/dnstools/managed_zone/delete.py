# Copyright 2013 Google Inc. All Rights Reserved.

"""'dns managed-zone delete' command."""

from apiclient import errors

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import properties
from googlecloudsdk.core.util import console_io
from googlecloudsdk.dns.lib import util


class Delete(base.Command):
  """Delete a Cloud DNS managed zone."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument(
        'zone',
        help='Managed Zone name.')
    parser.add_argument(
        '--delete-zone-contents',
        default=False,
        required=False,
        help='If true, delete the contents of the zone first')

  def Run(self, args):
    """Run 'dns managed-zone delete'.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the changes resource obtained by the delete
      operation if the delete was successful.
    """
    project = properties.VALUES.core.project.Get(required=True)
    really = console_io.PromptContinue(
        'Deleting %s in %s' % (args.zone, project))
    if not really:
      return

    dns = self.context['dns']
    if args.delete_zone_contents:
      self.DeleteZoneContents_(dns, project, args.zone)

    request = dns.managedZones().delete(project=project, managedZone=args.zone)
    try:
      result = request.execute()
      return result
    except errors.HttpError as error:
      raise exceptions.HttpException(util.GetError(error, verbose=True))
    except errors.Error as error:
      raise exceptions.ToolException(error)

  def Display(self, unused_args, result):
    """Display prints information about what just happened to stdout.

    Args:
      unused_args: The same as the args in Run.
      result: The results of the Run() method.
    """
    if result is not None:
      util.PrettyPrint(result)

  def DeleteRecords_(self, dns, old_soa, new_soa, rrsets, project, zone):
    records_to_delete = []
    for record in rrsets:
      if record['type'] != 'SOA' and record['type'] != 'NS':
        records_to_delete.append(record)
    if not records_to_delete:
      return None
    records_to_delete.append(old_soa)

    change = {}
    change['additions'] = [new_soa]
    change['deletions'] = records_to_delete

    request = dns.changes().create(
        project=project, managedZone=zone, body=change)
    return request.execute()

  def DeleteZoneContents_(self, dns, project, zone):
    soa_rr_set = self.GetSoaResourceRecordSet(dns, project, zone)

    next_soa_rr_set = dict(soa_rr_set)
    next_soa_rr_set['rrdatas'] = [self._BumpVersion(soa_rr_set['rrdatas'][0])]

    request = dns.resourceRecordSets().list(project=project, managedZone=zone)
    response = result = request.execute()
    self.DeleteRecords_(
        dns, soa_rr_set, next_soa_rr_set, response['rrsets'], project, zone)

    while 'nextPageToken' in result and result['nextPageToken'] is not None:
      request = dns.resourceRecordSets().list(
          project=project,
          managedZone=zone,
          pageToken=result['nextPageToken'])
      result = request.execute()

      soa_rr_set = next_soa_rr_set
      next_soa_rr_set = dict(soa_rr_set)
      next_soa_rr_set['rrdatas'] = [self._BumpVersion(
          soa_rr_set['rrdatas'][0])]

      self.DeleteRecords_(
          dns, soa_rr_set, next_soa_rr_set, response['rrsets'], project, zone)

  # TODO(user) : These are duped, figure out the right class structure
  # and fix this so that they are inherited/utilities.
  def GetSoaResourceRecordSet(self, dns, project, zone):
    """Get the SOA ResourceRecordSet for a project.

    Args:
      dns: The DNS API endpoint.
      project: The project id.
      zone: The name of the zone.

    Returns:
      A dict containing the SOA record.

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
      raise exceptions.ToolException(
          'unexpected soa list response: %s' % list_response)

    return list_response['rrsets'][0]

  def _BumpVersion(self, version):
    parts = version.split()
    parts[2] = str((long(parts[2]) + 1) % (1L << 32))
    return ' '.join(parts)
