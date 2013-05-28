#!/usr/bin/python

import commands
from glob import glob
import httplib
import json
from optparse import OptionParser
import os
import shutil
import sys
from urlparse import urlparse
import datetime

sys.path.append('../python-lib')
from api import *

STATUS_CODES = {
  200 : 'OK',
  201 : 'Created',
  404 : 'Not Found',
  500 : 'Internal Server Error'
}

LICENSES = {
  'apache2' : 'http://www.apache.org/licenses/LICENSE-2.0.html',
  'gpl' : 'http://www.gnu.org/licenses/gpl.html'
}

ANON_TYPES = []

class StringBuilder:
  def __init__(self):
    self.string = ''

  def append_line(self, line=''):
    self.string += line + '\n'

  def append(self, line):
    self.string += line

  def to_string(self):
    return self.string

def get_curl_command(operation, resource, api):
  cmd = 'curl -v '
  if api.base[0].startswith('https://'):
    cmd += '-k '
  if operation.method != 'GET':
    if operation.method == 'POST' and operation.input.contentType[0] == 'application/x-www-form-urlencoded':
      cmd += '-d @input.txt '
    elif operation.method == 'POST' or operation.method == 'PUT':
      cmd += '-X ' + operation.method + ' '
      cmd += '-d @input.txt '
      cmd += '-H "Content-type: ' + operation.input.contentType[0] + '" '
    else:
      cmd += '-X ' + operation.method + ' '
  cmd += api.base[0]
  if resource.path != '/':
    cmd += resource.path
  return cmd

def get_sample_value(data_type, api):
  if isinstance(data_type, PrimitiveTypeRef):
    type_name = data_type.get_reference_name()
    if type_name == 'string':
      value = 'string'
    elif type_name == 'int' or type_name == 'long' or type_name == 'short':
      value = 12345
    elif type_name == 'boolean':
      value = True
    elif type_name == 'href':
      value = 'http://example.com'
    elif type_name == 'double':
      value = 12.345
    elif type_name == 'byte':
      value = ord('a')
    else:
      value = 'A1B2C3D4E5'
    return value
  elif isinstance(data_type, ContainerTypeRef):
    if isinstance(data_type.type, PrimitiveTypeRef):
      type_name = data_type.type.get_reference_name()
      if type_name == 'string':
        value1 = 'string1'
        value2 = 'string2'
        value3 = 'string3'
      elif type_name == 'int' or type_name == 'long' or type_name == 'short':
        value1 = 100001
        value2 = 200002
        value3 = 300003
      elif type_name == 'boolean':
        value1 = True
        value2 = False
        value3 = True
      elif type_name == 'href':
        value1 = 'http://example1.com'
        value2 = 'http://example2.com'
        value3 = 'http://example3.com'
      elif type_name == 'double':
        value1 = 100.001
        value2 = 200.002
        value3 = 300.003
      elif type_name == 'byte':
        value1 = ord('a')
        value2 = ord('b')
        value3 = ord('c')
      else:
        value1 = 'A1B2C3D4E5_1'
        value2 = 'A1B2C3D4E5_2'
        value3 = 'A1B2C3D4E5_3'
      return [ value1, value2, value3 ]
    else:
      value = get_sample_value(data_type.type, api)
      return [ value, value ]
  elif isinstance(data_type, TypeDef):
    sample = {}
    for field in data_type.fields:
      if not field.optional:
        key = field.name
        field_type = field.type.type
        value = get_sample_value(field_type, api)
        sample[key] = value
    return sample
  else:
    actual_type = api.get_type_by_name(data_type.name)
    sample = {}
    for field in actual_type.fields:
      if not field.optional:
        key = field.name
        field_type = field.type.type
        value = get_sample_value(field_type, api)
        sample[key] = value
    return sample

def generate_data_type_docs(data_type, api):
  builder = StringBuilder()
  builder.append_line(data_type.name)
  builder.append_line('=' * len(data_type.name))
  builder.append_line()
  if data_type.description:
    builder.append_line(data_type.description)
  builder.append_line()

  builder.append_line('Fields')
  builder.append_line('------')
  builder.append_line()
  for field in data_type.fields:
    builder.append_line(field.name)
    builder.append_line('^' * len(field.name))
    builder.append_line()
    if field.description:
      builder.append_line('      ' + field.description)
      builder.append_line()
    field_type = field.type.type
    if isinstance(field_type, TypeDef):
      temp_type = NamedTypeDef(name=data_type.name + '_' + field.name, fields=field_type.fields)
      ANON_TYPES.append(temp_type)
      builder.append_line('      **Type**: ' + generate_type_ref(temp_type))
    else:
      builder.append_line('      **Type**: ' + generate_type_ref(field_type))
    builder.append_line()
    required = '      **Required**: '
    if field.optional:
      required += 'No'
    else:
      required += 'Yes'
    builder.append_line(required)
    builder.append_line()
  builder.append_line()

  return builder.to_string()

