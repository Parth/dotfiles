# Copyright 2014 Google Inc. All Rights Reserved.

"""Library for launching a docker container serving GCE-style metadata."""

from collections import namedtuple
import json
import random
import string
import subprocess
import tempfile

from googlecloudsdk.core import config
from googlecloudsdk.core import log
from googlecloudsdk.core.util import constants as const_lib
from googlecloudsdk.core.util import docker as docker_lib

MANIFEST_FORMAT = """\
computeMetadata:
  v1: &V1
    project:
      projectId: &PROJECT-ID
        {project_id}
      # TODO(mattmoor): remove gcloud's dependency on this.
      numericProjectId: 1234
    instance:
      attributes: {attributes}
      projectId: *PROJECT-ID
      hostname: test-hostname.kir
      machineType: n1-standard-1
      maintenanceEvent: NONE
      serviceAccounts:
        # Use YAML magic to minimize redundancy
        default: *DEFAULT
        {email}: &DEFAULT
          email: {email}
          scopes: {scopes}
      zone: us-central1-a
"""


class MetadataOptions(namedtuple('_MetadataOptionsT',
                                 ['account', 'credential', 'project',
                                  'attributes', 'scopes'])):
  """Options for creating and running the fake metadata service."""

  def __new__(cls, account=None, credential=None, project=None,
              attributes=None, scopes=None):
    """Initialize a new MetadataOptions named tuple."""
    if not attributes:
      attributes = {}
    if not scopes:
      scopes = config.CLOUDSDK_SCOPES
    return super(MetadataOptions, cls).__new__(
        cls, account=account, credential=credential, project=project,
        attributes=attributes, scopes=scopes)


class FakeMetadata(object):
  """Creates a Fake Metadata instance usable via 'with'."""

  def __init__(self, image, options):
    """Initialize the fake metadata instance."""
    self._image = image
    self._options = options
    suffix = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(5))
    self._name = 'metadata-%s' % suffix

  @property
  def name(self):
    """String, identifying a container. Required for linking."""
    return self._name

  @property
  def image(self):
    """String, identifying a fake-metadata image to be run."""
    return self._image

  def __enter__(self):
    """Makes FakeMetadata usable with "with" statement."""
    log.Print('Surfacing credentials via {metadata}...'.format(
        metadata=self._name))

    manifest = tempfile.NamedTemporaryFile(suffix='.yaml').name
    with open(manifest, 'w') as f_out:
      f_out.write(MANIFEST_FORMAT.format(
          attributes=json.dumps(self._options.attributes),
          project_id=self._options.project,
          email=self._options.account,
          scopes=json.dumps(self._options.scopes)))

    # We refresh credentials in case a pull is needed.
    docker_lib.UpdateDockerCredentials(const_lib.DEFAULT_REGISTRY)
    subprocess.check_call([
        'docker', 'run', '-d',
        '--name', self._name,
        '-v', manifest + ':' + manifest,
        self.image,
        # Arguments to the //cloud/containers/metadata binary,
        # which is the entrypoint:
        '-manifest_file='+manifest,
        '-refresh_token='+self._options.credential.refresh_token],
                          stdin=None, stdout=None, stderr=None)
    return self

  # pylint: disable=redefined-builtin
  def __exit__(self, type, value, traceback):
    """Makes FakeMetadata usable with "with" statement."""
    log.Print('Shutting down metadata credentials')
    subprocess.check_call(['docker', 'rm', '-f', self._name],
                          stdin=None, stdout=None, stderr=None)
