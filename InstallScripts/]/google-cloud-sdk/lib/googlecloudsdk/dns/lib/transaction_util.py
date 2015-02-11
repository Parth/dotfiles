# Copyright 2014 Google Inc. All Rights Reserved.

"""Helper methods for record-set transactions."""

import os
from dns import rdatatype
import yaml

from googlecloudapis.dns.v1beta1 import dns_v1beta1_messages as messages
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core.util import resource_printer
from googlecloudsdk.dns.lib import import_util


DEFAULT_PATH = 'transaction.yaml'


def WriteToYamlFile(yaml_file, change):
  """Writes the given change in yaml format to the given file.

  Args:
    yaml_file: file, File into which the change should be written.
    change: Change, Change to be written out.
  """
  printer = resource_printer.YamlPrinter(yaml_file)
  printer.AddRecord(change)


def _RecordSetsFromDictionaries(record_set_dictionaries):
  """Converts list of record-set dictionaries into list of ResourceRecordSets.

  Args:
    record_set_dictionaries: [{str:str}], list of record-sets as dictionaries.

  Returns:
    list of ResourceRecordSets equivalent to given list of yaml record-sets
  """
  record_sets = []
  for record_set_dict in record_set_dictionaries:
    record_set = messages.ResourceRecordSet()
    # Need to assign kind to default value for useful equals comparisons.
    record_set.kind = record_set.kind
    record_set.name = record_set_dict['name']
    record_set.ttl = record_set_dict['ttl']
    record_set.type = record_set_dict['type']
    record_set.rrdatas = record_set_dict['rrdatas']
    record_sets.append(record_set)
  return record_sets


def ChangeFromYamlFile(yaml_file):
  """Returns the change contained in the given yaml file.

  Args:
    yaml_file: file, A yaml file with change.

  Returns:
    Change, the change contained in the given yaml file.
  """
  change_dict = yaml.safe_load(yaml_file)
  change = messages.Change()
  change.additions = _RecordSetsFromDictionaries(change_dict['additions'])
  change.deletions = _RecordSetsFromDictionaries(change_dict['deletions'])
  return change


def CreateRecordSetFromArgs(args):
  """Creates and returns a record-set from the given args.

  Args:
    args: The arguments to use to create the record-set.

  Raises:
    ToolException: If given record-set type is not supported

  Returns:
    ResourceRecordSet, the record-set created from the given args.
  """
  rd_type = rdatatype.from_text(args.type)
  if rd_type not in import_util.RDATA_TRANSLATIONS:
    raise exceptions.ToolException(
        'unsupported record-set type [{0}]'.format(args.type))

  record_set = messages.ResourceRecordSet()
  # Need to assign kind to default value for useful equals comparisons.
  record_set.kind = record_set.kind
  record_set.name = args.name
  record_set.ttl = args.ttl
  record_set.type = args.type
  record_set.rrdatas = args.data
  if rd_type is rdatatype.TXT or rd_type is rdatatype.SPF:
    record_set.rrdatas = [import_util.EscapedText(datum) for datum in args.data]
  return record_set


class TransactionFile(object):
  """Context for reading/writing from/to a transaction file."""

  def __init__(self, trans_file_path, mode='r'):
    if not os.path.isfile(trans_file_path):
      raise exceptions.ToolException(
          'transaction not found at [{0}]'.format(trans_file_path))

    self.__trans_file_path = trans_file_path

    try:
      self.__trans_file = open(trans_file_path, mode)
    except IOError as exp:
      msg = 'unable to open transaction [{0}] because [{1}]'
      msg = msg.format(trans_file_path, exp)
      raise exceptions.ToolException(msg)

  def __enter__(self):
    return self.__trans_file

  def __exit__(self, typ, value, traceback):
    self.__trans_file.close()

    if typ is IOError or typ is yaml.YAMLError:
      msg = 'unable to read/write transaction [{0}] because [{1}]'
      msg = msg.format(self.__trans_file_path, value)
      raise exceptions.ToolException(msg)
