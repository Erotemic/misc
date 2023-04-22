

class Group:
    def __init__(self, group):
        self.group = group

    def __enter__(self):
        return self

    def __exit__(self, *args):
        ...

    def value(self, value, *kwargs):
        return {'group': self.group, 'value': value, 'kwargs': kwargs}


class Foo:
    with Group('group') as g:
        a = g.value(1)


class Class1:
    class Class2:
        ...

import scriptconfig as scfg
import ubelt as ub
print('Foo.__dict__ = {}'.format(ub.urepr(dict(Foo.__dict__), nl=2)))


class ValueContext:
    def __init__(self, **common):
        self.common = common

    def __enter__(self):
        return self

    def __exit__(self, *args):
        ...

    def Value(self, value, **kwargs):
        kwargs = ub.udict(self.common) | kwargs
        return scfg.Value(value, **kwargs)


class MyConfig(scfg.DataConfig):
    with ValueContext(group='group') as _g:
        a = _g.Value(1)
        b = _g.Value(2)
        print(vars())
        c = _g.Value(3)
        print(vars())


self = MyConfig()
print('MyConfig.__default__ = {}'.format(ub.urepr(dict(MyConfig.__default__), nl=1)))
print('self = {}'.format(ub.urepr(self, nl=1)))
