# Copyright 2014 Google Inc. All Rights Reserved.
"""Command for setting a backup target pool."""
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.compute.lib import base_classes
from googlecloudsdk.compute.lib import utils


class SetBackup(base_classes.NoOutputAsyncMutator):
  """Set a backup pool for a target pool."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--backup-pool',
        nargs='?',
        help=('Name of the target pool that will serve as backup. '
              'If this flag is provided without a value, the existing '
              'backup pool is removed.'),
        required=True)

    utils.AddRegionFlag(
        parser,
        resource_type='target pool',
        operation_type='set a backup pool for')

    parser.add_argument(
        '--failover-ratio',
        type=float,
        help=('The new failover ratio value for the target pool. '
              'This must be a float in the range of [0, 1].'))

    parser.add_argument(
        'name',
        help='The name of the target pool for which to set the backup pool.')

  @property
  def service(self):
    return self.compute.targetPools

  @property
  def method(self):
    return 'SetBackup'

  @property
  def resource_type(self):
    return 'targetPools'

  def CreateRequests(self, args):
    """Returns a request necessary for setting a backup target pool."""

    target_pool_ref = self.CreateRegionalReference(args.name, args.region)

    if args.backup_pool:
      backup_pool_ref = self.CreateRegionalReference(
          args.backup_pool, target_pool_ref.region,
          resource_type='targetPools')
      target_reference = self.messages.TargetReference(
          target=backup_pool_ref.SelfLink())
    else:
      target_reference = self.messages.TargetReference()

    if args.backup_pool and args.failover_ratio is None:
      raise calliope_exceptions.ToolException(
          '[--failover-ratio] must be provided when setting a backup pool.')

    if args.failover_ratio is not None and (
        args.failover_ratio < 0 or args.failover_ratio > 1):
      raise calliope_exceptions.ToolException(
          '[--failover-ratio] must be a number between 0 and 1, inclusive.')

    request = self.messages.ComputeTargetPoolsSetBackupRequest(
        targetPool=target_pool_ref.Name(),
        targetReference=target_reference,
        failoverRatio=args.failover_ratio,
        region=target_pool_ref.region,
        project=self.project)

    return [request]


SetBackup.detailed_help = {
    'brief': 'Set a backup pool for a target pool',
    'DESCRIPTION': """\
        *{command}* is used to set a backup target pool for a primary
        target pool, which defines the fallback behavior of the primary
        pool. If the ratio of the healthy instances in the primary pool
        is at or below the specified ``--failover-ratio value'', then traffic
        arriving at the load-balanced IP address will be directed to the
        backup pool.
        """,
    'EXAMPLES': """\
        To cause ``TARGET-POOL'' (in region ``us-central1'') to fail over
        to ``BACKUP-POOL'' when more than half of the ``TARGET-POOL''
        instances are unhealthy, run:

          $ {command} TARGET-POOL --backup-pool BACKUP-POOL --failover-ratio 0.5 --region us-central1

        To remove ``BACKUP-POOL'' as a backup to ``TARGET-POOL'', run:

          $ {command} TARGET-POOL --backup-pool --region us-central1
        """,
}
