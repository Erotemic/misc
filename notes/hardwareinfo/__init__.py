"""
mkinit ~/misc/notes/hardwareinfo/__init__.py --lazy -w --noattr
"""


def lazy_import(module_name, submodules, submod_attrs):
    import importlib
    import importlib.util
    all_funcs = []
    for mod, funcs in submod_attrs.items():
        all_funcs.extend(funcs)
    name_to_submod = {
        func: mod for mod, funcs in submod_attrs.items()
        for func in funcs
    }

    def __getattr__(name):
        if name in submodules:
            attr = importlib.import_module(
                '{module_name}.{name}'.format(
                    module_name=module_name, name=name)
            )
        elif name in name_to_submod:
            modname = name_to_submod[name]
            module = importlib.import_module(
                '{module_name}.{modname}'.format(
                    module_name=module_name, modname=modname)
            )
            attr = getattr(module, name)
        else:
            raise AttributeError(
                'No {module_name} attribute {name}'.format(
                    module_name=module_name, name=name))
        globals()[name] = attr
        return attr
    return __getattr__


__getattr__ = lazy_import(
    __name__,
    submodules=[
        'backend_linux',
    ],
    submod_attrs={},
)


def __dir__():
    return __all__

__all__ = ['backend_linux']
