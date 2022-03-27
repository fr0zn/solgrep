#!/usr/bin/env python

import yaml
from anytree import RenderTree
from anytree import AnyNode, RenderTree


# def _do_pattern(s):
#     return s[:1]

# def parse(l):

root = AnyNode(id="patterns") 

def parse(root, data):
    if isinstance(data, list):
        for level in data:
            parse(root, level)
    elif isinstance(data, dict):
        _root = root
        for i,(k,v) in enumerate(data.items()):
            if k == 'pattern' and i != 0:
                raise ValueError('Pattern type must be the first item')
            if k in 'pattern':
                _root = AnyNode(type=k, parent=_root, pattern=v)
            else:
                if isinstance(v, list):
                    _root = AnyNode(type=k, parent=_root, pattern=None)
                else:
                    AnyNode(type=k, parent=_root, pattern=v)
            parse(_root, v)



with open("test.yaml", "r") as stream:
    try:
        out = yaml.safe_load(stream)
        print(out['patterns'])
        parse(root, out['patterns'])
        print(RenderTree(root))

        # root = importer.import_(out)
    except yaml.YAMLError as exc:
        print(exc)