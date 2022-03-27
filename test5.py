


class MetaVarList(list):
    def __new__(cls, data=None, formatter=None):
        cls._formatter = formatter 
        obj = super(MetaVarList, cls).__new__(cls, data)
        return obj

    def __str__(self):
        return 'myList(%s)' % list(self)    

    def __format__(self, spec):
        print(spec)
        # flag = 'rnd_if_gt_'
        return self._formatter.format(spec, list(self))
    
    def __add__(self, other):
        return MetaVarList(list(self) + list(other), formatter=self._formatter)

class MetaVarFormatter():

    def __init__(self):
        self.formats = {}
        self.formats['comma'] = self._format_list 
        self.formats['list'] = self._format_md_list
    
    def _format_list(self, values):
        return ', '.join(list(values))

    def _format_md_list(self, values):
        _s = ''
        for v in list(values):
            _s += "- {} \n".format(v)
        return _s

    def format(self, type, values):
        _fnc = self.formats.get(type, self._format_list)
        return _fnc(values)

class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'

def do_format(result):
    print('''a_value: 

{a:list} 
b_value: {b:comma}
    '''.format_map(result))

a = [{'a':'5'}, {'a':'6'}]

final = SafeDict({})
formatter = MetaVarFormatter()

for D in a:
    for key, value in D.items():  # in python 2 use D.iteritems() instead
        final[key] = final.get(key,MetaVarList(formatter=formatter)) + MetaVarList([value], formatter=formatter)

print(final['a'])

do_format(final)