def barron_mwe_error_unicode_literal():
    import textwrap
    import redbaron


    # This works properly
    text = textwrap.dedent(
        '''
        p1, p2 = (1, 2)
        ''').strip('\n')
    red = redbaron.RedBaron(text)

    # But this fails when we use unicode symbols for identifiers
    text = textwrap.dedent(
        '''
        ρ1, ρ2 = (1, 2)
        ''').strip('\n')
    red = redbaron.RedBaron(text)

    # Still fails with a single unicdoe element
    text = textwrap.dedent(
        '''
        ρ2 = 2
        ''').strip('\n')
    red = redbaron.RedBaron(text)

    # Still fails with different unicode identifiers even with explicit
    # unicode literal futures
    text = textwrap.dedent(
        '''
        from __future__ import unicode_literals
        θ = 2
        ''').strip('\n')
    red = redbaron.RedBaron(text)


    # System information
    import sys
    print('sys.version_info = {!r}'.format(sys.version_info))
    import ubelt as ub
    _ = ub.cmd('pip list | grep redbaron', shell=True, verbose=1)


def barron_mwe_error_dict_unpack():
    import textwrap
    import redbaron
    text = textwrap.dedent(
        '''
        d1 = {1: 2}
        d2 = {3: 4}
        d_combo = {**d1, **d2}
        ''').strip('\n')

    # This code should work
    exec(text)

    # But it does not
    red = redbaron.RedBaron(text)

    # import parso
    # p = parso.parse(text)
