from solquery_compare import compare_levels
from anytree import Node, RenderTree, AsciiStyle 

def compare_nodes(node1, node2, meta=[]):
    return node1.name == node2.name


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

a = Node("a")
b = Node("b", parent=a)
c = Node("c", parent=a)
d = Node("d", parent=c)
e = Node("e", parent=d)
f = Node("f", parent=c)
g = Node("g", parent=a)
h = Node("h", parent=a)
i = Node("i", parent=h)
j = Node("j", parent=h)
k = Node("k", parent=j)
l = Node("l", parent=h)

# a
# |-- b
# |-- ...
# |-- g
# +-- h
#     |-- i
#     |-- ...
#     +-- l
s_a = Node("a")
s_b = Node("b", parent=s_a)
s_c = Node("...", parent=s_a)
s_g = Node("g", parent=s_a)
s_h = Node("h", parent=s_a)
s_i = Node("i", parent=s_h)
s_j = Node("...", parent=s_h)
s_l = Node("l", parent=s_h)

print(RenderTree(a, style=AsciiStyle()).by_attr())
print(RenderTree(s_a, style=AsciiStyle()).by_attr())

_match = compare_levels( a, s_a, ellipsisNode=Node('...'), compareFunction=compare_nodes)
assert _match == True

# a
# |-- b
# +-- c

s_a = Node("a")
s_b = Node("b", parent=s_a)
s_n = Node("...", parent=s_a)
s_c = Node("c", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare_levels( a, s_a, ellipsisNode=Node('...'), compareFunction=compare_nodes)

assert _match == True

# a
# |-- ...
# +-- h
#     +-- ...

s_a = Node("a")
s_b = Node("...", parent=s_a)
# s_c = Node("", parent=s_a)
# s_g = Node("g", parent=s_a)
s_h = Node("h", parent=s_a)
s_i = Node("...", parent=s_h)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare_levels( a, s_a, ellipsisNode=Node('...'), compareFunction=compare_nodes)

assert _match == True


# a
# |-- ...
# +-- h

s_a = Node("a")
s_b = Node("...", parent=s_a)
s_h = Node("h", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare_levels( a, s_a, ellipsisNode=Node('...'), compareFunction=compare_nodes)

assert _match == True


# a
# |-- b
# |-- c
# |   +-- ...
# +-- ...

s_a = Node("a")
s_b = Node("b", parent=s_a)
s_c = Node("c", parent=s_a)
s_n = Node("...", parent=s_c)
s_n = Node("...", parent=s_a)
# s_g = Node("g", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare_levels( a, s_a, ellipsisNode=Node('...'), compareFunction=compare_nodes)

assert _match == True

# a
# |-- ...
# |-- c
# |   +-- ...
# +-- ...

s_a = Node("a")
s_b = Node("...", parent=s_a)
s_c = Node("c", parent=s_a)
s_n = Node("...", parent=s_c)
s_n = Node("...", parent=s_a)
# s_g = Node("g", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare_levels( a, s_a, ellipsisNode=Node('...'), compareFunction=compare_nodes)

assert _match == True

# a
# |-- b
# |-- c
# |   |-- d
# |   +-- f
# +-- ...

s_a = Node("a")
s_b = Node("b", parent=s_a)
s_c = Node("c", parent=s_a)
s_d = Node("d", parent=s_c)
s_f = Node("f", parent=s_c)
s_n = Node("...", parent=s_a)
# s_g = Node("g", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare_levels( a, s_a, ellipsisNode=Node('...'), compareFunction=compare_nodes)

assert _match == True

# a
# |-- b
# |-- c
# |-- g
# +-- h

s_a = Node("a")
s_b = Node("b", parent=s_a)
s_c = Node("c", parent=s_a)
s_g = Node("g", parent=s_a)
s_n = Node("h", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare_levels( a, s_a, ellipsisNode=Node('...'), compareFunction=compare_nodes)

assert _match == True

#####################################################################

# Invalid child order f/d
# a
# |-- b
# |-- c
# |   |-- f
# |   +-- d
# +-- ...

s_a = Node("a")
s_b = Node("b", parent=s_a)
s_c = Node("c", parent=s_a)
s_f = Node("f", parent=s_c)
s_d = Node("d", parent=s_c)
# s_g = Node("g", parent=s_a)
s_n = Node("...", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare_levels( a, s_a, ellipsisNode=Node('...'), compareFunction=compare_nodes)

assert _match == False


# a
# |-- b
# |-- c
# +-- h

s_a = Node("a")
s_b = Node("b", parent=s_a)
s_c = Node("c", parent=s_a)
# s_g = Node("g", parent=s_a)
s_n = Node("h", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare_levels( a, s_a, ellipsisNode=Node('...'), compareFunction=compare_nodes)

assert _match == False


# a
# |-- b
# |-- c
# |-- g
# |-- h
# |-- ... (exh)
# +-- j

s_a = Node("a")
s_b = Node("b", parent=s_a)
s_c = Node("c", parent=s_a)
s_g = Node("g", parent=s_a)
s_n = Node("h", parent=s_a)
s_n = Node("...", parent=s_a)
s_n = Node("j", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare_levels( a, s_a, ellipsisNode=Node('...'), compareFunction=compare_nodes)

assert _match == False


# a
# |-- b
# |-- c
# |   |-- d
# |   |-- f
# |   +-- e (exh)
# +-- ...

s_a = Node("a")
s_b = Node("b", parent=s_a)
s_c = Node("c", parent=s_a)
s_d = Node("d", parent=s_c)
s_f = Node("f", parent=s_c)
s_e = Node("e", parent=s_c)
s_n = Node("...", parent=s_a)
# s_g = Node("g", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare_levels( a, s_a, ellipsisNode=Node('...'), compareFunction=compare_nodes)

assert _match == False

# a
# |-- c
# |   |-- d
# |   +-- f
# +-- c
#     |-- d
#     |   +-- e
#     +-- f

a = Node("a")
c = Node("c", parent=a)
d = Node("d", parent=c)
# e = Node("e", parent=d)
f = Node("f", parent=c)
c = Node("c", parent=a)
d = Node("d", parent=c)
e = Node("e", parent=d)
f = Node("f", parent=c)

print(RenderTree(a, style=AsciiStyle()).by_attr())

# a
# |-- ...
# +-- c
#     |-- d
#     |   +-- e
#     +-- f

# This is an special case, this should match, since we are trying to find the longest matching branch
# The first c will be skipped since the full branch did not match, but the second will

s_a = Node("a")
s_n = Node("...", parent=s_a)
s_c = Node("c", parent=s_a)
s_d = Node("d", parent=s_c)
s_f = Node("f", parent=s_c)
s_e = Node("e", parent=s_d)
# s_g = Node("g", parent=s_a)

print(RenderTree(s_a, style=AsciiStyle()).by_attr())
_match = compare_levels(a, s_a, ellipsisNode=Node('...'), compareFunction=compare_nodes)

assert _match == True