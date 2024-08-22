"""
Demo how to add real module level properties

The following code follows [SO1060796]_ to enrich a module with class features
like properties, `__call__()`, and `__iter__()`, etc... for Python versions
3.5+.  In the future, if [PEP713]_ is accepted then that will be preferred.
Note that type checking is ignored here because mypy cannot handle callable
modules [MyPy9240]_.

References
----------
.. [SO1060796] https://stackoverflow.com/questions/1060796/callable-modules
.. [PEP713] https://peps.python.org/pep-0713/
.. [MyPy9240] https://github.com/python/mypy/issues/9240

Example
-------
>>> # Assuming this file is in your cwd named "demo_module_properties.py"
>>> import demo_module_properties
>>> print(demo_module_properties.MY_GLOBAL)
0
>>> print(demo_module_properties.our_property1)
we made a module level property with side effects
>>> print(demo_module_properties.MY_GLOBAL)
1
>>> demo_module_properties()
YOU CALLED ME!
>>> print(list(demo_module_properties))
[1, 2, 3]

"""
import sys

MY_GLOBAL = 0


class OurModule(sys.modules[__name__].__class__):  # type: ignore

    def __iter__(self):
        yield from [1, 2, 3]

    def __call__(self, *args, **kwargs):
        print('YOU CALLED ME!')

    @property
    def our_property1(self):
        global MY_GLOBAL
        MY_GLOBAL += 1
        return 'we made a module level property with side effects'


sys.modules[__name__].__class__ = OurModule
del sys, OurModule
