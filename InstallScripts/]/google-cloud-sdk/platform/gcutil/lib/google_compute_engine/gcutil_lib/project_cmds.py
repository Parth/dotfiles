# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Commands for interacting with Google Compute Engine."""




import ipaddr

from google.apputils import app
from google.apputils import appcommands
import gflags as flags

from gcutil_lib import command_base
from gcutil_lib import gcutil_errors
from gcutil_lib import gcutil_logging
from gcutil_lib import metadata
from gcutil_lib import scopes
from gcutil_lib import version


FLAGS = flags.FLAGS
LOGGER = gcutil_logging.LOGGER


def _DefineUsageExportFlags(flag_values):
  flags.DEFINE_string('bucket', None,
                      ('The name of an existing bucket in Google Storage where '
                       'the usage report object is stored. The Google Service '
                       'Account is granted write access to this bucket. This is'
                       ' simply the bucket name, with no "gs://" or '
                       '"https://storage.googleapis.com/" in front of it.'),
                      flag_values=flag_values)

  flags.DEFINE_string('prefix', None,
                      ('An optional prefix for the name of the usage report '
                       'object stored in bucket. If not supplied, '
                       'defaults to "usage_".  The report is stored as a CSV '
                       'file named <report_name_prefix>_gce_<YYYYMMDD>.csv. '
                       'where <YYYYMMDD> is the day of the usage according to '
                       'Pacific Time. The prefix should conform to Google '
                       'Storage object naming conventions.'),
                      flag_values=flag_values)


class ProjectCommand(command_base.GoogleComputeCommand):
  """Base command for working with the projects collection."""

  print_spec = command_base.ResourcePrintSpec(
      summary=['name', 'description'],
      field_mappings=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp')),
      detail=(
          ('name', 'name'),
          ('description', 'description'),
          ('creation-time', 'creationTimestamp'),
          ('common-instance-metadata-fingerprint',
           'commonInstanceMetadata.fingerprint')),
      sort_by='name')

  def __init__(self, name, flag_values):
    super(ProjectCommand, self).__init__(name, flag_values)

  def GetDetailRow(self, result):
    """Returns an associative list of items for display in a detail table.

    Args:
      result: A dict returned by the server.

    Returns:
      A list.
    """
    data = []
    # Add the IP addresses
    ips = [ipaddr.IPv4Address(ip) for ip
           in result.get('externalIpAddresses', [])]
    if ips:
      blocks = sorted(ipaddr.collapse_address_list(ips))

      ip_info = [('count', len(ips))]
      if blocks:
        ip_info.append(('blocks', blocks))
      data.append(('ips', ip_info))

    # Add the quotas

    quota_info = []
    for quota in result.get('quotas', []):
      quota_info.append((quota['metric'].lower().replace('_', '-'),
                         '%s/%s' % (str(quota['usage']), str(quota['limit']))))
    data.append(('usage', quota_info))

    # Add the metadata
    if result.get('commonInstanceMetadata', []):

      metadata_container = result.get('commonInstanceMetadata', [])
      if 'kind' in metadata_container:
        metadata_container = metadata_container.get('items', [])

      metadata_info = []
      for metadata_entry in metadata_container:
        metadata_info.append((
            metadata_entry.get('key'),
            metadata_entry.get('value')))
      data.append(('common-instance-metadata', metadata_info))
      data.append(('common-instance-metadata-fingerprint',
                   result.get('commonInstanceMetadata', {}).get('fingerprint')))

    usage_export = result.get('usageExportLocation', [])
    if usage_export:
      data.append(('usageExportLocation',
                   [('bucketName', usage_export['bucketName']),
                    ('reportNamePrefix', usage_export['reportNamePrefix'])]))

    return data


class GetProject(ProjectCommand):
  """Get a Google Compute Engine project."""

  positional_args = '<project-name>'

  def __init__(self, name, flag_values):
    super(GetProject, self).__init__(name, flag_values)

  def Handle(self, project=None):
    """Get the specified project.

    Args:
      project: The project for which to get defails.

    Returns:
      The result of getting the project.
    """
    project = project or self._flags.project

    project_context = self._context_parser.ParseContextOrPrompt('projects',
                                                                project)

    project_request = self.api.projects.get(project=project_context['project'])
    return project_request.execute()


class OptimisticallyLockedProjectCommand(ProjectCommand):
  """Base class for project commands that optionally use a fingerprint."""

  def __init__(self, name, flag_values):
    super(OptimisticallyLockedProjectCommand, self).__init__(name, flag_values)

    flags.DEFINE_string('fingerprint',
                        None,
                        '[Optional] Fingerprint of the data to be '
                        'overwritten. This fingerprint provides optimistic '
                        'locking. Data will only be set if a fingerprint '
                        'is not provided or if the given '
                        'fingerprint matches the state of the data prior to '
                        'this request.',
                        flag_values=flag_values)

  def Handle(self):
    """Invokes the HandleCommand method of the subclass."""
    return self.HandleCommand()


