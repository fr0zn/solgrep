from solquery_compare import compare_levels
from tree_sitter import Language, Parser
from anytree import RenderTree, NodeMixin,PreOrderIter,LevelOrderGroupIter
from anytree.exporter import DotExporter,UniqueDotExporter
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

class TreeNode(NodeMixin): 
    def __init__(self, type, node, content, parent=None, children=None):
        super(TreeNode, self).__init__()
        self.name = "{}".format(type)
        self.type = type
        self.node = node
        self.content = content
        self.parent = parent
        self.is_named = node.is_named if node else False
        self.is_meta = False
        if children:
            self.children = children
    
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

        # self.metavars = {}

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
        if self.root == None:
            self.root = node
        # if node.type == 'identifier':
        #     _identifier = node.content
        #     if _identifier.startswith('$'):
        #         node.is_meta = True
        #         if _identifier not in self.metavars: 
        #             self.metavars[_identifier] = None #MetaVar(node)
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
    
    # def __repr__(self) -> str:
    #     return self.__str__()

# class MetaVar():
#     def __init__(self, node):
#         self.node = node
#         self.value = None
    
#     def __repr__(self):
#         return "{}({})".format(self.node.content, self.value)

class SolidityQuery():
    def __init__(self):
        self._build_load_library()
        self.parser = Parser()
        self.parser.set_language(self.SOLIDITY_LANGUAGE)

        self.src = None
        self.queries = None

        # A dictionary of META keys and values
        self.query_metavars = []
        self.query_metavars_index = 0

    def _build_load_library(self):
        Language.build_library('build/solidity.so',[ '.' ])
        self.SOLIDITY_LANGUAGE = Language('build/solidity.so', 'solidity')

    def _parse_file(self, fileName):
        _content = open(fileName).read()
        # Append and prepend ellipsis to the query
        # _content = '...\n' + _content + '\n...'
        # _content = _content + '\n...'
        return (_content, self.parser.parse(bytes(_content, 'utf8')))

    def load_source(self, fileName):
        _content, _tree = self._parse_file(fileName)
        # TODO: Checks MISSING ERROR
        self.src = TreeRoot(_content, _tree.root_node)
        return self.src

    def load_query(self, fileName):
        _content, _tree = self._parse_file(fileName)
        # TODO: Checks MISSING ERROR
        self.queries = TreeRoot(_content, _tree.root_node)
        return self.queries
    
    # def _parse_query(self, query_root):
    #     for query_node in PreOrderIter(query_root):
    #         if query_node.type == 'identifier':
    #             _content = query_node.content
    #             if query_node.content not in self.metavars:
    #                 self.metavars[_content] = None #MetaVar(query_node)
    #         # print(_content)

    # def get_node_content(self, node, src):
    #     return src[node.start_byte:node.end_byte]
    
    # def _parse_captures(self, capture):
    #     self.src
    #     print(capture)

    def _compareNodes(self, searchNode, compareNode, added_meta):
        # The compareNode can be an ellipsis
        if searchNode.type == compareNode.type:
            _gtype = searchNode.type
            if _gtype == 'ellipsis':
                return True
            elif _gtype == 'identifier':
                # If the search content starts with $, thats a METAVAR
                if searchNode.content.startswith('$'):
                    _metavar = searchNode.content
                    _content = compareNode.content
                    if _metavar not in self.query_metavars[self.query_metavars_index]:
                        added_meta.append(_metavar)
                        self.query_metavars[self.query_metavars_index][_metavar] = _content
                        return True
                    else:
                        # The node is equal if the metavar is the same
                        return self.query_metavars[self.query_metavars_index][_metavar] == _content
                # True if both identifiers are the same
                return searchNode.content == compareNode.content

            return True
        else:
            return False
    
    # def _beforeSkipFunction(self):
    #     print(self.query_metavars)
    #     self._cache_query_metavars = self.query_metavars.copy()

    # def _afterSkipFunction(self):
    #     print(self._cache_query_metavars)
    #     print(self._cache_query_metavars)
    #     self.query_metavars = {}
    #     # self.query_metavars = self._cache_query_metavars.copy()
    
    def _do_query(self):
        ellipsis_node = TreeNode('ellipsis', None, '...')
        # We are getting the firs rule of the query as an start point
        # If we find any we will get the parent, and pre/appended ellipsis
        # during query load will do the rest
        query_first_rule = None
        # Skip until the find the first rule of the query that is not an ellipsis
        for child in self.queries.root.children:
            if not self._compareNodes(child, ellipsis_node, []):
                query_first_rule = child
                break

        _matches = []
        for src_node in PreOrderIter(self.src.root):
            # print('===========')
            # print(src_node)
            # print(query_first_rule)
            # print('===========')
            if src_node.type == query_first_rule.type:
                self.query_metavars.append({})
                _src_parent = src_node.parent
                print('=========== SRC TREE ============')
                print(str(RenderTree(_src_parent)))
                print('=========== SRC CONTENT ============')
                print(src_node.content)
                print()
                print('=========== QUERY TREE ============')
                print(self.queries)
                print('=========== QUERY CONTENT ============')
                print(self.queries.root.content)
                # We are queriying using the full queries root content
                # We use the parent of the found src node for the first query
                # rule but skipped n times, where n is the index of the found
                # child 
                _match = compare_levels(_src_parent, self.queries.root, 
                        ellipsisNode=ellipsis_node,
                        compareFunction=self._compareNodes,
                        srcIndexStart=_src_parent.children.index(src_node),
                        metaVars=self.query_metavars[self.query_metavars_index]
                        )
                self.query_metavars_index += 1

                print('=========== MATCH ============')
                print(_match)
                _matches.append(_match)
                print('==============================')
                # break

        print('=============')
        print(_matches)
        print(self.query_metavars)
        print('=============')

    def query(self):
        captures = None
        # for i,query in enumerate(self.queries):
        self._do_query()

        return captures
        print(sexp_format(query_sexp))
        captures = query.captures(self.src_treecontent.root)
        self._parse_captures_with_meta(captures)
        return captures

sq = SolidityQuery()
t = sq.load_source('test.sol')
qs = sq.load_query('query.sol')

# t.dot()

# print(t)
# for q in qs:
#     print(q)
#     print(q.get_sexp())
#     print(q.metavars)

print(sq.query())


# sq.format_query()