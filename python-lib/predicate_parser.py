import ast
import _ast
import os
import random
import string
import api
import ast2code

__author__ = 'hiranya'

PREDICATE_SIMILARITY_THRESHOLD = 0.9
PREDICATE_SET_SIMILARITY_THRESHOLD = 0.85

def parse(string):
  return ast.parse(string, mode='eval')

class PredicateEvaluator(ast.NodeVisitor):
  def evaluate(self, string):
    tree = parse(string)
    return self.visit(tree)

  def visit_Expression(self, node):
    return self.visit(node.body)

  def visit_Compare(self, node):
    left = self.visit(node.left)
    op = node.ops[0]
    right = self.visit(node.comparators[0])
    if isinstance(op, _ast.Gt):
      return left > right
    elif isinstance(op, _ast.Lt):
      return left < right
    elif isinstance(op, _ast.GtE):
      return left >= right
    elif isinstance(op, _ast.LtE):
      return left <= right
    elif isinstance(op, _ast.Eq):
      return left == right
    elif isinstance(op, _ast.NotEq):
      return left != right
    elif isinstance(op, _ast.In):
      return left in right
    elif isinstance(op, _ast.NotIn):
      return left not in right
    elif isinstance(op, _ast.Is):
      return left is right
    elif isinstance(op, _ast.IsNot):
      return left not in right

  def visit_Num(self, node):
    return node.n

  def visit_Str(self, node):
    return node.s

  def visit_List(self, node):
    items = []
    for item in node.elts:
      items.append(self.visit(item))
    return items

  def visit_Tuple(self, node):
    items = []
    for item in node.elts:
      items.append(self.visit(item))
    return tuple(items)

  def visit_Dict(self, node):
    keys = node.keys
    values = node.values
    items = {}
    for i in range(0, len(keys)):
      items[keys[i]] = values[i]
    return items

  def visit_Attribute(self, node):
    value = self.visit(node.value)
    return getattr(value, node.attr)

  def visit_Name(self, node):
    if node.id == 'True':
      return True
    return None

  def visit_BinOp(self, node):
    left = self.visit(node.left)
    op = node.op
    right = self.visit(node.right)
    if isinstance(op, _ast.Add):
      return left + right
    elif isinstance(op, _ast.Sub):
      return left - right
    elif isinstance(op, _ast.Mult):
      return left * right
    elif isinstance(op, _ast.Div):
      return left / right
    elif isinstance(op, _ast.Mod):
      return left % right
    elif isinstance(op, _ast.Pow):
      return left ** right

  def visit_BoolOp(self, node):
    result = None
    op = node.op
    for value in node.values:
      if result is None:
        result = self.visit(value)
      elif isinstance(op, _ast.And):
        result = result and self.visit(value)
      else:
        result = result or self.visit(value)
    return result

  def visit_UnaryOp(self, node):
    result = self.visit(node.operand)
    op = node.op
    if isinstance(op, _ast.Not):
      return not result

  def visit_Call(self, node):
    function = node.func.id
    args = node.args
    if function == 'len':
      return len(self.visit(args[0]))
    elif function == 'forall':
      items = self.visit(args[1])
      for item in items:
        if not self.visit(args[2]):
          return False
      return True
    elif function == 'exists':
      items = self.visit(args[1])
      for item in items:
        if self.visit(args[2]):
          return True
      return False
    elif function == 'implies':
      # also support follows/iff/niff
      left = bool(self.visit(args[0]))
      right = bool(self.visit(args[1]))
      return left and right

