#!/usr/bin/python

import httplib
import sys

sys.path.append('../python-lib')

from api import *
from codegen_core import *
from optparse import OptionParser
from serializers import get_serializer, get_function_name
from urlparse import urlparse

__author__ = 'hiranya'

CLASSES = []
CLASS_NAMES = []
CLASS_NAME_MAPPINGS = {}
STATIC_METHODS = []

CONTENT_TYPES = {
  'application/json' : 'json',
  'application/x-www-form-urlencoded' : 'form',
  '_ANY_' : '_any_'
}

def define_class_name(string):
  """
  Define a valid Python class name for the specified type name. This method
  ensures that the generated class name is a valid Python identifier and is
  not already allocated for a different class. This method computes the
  Python class name from the given type name by, replacing all the invalid characters
  with empty string. If this results in an empty class name, it reverts back to
  a generic class name prefixed by 'DataType'.  If a class name derived by this
  technique is already allocated, then this method would append a numeric value
  to the end of the class name to make it unique.

  Some example type name to class name mappings are given below:
    Foo --> Foo
    BarType --> BarType
    bar --> Bar
    bar type --> Bartype
    1FooType --> FooType
    12345 --> DataType

  Args:
    string Name of the type for which a Python class name is required

  Returns:
    A valid Python class name identifier
  """
  temp_name = ''.join([i for i in string if i.isalnum() or i == '_'])
  if not temp_name:
    # All the characters in the original string got replaced by '' and we
    # are left with an empty class name.
    # '' -> 'DataType'
    temp_name = 'DataType'
  elif temp_name[0].isdigit():
    # Replacing invalid characters in the original string left us with a numeric
    # value, which is not a valid Python class name
    # '12345' -> 'DataType12345'
    temp_name = 'DataType' + temp_name

  class_name = temp_name[0].upper() + temp_name[1:]
  counter = 0
  while True:
    if class_name in CLASS_NAMES:
      # Name already allocated. Try randomizing it by adding an integer
      # to the end.
      if counter > 0:
        class_name = class_name[:-1*len(str(counter))]
      counter += 1
      class_name += str(counter)
      continue
    else:
      # We have found a valid Python class name.
      CLASS_NAMES.append(class_name)
      CLASS_NAME_MAPPINGS[string] = class_name
      return class_name

def define_method_name(clazz, string):
  """
  Define a valid Python method name for the given <class name, operation name>
  pair. This method ensures that the generated method name is a valid Python
  method name and is not already assigned to a method in the same class.

  Args:
    clazz Name of the class to which the method belongs
    string  Name of the operation for which a method is being generated

  Returns:
    Name of the method
  """
  temp_name = ''.join([i for i in string if i.isalnum() or i == '_'])
  if not temp_name:
    temp_name = 'method'
  elif temp_name[0].isdigit():
    temp_name = 'method_' + temp_name
  method_name = temp_name[0].lower() + temp_name[1:]
  counter = 0
  while True:
    if clazz.has_method(method_name):
      if counter > 0:
        method_name = method_name[:-1*len(str(counter))]
      counter += 1
      method_name += str(counter)
      continue
    else:
      return method_name

def define_static_method_name(string):
  """
  Define a valid Python static method name for the operation name . This method
  ensures that the generated method name is a valid Python method name and is
  not already assigned to any other static method.

  Args:
    string  Name of the operation for which a method is being generated

  Returns:
    Name of the static method
  """
  temp_name = ''.join([i for i in string if i.isalnum() or i == '_'])
  if not temp_name:
    temp_name = 'method'
  elif temp_name[0].isdigit():
    temp_name = 'method_' + temp_name
  method_name = temp_name[0].lower() + temp_name[1:]
  for sm in STATIC_METHODS:
    if sm.name == method_name:
      return None
  return method_name

