"""Tests for mock_api_types."""

import path_initializer
path_initializer.InitSysPath()

import base64


import unittest
from gcutil_lib import mock_api_types


class TypeTest(unittest.TestCase):
  def testObjectTypeStr(self):
    properties = [
        mock_api_types.Property('name', mock_api_types.StringType(None)),
        mock_api_types.Property('value', mock_api_types.IntegerType('int32'))
    ]
    object_type = mock_api_types.ObjectType()
    object_type.Define('Object', properties, None)

    self.assertEquals('<Object [\'name\', \'value\']>', str(object_type))

  def testAnyTypeValidate(self):
    any_type = mock_api_types.AnyType()
    any_value = (None, 'string', 3, 3.14, [], {})
    for value in any_value:
      any_type.Validate('method', 'path', value)

  def testAnyTypeValidateString(self):
    any_type = mock_api_types.AnyType()
    any_value = ('true', 'string', '3', '3.14', '[]', '{}')
    for value in any_value:
      self.assertRaises(mock_api_types.ValidationError,
                        any_type.ValidateString, 'method', 'path', value)

  def testBooleanValidate(self):
    boolean_type = mock_api_types.BooleanType()
    boolean_type.Validate('method', 'path', True)
    boolean_type.Validate('method', 'path', False)

    non_bools = (None, 'string', 3, 3.14, [], {})
    for value in non_bools:
      self.assertRaises(mock_api_types.ValidationError,
                        boolean_type.Validate, 'method', 'path', value)

  def testBooleanValidateString(self):
    boolean_type = mock_api_types.BooleanType()
    boolean_type.ValidateString('method', 'path', 'true')
    boolean_type.ValidateString('method', 'path', 'false')

    non_bools = (None, 'string', '3', '3.14')
    for value in non_bools:
      self.assertRaises(mock_api_types.ValidationError,
                        boolean_type.ValidateString, 'method', 'path', value)

  def testStringTypeValidate(self):
    string_type = mock_api_types.StringType(None)
    string_type.Validate('method', 'path', 'string')
    string_type.Validate('method', 'path', u'unicode')

    non_strings = (None, 3, 3.14, [], {})
    for value in non_strings:
      self.assertRaises(mock_api_types.ValidationError,
                        string_type.Validate, 'method', 'path', value)

  def testStringTypeValidateString(self):
    string_type = mock_api_types.StringType(None)
    string_type.ValidateString('method', 'path', 'string')
    string_type.ValidateString('method', 'path', u'unicode')

  def testStringTypeValidateByte(self):
    string_type = mock_api_types.StringType('byte')
    value = base64.urlsafe_b64encode('encoded string')
    string_type.Validate('method', 'path', value)

    non_bytes = (None, 3, 3.14, [], {}, 'non-base64')
    for value in non_bytes:
      self.assertRaises(mock_api_types.ValidationError,
                        string_type.Validate, 'method', 'path', value)

  def testStringTypeValidateDate(self):
    string_type = mock_api_types.StringType('date')
    value = '2013-05-18'
    string_type.Validate('method', 'path', value)

    non_dates = (None, 3, 3.14, [], {}, 'non-date',
                 '2013',
                 '2013-05',
                 '2013-05-18T',
                 '2013-05-18T14',
                 '2013-05-18T14:42',
                 '2013-05-18T14:42:37',
                 '2013-05-18T14:42:37.',
                 '2013-05-18T14:42:37.425',
                 '2013-05-18T14:42:37.425Z')
    for value in non_dates:
      self.assertRaises(mock_api_types.ValidationError,
                        string_type.Validate, 'method', 'path', value)

  def testStringTypeValidateDateTime(self):
    string_type = mock_api_types.StringType('date-time')
    value = '2013-05-18T14:42:37.425Z'
    string_type.Validate('method', 'path', value)

    non_date_times = (None, 3, 3.14, [], {}, 'non-date-time',
                      '2013',
                      '2013-05',
                      '2013-05-18',
                      '2013-05-18T',
                      '2013-05-18T14',
                      '2013-05-18T14:42',
                      '2013-05-18T14:42:37',
                      '2013-05-18T14:42:37.',
                      '2013-05-18T14:42:37.425')
    for value in non_date_times:
      self.assertRaises(mock_api_types.ValidationError,
                        string_type.Validate, 'method', 'path', value)

  def testStringTypeValidateInt64(self):
    string_type = mock_api_types.StringType('int64')
    values = (
        '0',
        '253489657232345',
        str(2**63 - 1),
        str(-(2**63)))

    for value in values:
      string_type.Validate('method', 'path', value)

    non_int64s = (None, 3, 3.14, [], {}, 'non-int64',
                  str(2**64), str(2**63), str(-(2**63)-1))
    for value in non_int64s:
      self.assertRaises(mock_api_types.ValidationError,
                        string_type.Validate, 'method', 'path', value)

  def testStringTypeValidateUInt64(self):
    string_type = mock_api_types.StringType('uint64')
    values = (
        '0',
        '253489657232345',
        str(2**63),
        str(2**64 - 1))

    for value in values:
      string_type.Validate('method', 'path', value)

    non_int64s = (None, 3, 3.14, [], {}, 'non-uint64',
                  str(2**64), '-1')
    for value in non_int64s:
      self.assertRaises(mock_api_types.ValidationError,
                        string_type.Validate, 'method', 'path', value)

  def testIntegerTypeValidate(self):
    integer_type = mock_api_types.IntegerType(None)

    for value in (-2147483648, 0, 2147483647, 3):
      integer_type.Validate('method', 'path', value)
      integer_type.Validate('method', 'path', int(value))
      integer_type.Validate('method', 'path', long(value))

    non_integers = (None, 3.14, [], {}, 'non-integer',
                    2**32, 2**31, -(2**31) - 1)
    for value in non_integers:
      self.assertRaises(mock_api_types.ValidationError,
                        integer_type.Validate, 'method', 'path', value)

  def testIntegerTypeValidateString(self):
    integer_type = mock_api_types.IntegerType(None)

    for value in (-2147483648, 0, 2147483647, 3):
      integer_type.ValidateString('method', 'path', str(value))

    non_integers = (None, 3.14, [], {}, 'non-integer',
                    2**32, 2**31, -(2**31) - 1)
    for value in non_integers:
      self.assertRaises(mock_api_types.ValidationError,
                        integer_type.ValidateString,
                        'method', 'path', str(value))

  def testIntegerTypeValidateInt32(self):
    integer_type = mock_api_types.IntegerType('int32')

    for value in (-2147483648, 0, 2147483647, 3):
      integer_type.Validate('method', 'path', value)
      integer_type.Validate('method', 'path', int(value))
      integer_type.Validate('method', 'path', long(value))

    non_int32s = (None, 3.14, [], {}, 'non-integer',
                  2**32, 2**31, -(2**31) - 1)
    for value in non_int32s:
      self.assertRaises(mock_api_types.ValidationError,
                        integer_type.Validate, 'method', 'path', value)

  def testIntegerTypeValidateStringInt32(self):
    integer_type = mock_api_types.IntegerType('int32')

    for value in (-2147483648, 0, 2147483647, 3):
      integer_type.ValidateString('method', 'path', str(value))

    non_int32s = (None, 3.14, [], {}, 'non-integer',
                  2**32, 2**31, -(2**31) - 1)
    for value in non_int32s:
      self.assertRaises(mock_api_types.ValidationError,
                        integer_type.ValidateString,
                        'method', 'path', str(value))

  def testIntegerTypeValidateUInt32(self):
    integer_type = mock_api_types.IntegerType('uint32')

    for value in (0, 2147483647, 3, 2**32 - 1):
      integer_type.Validate('method', 'path', value)
      integer_type.Validate('method', 'path', int(value))
      integer_type.Validate('method', 'path', long(value))

    non_uint32s = (None, 3.14, [], {}, 'non-integer',
                   -2147483648, 2**32, -1)
    for value in non_uint32s:
      self.assertRaises(mock_api_types.ValidationError,
                        integer_type.Validate, 'method', 'path', value)

  def testIntegerTypeValidateStringUInt32(self):
    integer_type = mock_api_types.IntegerType('uint32')

    for value in (0, 2147483647, 3, 2**32 - 1):
      integer_type.ValidateString('method', 'path', str(value))

    non_uint32s = (None, 3.14, [], {}, 'non-integer',
                   -2147483648, 2**32, -1)
    for value in non_uint32s:
      self.assertRaises(mock_api_types.ValidationError,
                        integer_type.ValidateString,
                        'method', 'path', str(value))

  def testNumberTypeValidate(self):
    number_type = mock_api_types.NumberType(None)

    for value in (1, 0, -214783647, 3.14, 500e-3, 1345234523L):
      number_type.Validate('method', 'path', value)

    non_numbers = (None, [], {}, 'non-number')
    for value in non_numbers:
      self.assertRaises(mock_api_types.ValidationError,
                        number_type.Validate, 'method', 'path', value)

  def testNumberTypeValidateString(self):
    number_type = mock_api_types.NumberType(None)

    for value in (1, 0, -214783647, 3.14, 500e-3, 1345234523L):
      number_type.ValidateString('method', 'path', str(value))

    non_numbers = (None, [], {}, 'non-number')
    for value in non_numbers:
      self.assertRaises(mock_api_types.ValidationError,
                        number_type.ValidateString,
                        'method', 'path', str(value))

  def testArrayTypeValidate(self):
    # Array of string
    array_type = mock_api_types.ArrayType(mock_api_types.StringType(None))

    for value in (
        (),
        [],
        ('string-value',),
        ['string-value'],
        ('string1', 'string2'),
        ['string1', 'string2']):
      array_type.Validate('method', 'path', value)

    for value in (
        (123,),
        [()],
        {},
        ({},),
        ['string', 7],
        ('string', 3.14),
        ['string', True]):
      self.assertRaises(mock_api_types.ValidationError,
                        array_type.Validate, 'method', 'path', value)
    try:
      array_type.Validate('method', 'path', ['good', 'good', 7, 'good'])
      self.fail('Validation should have failed.')
    except mock_api_types.ValidationError, e:
      self.assertEquals('method path[2]: expected string, but received 7',
                        e.message)

  def testObjectTypeValidate(self):
    object_type = mock_api_types.ObjectType()
    object_type.Define(
        'TestType',
        (
            mock_api_types.Property(
                name='key', type=mock_api_types.StringType(None)),
            mock_api_types.Property(
                name='value', type=mock_api_types.IntegerType(None))
        ),
        None)

    for value in (
        {},
        {'key': 'test-key'},
        {'value': 17},
        {'key': 'test-key2', 'value': 19}):
      object_type.Validate('method', 'path', value)

    for value in (
        (),
        [],
        'key',
        17,
        3.14,
        234985342089L,
        {'name': 'invalid-property'},
        {'value': 'invalid-valie'}
        ):
      self.assertRaises(mock_api_types.ValidationError,
                        object_type.Validate, 'method', 'path', value)

    try:
      object_type.Validate('method', 'path', {'bad': 'some-name'})
      self.fail('Validation should have failed.')
    except mock_api_types.ValidationError, e:
      self.assertEquals('method path: Unexpected property bad in '
                        '{\'bad\': \'some-name\'}.',
                        e.message)

  def testObjectTypeValidateAdditional(self):
    additional = mock_api_types.ObjectType()
    additional.Define(
        'AdditionalType',
        (
            mock_api_types.Property(
                name='key', type=mock_api_types.StringType(None)),
            mock_api_types.Property(
                name='value', type=mock_api_types.IntegerType(None))
        ),
        None)
    object_type = mock_api_types.ObjectType()
    object_type.Define('TestAdditional', None, additional)

    object_type.Validate('method', 'path', {
        'element-one': {'key': 'key-one', 'value': 7},
        'element-two': {'key': 'key-two', 'value': 11}
    })


