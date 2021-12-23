from sys import meta_path
from solquery_compare import compare_levels
from tree_sitter import Language, Parser
from anytree import RenderTree, NodeMixin,PreOrderIter,LevelOrderGroupIter
from anytree.exporter import DotExporter,UniqueDotExporter
from jinja2 import Template
from jinja2.filters import FILTERS
import json
import yaml
import re

def sexp_format(sexp):
    _str = ''
    _indent = -1
    _inspace = False
    _inbraket = False
    for c in sexp:
        if c == '(':
            _indent += 1
            _inspace = False
            _inbraket = True
        elif c == ')':
            if not _inbraket:
                _str += ' '*_indent
            _str += ')\n'
            _indent -= 1
            _inbraket = False
            continue
        elif c == ' ':
            if not _inspace:
                if _inbraket:
                    _str += '\n'
                _str += ' '*_indent
                _inspace = True
        _str += c

    return _str

class TreePattern(NodeMixin):
    def __init__(self, type, pattern=None, parent=None, children=None):
        super(TreePattern, self).__init__()
        self.name = "{}-{}".format(type, pattern.__repr__())
        self.type = type
        self.pattern = pattern

        self.states = []

        self.parent = parent
        if children:
            self.children = children

    def uppropagate(self):
        self.parent.states = self.states

    def downpropagate(self):
        self.states = self.parent.states

    def __repr__(self):
        return self.__str__()

    def sexp(self):
        return self.type

    def __str__(self):
        return "'{}'".format(self.name)

class TreeNode(NodeMixin):
    def __init__(self, type, node, content, parent=None, children=None):
        super(TreeNode, self).__init__()
        self.name = "{}".format(type)
        self.type = type
        self.node = node
        self.parent = parent
        self.is_named = node.is_named if node else False
        self.is_ellipsis = False
        self.is_comma = False
        self.is_comment = False
        self.content = content
        if children:
            self.children = children


    # def getcontent(self, start=0, end=-1):
    #     if end == -1:
    #         end = len(self.__content)
    #     return self.__content[start:end].decode("utf-8")

    # content=property(getcontent)

    def __repr__(self):
        return self.__str__()

    def sexp(self):
        return self.type


    def __str__(self):
        # return str(self.node)
        # if len(self.children) == 0:
        #     return "{} - '{}'".format(self.content, self.name)
        # else:
        return "'{}'".format(self.name)

class TreeRoot():
    def __init__(self, _content, _root):

        self.root = None

        self._root = _root
        self._src = _content

        self._sexp = ''
        self.rules = []

        self._prepare_traverse()

    def get_sexp(self, filters=[]):
        _sexp = ''
        def _traverse_sexp(node):
            nonlocal _sexp
            if node.type not in filters and node.is_named:
                _sexp += '('
                _sexp += "{} ".format(node.type)
                for child in node.children:
                    _traverse_sexp(child)
                _sexp += ')'
        _traverse_sexp(self.root)
        return _sexp

    def filter_type(self, filterTypes):
        sexp = self.get_sexp(filters=filterTypes)
        return sexp

    def _parse_node(self, _node, _last_parent):
        node = TreeNode(_node.type, _node, self._src[_node.start_byte:_node.end_byte], parent=_last_parent)
        if _node.type == 'ellipsis':
            node.is_ellipsis = True
        elif _node.type == ',':
            node.is_comma = True
        elif _node.type == 'comment':
            node.is_comment = True

        if self.root == None:
            self.root = node

        return node

    def _prepare_traverse(self):
        last_parent = None
        def _traverse(node, last_parent):
            last_parent = self._parse_node(node, last_parent)
            for child in node.children:
                _traverse(child, last_parent)
        _traverse(self._root, last_parent)

    def __str__(self):
        return str(RenderTree(self.root))

    def dot(self):
        UniqueDotExporter(self.root).to_picture("TreeRoot.png")

    def __repr__(self) -> str:
        return "{} ...".format(self.root.content[:10])

    # def __repr__(self) -> str:
    #     return self.__str__()

# class MetaVar():
#     def __init__(self, node):
#         self.node = node
#         self.value = None

#     def __repr__(self):
#         return "{}({})".format(self.node.content, self.value)

def decode_convert(data):
    if isinstance(data, bytes):  return data.decode('ascii')
    if isinstance(data, dict):   return dict(map(decode_convert, data.items()))
    if isinstance(data, tuple):  return map(decode_convert, data)
    return data

