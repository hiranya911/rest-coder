import string

__author__ = 'hiranya'

class PythonCodeGenerator:
  """
  Utility class for managing Python code generation. Provides helper methods
  for generating lines of Python code while maintaining proper indentation
  between code blocks.
  """

  def begin(self, tab="\t"):
    """
    Signal the beginning of code generation.

    Args:
      tab Character or character sequence to use for indentation
    """
    self.code = []
    self.tab = tab
    self.level = 0

  def end(self):
    """
    Signal the end of code generation.

    Returns:
      The code segment generated
    """
    return string.join(self.code, "")

  def writeln(self, string=''):
    """
    Generate a line of Python code.

    Args:
      string Line of code (without the terminating newline character)
    """
    self.write(string + '\n')

  def write(self, string):
    self.code.append(self.tab * self.level + string)

  def indent(self):
    """
    Increment the indentation level. Use this to signal the beginning of
    a new code block.
    """
    self.level += 1

  def dedent(self):
    """
    Decrement the indentation level. Use this to signal the ending of a new
    code block.
    """
    if not self.level:
      raise SyntaxError, "internal error in code generator"
    self.level -= 1

class MethodArgument:
  """
  Describes a method argument. A method argument is comprised of a name,
  an optional data type and an optional default value.
  """
  def __init__(self, name, data_type=None, default=None):
    self.name = name
    self.data_type = data_type
    self.default = default
    self.doc = None

class Method:
  """
  Describes a Python class method. Provides helper methods for constructing a
  method one line of code at a time.
  """

  def __init__(self, name):
    """
    Create a new Method instance.

    Args:
      name  Name of the method
    """
    self.name = name
    self.arguments = []
    self.return_type = None
    self.body = []
    self.argument_mappings = {}
    self.doc = None
    self.return_type = None
    self.doc_enabled = True

  def define_mapping(self, key, value):
    """
    Define a new mapping between two strings. This can be used to define string
    mappings between Python identifiers and API identifiers. For instance:
    API: 'test-param' => Python: 'test_param'

    Args:
      key String key
      value String value
    """
    self.argument_mappings[key] = value

  def get_mapping(self, key):
    """
    Get the string mapped to the specified key. Throws an error if no mapping
    exists for the specified key.

    Args:
      key A string identifier

    Returns:
      A string mapped to the given input key
    """
    return self.argument_mappings[key]

  def add_line(self, line):
    """
    Add a line of code to the method body.

    Args:
      line  A line of code to be added to the method body
    """
    self.body.append(line)

  def indent(self):
    """
    Increment the indentation level of the current position in the method
    body. Use this to signal the start of a new code block within the
    current method body.
    """
    self.body.append('__indent')

  def dedent(self):
    """
    Decrement the indentation level of the current position in the method
    body. Use this to signal the end of a code block within the
    current method body.
    """
    self.body.append('__dedent')

  def has_argument(self, name):
    """
    Check whether a particular argument is defined in the method signature.

    Args:
      name  Name of the argument to be checked

    Returns:
      True if the argument is defined in the method or False otherwise.
    """
    for arg in self.arguments:
      if arg.name == name:
        return True
    return False

  def generate_code(self, pcg):
    """
    Generate the Python code for this method using the provided PythonCodeGenerator
    instance. This will return a formatted Python code block consisting of the
    method signature and body. If no lines of code have been added to the method
    body (through the add_line method of this class), then a default method
    body consisting of a single 'pass' statement would be generated.

    Args:
      pcg An instance of the PythonCodeGenerator class

    Returns:
      A well-formed Python method as a formatted string
    """
    pcg.indent()
    signature = 'def ' + self.name + '(self'
    for i in range(0, len(self.arguments)):
      arg = self.arguments[i]
      if not arg.default:
        signature += ', ' + arg.name

    for i in range(0, len(self.arguments)):
      arg = self.arguments[i]
      if arg.default:
        signature += ', ' + arg.name + '=' + arg.default

    signature += '):'
    pcg.writeln(signature)
    pcg.indent()

    # Generate doc string for the method if applicable
    self.__generate_doc_string(pcg)

    if len(self.body):
      # Add method body - line by line
      for line in self.body:
        if line == '__indent':
          pcg.indent()
        elif line == '__dedent':
          pcg.dedent()
        else:
          pcg.writeln(line)
    else:
      # If no code lines have been added to this method, simply generate a
      # body with a single 'pass' statement.
      pcg.writeln('pass')
    pcg.dedent()
    pcg.dedent()

  def __format_doc(self):
    """
    Format the documentation defined for the current method into lines of text.
    Each line if no longer that 70 characters.

    Returns:
      A formatted string consisting of multiple lines of text.
    """
    counter = 0
    doc_list = list(self.doc.replace('\n', ' '))
    for i in range(0, len(doc_list)):
      if doc_list[i] == ' ' and counter > 70:
        doc_list[i] = '\n'
        counter = 0
      counter += 1
    return ''.join(doc_list)

  def __generate_doc_string(self, pcg):
    """
    Checks whether the current method should be given a doc string and
    generates the relevant code/comments if applicable. A method is eligible
    to have a doc string if all of the following conditions holds:
      1. Documentation is not explicitly disabled on the method (self.doc_enabled = False)
      2. Method is not the constructor of a class
      3. Method has some document worthy elements on it (a user specified comment block,
         arguments or return type)
    If the current method is not eligible for a doc string, this method simply returns.

    Args:
      pcg Python code generator used to generate code for this method
    """
    is_constructor = (self.name == '__init__')
    no_doc_elements = not (self.arguments or self.return_type or self.doc)

    if not self.doc_enabled or is_constructor or no_doc_elements:
      return

    pcg.writeln('"""')
    if self.doc:
      doc = self.__format_doc()
      for line in doc.split('\n'):
        pcg.writeln(line)

    if self.arguments:
      if self.doc:
        pcg.writeln()
      pcg.writeln('Args:')
      pcg.indent()
      for arg in self.arguments:
        doc = arg.name
        if arg.data_type:
          doc += ' ' + arg.data_type
        pcg.writeln(doc)
      pcg.dedent()

    if self.return_type:
      if self.doc or self.arguments:
        pcg.writeln()
      pcg.writeln('Returns:')
      pcg.indent()
      pcg.writeln(self.return_type)
      pcg.dedent()
    pcg.writeln('"""')

