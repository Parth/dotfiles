# Copyright 2014 Google Inc. All Rights Reserved.
"""Common classes and functions for zones."""
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.compute.lib import request_helper
from googlecloudsdk.compute.lib import utils
from googlecloudsdk.core.util import console_io


class ZoneResourceFetcher(object):
  """Mixin class for working with zones."""

  def GetZones(self, resource_refs):
    """Fetches zone resources."""
    errors = []
    requests = []
    zone_names = set()
    for resource_ref in resource_refs:
      if resource_ref.zone not in zone_names:
        zone_names.add(resource_ref.zone)
        requests.append((
            self.compute.zones,
            'Get',
            self.messages.ComputeZonesGetRequest(
                project=self.project,
                zone=resource_ref.zone)))

    res = list(request_helper.MakeRequests(
        requests=requests,
        http=self.http,
        batch_url=self.batch_url,
        errors=errors,
        custom_get_requests=None))

    if errors:
      return None
    else:
      return res

  def WarnForZonalCreation(self, resource_refs):
    """Warns the user if a zone has upcoming maintanence or deprecation."""
    zones = self.GetZones(resource_refs)
    if not zones:
      return

    prompts = []
    zones_with_upcoming_maintenance = []
    zones_with_deprecated = []
    for zone in zones:
      if zone.maintenanceWindows:
        zones_with_upcoming_maintenance.append(zone)
      if zone.deprecated:
        zones_with_deprecated.append(zone)

    if not zones_with_upcoming_maintenance and not zones_with_deprecated:
      return

    if zones_with_upcoming_maintenance:
      phrases = []
      if len(zones_with_upcoming_maintenance) == 1:
        phrases = ('a zone', 'window is')
      else:
        phrases = ('zones', 'windows are')
      title = ('You have selected {0} with upcoming '
               'maintenance. During maintenance, resources are '
               'temporarily unavailible. The next scheduled '
               '{1} as follows:'.format(phrases[0], phrases[1]))
      printable_maintenance_zones = []
      for zone in zones_with_upcoming_maintenance:
        next_event = min(zone.maintenanceWindows, key=lambda x: x.beginTime)
        window = '[{0}]: {1} -- {2}'.format(zone.name,
                                            next_event.beginTime,
                                            next_event.endTime)
        printable_maintenance_zones.append(window)
      prompts.append(utils.ConstructList(title, printable_maintenance_zones))

    if zones_with_deprecated:
      phrases = []
      if len(zones_with_deprecated) == 1:
        phrases = ('zone is', 'this zone', 'the')
      else:
        phrases = ('zones are', 'these zones', 'their')
      title = ('\n'
               'WARNING: The following selected {0} deprecated.'
               ' All resources in {1} will be deleted after'
               ' {2} turndown date.'.format(phrases[0], phrases[1], phrases[2]))
      printable_deprecated_zones = []
      for zone in zones_with_deprecated:
        if zone.deprecated.deleted:
          printable_deprecated_zones.append(('[{0}] {1}').format(zone.name,
                                                                 zone.deprecated
                                                                 .deleted))
        else:
          printable_deprecated_zones.append('[{0}]'.format(zone.name))
      prompts.append(utils.ConstructList(title, printable_deprecated_zones))

    final_message = ' '.join(prompts)
    if not console_io.PromptContinue(message=final_message):
      raise calliope_exceptions.ToolException('Creation aborted by user.')