def format_list(_list, pattern='{}', endline='\n'):
    return endline.join([pattern.format(s) for s in _list])

def pluralize(list, singular = '', plural = 's'):
    if len(list) > 1:
        return plural
    else:
        return singular

FILTERS['pluralize'] = pluralize
FILTERS['format_list'] = format_list
class QueryRule():
    def __init__(self, id, message, risk, impact):
        self.id = id
        self.message = Template(message)
        self.risk = risk
        self.impact = impact


    def _format_message_meta(self, metavars):
        return self.message.render(metavars)

    def report(self, matched_queries):
        if len(matched_queries) == 0:
            return {}
        _metavars = {}
        _bytesranges = []
        _linesranges = []
        for query in matched_queries:
            _bytesranges.append(query.get_bytes_range())
            _linesranges.append(query.get_range())
            for key, value in query.meta_vars.items():
                # TODO: Assume meta with $
                key = key[1:]
                _metavars[key.decode('ascii')] = _metavars.get(key.decode('ascii'),[]) + [value.decode('ascii')]

            for cquery in query.children:
                for key, value in cquery.meta_vars.items():
                    # TODO: Assume meta with $
                    key = key[1:]
                    _metavars[key.decode('ascii')] = _metavars.get(key.decode('ascii'),[]) + [value.decode('ascii')]

            if query.parent is not None:
                for pquery in query.parent.children:
                    for key, value in pquery.meta_vars.items():
                        # TODO: Assume meta with $
                        key = key[1:]
                        _metavars[key.decode('ascii')] = _metavars.get(key.decode('ascii'),[]) + [value.decode('ascii')]

        _data = {
            'id': self.id,
            'message': self._format_message_meta(_metavars),
            'risk': self.risk,
            'impact': self.impact,
            'results': len(matched_queries),
            'metavars': _metavars,
            'bytesrange': _bytesranges,
            'linesrange': _linesranges
        }
        return _data
        # return json.dumps(_data)


class QueryStates(NodeMixin):
    query_state_id = 0
    def __init__(self, parent):
        self.meta_vars = {}
        self.is_match = False
        self._matched_nodes = []
        self._is_skip = False
        self._added_meta = []

        self.id = QueryStates.query_state_id
        # Used for and queries
        # self.parent_states = []
        # Used for not queries
        # self.child_states = []

        # self.child = []

        self.parent = parent

        QueryStates.query_state_id += 1


    def __eq__(self, other):
        return self.id == other.id

    def get_root(self):
        return self._matched_nodes[0].parent

    def get_range(self):
        if len(self._matched_nodes) > 0:
            return (
                self._matched_nodes[0].node.start_point,
                self._matched_nodes[-1].node.end_point,
                )
        else:
            return (0, -1)

    def get_bytes_range(self):
        if len(self._matched_nodes) > 0:
            return (
                self._matched_nodes[0].node.start_byte,
                self._matched_nodes[-1].node.end_byte,
                )
        else:
            return (0, -1)

    def __repr__(self) -> str:
        _last = ' '.join([str(x.content.decode('utf8')) for x in self._matched_nodes])[:20] + '...'
        return '{} - {} - {} - {}'.format(self.id, self.is_match, self.meta_vars, _last)


