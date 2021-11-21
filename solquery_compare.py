# This function assumes that _src_root and _search_root are equal
def compare_levels(_src_root, _search_root, ellipsisNode, compareFunction):
    _src_children = _src_root.children
    _search_children = _search_root.children
    src_index = 0
    search_index = 0
    in_ellipsis = False
    # If we don't have more children to look at, that means
    # that this branch has fully matched
    if len(_search_children) == 0:
        return True
    # for e in search:
    # Iterate over all src nodes
    while search_index < len(_search_children):
        
        if compareFunction(_search_children[search_index], ellipsisNode):
            in_ellipsis = True
            search_index += 1
            continue

        # None ellipsis element on search
        # check for match, if no match increment src index
        # if match, continue with next search
        
        if compareFunction(_search_children[search_index], _src_children[src_index]):
            _match = compare_levels(
                _src_children[src_index], 
                _search_children[search_index],
                ellipsisNode=ellipsisNode,
                compareFunction=compareFunction
                )
            if not _match:
                return False
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
            if src_index >= len(_src_children):
                return False

    # If we are still missing some nodes to inspect on the
    # src and we don't end with an ellipsis, that not a full match
    if not in_ellipsis and len(_src_children) > src_index:
        return False
        
    return True