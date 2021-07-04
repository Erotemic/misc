"""
Conclusions:

    * Calling a classmethod from an instance does not pass instance information
      to the underlying function, you just get the type instead.

    * Calling a regular method as a classmethod works in Python 3, but has
      caveats. If you call it as a classmethod it works as a literal function
      so, no class information is passed to it.

"""
import ubelt as ub


def compat_multiargs_classmethod(func):
    import six
    if six.PY2:
        def _py2_wrap(self, *args, **kw):
            # Not sure if this is possible to implement. Maybe with a
            # metaclass? Either way if Python 2 support isn't needed this isn't
            # a problem.
            return func(*args, **kw)
        return _py2_wrap
    else:
        return func


class MyType(object):
    def __repr__(self):
        return ub.color_text('<AnInstance>', 'yellow')

    @classmethod
    def classmethod_self_args(self, *args):
        print(' * self = {!r}'.format(self))
        print(' * args = {!r}'.format(args))

    @classmethod
    def classmethod_args(*args):
        print(' * args = {!r}'.format(args))
        pass

    # Fails on Python 2 and 3
    def method_self_args(self, *args):
        print(' * self = {!r}'.format(self))
        print(' * args = {!r}'.format(args))

    # Fails on Python 2, but has behavior we want on Python3
    def method_args(*args):
        print(' * args = {!r}'.format(args))

    @compat_multiargs_classmethod
    def compat_method_args(*args):
        print(' * args = {!r}'.format(args))


def main():
    import sys
    print(ub.color_text(' === TEST MULTIARG CLASSMETHOD ===', 'blue'))
    print('sys.version_info = {!r}'.format(sys.version_info))

    unbound_methods = {
        # 'classmethod_self_args': MyType.classmethod_self_args,
        # 'classmethod_args': MyType.classmethod_args,
        # 'method_self_args': MyType.method_self_args,
        'method_args': MyType.method_args,
        'compat_method_args': MyType.compat_method_args,
    }

    for key, unbound in unbound_methods.items():
        print('---')
        print('key = {!r}'.format(key))
        print('unbound = {!r}'.format(unbound))
        try:
            instance = MyType()
            print('instance = {!r}'.format(instance))

            bound = getattr(instance, key)
            print('bound = {!r}'.format(bound))

            print('Call as classmethod with 2 args')
            unbound(instance, 42)
            unbound(32, 42)

            print('Call as bound method with 2 args')
            bound(instance, 42)
            bound(32, 42)

            print('Call as classmethod with 1 args')
            unbound(instance)
            unbound(32)

            print('Call as bound method with 1 args')
            bound(instance)
            bound(32)

            print('Call as classmethod with 0 args')
            unbound()

            print('Call as bound method with 0 args')
            bound()

        except Exception as ex:
            print(ub.color_text('XXX ex = {!r}'.format(ex), 'red'))
        else:
            print(ub.color_text('OOO worked', 'green'))


if __name__ == '__main__':
    """
    CommandLine:
        /home/joncrall/.pyenv/versions/2.7.18/envs/pyenv2.7.18/bin/python ~/misc/tests/python/test_multiarg_classmethod.py && \
        /home/joncrall/.pyenv/versions/3.6.13/envs/pyenv3.6.13/bin/python3 ~/misc/tests/python/test_multiarg_classmethod.py && \
        /home/joncrall/.pyenv/versions/3.8.9/envs/pyenv3.8.9/bin/python3 ~/misc/tests/python/test_multiarg_classmethod.py
    """
    main()
