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


"""Parsing API Discovery document."""

import mock_api_types

from gcutil_lib import mock_api_types


class Parser(object):
  """Discovery document parser.

  Parses discovery document types, resources and methods. Result of parsing is a
  dictionary method_id -> method.
  """

  __slots__ = ('_discovery_document', '_parsed_schemas', '_parsed_methods',
               '_base_url', '_common_parameters')

  def __init__(self, doc):
    self._discovery_document = doc
    self._parsed_schemas = {}
    self._parsed_methods = {}
    self._base_url = ''
    self._common_parameters = {}

  def _ParseType(self, discovery_type):
    ref = discovery_type.get('$ref')
    if ref:
      return self._GetSchema(ref)

    type_name = discovery_type['type']
    if type_name == 'any':
      return mock_api_types.AnyType()
    elif type_name == 'array':
      return mock_api_types.ArrayType(self._ParseType(discovery_type['items']))
    elif type_name == 'boolean':
      return mock_api_types.BooleanType()
    elif type_name == 'integer':
      return self._ParseIntegerType(discovery_type)
    elif type_name == 'number':
      return self._ParseNumberType(discovery_type)
    elif type_name == 'object':
      return self._ParseObjectType(discovery_type)
    elif type_name == 'string':
      return self._ParseStringType(discovery_type)
    else:
      raise ValueError('Unrecognized type {type}'.format(type=type_name))

  def _ParseIntegerType(self, discovery_type):
    value_format = discovery_type.get('format')
    if value_format in (None, 'int32', 'uint32'):
      return mock_api_types.IntegerType(value_format or 'int32')
    raise ValueError('Invalid integer format {value}'.format(
        value=value_format))

  def _ParseNumberType(self, discovery_type):
    value_format = discovery_type.get('format')
    if value_format in (None, 'double', 'float'):
      return mock_api_types.NumberType(value_format or 'double')
    raise ValueError('Invalid number format {value}'.format(
        value=value_format))

  def _ParseStringType(self, discovery_type):
    value_format = discovery_type.get('format')
    if value_format in (None, 'byte', 'date', 'date-time', 'int64', 'uint64'):
      return mock_api_types.StringType(value_format)
    raise ValueError('Invalid string format {value}'.format(
        value=value_format))

  def _ParseObjectType(self, discovery_type):
    properties, additional = self._ParseProperties(discovery_type)
    object_type = mock_api_types.ObjectType()
    object_type.Define('', properties, additional)
    return object_type

  def _ParseSchema(self, discovery_schema):
    properties, additional = self._ParseProperties(discovery_schema)
    return self._CreateSchema(
        discovery_schema.get('id'), properties, additional)

  def _ParseProperties(self, discovery_object_type):
    """Parses properties of a discovery document object tyoe."""
    assert discovery_object_type.get('type') == 'object'

    properties = []
    for property_name, property_type in (
        discovery_object_type.get('properties', {}).iteritems()):
      properties.append(mock_api_types.Property(
          property_name, self._ParseType(property_type)))

    additional = None
    additional_properties = discovery_object_type.get('additionalProperties')
    if additional_properties is not None:
      additional = self._ParseType(additional_properties)
    return properties, additional

  def _ParseSchemas(self, discovery_schemas):
    for _, discovery_schema in discovery_schemas.iteritems():
      self._ParseSchema(discovery_schema)

  def _ParseMethods(self, discovery_methods):
    for method_name, discovery_method in discovery_methods.iteritems():
      self._ParseMethod(method_name, discovery_method)

  def _ParseParameter(self, parameter_name, parameter_type):
    return mock_api_types.Parameter(
        parameter_name, self._ParseType(parameter_type))

  def _ParseParameters(self, discovery_method_parameters):
    parameters = []
    for parameter_name, parameter_type in (
        discovery_method_parameters.iteritems()):
      parameters.append(
          self._ParseParameter(parameter_name, parameter_type))
    parameters.sort(key=lambda parameter: parameter.name)
    return parameters

  def _ParseMethod(self, method_name, discovery_method):
    parameters = self._ParseParameters(discovery_method.get('parameters', {}))

    # Parse request type
    discovery_method_request = discovery_method.get('request')
    if discovery_method_request is None:
      request_type = None
    else:
      request_type = self._ParseType(discovery_method_request)

    # Parse response type.
    discovery_method_response = discovery_method.get('response')
    if discovery_method_response is None:
      response_type = None
    else:
      response_type = self._ParseType(discovery_method_response)

    return self._CreateMethod(
        discovery_method.get('id'), method_name,
        discovery_method.get('path', ''), parameters,
        request_type, response_type)

  def _ParseResources(self, discovery_resources):
    for _, discovery_resource in discovery_resources.iteritems():
      self._ParseResource(discovery_resource)
    # Return all accumulated methods.
    return self._parsed_methods

  def _ParseResource(self, discovery_resource):
    discovery_methods = discovery_resource.get('methods')
    if discovery_methods:
      self._ParseMethods(discovery_methods)
    discovery_resources = discovery_resource.get('resources')
    if discovery_resources:
      self._ParseResources(discovery_resources)

  def _ParseGlobals(self, discovery_document):
    self._base_url = discovery_document.get('baseUrl')
    self._common_parameters = self._ParseParameters(
        discovery_document.get('parameters', {}))

  def Parse(self):
    self._ParseGlobals(self._discovery_document)
    self._ParseSchemas(self._discovery_document.get('schemas'))
    return self._ParseResources(self._discovery_document.get('resources'))

  def _GetSchema(self, name):
    schema = self._parsed_schemas.get(name)
    if schema is None:
      self._parsed_schemas[name] = schema = mock_api_types.ObjectType()
    return schema

  def _CreateSchema(self, name, properties, additional):
    schema = self._GetSchema(name)
    schema.Define(name, properties, additional)
    return schema

  def _CreateMethod(self, method_id, name, path, parameters, request, response):
    if method_id in self._parsed_methods:
      raise ValueError('Duplicate method {method}'.format(method=method_id))

    all_parameters = dict((p.name, p) for p in self._common_parameters)
    all_parameters.update(dict((p.name, p) for p in parameters))

    path = self._base_url + path
    method = mock_api_types.Method(
        method_id, name, path, all_parameters, request, response)
    self._parsed_methods[method_id] = method
    return method
