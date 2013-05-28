from ast import NodeVisitor

def to_source(node):
  gen = SourceGenerator()
  return gen.visit(node)

class SourceGenerator(NodeVisitor):
  def visit_Expression(self, node):
    return self.visit(node.body)

  def visit_Compare(self, node):
    string = self.visit(node.left)
    for i in range(0, len(node.ops)):
      op = node.ops[i]
      comp = node.comparators[i]
      string += ' ' + self.visit(op) + ' ' + self.visit(comp)
    return string

  def visit_Call(self, node):
    string = self.visit(node.func) + '('
    for arg in node.args:
      if not string.endswith('('):
        string += ', '
      string += self.visit(arg)
    string += ')'
    return string

  def visit_UnaryOp(self, node):
    return self.visit(node.op) + ' ' + self.visit(node.operand)

  def visit_BoolOp(self, node):
    op = self.visit(node.op)
    string = self.visit(node.values[0])
    for value in node.values[1:]:
      string += ' ' + op + ' ' + self.visit(value)
    return string

  def visit_BinOp(self, node):
    return self.visit(node.left) + ' ' + self.visit(node.op) + ' ' + self.visit(node.right)

  def visit_Add(self, node):
    return '+'

  def visit_Mult(self, node):
    return '*'

  def visit_Sub(self, node):
    return '-'

  def visit_Div(self, node):
    return '/'

  def visit_Mod(self, node):
    return '%'

  def visit_And(self, node):
    return 'and'

  def visit_Or(self, node):
    return 'or'

  def visit_Not(self, node):
    return 'not'

  def visit_Attribute(self, node):
    return self.visit(node.value) + '.' + node.attr

  def visit_Eq(self, node):
    return '=='

  def visit_NotEq(self, node):
    return '!='

  def visit_Gt(self, node):
    return '>'

  def visit_Lt(self, node):
    return '<'

  def visit_GtE(self, node):
    return '>='

  def visit_LtE(self, node):
    return '<='

  def visit_In(self, node):
    return 'in'

  def visit_NotIn(self, node):
    return 'not in'

  def visit_Is(self, node):
    return 'is'

  def visit_IsNot(self, node):
    return 'is not'

  def visit_Name(self, node):
    return node.id

  def visit_Num(self, node):
    return repr(node.n)

  def visit_Str(self, node):
    return repr(node.s)

  def visit_Tuple(self, node):
    string = '('
    for element in node.elts:
      if not string.endswith('('):
        string += ', '
      string += self.visit(element)
    string += ')'
    return string

  def visit_List(self, node):
    string = '['
    for element in node.elts:
      if not string.endswith('['):
        string += ', '
      string += self.visit(element)
    string += ']'
    return string
