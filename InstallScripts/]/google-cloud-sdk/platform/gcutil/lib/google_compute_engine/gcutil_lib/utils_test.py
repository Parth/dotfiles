"""Unit tests for the utils module."""



import path_initializer
path_initializer.InitSysPath()


import apiclient
import httplib2

import gflags as flags
import unittest

from gcutil_lib import old_mock_api
from gcutil_lib import utils


class FlattenListTests(unittest.TestCase):
  """Tests for utils.FlattenList."""
  test_cases = (
      ([[1], [2], [3]], [1, 2, 3]),
      ([[1, 2, 3], [4, 5], [6]], [1, 2, 3, 4, 5, 6]),
      ([['a'], ['    b '], ['c       ']], ['a', '    b ', 'c       ']),
      )

  def testFlattenList(self):
    for arg, expected in self.test_cases:
      self.assertEqual(utils.FlattenList(arg), expected)


class GlobsToFilterTests(unittest.TestCase):
  """Tests for utils.RegexesToFilterExpression."""
  test_cases = (
      (None, None),
      ([], None),
      (['instance-1'], 'instance-1'),
      (['instance-1 instance-2'], 'instance-1|instance-2'),
      (['instance-1', 'i.*'], 'instance-1|i.*'),
      (['a', 'b', 'c'], 'a|b|c'),
      (['a          b c'], 'a|b|c'),
      (['a          b c', 'd     e    f'], 'a|b|c|d|e|f'),
      (['instance-[0-9]+'], 'instance-[0-9]+'),
      (['a-[0-9]+', 'b-[0-9]+'], 'a-[0-9]+|b-[0-9]+'),
      (['  a-[0-9]+     b-[0-9]+ '], 'a-[0-9]+|b-[0-9]+'),
      )

  def testCombineRegexes(self):
    for arg, expected in self.test_cases:
      self.assertEqual(utils.CombineRegexes(arg), expected)


class ProtocolPortsTests(unittest.TestCase):

  def testParseProtocolFailures(self):
    failure_cases = (
        None, '', 'foo'
        )
    for failure_case in failure_cases:
      self.assertRaises(ValueError, utils.ParseProtocol, failure_case)

  def testParseProtocolSuccesses(self):
    test_cases = (
        (6, 6),
        ('6', 6),
        ('tcp', 6),
        ('udp', 17)
        )
    for arg, expected in test_cases:
      self.assertEqual(utils.ParseProtocol(arg), expected)

  def testReplacePortNamesFailures(self):
    failure_cases = (
        None, 22, '', 'foo', 'foo-bar', '24-42-2442'
        )
    for failure_case in failure_cases:
      self.assertRaises(ValueError, utils.ReplacePortNames, failure_case)

  def testReplacePortNameSuccesses(self):
    test_cases = (
        ('ssh', '22'),
        ('22', '22'),
        ('ssh-http', '22-80'),
        ('22-http', '22-80'),
        ('ssh-80', '22-80'),
        ('22-80', '22-80')
        )
    for arg, expected in test_cases:
      self.assertEqual(utils.ReplacePortNames(arg), expected)


class SingularizeTests(unittest.TestCase):
  """Tests for utils.Singularize."""

  test_cases = (
      ('instances', 'instance'),
      ('disks', 'disk'),
      ('firewalls', 'firewall'),
      ('snapshots', 'snapshot'),
      ('operations', 'operation'),
      ('images', 'image'),
      ('networks', 'network'),
      ('machineTypes', 'machineType'),
      )

  def testSingularize(self):
    for arg, expected in self.test_cases:
      self.assertEqual(utils.Singularize(arg), expected)
      self.assertEqual(utils.Singularize(expected), expected)


