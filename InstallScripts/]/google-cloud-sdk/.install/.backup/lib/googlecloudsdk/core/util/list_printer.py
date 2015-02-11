# Copyright 2014 Google Inc. All Rights Reserved.

"""List printer for Cloud Platform resources."""

from googlecloudsdk.core import remote_completion
from googlecloudsdk.core.util import attrpath
from googlecloudsdk.core.util import console_io


def PrintResourceList(collection, items):
  """Print a list of cloud resources.

  Args:
    collection: str, The name of the collection to which the items belong.
    items: iterable, A list or otherwise iterable object that generates the
        rows of the list.
  """
  options = []
  cache = remote_completion.RemoteCompletion()

  class Iter(object):
    """Create an iterator that steals the names of objects.

    Args:
      items: List of items to iterate
      options: List of names of the items created by iterator.
    """

    def __init__(self, items, options):
      self.items = items
      self.options = options

    def next(self):
      item = self.items.next()
      fun = cache.ITEM_NAME_FUN['sql']
      if fun:
        self.options.append(fun(item))
      return item

    def __iter__(self):
      return self

  if cache.ResourceIsCached(collection):
    items = Iter(iter(items), options)
  console_io.PrintExtendedList(items, COLLECTION_COLUMNS[collection])
  if options:
    cache.StoreInCache(collection, options, None)


def _Select(path, transform=None):
  """Get a column fetcher for the given attr path and transform.

  Args:
    path: str, The attr path that keys into the resource.
    transform: func(str)->str, A func that takes something found by the path
        and maps it to some other strip.

  Returns:
    func(obj)->str, A func that takes an object and returns the value
    for a particular column.
  """

  getter = attrpath.Selector(path)

  if transform is None:
    return getter

  def GetAndTransform(obj):
    return transform(getter(obj))
  return GetAndTransform


def _NameOnly(value):
  """Get only the last token from a longer path, usually the name.

  Intended to be a selector transform for URLs.

  Args:
    value: str, The value whose last token will be returned.

  Returns:
    str, The name from value.
  """
  if value:
    return value.split('/')[-1]
  return value


def _CommaList(default=None):
  def Transform(items):
    if not items:
      return default
    return ', '.join(items)
  return Transform


def _DiskSize(value):
  """Returns a human readable string representation of the disk size.

  Args:
    value: str, Disk size represented as number of bytes.

  Returns:
    A human readable string representation of the disk size.
  """
  size = float(value)
  the_unit = 'TB'
  for unit in ['bytes', 'KB', 'MB', 'GB']:
    if size < 1024.0:
      the_unit = unit
      break
    size = float(size) / 1024.0
  if size == int(size):
    return '%d %s' % (size, the_unit)
  else:
    return '%3.1f %s' % (size, the_unit)


def _ScreenResolution(model):
  """Build a human readable string representation of a screen resolution.

  Args:
    model: a Test_v1.AndroidModel message (from ApiTools)

  Returns:
    Returns a human readable string representation of a screen resolution.
  """
  return '{x} x {y}'.format(x=model.screenX, y=model.screenY)




def _SelectTime(path):
  return _Select(path, transform=lambda x: x and x.isoformat())


