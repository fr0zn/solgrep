from tree_sitter import Language, Parser

def format_sexp(sexp):
  _indentation = 0
  _chunk = ""
  for i,element in enumerate(sexp):
    if element == '(':
      print("\n{}{}".format(' '*_indentation, _chunk), end='')
      _chunk = ""
      _indentation += 1
    if element == ')':
      print(')', end='')
      #print("{}{}".format(' '*_indentation, _chunk))
      #_chunk = ""
      _indentation -= 1
    _chunk += element
  print() 


Language.build_library(
  # Store the library in the `build` directory
  'build/my-languages.so',

  # Include one or more languages
  [
    '.',
  ]
)

SOLIDITY_LANGUAGE = Language('build/my-languages.so', 'solidity')

parser = Parser()
parser.set_language(SOLIDITY_LANGUAGE)

_content = open('test.sol').read()
_query_content = open('query.sol').read()
tree = parser.parse(bytes(_content, 'utf8'))

# format_sexp(tree.root_node.sexp())

print('--------------------')

identifiers = {}

def print_node(node):
    pos_point = f"[{node.start_point},{node.end_point}]"
    pos_byte = f"({node.start_byte},{node.end_byte})"
    print(
        f"{repr(node.type):<25}{'is_named' if node.is_named else '-':<20}"
        f"{pos_point:<30}{pos_byte}"
    )
  

def parse_identifiers(node, scope):
  # print_node(node)
  _name = _query_content[node.start_byte:node.end_byte]
  if _name not in identifiers:
    identifiers[_name] = scope

def traverse(tree):
    scope = 0
    def _traverse(node, scope):
        if node.type == 'identifier':
          parse_identifiers(node, scope)
  
        scope += 1
        for child in node.children:
            _traverse(child, scope)
        scope -= 1

    _traverse(tree.root_node, scope)

query_tree = parser.parse(bytes(open('query.sol').read(), "utf8"))

query_cursor = query_tree.root_node.walk()
# actual pattern

traverse(query_tree)

print(identifiers)

# import sys
# sys.exit(1)

#query_cursor.goto_first_child()
query_sexp = ''.join([child.sexp() + '@child{}'.format(i) for i,child in enumerate(query_cursor.node.children)])
query_sexp = '('  + query_sexp + ')'

# format_sexp(query_sexp)

query_sexp = "{}".format(query_sexp).replace('(ellipsis)','')

print(query_sexp)

query_sexp = '''((function_definition function_name: (identifier) body: (function_body (variable_declaration_statement (variable_declaration (type_name (primitive_type)) name: (identifier)) ) (expression_statement (call_expression (identifier) )) (return_statement (identifier))))@child0)'''

query = SOLIDITY_LANGUAGE.query(query_sexp)

captures = query.captures(tree.root_node)

# _content_lines = _content.split('\n')

for capture in captures:
  print('========================')
  print(capture)
  print('========================')
  c = capture[0]
  print(c)
  print('-------------------------')
  print(_content[c.start_byte:c.end_byte])


#cursor = tree.walk()

c = captures[0][0]
