#!/usr/bin/env python
# Copyright 2011 Google Inc. All Rights Reserved.

"""Tests for bigquery_client.py."""



import itertools
import json
import tempfile

from google.apputils import googletest

import bigquery_client


class BigqueryClientTest(googletest.TestCase):

  def setUp(self):
    self.client = bigquery_client.BigqueryClient(api='http', api_version='')
    self.reference_tests = {
        'prj:': ('prj', '', ''),
        'example.com:prj': ('example.com:prj', '', ''),
        'example.com:prj-2': ('example.com:prj-2', '', ''),
        'www.example.com:prj': ('www.example.com:prj', '', ''),
        'prj:ds': ('prj', 'ds', ''),
        'example.com:prj:ds': ('example.com:prj', 'ds', ''),
        'prj:ds.tbl': ('prj', 'ds', 'tbl'),
        'example.com:prj:ds.tbl': ('example.com:prj', 'ds', 'tbl'),
        'prefix::example:buganizer.metadata.all': (
            'prefix::example', 'buganizer.metadata', 'all'),
        'prefix.example:buganizer.metadata.all': (
            'prefix.example', 'buganizer.metadata', 'all'),
        'prefix.example:foo_metrics.bar_walkups_sanitised.all': (
            'prefix.example', 'foo_metrics.bar_walkups_sanitised', 'all'),
        }
    self.parse_tests = self.reference_tests.copy()
    self.parse_tests.update({
        'ds.': ('', 'ds', ''),
        'ds.tbl': ('', 'ds', 'tbl'),
        'tbl': ('', '', 'tbl'),
        })
    self.field_names = ('projectId', 'datasetId', 'tableId')

  @staticmethod
  def _LengthToType(parts):
    if len(parts) == 1:
      return bigquery_client.ApiClientHelper.ProjectReference
    if len(parts) == 2:
      return bigquery_client.ApiClientHelper.DatasetReference
    if len(parts) == 3:
      return bigquery_client.ApiClientHelper.TableReference
    return None

  def _GetReference(self, parts):
    parts = filter(bool, parts)
    reference_type = BigqueryClientTest._LengthToType(parts)
    args = dict(itertools.izip(self.field_names, parts))
    return reference_type(**args)

  def testToCamel(self):
    self.assertEqual('lowerCamel', bigquery_client._ToLowerCamel('lower_camel'))

  def testReadSchemaFromFile(self):
    # Test the filename case.
    with tempfile.NamedTemporaryFile() as f:
      # Write out the results.
      print >>f, '['
      print >>f, ' { "name": "Number", "type": "integer", "mode": "REQUIRED" },'
      print >>f, ' { "name": "Name", "type": "string", "mode": "REQUIRED" },'
      print >>f, ' { "name": "Other", "type": "string", "mode": "OPTIONAL" }'
      print >>f, ']'
      f.flush()
      # Read them as JSON.
      f.seek(0)
      result = json.load(f)
      # Compare the results.
      self.assertEqual(result, self.client.ReadSchema(f.name))

  def testReadSchemaFromString(self):
    # Check some cases that should pass.
    self.assertEqual(
        [{'name': 'foo', 'type': 'INTEGER'}],
        bigquery_client.BigqueryClient.ReadSchema('foo:integer'))
    self.assertEqual(
        [{'name': 'foo', 'type': 'INTEGER'},
         {'name': 'bar', 'type': 'STRING'}],
        bigquery_client.BigqueryClient.ReadSchema('foo:integer, bar:string'))
    self.assertEqual(
        [{'name': 'foo', 'type': 'STRING'}],
        bigquery_client.BigqueryClient.ReadSchema('foo'))
    self.assertEqual(
        [{'name': 'foo', 'type': 'STRING'},
         {'name': 'bar', 'type': 'STRING'}],
        bigquery_client.BigqueryClient.ReadSchema('foo,bar'))
    self.assertEqual(
        [{'name': 'foo', 'type': 'INTEGER'},
         {'name': 'bar', 'type': 'STRING'}],
        bigquery_client.BigqueryClient.ReadSchema('foo:integer, bar'))
    # Check some cases that should fail.
    self.assertRaises(bigquery_client.BigquerySchemaError,
                      bigquery_client.BigqueryClient.ReadSchema,
                      '')
    self.assertRaises(bigquery_client.BigquerySchemaError,
                      bigquery_client.BigqueryClient.ReadSchema,
                      'foo,bar:int:baz')
    self.assertRaises(bigquery_client.BigquerySchemaError,
                      bigquery_client.BigqueryClient.ReadSchema,
                      'foo:int,,bar:string')
    self.assertRaises(bigquery_client.BigquerySchemaError,
                      bigquery_client.BigqueryClient.ReadSchema,
                      '../foo/bar/fake_filename')

  def testParseIdentifier(self):
    for identifier, parse in self.parse_tests.iteritems():
      self.assertEquals(parse, bigquery_client.BigqueryClient._ParseIdentifier(
          identifier))

  def testGetReference(self):
    for identifier, parse in self.reference_tests.iteritems():
      reference = self._GetReference(parse)
      self.assertEquals(reference, self.client.GetReference(identifier))

  def testParseDatasetReference(self):
    dataset_parses = dict((k, v) for k, v in self.reference_tests.iteritems()
                          if len(filter(bool, v)) == 2)

    for identifier, parse in dataset_parses.iteritems():
      reference = self._GetReference(parse)
      self.assertEquals(reference, self.client.GetDatasetReference(identifier))

  def testParseProjectReference(self):
    project_parses = dict((k, v) for k, v in self.reference_tests.iteritems()
                          if len(filter(bool, v)) == 1)

    for identifier, parse in project_parses.iteritems():
      reference = self._GetReference(parse)
      self.assertEquals(reference, self.client.GetProjectReference(identifier))

    invalid_projects = [
        'prj:ds', 'example.com:prj:ds', 'ds.', 'ds.tbl', 'prj:ds.tbl']

    for invalid in invalid_projects:
      self.assertRaises(bigquery_client.BigqueryError,
                        self.client.GetProjectReference, invalid)

  def testParseJobReference(self):
    self.assertTrue(self.client.GetJobReference('proj:job_id'))
    self.client.project_id = None
    self.assertRaises(bigquery_client.BigqueryError,
                      self.client.GetJobReference, 'job_id')
    self.client.project_id = 'proj'
    self.assertTrue(self.client.GetJobReference('job_id'))

    invalid_job_ids = [
        'prj:', 'example.com:prj:ds.tbl', 'ds.tbl', 'prj:ds.tbl']

    for invalid in invalid_job_ids:
      self.assertRaises(bigquery_client.BigqueryError,
                        self.client.GetJobReference, invalid)

  def testRaiseError(self):
    # Confirm we handle arbitrary errors gracefully.
    try:
      bigquery_client.BigqueryClient.RaiseError({})
    except bigquery_client.BigqueryError as _:
      pass

  def testJsonToInsertEntry(self):
    result = [
        bigquery_client.JsonToInsertEntry(None, '{"a":1}'),
        bigquery_client.JsonToInsertEntry('key', '{"b":2}'),
        ]
    self.assertEquals([None, 'key'], [x[0] for x in result])
    self.assertEquals(1, result[0][1]['a'])
    self.assertEquals(2, result[1][1]['b'])

    self.assertRaisesRegexp(
        bigquery_client.BigqueryClientError,
        r'Could not parse',
        bigquery_client.JsonToInsertEntry, None, '_junk_')
    self.assertRaisesRegexp(
        bigquery_client.BigqueryClientError,
        r'not a JSON object',
        bigquery_client.JsonToInsertEntry, None, '[1, 2]')


if __name__ == '__main__':
  googletest.main()
