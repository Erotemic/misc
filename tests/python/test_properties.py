
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
