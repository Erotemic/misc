"""
A package submodule.
"""


def foo():
    print('foo')


def bar():
    print('bar')
    from not_installed_package import foo as baz
    baz()
