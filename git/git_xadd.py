"""
Adds and commits a change to an external (a local branch, but not the one
currently checked out) branch
"""
import git
import sys


def git_xadd(branch, files, message='wip'):
    repo = git.Repo()
    orig_branch_name = repo.active_branch.name

    if branch not in {branch.name for branch in repo.branches}:
        raise ValueError('Branch {!r} does not exist'.format(branch))

    try:
        repo.git.checkout(branch)
        repo.git.add(files)
        repo.git.commit(m=message)
    except Exception:
        raise
    finally:
        repo.git.checkout(orig_branch_name)


def get_varargs(argv=None):
    """
    Returns positional args specified directly after the scriptname
    and before any args starting with '-' on the commandline.
    """
    if argv is None:
        argv = sys.argv
    scriptname = argv[0]
    if scriptname == '':
        # python invoked by iteself
        pos_start = 0
        pos_end = 0
    else:
        pos_start = pos_end = 1
        for idx in range(pos_start, len(argv)):
            if argv[idx].startswith('-'):
                pos_end = idx
                break
        else:
            pos_end = len(argv)
    varargs = argv[pos_start:pos_end]
    return varargs


if __name__ == '__main__':
    r"""
    SeeAlso:
        git_squash_streaks.py

    Ignore:
        python ~/misc/git/git_xadd.py dev/doc_fixes arrows/ocv/split_image.cxx -m "added a bit more info"
        git merge dev/doc_fixes

    CommandLine:
        export PYTHONPATH=$PYTHONPATH:/home/joncrall/misc
        python ~/misc/git_xadd.py
    """
    import ubelt as ub
    message = ub.argval('-m', default='wip')
    varargs = get_varargs()
    branch = varargs[0]
    files = varargs[1:]

    git_xadd(branch, files, message=message)
