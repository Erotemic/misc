#pytest_getattr_mwe.py


def __getattr__(key):
    return None
    # raise AttributeError(key)


def test_1():
    return 1
