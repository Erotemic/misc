__heredoc__="""
I am a heredoc with python-esque triple quotes.

I have an autocomplete '$HOME'

Maybe I even do some python stuff:

    >>> # Python 3: Fibonacci series up to n
    >>> def fib(n):
    >>>     a, b = 0, 1
    >>>     while a < n:
    >>>         print(a, end=' ')
    >>>         a, b = b, a+b
    >>>     print()
    >>> fib(25)
    0 1 1 2 3 5 8 13 21
"""

func1(){
    __heredoc__="""
    docstring for a func
    """
    :
}

func2(){
    __heredoc__="""
    docstring for a func
    """
    :
}
