"""Tests for mock_api."""

import path_initializer
path_initializer.InitSysPath()

import unittest
from gcutil_lib import mock_api
from gcutil_lib import mock_api_server


class MockApiTest(unittest.TestCase):
  def testCreateV1(self):
    mock, api = mock_api.CreateApi('v1')
    self.assertTrue(isinstance(mock, mock_api_server.MockServer))
    self.assertTrue(api is not None)
    # Add tests here for presence of v1-specific collections.



if __name__ == '__main__':
  unittest.main()
