"""
References:
    https://stackoverflow.com/questions/36745577/how-do-you-create-in-python-a-file-with-permissions-other-users-can-write
"""

import ubelt as ub
import safer
import os
dpath = ub.Path.appdir('misc/tests/file_perm_with_open').delete().ensuredir()

new_fpath1 = dpath / 'fpath_builtin_open.txt'
with open(new_fpath1, 'w') as f:
    f.write('foo')

new_fpath2 = dpath / 'fpath_os_open.txt'
descriptor = os.open(
    path=new_fpath2,
    flags=(
        os.O_WRONLY  # access mode: write only
        | os.O_CREAT  # create if not exists
        | os.O_TRUNC  # truncate the file to zero
    ),
    mode=0o640
)
with open(descriptor, 'w') as f:
    f.write('some text')

new_fpath3 = dpath / 'fpath_safer_open_defualt.txt'
with safer.open(new_fpath3, 'w') as f:
    f.write('safer without tempfile')


new_fpath4 = dpath / 'fpath_safer_open_temp.txt'
with safer.open(new_fpath4, 'w', temp_file=True) as f:
    f.write('safer with tempfile')

_ = ub.cmd('ls -al', cwd=dpath, verbose=3)
