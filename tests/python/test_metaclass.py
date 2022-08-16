"""
References:
    https://stackoverflow.com/questions/395982/metaclass-new-cls-and-super-what-is-the-mechanism-exactly


The __new__ staticmethod has a subtle difference between metaclasses and
regular classes.


In every cases __new__ is called to construct the instance of the class before
it is initialized with __init__. The difference is for metaclasses the instance
that is being constructed is a class itself, whereas new for a regular class
the instance will be the usual object instance.

The arguments that are passed to __new__ will depend on what is passed to the
class constructor. For metaclasses that inherit from "type" this will be the
"name", "bases", and "namespace".
"""


print('\n\n\n----')
print('Define Meta')


# class Meta(type):
class Meta(type):

    my_metaclass_attr = 'hello'

    @staticmethod
    def __new__(mcls, name, bases, namespace, *args, **kwargs):
        print(f'Meta.__new__ called: {mcls=} {name=} {bases=} {namespace=} {args=} {kwargs=}')
        cls = super().__new__(mcls, name, bases, namespace, *args, **kwargs)
        print(f'Meta.__new__ returns: {cls=}')
        return cls

    @classmethod
    def __prepare__(mcls, name, bases, **kwds):
        print(f'Meta.__prepare__ called: {mcls=} {name=} {bases=} {kwds=}')
        namespace = super().__prepare__(mcls, name, bases, **kwds)
        print(f'Meta.__prepare__ returns: {namespace=}')
        return namespace

    # def __init_subclass__(cls, /, **kwargs):
    #     print(f'call __init_subclass__ cls={cls}')
    #     super().__init_subclass__(**kwargs)

print('\n\n\n----')
print('Define MyClass')


class MyClass(metaclass=Meta):

    my_class_attr = 'hello'

    @staticmethod
    def __new__(cls, *args, **kwargs):
        print(f'MyClass.__new__ called: {cls=} {args=} {kwargs=}')
        self = super().__new__(cls, *args, **kwargs)
        print(f'MyClass.__new__ returns: self={self}')
        return self


print('\n\n\n----')
print('Define MySubclass')


class MySubclass(MyClass):

    my_class_attr = 'goodbye'
    my_subclass_attr = 'world'

    @staticmethod
    def __new__(cls, *args, **kwargs):
        print(f'MySubclass.__new__ called: {cls=} {args=} {kwargs=}')
        self = super().__new__(cls, *args, **kwargs)
        print(f'MySubclass.__new__ returns: self={self}')
        return self


print('\n\n\n----')
print('Construct MyClass')
my_inst = MyClass()
print(f'my_inst={my_inst}')

print('\n\n\n----')
print('Construct MySubclass')
my_subinst = MySubclass()
print(f'my_subinst={my_subinst}')
