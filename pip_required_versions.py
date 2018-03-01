
def main():
    import ubelt as ub

    want = {}
    versioned = {}
    unversioned = []
    gitversioned = {}

    for line in set(open('requirements.txt').read().split('\n')):
        line = line.strip()
        if not line.startswith('#'):
            if '==' in line:
                key, version = line.split('==')
            if '>=' in line:
                key, version = line.split('>=')
            if '#egg=' in line:
                version, key = line.split('#egg=')
            else:
                key = line
                version = None
            if key:
                want[key] = version
    print('want ' + ub.repr2(want, si=True))

    out = ub.cmd('pip freeze')['out']
    for line in out.split('\n'):
        line = line.strip()
        item = line.split('==')
        if len(item) == 2:
            key, version = item
            versioned[key] = version
        else:
            if '#egg=' in line:
                githash, key = line.split('#egg=')
                gitversioned[key] = githash
            else:
                if line:
                    unversioned.append(line)

    versioned.update(gitversioned)

    # print('versioned ' + ub.repr2(versioned, si=True))
    # print('gitversioned ' + ub.repr2(gitversioned, si=True))
    # print('unversioned ' + ub.repr2(unversioned, si=True))

    unknown = set(want) - set(versioned.keys())
    if unknown:
        print('unknown = {}'.format(ub.repr2(unknown, si=True)))

    have = ub.dict_subset(versioned, set(versioned.keys()).intersection(set(want)))
    print('have ' + ub.repr2(have, si=True))

    outlines = []
    for key, value in have.items():
        if value.startswith('-e'):
            outlines.append('{}#egg={}'.format(value, key))
        else:
            outlines.append('{}=={}'.format(key, value))
    print('\n'.join(sorted(outlines)))

    # print('\n'.join(['=='.join(item) for item in .items()]))


if __name__ == '__main__':
    r"""
    CommandLine:
        export PYTHONPATH=$PYTHONPATH:/home/joncrall/misc
        python ~/misc/pip_required_versions.py
    """
    main()
