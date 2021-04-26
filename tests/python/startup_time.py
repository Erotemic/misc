def test_startup_time():
    import ubelt as ub
    cmdlist = [
        '/usr/bin/python2',
        '/usr/bin/python3',
        # '/home/joncrall/venv3.6/bin/python3',
        '/home/joncrall/.local/conda/envs/py36/bin/python',
    ]
    for exe in cmdlist:
        print('\n==========\nexe = {!r}'.format(exe))
        for opts in ['', '-B', '-S', '-OO']:
            args = ' -c "import argparse"'
            command = exe + ' ' + opts + args
            for timer in ub.Timerit(50, bestof=5, label=repr(command), verbose=1):
                with timer:
                    ub.cmd(command)


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/startup_time.py
    """
    test_startup_time()
