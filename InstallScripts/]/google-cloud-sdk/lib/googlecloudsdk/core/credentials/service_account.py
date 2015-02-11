# Copyright 2014 Google Inc. All Rights Reserved.

"""One-line documentation for auth module.

A detailed description of auth.
"""

import json

from oauth2client import client
from oauth2client import service_account

from googlecloudsdk.core import config


# pylint: disable=protected-access, until oauth2client properly exposes class
class ServiceAccountCredentials(service_account._ServiceAccountCredentials):

  def to_json(self):
    self.service_account_name = self._service_account_email
    strip = ['_private_key'] + client.Credentials.NON_SERIALIZED_MEMBERS
    return super(ServiceAccountCredentials, self)._to_json(strip)

  @classmethod
  def from_json(cls, s):
    data = json.loads(s)
    retval = ServiceAccountCredentials(
        service_account_id=data['_service_account_id'],
        service_account_email=data['_service_account_email'],
        private_key_id=data['_private_key_id'],
        private_key_pkcs8_text=data['_private_key_pkcs8_text'],
        scopes=config.CLOUDSDK_SCOPES,
        user_agent=config.CLOUDSDK_USER_AGENT)
    retval.invalid = data['invalid']
    retval.access_token = data['access_token']
    return retval
