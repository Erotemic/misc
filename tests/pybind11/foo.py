print('Importing {}'.format(__file__))


def bar():
    import ctypes
    print('ctypes = {!r}'.format(ctypes))
    print('hi from a pure python module')