class MethodTest(unittest.TestCase):

  def setUp(self):
    self._request = mock_api_types.ObjectType()
    self._request.Define(
        'Request',
        (mock_api_types.Property(
            name='request', type=mock_api_types.StringType(None)),),
        None)

    self._response = mock_api_types.ObjectType()
    self._response.Define(
        'Response',
        (mock_api_types.Property(
            name='response', type=mock_api_types.IntegerType(None)),),
        None)

  def testTryStringToJson(self):
    self.assertEquals({}, mock_api_types.Method._TryStringToJson('{}'))
    self.assertEquals([], mock_api_types.Method._TryStringToJson('[]'))
    self.assertEquals('/not-a-json',
                      mock_api_types.Method._TryStringToJson('/not-a-json'))

  def testValidateBody(self):
    method = mock_api_types.Method('compute.networks.insert', 'insert', '',
                                   (), self._request, self._response)

    # Call _ValidateBody directly
    method._ValidateBody('request', self._request, {'request': 'request-value'})
    method._ValidateBody('response', self._response, {'response': 13})

    # Expect non-empty body, give empy.
    self.assertRaises(mock_api_types.ValidationError,
                      method._ValidateBody, 'request', self._request, None)

    # Expect empty body, give non-empy.
    self.assertRaises(mock_api_types.ValidationError,
                      method._ValidateBody, 'request', None, {})

    # Give invalid body.
    self.assertRaises(mock_api_types.ValidationError,
                      method._ValidateBody, 'request', self._request,
                      {'response': 13})

  def testValidateRequest(self):
    method = mock_api_types.Method(
        'compute.networks.insert', 'insert', 'http://uri',
        (), self._request, self._response)

    method.ValidateRequest('http://uri', {'request': 'request-value'})

    for body in (None, 7, []):
      self.assertRaises(mock_api_types.ValidationError,
                        method.ValidateRequest, 'http://uri', body)

  def testValidateResponse(self):
    method = mock_api_types.Method('compute.networks.insert', 'insert', '',
                                   (), self._request, self._response)

    method.ValidateResponse({'response': 13})

    for body in (None, 7, []):
      self.assertRaises(mock_api_types.ValidationError,
                        method.ValidateResponse, body)

  def testValidateParameters(self):
    method = mock_api_types.Method(
        'compute.instances.list', 'list',
        ('https://www.googleapis.com/compute/v1/'
         'projects/{project}/zones/{zone}/instances'),
        {
            'filter': mock_api_types.Parameter(
                name='filter', type=mock_api_types.StringType(None)),
            'maxResults': mock_api_types.Parameter(
                name='maxResults', type=mock_api_types.IntegerType('int32')),
            'project': mock_api_types.Parameter(
                name='project', type=mock_api_types.StringType('uint64')),
            'zone': mock_api_types.Parameter(
                name='zone', type=mock_api_types.NumberType('double')),
            'all': mock_api_types.Parameter(
                name='all', type=mock_api_types.BooleanType())
        }, None, None)

    parameters = method._ValidateParameters(
        'https://www.googleapis.com/compute/v1/'
        'projects/1234567890/zones/3.14159265/instances?'
        'filter=filter-expression&'
        'maxResults=132&'
        'all=false')
    self.assertEquals(
        {'filter': 'filter-expression',
         'maxResults': '132',
         'project': '1234567890',
         'zone': '3.14159265',
         'all': 'false'},
        parameters)

    # Invalid cases. The base URL will be prepended to all these values below.
    invalid_suffixes = (
        '',
        '1234567890',
        '1234567890/zones',
        '1234567890/zones/3.14159265',
        'my-project/zones/3.14159265/instances',
        '1234567890/zones/my-zone/instances',
        '1234567890/zones/3.14159265/instances?maxResults=hello',
        '1234567890/zones/3.14159265/instances?all=yes-please')

    for suffix in invalid_suffixes:
      self.assertRaises(
          mock_api_types.ValidationError,
          method._ValidateParameters,
          'https://www.googleapis.com/compute/v1/projects/' + suffix)

if __name__ == '__main__':
  unittest.main()