class ASTComparator(ast.NodeVisitor):
  def compare(self, item1, item2):
    if isinstance(item1, str):
      left = parse(item1)
    else:
      left = item1
    if isinstance(item2, str):
      right = parse(item2)
    else:
      right = item2

    self.current_right = right
    return self.visit(left)

  def visit_Expression(self, node):
    if not isinstance(self.current_right, _ast.Expression):
      print 'expression mismatch'
      return False
    left = node.body
    self.current_right = self.current_right.body
    return self.visit(left)

  def visit_BinOp(self, node):
    if not isinstance(self.current_right, _ast.BinOp):
      return False

    left_op = node.op
    right_op = self.current_right.op
    if not isinstance(left_op, type(right_op)):
      print 'binop op mismatch'
      return False

    temp = self.current_right
    left_arg = node.left
    self.current_right = temp.left
    left_2_left = False
    if not self.visit(left_arg):
      self.current_right = temp.right
      if not self.visit(left_arg):
        print 'binop left arg mismatch'
        return False
    else:
      left_2_left = True

    right_arg = node.right
    if left_2_left:
      self.current_right = temp.right
    else:
      self.current_right = temp.left
    return self.visit(right_arg)

  def visit_BoolOp(self, node):
    if not isinstance(self.current_right, _ast.BoolOp):
      print 'boolop mismatch'
      return False
    left_op = node.op
    right_op = self.current_right.op
    if not isinstance(left_op, type(right_op)):
      print 'boolop op mismatch'
      return False

    left_values = node.values
    right_values = self.current_right.values
    if len(left_values) != len(right_values):
      print 'boolop value count mismatch'
      return False

    matches = []
    for i in range(0, len(left_values)):
      for j in range(0, len(right_values)):
        self.current_right = right_values[j]
        if self.visit(left_values[i]):
          matches.append(True)
          break

    if len(matches) != len(left_values):
      print 'one or more boolop values did not match'
      return False
    return True

  def visit_Compare(self, node):
    if not isinstance(self.current_right, _ast.Compare):
      print 'comparison mismatch'
      return False

    left_op = node.ops[0]
    right_op = self.current_right.ops[0]
    opposite_op = False
    if not isinstance(left_op, type(right_op)):
      if isinstance(left_op, _ast.Lt) and isinstance(right_op, _ast.Gt):
        opposite_op = True
      elif isinstance(left_op, _ast.Gt) and isinstance(right_op, _ast.Lt):
        opposite_op = True
      elif isinstance(left_op, _ast.LtE) and isinstance(right_op, _ast.GtE):
        opposite_op = True
      elif isinstance(left_op, _ast.GtE) and isinstance(right_op, _ast.LtE):
        opposite_op = True
      else:
        return False
    elif isinstance(left_op, _ast.Eq) or isinstance(left_op, _ast.NotEq):
      opposite_op = True

    temp = self.current_right
    if opposite_op:
      left_arg = node.comparators[0]
      self.current_right = temp.left
      if not self.visit(left_arg):
        print 'comparison arg mismatch'
        return False

      right_arg = node.left
      self.current_right = temp.comparators[0]
      return self.visit(right_arg)
    else:
      left_arg = node.left
      self.current_right = temp.left
      if not self.visit(left_arg):
        print 'comparison left arg mismatch'
        return False

      right_arg = node.comparators[0]
      self.current_right = temp.comparators[0]
      return self.visit(right_arg)

  def visit_Call(self, node):
    if not isinstance(self.current_right, _ast.Call):
      print 'function call mismatch'
      return False
    temp = self.current_right
    left_name = node.func
    self.current_right = temp.func
    if not self.visit(left_name):
      print 'function name mismatch'
      return False

    left_args = node.args
    right_args = temp.args
    if len(left_args) != len(right_args):
      print 'function arg count mismatch'
      return False

    for i in range(0, len(left_args)):
      self.current_right= right_args[i]
      if not self.visit(left_args[i]):
        print 'function arg mismatch'
        return False
    return True

  def visit_Name(self, node):
    if not isinstance(self.current_right, _ast.Name):
      print 'name mismatch'
      return False
    if node.id != self.current_right.id:
      print 'name id mismatch'
      return False
    return True

  def visit_Num(self, node):
    if not isinstance(self.current_right, _ast.Num):
      print 'number mismatch'
      return False
    if node.n != self.current_right.n:
      print 'number value mismatch'
      return False
    return True

  def visit_Attribute(self, node):
    if not isinstance(self.current_right, _ast.Attribute):
      print 'attribute mismatch'
      return False
    if node.attr != self.current_right.attr:
      print 'attr value mismatch'
      return False
    self.current_right = self.current_right.value
    return self.visit(node.value)

  def visit_Str(self, node):
    if not isinstance(self.current_right, _ast.Str):
      print 'string mismatch'
      return False
    if node.s != self.current_right.s:
      print 'string value mismatch'
      return False
    return True

  def visit_List(self, node):
    if not isinstance(self.current_right, _ast.List):
      print 'list mismatch'
      return False
    left_elements = node.elts
    right_elements = self.current_right.elts
    if len(left_elements) != len(right_elements):
      print 'list length mismatch'
      return False
    for i in range(0, len(left_elements)):
      self.current_right = right_elements[i]
      if not self.visit(left_elements[i]):
        print 'list member mismatch'
        return False
    return True

  def visit_Tuple(self, node):
    if not isinstance(self.current_right, _ast.Tuple):
      print 'tuple mismatch'
      return False
    left_elements = node.elts
    right_elements = self.current_right.elts
    if len(left_elements) != len(right_elements):
      print 'tuple length mismatch'
      return False
    for i in range(0, len(left_elements)):
      self.current_right = right_elements[i]
      if not self.visit(left_elements[i]):
        print 'tuple member mismatch'
        return False
    return True

  def visit_Dict(self, node):
    if not isinstance(self.current_right, _ast.Dict):
      print 'dict mismatch'
      return False

    temp = self.current_right

    left_keys = node.keys
    right_keys = temp.keys
    if len(left_keys) != len(right_keys):
      print 'dict length mismatch'
      return False
    for i in range(0, len(left_keys)):
      self.current_right = right_keys[i]
      if not self.visit(left_keys[i]):
        print 'dict key mismatch'
        return False

    left_values = node.values
    right_values = temp.values
    for i in range(0, len(left_values)):
      self.current_right = right_values[i]
      if not self.visit(left_values[i]):
        print 'dict value mismatch'
        return False
    return True

