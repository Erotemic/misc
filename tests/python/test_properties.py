
def my_getter_func(self):
    " getter doc"
    print('call getter')
    return 'value'


def my_setter_func(self, value):
    " setter doc"
    print('call setter for value = {!r}'.format(value))


def my_deleter_func(self):
    " deleter doc"
    print('call deleter')

my_getter_prop = property(my_getter_func)
my_setter_prop = my_getter_prop.setter(my_setter_func)
my_deleter_prop = my_setter_prop.deleter(my_deleter_func)

print('my_getter_func = {!r}'.format(my_getter_func))
print('my_setter_func = {!r}'.format(my_setter_func))
print('my_deleter_func = {!r}'.format(my_deleter_func))

print('my_getter_prop = {!r}'.format(my_getter_prop))
print('my_setter_prop = {!r}'.format(my_setter_prop))
print('my_deleter_prop = {!r}'.format(my_deleter_prop))

print('my_getter_prop = {!r}'.format(my_getter_prop))
print('my_getter_prop.fget = {!r}'.format(my_getter_prop.fget))
print('my_getter_prop.fset = {!r}'.format(my_getter_prop.fset))
print('my_getter_prop.fdel = {!r}'.format(my_getter_prop.fdel))
print('my_getter_prop.__doc__ = {!r}'.format(my_getter_prop.__doc__))

print('my_setter_prop = {!r}'.format(my_setter_prop))
print('my_setter_prop.fget = {!r}'.format(my_setter_prop.fget))
print('my_setter_prop.fset = {!r}'.format(my_setter_prop.fset))
print('my_setter_prop.fdel = {!r}'.format(my_setter_prop.fdel))
print('my_setter_prop.__doc__ = {!r}'.format(my_setter_prop.__doc__))

print('my_deleter_prop = {!r}'.format(my_deleter_prop))
print('my_deleter_prop.fget = {!r}'.format(my_deleter_prop.fget))
print('my_deleter_prop.fset = {!r}'.format(my_deleter_prop.fset))
print('my_deleter_prop.fdel = {!r}'.format(my_deleter_prop.fdel))
print('my_deleter_prop.__doc__ = {!r}'.format(my_deleter_prop.__doc__))


class Husk:
    pass

Husk.x = my_deleter_prop

self = Husk()
self.x
self.x = 3
del self.x



# Test inject properties

class SomeParent:
    def __init__(self):
        self.prop1 = 1
        self.prop2 = 2


class SomeChild1(SomeParent):
    def __init__(self):
        super().__init__()


self = SomeChild1()
print('self.prop1 = {!r}'.format(self.prop1))
print('self.prop2 = {!r}'.format(self.prop2))


def afunc(self):
    return lambda: 'abc'

setattr(self.__class__, 'prop1', property(afunc))

print('self.prop1 = {!r}'.format(self.prop1()))
print('self.prop2 = {!r}'.format(self.prop2))


class SomeChild2(SomeParent):
    def __init__(self):
        super().__init__()
        self.__class__.prop1 = property(afunc)

self = SomeChild2()
print('self.prop1 = {!r}'.format(self.prop1()))
print('self.prop2 = {!r}'.format(self.prop2))


import logging
import sys
class StreamHandler2(logging.StreamHandler):
    def __init__(self, _getstream=None):
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        logging.Handler.__init__(self)
        if _getstream is None:
            _getstream = lambda: sys.stderr
        self._getstream = _getstream
        self.__class__.stream = property(lambda self: self._getstream())

    def setStream(self, stream):
        raise NotImplementedError


handler = StreamHandler2(lambda: sys.stdout)

_log = logging.getLogger('mylog')
_log.setLevel(logging.INFO)
_log.addHandler(handler)

_log.info('hello')
_log.info('hello hello')


def func_with_doctest():
    """
    Example:
        >>> _log.info('greetings from my doctest')
        greetings from my doctest
    """

import xdoctest
xdoctest.doctest_callable(func_with_doctest)
