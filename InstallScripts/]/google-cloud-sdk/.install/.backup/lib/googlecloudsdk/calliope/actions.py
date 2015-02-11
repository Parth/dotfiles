# Copyright 2013 Google Inc. All Rights Reserved.

"""argparse Actions for use with calliope.
"""

# pylint:disable=g-bad-import-order
import argparse
import sys


from googlecloudsdk.calliope import usage_text
from googlecloudsdk.core import properties


def FunctionExitAction(func):
  """Get an argparse.Action that runs the provided function, and exits.

  Args:
    func: func, the function to execute.

  Returns:
    argparse.Action, the action to use.
  """

  class Action(argparse.Action):

    def __init__(self, **kwargs):
      kwargs['nargs'] = 0
      super(Action, self).__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
      func()
      sys.exit(0)

  return Action


def StoreProperty(prop):
  """Get an argparse action that stores a value in a property.

  Also stores the value in the namespace object, like the default action. The
  value is stored in the invocation stack, rather than persisted permanently.

  Args:
    prop: properties._Property, The property that should get the invocation
        value.

  Returns:
    argparse.Action, An argparse action that routes the value correctly.
  """

  class Action(argparse.Action):
    """The action created for StoreProperty."""

    def __init__(self, *args, **kwargs):
      super(Action, self).__init__(*args, **kwargs)
      option_strings = kwargs.get('option_strings')
      if option_strings:
        option_string = option_strings[0]
      else:
        option_string = None
      properties.VALUES.SetInvocationValue(prop, None, option_string)

    def __call__(self, parser, namespace, values, option_string=None):
      properties.VALUES.SetInvocationValue(prop, values, option_string)
      setattr(namespace, self.dest, values)

  return Action


def StoreConstProperty(prop, const):
  """Get an argparse action that stores a constant in a property.

  Also stores the constannt in the namespace object, like the store_true action.
  The const is stored in the invocation stack, rather than persisted
  permanently.

  Args:
    prop: properties._Property, The property that should get the invocation
        value.
    const: str, The constant that should be stored in the property.

  Returns:
    argparse.Action, An argparse action that routes the value correctly.
  """

  class Action(argparse.Action):

    def __init__(self, *args, **kwargs):
      kwargs = dict(kwargs)
      kwargs['nargs'] = 0
      super(Action, self).__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
      properties.VALUES.SetInvocationValue(prop, const, option_string)
      setattr(namespace, self.dest, const)

  return Action


# pylint:disable=pointless-string-statement
""" Some example short help outputs follow.

$ gcloud -h
usage: gcloud            [optional flags] <group | command>
  group is one of        auth | components | config | dns | sql
  command is one of      init | interactive | su | version

Google Cloud Platform CLI/API.

optional flags:
  -h, --help             Print this help message and exit.
  --project PROJECT      Google Cloud Platform project to use for this
                         invocation.
  --quiet, -q            Disable all interactive prompts when running gcloud
                         commands.  If input is required, defaults will be used,
                         or an error will be raised.

groups:
  auth                   Manage oauth2 credentials for the Google Cloud SDK.
  components             Install, update, or remove the tools in the Google
                         Cloud SDK.
  config                 View and edit Google Cloud SDK properties.
  dns                    Manage Cloud DNS.
  sql                    Manage Cloud SQL databases.

commands:
  init                   Initialize a gcloud workspace in the current directory.
  interactive            Use this tool in an interactive python shell.
  su                     Switch the user account.
  version                Print version information for Cloud SDK components.



$ gcloud auth -h
usage: gcloud auth       [optional flags] <command>
  command is one of      activate_git_p2d | activate_refresh_token |
                         activate_service_account | list | login | revoke

Manage oauth2 credentials for the Google Cloud SDK.

optional flags:
  -h, --help             Print this help message and exit.

commands:
  activate_git_p2d       Activate an account for git push-to-deploy.
  activate_refresh_token
                         Get credentials via an existing refresh token.
  activate_service_account
                         Get credentials via the private key for a service
                         account.
  list                   List the accounts for known credentials.
  login                  Get credentials via Google's oauth2 web flow.
  revoke                 Revoke authorization for credentials.



$ gcloud sql instances create -h
usage: gcloud sql instances create
                         [optional flags] INSTANCE

Creates a new Cloud SQL instance.

optional flags:
  -h, --help             Print this help message and exit.
  --authorized-networks AUTHORIZED_NETWORKS
                         The list of external networks that are allowed to
                         connect to the instance. Specified in CIDR notation,
                         also known as 'slash' notation (e.g. 192.168.100.0/24).
  --authorized-gae-apps AUTHORIZED_GAE_APPS
                         List of App Engine app ids that can access this
                         instance.
  --activation-policy ACTIVATION_POLICY; default="ON_DEMAND"
                         The activation policy for this instance. This specifies
                         when the instance should be activated and is applicable
                         only when the instance state is RUNNABLE. Defaults to
                         ON_DEMAND.
  --follow-gae-app FOLLOW_GAE_APP
                         The App Engine app this instance should follow. It must
                         be in the same region as the instance.
  --backup-start-time BACKUP_START_TIME
                         Start time for the daily backup configuration in UTC
                         timezone,in the 24 hour format - HH:MM.
  --gce-zone GCE_ZONE    The preferred Compute Engine zone (e.g. us-central1-a,
                         us-central1-b, etc.).
  --pricing-plan PRICING_PLAN, -p PRICING_PLAN; default="PER_USE"
                         The pricing plan for this instance. Defaults to
                         PER_USE.
  --region REGION; default="us-east1"
                         The geographical region. Can be us-east1 or europe-
                         west1. Defaults to us-east1.
  --replication REPLICATION; default="SYNCHRONOUS"
                         The type of replication this instance uses. Defaults to
                         SYNCHRONOUS.
  --tier TIER, -t TIER; default="D0"
                         The tier of service for this instance, for example D0,
                         D1. Defaults to D0.
  --assign-ip            Specified if the instance must be assigned an IP
                         address.
  --enable-bin-log       Specified if binary log must be enabled. If backup
                         configuration is disabled, binary log must be disabled
                         as well.
  --no-backup            Specified if daily backup must be disabled.

positional arguments:
  INSTANCE               Cloud SQL instance ID.


"""



def ShortHelpAction(command, argument_interceptor, detailed_help=False):
  """Get an argparse.Action that prints a short help.

  Args:
    command: calliope._CommandCommon, The command object that we're helping.
    argument_interceptor: calliope._ArgumentInterceptor, the object that tracks
        all of the flags for this command or group.
    detailed_help: bool, If True, suggest using the 'help' command for detailed
        help.

  Returns:
    argparse.Action, the action to use.
  """

  class Action(argparse.Action):

    def __init__(self, **kwargs):
      kwargs['nargs'] = 0
      super(Action, self).__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
      print usage_text.ShortHelpText(command, argument_interceptor)

      if detailed_help:
        sys.stdout.write("""
  To see detailed help, run the following command.
    $ {tool} help {command_path}
  """.format(tool=command.GetPath()[0],
             command_path=' '.join(command.GetPath()[1:])))

      sys.exit(0)

  return Action
