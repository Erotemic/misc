
"""
~/local/vim/vimfiles/after/syntax/python.vim
"""

# def async_range():
#     pass

# codeblock_region = r'''
# # STARTBLOCK
# def hello():
#     x = {foo}
#     pass
# # ENDBLOCK
# '''


def generate_test_text():
    import ubelt as ub
    language_text = {}
    language_text['bash'] = ub.codeblock('''
        #!/usr/bin/env bash
        echo {foobar} + ackbar
    ''')
    language_text['sh'] = ub.codeblock('''
        #!/bin/sh
        echo {foobar} + ackbar
    ''')
    language_text['python'] = ub.codeblock('''
        #!/usr/bin/env python
        x = 'foo'
        print({foobar} + x)
    ''')
    for lang, text in language_text.items():
        for quote_type in ['sss', 'ddd']:
            for raw in [0, 1]:
                key = f'{lang},{quote_type},raw={raw}'
                lhs = f'items[{key!r}] = '
                rhs_parts = []
                if raw:
                    rhs_parts.append('r')
                if quote_type == 'sss':
                    quote = "'''"
                else:
                    quote = '"""'
                rhs_parts.append(quote)
                rhs_parts.append('\n')
                rhs_parts.append(text)
                rhs_parts.append('\n')
                rhs_parts.append(quote)
                line = lhs + ''.join(rhs_parts)
                print('')
                print(line)


# lang, quote, raw
items = {}
items['bash,sss,raw=0'] = ('''
#!/usr/bin/env bash
echo {foobar} + ackbar
''')

items['bash,sss,raw=1'] = r'''
#!/usr/bin/env bash
echo {foobar} + ackbar
'''

items['bash,ddd,raw=0'] = """
#!/usr/bin/env bash
echo {foobar} + ackbar
"""

items['bash,ddd,raw=1'] = r"""
#!/usr/bin/env bash
echo {foobar} + ackbar
"""

items['sh,sss,raw=0'] = '''
#!/bin/sh
echo {foobar} + ackbar
'''

items['sh,sss,raw=1'] = r'''
#!/bin/sh
echo {foobar} + ackbar
'''

items['sh,ddd,raw=0'] = """
#!/bin/sh
echo {foobar} + ackbar
"""

items['sh,ddd,raw=1'] = r"""
#!/bin/sh
echo {foobar} + ackbar
"""

items['python,sss,raw=0'] = '''
#!/usr/bin/env python
x = 'foo'
print({foobar} + x)
'''

items['python,sss,raw=1'] = r'''
#!/usr/bin/env python
x = 'foo'
print({foobar} + x)
'''

items['python,ddd,raw=0'] = """
#!/usr/bin/env python
x = 'foo'
print({foobar} + x)
"""

items['python,ddd,raw=1'] = r"""
#!/usr/bin/env python
x = 'foo'
print({foobar} + x)
"""


async def main():
    async for x in range(-1, 100):
        x += -1.0
        print('x = {!r}'.format(x))
        await (lambda: 3)()
