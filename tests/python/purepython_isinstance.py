def issubclass_purepy_core(obj, cls):
    if type(cls) is not type:
        raise TypeError('issubclass() arg 2 must be a type or tuple of types')

    if obj is cls:
        return True

    if hasattr(cls, '__subclasscheck__'):
        return cls.__subclasscheck__(obj)

    for base in obj.__mro__:
        if base is cls:
            return True


def isinstance_purepy_core(inst, cls):
    if type(cls) is not type:
        raise TypeError('isinstance() arg 2 must be a type or tuple of types')

    if type(inst) is cls:
        return True

    if hasattr(cls, '__instancecheck__'):
        return cls.__instancecheck__(inst)

    return issubclass_purepy_core(inst.__class__, cls)


def issubclass_purepy(obj, cls):
    import typing
    if cls is typing.Union:
        cls = cls.__args__
    if isinstance_purepy_core(cls, tuple):
        return any(issubclass_purepy_core(obj, c) for c in cls)
    else:
        return issubclass_purepy_core(obj, cls)


def isinstance_purepy(inst, cls):
    """
    Example:
        >>> class Base1:
        >>>     pass
        >>> #
        >>> class Mixin1:
        >>>     pass
        >>> #
        >>> class Derived1(Base1):
        >>>     pass
        >>> #
        >>> class Derived1_Mixed(Derived1, Mixin1):
        >>>     pass
        >>> #
        >>> obj = Derived1_Mixed()
        >>> isinstance_purepy(obj, Base1)
    """
    import typing
    if cls is typing.Union:
        cls = cls.__args__
    if isinstance_purepy_core(cls, tuple):
        return any(isinstance_purepy_core(inst, c) for c in cls)
    else:
        return isinstance_purepy_core(inst, cls)


def _test_purepy_isinstance_issubclass():
    class Base1:
        pass
    #
    class Mixin1:
        pass
    #
    class Derived1(Base1):
        pass
    #
    class Derived1_Mixed(Derived1, Mixin1):
        pass
    #
    print(issubclass_purepy(Derived1_Mixed, Base1))
    print(issubclass_purepy(Derived1, Mixin1))
    print(issubclass_purepy(Derived1, (Mixin1, Base1)))

    print(isinstance_purepy(Derived1_Mixed, Base1))
    print(isinstance_purepy(Derived1, Mixin1))
    print(isinstance_purepy(Derived1, (Mixin1, Base1)))

    print(isinstance_purepy(Derived1_Mixed(), Base1))
    print(isinstance_purepy(Derived1(), Mixin1))
    print(isinstance_purepy(Derived1(), (Mixin1, Base1)))


#### Test with auto reload


class Base1:
    ...


class Derived1(Base1):
    ...


class Reloadable(type):
    """
    This is a metaclass that overrides the behavior of isinstance and
    issubclass when invoked on classes derived from this such that they only
    check that the module and class names agree, which are preserved through
    module reloads, whereas class instances are not.

    This is useful for interactive develoment, but should be removed in
    production.
    """

    def __subclasscheck__(cls, sub):
        """
        Is ``sub`` a subclass of ``cls``
        """
        cls_mod_name = (cls.__module__, cls.__name__)
        for b in sub.__mro__:
            b_mod_name = (b.__module__, b.__name__)
            if cls_mod_name == b_mod_name:
                return True

    def __instancecheck__(cls, inst):
        """
        Is ``inst`` an instance of ``cls``
        """
        return cls.__subclasscheck__(inst.__class__)


def add_metaclass_in_IPython(metaclass):
    """
    Class decorator for creating a class with a metaclass.
    But only if we are running in IPython.
    """
    def wrapper(cls):
        try:
            __IPython__
        except NameError:
            return cls
        else:
            orig_vars = cls.__dict__.copy()
            slots = orig_vars.get('__slots__')
            if slots is not None:
                if isinstance(slots, str):
                    slots = [slots]
                for slots_var in slots:
                    orig_vars.pop(slots_var)
            orig_vars.pop('__dict__', None)
            orig_vars.pop('__weakref__', None)
            if hasattr(cls, '__qualname__'):
                orig_vars['__qualname__'] = cls.__qualname__
            return metaclass(cls.__name__, cls.__bases__, orig_vars)
    return wrapper


class Base2(metaclass=Reloadable):
    ...


class Derived2(Base2):
    ...


def import_self():
    import ubelt as ub
    try:
        modpath = __file__
    except NameError:
        # explict pointer to this file, so the test can also be run in IPython
        modpath = ub.Path('~/misc/tests/python/purepython_isinstance.py').expand()
    module = ub.import_module_from_path(modpath)
    return module


def main():
    """
    Demonstrate how reloading a module causes the normal
    isinstance method to fail

    Ignore:
        import sys, ubelt
        sys.path.append(ubelt.expandpath('~/misc/tests/python'))
        from purepython_isinstance import *  # NOQA
    """
    module = import_self()

    inst1 = module.Derived1()
    inst2 = module.Derived2()
    assert isinstance(inst1, module.Base1)
    assert isinstance(inst1, module.Derived1)
    assert isinstance(inst2, module.Base2)
    assert isinstance(inst2, module.Derived2)

    import importlib
    reloaded = importlib.reload(module)

    # Reloading the module "breaks" the isinstance checks for instances
    # created from classes as they were before the reload. But overriding
    # the isinstance check allows us to continue development normally in most
    # cases.

    assert not isinstance(inst1, reloaded.Base1)
    assert not isinstance(inst1, reloaded.Derived1)
    assert isinstance(inst2, reloaded.Base2)
    assert isinstance(inst2, reloaded.Derived2)


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/purepython_isinstance.py
    """
    main()