class ASTSimilarityChecker(ast.NodeVisitor):
  def get_similarity(self, item1, item2):
    if isinstance(item1, str):
      left_tree = parse(item1)
    else:
      left_tree = item1

    if isinstance(item2, str):
      right_tree = parse(item2)
    else:
      right_tree = item2

    self.left = []
    self.shared = []
    self.matcher = NodeMatcher(right_tree)

    self.visit(left_tree)

    S = len(self.shared)
    L = len(self.left)
    R = len(self.matcher.nodes)
    similarity = (2.0 * S) / (2.0 * S + L + R)
    return similarity

  def visit(self, node):
    self.generic_visit(node)
    if self.matcher.match(node):
      self.shared.append(node)
    else:
      self.left.append(node)

class NodeEnumerator(ast.NodeVisitor):
  def get_node_list(self, tree):
    self.nodes = []
    self.visit(tree)
    return self.nodes

  def visit(self, node):
    self.generic_visit(node)
    self.nodes.append(node)

class NodeMatcher():
  def __init__(self, right):
    enumerator = NodeEnumerator()
    self.nodes = enumerator.get_node_list(right)
    self.matched_nodes = []

  def match(self, target):
    match = None
    for node in self.nodes:
      if not isinstance(target, type(node)):
        continue
      elif hasattr(self, 'visit_' + type(node).__name__):
        method = getattr(self, 'visit_' + type(node).__name__)
        if method(node, target):
          match = node
      else:
        match = node

    if match is not None:
      self.matched_nodes.append(match)
      self.nodes.remove(match)
      return True
    return False

  def visit_Call(self, node, target):
    return node.func.id == target.func.id

  def visit_Num(self, node, target):
    return node.n == target.n

  def visit_Str(self, node, target):
    return node.s == target.s