def generate_type_ref(data_type):
  ref = ''
  if isinstance(data_type, NamedTypeDef):
    ref += ':doc:`data_type_' + data_type.name.lower() + '`'
  elif isinstance(data_type, ContainerTypeRef):
    ref += data_type.container + '(' + generate_type_ref(data_type.type) + ')'
  elif isinstance(data_type, PrimitiveTypeRef):
    ref += data_type.get_reference_name()
  else:
    if data_type.name == '_API_':
      ref += 'API Description'
    else:
      ref += ':doc:`data_type_' + data_type.get_reference_name().lower() + '`'
  return ref

def generate_resource_docs(resource, api):
  builder = StringBuilder()
  builder.append_line(resource.name)
  builder.append_line('=' * len(resource.name))
  builder.append_line()
  builder.append_line('This resource can be accessed via following URLs.')
  builder.append_line()
  for url in api.base:
    builder.append_line('   * ' + url + resource.path)
  builder.append_line()

  for operation in resource.operations:
    title = operation.name + ' (' + operation.method + ')'
    builder.append_line(title)
    builder.append_line('-' * len(title))
    builder.append_line()
    if operation.description:
      builder.append_line('   ' + operation.description)
    else:
      builder.append_line('   No description available')
    builder.append_line()

    if operation.method == 'POST' or operation.method == 'PUT':
      request_type = '   **Request Type**: '
      in_data_type = operation.input.type.type
      if isinstance(in_data_type, TypeDef):
        in_data_type = NamedTypeDef(name=resource.name + '_' + operation.name + '_InputType', fields=in_data_type.fields)
        ANON_TYPES.append(in_data_type)
      request_type += generate_type_ref(in_data_type)
      builder.append_line(request_type)
      builder.append_line()

      builder.append_line('   **Supported Request Media Types**: ')
      for content_type in operation.input.contentType:
        builder.append_line('      * ' + content_type)
      builder.append_line()

      if 'application/json' in operation.input.contentType:
        builder.append_line('   **Sample Request**:: ')
        builder.append_line()
        sample = get_sample_value(in_data_type, api)
        json_string = json.dumps(sample, indent=4, separators=(',', ': '))
        lines = json_string.splitlines()
        for line in lines:
          builder.append_line('      ' + line)
        builder.append_line()

    return_type = '   **Response Type**: '
    out_data_type = operation.output.type.type
    if isinstance(out_data_type, TypeDef):
      out_data_type = NamedTypeDef(name=resource.name + '_' + operation.name + '_OutputType', fields=out_data_type.fields)
      ANON_TYPES.append(out_data_type)
    return_type += generate_type_ref(out_data_type)
    builder.append_line(return_type)
    builder.append_line()

    builder.append_line('   **Supported Response Media Types**: ')
    for content_type in operation.output.contentType:
      builder.append_line('      * ' + content_type)
    builder.append_line()

    if 'application/json' in operation.output.contentType:
      if isinstance(out_data_type, CustomTypeRef) and out_data_type.get_reference_name() == '_API_':
        pass
      elif not isinstance(out_data_type, PrimitiveTypeRef):
        builder.append_line('   **Sample Response**:: ')
        builder.append_line()
        sample = get_sample_value(out_data_type, api)
        json_string = json.dumps(sample, indent=4, separators=(',', ': '))
        lines = json_string.splitlines()
        for line in lines:
          builder.append_line('      ' + line)
        builder.append_line()

    status = '   **Return HTTP Status**: ' + str(operation.output.status)
    if STATUS_CODES.has_key(operation.output.status):
      status += ' ' + STATUS_CODES[operation.output.status]
    builder.append_line(status)
    builder.append_line()

    if operation.errors:
      builder.append_line('   **Errors**:')
      for status, cause in operation.errors.items():
        error = '      * ' + str(status)
        if STATUS_CODES.has_key(status):
          error += ' ' + STATUS_CODES[status]
        builder.append_line(error + ' - ' + cause)
      builder.append_line()

    builder.append_line('   **Example Curl Command**::')
    builder.append_line()
    builder.append_line('      ' + get_curl_command(operation, resource, api))
    builder.append_line()
  return builder.to_string()

def generate_index(api, api_info):
  builder = StringBuilder()
  heading = 'Welcome to the Documentation of {0}'.format(api_info['project_name'])
  builder.append_line(heading)
  builder.append_line('=' * len(heading))
  builder.append_line()
  if api.description:
    builder.append_line('Description')
    builder.append_line('-----------')
    builder.append_line()
    builder.append_line(api.description)
    builder.append_line()

  builder.append_line('Available Operations')
  builder.append_line('--------------------')
  builder.append_line()
  builder.append_line('.. toctree::')
  builder.append_line('   :maxdepth: 2')
  builder.append_line()
  for resource in api.resources:
    builder.append_line('   ' + resource.name.lower())
  builder.append_line()

  if api.data_types:
    builder.append_line('Data Models')
    builder.append_line('-----------')
    builder.append_line()
    builder.append_line('.. toctree::')
    builder.append_line('   :maxdepth: 1')
    builder.append_line()
    for data_type in api.data_types:
      builder.append_line('   data_type_' + data_type.name.lower())
    builder.append_line()

  builder.append_line('Endpoints')
  builder.append_line('---------')
  builder.append_line()
  builder.append_line('This API can be accessed via following URLs.')
  builder.append_line()
  for url in api.base:
    builder.append_line('   * ' + url)
  builder.append_line()

  if api.license:
    builder.append_line('License')
    builder.append_line('-------')
    builder.append_line()
    if LICENSES.has_key(api.license):
      builder.append_line('This API is made available under the `' +
                          api.license + ' <' + LICENSES[api.license] + '>`_ license.')
    else:
      builder.append_line('This API is made available under the ' + api.license + ' license')
    builder.append_line()

  return builder.to_string()

