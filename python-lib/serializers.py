from api import *
from codegen_core import *

__author__ = 'hiranya'

def get_function_name(prefix, data_type, media_type, api):
  name = ''
  if isinstance(data_type, ContainerTypeRef):
    child_type = api.get_type_by_name(data_type.type.get_reference_name())
    name += prefix + '_' + data_type.container
    name = get_function_name(name, child_type, media_type, api)
  else:
    name += prefix + '_' + sanitize(data_type.name) + '_' + media_type
  return name

def sanitize(string):
  temp_name = ''.join([i for i in string if i.isalnum() or i == '_'])
  if not temp_name:
    temp_name = 'method'
  elif temp_name[0].isdigit():
    temp_name = 'method_' + temp_name
  return temp_name

def get_serializer(media_type, classes, class_name_mappings):
  if media_type == 'json':
    return JSONSerializer(classes, class_name_mappings)
  elif media_type == 'form':
    return FormSerializer(classes, class_name_mappings)
  else:
    return UnsupportedSerializer(classes, class_name_mappings, media_type)

class AbstractSerializer:
  def __init__(self, classes, class_name_mappings):
    self.classes = classes
    self.class_name_mappings = class_name_mappings

  def generate_serializers(self, data_type, api):
    raise NotImplementedError

  def generate_deserializers(self, data_type, api):
    raise NotImplementedError

  def generate_final_serializer(self):
    raise NotImplementedError

  def get_class_parameter(self, data_type, key):
    class_name = self.class_name_mappings[data_type]
    for clazz in self.classes:
      if clazz.name == class_name:
        constructor = clazz.get_constructor()
        return constructor.get_mapping(key)
    return None

class UnsupportedSerializer(AbstractSerializer):
  def __init__(self, classes, class_name_mappings, media_type):
    AbstractSerializer.__init__(self, classes, class_name_mappings)
    self.media_type = media_type

  def generate_final_serializer(self):
    sm = StaticMethod('serialize_final_' + self.media_type)
    sm.arguments.append(MethodArgument('obj'))
    sm.add_line('raise NotImplementedError')
    return sm

  def generate_serializers(self, data_type, api):
    function_name = get_function_name('serialize', data_type, self.media_type, api)
    sm = StaticMethod(function_name)
    sm.arguments.append(MethodArgument('obj'))
    sm.add_line('raise NotImplementedError')
    return [ sm, self.generate_final_serializer() ]

  def generate_deserializers(self, data_type, api):
    function_name = get_function_name('deserialize', data_type, self.media_type, api)
    sm = StaticMethod(function_name)
    sm.arguments.append(MethodArgument('obj'))
    sm.add_line('raise NotImplementedError')
    return [ sm ]

