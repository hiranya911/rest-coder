import ast
from collections import OrderedDict
import json
import traceback
import ast2code

__author__ = 'hiranya'

AVAILABILITY = 'availability'
BASE = 'base'
BINDING = 'binding'
CATEGORIES = 'categories'
CAUSE = 'cause'
COMMUNITY = 'community'
CONTENT_TYPE = 'contentType'
CONSTRAINTS = 'constraints'
COST_MODEL = 'costModel'
CURRENCY = 'currency'
DATA_TYPES = 'dataTypes'
DESCRIPTION = 'description'
EMAIL = 'email'
ENSURES = 'ensures'
ERRORS = 'errors'
FIELDS = 'fields'
HEADERS = 'headers'
ID = 'id'
INPUT = 'input'
INPUT_BINDINGS = 'inputBindings'
LICENSE = 'license'
METHOD = 'method'
MODE = 'mode'
NAME = 'name'
OPERATIONS = 'operations'
OPTIONAL = 'optional'
OUTPUT = 'output'
OWNERSHIP = 'ownership'
OWNER_TYPE = 'ownerType'
PARAMS = 'params'
PATH = 'path'
RATE_LIMIT = 'rateLimit'
REF = 'ref'
REQUESTS_PER_UNIT = 'requestsPerUnit'
REQUIRES = 'requires'
RESOURCES = 'resources'
SLA = 'sla'
STATUS = 'status'
STRATEGY = 'strategy'
TAGS = 'tags'
TIME_UNIT = 'timeUnit'
TYPE = 'type'
UNIT_PRICE = 'unitPrice'
VERSION = 'version'

def init_field(obj, data, key, required=False):
  if data.has_key(key):
    attribute = getattr(obj, key)
    if isinstance(attribute, list):
      if isinstance(data[key], list):
        attribute.extend(sanitize(data[key]))
      else:
        attribute.append(sanitize(data[key]))
    elif isinstance(attribute, bool) or isinstance(attribute, int) or isinstance(attribute, float):
      setattr(obj, key, data[key])
    else:
      setattr(obj, key, sanitize(data[key]))
  elif required:
    raise APIDescriptionException('Attribute ' + key + ' is required')

def serialize_field(obj, data, key):
  if hasattr(obj, key):
    value = getattr(obj, key)
    if value is not None:
      if isinstance(value, list):
        if len(value):
          data[key] = value
      else:
        data[key] = value

def sanitize(value):
  if isinstance(value, list):
    copy = []
    for item in value:
      copy.append(str(item))
    return copy
  else:
    return str(value)

class APIDescriptionException(Exception):
  pass

class Field:
  def __init__(self, data=None, name=None, type=None):
    self.name = None
    self.description = None
    self.type = None
    self.optional = False
    if data is not None:
      if name is not None or type is not None:
        raise APIDescriptionException('name and type attributes must be None '
                                      'when the data field is provided')
      else:
        init_field(self, data, NAME, True)
        init_field(self, data, DESCRIPTION)
        init_field(self, data, OPTIONAL)
        self.type = DataType(data)
    else:
      if name is None or type is None:
        raise APIDescriptionException('name and type attributes must not be '
                                      'None when the data field is not provided')
      else:
        self.name = name
        self.type = type

  def serialize(self):
    data = OrderedDict([(NAME , self.name)])
    serialize_field(self, data, DESCRIPTION)
    if self.optional:
      serialize_field(self, data, OPTIONAL)
    data[TYPE] = self.type.serialize()
    return data

  def validate(self, types):
    self.type.validate(types)

class TypeRef(object):
  def get_reference_name(self):
    raise NotImplementedError

  def validate(self, types):
    raise NotImplementedError

def create_type_reference(name):
  try:
    return PrimitiveTypeRef(name)
  except Exception:
    pass

  try:
    return ContainerTypeRef(name)
  except Exception:
    pass

  return CustomTypeRef(name)

