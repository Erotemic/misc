__doc__="
Symlinks take up 1 block on an ext4 filesytem, which is 4Kb even though they
are only 7 bytes of data.



"

mkdir -p $HOME/tmp/symlink_size_test
rm -rf $HOME/tmp/symlink_size_test
mkdir -p $HOME/tmp/symlink_size_test
cd $HOME/tmp/symlink_size_test

mkdir -p $HOME/tmp/symlink_size_test/subdir

# Create a file with some random data
head -c200000000 /dev/urandom > $HOME/tmp/symlink_size_test/some_file

# Meausre disk space before
#/dev/sdd1       479668904  422991788  32241508  93% /
#/dev/sdd1       458G  404G   31G  93% /
df  && df -h
#df  | grep sdd1 && df -h | grep sdd1

# Create a large number of symlinks
END=30000
for i in $(seq 1 $END); do
    echo "$i"
    ln -s $HOME/tmp/symlink_size_test/some_file $HOME/tmp/symlink_size_test/subdir/a_link_$i
done

ls subdir | wc
du -sh *
# 932K

# Measure size reported by du
df  && df -h
#df  | grep sdd1 && df -h | grep sdd1

# Meausre disk space after
#/dev/sdd1       479668904  422994780  32238516  93% /
#/dev/sdd1       458G  404G   31G  93% /

422994780 - 422991788 = 2992
