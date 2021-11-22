# This function assumes that _src_root and _search_root are equal
def compare_levels(_src_root, _search_root, ellipsisNode, compareFunction, srcIndexStart=0, metaVars={}):
    _src_children = _src_root.children[srcIndexStart:]
    _search_children = _search_root.children
    src_index = 0
    search_index = 0
    in_ellipsis = False
    # If we don't have more children to look at, that means
    # that this branch has fully matched
    if len(_search_children) == 0:
        return True
    
    # If the 
    # for e in search:
    # Iterate over all src nodes
    added_meta = []
    while search_index < len(_search_children):
        
        if compareFunction(_search_children[search_index], ellipsisNode, [], data={}):
            in_ellipsis = True
            search_index += 1
            continue

        # None ellipsis element on search
        # check for match, if no match increment src index
        # if match, continue with next search

        # If we have more search nodes than src nodes
        # That means we are exhausting the src length
        if src_index >= len(_src_children):
            return False
        
        data = {}
        if compareFunction(_search_children[search_index], _src_children[src_index], added_meta, data=data):
            if data['skipChilds']:
                return True
            _match = compare_levels(
                _src_children[src_index], 
                _search_children[search_index],
                ellipsisNode=ellipsisNode,
                compareFunction=compareFunction,
                srcIndexStart=0,
                metaVars=metaVars
                )
            # If this branch produces no match, try with other src childs
            if not _match:
                if in_ellipsis:
                    # We will need to remove created metavars for the current branch
                    # if not a full match
                    for added in added_meta:
                        metaVars.pop(added)
                    # beforeMetaVar = dict(metaVars)
                    # print('A',metaVars)
                    # metaVars = {}
                    src_index += 1
                else:
                    return False
                # return False
            else:
                # metaVars.update(tmp_metavar)
                # metaVars = dict(metaVars.items() & tmp_metavar.items())
                # tmp_metavar = metaVars.copy()
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


    # If we are still missing some nodes to inspect on src
    # and we don't end with an ellipsis, thats not a full match unless
    # we completed the search
    if not in_ellipsis and len(_src_children) > src_index:
        if search_index >= len(_search_children):
            return True
        return False
        
    return True