def define_argument_name(method, string):
  """
  Define a valid Python argument name for the given <method name, param name>
  pair. This method ensures that the generated argument name is a valid Python
  argument name and is not already assigned to an argument in the same method.

  Args:
    method Name of the class to which the argument belongs
    string  Name of the parameter for which an argument is being generated

  Returns:
    Name of the argument
  """
  temp_name = ''.join([i for i in string if i.isalnum() or i == '_'])
  if not temp_name:
    temp_name = 'param'
  elif temp_name[0].isdigit():
    temp_name = 'param_' + temp_name
  param_name = temp_name[0].lower() + temp_name[1:]
  counter = 0
  while True:
    if method.has_argument(param_name):
      if counter > 0:
        param_name = param_name[:-1*len(str(counter))]
      counter += 1
      param_name += str(counter)
      continue
    else:
      return param_name

def generate_imports():
  """
  Generate code for the required Python imports.

  Returns:
    A formatted string containing a set of Python module import statements.
  """
  pcg = PythonCodeGenerator()
  pcg.begin(tab='  ')
  pcg.writeln('from api import *')
  pcg.writeln('from urlparse import urlparse')
  pcg.writeln('import httplib')
  pcg.writeln('import json')
  pcg.writeln('import urllib')
  return pcg.end()

def generate_epr_definitions(base_urls):
  """
  Generate code segments with API endpoint (URL) definitions

  Args:
    base_urls List of base URLs of the API

  Returns:
    A string containing Python code for the endpoint definitions
  """
  pcg = PythonCodeGenerator()
  pcg.begin(tab='  ')
  pcg.writeln('BASE_URL = [')
  pcg.indent()
  for base in base_urls:
    pcg.writeln('\'' + base + '\',')
  pcg.dedent()
  pcg.writeln(']')
  return pcg.end()

def generate_exception_definitions():
  """
  Generate the exception class definition.

  Returns:
    A Class object containing the auto-generated RemoteException type.
  """
  clazz = Class(define_class_name('RemoteException'), 'Exception')
  constructor = Method('__init__')
  constructor.arguments.append(MethodArgument('status'))
  constructor.arguments.append(MethodArgument('cause'))
  constructor.arguments.append(MethodArgument('details'))
  constructor.add_line('Exception.__init__(self, cause)')
  constructor.add_line('self.status = status')
  constructor.add_line('self.details = details')
  clazz.methods.append(constructor)
  return clazz

def generate_parent_resource():
  """
  Generate the AbstractResourceClient class definition. All the resource
  clients generated by this code generator extends AbstractResourceClient.
  This auto-generated abstract class contains all the basic methods for
  making HTTP connections, processing output and handling debug information.

  Returns:
    A Class object containing the auto-generated AbstractResourceClient type.
  """
  class_name = define_class_name('AbstractResourceClient')
  clazz = Class(class_name)

  # Create the constructor definition
  constructor = Method('__init__')
  constructor.arguments.append(MethodArgument('endpoint'))
  constructor.arguments.append(MethodArgument('debug'))
  constructor.add_line('if endpoint is not None:')
  constructor.indent()
  constructor.add_line('self.endpoint = endpoint')
  constructor.dedent()
  constructor.add_line('else:')
  constructor.indent()
  constructor.add_line('self.endpoint = BASE_URL[0]')
  constructor.dedent()
  constructor.add_line('self.debug = debug')
  clazz.methods.append(constructor)

  # get_connection method - Open a HTTP connection to the API
  get_connection = Method(define_method_name(clazz, 'get_connection'))
  get_connection.doc_enabled = False
  get_connection.add_line('result = urlparse(self.endpoint)')
  get_connection.add_line('ssl = result.scheme == \'https\'')
  get_connection.add_line('if ssl:')
  get_connection.indent()
  get_connection.add_line('conn = httplib.HTTPSConnection(result.netloc)')
  get_connection.dedent()
  get_connection.add_line('else:')
  get_connection.indent()
  get_connection.add_line('conn = httplib.HTTPConnection(result.netloc)')
  get_connection.dedent()
  get_connection.add_line('if self.debug:')
  get_connection.indent()
  get_connection.add_line('conn.set_debuglevel(1)')
  get_connection.dedent()
  get_connection.add_line('return conn')
  clazz.methods.append(get_connection)

  # get_path method - Process API endpoint information and return a suitable URL
  get_path = Method(define_method_name(clazz, 'get_path'))
  get_path.doc_enabled = False
  get_path.add_line('result = urlparse(BASE_URL[0])')
  get_path.add_line('return result.path')
  clazz.methods.append(get_path)

  # get_output method - Process HTTP invocation output return payload
  get_output = Method(define_method_name(clazz, 'get_output'))
  get_output.doc_enabled = False
  get_output.arguments.append(MethodArgument(
    define_argument_name(get_output, 'response')))
  get_output.arguments.append(MethodArgument(
    define_argument_name(get_output, 'expected')))
  get_output.arguments.append(MethodArgument(
    define_argument_name(get_output, 'errors')))
  get_output.add_line('status = response.status')
  get_output.add_line('payload = response.read()')
  get_output.add_line('if not errors and errors.has_key(status):')
  get_output.indent()
  get_output.add_line('raise RemoteException(status, errors[status], payload)')
  get_output.dedent()
  get_output.add_line('elif status != expected:')
  get_output.indent()
  get_output.add_line('raise RemoteException(status, \'Unexpected return '
                      'status: \' + str(status), payload)')
  get_output.dedent()
  get_output.add_line('return payload')
  clazz.methods.append(get_output)

  return clazz

