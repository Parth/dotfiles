# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Support for mocking Google Compute Engine API method calls."""

import base64
import collections
import json
import re
import urlparse

from gcutil_lib import gcutil_logging

LOGGER = gcutil_logging.LOGGER

Property = collections.namedtuple('Property', ('name', 'type'))
Parameter = collections.namedtuple('Parameter', ('name', 'type'))


class ValidationError(Exception):
  """Raised when request or response validation fails."""


class _ApiType(object):
  __slots__ = tuple()

  # pylint: disable=unused-argument
  def Validate(self, method, path, value):
    raise ValidationError(
        '{name} doesn\'t support validation'.format(
            name=self.__class__.__name__))

  # pylint: disable=unused-argument
  def ValidateString(self, method, path, value):
    raise ValidationError(
        '{name} doesn\'t support validation of a string value'.format(
            name=self.__class__.__name__))


class AnyType(_ApiType):
  """Represents discovery type 'any'."""
  __slots__ = tuple()

  def Validate(self, method, path, value):
    pass


class BooleanType(_ApiType):
  """Represents discovery type 'bool'."""

  __slots__ = tuple()

  def Validate(self, method, path, value):
    if not isinstance(value, bool):
      raise ValidationError(
          '{method} {path}: expected bool, but received {value}'.format(
              method=method, path=path, value=value))

  def ValidateString(self, method, path, value):
    """Validates boolean value serialized as string."""
    if value == 'true':
      boolean_value = True
    elif value == 'false':
      boolean_value = False
    else:
      raise ValidationError(
          '{method} {path}: expected string with boolean value, '
          'but received {value}'.format(method=method, path=path, value=value))

    self.Validate(method, path, boolean_value)


class StringType(_ApiType):
  """Represents discovery types in the string family."""

  __slots__ = ('_format',)

  DATE_TIME_REGEX = re.compile(
      r'^'
      r'(?P<year>\d{4})'
      r'-'
      r'(?P<month>\d{2})'
      r'-'
      r'(?P<day>\d{2})'
      r'[Tt]'
      r'(?P<hour>\d{2})'
      r':'
      r'(?P<minute>\d{2})'
      r':'
      r'(?P<second>\d{2})'
      r'(\.(?P<fraction>\d+))?'
      r'[Zz]'
      r'$')

  DATE_REGEX = re.compile(
      r'^'
      r'(?P<year>\d{4})'
      r'-'
      r'(?P<month>\d{2})'
      r'-'
      r'(?P<day>\d{2})'
      r'$')

  MIN_UINT64 = 0
  MAX_UINT64 = 2 ** 64 - 1

  MIN_INT64 = -(2 ** 63)
  MAX_INT64 = 2 ** 63 - 1

  def __init__(self, value_format):
    self._format = value_format

  def _ValidateByte(self, method, path, value):
    """Validates base64url encoded string."""
    try:
      if type(value) is unicode:
        base64.urlsafe_b64decode(value.encode('ascii'))
      else:
        base64.urlsafe_b64decode(value)
    except TypeError:
      raise ValidationError(
          '{method} {path}: expected base64url but received {value}'.format(
              method=method, path=path, value=value))

  def _ValidateDate(self, method, path, value):
    """Validates an RFC3339 date."""
    if not self.DATE_REGEX.match(value):
      raise ValidationError(
          '{method} {path}: expected RFC3339 date, but received {value}'.format(
              method=method, path=path, value=value))

  def _ValidateDateTime(self, method, path, value):
    """Validates RFC3339 timestamp."""
    if not self.DATE_TIME_REGEX.match(value):
      raise ValidationError(
          '{method} {path}: expected RFC3339 date, but received {value}'.format(
              method=method, path=path, value=value))

  def _ValidateInt64(self, method, path, value):
    """Validates an int64 value MIN_INT64 <= value <= MAX_INT64."""
    try:
      long_value = long(value)
    except ValueError:
      raise ValidationError(
          '{method} {path}: expected int64 but received {value}'.format(
              method=method, path=path, value=value))
    if not self.MIN_INT64 <= long_value <= self.MAX_INT64:
      raise ValidationError(
          '{method} {path}: int64 value {value} not in range '
          'MIN_INT64..MAX_INT64'.format(
              method=method, path=path, value=value))

  def _ValidateUInt64(self, method, path, value):
    """Validates an uint64 value 0 <= value <= MAX_INT64."""
    try:
      long_value = long(value)
    except ValueError:
      raise ValidationError(
          '{method} {path}: expected int64 but received {value}'.format(
              method=method, path=path, value=value))

    if not self.MIN_UINT64 <= long_value <= self.MAX_UINT64:
      raise ValidationError(
          '{method} {path}: int64 value {value} not in range '
          'MIN_INT64..MAX_INT64'.format(
              method=method, path=path, value=value))

  def Validate(self, method, path, value):
    if not isinstance(value, basestring):
      raise ValidationError(
          '{method} {path}: expected string, but received {value}'.format(
              method=method, path=path, value=value))

    if self._format == 'byte':
      self._ValidateByte(method, path, value)
    elif self._format == 'date':
      self._ValidateDate(method, path, value)
    elif self._format == 'date-time':
      self._ValidateDateTime(method, path, value)
    elif self._format == 'int64':
      self._ValidateInt64(method, path, value)
    elif self._format == 'uint64':
      self._ValidateUInt64(method, path, value)

  def ValidateString(self, method, path, value):
    self.Validate(method, path, value)