class PrimitiveTypeRef(TypeRef):
  PRIMITIVES = ( 'short', 'int', 'long', 'string', 'boolean',
                'double', 'byte', 'binary', 'href' )

  def __init__(self, name):
    if name in self.PRIMITIVES:
      self.name = name
    else:
      raise APIDescriptionException('Invalid primitive type name: ' + name)

  def get_reference_name(self):
    return self.name

  def validate(self, types):
    pass

class ContainerTypeRef(TypeRef):
  CONTAINERS = ( 'list', 'set' )

  def __init__(self, name):
    index = name.index('(')
    container = name[0 : index]
    type = name[index + 1 : -1]
    if container in self.CONTAINERS:
      self.container = container
      self.type = create_type_reference(type)
    else:
      raise APIDescriptionException('Invalid container type: ' + container)

  def validate(self, types):
    self.type.validate(types)

  def get_reference_name(self):
    return self.container + '(' + self.type.get_reference_name() + ')'

class CustomTypeRef(TypeRef):
  def __init__(self, name):
    self.name = name

  def get_reference_name(self):
    return self.name

  def validate(self, types):
    if self.name == '_API_' or self.name == '_NONE_':
      return
    for type in types:
      if type == self.name:
        return
    raise APIDescriptionException('Reference to unknown data type: ' + self.name)

class TypeDef(object):
  def __init__(self, data=None, fields=None):
    self.fields = []
    self.constraints = []
    self.description = None
    if data is not None:
      if fields is not None:
        raise APIDescriptionException('fields attribute must be None when '
                                      'the data field is provided')
      else:
        fields = data[FIELDS]
        for field in fields:
          self.fields.append(Field(field))
        init_field(self, data, DESCRIPTION)
        if data.has_key(CONSTRAINTS):
          constraints = data[CONSTRAINTS]
          for constraint in constraints:
            self.constraints.append(sanitize(constraint))
    else:
      if fields is None:
        raise APIDescriptionException('fields attribute must not be None when'
                                      ' the data field is not provided')
      else:
        self.fields = fields

  def get_constraints(self, api):
    constraints = []
    constraints.extend(self.constraints)
    return constraints

  def serialize(self):
    data = OrderedDict()
    serialize_field(self, data, DESCRIPTION)
    data[FIELDS] = []
    for field in self.fields:
      data[FIELDS].append(field.serialize())

    if self.constraints:
      data[CONSTRAINTS] = []
      for constraint in self.constraints:
        data[CONSTRAINTS].append(constraint)
    return data

  def validate(self, types):
    field_names = []
    for field in self.fields:
      field.validate(types)
      if field.name not in field_names:
        field_names.append(field.name)
      else:
        raise APIDescriptionException('Duplicate field ' + field.name + ' in type')

class NamedTypeDef(TypeDef):
  def __init__(self, data=None, name=None, fields=None):
    if data is not None:
      if name is not None or fields is not None:
        raise APIDescriptionException('name and fields attributes must be None'
                                      ' when the data field is provided')
      else:
        TypeDef.__init__(self, data=data)
        self.name = data[NAME]
    else:
      if name is None or fields is None:
        raise APIDescriptionException('name and fields attributes must not '
                                      'be None when the data field is not Provided')
      else:
        TypeDef.__init__(self, fields=fields)
        self.name = name

  def serialize(self):
    data = OrderedDict([(NAME , self.name)])
    parent = super(NamedTypeDef, self).serialize()
    for k,v in parent.items():
      data[k] = v
    return data

class DataType:
  def __init__(self, data):
    type_value = data[TYPE]
    self.ref = None
    if isinstance(type_value, dict):
      self.type = TypeDef(type_value)
    else:
      self.type = create_type_reference(type_value)
      if data.has_key(REF):
        self.ref = data[REF]

  def serialize(self):
    if isinstance(self.type, TypeDef):
      return self.type.serialize()
    else:
      return self.type.get_reference_name()

  def isHref(self):
    return isinstance(self.type, PrimitiveTypeRef) and self.type.get_reference_name() == 'href'

  def validate(self, types):
    self.type.validate(types)
    if self.ref is not None and not self.isHref():
      raise APIDescriptionException('Invalid reference to: ' + self.ref + ' from non href type')

