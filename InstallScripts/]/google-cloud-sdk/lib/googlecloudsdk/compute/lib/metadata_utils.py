# Copyright 2014 Google Inc. All Rights Reserved.
"""Convenience functions for dealing with metadata."""
import copy

from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import file_utils


def _DictToMetadataMessage(message_classes, metadata_dict):
  """Converts a metadata dict to a Metadata message."""
  message = message_classes.Metadata()
  if metadata_dict:
    for key, value in sorted(metadata_dict.iteritems()):
      message.items.append(message_classes.Metadata.ItemsValueListEntry(
          key=key,
          value=value))
  return message


def _MetadataMessageToDict(metadata_message):
  """Converts a Metadata message to a dict."""
  res = {}
  if metadata_message:
    for item in metadata_message.items:
      res[item.key] = item.value
  return res


def ConstructMetadataMessage(message_classes,
                             metadata=None,
                             metadata_from_file=None,
                             existing_metadata=None):
  """Creates a Metadata message from the given dicts of metadata.

  Args:
    message_classes: An object containing API message classes.
    metadata: A dict mapping metadata keys to metadata values or None.
    metadata_from_file: A dict mapping metadata keys to file names
      containing the keys' values or None.
    existing_metadata: If not None, the given metadata values are
      combined with this Metadata message.

  Raises:
    ToolException: If metadata and metadata_from_file contain duplicate
      keys or if there is a problem reading the contents of a file in
      metadata_from_file.

  Returns:
    A Metadata protobuf.
  """
  metadata = metadata or {}
  metadata_from_file = metadata_from_file or {}

  new_metadata_dict = copy.deepcopy(metadata)
  for key, file_path in metadata_from_file.iteritems():
    if key in new_metadata_dict:
      raise exceptions.ToolException(
          'Encountered duplicate metadata key [{0}].'.format(key))

    new_metadata_dict[key] = file_utils.ReadFile(
        file_path, 'metadata key [{0}]'.format(key))

  existing_metadata_dict = _MetadataMessageToDict(existing_metadata)
  existing_metadata_dict.update(new_metadata_dict)
  new_metadata_message = _DictToMetadataMessage(message_classes,
                                                existing_metadata_dict)

  if existing_metadata:
    new_metadata_message.fingerprint = existing_metadata.fingerprint

  return new_metadata_message


def MetadataEqual(metadata1, metadata2):
  """Returns True if both metadata messages have the same key/value pairs."""
  return _MetadataMessageToDict(metadata1) == _MetadataMessageToDict(metadata2)


def RemoveEntries(message_classes, existing_metadata,
                  keys=None, remove_all=False):
  """Removes keys from existing_metadata.

  Args:
    message_classes: An object containing API message classes.
    existing_metadata: The Metadata message to remove keys from.
    keys: The keys to remove. This can be None if remove_all is True.
    remove_all: If True, all entries from existing_metadata are
      removed.

  Returns:
    A new Metadata message with entries removed and the same
      fingerprint as existing_metadata if existing_metadata contains
      a fingerprint.
  """
  if remove_all:
    new_metadata_message = message_classes.Metadata()
  elif keys:
    existing_metadata_dict = _MetadataMessageToDict(existing_metadata)
    for key in keys:
      existing_metadata_dict.pop(key, None)
    new_metadata_message = _DictToMetadataMessage(
        message_classes, existing_metadata_dict)

  new_metadata_message.fingerprint = existing_metadata.fingerprint

  return new_metadata_message


def AddMetadataArgs(parser):
  """Adds --metadata and --metadata-from-file flags."""
  metadata = parser.add_argument(
      '--metadata',
      action=arg_parsers.AssociativeList(),
      default={},
      help=('Metadata to be made available to the guest operating system '
            'running on the instances'),
      metavar='KEY=VALUE',
      nargs='+')
  metadata.detailed_help = """\
      Metadata to be made available to the guest operating system
      running on the instances. Each metadata entry is a key/value
      pair separated by an equals sign. Metadata keys must be unique
      and less than 128 bytes in length. Values must be less than or
      equal to 32,768 bytes in length. Multiple arguments can be
      passed to this flag, e.g., ``--metadata key-1=value-1
      key-2=value-2 key-3=value-3''.

      In images that have
      link:https://developers.google.com/compute/docs/building-image[Compute
      Engine tools installed] on them, the following metadata keys
      have special meanings:

      *startup-script*::: Specifies a script that will be executed
      by the instances once they start running. For convenience,
      ``--metadata-from-file'' can be used to pull the value from a
      file.

      *startup-script-url*::: Same as ``startup-script'' except that
      the script contents are pulled from a publicly-accessible
      location on the web.
      """

  metadata_from_file = parser.add_argument(
      '--metadata-from-file',
      action=arg_parsers.AssociativeList(),
      default={},
      help=('Same as ``--metadata'' except that the value for the entry '
            'will be read from a local file.'),
      metavar='KEY=LOCAL_FILE_PATH',
      nargs='+')
  metadata_from_file.detailed_help = """\
      Same as ``--metadata'' except that the value for the entry will
      be read from a local file. This is useful for values that are
      too large such as ``startup-script'' contents.
      """
