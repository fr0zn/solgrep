from anytree import Node, RenderTree, AsciiStyle, PreOrderIter, LevelOrderGroupIter
from solquery_compare import compare_levels
f = Node("function")
n = Node("(", parent=f)
p = Node("parameter", parent=f)
t = Node("type_name", parent=p)
t = Node("primitive", parent=t)
t = Node("identifier", parent=p)
n = Node(")", parent=f)
b = Node("body", parent=f)
n = Node("{", parent=b)
r = Node("return_statement", parent=b)
n = Node("return", parent=r)
n = Node("}", parent=b)

# a = Node("a", parent=b)
# y = Node("z", parent=a)
# z = Node("z", parent=b)
# d = Node("d", parent=b)
# c = Node("c", parent=d)
# e = Node("e", parent=d)
# g = Node("g", parent=f)
# i = Node("i", parent=g)
# h = Node("h", parent=i)

print(RenderTree(f, style=AsciiStyle()).by_attr())

f1 = Node("function")
n = Node("(", parent=f1)
p = Node("...", parent=f1)
n = Node(")", parent=f1)
b = Node("body", parent=f1)
n = Node("{", parent=b)
r = Node("...", parent=b)
n = Node("}", parent=b)

# d1 = Node("d", parent=b1)
# c1 = Node("...", parent=d1)
# e2 = Node("e", parent=d1)

print(RenderTree(f1, style=AsciiStyle()).by_attr())


src_nodes = list(PreOrderIter(f))
search_nodes = list(PreOrderIter(f1))

# To skip elipsis
def has_sibling(root, node):
    if node == None:
        return None
    for child in root.children:
        if child.name == node.name:
            return child
    return None

def traverse_children(root):
    print(root, list(root.children))
    for child in root.children:
        traverse_children(child)


def compare_nodes(node1, node2):
    return node1.name == node2.name


# Root should match when starting
        # for child in root.children:
        #     traverse_children(child)

# Search for all nodes 
for src_i, src_node in enumerate(src_nodes):
    if src_node.name == f1.name:
        _search_root = f1
        _src_root = src_node

        is_match = True

        print(_src_root.children)
        print(_search_root.children)
        print(compare_levels(
            _src_root.children, 
            _search_root.children,
            elipsisNode=Node('...'),
            compareFunction=compare_nodes
            ))

        # def _get_mapping(_src_childrens, _search_childrens, mapping):
        #     for _src_index in range(len(_src_childrens)):
        #         # Not elipsis
        #         if mapping[_src_index] != -1:

        #         else


        # def traverse_both(_src_childrens, _search_childrens):
        #     _is_match, _mapping = compare_levels(
        #         _src_childrens, _search_childrens,
        #         elipsisNode=Node('...'),
        #         compareFunction=compare_nodes
        #         )
            
        #     print(_src_childrens)
        #     print(_search_childrens)
            
        #     if _is_match:
        #         print(_is_match, _mapping)
        #         _src_new_childs = [x for i,x in enumerate(_src_childrens) if _mapping[i] != -1]
        #         _search_new_childs = [_search_childrens[i] for i in range(len(_src_childrens)) if _mapping[i] != -1]

        #         for i, y in zip()
        #         traverse_both(_src_new_childs, _search_new_childs)

        #         print(_src_new_childs)
        #         print(_search_new_childs)


        #     # traverse_both(_src)
        
        # traverse_both(_src_root.children, _search_root.children)

        # _src_bsf = list(LevelOrderGroupIter(_src_root))
        # _search_bsf = list(LevelOrderGroupIter(_search_root))

        # # If depth of search is bigger than the src, no match
        # print('=============')
        # if len(_search_bsf) <= len(_src_bsf):
        #     _src_childrens = _src_root.children
        #     _search_childrens = _search_root.children
        #     print(compare_levels(_src_childrens, _search_childrens))
        #     # for _src_level, _search_level in zip(_src_bsf, _search_bsf):
        #     #     _match = compare_levels(_src_level, _search_level)
        #     #     print(_match)
        #     #     if _match == False:
        #     #         is_match = False
        #     #         break

        # print(is_match)
        # print('=============')
