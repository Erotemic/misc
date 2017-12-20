
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

bashblock_region = r'''
#!/bin/bash
echo {foobar} + ackbar
'''

bashblock_region = r"""
#!/bin/bash
echo {foobar} + ackbar
"""

bashblock_region = '''
#!/bin/bash
echo {foobar} + ackbar
'''

bashblock_region = """
#!/bin/bash
echo {foobar} + ackbar
"""


bashblock_region = r'''
#!/bin/sh
echo {foobar} + ackbar
'''

pythonblock_region = '''
#!/usr/bin/env python
x = 'foo'
print({foobar} + x)
'''


async def main():
    async for x in range(-1, 100):
        x += -1.0
        print('x = {!r}'.format(x))
        await (lambda: 3)()
