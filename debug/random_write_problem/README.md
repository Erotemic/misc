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