class InputBinding(object):
  def __init__(self, data=None, mode=None, name=None, type=None):
    self.mode = None
    self.name = None
    self.type = None
    if data is not None:
      if mode is not None or name is not None or type is not None:
        raise APIDescriptionException('mode, name and type attributes must be '
                                      'None when the data field is provided')
      else:
        init_field(self, data, MODE, True)
        init_field(self, data, NAME, True)
        self.type = DataType(data)
    else:
      if mode is None or name is None or type is None:
        raise APIDescriptionException('mode, name and type attributes must not '
                                      'be None when the data field is not provided')
      else:
        self.mode = mode
        self.name = name
        self.type = type

  def validate(self, types):
    self.type.validate(types)

class NamedInputBinding(InputBinding):
  def __init__(self, data=None, id=None, mode=None, name=None, type=None):
    InputBinding.__init__(self, data, mode, name, type)
    self.id = None
    if data is not None:
      init_field(self, data, ID, True)
    else:
      self.id = id

  def serialize(self):
    return OrderedDict([
      (ID , self.id),
      (MODE , self.mode),
      (NAME , self.name),
      (TYPE, self.type.serialize())
    ])

class Parameter:
  def __init__(self, data=None, binding=None):
    self.binding = None
    self.optional = False
    self.description = None
    if data is not None:
      if binding is not None:
        raise APIDescriptionException('binding attribute must be None when '
                                      'the data field is provided')
      else:
        if data.has_key(BINDING):
          init_field(self, data, BINDING)
        else:
          self.binding = InputBinding(data=data)
        init_field(self, data, DESCRIPTION)
        init_field(self, data, OPTIONAL)
    else:
      if binding is None:
        raise APIDescriptionException('binding attribute must not be None when '
                                      'the data field is not provided')
      else:
        self.binding = binding

  def serialize(self):
    data = OrderedDict()
    if isinstance(self.binding, InputBinding):
      data[NAME] = self.binding.name
      data[MODE] = self.binding.mode
      data[TYPE] = self.binding.type.serialize()
    else:
      data[BINDING] = self.binding

    serialize_field(self, data, DESCRIPTION)
    if self.optional:
      data[OPTIONAL] = True
    return data

  def validate(self, types, bindings):
    if isinstance(self.binding, InputBinding):
      self.binding.validate(types)
    else:
      for binding in bindings:
        if binding == self.binding:
          return
      raise APIDescriptionException('Reference to unknown binding: ' + self.binding)

class Input:
  def __init__(self, data=None, content_type=None, type=None):
    self.contentType = []
    self.type = None
    self.params = []
    self.description = None
    if data is not None:
      if content_type is not None or type is not None:
        raise APIDescriptionException('content_type and types attributes must '
                                     'be None when the data field is provided')
      else:
        init_field(self, data, CONTENT_TYPE)
        init_field(self, data, DESCRIPTION)
        if data.has_key(PARAMS):
          for param in data[PARAMS]:
            self.params.append(Parameter(data=param))
        if data.has_key(TYPE):
          self.type = DataType(data)
    else:
      if type is None:
        raise APIDescriptionException('type attribute must not be None when '
                                      'the data field is not provided')
      if content_type is not None:
        if isinstance(content_type, list):
          self.contentType.extend(content_type)
        else:
          self.contentType.append(content_type)
      self.type = type

  def serialize(self):
    data = OrderedDict()
    if self.params:
      data[PARAMS] = []
      for param in self.params:
        data[PARAMS].append(param.serialize())
    serialize_field(self, data, CONTENT_TYPE)
    if self.type:
      data[TYPE] = self.type.serialize()
    serialize_field(self, data, DESCRIPTION)
    return data

  def validate(self, types, bindings):
    if self.type:
      self.type.validate(types)
    for param in self.params:
      param.validate(types, bindings)

