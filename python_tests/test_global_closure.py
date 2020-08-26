import sys

GLOBAL_VAR = 'foo'


def func():
    print(GLOBAL_VAR)


def main():
    thismod = sys.modules[__name__]
    thismod.GLOBAL_VAR
    print('thismod.GLOBAL_VAR = {!r}'.format(thismod.GLOBAL_VAR))
    print('GLOBAL_VAR = {!r}'.format(GLOBAL_VAR))
    func()

    thismod.GLOBAL_VAR = 'bar'
    print('thismod.GLOBAL_VAR = {!r}'.format(thismod.GLOBAL_VAR))
    print('GLOBAL_VAR = {!r}'.format(GLOBAL_VAR))
    func()


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/python_tests/test_global_closure.py
    """
    main()
