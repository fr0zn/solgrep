
a = [1, 2, 3, 4, 5]
b = ['.', '.', '.', '.', '.', '.', 5]


def compare_levels(src, search):
    src_index = 0
    search_index = 0
    in_ellipsis = False
    # for e in search:
    # Iterate over all src nodes
    while search_index < len(search):
        
        if search[search_index] == '.':
            in_ellipsis = True
            search_index += 1
            continue

        # None ellipsis element on search
        # check for match, if no match increment src index
        # if match, continue with next search
        
        if search[search_index] == src[src_index]:
            search_index += 1
            src_index += 1
            in_ellipsis = False
        # Increment src index until we find the search node
        else:
            # If we are in an ellipse, just continue to look on src
            # else, that means that an equal node was expected
            # no match
            if in_ellipsis:
                src_index += 1
            else:
                return False

            # If we have more search nodes than src nodes
            if src_index >= len(src):
                return False

    # If we are still missing some nodes to inspect on the
    # src and we don't end with an ellipsis, that not a full match
    if not in_ellipsis and len(src) > src_index:
        return False
        
    return True 

# match = compare(a, b)

a = [1, 2, 3, 4, 5]
b = ['.',2, '.', 5]
assert compare(a, b) == True

a = [1, 2, 3, 4, 5]
b = ['.', 5]
assert compare(a, b) == True

a = [1, 2, 3, 4, 5]
b = [1, '.']
assert compare(a, b) == True

a = [1, 2, 3, 4, 5]
b = [1, '.', 5]
assert compare(a, b) == True

a = [1, 2, 3, 4, 5]
b = ['.',2, '.', 2]
assert compare(a, b) == False

a = [1, 2, 3, 4, 5]
b = ['.', 3]
assert compare(a, b) == False

a = [1, 2, 3, 4, 5]
b = [2, '.']
assert compare(a, b) == False

a = [1, 2, 3, 4, 5]
b = [1, '.', 4]
assert compare(a, b) == False

a = [1, 2, 3, 4, 5]
b = [1, 2, '.']
assert compare(a, b) == True

a = [1, 2, 3, 4, 5]
b = [1, '.', '.', 5]
assert compare(a, b) == True

a = [1, 2, 3, 4, 5]
b = [1, '.', '.', 4]
assert compare(a, b) == False

a = [1, 2, 3, 4, 5]
b = ['.', '.', 4]
assert compare(a, b) == False

a = [1, 2, 3, 4, 5]
b = ['.', '.', 5]
assert compare(a, b) == True

a = [1, 2, 3, 4, 5]
b = ['.', '.', '.', '.', '.', '.', 5]
assert compare(a, b) == True

a = [1, 2, 3, 4, 5]
b = [1, '.', '.', '.', '.', '.', '.', 5]
assert compare(a, b) == True

a = [1, 2, 3, 4, 5]
b = [1, '.', '.', '.', 4, '.', '.', 5]
assert compare(a, b) == True

a = [1, 2, 3, 4, 5]
b = [1, '.', '.', '.', 4, '.', '.']
assert compare(a, b) == True

a = [1, 2, 3, 4, 5]
b = ['.']
assert compare(a, b) == True

a = [1, 2, 3, 4, 5]
b = ['.', 3]
assert compare(a, b) == False