def get_api_info(api):
  project_name = api.name
  if not project_name.endswith('API') and not project_name.endswith('api'):
    project_name += ' API'

  year = str(datetime.datetime.now().year)
  authors = ''
  for owner in api.ownership:
    if authors:
      authors += ', '
    authors += owner.name

  version = '0.0'
  if api.version:
    version = api.version.id

  file_name = api.name.replace(' ', '_').lower()

  return {
    'project_name' : project_name,
    'year' : year,
    'authors' : authors,
    'version' : version,
    'file_name' : file_name
  }

def report_error(msg):
  print msg
  exit(1)

def get_output_dir(output):
  if os.path.exists(options.output) and not os.path.isdir(options.output):
    report_error('Specified output location: ' + options.output + ' is not a directory')
  elif not os.path.exists(options.output):
    os.makedirs(options.output)

  root = os.path.abspath(output)
  if os.path.exists(os.path.join(root, '_build')):
    shutil.rmtree(os.path.join(root, '_build'))
  os.mkdir(os.path.join(root, '_build'))

  if os.path.exists(os.path.join(root, '_static')):
    shutil.rmtree(os.path.join(root, '_static'))
  os.mkdir(os.path.join(root, '_static'))

  if os.path.exists(os.path.join(root, '_templates')):
    shutil.rmtree(os.path.join(root, '_templates'))
  os.mkdir(os.path.join(root, '_templates'))

  for f in glob(root + '/*.rst'):
    os.unlink (f)

  for f in glob(root + '/*.html'):
    os.unlink (f)

  return root

def load_conf_template(info):
  template = open('../python-lib/sphinx_template.py', 'r')
  template_content = template.read()
  template_content = template_content.replace('{__project__}', info['project_name'])
  template_content = template_content.replace('{__year__}', info['year'])
  template_content = template_content.replace('{__authors__}', info['authors'])
  template_content = template_content.replace('{__version__}', info['version'])
  template_content = template_content.replace('{__base__}', info['file_name'])
  template.close()
  return template_content

if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option('-f', '--file', dest='file',
    help='Path to the input API description file')
  parser.add_option('-u', '--url', dest='url',
    help='URL of the input API description')
  parser.add_option('-m', '--method', dest='method',
    help='The HTTP method that should be used to pull the input API description from the input URL (defaults to OPTIONS)')
  parser.add_option('-o', '--output', dest='output',
    help='Output directory')
  parser.add_option('-e', '--export', dest='export',
    help='Export format (defaults to html)')

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
        report_error('Invalid protocol in the URL (must be http or https)')
      conn = httplib.HTTPConnection(result.netloc)
    conn.request(method, result.path)
    response = conn.getresponse()
    json_string = json.loads(response.read())
    conn.close()
    api = API(data=json_string)
    print 'API description loaded from', options.url
  else:
    api = None
    report_error('Please specify the path or the URL of the input API description file')

  if not options.output:
    report_error('Please specify the output directory')

  if options.export:
    export = options.export
  else:
    export = 'html'

  root  = get_output_dir(options.output)
  info = get_api_info(api)

  template_content = load_conf_template(info)
  conf = open(os.path.join(root, 'conf.py'), 'w')
  conf.write(template_content)
  conf.flush()
  conf.close()

  index = open(os.path.join(root, 'index.rst'), 'w')
  index.write(generate_index(api, info))
  index.flush()
  index.close()

  for resource in api.resources:
    resource_file = open(os.path.join(root, resource.name.lower()) + '.rst', 'w')
    resource_file.write(generate_resource_docs(resource, api))
    resource_file.flush()
    resource_file.close()

  for data_type in api.data_types:
    type_file = open(os.path.join(root, 'data_type_' + data_type.name.lower()) + '.rst', 'w')
    type_file.write(generate_data_type_docs(data_type, api))
    type_file.flush()
    type_file.close()

  for data_type in ANON_TYPES:
    type_file = open(os.path.join(root, 'data_type_' + data_type.name.lower()) + '.rst', 'w')
    type_file.write(generate_data_type_docs(data_type, api))
    type_file.flush()
    type_file.close()

  cmd = 'sphinx-build -b ' + export + ' ' + root + ' ' + root
  print 'Running Sphinx doc engine'
  output = commands.getoutput(cmd)
  print output