class PredicateRandomizer(ast.NodeTransformer):
  def randomize(self):
    return bool(random.randint(0,1))

  def visit_Num(self, node):
    if self.randomize():
      number = random.random() * node.n
      return ast.copy_location(_ast.Num(n=number), node)
    else:
      return node

  def visit_Str(self, node):
    if self.randomize():
      n = len(node.s)
      s = ''.join(random.choice(string.ascii_uppercase + string.lowercase + string.digits) for x in range(n))
      return ast.copy_location(_ast.Str(s=s), node)
    else:
      return node

  def visit_Eq(self, node):
    if self.randomize():
      return ast.copy_location(_ast.NotEq(), node)
    else:
      return node

  def visit_NotEq(self, node):
    if self.randomize():
      return ast.copy_location(_ast.Eq(), node)
    else:
      return node

  def visit_In(self, node):
    if self.randomize():
      return ast.copy_location(_ast.NotIn(), node)
    else:
      return node

  def visit_NotIn(self, node):
    if self.randomize():
      return ast.copy_location(_ast.In(), node)
    else:
      return node

  def visit_Gt(self, node):
    return self.get_random_comparator(node)

  def visit_GtE(self, node):
    return self.get_random_comparator(node)

  def visit_Lt(self, node):
    return self.get_random_comparator(node)

  def visit_LtE(self, node):
    return self.get_random_comparator(node)

  def get_random_comparator(self, node):
    if self.randomize():
      comp = random.randint(1,4)
      if comp == 1:
        op = _ast.Lt()
      elif comp == 2:
        op = _ast.LtE()
      elif comp ==  3:
        op = _ast.Gt()
      else:
        op = _ast.GtE()
      return ast.copy_location(op, node)
    else:
      return node

  def visit_Tuple(self, node):
    if self.randomize():
      elements = [self.visit(node.elts[0])]
      for element in node.elts[1:]:
        if self.randomize():
          elements.append(self.visit(element))
      if self.randomize():
        for element in node.elts:
          if self.randomize():
            elements.append(self.visit(element))
      return ast.copy_location(_ast.Tuple(elts=elements), node)
    else:
      return node

  def visit_BoolOp(self, node):
    if self.randomize():
      if self.randomize():
        op = ast.And()
      else:
        op = ast.Or()
      values = []
      for value in node.values:
        values.append(self.visit(value))
      return ast.copy_location(_ast.BoolOp(op=op, values=values), node)
    else:
      return node

  def visit_Name(self, node):
    if self.randomize():
      if node.id == 'forall':
        return ast.copy_location(_ast.Name(id='exists'), node)
      elif node.id == 'exists':
        return ast.copy_location(_ast.Name(id='forall'), node)
    return node

def parse_predicate_set(string_set):
  tree_set = []
  for string in string_set:
    tree_set.append(parse(string))
  return tree_set

def pre_process_ast_set(ast_set):
  tree_set = []
  for item in ast_set:
    if isinstance(item.body, _ast.BoolOp):
      for subtree in item.body.values:
        expression = _ast.Expression()
        expression.body = subtree
        tree_set.append(expression)
    else:
      tree_set.append(item)
  return tree_set

def compare_predicate_sets(set1, set2):
  temp_set1 = parse_predicate_set(set1)
  temp_set2 = parse_predicate_set(set2)
  tree_set1 = pre_process_ast_set(temp_set1)
  tree_set2 = pre_process_ast_set(temp_set2)

  temp_tree_set2 = []
  for tree in tree_set2:
    temp_tree_set2.append(tree)

  checker = ASTSimilarityChecker()
  similarities = {}
  matches = {}
  for tree1 in tree_set1:
    for tree2 in temp_tree_set2:
      sim = checker.get_similarity(tree1, tree2)
      if sim >= PREDICATE_SIMILARITY_THRESHOLD:
        prev_sim = similarities.get(tree1)
        if prev_sim is None or sim > prev_sim:
          similarities[tree1] = sim
          matches[tree1] = tree2
    if matches.has_key(tree1):
      temp_tree_set2.remove(matches[tree1])

  S = len(similarities)
  L = len(tree_set1) - S
  R = len(tree_set2) - S
  if S + L + R == 0:
    return -1
  else:
    return (2.0 * S) / (2.0 * S + L + R)