class Header:
  def __init__(self, data=None, name=None, type=None):
    self.name = None
    self.description = None
    self.type = None
    if data is not None:
      if name is not None or type is not None:
        raise APIDescriptionException('name and type attributes must be None '
                                      'when the data field is provided')
      else:
        init_field(self, data, NAME, True)
        init_field(self, data, DESCRIPTION)
        self.type = DataType(data)
    else:
      if name is None or type is None:
        raise APIDescriptionException('name and type attributes must not be '
                                      'None when the data field is not provided')
      else:
        self.name = name
        self.type = type

  def serialize(self):
    data = OrderedDict([(NAME, self.name)])
    serialize_field(self, data, DESCRIPTION)
    data[TYPE] = self.type.serialize()
    if self.type.ref:
      data[REF] = self.type.ref
    return data

class Output:
  def __init__(self, data=None, status=None, content_type=None, type=None):
    self.status = -1
    self.contentType = []
    self.type = None
    self.headers = []
    self.description = None
    if data is not None:
      if status is not None or content_type is not None or type is not None:
        raise APIDescriptionException('status, content_type and type attributes '
                                      'must be None when the data field is provided')
      else:
        init_field(self, data, STATUS, True)
        init_field(self, data, CONTENT_TYPE)
        init_field(self, data, DESCRIPTION)
        if data.has_key(TYPE):
          self.type = DataType(data)
        if data.has_key(HEADERS):
          for header in data[HEADERS]:
            self.headers.append(Header(header))
    else:
      self.status = status
      self.contentType = content_type
      self.type = type

  def serialize(self):
    data = OrderedDict([
      (STATUS , self.status),
      (CONTENT_TYPE , self.contentType)
    ])
    if self.type:
      data[TYPE] = self.type.serialize()
      if self.type.ref:
        data[REF] = self.type.ref
    serialize_field(self, data, DESCRIPTION)
    if self.headers:
      data[HEADERS] = []
      for header in self.headers:
        data[HEADERS].append(header.serialize())
    return data

  def validate(self, types):
    if self.type:
      self.type.validate(types)

class Operation:
  def __init__(self, data=None, name=None, method=None):
    self.name = None
    self.method = None
    self.input = None
    self.output = None
    self.errors = {}
    self.description = None
    self.requires = []
    self.ensures = []
    if data is not None:
      if name is not None or method is not None:
        raise APIDescriptionException('name and method attributes must be None '
                                      'when the data field is provided')
      else:
        init_field(self, data, NAME, True)
        init_field(self, data, METHOD, True)
        init_field(self, data, DESCRIPTION)
        if data.has_key(INPUT):
          self.input = Input(data=data[INPUT])
        if data.has_key(OUTPUT):
          self.output = Output(data=data[OUTPUT])
        if data.has_key(ERRORS):
          for error in data[ERRORS]:
            self.errors[int(error[STATUS])] = sanitize(error[CAUSE])
        if data.has_key(REQUIRES):
          for condition in data[REQUIRES]:
            self.requires.append(sanitize(condition))
        if data.has_key(ENSURES):
          for condition in data[ENSURES]:
            self.ensures.append(sanitize(condition))
    else:
      if name is None or method is None:
        raise APIDescriptionException('name and method attributes must not be '
                                      'None when the data field is not provided')
      else:
        self.name = name
        self.method = method

  def get_pre_conditions(self, api):
    conditions = []
    conditions.extend(self.requires)
    if self.input and self.input.type:
      data_type = self.input.type.type
      conditions.extend(self.__get_type_constraints(data_type, api, 'input'))
    return conditions

  def get_post_conditions(self, api):
    conditions = []
    conditions.extend(self.ensures)
    if self.output.type:
      data_type = self.output.type.type
      conditions.extend(self.__get_type_constraints(data_type, api, 'output'))
    return conditions

  def __get_type_constraints(self, type, api, context):
    constraints = []
    if isinstance(type, TypeDef):
      constraints.extend(type.constraints)
      for field in type.fields:
        field_constraints = self.__get_type_constraints(field.type.type, api,
          context + '.' + field.name)
        for constraint in field_constraints:
          constraints.append(self.__change_context(constraint, 'self',
            'self.' + field.name))
    elif isinstance(type, CustomTypeRef):
      type_def = api.get_type_by_name(type.get_reference_name())
      for constraint in self.__get_type_constraints(type_def, api, context):
        constraints.append(self.__change_context(constraint, 'self', context))
    elif isinstance(type, ContainerTypeRef):
      child_type = type.type
      if context.endswith('_item'):
        variable = '_' + context
      elif context.startswith('_item.'):
        variable =  '_' + context.replace('.','_')
      else:
        variable = '_item'
      for constraint in self.__get_type_constraints(child_type, api, variable):
        constraints.append('forall(' + variable + ', ' + context +
                           ', ' + constraint + ')')
    return constraints

  def __change_context(self, string, old, new):
    changer = ContextChanger()
    return changer.change_context(string, old, new)

  def serialize(self):
    data = OrderedDict([
      (NAME , self.name),
      (METHOD , self.method)
    ])
    serialize_field(self, data, DESCRIPTION)
    if self.input:
      input = self.input.serialize()
      if input:
        data[INPUT] = input
    if self.output:
      output = self.output.serialize()
      if output:
        data[OUTPUT] = output
    if self.errors:
      data[ERRORS] = []
      for k,v in self.errors.items():
        data[ERRORS].append({STATUS:k,CAUSE:v})
    if self.requires:
      data[REQUIRES] = []
      for condition in self.requires:
        data[REQUIRES].append(condition)
    if self.ensures:
      data[ENSURES] = []
      for condition in self.ensures:
        data[ENSURES].append(condition)
    return data

  def validate(self, types, bindings):
    if self.method == 'POST' or self.method == 'PUT':
      if not self.input:
        raise APIDescriptionException('input field undefined for entity enclosing request')
    if self.input:
      self.input.validate(types, bindings)
    self.output.validate(types)
    for condition in self.requires:
      ast.parse(condition, mode='eval')
    for condition in self.ensures:
      ast.parse(condition, mode='eval')

