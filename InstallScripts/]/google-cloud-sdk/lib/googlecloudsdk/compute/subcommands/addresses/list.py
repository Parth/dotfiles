# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for listing addresses."""
from googlecloudsdk.compute.lib import base_classes


class List(base_classes.GlobalRegionalLister):
  """List addresses."""

  @property
  def global_service(self):
    return self.compute.globalAddresses

  @property
  def regional_service(self):
    return self.compute.addresses

  @property
  def resource_type(self):
    return 'addresses'

  @property
  def allowed_filtering_types(self):
    return ['globalAddresses', 'addresses']


List.detailed_help = {
    'brief': 'List addresses',
    'DESCRIPTION': """\
        *{command}* lists summary information of addresses in a project. The
        ``--uri'' option can be used to display URIs instead. Users who want to
        see more data should use 'gcloud compute addresses describe'.

        By default, global addresses and addresses from all regions are listed.
        The results can be narrowed down by providing the ``--regions'' or
        ``--global'' flag.
        """,
    'EXAMPLES': """\
        To list all addresses in a project in table form, run:

          $ {command}

        To list the URIs of all addresses in a project, run:

          $ {command} --uri

        To list all of the global addresses in a project, run:

          $ {command} --global

        To list all of the regional addresses in a project, run:

          $ {command} --regions

        To list all of the addresses from the ``us-central1'' and the
        ``europe-west1'' regions, run:

          $ {command} --regions us-central1 europe-west1
        """,

}
