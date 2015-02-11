# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for describing the project."""
from googlecloudsdk.compute.lib import base_classes


class Describe(base_classes.BaseDescriber):
  """Describe the Google Compute Engine project resource."""

  @staticmethod
  def Args(parser):
    base_classes.AddFieldsFlag(parser, 'projects')

  @property
  def service(self):
    return self.compute.projects

  @property
  def resource_type(self):
    return 'projects'

  def CreateReference(self, args):
    return self.CreateGlobalReference(self.project)

  def SetNameField(self, args, request):
    pass


Describe.detailed_help = {
    'brief': 'Describe the Google Compute Engine project resource',
    'DESCRIPTION': """\
        *{command}* displays all data associated with the Google
        Compute Engine project resource. The project resource contains
        data such as global quotas, common instance metadata, and the
        project's creation time.
        """,
}
