"""Tests for mock_api."""

import path_initializer
path_initializer.InitSysPath()

import unittest
from gcutil_lib import mock_api_parser
from gcutil_lib import mock_api_types


class ParserTest(unittest.TestCase):
  def setUp(self):
    # Pass an empty document; we are calling individual methods directly.
    self._parser = mock_api_parser.Parser({})

  def testParseAnyType(self):
    result = self._parser._ParseType({'type': 'any'})
    self.assertTrue(isinstance(result, mock_api_types.AnyType))

  def testParseArrayType(self):
    # Array of simple types:
    for element in ('any', 'boolean', 'integer', 'number', 'string'):
      result = self._parser._ParseType(
          {'type': 'array', 'items': {'type': element}})
      self.assertTrue(isinstance(result, mock_api_types.ArrayType))
      self.assertTrue(
          result._element.__class__ is
          self._parser._ParseType({'type': element}).__class__)

    # Array of array
    for element in ('any', 'boolean', 'integer', 'number', 'string'):
      result = self._parser._ParseType(
          {
              'type': 'array',  # array
              'items': {
                  'type': 'array',  # of array
                  'items': {
                      'type': element  # of element
                  }
              }
          })

      self.assertTrue(isinstance(result, mock_api_types.ArrayType))
      self.assertTrue(isinstance(result._element, mock_api_types.ArrayType))
      self.assertTrue(
          result._element._element.__class__ is
          self._parser._ParseType({'type': element}).__class__)

    # Array of objects
    result = self._parser._ParseType(
        {
            'type': 'array',  # Array
            'items': {
                'type': 'object',  # of objects
                'properties': {
                    'key': {'type': 'string'},
                    'value': {'type': 'integer'}
                }
            }
        })
    self.assertTrue(isinstance(result, mock_api_types.ArrayType))
    element = result._element
    self.assertTrue(isinstance(element, mock_api_types.ObjectType))
    self.assertEquals(['key', 'value'], sorted(element._properties))

    key = element._properties['key']
    self.assertTrue(isinstance(key, mock_api_types.Property))
    self.assertEquals('key', key.name)
    self.assertTrue(isinstance(key.type, mock_api_types.StringType))

    value = element._properties['value']
    self.assertTrue(isinstance(value, mock_api_types.Property))
    self.assertEquals('value', value.name)
    self.assertTrue(isinstance(value.type, mock_api_types.IntegerType))

  def testParseBooleanType(self):
    result = self._parser._ParseType({'type': 'boolean'})
    self.assertTrue(isinstance(result, mock_api_types.BooleanType))

  def testParseIntegerType(self):
    # No format
    result = self._parser._ParseType({'type': 'integer'})
    self.assertTrue(isinstance(result, mock_api_types.IntegerType))

    # Format
    for fmt in ('int32', 'uint32'):
      result = self._parser._ParseType({'type': 'integer', 'format': fmt})
      self.assertTrue(isinstance(result, mock_api_types.IntegerType))
      self.assertEquals(fmt, result._format)

    # Invalid format
    self.assertRaises(ValueError, self._parser._ParseType,
                      {'type': 'integer', 'format': 'invalid-format'})

  def testParseNumberType(self):
    # No format
    result = self._parser._ParseType({'type': 'number'})
    self.assertTrue(isinstance(result, mock_api_types.NumberType))

    # Format
    for fmt in ('double', 'float'):
      result = self._parser._ParseType({'type': 'number', 'format': fmt})
      self.assertTrue(isinstance(result, mock_api_types.NumberType))
      self.assertEquals(fmt, result._format)

    # Invalid format
    self.assertRaises(ValueError, self._parser._ParseType,
                      {'type': 'number', 'format': 'invalid-format'})

  def testParseObjectType(self):
    result = self._parser._ParseType(
        {
            'type': 'object',
            'properties': {
                'code': {'type': 'string'},
                'data': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'value': {'type': 'number'},
                            'bool': {'type': 'boolean'}
                        }
                    }
                },
                'count': {'type': 'integer'}
            }
        })
    self.assertTrue(isinstance(result, mock_api_types.ObjectType))
    self.assertEquals(['code', 'count', 'data'], sorted(result._properties))

    # code is a string
    code = result._properties['code']
    self.assertTrue(isinstance(code, mock_api_types.Property))
    self.assertEquals('code', code.name)
    self.assertTrue(isinstance(code.type, mock_api_types.StringType))

    # data is a nested arry of objects
    data = result._properties['data']
    self.assertTrue(isinstance(data, mock_api_types.Property))
    self.assertEquals('data', data.name)
    self.assertTrue(isinstance(data.type, mock_api_types.ArrayType))

    element = data.type._element
    self.assertTrue(isinstance(element, mock_api_types.ObjectType))
    self.assertEquals(['bool', 'value'], sorted(element._properties))

    bool_property = element._properties['bool']
    self.assertTrue(isinstance(bool_property, mock_api_types.Property))
    self.assertEquals('bool', bool_property.name)
    self.assertTrue(isinstance(bool_property.type, mock_api_types.BooleanType))

    value = element._properties['value']
    self.assertTrue(isinstance(value, mock_api_types.Property))
    self.assertEquals('value', value.name)
    self.assertTrue(isinstance(value.type, mock_api_types.NumberType))

    # count is an integer property
    count = result._properties['count']
    self.assertTrue(isinstance(count, mock_api_types.Property))
    self.assertEqual('count', count.name)
    self.assertTrue(isinstance(count.type, mock_api_types.IntegerType))

  def testParseObjectTypeAdditional(self):
    result = self._parser._ParseType(
        {
            'type': 'object',
            'additionalProperties': {
                'type': 'object',
                'properties': {
                    'key': {'type': 'string'},
                    'value': {'type': 'string'}
                }
            }
        })

    self.assertTrue(isinstance(result, mock_api_types.ObjectType))
    self.assertEquals({}, result._properties)
    self.assertTrue(isinstance(result._additional, mock_api_types.ObjectType))
    self.assertEquals(['key', 'value'], sorted(result._additional._properties))
    self.assertTrue(result._additional._additional is None)

  def testParseObjectTypeAdditionalRef(self):
    result = self._parser._ParseType(
        {
            'type': 'object',
            'additionalProperties': {
                '$ref': 'Additional'
            }
        })

    self.assertTrue(isinstance(result, mock_api_types.ObjectType))
    self.assertTrue(isinstance(result._additional, mock_api_types.ObjectType))

    schema = self._parser._ParseSchema(
        {
            'id': 'Additional',
            'type': 'object',
            'properties': {
                'key': {'type': 'string'},
                'value': {'type': 'string'}
            }
        })

    self.assertTrue(result._additional is schema)

  def testParseStringType(self):
    # No format
    result = self._parser._ParseType({'type': 'string'})
    self.assertTrue(isinstance(result, mock_api_types.StringType))

    # Format
    for fmt in ('byte', 'date', 'date-time', 'int64', 'uint64'):
      result = self._parser._ParseType({'type': 'string', 'format': fmt})
      self.assertTrue(isinstance(result, mock_api_types.StringType))
      self.assertEquals(fmt, result._format)

    # Invalid format
    self.assertRaises(ValueError, self._parser._ParseType,
                      {'type': 'string', 'format': 'invalid-format'})

  def testParseReferenceType(self):
    result = self._parser._ParseType({'$ref': 'ReferencedObject'})
    self.assertTrue(isinstance(result, mock_api_types.ObjectType))
    self.assertTrue(result._name is None)
    self.assertTrue(result._properties is None)
    self.assertTrue(result._additional is None)

    schema = self._parser._ParseSchema(
        {
            'id': 'ReferencedObject',
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string'
                },
            }
        })

    self.assertTrue(schema is result)
    self.assertEquals('ReferencedObject', schema._name)
    self.assertEquals(['name'], sorted(schema._properties))
    self.assertTrue(schema._additional is None)

  def testParseMethodFull(self):
    self._parser._base_url = 'https://www.googleapis.com/compute/v1/projects/'
    result = self._parser._ParseMethod(
        'insert',
        {
            'id': 'compute.collection.insert',
            'path': '{project}/zones/{zone}/collection',
            'httpMethod': 'POST',
            'parameters': {
                'project': {
                    'type': 'string',
                    'required': True,
                    'location': 'path'
                },
                'zone': {
                    'type': 'string',
                    'required': True,
                    'location': 'path'
                }
            },
            'parameterOrder': [
                'project',
                'zone'
            ],
            'request': {
                '$ref': 'Instance'
            },
            'response': {
                '$ref': 'Operation'
            }
        })
    self.assertTrue(isinstance(result, mock_api_types.Method))
    self.assertEquals('insert', result._name)
    self.assertEquals('compute.collection.insert', result._id)
    self.assertEquals('https://www.googleapis.com/compute/v1/projects/'
                      '{project}/zones/{zone}/collection', result._path)

    # Parameters
    parameters = result._parameters
    self.assertEquals(2, len(parameters))

    project = parameters['project']
    self.assertTrue(isinstance(project, mock_api_types.Parameter))
    self.assertEquals('project', project.name)
    self.assertTrue(isinstance(project.type, mock_api_types.StringType))

    zone = parameters['zone']
    self.assertTrue(isinstance(zone, mock_api_types.Parameter))
    self.assertEquals('zone', zone.name)
    self.assertTrue(isinstance(zone.type, mock_api_types.StringType))

    # Request / Response
    self.assertTrue(isinstance(result._request, mock_api_types.ObjectType))
    self.assertTrue(isinstance(result._response, mock_api_types.ObjectType))

  def testParseMethodRequestResponse(self):
    result = self._parser._ParseMethod(
        'insert',
        {
            'id': 'compute.collection.insert',
            'request': {
                '$ref': 'Instance'
            },
            'response': {
                '$ref': 'Operation'
            }
        })
    self.assertTrue(isinstance(result._request, mock_api_types.ObjectType))
    self.assertTrue(isinstance(result._response, mock_api_types.ObjectType))

  def testParseMethodRequest(self):
    result = self._parser._ParseMethod(
        'insert',
        {
            'id': 'compute.collection.insert',
            'request': {
                '$ref': 'Instance'
            }
        })
    self.assertTrue(isinstance(result._request, mock_api_types.ObjectType))
    self.assertTrue(result._response is None)

  def testParseMethodResponse(self):
    result = self._parser._ParseMethod(
        'insert',
        {
            'id': 'compute.collection.insert',
            'response': {
                '$ref': 'Operation'
            }
        })

    self.assertTrue(result._request is None)
    self.assertTrue(isinstance(result._response, mock_api_types.ObjectType))

  def testParseMethodEmpty(self):
    result = self._parser._ParseMethod(
        'insert', {'id': 'compute.collection.insert'})

    self.assertEquals({}, result._parameters)
    self.assertTrue(result._request is None)
    self.assertTrue(result._response is None)

  def testParseGlobals(self):
    self._parser._ParseGlobals(
        {
            'baseUrl': 'https://www.googleapis.com/compute/v1/projects/',
            'parameters': {
                'prettyPrint': {
                    'type': 'boolean',
                    'location': 'query'
                }
            }
        })
    self.assertEquals('https://www.googleapis.com/compute/v1/projects/',
                      self._parser._base_url)
    self.assertEquals(1, len(self._parser._common_parameters))
    parameter = self._parser._common_parameters[0]
    self.assertEquals('prettyPrint', parameter.name)
    self.assertTrue(isinstance(parameter.type, mock_api_types.BooleanType))

if __name__ == '__main__':
  unittest.main()
