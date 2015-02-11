# Copyright 2014 Google Inc. All Rights Reserved.

"""Helper methods for exporting record-sets."""

from dns import name
from dns import rdata
from dns import rdataclass
from dns import rdatatype
from dns import zone

from googlecloudsdk.core.util import resource_printer


def WriteToZoneFile(zone_file, record_sets, domain):
  """Writes the given record-sets in zone file format to the given file.

  Args:
    zone_file: file, File into which the records should be written.
    record_sets: list, ResourceRecordSets to be written out.
    domain: str, The origin domain for the zone file.
  """
  zone_contents = zone.Zone(name.from_text(domain))
  for record_set in record_sets:
    rdset = zone_contents.get_rdataset(record_set.name,
                                       record_set.type,
                                       create=True)
    for rrdata in record_set.rrdatas:
      rdset.add(rdata.from_text(rdataclass.IN,
                                rdatatype.from_text(record_set.type),
                                str(rrdata),
                                origin=zone_contents.origin),
                ttl=record_set.ttl)
  zone_contents.to_file(zone_file, relativize=False)


def WriteToYamlFile(yaml_file, record_sets):
  """Writes the given record-sets in yaml format to the given file.

  Args:
    yaml_file: file, File into which the records should be written.
    record_sets: list, ResourceRecordSets to be written out.
  """
  printer = resource_printer.YamlPrinter(yaml_file)
  for record_set in record_sets:
    printer.AddRecord(record_set)


