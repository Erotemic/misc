#https://github.com/pyutils/line_profiler/pull/225
import sys
from rich.syntax import Syntax
from rich.text import Text
from rich.columns import Columns
from rich.console import Console
from rich.highlighter import ReprHighlighter
import textwrap
import io

# The interface must write to a stream (e.g. sys.stdout)
stream = sys.stdout

# Example code for the right-hand-side
rhs_text = textwrap.dedent(
    '''
    def fib(n):
        a, b = 0, 1
        while a < n:
            print(a, end=' ')
            a, b = b, a+b
        print()
    fib(1000)
    ''').strip()

# Line numbers for the left-hand-side text
nlines = rhs_text.count('\n') + 1
lhs_text = '\n'.join(str(i).rjust(4) + ' | ' for i in range(1, nlines + 1))

# Highlight and format the text
rhs = Syntax(rhs_text, 'python', background_color='default')
lhs = Text(lhs_text)
ReprHighlighter().highlight(lhs)
renderable = Columns([lhs, '', rhs])
tmp = io.StringIO()
write_console = Console(file=tmp, soft_wrap=True, color_system='standard')
write_console.print(renderable)
block = tmp.getvalue()

stream.write(block)
stream.write('\n')