class Resource:
  def __init__(self, data=None, name=None, path=None):
    self.name = None
    self.path = None
    self.input_bindings = []
    self.operations = []
    if data is not None:
      if name is not None or path is not None:
        raise APIDescriptionException('name and path attributes must be None '
                                      'when data field is provided')
      else:
        init_field(self, data, NAME, True)
        init_field(self, data, PATH, True)
        for op in data[OPERATIONS]:
          self.operations.append(Operation(data=op))
        if data.has_key(INPUT_BINDINGS):
          for binding in data[INPUT_BINDINGS]:
            self.input_bindings.append(NamedInputBinding(binding))

    else:
      if name is None or path is None:
        raise APIDescriptionException('name and path attributes must not be '
                                      'None when the data field is not provided')
      else:
        self.name = name
        self.path = path

  def serialize(self):
    data = OrderedDict()
    if self.input_bindings:
      data[INPUT_BINDINGS] = []
      for binding in self.input_bindings:
        data[INPUT_BINDINGS].append(binding.serialize())
    data[NAME] = self.name
    data[PATH] = self.path
    data[OPERATIONS] = []

    for op in self.operations:
      data[OPERATIONS].append(op.serialize())
    return data

  def get_binding_by_id(self, id):
    for binding in self.input_bindings:
      if binding.id == id:
        return binding
    return None

  def validate(self, types):
    binding_names = []
    for binding in self.input_bindings:
      binding.validate(types)
      binding_names.append(binding.id)
    op_names = []
    for operation in self.operations:
      operation.validate(types, binding_names)
      if operation.name in op_names:
        raise APIDescriptionException('Duplication operation ' + operation.name +
                                      ' in resource ' + self.name)
      else:
        op_names.append(operation.name)

