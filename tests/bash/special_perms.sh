#!/bin/bash

DPATH=$HOME/temp/test_special_perms
sudo rm -rf "$DPATH"
mkdir -p "$DPATH"
cd "$DPATH"

touch file1
touch file2
touch file3
mkdir -p dir1
mkdir -p dir2
mkdir -p dir3

ls -al

chmod u+s file1
chmod g+s file1

# Does nothing, but is marked as a valid code
chmod o+s file2

# invalid
# chmod u+S file2

# Does nothing, but is marked as a valid code
chmod o+t file2
chmod o+X file3
chmod o+X dir1
chmod o-x dir2
chmod o-x dir3
chmod o+X dir2

# Invalid code
# chmod u=rws,g=rw,o=rwT file2
chmod u=rwxs,g=rwxs,o=rwxt file1
ls -al file2
