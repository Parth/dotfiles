# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for deleting disks."""
from googlecloudsdk.compute.lib import base_classes


class Delete(base_classes.ZonalDeleter):
  """Delete Google Compute Engine disks."""

  @property
  def service(self):
    return self.compute.disks

  @property
  def resource_type(self):
    return 'disks'

  @property
  def custom_prompt(self):
    return ('The following disks will be deleted. Deleting a disk is '
            'irreversible and any data on the disk will be lost.')

Delete.detailed_help = {
    'brief': 'Delete Google Compute Engine persistent disks',
    'DESCRIPTION': """\
        *{command}* deletes one or more Google Compute Engine
        persistent disks. Disks can be deleted only if they are not
        being used by any virtual machine instances.
        """,
}
