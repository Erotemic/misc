#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ubelt as ub
import re


def parse_require_line(line):
    """
    Parse information from a line in a requirements text file
    """
    info = {}
    if line.startswith('-e '):
        url, package = line.split('#egg=')
        info['package'] = package
        info['raw_url'] = url
    else:
        # Remove versioning from the package
        pat = '(' + '|'.join(['>=', '==', '>']) + ')'
        parts = re.split(pat, line, maxsplit=1)
        parts = [p.strip() for p in parts]

        info['package'] = parts[0]
        if len(parts) > 1:
            op, rest = parts[1:]
            if ';' in rest:
                # Handle platform specific dependencies
                # http://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-platform-specific-dependencies
                version, platform_deps = map(str.strip, rest.split(';'))
                info['platform_deps'] = platform_deps
            else:
                version = rest  # NOQA
            info['version'] = (op, version)
    return info


def parse_requirements_file(require_fpath):
    # Parse what requires currently holds
    requires = {}
    with open(require_fpath, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line and not line.startswith('#'):
                info = parse_require_line(line)
                requires[info['package'].lower()] = info
    return requires


def query_pip_installed():
    # Parse what pip environment currently has
    pip_envs = {}
    out = ub.cmd('pip freeze')['out']
    for line in out.split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            info = parse_require_line(line)
            pip_envs[info['package'].lower()] = info
    return pip_envs


def pip_required_version(require_fpath='requirements.txt'):
    """
    Ignore:
        >>> import ubelt, sys
        >>> sys.path.append(ubelt.truepath('~/misc'))
        >>> from pip_required_versions import *
        >>> import xdev
        >>> globals().update(xdev.get_func_kwargs(pip_required_version))
    """

    requires = parse_requirements_file(require_fpath)
    pip_envs = query_pip_installed()

    missing_req = []
    missing_pypi = []
    disagree = []
    unhandled = []

    for package, req in requires.items():
        try:
            pypi = pip_envs[package]
        except KeyError:
            unhandled.append(package)
        else:
            req_version = req.get('version', None)
            pypi_version = pypi.get('version', None)

            if req_version is None:
                missing_req.append((package, req, pypi))

            elif pypi_version is None:
                missing_pypi.append((package, req, pypi))

            elif req_version[1] != pypi_version[1]:
                disagree.append((package, req, pypi))

    print('\n\n')
    for (package, req, pypi) in missing_req:
        print('MISSING REQUIRES VERSION')
        print('package = {!r}'.format(package))
        print('req = {!r}'.format(req))
        print('pypi = {!r}'.format(pypi))

    print('\n\n')
    for (package, req, pypi) in missing_pypi:
        print('MISSING PYPI VERSION')
        print('package = {!r}'.format(package))
        print('req = {!r}'.format(req))
        print('pypi = {!r}'.format(pypi))

    print('\n\n')
    for (package, req, pypi) in disagree:
        print('DISAGREE VERSION')
        print('package = {!r}'.format(package))
        print('req = {!r}'.format(req))
        print('pypi = {!r}'.format(pypi))

    print('\n\n')
    for package in unhandled:
        print('UNHANDLED ')
        print('package = {!r}'.format(package))


def forgot_what_this_was_for():
    if False:
        want = {}
        versioned = {}
        unversioned = []
        gitversioned = {}

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

        print('versioned ' + ub.repr2(versioned, si=True))
        print('gitversioned ' + ub.repr2(gitversioned, si=True))
        print('unversioned ' + ub.repr2(unversioned, si=True))

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


def main():
    """
    Notes:
        Also:
            pip install pipreqs
            pipreqs --print <pkgname>
    """
    import argparse
    parser = argparse.ArgumentParser(description='Find missing requirements.txt packages and versions')

    parser.add_argument('require_fpath', nargs='?', default='requirements.txt')
    args = parser.parse_args()
    ns = args.__dict__.copy()
    pip_required_version(**ns)


if __name__ == '__main__':
    r"""
    CommandLine:
        export PYTHONPATH=$PYTHONPATH:/home/joncrall/misc
        python ~/misc/pip_required_versions.py
    """
    main()
