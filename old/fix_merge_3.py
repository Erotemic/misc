# http://tedfelix.com/software/git-conflict-resolution.html


def resolve_diff3_conflict(text, mode='OURS'):

    lines = text.splitlines(keepends=True)
    new_lines = []
    state = 'NULL'
    for line in reversed(lines):
        if state == 'NULL':
            if line.startswith('>>>>>>> '):
                state = 'THEIRS'
                continue
        elif state == 'THEIRS':
            if line.startswith('======='):
                state = 'ANCESTORS'
                continue
        elif state == 'ANCESTORS':
            if line.startswith('|||||||'):
                state = 'OURS'
                continue
        elif state == 'OURS':
            if line.startswith('<<<<<<< '):
                state = 'NULL'
                continue

        if state == 'NULL':
            new_lines.append(line)
        elif state == mode:
            new_lines.append(line)
        # elif state == 'THEIRS':
        #     pass
        # elif state == 'ANCESTORS':
        #     pass
        # elif state == 'OURS':
        #     new_lines.append(line)

    return ''.join(new_lines[::-1])


if __name__ == '__main__':
    r"""
    CommandLine:
        export PYTHONPATH=$PYTHONPATH:/home/joncrall/misc
        python ~/misc/fix_merge_3.py
    """
    import sys
    argv = sys.argv[1:]

    import ubelt as ub
    fpaths = ub.cmd('git diff --name-only --diff-filter=U')['out'].splitlines()
    print('fpaths = {!r}'.format(fpaths))
    for fpath in fpaths:
        text = ub.readfrom(fpath)
        text = resolve_diff3_conflict(text)
        # print(text)
        ub.writeto(fpath, text)
