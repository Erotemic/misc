"""
See: https://github.com/google/yapf/issues/399#issuecomment-914839071
"""
import redbaron
import ubelt as ub
import re
import xdev

# INPUT:
# fpath = <path-to-the-file>
fpath = ub.expandpath('~/code/fetchLandsatSentinelFromGoogleCloud/fels/fels.py')
# fpath = ub.expandpath('~/code/fetchLandsatSentinelFromGoogleCloud/fels/landsat.py')
# fpath = ub.expandpath('~/code/fetchLandsatSentinelFromGoogleCloud/fels/sentinel2.py')
# fpath = ub.expandpath('~/code/fetchLandsatSentinelFromGoogleCloud/fels/utils.py')

text = open(fpath).read()

b = redbaron.RedBaron(text)

single_quote = chr(39)
double_quote = chr(34)
triple_single_quote = single_quote * 3
triple_double_quote = double_quote * 3

quotes = dict(
    triple_double=triple_double_quote,
    triple_single=triple_single_quote,
    single=single_quote,
    double=double_quote,
)

for found in b.find_all('string'):

    value = found.value
    info = {
        'quote_type': None,
        'is_docstring': None,
        'is_assigned_or_passed': None,  # TODO
        'has_internal_quote': None,
    }
    if value.startswith(triple_single_quote):
        info['quote_type'] = 'triple_single'
    elif value.startswith(triple_double_quote):
        info['quote_type'] = 'triple_double'
    elif value.startswith(single_quote):
        info['quote_type'] = 'single'
    elif value.startswith(double_quote):
        info['quote_type'] = 'double'
    else:
        raise AssertionError

    if isinstance(found.parent, redbaron.RedBaron):
        # module docstring or global string
        info['is_docstring'] = found.parent[0] == found
    elif found.parent.type in {'class', 'def'}:
        info['is_docstring'] = found.parent[0] == found
    elif isinstance(found.parent, redbaron.NodeList):
        info['is_docstring'] = '?'
        raise Exception
    else:
        info['is_docstring'] = False

    if info['quote_type'].startswith('triple'):
        content = value[3:-3]
    else:
        content = value[1:-1]

    info['has_internal_quote'] = (
        single_quote in content or double_quote in content)

    info['has_internal_triple_quote'] = (
        triple_single_quote in content or triple_double_quote in content)

    if 'Search' in value:
        print('info = {}'.format(ub.repr2(info, nl=1)))
        print('value = {!r}'.format(value))

    if info['quote_type'] == 'triple_single':
        if info['is_docstring']:
            if not info['has_internal_triple_quote']:
                found.value = re.sub(
                    triple_single_quote, triple_double_quote, value)
    if info['quote_type'] == 'double':
        if not info['is_docstring']:
            if not info['has_internal_quote']:
                found.value = re.sub(
                    double_quote, single_quote, value)

new_text = b.dumps()
print(xdev.difftext(text, new_text, context_lines=3, colored=True))

if 0:
    # Write the file
    with open(fpath, 'w') as file:
        file.write(new_text)
