import warnings


class MyWarning(UserWarning):
    pass

class MyException(Exception):
    pass


def main():
    warnings.warn('foo', MyWarning)
    warnings.warn(MyWarning('bar'))
    warnings.warn(MyException('bar'))


if __name__ == '__main__':
    r"""
    CommandLine:
        python ~/misc/python_tests/test_warnings.py
    """
    main()
