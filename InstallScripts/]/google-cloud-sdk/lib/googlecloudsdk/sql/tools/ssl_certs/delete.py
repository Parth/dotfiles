# Copyright 2013 Google Inc. All Rights Reserved.
"""Deletes an SSL certificate for a Cloud SQL instance."""

from googlecloudapis.apitools.base import py as apitools_base
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.sql import util


class Delete(base.Command):
  """Deletes an SSL certificate for a Cloud SQL instance."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    parser.add_argument(
        'common_name',
        help='User supplied name. Constrained to [a-zA-Z.-_ ]+.')
    parser.add_argument(
        '--async',
        action='store_true',
        help='Do not wait for the operation to complete.')

  def Run(self, args):
    """Deletes an SSL certificate for a Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the delete
      operation if the api request was successful.
    Raises:
      HttpException: A http error response was received while executing api
          request.
      ToolException: An error other than http error occured while executing the
          command.
    """
    sql_client = self.context['sql_client']
    sql_messages = self.context['sql_messages']
    resources = self.context['registry']

    util.ValidateInstanceName(args.instance)
    instance_ref = resources.Parse(args.instance, collection='sql.instances')

    # TODO(user): figure out how to rectify the common_name and the
    # sha1fingerprint, so that things can work with the resource parser.
    try:

      cert_ref = util.GetCertRefFromName(sql_client, sql_messages, resources,
                                         instance_ref, args.common_name)
      if not cert_ref:
        raise exceptions.ToolException(
            'no ssl cert named [{name}] for instance [{instance}]'.format(
                name=args.common_name,
                instance=instance_ref))

      result = sql_client.sslCerts.Delete(
          sql_messages.SqlSslCertsDeleteRequest(
              project=cert_ref.project,
              instance=cert_ref.instance,
              sha1Fingerprint=cert_ref.sha1Fingerprint))

      operation_ref = resources.Create(
          'sql.operations',
          operation=result.operation,
          project=cert_ref.project,
          instance=cert_ref.instance,
      )

      if args.async:
        return sql_client.operations.Get(operation_ref.Request())

      util.WaitForOperation(sql_client, operation_ref, 'Deleting sslCert')

      log.DeletedResource(cert_ref)

    except apitools_base.HttpError as error:
      raise exceptions.HttpException(util.GetErrorMessage(error))

  def Display(self, args, result):
    self.format(result)