def create_named_type(name, data_type):
  """
  Create a temporary NamedTypeDef instance for the given data_type. This is
  used to handle certain anonymous data types as named types for code generation
  purposes.

  Args:
    name Name of the type to be generated
    data_type An existing (anonymous) TypeDef instance

  Returns:
    A NamedTypeDef with the specified name and all the fields of the
    input data_type
  """
  named_type = NamedTypeDef(name=name, fields=[])
  named_type.fields = data_type.fields
  return named_type

def generate_data_types(data_type):
  """
  Generate a Python class for the specified data type. If the input data type
  makes references to any other complex data types, this method will recursively
  generate Python classes for such referred types too. All the generated
  classes are appended to the CLASSES global.

  Args:
    data_type A NamedTypeDef instance
  """
  class_name = define_class_name(data_type.name)
  clazz = Class(class_name)
  constructor = Method('__init__')
  for field in data_type.fields:
    arg_name = define_argument_name(constructor, field.name)
    arg = MethodArgument(arg_name)
    if field.optional:
      arg.default = 'None'
    constructor.arguments.append(arg)
    constructor.define_mapping(field.name, arg_name)
    constructor.add_line('self.' + arg.name + ' = ' + arg.name)
    field_type = field.type.type
    if isinstance(field_type, TypeDef):
      named_type = create_named_type(class_name + '_' + field.name, field_type)
      generate_data_types(named_type)
  clazz.methods.append(constructor)
  CLASSES.append(clazz)

def define_resource_operation(api, resource, operation, clazz):
  """
  Generate a Python method for the given API resource operation. The method
  will be generated as a class method of some given class. Note that this
  method does not really add the generated method to the class definition.
  That should be handled separately by the caller.

  Args:
    api An API object
    resource  Current resource
    operation The operation for which a Python method will be generated
    clazz The Python class to which the method will be added

  Returns:
    A Method object
  """
  method = Method(define_method_name(clazz, operation.name))
  if operation.input:
    input_params = operation.input.params
    for param in input_params:
      if param.binding:
        for binding in resource.input_bindings:
          if binding.id == param.binding:
            arg_name = define_argument_name(method, binding.name)
            arg = MethodArgument(arg_name)
            arg.data_type = binding.type.type.get_reference_name()
            method.arguments.append(arg)
            method.define_mapping(binding.name, arg_name)
            if param.optional:
              arg.default = 'None'
            break
      else:
        arg_name = define_argument_name(method, param.name)
        arg = MethodArgument(arg_name)
        arg.data_type = param.type.type.get_reference_name()
        if param.optional:
          arg.default = 'None'
        method.arguments.append(arg)
        method.define_mapping(param.name, arg_name)

    if operation.input.type:
      input_type = operation.input.type.type
      if isinstance(input_type, TypeDef):
        type_name = resource.name + '_' + operation.name + '_InputType'
        named_type = create_named_type(type_name, input_type)
        generate_data_types(named_type)
        generate_serializers(api, named_type, operation.input.contentType)
        param_name = 'request'
        type_desc = 'An instance of the ' + type_name + ' class'
      elif isinstance(input_type, ContainerTypeRef):
        param_name = input_type.type.get_reference_name() + '_' + input_type.container
        type_desc = 'A ' + input_type.container + ' of ' + input_type.get_reference_name() + ' objects'
      else:
        param_name = input_type.get_reference_name()
        type_name = input_type.get_reference_name()
        data_type = api.get_type_by_name(type_name)
        generate_serializers(api, data_type, operation.input.contentType)
        type_desc = 'An instance of the ' + type_name + ' class'
      arg_name = define_argument_name(method, param_name)
      arg = MethodArgument(arg_name)
      arg.data_type = type_desc
      method.arguments.append(arg)
      method.define_mapping(param_name, arg_name)
  if operation.description:
    method.doc = operation.description
  return method