class SolidityQuery():

    def __init__(self):
        self._build_load_library()
        self.parser = Parser()
        self.parser.set_language(self.SOLIDITY_LANGUAGE)

        self.src = None
        # self.queries = None

        self.patterns = None
        self.root_state = None

        self.current_state = None

        # list of QueryStates()
        self.query_states = []

        self.metaRules = {}

        self.rule = None

    def _build_load_library(self):
        Language.build_library('build/solidity.so',[ '.' ])
        self.SOLIDITY_LANGUAGE = Language('build/solidity.so', 'solidity')

    def _parse_file(self, fileName):
        _content = bytes(open(fileName).read().strip(), 'utf8')
        # Append and prepend ellipsis to the query
        # _content = '...\n' + _content + '\n...'
        # _content = _content + '\n...'
        return (_content, self.parser.parse(_content))

    def load_source_string(self, string):
        _content = bytes(string.strip(), 'utf8')
        _tree = self.parser.parse(_content)
        self.src = TreeRoot(_content, _tree.root_node)
        return self.src

    def load_query_string(self, string):
        _content = bytes(string.strip(), 'utf8')
        _tree = self.parser.parse(_content)
        query = TreeRoot(_content, _tree.root_node)
        return query
        # self.queries = TreeRoot(_content, _tree.root_node)
        # return self.queries

    def load_source_file(self, fileName):
        _content, _tree = self._parse_file(fileName)
        # TODO: Checks MISSING ERROR
        self.src = TreeRoot(_content, _tree.root_node)
        return self.src

    def load_query_yaml_string(self, data):
        _data = yaml.safe_load(data)
        self._parse_query_yaml(_data)

    def load_query_yaml_file(self, fileName):
        with open(fileName, "r", encoding='utf-8') as stream:
            try:
                self.load_query_yaml_string(stream)
            except yaml.YAMLError as exc:
                print(exc)
                raise ValueError('Invalid YAML')
        # TODO: Checks MISSING ERROR
        # return self.queries


    def load_query_file(self, fileName):
        _content, _tree = self._parse_file(fileName)
        # TODO: Checks MISSING ERROR
        root = TreePattern(type="patterns")
        TreePattern(type='pattern', parent=root, pattern=TreeRoot(_content, _tree.root_node))
        self.patterns = root
        return self.patterns

    def _parse_query_yaml_patterns(self, root, data):
        if isinstance(data, list):
            for level in data:
                self._parse_query_yaml_patterns(root, level)
        elif isinstance(data, dict):
            _root = root
            for i,(k,v) in enumerate(data.items()):
                if k == 'pattern' and i != 0:
                    raise ValueError('Pattern type must be the first item')
                # if k in 'pattern':
                #     _root = TreePattern(type=k, parent=_root, pattern=self.load_query_string(v))
                # else:
                if isinstance(v, list):
                    _root = TreePattern(type='{}-either'.format(k), parent=_root, pattern=None)
                else:
                    # if optional['ineither']:
                    #     TreePattern(type='{}-either'.format(k), parent=_root, pattern=self.load_query_string(v))
                    # else:
                    _root = TreePattern(type=k, parent=_root, pattern=self.load_query_string(v))
                self._parse_query_yaml_patterns(_root, v)

    def _parse_query_yaml(self, _data):
        print(_data)
        for req in ['message', 'id', 'risk', 'impact']:
            if req not in _data:
                raise ValueError('Missing {} on the query file'.format(req))
        patterns = []
        self.rule = QueryRule(_data['id'], _data['message'], _data['risk'], _data['impact'])
        # Single pattern
        root = TreePattern(type="patterns")
        if 'pattern' in _data:
            _query = self.load_query_string(_data['pattern'])
            TreePattern(type='pattern', parent=root, pattern=self.load_query_string(_query))
            # patterns.append(('pattern',_query))
        elif 'patterns' in _data:
            self._parse_query_yaml_patterns(root, _data['patterns'])

        self.patterns = root

        #     _patterns = [list(p.items())[0] for p in _data['patterns']]
        #     for i,type_pattern in enumerate(_patterns):
        #         _type, _pattern = type_pattern
        #         if i == 0 and _type != 'pattern':
        #             raise ValueError('Patterns should start with "pattern" query')
        #         _query = self.load_query_string(_pattern)
        #         patterns.append((_type, _query))
        # print(patterns)

        if 'metavars-regex' in _data:
            self.preload_meta(_data['metavars-regex'])

        # self.queries = patterns


    def _is_skip(self):
        return self.current_state._is_skip

    def _after_skip(self):
        for added in self.current_state._added_meta:
            self.current_state.meta_vars.pop(added)
        self.current_state._added_meta = []

    def _is_match(self, node):
        self.current_state._matched_nodes.append(node)
        self.current_state._added_meta = []

    def _add_meta_compare(self, _metavar, _content):
        # _metavar = searchNode.content
        # _content = compareNode.content
        # This means there is a preloaded rule
        if _metavar == b'$_':
            return True

        if _metavar not in self.current_state.meta_vars:
            self.current_state._added_meta.append(_metavar)
            self.current_state.meta_vars[_metavar] = _content
            if _metavar in self.metaRules:
                return bool(re.search(self.metaRules[_metavar], _content))
            return True
        else:
            # The node is equal if the metavar is the same
            return bool(re.search(self.current_state.meta_vars[_metavar], _content))
            # TODO: Check if okay
            # If the metavar is preloaded, store the content to it if match


    ######################################

    def _compare_content(self, searchNode, compareNode, args):
        # _starts = args['starts']
        # _skip = args.get('skip', False)
        # True if both identifiers are the same
        return searchNode.content == compareNode.content

    def _compare_identifier(self, searchNode, compareNode, args):
        _starts = args['starts']
        _skip = args.get('skip', False)
        if _skip:
            self.current_state._is_skip = True
        if searchNode.content.startswith(_starts):
            return self._add_meta_compare(
                searchNode.content,
                compareNode.content
            )
        # True if both identifiers are the same
        return searchNode.content == compareNode.content

    def _compare_strings(self, searchNode, compareNode, args):
        # Removes ' and "
        _merged_search = ''.join([c.content[1:-1].decode('utf8') for c in searchNode.children if c.type != 'comment'])
        _merged_compare = ''.join([c.content[1:-1].decode('utf8') for c in compareNode.children if c.type != 'comment'])
        self.current_state._is_skip = True
        if _merged_search.startswith('$STRING'):
           return self._add_meta_compare(
                bytes(_merged_search,'utf8'),
                bytes(_merged_compare, 'utf8')
            )
        return bool(re.search(_merged_search, _merged_compare))


    def _compare_default(self, searchNode, compareNode, args):
        if searchNode.type == compareNode.type:
            # print('TRUE', searchNode.type, compareNode.type)
            # return searchNode.content == compareNode.content
            return True
        else:
            # print('DIFF', searchNode.type, compareNode.type)
            return False

    def _compare_expression(self, searchNode, compareNode, args):
        if searchNode.type == 'expression_statement':
            print(searchNode.children)
            print(searchNode.children)
            print(searchNode.children)
            print(searchNode.children)
            return False


    # Search node -> Compare Node -> (handler, data)

    def _compareNodes(self, searchNode, compareNode):
        SOLIDITY_NODES = {
            # ('ellipsis', 'ellipsis'): (lambda x: True, None),
            # ('contract_declaration', 'contract_declaration'): (lambda x: True, None),
            # ('contract_body', 'contract_body'): (lambda x: True, None),
            # ('state_variable_declaration', 'state_variable_declaration'): (lambda x: True, None),
            ('identifier', 'identifier')                          : (self._compare_identifier, {'starts':b'$'}),
            ('identifier', 'number_literal')                      : (self._compare_identifier, {'starts':b'$'}),
            ('primitive_type', 'primitive_type')                  : (self._compare_identifier, {'starts':b'$TYPE', 'skip':True}),
            ('visibility', 'visibility')                          : (self._compare_identifier, {'starts':b'$VISIBILITY', 'skip':True}),
            ('state_mutability', 'state_mutability')              : (self._compare_identifier, {'starts':b'$STATE'}),
            ('storage_location', 'storage_location')              : (self._compare_identifier, {'starts':b'$STORAGE'}),
            ('pragma_versions', 'pragma_versions')                : (self._compare_identifier, {'starts':b'$VERSION', 'skip':True}),
            ('experimental_directives', 'experimental_directives'): (self._compare_identifier, {'starts':b'$EXPERIMENTAL'}),
            ('string_literal', 'string_literal')                  : (self._compare_strings, {}),
            ('number_literal', 'number_literal')                  : (self._compare_content, {}),
            # If we have an expression_statement
            ('expression_statement', 'binary_expression')         : (self._compare_expression, {}),
        }
        self.current_state._is_skip = False

        _fnc, _data = SOLIDITY_NODES.get(
            (searchNode.type, compareNode.type),
            (self._compare_default, {})
            )

        _result =  _fnc(searchNode, compareNode, _data)
        return _result
        if _result == False:
            # print('NOO:')
            print(searchNode, compareNode)
        else:
            # print('YES:')
            print(searchNode, compareNode)

        return _result

    def _do_query(self, srcRoot, node, state, parent=None):
        _type = node.type
        query = node.pattern
        # _type = node.type
        # this_query_states = []
        # ellipsis_node = TreeNode('ellipsis', None, '...')
        # commaNode = TreeNode(',', None, ',')
        # We are getting the firs rule of the query as an start point
        # If we find any we will get the parent, and pre/appended ellipsis
        # during query load will do the rest
        query_first_rule = None
        # Skip until the find the first rule of the query that is not an ellipsis
        for child in query.root.children:
            if not child.is_ellipsis:
            # if not self._compareNodes(child, ellipsis_node):
                query_first_rule = child
                break

        _single_statement = False
        _did_any_match = False
        for src_node in PreOrderIter(srcRoot):
            # The new state is a child of the parent state
            self.current_state = QueryStates(state)
            # print('============= CHECKING NODES ================')
            # print(src_node)
            # print(query_first_rule)
            # print('===========')
            # if src_node.type == query_first_rule.type:
            if self._compareNodes(query_first_rule, src_node):
                # This is done because we want to support multistatment
                # with ellipsis. So we betch a common root branch that contains
                # the first found rule and allows ellipis skipping
                if _single_statement:
                    _src_parent = src_node
                    _query_parent = query.root.children[0]
                    _srcIndexStart = 0
                else:
                    _src_parent = src_node.parent
                    _query_parent = query.root
                    _srcIndexStart = _src_parent.children.index(src_node)
                # print('=========== SRC TREE ============')
                # print(str(RenderTree(_src_parent)))
                # print('=========== SRC CONTENT ============')
                # print(src_node.content)
                # print()
                # print('=========== QUERY TREE ============')
                # print(query)
                # print('=========== QUERY CONTENT ============')
                # print(query.root.content)
                # We are queriying using the full queries root content
                # We use the parent of the found src node for the first query
                # rule but skipped n times, where n is the index of the found
                # child
                _match = compare_levels(_src_parent, _query_parent,
                        # ellipsisNode=ellipsis_node,
                        # commaNode=commaNode,
                        compareFunction=self._compareNodes,
                        srcIndexStart=_srcIndexStart,
                        isSkipFunction=self._is_skip,
                        afterSkipFunction=self._after_skip,
                        isMatchFunction=self._is_match,
                        # data=self.query_data[self.query_index]
                        # metaVars=self.query_metavars[self.query_index],
                        )
                if _match:
                    _did_any_match = True
                    self.current_state.is_match = True
                # self.current_state.is_match = _match
                # self.query_states.append(self.current_state)
                if _type == 'pattern':
                    # inside and-either or not-either
                    if state and parent:
                        if parent.type == 'and-either':
                            if _match:
                                state.is_match = True
                                self.query_states.append(self.current_state)
                            # else:
                            #     del self.current_state
                        elif parent.type == 'not-either':
                            state.is_match = _match
                    if _match:
                        # this_query_states.append(self.current_state)
                        self.query_states.append(self.current_state)
                        # node.states.append(self.current_state)

                elif _type == 'not':
                    # print('BEFOREEEE', self.query_states)
                    if _match:
                        state.is_match = False
                        self.query_states.append(self.current_state)
                        # self.query_states.remove(_parent_state)
                        break
                    # print('AFTEREERRR', self.query_states)
                elif _type == 'and':
                    # _parent_state = _data['state']
                    # If we found a submatch for the and, the parent is a match
                    state.is_match = _match
                    # self.query_states.append(self.current_state)
                    # if _match:
                        # self.current_state.is_match = True
                        # self.current_state.parent_states.append(_parent_state)
                        # self.query_states.append(self.current_state)

                print('=========== MATCH ============')
                print(_match)
                # print(this_query_states)
                print('==============================')
                # break

        # After all nodes are searched
        # If the pattern is and and no match was found, then the parent should be ignored
        if _type == 'and':
            if not _did_any_match:
                state.is_match = False
        print()
                # print(_start, _end)
                # print('-------------')
                # print(self.src.root.content[_start:_end])
                # print('-------------')
                # print(query_result.meta_vars)

        # print([x.is_match for x in self.query_states])
        # print([x._matched_nodes for x in self.query_states])
        print('=============')
        # return this_query_states
        # return self.query_states

    def slash_match(self, state_tree, is_match):
        _childrens = []
        for s in state_tree.children:
            if s.is_match == is_match:
                _childrens.append(s)
        state_tree.children = _childrens


    def query(self):
        print(RenderTree(self.patterns))

        def _traverse(parent):
            def _process_node(current_pattern):
                print(current_pattern)
                _type = current_pattern.type
                if _type == 'pattern':
                    if current_pattern.depth == 1:
                        self._do_query(self.src.root, current_pattern, self.root_state)
                        # parent.states.extend(self.query_states)
                        # current.states = parent.states
                        # current.states = self.current_state
                        self.slash_match(self.root_state, True)
                        # current.states = parent.states
                        parent.states = self.query_states.copy()
                        current_pattern.states = self.query_states.copy()
                        # current.states = [s for s in self.query_states if s.is_match]
                    else:
                        if parent.type not in ['and-either', 'not-either']:
                            raise ValueError('Not implemented states for parent {}'.format(parent.type))

                        _new_level_childs = []
                        for s in parent.states:
                            self.query_states = []
                            _newTree = QueryStates(s)
                            if parent.type == 'and-either':
                                _newTree.is_match = False
                                # s.is_match = False
                            # _newTree.is_match = True
                            self._do_query(s.get_root(), current_pattern, _newTree, parent=parent)
                            self.slash_match(_newTree, True)
                            _new_level_childs.extend(_newTree.children)

                        current_pattern.states = _new_level_childs
                        # current.states.children = [s for s in _remaining_states if s.is_match]
                        # print(current.states.children)
                elif _type == 'and':
                    # self.query_states = []
                    for s in parent.states:
                        self._do_query(s.get_root(), current_pattern, s)
                        self.slash_match(s, True)
                    # current.states = parent.states
                    # current.states = self.query_states
                elif _type == 'not':
                    # self.query_states = []
                    for s in parent.states:
                        self._do_query(s.get_root(), current_pattern, s)
                        self.slash_match(s, True)
                    # current.states = parent.states
                    # current.states = self.query_states
                elif _type == 'and-either':
                    # for s in parent.states.children:
                    #     s.is_match = False
                    current_pattern.states = parent.states

                elif _type == 'not-either':
                    current_pattern.states = parent.states

            if len(parent.children) > 0:
                for current in parent.children:
                    _process_node(current)
                    _traverse(current)

        self.root_state = QueryStates(None)
        _traverse(self.patterns)

        print(RenderTree(self.root_state))

        def _delete_node(node):
            if node != node.root:
                _old_parent = node.parent
                node.parent = None
                # If we remove this node and no more childs, 
                # propagete up the parent deletion
                if len(_old_parent.children) == 0:
                    _delete_node(_old_parent)

        # Filter only full true branches, if any node is False remove the entire branch
        for n in PreOrderIter(self.root_state):
            if not n.is_match:
                _delete_node(n)

        print(RenderTree(self.root_state))

        # print(sexp_format(query_sexp))
        # captures = query.captures(self.src_treecontent.root)
        # self._parse_captures_with_meta(captures)
        # return captures

    def report(self):
        _all_report = []

        _matched_queries = [query for query in self.root_state.children if query.is_match]

        # Parsed a yaml rule
        print('================= RESULTS ==================')
        for query_result in _matched_queries:
            _start, _end = query_result.get_bytes_range()
            print('''============================
Content {} - {}:

{}

'''.format(_start, _end, self.src.root.content[_start:_end].decode('utf8'), query_result.meta_vars))

        return self.rule.report(_matched_queries)

    def preload_meta(self, metaRules):
        print(metaRules)
        new_data = { bytes(key, 'utf8'): bytes(val, 'utf8') for key, val in metaRules.items() }
        self.metaRules = new_data


if __name__ == '__main__':
    import sys
    sq = SolidityQuery()
    sq.load_source_file('test.sol')
    # if len(sys.argv) > 1:
    #     sq.load_query_yaml_file('query.yaml')
    # else:
    #     sq.load_query_file('query.sol')

    sq.load_query_yaml_file('query.yaml')

    # t.dot()

    # print(t)
    # for q in qs:
    #     print(q)
    #     print(q.get_sexp())
    #     print(q.metavars)

    # sq.preload_meta({
    #     b'$VISIBILITY': b'^((?!public).)*$'
    # })

    sq.query()
    _report = sq.report()

    print(_report)

    # if sys.argv[1] == 'swc':
    #     SWC = sys.argv[2]
    #     print('SWC {} written'.format(SWC))

    #     src = open('test.sol').read()
    #     query = open('query.yaml').read()

    #     open('SWC/swc-{}.report'.format(SWC),'w').write(json.dumps(_report))
    #     open('SWC/swc-{}.sol'.format(SWC),'w').write(src)
    #     open('SWC/swc-{}.yaml'.format(SWC), 'w').write(query)
