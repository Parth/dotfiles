# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing instance templates."""
from googlecloudsdk.compute.lib import base_classes


class List(base_classes.GlobalLister):
  """List Google Compute Engine virtual machine instance templates."""

  @property
  def service(self):
    return self.compute.instanceTemplates

  @property
  def resource_type(self):
    return 'instanceTemplates'


List.detailed_help = {
    'brief': 'List Google Compute Engine virtual machine instance templates',
    'DESCRIPTION': """\
        *{command}* lists summary information for the virtual
        machine instance templates in a project. The ``--uri'' option can be
        used to display the URIs of the instance templates in the project.
        Users who want to see more data should use 'gcloud compute
        instance-templates describe'.
        """,
}