class IntegerType(_ApiType):
  """Represents an integer type in the API type system."""
  __slots__ = ('_format',)

  def __init__(self, value_format):
    self._format = value_format

  def Validate(self, method, path, value):
    if not isinstance(value, (int, long)):
      raise ValidationError(
          '{method} {path}: expected int32, but received {value}'.format(
              method=method, path=path, value=value))

    if self._format == 'uint32':
      if not 0 <= value <= 4294967295:
        raise ValidationError(
            '{method} {path}: value {value} not in the uint32 range '
            '0 .. 4294967295'.format(method=method, path=path, value=value))
    elif not -2147483648 <= value <= 2147483647:
      raise ValidationError(
          '{method} {path}: value {value} not in the int32 range '
          '-2147483648 .. 2147483647'.format(
              method=method, path=path, value=value))

  def ValidateString(self, method, path, value):
    try:
      integer_value = long(value)
    except ValueError:
      raise ValidationError(
          '{method} {path}: value {value} not an integer'.format(
              method=method, path=path, value=value))
    self.Validate(method, path, integer_value)


class NumberType(_ApiType):
  """Represents a floating point number in the API type system."""
  __slots__ = ('_format',)

  def __init__(self, value_format):
    self._format = value_format

  def Validate(self, method, path, value):
    if not isinstance(value, (int, long, float)):
      raise ValidationError(
          '{method} {path}: expected number but received {value}'.format(
              method=method, path=path, value=value))

  def ValidateString(self, method, path, value):
    try:
      float_value = float(value)
    except ValueError:
      raise ValidationError(
          '{method} {path}: expected number but received {value}'.format(
              method=method, path=path, value=value))
    self.Validate(method, path, float_value)


class ArrayType(_ApiType):
  __slots__ = ('_element',)

  def __init__(self, element):
    self._element = element

  def Validate(self, method, path, value):
    if not isinstance(value, (list, tuple)):
      raise ValidationError(
          '{method} {path}: expected array but received {value}'.format(
              method=method, path=path, value=value))

    for index, element in enumerate(value):
      self._element.Validate(method,
                             '{path}[{index}]'.format(path=path, index=index),
                             element)


