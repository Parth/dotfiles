# Copyright 2014 Google Inc. All Rights Reserved.

"""Default value constants exposed by core utilities."""

LEGACY_REGISTRY = 'container.cloud.google.com'

DEFAULT_REGISTRY = 'gcr.io'

DEFAULT_DEVSHELL_IMAGE = (DEFAULT_REGISTRY +
                          '/dev_con/cloud-dev-common:prod')

# TODO(user): Change to container_prod
METADATA_IMAGE = DEFAULT_REGISTRY + '/_b_containers_qa/faux-metadata:latest'