def compare_operations(api1, op1, api2, op2):
  methods = sorted([op1.method, op2.method])
  if methods[0] == methods[1] or methods == ['GET','POST'] or methods == ['POST','PUT']:
    sim1 = compare_predicate_sets(op1.get_pre_conditions(api1), op2.get_pre_conditions(api2))
    sim2 = compare_predicate_sets(op1.get_post_conditions(api1), op2.get_post_conditions(api2))
    print sim1, sim2
    if sim1 >= PREDICATE_SET_SIMILARITY_THRESHOLD and sim2 >= PREDICATE_SET_SIMILARITY_THRESHOLD:
      return True
    elif sim1 >= PREDICATE_SET_SIMILARITY_THRESHOLD and sim2 == -1:
      return True
    elif sim1 == -1 and sim2 >= PREDICATE_SET_SIMILARITY_THRESHOLD:
      return True
  return False

def randomize_predicate(predicate):
  randomizer = PredicateRandomizer()
  tree = randomizer.visit(parse(predicate))
  return ast2code.to_source(tree)

def randomize_operation(api_def, op):
  if op.input and op.input.type:
    data_type = op.input.type.type
    if isinstance(data_type, api.CustomTypeRef):
      type_def = api_def.get_type_by_name(data_type.get_reference_name())
      constraints = []
      for constraint in type_def.constraints:
        randomize = random.randint(0,2) == 1
        if randomize:
          constraints.append(randomize_predicate(constraint))
        else:
          constraints.append(constraint)
      type_def.constraints = constraints

  if op.output.type:
    data_type = op.output.type.type
    if isinstance(data_type, api.CustomTypeRef):
      type_def = api_def.get_type_by_name(data_type.get_reference_name())
      constraints = []
      for constraint in type_def.constraints:
        randomize = random.randint(0,2) == 1
        if randomize:
          constraints.append(randomize_predicate(constraint))
        else:
          constraints.append(constraint)
      type_def.constraints = constraints

  requires = []
  for condition in op.requires:
    randomize = random.randint(0,2) == 1
    if randomize:
      requires.append(randomize_predicate(condition))
    else:
      requires.append(condition)
  op.requires = requires

  ensures = []
  for condition in op.ensures:
    randomize = random.randint(0,2) == 1
    if randomize:
      ensures.append(randomize_predicate(condition))
    else:
      ensures.append(condition)
  op.ensures = ensures
  return op

def randomize_api(api_def, name, output_dir):
  api_def.name = name
  for resource in api_def.resources:
    for op in resource.operations:
      randomize_operation(api_def, op)
  if not os.path.exists(output_dir):
    os.mkdir(output_dir)
  output = open(os.path.join(output_dir, name + '.json'), 'w')
  output.write(api_def.serialize_json())
  output.close()

def compare_predicates(p1, p2):
  checker = ASTSimilarityChecker()
  return checker.get_similarity(p1,p2)

if __name__ == '__main__':
#  for i in range(0, 100):
#    api_def = api.parse('/Users/hiranya/Projects/api-desc/sandbox/jaxrs-test/starbucks/starbucks3.json')
#    randomize_api(api_def, 'random' + str(i), '/Users/hiranya/Projects/api-desc/sandbox/jaxrs-test/random')
#  print 'DONE'

  k = 1
  api1 = api.parse('/Users/hiranya/Projects/api-desc/sandbox/jaxrs-test/starbucks/starbucks3.json')
  for i in [90]:
    api2 = api.parse('/Users/hiranya/Projects/api-desc/sandbox/jaxrs-test/random/random' + str(i) + '.json')
    for resource1 in api1.resources:
      for op1 in resource1.operations:
        for resource2 in api2.resources:
          for op2 in resource2.operations:
            print
            for c in op1.get_pre_conditions(api1):
              print c

            print
            for c in op2.get_pre_conditions(api2):
              print c

            print
            for c in op1.get_post_conditions(api1):
              print c

            print
            for c in op2.get_post_conditions(api2):
              print c
            if compare_operations(api1, op1, api2, op2):
              print k, api1.name, api2.name, '- Match ****************'
              k += 1