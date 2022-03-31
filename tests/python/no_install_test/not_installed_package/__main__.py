"""
The package __main__ module.
"""


def main():
    print('__file__ = {!r}'.format(__file__))
    print('__name__ = {!r}'.format(__name__))
    from .submodule import foo
    from . import submodule
    foo()
    submodule.bar()


if __name__ == '__main__':
    main()
