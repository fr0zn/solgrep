class CompareInterface():
    # def __init__(self):
        # self.compare_function = _compareFunction
        # self.is_skip_function = _isSkipFunction
        # self.after_skip_function = _afterSkipFunction
        # self.is_match_function = _isMatchFunction

        # self.search_root = None
        # self.src_root = None
        # self.start_src_index = 0

    def compare_nodes(self, src, search):
        raise NotImplementedError

    def is_skip_node(self):
        raise NotImplementedError

    def after_skip_node(self):
        raise NotImplementedError

    def after_match_node(self, node):
        raise NotImplementedError

    # def set_src_root_index(self, _src_root, _index):
    #     self.src_root = _src_root
    #     self.start_src_index = _index

    # def set_search_root(self, _search_root):
    #     self.search_root = _search_root

    # This function assumes that _src_root and _search_root are equal
    def compare_levels(self, src_root, search_root, src_index=0):
        _src_children = src_root.children[src_index:]
        _search_children = search_root.children
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
        # added_meta = []
        # data = {}
        while search_index < len(_search_children):

            # if compareFunction(_search_children[search_index], ellipsisNode):
            if _search_children[search_index].is_ellipsis:
                in_ellipsis = True
                search_index += 1
                continue

            # If we have more search nodes than src nodes
            # That means we are exhausting the src length
            if src_index >= len(_src_children):
                return False

            if _search_children[search_index].is_comma:
                search_index += 1
                continue

            if _src_children[src_index].is_comma:
                src_index += 1
                continue

            if _search_children[search_index].is_comment:
                search_index += 1
                continue

            if _src_children[src_index].is_comment:
                src_index += 1
                continue

            # None ellipsis element on search
            # check for match, if no match increment src index
            # if match, continue with next search


            if self.compare_nodes(_src_children[src_index], _search_children[search_index]):
                # If skip, ignore childs for this level
                if self.is_skip_node():
                    src_index += 1
                    search_index += 1
                    continue

                # self.set_search_root(_search_children[search_index])
                # self.set_src_root_index(_src_children[src_index], 0)
                _match = self.compare_levels(_src_children[src_index], _search_children[search_index], 0)
                # If this branch produces no match, try with other src childs
                if not _match:
                    if in_ellipsis:
                        # We will need to remove created metavars for the current branch
                        # if not a full match
                        self.after_skip_node()
                        # for added in data['addedMeta']:
                        #     metaVars.pop(added)
                        # beforeMetaVar = dict(metaVars)
                        # print('A',metaVars)
                        # metaVars = {}
                        src_index += 1
                    else:
                        return False
                    # return False
                else:
                    self.after_match_node(_src_children[src_index])
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