class Owner:
  def __init__(self, data=None, name=None, email=None, type=None):
    self.name = None
    self.email = None
    self.ownerType = None
    if data is not None:
      if name is not None or email is not None or type is not None:
        raise APIDescriptionException('name, email and type attributes must '
                                      'be None when the data field is provided')
      else:
        init_field(self, data, NAME, True)
        init_field(self, data, EMAIL, True)
        init_field(self, data, OWNER_TYPE, True)
    else:
      if name is None or email is None or type is None:
        raise APIDescriptionException('name, email and type attributes must '
                                      'not be None when the data field is provided')
      else:
        self.name = name
        self.email = email
        self.ownerType = type

  def serialize(self):
    return OrderedDict([
      ('name' , self.name),
      ('email', self.email),
      ('ownerType', self.ownerType)
    ])

class CostModel:
  def __init__(self, data=None, currency=None, unit_price=None, requests=None):
    self.currency = None
    self.unitPrice = 0.0
    self.requestsPerUnit = 0
    if data is not None:
      if currency is not None or unit_price is not None or requests is not None:
        raise APIDescriptionException('currency, unit_price and requests '
                                      'attributes must be None when the data '
                                      'field is provided')
      else:
        init_field(self, data, CURRENCY, True)
        init_field(self, data, UNIT_PRICE, True)
        init_field(self, data, REQUESTS_PER_UNIT, True)
    else:
      if currency is None or unit_price is None or requests is None:
        raise APIDescriptionException('currency, unit_price and requests '
                                      'attributes must not be None when the '
                                      'data field is not provided')
      else:
        self.currency = currency
        self.unitPrice = unit_price
        self.requestsPerUnit = requests

  def serialize(self):
    return OrderedDict([
      (CURRENCY , self.currency),
      (UNIT_PRICE, self.unitPrice),
      (REQUESTS_PER_UNIT, self.requestsPerUnit)
    ])

class SLADef:
  def __init__(self, data=None, name=None):
    self.name = None
    self.description = None
    self.availability = 0.0
    self.rateLimit = 0
    self.timeUnit = None
    self.costModel = None
    if data is not None:
      if name is not None:
        raise APIDescriptionException('name attribute must be None when the '
                                      'data field is provided')
      else:
        init_field(self, data, NAME, True)
        init_field(self, data, DESCRIPTION)
        init_field(self, data, AVAILABILITY)
        init_field(self, data, RATE_LIMIT)
        if self.rateLimit:
          init_field(self, data, TIME_UNIT, True)
        if data.has_key(COST_MODEL):
          self.costModel = CostModel(data[COST_MODEL])
    else:
      if name is not None:
        raise APIDescriptionException('name attribute must not be None when '
                                      'the data field is not provided')
      else:
        self.name = name

  def serialize(self):
    data = OrderedDict([
      (NAME , self.name)
    ])
    serialize_field(self, data, DESCRIPTION)
    if self.availability:
      data[AVAILABILITY] = self.availability
    if self.rateLimit:
      data[RATE_LIMIT] = self.rateLimit
      data[TIME_UNIT] = self.timeUnit
    if self.costModel:
      data[COST_MODEL] = self.costModel.serialize()
    return data

class Version:
  def __init__(self, data=None, id=None):
    self.id = None
    self.strategy = None
    if data is not None:
      if id is not None:
        raise APIDescriptionException('id attribute must be None when the '
                                      'data field is provided')
      else:
        init_field(self, data, ID, True)
        init_field(self, data, STRATEGY)
    else:
      if id is not None:
        raise APIDescriptionException('id attribute must not be None when '
                                      'the data field is not provided')
      else:
        self.id = id

  def serialize(self):
    data = OrderedDict([
      (ID , self.id)
    ])
    serialize_field(self, data, STRATEGY)
    return data