class AllTests(unittest.TestCase):
  """Tests for utils.All."""

  def setUp(self):
    self._page = 0

  def testArgumentPlumbing(self):

    # pylint: disable=redefined-builtin,g-bad-name
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None):
      self.assertEqual(project, 'my-project')
      self.assertEqual(maxResults, 500)
      self.assertEqual(filter, 'name eq my-instance')
      self.assertEqual(pageToken, None)
      return old_mock_api.MockRequest(
          {'kind': 'numbers', 'items': [1, 2, 3]})

    utils.All(MockFunc, 'my-project',
              max_results=651,
              filter='name eq my-instance')

  def testSkipIfNotFoundWhenTrue(self):

    # pylint: disable=unused-argument,redefined-builtin,g-bad-name
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None):
      if project == 'project-1':
        return old_mock_api.MockRequest(
            {'kind': 'numbers', 'items': [1, 2, 3]})
      elif project == 'project-2':
        raise apiclient.errors.HttpError(
            httplib2.Response({'status': 404, 'reason': 'project not found'}),
            'content')
      elif project == 'project-3':
        return old_mock_api.MockRequest(
            {'kind': 'numbers', 'items': [4, 5, 6]})

    self.assertEqual(utils.All(MockFunc,
                               ['project-1', 'project-2', 'project-3'],
                               skip_if_not_found=True),
                     {'kind': 'numbers', 'items': [1, 2, 3, 4, 5, 6]})

  def testSkipIfNotFoundWhenFalse(self):

    # pylint: disable=unused-argument,redefined-builtin,g-bad-name
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None):
      if project == 'project-1':
        return old_mock_api.MockRequest(
            {'kind': 'numbers', 'items': [1, 2, 3]})
      elif project == 'project-2':
        raise apiclient.errors.HttpError(
            httplib2.Response({'status': 404, 'reason': 'project not found'}),
            'content')
      elif project == 'project-3':
        return old_mock_api.MockRequest(
            {'kind': 'numbers', 'items': [4, 5, 6]})

    try:
      utils.All(MockFunc, ['project-1', 'project-2', 'project-3'])
      self.fail()

    except apiclient.errors.HttpError:
      pass

  def testAllAggregatedSkipIfNotFoundWhenTrue(self):

    # pylint: disable=unused-argument,redefined-builtin,g-bad-name
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None):
      if project == 'project-1':
        return old_mock_api.MockRequest(
            {'kind': 'numbers',
             'items': {'numbers': {'items': [1, 2, 3]}}})
      elif project == 'project-2':
        raise apiclient.errors.HttpError(
            httplib2.Response({'status': 404, 'reason': 'project not found'}),
            'content')
      elif project == 'project-3':
        return old_mock_api.MockRequest(
            {'kind': 'numbers',
             'items': {'numbers': {'items': [4, 5, 6]}}})

    self.assertEqual(
        utils.AllAggregated(MockFunc, ['project-1', 'project-2', 'project-3'],
                            skip_if_not_found=True),
        {'items': {'numbers': {'items': [1, 2, 3, 4, 5, 6]}},
         'kind': 'numbers'})

  def testAllAggregatedSkipIfNotFoundWhenFalse(self):

    # pylint: disable=unused-argument,redefined-builtin,g-bad-name
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None):
      if project == 'project-1':
        return old_mock_api.MockRequest(
            {'kind': 'numbers',
             'items': {'numbers': {'items': [1, 2, 3]}}})
      elif project == 'project-2':
        raise apiclient.errors.HttpError(
            httplib2.Response({'status': 404, 'reason': 'project not found'}),
            'content')
      elif project == 'project-3':
        return old_mock_api.MockRequest(
            {'kind': 'numbers',
             'items': {'numbers': {'items': [4, 5, 6]}}})

    try:
      utils.AllAggregated(MockFunc, ['project-1', 'project-2', 'project-3'])
      self.fail()

    except apiclient.errors.HttpError:
      pass

  def testMaxResults(self):
    # pylint: disable=unused-argument,redefined-builtin,g-bad-name
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None):
      self.assertEqual(maxResults, 37)
      return old_mock_api.MockRequest({'kind': 'numbers', 'items': [1, 2, 3]})

    utils.All(MockFunc, 'my-project',
              max_results=37,
              filter='name eq my-instance')

    def MockAggregatedFunc(
        project=None, maxResults=None, filter=None, pageToken=None):
      self.assertEqual(maxResults, 37)
      return old_mock_api.MockRequest(
          {'items':
               {'danger-zone':
                    {'numbers':
                         [{'kind': 'numbers', 'items': [1, 2, 3]}]}}})

    utils.AllAggregated(MockAggregatedFunc, 'my-project',
                        max_results=37,
                        filter='name eq my-instance')

  def testMaxResults2(self):
    max_result_values = []  # maxResult parameter values collected by MockFunc
    returned_counts = [80, 40, 50]  # Server returns these counts of objects

    # pylint: disable=unused-argument,g-bad-name,redefined-builtin
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None):
      max_result_values.append(maxResults)
      return old_mock_api.MockRequest({
          'kind': 'numbers',
          'items': range(returned_counts[len(max_result_values) - 1]),
          'nextPageToken': 'next'
          })

    utils.All(MockFunc, 'my-project',
              max_results=150,
              filter='name eq my-instance')
    self.assertEqual((150, 70, 30), tuple(max_result_values))

  def testMaxResults3(self):
    # pylint: disable=unused-argument,g-bad-name,redefined-builtin
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None):
      self.assertEquals(500, maxResults)
      return old_mock_api.MockRequest({})

    utils.AllAggregated(MockFunc, 'my-project')

  def testWithZones(self):
    # pylint: disable=unused-argument,redefined-builtin,g-bad-name
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None,
                 zone=None):
      self.assertEqual('some-zone', zone)
      return old_mock_api.MockRequest(
          {'kind': 'numbers', 'items': [1, 2, 3]})

    utils.All(MockFunc, 'my-project', zone='some-zone')

  def testWithEmptyResponse(self):

    # pylint: disable=unused-argument,redefined-builtin,g-bad-name
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None):
      return old_mock_api.MockRequest({'kind': 'numbers', 'items': []})

    self.assertEqual(utils.All(MockFunc, 'my-project'),
                     {'kind': 'numbers', 'items': []})

  def testWithNoPaging(self):

    # pylint: disable=unused-argument,redefined-builtin,g-bad-name
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None):
      return old_mock_api.MockRequest({'kind': 'numbers', 'items': [1, 2, 3]})

    self.assertEqual(utils.All(MockFunc, 'my-project'),
                     {'kind': 'numbers', 'items': [1, 2, 3]})

  def testWithPaging(self):
    responses = [
        old_mock_api.MockRequest(
            {'kind': 'numbers', 'items': [1, 2, 3], 'nextPageToken': 'abc'}),
        old_mock_api.MockRequest(
            {'kind': 'numbers', 'items': [4, 5, 6]})]

    # pylint: disable=unused-argument,redefined-builtin,g-bad-name
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None):
      self._page += 1
      return responses[self._page - 1]

    self.assertEqual(utils.All(MockFunc, 'my-project'),
                     {'kind': 'numbers', 'items': [1, 2, 3, 4, 5, 6]})

  def testWithNoPagingAndSlicing(self):

    # pylint: disable=unused-argument,redefined-builtin,g-bad-name
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None):
      return old_mock_api.MockRequest({'kind': 'numbers', 'items': [1, 2, 3]})

    self.assertEqual(utils.All(MockFunc, 'my-project', max_results=2),
                     {'kind': 'numbers', 'items': [1, 2]})

  def testWithPagingAndSlicing(self):
    responses = [
        old_mock_api.MockRequest(
            {'kind': 'numbers', 'items': [1, 2, 3], 'nextPageToken': 'abc'}),
        old_mock_api.MockRequest(
            {'kind': 'numbers', 'items': [4, 5, 6]})]

    # pylint: disable=unused-argument,redefined-builtin,g-bad-name
    def MockFunc(project=None, maxResults=None, filter=None, pageToken=None):
      self._page += 1
      return responses[self._page - 1]

    self.assertEqual(utils.All(MockFunc, 'my-project', max_results=5),
                     {'kind': 'numbers', 'items': [1, 2, 3, 4, 5]})

  def testIsAnyScopeFlagSpecified(self):
    flag_values = flags.FlagValues()
    flags.DEFINE_string('zone', None, 'zone', flag_values)
    flags.DEFINE_string('region', None, 'region', flag_values)
    flags.DEFINE_bool('global', False, 'global', flag_values)

    def Set(name, value):
      flag_values[name].present = 1
      flag_values[name].value = value

    def Clear(name):
      flag_values[name].present = 0
      flag_values[name].value = flag_values[name].default

    #
    # The order of Set/Clear below is important to test all combinations.
    #

    # Nothing is set
    self.assertFalse(utils.IsAnyScopeFlagSpecified(flag_values))

    # Zone
    Set('zone', 'my-test-zone')
    self.assertTrue(utils.IsAnyScopeFlagSpecified(flag_values))

    # Zone + Global
    Set('global', True)
    self.assertTrue(utils.IsAnyScopeFlagSpecified(flag_values))

    # Global
    Clear('zone')
    self.assertTrue(utils.IsAnyScopeFlagSpecified(flag_values))

    # Region + Global
    Set('region', 'my-test-region')
    self.assertTrue(utils.IsAnyScopeFlagSpecified(flag_values))

    # Region
    Clear('global')
    self.assertTrue(utils.IsAnyScopeFlagSpecified(flag_values))

    # Region + Zone
    Set('zone', 'my-test-zone')
    self.assertTrue(utils.IsAnyScopeFlagSpecified(flag_values))

    # Zone + Region + Global
    Set('global', True)
    self.assertTrue(utils.IsAnyScopeFlagSpecified(flag_values))

  def testCombineListResults(self):
    result1 = {'kind': 'cloud#object', 'items': ['item1', 'item2', 'item3']}
    result2 = {'kind': 'cloud#object', 'items': ['item4', 'item5', 'item6']}

    self.assertTrue(None is utils.CombineListResults(None, None))
    self.assertTrue(result1 is utils.CombineListResults(result1, None))
    self.assertTrue(result2 is utils.CombineListResults(None, result2))

    result = utils.CombineListResults(result1, result2)
    self.assertEquals('cloud#object', result['kind'])
    self.assertEquals(result1['items'] + result2['items'], result['items'])

    result = utils.CombineListResults({}, result2)
    self.assertEquals('cloud#object', result['kind'])
    self.assertEquals(result2, result)

    result = utils.CombineListResults(result1, {})
    self.assertEquals('cloud#object', result['kind'])
    self.assertEquals(result1, result)


if __name__ == '__main__':
  unittest.main()
