# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for setting usage buckets."""
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import utils


class SetUsageBucket(base_classes.NoOutputAsyncMutator):
  """Set the usage reporting bucket for a project."""

  @staticmethod
  def Args(parser):
    bucket = parser.add_argument(
        '--bucket',
        nargs='?',
        required=True,
        help=('The URI of a Google Cloud Storage bucket where the usage report '
              'object should be stored'))
    bucket.detailed_help = """\
        The URI of a Google Cloud Storage bucket where the usage
        report object should be stored. The Google Service Account for
        performing usage reporting is granted write access to this bucket.
        The user running this command must be an owner of the bucket.

        To clear the usage bucket, specify this flag without an
        argument:

          $ gcloud compute project-info set-usage-bucket --bucket
        """

    prefix = parser.add_argument(
        '--prefix',
        help='An optional prefix for the name of the usage report object.')
    prefix.detailed_help = """\
        An optional prefix for the name of the usage report object stored in
        the bucket. If not supplied, then this defaults to ``usage''. The
        report is stored as a CSV file named PREFIX_gce_YYYYMMDD.csv where
        YYYYMMDD is the day of the usage according to Pacific Time. The prefix
        should conform to Google Cloud Storage object naming conventions.
        This flag must not be provided when clearing the usage bucket.
        """

  @property
  def service(self):
    return self.compute.projects

  @property
  def method(self):
    return 'SetUsageExportBucket'

  @property
  def resource_type(self):
    return 'projects'

  def CreateRequests(self, args):
    if not args.bucket and args.prefix:
      raise exceptions.ToolException(
          '[--prefix] cannot be specified when unsetting the usage bucket.')

    bucket_uri = utils.NormalizeGoogleStorageUri(args.bucket)

    request = self.messages.ComputeProjectsSetUsageExportBucketRequest(
        project=self.project,
        usageExportLocation=self.messages.UsageExportLocation(
            bucketName=bucket_uri,
            reportNamePrefix=args.prefix,
        )
    )

    return [request]


SetUsageBucket.detailed_help = {
    'brief': 'Set the usage reporting bucket for a project',
    'DESCRIPTION': """\
        *{command}* is used to configure usage reporting for projects.

        Setting usage reporting will cause a log of usage per resource to be
        written to a specified Google Cloud Storage bucket daily. For example,

          $ gcloud compute project-info set-usage-bucket --bucket gs://my-bucket

        will cause logs of the form usage_gce_YYYYMMDD.csv to be written daily
        to the bucket ``my-bucket''. To disable this feature, issue the command:

          $ gcloud compute project-info set-usage-bucket --bucket
        """,
}
