
def main():
    from os.path import join
    import six
    import pytest
    import ubelt as ub
    import os
    from xdoctest import static_analysis as static
    dpath = ub.ensure_app_cache_dir('import_abi_test')
    text = ub.codeblock(
        '''
        a = 42
        ''')

    os.chdir(dpath)

    modpath = join(dpath, 'foo.py')
    ub.writeto(modpath, text)
    import foo
    assert foo.a == 42

    tag = static._extension_module_tags()[0]

    # Q: Can augment .py files with an ABI tag
    # A: No
    modpath = join(dpath, 'bar.' + tag + '.py')
    ub.writeto(modpath, text)
    with pytest.raises(ImportError, match=".*No module named .?bar.*"):
        import bar  # NOQA

    # Q: Can we augment .so files with an ABI tag
    # A: Yes (note its not a valid so so it fails)
    modpath = join(dpath, 'baz.' + tag + '.so')
    ub.writeto(modpath, text)
    with pytest.raises(ImportError, match=".*file too short"):
        import baz  # NOQA

    # Q: Can we augment .so files with an **arbitrary** tag?
    # A: No
    modpath = join(dpath, 'buz.' + 'junktag' + '.so')
    ub.writeto(modpath, text)
    with pytest.raises(ImportError, match="No module named .*"):
        import buz  # NOQA

    # Q: Can we augment .so files with an "abi3" tag?
    # A: Yes, but not in python2
    modpath = join(dpath, 'biz.' + 'abi3' + '.so')
    ub.writeto(modpath, text)
    if six.PY3:
        with pytest.raises(ImportError, match=".*file too short"):
            import biz  # NOQA
    else:
        with pytest.raises(ImportError, match="No module named .*"):
            import biz  # NOQA

    # Q: Can we augment .so files with a semi-nice tag?
    # A: No
    modpath = join(dpath, 'spam.' + 'linux' + '.so')
    ub.writeto(modpath, text)
    with pytest.raises(ImportError, match="No module named .*"):
        import spam  # NOQA

    modpath = join(dpath, 'eggs.' + 'cp3-abi3-linux_x86_64' + '.so')
    ub.writeto(modpath, text)
    with pytest.raises(ImportError, match="No module named .*"):
        import eggs  # NOQA

    modpath = join(dpath, 'ham.' + 'py3-none-any' + '.so')
    ub.writeto(modpath, text)
    with pytest.raises(ImportError, match="No module named .*"):
        import ham  # NOQA