class API:
  """
  Represents an API description at the runtime. Encapsulates all the major
  attributes of an API description including name, resources, data types and
  other non-functional properties.
  """

  def __init__(self, data=None, name=None):
    """
    Creates a new API instance using the provided input data. This constructor
    takes two different arguments, but only one of them should be provided
    at a time. The dictionary argument is useful for creating an API instance
    from a given JSON description of the API. The other string argument is
    useful when creating an API instance entirely programatically.

    Args:
      data  A dictionary containing all the required API attributes
      name  Name of the API
    """
    self.name = None
    self.base = []
    self.description = None
    self.version = None
    self.resources = []
    self.data_types = []
    self.ownership = []
    self.sla = []
    self.license = None
    self.categories = []
    self.tags = []
    self.security = None
    self.community = None

    if data is not None:
      if name is not None:
        raise APIDescriptionException('name attribute must be None when the '
                                      'data field is provided')
      else:
        init_field(self, data, NAME, True)
        init_field(self, data, DESCRIPTION)
        init_field(self, data, BASE)
        init_field(self, data, CATEGORIES)
        init_field(self, data, TAGS)
        init_field(self, data, LICENSE)
        init_field(self, data, COMMUNITY)
        if data.has_key(RESOURCES):
          for resource in data[RESOURCES]:
            self.resources.append(Resource(data=resource))
        if data.has_key(DATA_TYPES):
          for data_type in data[DATA_TYPES]:
            self.data_types.append(NamedTypeDef(data=data_type))
        if data.has_key(OWNERSHIP):
          for owner in data[OWNERSHIP]:
            self.ownership.append(Owner(data=owner))
        if data.has_key(SLA):
          for sla in data[SLA]:
            self.sla.append(SLADef(data=sla))
        if data.has_key(VERSION):
          self.version = Version(data=data[VERSION])
        self.validate()
    else:
      if name is None:
        raise APIDescriptionException('name attribute must not be None when '
                                      'the data field is not provided')
      else:
        self.name = name

  def get_type_by_name(self, name):
    for data_type in self.data_types:
      if data_type.name == name:
        return data_type

    try:
      data_type = PrimitiveTypeRef(name)
      return data_type
    except Exception:
      pass

    try:
      data_type = ContainerTypeRef(name)
      return data_type
    except Exception:
      pass

    if name == '_API_':
      return NamedTypeDef(name='_API_', fields=[])
    return None

  def serialize(self):
    data = OrderedDict([
      (NAME , self.name),
    ])
    serialize_field(self, data, DESCRIPTION)
    serialize_field(self, data, BASE)
    serialize_field(self, data, CATEGORIES)
    serialize_field(self, data, TAGS)
    serialize_field(self, data, LICENSE)
    serialize_field(self, data, COMMUNITY)
    data[RESOURCES] = []
    for resource in self.resources:
      data[RESOURCES].append(resource.serialize())
    if self.data_types:
      data[DATA_TYPES] = []
      for data_type in self.data_types:
        data[DATA_TYPES].append(data_type.serialize())
    if self.ownership:
      data[OWNERSHIP] = []
      for owner in self.ownership:
        data[OWNERSHIP].append(owner.serialize())
    if self.sla:
      data[SLA] = []
      for sla in self.sla:
        data[SLA].append(sla.serialize())
    if self.version:
      data[VERSION] = self.version.serialize()
    return data

  def validate(self):
    type_names = []
    for type in self.data_types:
      if type.name not in type_names:
        type_names.append(type.name)
      else:
        raise APIDescriptionException('Duplicate type definitions for ' + type.name)
    for type in self.data_types:
      type.validate(type_names)
    for resource in self.resources:
      resource.validate(type_names)

  def serialize_json(self):
    return json.dumps(self.serialize(), indent=4, separators=(',', ': '))

class ContextChanger(ast.NodeTransformer):
  def change_context(self, string, old, new):
    self.old = old
    self.new = new
    tree = ast.parse(string, mode='eval')
    self.visit(tree)
    return ast2code.to_source(tree)

  def visit_Name(self, node):
    if node.id == self.old:
      return ast.copy_location(ast.Name(id=self.new, ctx=ast.Load()), node)
    else:
      return node

def parse(path):
  """
  Parse and validate the specified API description file.

  Args:
    path  Path to the API description file

  Returns:
    An instance of the API class.

  Raises:
    APIDescriptionException If an error occurs while parsing or validating
                            the input API description
  """
  try:
    fp = open(path)
    data = json.load(fp)
    fp.close()
    return API(data)
  except APIDescriptionException as e:
    raise e
  except Exception as e:
    traceback.print_exc()
    raise APIDescriptionException(e)

