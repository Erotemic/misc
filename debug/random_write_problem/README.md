This folder is a place where I will store a collection of files that are the
symptom of some issue in my stack. The symptom I'm seeing is that sometimes on
disk there are these seemingly random files that are usually named with some
string I had just been typing and the contents seem to be the output of some
command, but I'm not sure if there is a pattern or not.

I have been experiencing this problem for some time and I haven't been able to
determine what the cause is. To see if there is a better pattern that I can
spot I'm going to move and archive these files here as I find them to hopefully
ultimately fix the issue.

The symptoms directory will mirror my home directory and relative to it will be
where I found the errant file.


It might be worth using a LoggedFS filesystem to figure out what program is
actually doing the writing.

Currently I *think* it is gvim, but I'm not sure.


To archive a file when it is found run:

```bash

python ~/misc/debug/random_write_problem/archive_symptom.py  <path-to-file>


To check the status of the files run:
cd ~/misc/debug/random_write_problem

tree symptoms

find symptoms/ -type f -iname '*' \
    -exec echo "+====" \; \
    -exec echo Inspect File: {} \; \
    -exec stat {} \; \
    -exec echo "+====" \; \
    -exec cat {} \; \
    -exec echo "L____" \; \
```


UPDATE 2023-01-29:

I've observed the behavior in a much simpler context: INSIDE A DOCKER
CONTAINER.  This separates it from a large swatch of my environment
customizations. As such I can't archive the files, but I can describe them.

The context is using xdev freshpyenv --image=python:3.11 on the ibeis repo

After running some sequence of resetdbs, git pull, pytest, and ./run_doctests I
saw the following file structure at 23:58 UTC (the docker clock is UTC, so it
was 18:53 EST).

```
-rw-r--r--  1 root root        97 Jan 29 19:52 '='
-rw-r--r--  1 root root       318 Jan 29 19:52 '=0.1.1'
```


The contents were:

```
(venv311) root@52dfce4c490f:~/repo# cat "="
Requirement already satisfied: vtool_ibeis_ext in ./venv311/lib/python3.11/site-packages (0.1.1)

(venv311) root@52dfce4c490f:~/repo# cat "=0.1.1" 
Requirement already satisfied: vtool_ibeis_ext in ./venv311/lib/python3.11/site-packages (0.1.1)
Requirement already satisfied: numpy in ./venv311/lib/python3.11/site-packages (from vtool_ibeis_ext) (1.24.1)
Requirement already satisfied: ubelt in ./venv311/lib/python3.11/site-packages (from vtool_ibeis_ext) (1.2.3)
```

Other files in the repo were:

```
-rw-r--r--  1 root root        39 Jan 29 19:12  conda_requires.py
-rwxr-xr-x  1 root root       275 Jan 29 19:12  clean.sh
-rw-r--r--  1 root root     11341 Jan 29 19:12  LICENSE
-rw-r--r--  1 root root     10836 Jan 29 19:12  .travis.yml
-rw-r--r--  1 root root       423 Jan 29 19:12  .readthedocs.yml
-rw-r--r--  1 root root       456 Jan 29 19:12  .gitignore
drwxr-xr-x  3 root root      4096 Jan 29 19:12  .github
-rw-r--r--  1 root root       228 Jan 29 19:12  .gitattributes
drwxr-xr-x  3 root root      4096 Jan 29 19:12  docs
drwxr-xr-x  7 root root      4096 Jan 29 19:12  dev
-rwxr-xr-x  1 root root     26800 Jan 29 19:12  super_setup.py
-rwxr-xr-x  1 root root       459 Jan 29 19:12  run_tests.py
-rwxr-xr-x  1 root root        85 Jan 29 19:12  run_linter.sh
-rwxr-xr-x  1 root root        58 Jan 29 19:12  run_doctests.sh
-rwxr-xr-x  1 root root       155 Jan 29 19:12  run_developer_setup.sh
-rw-r--r--  1 root root        83 Jan 29 19:12  requirements.txt
-rwxr-xr-x  1 root root     14111 Jan 29 19:12  publish.sh
drwxr-xr-x  5 root root      4096 Jan 29 19:35  venv311
drwxr-xr-x  3 root root      4096 Jan 29 19:36  tests
drwxr-xr-x  3 root root      4096 Jan 29 19:36  .pytest_cache
-rw-r--r--  1 root root        97 Jan 29 19:52 '='
-rw-r--r--  1 root root       318 Jan 29 19:52 '=0.1.1'
drwxr-xr-x  2 root root      4096 Jan 29 19:54  ibeis.egg-info
drwxrwxrwx  4 root root      4096 Jan 29 20:06  testdb0
-rw-rw-rw-  1 root root 224381870 Jan 29 20:07  PZ_MTEST.zip
drwxrwxrwt  6 root root      4096 Jan 29 20:07  PZ_MTEST
-rw-rw-rw-  1 root root    512820 Jan 29 20:07  NAUT_test.zip
-rw-rw-rw-  1 root root 117131585 Jan 29 20:07  testdb2.tar.gz
drwxrwxr-x  5 1000 1000      4096 Jan 29 20:07  testdb2
drwxrwxrwt  7 root root      4096 Jan 29 20:12  NAUT_test
drwxrwxrwt  5 root root      4096 Jan 29 20:13  testdb1
drwx------  1 root root      4096 Jan 29 20:20  ..
-rw-r--r--  1 root root     13082 Jan 29 20:23  README.rst
-rw-r--r--  1 root root       992 Jan 29 20:23  CHANGELOG.md
drwxr-xr-x  2 root root      4096 Jan 29 20:29  requirements
drwxrwxrwx  2 root root     20480 Jan 29 20:34  htmlcov
-rwxr-xr-x  1 root root      9318 Jan 29 23:45  setup.py
-rw-r--r--  1 root root      1627 Jan 29 23:45  pyproject.toml
drwxr-xr-x 15 root root      4096 Jan 29 23:45  ibeis
drwxr-xr-x  8 root root      4096 Jan 29 23:45  .git
-rw-r--r--  1 root root   1261568 Jan 29 23:51  .coverage
-rw-rw-rw-  1 root root         3 Jan 29 23:51  tempfile2.txt
-rw-r--r--  1 root root         3 Jan 29 23:51  tempfile1.txt
drwxr-xr-x 19 root root      4096 Jan 29 23:51  .
drwxrwxrwx  4 root root      4096 Jan 29 23:51  testdb_dst
-rw-rw-rw-  1 root root      4971 Jan 29 23:52  vsone.zebra_plains.match_state.RF.107.ymgraivvsgfsiozg.cPkl.meta.json
-rw-rw-rw-  1 root root   1136630 Jan 29 23:52  vsone.zebra_plains.match_state.RF.107.ymgraivvsgfsiozg.cPkl
```

Indicating that whatever wrote the rouge files happened about 40 minutes after
I initially cloned the repo.