COLLECTION_COLUMNS = {
    # APPENGINE
    'app.module_versions': (
        ('MODULE', _Select('module')),
        ('VERSION', _Select('version')),
        ('IS_DEFAULT', _Select('is_default',
                               transform=lambda x: '*' if x else '-')),
    ),

    # AUTOSCALER
    'autoscaler.instances': (
        ('NAME', _Select('name')),
        ('DESCRIPTION', _Select('description')),
        ('STATE', _Select('state')),
        ('STATE_DETAILS', _Select('state_details')),
    ),

    # BIGQUERY
    'bigquery.datasets': (
        ('DATASET_ID', _Select('datasetReference.datasetId')),
    ),
    'bigquery.jobs.describe': (
        ('JOB_TYPE', _Select('job_type')),
        ('STATE', _Select('state')),
        ('START_TIME', _Select('start_time')),
        ('DURATION', _Select('duration')),
        ('BYTES_PROCESSED', _Select('bytes_processed')),
    ),
    'bigquery.jobs.list': (
        ('JOB_ID', _Select('job_id')),
        ('JOB_TYPE', _Select('job_type')),
        ('STATE', _Select('state')),
        ('START_TIME', _Select('start_time')),
        ('DURATION', _Select('duration')),
    ),
    'bigquery.jobs.wait': (
        ('JOB_TYPE', _Select('job_type')),
        ('STATE', _Select('state')),
        ('START_TIME', _Select('start_time')),
        ('DURATION', _Select('duration')),
        ('BYTES_PROCESSED', _Select('bytes_processed')),
    ),
    'bigquery.projects': (
        ('PROJECT_ID', _Select('projectReference.projectId')),
        ('FRIENDLY_NAME', _Select('friendlyName')),
    ),
    'bigquery.tables.list': (
        ('ID', _Select('id')),
        ('TABLE_OR_VIEW', _Select('type')),
    ),

    # COMPUTE
    'compute.instances': (
        ('NAME', _Select('name')),
        ('ZONE', _Select('zone', _NameOnly)),
        ('MACHINE_TYPE', _Select('machineType', _NameOnly)),
        ('INTERNAL_IP', _Select('networkInterfaces[0].networkIP')),
        ('EXTERNAL_IP', _Select('networkInterfaces[0].accessConfigs[0].natIP')),
        ('STATUS', _Select('status')),
    ),

    # DATAFLOW
    'dataflow.jobs': (
        ('NAME', _Select('job_name')),
        ('ID', _Select('job_id')),
        ('TYPE', _Select('job_type')),
        ('STATUS', _Select('status')),
        ('STATUS_TIME', _Select('status_time')),
        ('CREATION_TIME', _Select('creation_time')),
    ),

    # DNS
    'dns.changes': (
        ('ID', _Select('id')),
        ('START_TIME', _Select('startTime')),
        ('STATUS', _Select('status')),
    ),
    'dns.managedZones': (
        ('NAME', _Select('name')),
        ('DNS_NAME', _Select('dnsName')),
        ('DESCRIPTION', _Select('description')),
    ),
    'dns.resourceRecordSets': (
        ('NAME', _Select('name')),
        ('TYPE', _Select('type')),
        ('TTL', _Select('ttl')),
        ('DATA', _Select('rrdatas', _CommaList(''))),
    ),

    # DEPLOYMENTMANAGER V2
    'deploymentmanager.deployments': (
        ('NAME', _Select('name')),
        ('ID', _Select('id')),
        ('DESCRIPTION', _Select('description')),
        ('MANIFEST', _Select('manifest')),
    ),
    'deploymentmanager.operations': (
        ('NAME', _Select('name')),
        ('TYPE', _Select('operationType')),
        ('STATUS', _Select('status')),
        ('TARGET_LINK', _Select('targetLink')),
        ('ERRORS', _Select('error.errors')),
    ),
    'deploymentmanager.resources': (
        ('NAME', _Select('name')),
        ('TYPE', _Select('type')),
        ('ID', _Select('id')),
        ('STATE', _Select('state')),
        ('ERRORS', _Select('errors')),
    ),

    # SQL
    'sql.backupRuns': (
        ('DUE_TIME', _SelectTime('dueTime')),
        ('ERROR', _Select('error.code')),
        ('STATUS', _Select('status')),
    ),
    'sql.flags': (
        ('NAME', _Select('name')),
        ('TYPE', _Select('type')),
        ('ALLOWED_VALUES', _Select('allowedStringValues', _CommaList(''))),
    ),
    'sql.instances': (
        ('NAME', _Select('instance')),
        ('REGION', _Select('region')),
        ('TIER', _Select('settings.tier')),
        ('ADDRESS', _Select('ipAddresses[0].ipAddress')),
        ('STATUS', _Select('state')),
    ),
    'sql.operations': (
        ('OPERATION', _Select('operation')),
        ('TYPE', _Select('operationType')),
        ('START', _SelectTime('startTime')),
        ('END', _SelectTime('endTime')),
        ('ERROR', _Select('error[0].code')),
        ('STATUS', _Select('state')),
    ),
    'sql.sslCerts': (
        ('NAME', _Select('commonName')),
        ('SHA1_FINGERPRINT', _Select('sha1Fingerprint')),
        ('EXPIRATION', _Select('expirationTime')),
    ),
    'sql.tiers': (
        ('TIER', _Select('tier')),
        ('AVAILABLE_REGIONS', _Select('region', _CommaList(''))),
        ('RAM', _Select('RAM', _DiskSize)),
        ('DISK', _Select('DiskQuota', _DiskSize)),
    ),

    # projects
    'developerprojects.projects': (
        ('PROJECT_ID', _Select('projectId')),
        ('TITLE', _Select('title')),
        ('PROJECT_NUMBER', _Select('projectNumber')),
    ),

    # Cloud Updater
    'replicapoolupdater.rollingUpdates': (
        ('ID', _Select('id')),
        ('GROUP_NAME', _Select('instanceGroupManager', _NameOnly)),
        ('TEMPLATE_NAME', _Select('instanceTemplate', _NameOnly)),
        ('STATUS', _Select('status')),
        ('STATUS_MESSAGE', _Select('statusMessage')),
    ),
    'replicapoolupdater.rollingUpdates.instanceUpdates': (
        ('INSTANCE_NAME', _Select('instance', _NameOnly)),
        ('STATUS', _Select('status')),
    ),

    # TEST
    'test.android.devices': (
        ('DEVICE_ID', _Select('id')),
        ('MAKE', _Select('manufacturer')),
        ('MODEL', _Select('name')),
        ('FORM', _Select('form')),
        ('SCREEN_RES', _ScreenResolution),
        ('OS_VERSION_IDS', _Select('supportedVersionIds', _CommaList('none')))
    ),

    # Cloud Logging
    'logging.logs': (
        ('NAME', _Select('name')),
    ),
    'logging.sinks': (
        ('NAME', _Select('name')),
        ('DESTINATION', _Select('destination')),
    ),
    'logging.typedSinks': (
        ('NAME', _Select('name')),
        ('DESTINATION', _Select('destination')),
        ('TYPE', _Select('type')),
    ),
}
