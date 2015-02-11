# Copyright 2013 Google Inc. All Rights Reserved.

"""'dns project-info get' command."""

from apiclient import errors

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import properties
from googlecloudsdk.dns.lib import util


class Get(base.Command):
  """Get Cloud DNS information for a project.  Returns usage and quota data."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """

  def Run(self, args):
    """Run 'dns project get'.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the project resource obtained by the get
      operation if the get was successful.
    """
    dns = self.context['dns']
    project = properties.VALUES.core.project.Get(required=True)
    request = dns.projects().get(project=project)
    try:
      result = request.execute()
      return result
    except errors.HttpError as error:
      raise exceptions.HttpException(util.GetError(error, verbose=True))
    except errors.Error as error:
      raise exceptions.ToolException(error)

  def Display(self, unused_args, result):
    """Display prints information about what just happened to stdout.

    Args:
      unused_args: The same as the args in Run.
      result: The results of the Run() method.
    """
    util.PrettyPrint(result)

