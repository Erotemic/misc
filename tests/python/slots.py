
USE_SLOTS = 0


class BaseClass:
    if USE_SLOTS:
        __slots__ = ('base_attr',)
    def __init__(self):
        self.base_attr = 1


class DerivedClass_V1(BaseClass):
    if USE_SLOTS:
        __slots__ = ('base_attr', 'extended_attr')
    def __init__(self):
        super().__init__()
        self.extended_attr = 1


class DerivedClass_V2(BaseClass):
    if USE_SLOTS:
        __slots__ = BaseClass.__slots__ + ('extended_attr',)
    def __init__(self):
        super().__init__()
        self.extended_attr = 1


class MixinClass:
    if USE_SLOTS:
        __slots__ = tuple()
    def foobar(self):
        return 1


class DerivedClassWithMixin(BaseClass, MixinClass):
    if USE_SLOTS:
        __slots__ = ('base_attr', 'extended_attr')
    def __init__(self):
        super().__init__()
        self.extended_attr = 1


obj_base = BaseClass()
obj_derived_v1 = DerivedClass_V1()
obj_derived_v2 = DerivedClass_V2()
obj_derived_with_mixin = DerivedClassWithMixin()

if USE_SLOTS:
    assert not hasattr(obj_base, '__dict__')
    assert not hasattr(obj_derived_v1, '__dict__')
    assert not hasattr(obj_derived_v2, '__dict__')
    assert not hasattr(obj_derived_with_mixin, '__dict__')
else:
    assert hasattr(obj_base, '__dict__')
    assert hasattr(obj_derived_v1, '__dict__')
    assert hasattr(obj_derived_v2, '__dict__')
    assert hasattr(obj_derived_with_mixin, '__dict__')
