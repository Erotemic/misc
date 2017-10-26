"""
Commits a change to a file to some other branch
"""


def git_other_add(branch, files, message=''):
    import git
    repo = git.Repo()


if __name__ == '__main__':
    r"""
    CommandLine:
        export PYTHONPATH=$PYTHONPATH:/home/joncrall/misc
        python ~/misc/git-other-add.py
    """
    args = ut.get_varargs()
