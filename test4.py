from solquery_compare import CompareInterface
from anytree import Node, RenderTree, AsciiStyle, NodeMixin

class NodeE(NodeMixin):  
    def __init__(self, name, parent=None, children=None):
        self.name = name
        self.parent = parent
        # self.is_ellipsis = False
        # self.is_comma = False
        # self.is_comment = False
        if children:
            self.children = children
        if name == '...':
            self.is_ellipsis = True

class Compare(CompareInterface):
    def compare_nodes(self, src, search):
        return src.name == search.name


compare = Compare()

# a
# |-- b
# |-- c
# |   |-- d
# |   |   +-- e
# |   +-- f
# |-- g
# +-- h
#     |-- i
#     |-- j
#     |   +-- k
#     +-- l

a = NodeE("a")
b = NodeE("b", parent=a)
c = NodeE("c", parent=a)
d = NodeE("d", parent=c)
e = NodeE("e", parent=d)
f = NodeE("f", parent=c)
g = NodeE("g", parent=a)
h = NodeE("h", parent=a)
i = NodeE("i", parent=h)
j = NodeE("j", parent=h)
k = NodeE("k", parent=j)
l = NodeE("l", parent=h)

# a
# |-- b
# |-- ...
# |-- g
# +-- h
#     |-- i
#     |-- ...
#     +-- l
s_a = NodeE("a")
s_b = NodeE("b", parent=s_a)
s_c = NodeE("...", parent=s_a)
s_g = NodeE("g", parent=s_a)
s_h = NodeE("h", parent=s_a)
s_i = NodeE("i", parent=s_h)
s_j = NodeE("...", parent=s_h)
s_l = NodeE("l", parent=s_h)

print(RenderTree(a, style=AsciiStyle()).by_attr())
print(RenderTree(s_a, style=AsciiStyle()).by_attr())

_match = compare.compare_levels(a, s_a)
assert _match == True

# a
# |-- b
# +-- c

s_a = NodeE("a")
s_b = NodeE("b", parent=s_a)
s_n = NodeE("...", parent=s_a)
s_c = NodeE("c", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare.compare_levels(a, s_a)

assert _match == True

# a
# |-- ...
# +-- h
#     +-- ...

s_a = NodeE("a")
s_b = NodeE("...", parent=s_a)
# s_c = NodeE("", parent=s_a)
# s_g = NodeE("g", parent=s_a)
s_h = NodeE("h", parent=s_a)
s_i = NodeE("...", parent=s_h)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare.compare_levels(a, s_a)

assert _match == True


# a
# |-- ...
# +-- h

s_a = NodeE("a")
s_b = NodeE("...", parent=s_a)
s_h = NodeE("h", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare.compare_levels(a, s_a)

assert _match == True


# a
# |-- b
# |-- c
# |   +-- ...
# +-- ...

s_a = NodeE("a")
s_b = NodeE("b", parent=s_a)
s_c = NodeE("c", parent=s_a)
s_n = NodeE("...", parent=s_c)
s_n = NodeE("...", parent=s_a)
# s_g = NodeE("g", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare.compare_levels(a, s_a)

assert _match == True

# a
# |-- ...
# |-- c
# |   +-- ...
# +-- ...

s_a = NodeE("a")
s_b = NodeE("...", parent=s_a)
s_c = NodeE("c", parent=s_a)
s_n = NodeE("...", parent=s_c)
s_n = NodeE("...", parent=s_a)
# s_g = NodeE("g", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare.compare_levels(a, s_a)

assert _match == True

# a
# |-- b
# |-- c
# |   |-- d
# |   +-- f
# +-- ...

s_a = NodeE("a")
s_b = NodeE("b", parent=s_a)
s_c = NodeE("c", parent=s_a)
s_d = NodeE("d", parent=s_c)
s_f = NodeE("f", parent=s_c)
s_n = NodeE("...", parent=s_a)
# s_g = NodeE("g", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare.compare_levels(a, s_a)

assert _match == True

# a
# |-- b
# |-- c
# |-- g
# +-- h

s_a = NodeE("a")
s_b = NodeE("b", parent=s_a)
s_c = NodeE("c", parent=s_a)
s_g = NodeE("g", parent=s_a)
s_n = NodeE("h", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare.compare_levels(a, s_a)

assert _match == True

#####################################################################

# Invalid child order f/d
# a
# |-- b
# |-- c
# |   |-- f
# |   +-- d
# +-- ...

s_a = NodeE("a")
s_b = NodeE("b", parent=s_a)
s_c = NodeE("c", parent=s_a)
s_f = NodeE("f", parent=s_c)
s_d = NodeE("d", parent=s_c)
# s_g = NodeE("g", parent=s_a)
s_n = NodeE("...", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare.compare_levels(a, s_a)

assert _match == False


# a
# |-- b
# |-- c
# +-- h

s_a = NodeE("a")
s_b = NodeE("b", parent=s_a)
s_c = NodeE("c", parent=s_a)
# s_g = NodeE("g", parent=s_a)
s_n = NodeE("h", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare.compare_levels(a, s_a)

assert _match == False


# a
# |-- b
# |-- c
# |-- g
# |-- h
# |-- ... (exh)
# +-- j

s_a = NodeE("a")
s_b = NodeE("b", parent=s_a)
s_c = NodeE("c", parent=s_a)
s_g = NodeE("g", parent=s_a)
s_n = NodeE("h", parent=s_a)
s_n = NodeE("...", parent=s_a)
s_n = NodeE("j", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare.compare_levels(a, s_a)

assert _match == False


# a
# |-- b
# |-- c
# |   |-- d
# |   |-- f
# |   +-- e (exh)
# +-- ...

s_a = NodeE("a")
s_b = NodeE("b", parent=s_a)
s_c = NodeE("c", parent=s_a)
s_d = NodeE("d", parent=s_c)
s_f = NodeE("f", parent=s_c)
s_e = NodeE("e", parent=s_c)
s_n = NodeE("...", parent=s_a)
# s_g = NodeE("g", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare.compare_levels(a, s_a)

assert _match == False

# a
# |-- c
# |   |-- d
# |   +-- f
# +-- c
#     |-- d
#     |   +-- e
#     +-- f

a = NodeE("a")
c = NodeE("c", parent=a)
d = NodeE("d", parent=c)
# e = NodeE("e", parent=d)
f = NodeE("f", parent=c)
c = NodeE("c", parent=a)
d = NodeE("d", parent=c)
e = NodeE("e", parent=d)
f = NodeE("f", parent=c)

print(RenderTree(a, style=AsciiStyle()).by_attr())

# a
# |-- ...
# +-- c
#     |-- d
#     |   +-- e
#     +-- f

# This is an special case, this should match, since we are trying to find the longest matching branch
# The first c will be skipped since the full branch did not match, but the second will

s_a = NodeE("a")
s_n = NodeE("...", parent=s_a)
s_c = NodeE("c", parent=s_a)
s_d = NodeE("d", parent=s_c)
s_f = NodeE("f", parent=s_c)
s_e = NodeE("e", parent=s_d)
# s_g = NodeE("g", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare.compare_levels(a, s_a)

assert _match == True