class StaticMethod(Method):
  """
  Describes a Python class method. This class extends the Method class and
  therefore has similar behavior. The main difference is that the Method class
  makes references to the self attribute in the generated code whereas this
  class does not generate any code with references to self.
  """

  def generate_code(self, pcg=None):
    """
    Generate the Python code for this method using the provided PythonCodeGenerator
    instance. This will return a formatted Python code block consisting of the
    method signature and body. If no lines of code have been added to the method
    body (through the add_line method of this class), then a default method
    body consisting of a single 'pass' statement would be generated.

    Args:
      pcg An instance of the PythonCodeGenerator class

    Returns:
      A well-formed Python static method as a formatted string
    """
    pcg = PythonCodeGenerator()
    pcg.begin(tab='  ')
    signature = 'def ' + self.name + '('
    for i in range(0, len(self.arguments)):
      arg = self.arguments[i]
      if i > 0:
        signature += ', '
      signature += arg.name
      if arg.default:
        signature += '=' + arg.default
    signature += '):'
    pcg.writeln(signature)
    pcg.indent()
    if len(self.body):
      for line in self.body:
        if line == '__indent':
          pcg.indent()
        elif line == '__dedent':
          pcg.dedent()
        else:
          pcg.writeln(line)
    else:
      pcg.writeln('pass')
    pcg.dedent()
    return pcg.end()

class Class:
  """
  Describes a Python class definition. A class has a unique name and one or
  methods (including a constructor). A class definition may also optionally
  extend from an existing super class. This class provides helper methods
  to generate the code for an entire Python class, including all the member
  methods.
  """

  def __init__(self, name, super_class=None):
    """
    Create a new class definition.

    Args:
      name  Name of the class
      super_class Name of the super class (Optional)
    """
    self.name = name
    self.super_class = super_class
    self.methods = []

  def has_method(self, name):
    """
    Checks whether a particular method is defined in this class.

    Args:
      name  Name of the method to be checked for existence

    Returns:
      True if the method is defined in the class, and False otherwise.
    """
    for method in self.methods:
      if method.name == name:
        return True
    return False

  def get_constructor(self):
    """
    Get the Method object for the constructor of the class.

    Returns:
      A Method instance (possibly None if the constructor is not defined)
    """
    for method in self.methods:
      if method.name == '__init__':
        return method
    return None

  def generate_code(self):
    """
    Generate code for this class. Generated code contains the class declaration,
    and code for all the member methods.

    Returns:
      A formatted string consisting of well-formed Python code for this class.
    """
    print 'Generating code for the', self.name, 'class...'
    pcg = PythonCodeGenerator()
    pcg.begin(tab='  ')
    signature = 'class ' + self.name
    if self.super_class:
      signature += '(' + self.super_class + ')'
    signature += ':'
    pcg.writeln(signature)
    if len(self.methods):
      for i in range(0, len(self.methods)):
        if i > 0:
          pcg.writeln()
        self.methods[i].generate_code(pcg)
    else:
      # If the class has no methods, simply generate a class body with a single
      # 'pass' statement.
      pcg.indent()
      pcg.writeln('pass')
      pcg.dedent()
    return pcg.end()
