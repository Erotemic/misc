"""
Looks at the `git_*.{sh,ph}` scripts and makes corresponding `git-*` scripts
"""
import glob
from os.path import dirname, join, basename, splitext
import ubelt as ub


SCRIPT_HEADER = ub.codeblock(
    r'''
    #!/bin/bash
    # References:
    # https://stackoverflow.com/questions/59895/getting-the-source-directory-of-a-bash-script-from-within

    SOURCE="${BASH_SOURCE[0]}"
    while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
      DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
      SOURCE="$(readlink "$SOURCE")"
      [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
    done

    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
    ''')

SCRIPT_FOOTER_FMT = '$DIR/{fname} $@'

def setup_git_commands():
    dpath = dirname(__file__)

    git_sh_scripts = list(glob.glob(join(dpath, 'git_*.sh')))
    git_py_scripts = list(glob.glob(join(dpath, 'git_*.py')))
    git_scripts = git_py_scripts + git_sh_scripts

    for fpath in git_scripts:
        fname = basename(fpath)
        script_text = SCRIPT_HEADER + '\n' + SCRIPT_FOOTER_FMT.format(fname=fname)

        new_fname = splitext(fname)[0].replace('_', '-')
        new_fpath = join(dpath, new_fname)
        print('writing script {!r}'.format(new_fname))
        ub.writeto(new_fpath, script_text)


if __name__ == '__main__':
    r"""
    CommandLine:
        python ~/misc/git/_setup_git_commands.py
    """
    setup_git_commands()