def select_media_type(content_types, preference=None):
  if preference is not None:
    for content_type in content_types:
      if find_media_type(content_type) == preference:
        return preference
  return find_media_type(content_types[0])

def find_media_type(content_type):
  if CONTENT_TYPES.has_key(content_type):
    return CONTENT_TYPES[content_type]
  else:
    string = content_type[content_type.rindex('/') + 1:]
    temp_name = ''.join([i for i in string if i.isalnum() or i == '_'])
    return temp_name

def resolve_uri_templates(request_path, resource, operation, method):
  if '{' in request_path:
    params = operation.input.params
    for param in params:
      if param.binding:
        for binding in resource.input_bindings:
          if binding.id == param.binding:
            param_name = method.get_mapping(binding.name)
            request_path = request_path.replace('{' + binding.name + '}',
              '\' + str(' + param_name + ') + \'')
      else:
        param_name = method.get_mapping(param.name)
        request_path = request_path.replace('{' + param.name + '}',
          '\' + str(' + param_name + ') + \'')
  request_path = '\'' + request_path + '\''
  return request_path.replace('+ \'\'', '')

def get_class_parameter(data_type, key):
  class_name = CLASS_NAME_MAPPINGS[data_type]
  for clazz in CLASSES:
    if clazz.name == class_name:
      constructor = clazz.get_constructor()
      return constructor.get_mapping(key)
  return None

def generate_serializers(api, data_type, content_types):
  for content_type in content_types:
    media_type = find_media_type(content_type)
    serializer = get_serializer(media_type, CLASSES, CLASS_NAME_MAPPINGS)
    serializer_functions = serializer.generate_serializers(data_type, api)
    for sf in serializer_functions:
      if define_static_method_name(sf.name) is not None:
        STATIC_METHODS.append(sf)

def generate_deserializers(api, data_type, content_types):
  for content_type in content_types:
    media_type = find_media_type(content_type)
    serializer = get_serializer(media_type, CLASSES, CLASS_NAME_MAPPINGS)
    serializer_functions = serializer.generate_deserializers(data_type, api)
    for sf in serializer_functions:
      if define_static_method_name(sf.name) is not None:
        STATIC_METHODS.append(sf)

def has_query_params(resource, operation):
  if operation.input:
    params = operation.input.params
    for param in params:
      if param.binding:
        for binding in resource.input_bindings:
          if binding.id == param.binding and binding.mode == 'query':
            return True
      elif param.mode == 'query':
        return True
  return False