class JSONSerializer(AbstractSerializer):
  def __init__(self, classes, class_name_mappings):
    AbstractSerializer.__init__(self, classes, class_name_mappings)

  def generate_final_serializer(self):
    sm = StaticMethod('serialize_final_json')
    sm.arguments.append(MethodArgument('obj'))
    sm.add_line('return json.dumps(obj)')
    return sm

  def generate_serializers(self, data_type, api):
    serializers = list()
    function_name = get_function_name('serialize', data_type, 'json', api)
    sm = StaticMethod(function_name)
    sm.arguments.append(MethodArgument('obj'))

    if isinstance(data_type, PrimitiveTypeRef):
      sm.add_line('return obj')
      serializers.append(sm)
    elif isinstance(data_type, ContainerTypeRef):
      if isinstance(data_type.type, PrimitiveTypeRef):
        sm.add_line('return obj')
      else:
        sm.add_line('output = list()')
        sm.add_line('for item in obj:')
        sm.indent()
        child_serializers = self.generate_serializers(data_type.type, api)
        serializers.extend(child_serializers)
        sm.add_line('output.append(' + child_serializers[-1].name + '(item))')
        sm.dedent()
        sm.add_line('return output')
      serializers.append(sm)
    elif isinstance(data_type, NamedTypeDef):
      sm.add_line('output = dict()')
      for field in data_type.fields:
        field_type = field.type.type
        key = field.name
        param = self.get_class_parameter(data_type.name, key)
        if isinstance(field_type, PrimitiveTypeRef):
          value = 'obj.' + param
        elif isinstance(field_type, ContainerTypeRef) and \
             isinstance(field_type.type, PrimitiveTypeRef):
          value = 'obj.' + param
        elif isinstance(field_type, TypeDef):
          named_type = NamedTypeDef(name=data_type.name + '_' + field.name,
            fields=field_type.fields)
          child_serializers = self.generate_serializers(named_type, api)
          serializers.extend(child_serializers)
          value = child_serializers[-1].name + '(obj.' + param + ')'
        else:
          child_serializers = self.generate_serializers(field_type, api)
          serializers.extend(child_serializers)
          value = child_serializers[-1].name + '(obj.' + param + ')'
        if field.optional:
          sm.add_line('if obj.' + param + ':')
          sm.indent()
          sm.add_line('output[\'' + key + '\'] = ' + value)
          sm.dedent()
        else:
          sm.add_line('output[\'' + key + '\'] = ' + value)
      sm.add_line('return output')
      serializers.append(sm)
    else:
      actual_type = api.get_type_by_name(data_type.get_reference_name())
      serializers.extend(self.generate_serializers(actual_type, api))

    serializers.append(self.generate_final_serializer())
    return serializers

  def generate_deserializers(self, data_type, api):
    deserializers = list()
    function_name = get_function_name('deserialize', data_type, 'json', api)
    sm = StaticMethod(function_name)
    sm.arguments.append(MethodArgument('obj'))
    sm.add_line('if obj is None:')
    sm.indent()
    sm.add_line('return None')
    sm.dedent()
    if isinstance(data_type, PrimitiveTypeRef):
      sm.add_line('if isinstance(obj, str):')
      sm.indent()
      sm.add_line('return json.loads(obj)')
      sm.dedent()
      sm.add_line('return obj')
      deserializers.append(sm)
    elif isinstance(data_type, ContainerTypeRef):
      sm.add_line('if isinstance(obj, list):')
      sm.indent()
      sm.add_line('data = obj')
      sm.dedent()
      sm.add_line('else:')
      sm.indent()
      sm.add_line('data = json.loads(obj)')
      sm.dedent()
      sm.add_line('container = []')
      sm.add_line('for item in data:')
      sm.indent()
      if isinstance(data_type.type, PrimitiveTypeRef):
        sm.add_line('container.append(item)')
      else:
        child_deserializers = self.generate_deserializers(data_type.type, api)
        deserializers.extend(child_deserializers)
        sm.add_line('container.append(' + child_deserializers[-1].name + '(item))')
      sm.dedent()
      if data_type.container == 'list':
        sm.add_line('return list(container)')
      else:
        sm.add_line('return set(container)')
      deserializers.append(sm)
    elif isinstance(data_type, NamedTypeDef):
      sm.add_line('if isinstance(obj, dict):')
      sm.indent()
      sm.add_line('data = obj')
      sm.dedent()
      sm.add_line('else:')
      sm.indent()
      sm.add_line('data = json.loads(obj)')
      sm.dedent()
      if data_type.name in PrimitiveTypeRef.PRIMITIVES:
        sm.add_line('return data')
      elif data_type.name == '_API_':
        sm.add_line('return API(data)')
      else:
        fields = data_type.fields
        constructor = 'result = ' + self.class_name_mappings[data_type.name] + '('
        i = 0
        for field in fields:
          if i > 0:
            constructor += ', '
          i += 1
          field_type = field.type.type
          param = self.get_class_parameter(data_type.name, field.name)
          if isinstance(field_type, PrimitiveTypeRef):
            sm.add_line(param + ' = data.get(\'' + field.name + '\')')
          elif isinstance(field_type, ContainerTypeRef) and \
               isinstance(field_type.type, PrimitiveTypeRef):
            sm.add_line(param + ' = data.get(\'' + field.name + '\')')
          elif isinstance(field_type, TypeDef):
            named_type = NamedTypeDef(name=data_type.name + '_' + field.name,
              fields=field_type.fields)
            child_deserializers = self.generate_deserializers(named_type, api)
            deserializers.extend(child_deserializers)
            sm.add_line(param + ' = ' + child_deserializers[-1].name + '(data.get(\'' + field.name + '\'))')
          else:
            child_deserializers = self.generate_deserializers(field_type, api)
            deserializers.extend(child_deserializers)
            sm.add_line(param + ' = ' + child_deserializers[-1].name + '(data.get(\'' + field.name + '\'))')
          constructor += param + '=' + param
        constructor += ')'
        sm.add_line(constructor)
        sm.add_line('return result')
      deserializers.append(sm)
    else:
      actual_type = api.get_type_by_name(data_type.get_reference_name())
      deserializers.extend(self.generate_deserializers(actual_type, api))
    return deserializers

class FormSerializer(AbstractSerializer):
  def __init__(self, classes, class_name_mappings):
    AbstractSerializer.__init__(self, classes, class_name_mappings)

  def generate_final_serializer(self):
    sm = StaticMethod('serialize_final_form')
    sm.arguments.append(MethodArgument('obj'))
    sm.add_line('return urllib.urlencode(obj)')
    return sm

  def generate_serializers(self, data_type, api):
    serializers = list()
    function_name = get_function_name('serialize', data_type, 'form', api)
    sm = StaticMethod(function_name)
    sm.arguments.append(MethodArgument('obj'))

    if isinstance(data_type, PrimitiveTypeRef):
      sm.add_line('return [ (\'value\',obj) ]')
      serializers.append(sm)
    elif isinstance(data_type, ContainerTypeRef):
      if isinstance(data_type.type, PrimitiveTypeRef):
        sm.add_line('return [ (\'value\',obj) ]')
      else:
        sm.add_line('output = list()')
        sm.add_line('for item in obj:')
        sm.indent()
        child_serializers = self.generate_serializers(data_type.type, api)
        serializers.extend(child_serializers)
        sm.add_line('output.append(' + child_serializers[-1].name + '(item))')
        sm.dedent()
        sm.add_line('return output')
      serializers.append(sm)
    elif isinstance(data_type, NamedTypeDef):
      sm.add_line('output = dict()')
      for field in data_type.fields:
        field_type = field.type.type
        key = field.name
        param = self.get_class_parameter(data_type.name, key)
        if isinstance(field_type, PrimitiveTypeRef):
          value = 'obj.' + param
        elif isinstance(field_type, ContainerTypeRef) and\
             isinstance(field_type.type, PrimitiveTypeRef):
          value = 'obj.' + param
        else:
          child_serializers = self.generate_serializers(field_type, api)
          serializers.extend(child_serializers)
          value = child_serializers[-1].name + '(obj.' + param + ')'
        if field.optional:
          sm.add_line('if obj.' + param + ':')
          sm.indent()
          sm.add_line('output[\'' + key + '\'] = ' + value)
          sm.dedent()
        else:
          sm.add_line('output[\'' + key + '\'] = ' + value)
      sm.add_line('return output')
      serializers.append(sm)
    else:
      actual_type = api.get_type_by_name(data_type.get_reference_name())
      serializers.extend(self.generate_serializers(actual_type, api))

    serializers.append(self.generate_final_serializer())
    return serializers