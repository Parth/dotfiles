# Copyright 2014 Google Inc. All Rights Reserved.

"""Initialize a gcloud workspace.

Creates a .gcloud folder. When gcloud starts, it looks for this .gcloud folder
in the cwd or one of the cwd's ancestors.
"""

import argparse
import os
import textwrap

from googlecloudapis.apitools.base import py as apitools_base
from googlecloudapis.source import v0 as source_v0
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exc
from googlecloudsdk.core import config
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core import workspaces
from googlecloudsdk.core.credentials import store as c_store
from googlecloudsdk.core.util import files


class Init(base.Command):
  """Create and initialize a gcloud workspace in the current directory."""

  detailed_help = {
      'DESCRIPTION': """\
          This command is creates and initializes a local workspace for a
          Google Cloud Platform project.

          The local workspace is indicated by the creation of a [{dotgcloud}]
          folder. In this folder is a file [properties] which allows you to
          override any global properties you may have set via the
          `$ gcloud config` command.

          When you run a Cloud SDK command-line tool from within this new
          workspace, it will use the new [properties] file as the first place to
          load properties. As a result, if you use gcloud, gcutil, gsutil, or
          any of the other commands in google-cloud-sdk/bin from within the
          workspace, they will connect to the correct project.

          If you have enabled push-to-deploy in the Cloud Console, one of the
          things that `gcloud init` will do for you is cloning the Google-hosted
          git repository associated with PROJECT. This repository will
          automatically be connected to Google, and it will use the credentials
          indicated as _active_ by `gcloud auth list`. Pushing
          to the origin's _master_ branch will trigger an App Engine deployment
          using the contents of that branch.
      """.format(dotgcloud=config.Paths.CLOUDSDK_WORKSPACE_CONFIG_DIR_NAME),
      'EXAMPLES': textwrap.dedent("""\
          To perform a simple `"Hello, world!"` App Engine deployment with this
          command, run the following command lines with MYPROJECT replaced by
          a project you own and can use for this experiment.

            $ gcloud auth login
            $ gcloud init MYPROJECT
            $ cd MYPROJECT/default
            $ git pull
              https://github.com/GoogleCloudPlatform/appengine-helloworld-python
            $ git push origin master
      """),
  }

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--devshell-image',
        help=argparse.SUPPRESS,
        required=False)
    project_arg = parser.add_argument(
        'project',
        help='The Google Cloud project to tie the workspace to.')
    project_arg.detailed_help = """\
        The name of the Google Cloud Platform project that you want to use in a
        local workspace that will be created by this command. If this project
        has an associated Google-hosted git repository, that repository will be
        cloned into the local workspace.
        """

  @c_exc.RaiseToolExceptionInsteadOf(workspaces.Error, c_store.Error)
  def Run(self, args):
    """Create the .gcloud folder, if possible.

    Args:
      args: argparse.Namespace, the arguments this command is run with.

    Raises:
      ToolException: on project initialization errors.

    Returns:
      The path to the new gcloud workspace.
    """
    # Ensure that we're logged in.
    creds = c_store.Load()

    is_new_directory = False

    try:
      workspace = workspaces.FromCWD()
      # Cannot re-init when in a workspace.
      current_project = workspace.GetProperty(properties.VALUES.core.project)
      if current_project != args.project:
        message = (
            'Directory [{root_directory}] is already initialized to project'
            ' [{project}].'
        ).format(
            root_directory=workspace.root_directory,
            project=current_project)
      else:
        message = (
            'Directory [{root_directory}] is already initialized.'
        ).format(root_directory=workspace.root_directory)
      raise c_exc.ToolException(message)
    except workspaces.NoContainingWorkspaceException:
      workspace_dir = os.path.join(os.getcwd(), args.project)
      message = (
          'Directory [{root_directory}] is not empty.'
      ).format(root_directory=workspace_dir)
      if os.path.exists(workspace_dir) and os.listdir(workspace_dir):
        raise c_exc.ToolException(message)
      else:
        files.MakeDir(workspace_dir)
        is_new_directory = True
        workspace = workspaces.Create(workspace_dir)

    workspace.SetProperty(properties.VALUES.core.project, args.project)
    if args.devshell_image:
      workspace.SetProperty(properties.VALUES.devshell.image,
                            args.devshell_image)

    # Everything that can fail should happen within this next try: block.
    # If something fails, and the result is an empty directory that we just
    # created, we clean it up.
    try:
      source_client = source_v0.SourceV0(credentials=creds)
      try:
        response = source_client.repos.List(source_v0.SourceReposListRequest(
            projectId=args.project))
      except apitools_base.HttpError:
        # Source API is down! Let's guess the repo.
        log.status.write(textwrap.dedent("""\
            Unable to fetch repository URL. Guessing the URL, but if your
            project uses repo-sync then the cloned repository may be read-only.
            """))
        try:
          workspace.CloneProjectRepository(
              args.project, workspaces.DEFAULT_REPOSITORY_ALIAS)
        except workspaces.CannotFetchRepositoryException as e:
          log.error(e)
      else:
        for repo in response.repos:
          try:
            workspace.CloneProjectRepository(
                args.project, repo.repoName, repo.cloneUrl)
          except workspaces.CannotFetchRepositoryException as e:
            log.error(e)
    finally:
      cleared_files = False
      if is_new_directory:
        dir_files = os.listdir(workspace_dir)
        if not dir_files or dir_files == [
            config.Paths().CLOUDSDK_WORKSPACE_CONFIG_DIR_NAME]:
          log.error(('Unable to initialize project [{project}], cleaning up'
                     ' [{path}].').format(
                         project=args.project, path=workspace_dir))
          files.RmTree(workspace_dir)
          cleared_files = True
    if cleared_files:
      raise c_exc.ToolException(
          'Unable to initialize project [{project}].'.format(
              project=args.project))
    log.status.write('Project [{prj}] was initialized in [{path}].\n'.format(
        path=workspace.root_directory,
        prj=args.project))

    return workspace