def handle_query_params(method, resource, operation):
  method.add_line('query = \'\'')
  if has_query_params(resource, operation):
    method.add_line('query_data = dict()')
    params = operation.input.params
    for param in params:
      if param.binding:
        for binding in resource.input_bindings:
          if binding.id == param.binding and binding.mode == 'query':
            param_name = method.get_mapping(binding.name)
            if binding.type.type.get_reference_name() == 'boolean':
              method.add_line('if ' + param_name + ' is not None:')
              method.indent()
              method.add_line('query_data[\'' + binding.name + '\'] = str(bool(' + param_name + ')).lower()')
              method.dedent()
            else:
              method.add_line('if ' + param_name + ':')
              method.indent()
              method.add_line('query_data[\'' + binding.name + '\'] = str(' + param_name + ')')
              method.dedent()
      elif param.mode == 'query':
        param_name = method.get_mapping(param.name)
        if param.type.type.get_reference_name() == 'boolean':
          method.add_line('if ' + param_name + ' is not None:')
          method.indent()
          method.add_line('query_data[\'' + param.name + '\'] = str(bool(' + param_name + ')).lower()')
          method.dedent()
        else:
          method.add_line('if ' + param_name + ':')
          method.indent()
          method.add_line('query_data[\'' + param.name + '\'] = str(' + param_name + ')')
          method.dedent()
    method.add_line('if query_data:')
    method.indent()
    method.add_line('query = \'?\' + urllib.urlencode(query_data)')
    method.dedent()

def generate_method_output(operation, method, output_preference):
  output_type = operation.output.type
  if output_type is None:
    return

  content_types = operation.output.contentType
  if isinstance(output_type.type, TypeDef):
    temp_name = resource.name + '_' + operation.name + '_OutputType'
    data_type = create_named_type(temp_name, output_type.type)
    generate_data_types(data_type)
    method.return_type = 'An instance of the ' + data_type.name + ' class'
  else:
    data_type = api.get_type_by_name(output_type.type.get_reference_name())
    if isinstance(output_type.type, ContainerTypeRef):
      method.return_type = 'A ' + output_type.type.container + ' of ' +\
                           output_type.type.type.get_reference_name() + ' objects'
    elif data_type.name == '_API_':
      method.return_type = 'An instance of the API class'
    else:
      method.return_type = 'An instance of the ' + data_type.name + ' class'
  generate_deserializers(api, data_type, content_types)
  media_type = select_media_type(content_types, output_preference)
  function_name = get_function_name('deserialize', data_type, media_type, api)
  deserializer_name = function_name + '(payload)'
  method.add_line('return ' + deserializer_name)

def generate_rest_invocation(operation, method, request_path):
  """
  Helper method to generate Python code for making a RESTful invocation of
  a given API operation.

  Args:
    operation The API operation being invoked
    method  Python Method that's being code generated. All the code generated
            by this method will be added to this Method object.
    request_path  Request URL path for the HTTP call
  """

  # Start by obtaining a connection
  method.add_line('conn = self.get_connection()')

  if operation.method == 'POST' or operation.method == 'PUT':
    # If the request is an entity enclosing request, we need to deal with
    # parameter/payload serialization.
    content_type = operation.input.contentType[0]
    input_type = operation.input.type.type
    if isinstance(input_type, TypeDef):
      param_name = method.get_mapping('request')
    elif isinstance(input_type, ContainerTypeRef):
      arg_name = input_type.type.get_reference_name() + '_' + input_type.container
      param_name = method.get_mapping(arg_name)
    else:
      data_type = api.get_type_by_name(input_type.get_reference_name())
      param_name = method.get_mapping(data_type.name)

    # Generate serializer methods for the selected input content type
    generate_serializers(api, input_type, operation.input.contentType)
    media_type = find_media_type(content_type)

    # Generate the code to call the serializer
    function_name = get_function_name('serialize', input_type, media_type, api)
    payload = 'payload = serialize_final_' + media_type + '(' + \
              function_name + '(' + param_name + '))'

    # Generate code to set the HTTP Content-type header
    headers = 'headers = { \'Content-type\' : \'' + content_type + '\' }'
    method.add_line(headers)
    method.add_line(payload)

    # Make the HTTP POST/PUT call
    method.add_line('conn.request(\'' + operation.method + '\', self.get_path() + ' +
                    request_path + ' + query, payload, headers)')
  else:
    # Not an entity enclosing request - Simply make the URL request
    method.add_line('conn.request(\'' + operation.method + '\', self.get_path() + ' +
                    request_path + ' + query)')

  # Generate code to obtain the response
  method.add_line('response = conn.getresponse()')

  output = operation.output
  status = output.status
  errors = {}

  # Generate error handling code
  if operation.errors:
    errors = operation.errors
  method.add_line('expected_status = ' + str(status))
  method.add_line('errors = ' + str(errors))
  method.add_line('payload = self.get_output(response, expected_status, errors)')
  method.add_line('conn.close()')
  method.add_line('if self.debug:')
  method.indent()
  method.add_line('print \'payload:\', payload')
  method.dedent()

