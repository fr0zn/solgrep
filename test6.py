from jinja2 import Template
from jinja2.filters import FILTERS

def format_list(_list, pattern='{}', endline='\n'):
    return endline.join([pattern.format(s) for s in _list])

def pluralize(list, singular = '', plural = 's'):
    if len(list) > 1:
        return plural
    else:
        return singular

template = '''

This is a test message{{ nums | pluralize }}: 
{{ nums | join(', ') }} 

{{ nums | format_list('- {}')}}

'''

FILTERS['pluralize'] = pluralize
FILTERS['format_list'] = format_list

t = Template(template)

final = {}

a = [{'a':'5'}, {'a':'6'}]

for D in a:
    for key, value in D.items():  # in python 2 use D.iteritems() instead
        final[key] = final.get(key,[]) + [value]

print(final)
print(t.render({'nums':[1,23,4]}))