class SetCommonInstanceMetadata(OptimisticallyLockedProjectCommand):
  """Set the commonInstanceMetadata field for a Google Compute Engine project.

  This is a blanket overwrite of all of the project wide metadata.
  """

  def __init__(self, name, flag_values):
    super(SetCommonInstanceMetadata, self).__init__(name, flag_values)
    flags.DEFINE_bool('force',
                      False,
                      'Sets project metadata even if it erases existing '
                      'metadata keys.',
                      flag_values=flag_values,
                      short_name='f')
    self._metadata_flags_processor = metadata.MetadataFlagsProcessor(
        flag_values)

  def HandleCommand(self):
    """Set the metadata common to all instances in the specified project.

    Args:
      None.

    Returns:
      The result of setting the project wide metadata.

    Raises:

      gcutil_errors.CommandError: If the update would cause some metadata to
        be deleted.
    """
    new_metadata = self._metadata_flags_processor.GatherMetadata()

    project = self._flags.project
    project_context = self._context_parser.ParseContextOrPrompt('projects',
                                                                project)

    if not self._flags.force:
      get_request = self.api.projects.get(project=project_context['project'])
      project_resource = get_request.execute()
      project_metadata = project_resource.get('commonInstanceMetadata', [])
      if 'kind' in project_metadata:
        project_metadata = project_metadata.get('items', [])
      existing_keys = set([entry['key'] for entry in project_metadata])
      new_keys = set([entry['key'] for entry in new_metadata])
      dropped_keys = existing_keys - new_keys
      if dropped_keys:
        raise gcutil_errors.CommandError(
            'Discarding update that would wipe out the following metadata: %s.'
            '\n\nRe-run with the -f flag to force the update.' %
            ', '.join(list(dropped_keys)))

    metadata_resource = {'kind': self._GetResourceApiKind('metadata'),
                         'items': new_metadata}
    if self._flags.fingerprint:
      metadata_resource['fingerprint'] = self._flags.fingerprint

    project_request = self.api.projects.setCommonInstanceMetadata(
        project=project_context['project'],
        body=metadata_resource)
    return project_request.execute()


class UsageExportCommand(ProjectCommand):
  """Abstract command containing helper method for Usage Export Commands."""

  def ExecuteUsageExportRequest(self, bucket_name, report_name_prefix):
    project = self._flags.project
    project_context = self._context_parser.ParseContextOrPrompt('projects',
                                                                project)
    body = {'kind': self._GetResourceApiKind('usageExportLocation')}
    if bucket_name:
      body['bucketName'] = bucket_name
    if report_name_prefix:
      body['reportNamePrefix'] = report_name_prefix

    set_usage_export_request = (
        self.api.projects.setUsageExportBucket(
            project=project_context['project'],
            body=body))
    return set_usage_export_request.execute()


class SetUsageExportBucket(UsageExportCommand):
  """Set the usageExportLocation field for a Google Compute Engine project."""

  def __init__(self, name, flag_values):
    super(SetUsageExportBucket, self).__init__(name, flag_values)
    _DefineUsageExportFlags(flag_values)

  def Handle(self):
    """Set the cloud storage bucket where usage reports will be exported to.

    Args:
      None.

    Returns:
      The result of setting the cloud storage bucket.

    Raises:

      UsageError: If user does not specify a bucket.

    """
    if not self._flags['bucket'].present:
      raise app.UsageError('You must specify a bucket name. '
                           'To unset this feature run clearusagebucket')

    return self.ExecuteUsageExportRequest(
        self._flags.bucket,
        self._flags.prefix if self._flags['prefix'].present else None)


class ClearUsageExportBucket(UsageExportCommand):
  """Convenience method for clearing the usageExportLocation field."""

  def Handle(self):
    """Set the cloud storage bucket where usage reports will be exported to.

    Args:
      None.

    Returns:
      The result of setting the cloud storage bucket.

    """
    return self.ExecuteUsageExportRequest(None, None)


def AddCommands():
  appcommands.AddCmd('getproject', GetProject)
  appcommands.AddCmd('setcommoninstancemetadata', SetCommonInstanceMetadata)
  appcommands.AddCmd('setusagebucket', SetUsageExportBucket)
  appcommands.AddCmd('clearusagebucket', ClearUsageExportBucket)