def generate_resource_client(api, resource, parent, output_preference=None):
  """
  Generate a client stub (Python class) for a given API resource.

  Args:
    api The API object to which the resource belongs
    resource  The resource for which a client should be generated
    parent  Any parent class from which the generated stub should extend
    output_preference If the resource supports multiple output content types,
                      specify this parameter to select one of the content types
                      as the preferred content type for deserialization.

  Returns:
    A Class object containing the Python stub for the given resource
  """
  clazz = Class(define_class_name(resource.name + 'Client'), super_class=parent.name)
  constructor = Method('__init__')
  endpoint = MethodArgument('endpoint')
  endpoint.default = 'None'
  debug = MethodArgument('debug')
  debug.default = 'False'
  constructor.arguments.append(endpoint)
  constructor.arguments.append(debug)
  constructor.add_line('AbstractResourceClient.__init__(self, endpoint, debug)')
  clazz.methods.append(constructor)

  for operation in resource.operations:
    method = define_resource_operation(api, resource, operation, clazz)
    handle_query_params(method, resource, operation)
    request_path = resolve_uri_templates(resource.path, resource, operation, method)
    generate_rest_invocation(operation, method, request_path)
    generate_method_output(operation, method, output_preference)
    clazz.methods.append(method)
  return clazz

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option('-f', '--file', dest='file',
    help='Path to the input API description file')
  parser.add_option('-u', '--url', dest='url',
    help='URL of the input API description')
  parser.add_option('-m', '--method', dest='method',
    help='The HTTP method that should be used to pull the input API description from the input URL (defaults to OPTIONS)')
  parser.add_option('-o', '--output', dest='output',
    help='Path to the output Python file to be generated')
  parser.add_option('-d', '--deserializer', dest='deserializer',
    help='Preferred output deserializer (used for all operations that support this content type)')

  (options, args) = parser.parse_args(sys.argv)
  if options.file:
    api = parse(options.file)
    print 'API description loaded from', options.file
  elif options.url:
    if options.method:
      method = options.method
    else:
      method = 'OPTIONS'
    result = urlparse(options.url)
    ssl = result.scheme == 'https'
    if ssl:
      conn = httplib.HTTPSConnection(result.netloc)
    else:
      if result.scheme != 'http':
        print 'Invalid protocol in the URL (must be http or https)'
        exit(1)
      conn = httplib.HTTPConnection(result.netloc)
    conn.request(method, result.path)
    response = conn.getresponse()
    json_string = json.loads(response.read())
    conn.close()
    api = API(data=json_string)
    print 'API description loaded from', options.url
  else:
    api = None
    print 'Please specify the path or the URL of the input API description file'
    exit(1)

  if not options.output:
    print 'Please specify the output file name'
    exit(1)

  output_format = None
  if options.deserializer:
    output_format = options.deserializer
    if output_format not in CONTENT_TYPES.values():
      print output_format, 'is not supported as an output format - Ignoring...'
      output_format = None

  CLASSES.append(generate_exception_definitions())
  parent_resource = generate_parent_resource()
  CLASSES.append(parent_resource)
  for data_type in api.data_types:
    generate_data_types(data_type)
  for resource in api.resources:
    CLASSES.append(generate_resource_client(api, resource, parent_resource, output_format))

  output = open(options.output, 'w')
  output.write(generate_imports())
  output.write('\n')
  output.write(generate_epr_definitions(api.base))
  output.write('\n')
  for serializer in STATIC_METHODS:
    output.write(serializer.generate_code())
    output.write('\n')
  for clazz in CLASSES:
    output.write(clazz.generate_code())
    output.write('\n')
  output.flush()
  output.close()

  print 'Client stubs generated SUCCESSFULLY'