class ObjectType(_ApiType):
  """Represents an API object tyoe."""

  __slots__ = ('_name', '_properties', '_additional')

  def __init__(self):
    self._name = None
    self._properties = None
    self._additional = None

  def __str__(self):
    return '<{name} {properties}>'.format(
        name=self._name, properties=sorted(self._properties))

  def Define(self, name, properties, additional):
    self._name = name
    self._properties = dict((object_property.name, object_property)
                            for object_property in properties or [])
    self._additional = additional

  def Validate(self, method, path, value):
    if not isinstance(value, dict):
      raise ValidationError(
          '{method} {path}: expected dict but received {value}'.format(
              method=method, path=path, value=value))

    for property_name, property_value in value.iteritems():
      named_property = self._properties.get(property_name)
      if named_property is None:
        if not self._additional:
          raise ValidationError(
              '{method} {path}: Unexpected property {name} in {value}.'.format(
                  method=method, path=path, name=property_name, value=value))
        self._additional.Validate(
            method,
            '{path}[{name}]'.format(path=path, name=property_name),
            property_value)
      else:
        named_property.type.Validate(
            method,
            '{path}.{name}'.format(path=path, name=property_name),
            property_value)


class Method(object):
  """Represents an API resource collection method."""

  __slots__ = ('_id', '_name', '_path', '_parameters', '_request', '_response')

  PARAMETER_RE = re.compile('^{(\\w+)}$')

  def __init__(self, method_id, name, path, parameters, request, response):
    self._id = method_id
    self._name = name
    self._path = path
    self._parameters = parameters
    self._request = request
    self._response = response

  @staticmethod
  def _TryStringToJson(string):
    try:
      return json.loads(string)
    # pylint: disable=bare-except
    except:
      return string

  def _ValidateParameters(self, uri):
    parsed_uri = urlparse.urlsplit(uri)
    parsed_path = urlparse.urlsplit(self._path)

    if parsed_uri.scheme != parsed_path.scheme:
      raise ValidationError(
          'Incompatible URL schemes: {value} / {template}'.format(
              value=parsed_uri.scheme, template=parsed_path.scheme))
    if parsed_uri.netloc != parsed_path.netloc:
      raise ValidationError(
          'Incompatible URL netlocs: {value} / {template}'.format(
              value=parsed_uri.netloc, template=parsed_path.netloc))

    # Validate the path contents
    split_url_path = parsed_uri.path.split('/')
    split_template = parsed_path.path.split('/')

    if len(split_url_path) != len(split_template):
      raise ValidationError(
          'URI path length doesn\'t match template {value} / {template}'.format(
              value=parsed_uri.path, template=parsed_path.path))

    parameter_values = {}
    for template, value in zip(split_template, split_url_path):
      parameter_match = self.PARAMETER_RE.match(template)
      if parameter_match:
        name = parameter_match.group(1)
        self._ValidateParameter(name, value, uri)
        parameter_values[name] = value
      elif template != value:
        raise ValidationError(
            'URL path element mismatch {value} / {template} '
            '({value_uri} / {template_uri})'.format(
                value=value, template=template,
                value_uri=parsed_uri.path, template_uri=parsed_path.path))

    for name, values in urlparse.parse_qs(parsed_uri.query).iteritems():
      if len(values) != 1:
        raise ValidationError(
            'Invalid count of query parameter values: {name} ({values})'.format(
                name=name, values=values))
      value = values[0]
      self._ValidateParameter(name, value, uri)
      parameter_values[name] = value
    return parameter_values

  def _ValidateParameter(self, name, value, uri):
    parameter = self._parameters.get(name)
    if parameter is None:
      raise ValidationError('Unknown parameter found {name} ({uri})'.format(
          name=name, uri=uri))
    parameter.type.ValidateString(self._id, name, value)

  def _ValidateBody(self, message, body_type, body_value):
    if body_type is None:
      if body_value is not None:
        raise ValidationError(
            'Expected no {message} body but received one.'.format(
                message=message),
            self._id, body_value)
    else:
      if (isinstance(body_type, ObjectType) and
          isinstance(body_value, basestring)):
        body_value = self._TryStringToJson(body_value)
      body_type.Validate(self._id, '<{message}>'.format(message=message),
                         body_value)

  def ValidateRequest(self, uri, body):
    LOGGER.debug('Validating request %s %s.\n', uri, body)
    parameter_values = self._ValidateParameters(uri)
    self._ValidateBody('request', self._request, body)
    return parameter_values

  def ValidateResponse(self, body):
    LOGGER.debug('Validating response %s.\n', body)
    self._ValidateBody('response', self._response, body)
