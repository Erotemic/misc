
def test_monkeypatch_open():
    import ubelt as ub
    from os.path import join

    code1 = ub.codeblock(
        '''
        import builtins

        def _make_dummy(x):
             def _dummy_open(x):
                return x
             _dummy_open.__name__ = x
             return _dummy_open


        if 0:
            builtins.open = _make_dummy('overwrite-builtins-open-preimport')

        import mod2
        mod2.check_relevant()

        if 1:
            builtins.open = _make_dummy('overwrite-builtins-open')
            mod2.check_relevant()

        if 1:
            mod2.open = _make_dummy('overwrite-mod2-open')
            mod2.check_relevant()
        ''')

    code2 = ub.codeblock(
        '''
        attr1 = 'foo'
        print(open)

        def check_relevant():
            print('--- MOD 2 VARS ---')
            print('attr1 = {!r}'.format(attr1))
            print('open = {!r}'.format(open))
            print('__builtins__["open"] = {!r}'.format(__builtins__['open']))
            print('globals()["open"] = {!r}'.format(globals().get('open', None)))
            open_result = open('foo')
            print('open_result = {!r}'.format(open_result))
        ''')

    dpath = ub.ensure_app_cache_dir('ubelt', 'test_monkeypatch')

    mod1_fpath = join(dpath, 'mod1.py')
    mod2_fpath = join(dpath, 'mod2.py')

    with open(mod1_fpath, 'w') as file:
        file.write(code1)
    with open(mod2_fpath, 'w') as file:
        file.write(code2)

    info = ub.cmd('python mod1.py', cwd=dpath, verbose=3)
