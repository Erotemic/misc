
TEST_BASE=rsync_test
REMOTE_DPATH=$HOME/tmp/rsync-test/remote
LOCAL_DPATH=$HOME/tmp/rsync-test/local
REMOTE_URI=$REMOTE_DPATH
REMOTE_MOUNT=$REMOTE_DPATH


reset_rsync_test_remote()
{
    # Clean
    if [ -d "$REMOTE_DPATH" ]; then
        rm -rf $REMOTE_DPATH
    fi

    mkdir -p $REMOTE_DPATH

    # Setup remote data
    mkdir -p $REMOTE_DPATH/$TEST_BASE/root/dir_L0_X0_A
    mkdir -p $REMOTE_DPATH/$TEST_BASE/root/dir_L0_X0_A/dir_L1_X0_B
    mkdir -p $REMOTE_DPATH/$TEST_BASE/root/dir_L0_X1_C
    mkdir -p $REMOTE_DPATH/$TEST_BASE/root/inside_dir
    mkdir -p $REMOTE_DPATH/$TEST_BASE/root/links
    mkdir -p $REMOTE_DPATH/$TEST_BASE/outside_dir/

    touch $REMOTE_DPATH/$TEST_BASE/root/file_L0_X0_a.txt
    touch $REMOTE_DPATH/$TEST_BASE/root/dir_L0_X0_A/file_L1_X0_b.txt
    touch $REMOTE_DPATH/$TEST_BASE/root/dir_L0_X1_C/file_L1_X0_c.txt

    touch $REMOTE_DPATH/$TEST_BASE/root/inside_dir/inside_file.txt
    touch $REMOTE_DPATH/$TEST_BASE/outside_dir/outside_file.txt

    # Create links to inside and outside the sync root
    ln -s $REMOTE_DPATH/$TEST_BASE/root/inside_dir/inside_file.txt $REMOTE_DPATH/$TEST_BASE/root/links/inside_flink.txt
    ln -s $REMOTE_DPATH/$TEST_BASE/outside_dir/outside_file.txt $REMOTE_DPATH/$TEST_BASE/root/links/outside_flink.txt
    ln -s $REMOTE_DPATH/$TEST_BASE/outside_dir $REMOTE_DPATH/$TEST_BASE/root/links/outside_dlink
    ln -s $REMOTE_DPATH/$TEST_BASE/root/inside_dir $REMOTE_DPATH/$TEST_BASE/root/links/inside_dlink

    ln -sr $REMOTE_DPATH/$TEST_BASE/root/inside_dir/inside_file.txt $REMOTE_DPATH/$TEST_BASE/root/links/rel_inside_flink.txt
    ln -sr $REMOTE_DPATH/$TEST_BASE/outside_dir/outside_file.txt $REMOTE_DPATH/$TEST_BASE/root/links/rel_outside_flink.txt
    ln -sr $REMOTE_DPATH/$TEST_BASE/outside_dir $REMOTE_DPATH/$TEST_BASE/root/links/rel_outside_dlink
    ln -sr $REMOTE_DPATH/$TEST_BASE/root/inside_dir $REMOTE_DPATH/$TEST_BASE/root/links/rel_inside_dlink

    tree $REMOTE_DPATH/
}

reset_rsync_test_local(){
    # Setup home data
    echo "LOCAL_DPATH = $LOCAL_DPATH"
    if [ -d "$LOCAL_DPATH" ]; then
        rm -rf $LOCAL_DPATH
    fi
    mkdir -p $LOCAL_DPATH
    mkdir -p $LOCAL_DPATH/$TEST_BASE

    # Make an existing link on the destination that we will sync to
    mkdir -p $LOCAL_DPATH/link-dest1
    mkdir -p $LOCAL_DPATH/link-dest2
    ln -s $LOCAL_DPATH/link-dest1 $LOCAL_DPATH/rsync_test-link
    ln -s $LOCAL_DPATH/link-dest2 $LOCAL_DPATH/rsync_test-link/root

    tree $LOCAL_DPATH
}

reset_rsync_test_remote

# Method 1 with -KL
# The -K is important when syncing to a destination dir that is a symlink
# The -L will resolve any symlinks
#     this grabs everything however, all files will be copied over as hard files

#       -L, --copy-links
#              When  symlinks  are encountered, the item that they point to (the referent) is copied, rather than
#              the symlink.  In older versions of rsync, this option also had  the  side-effect  of  telling  the
#              receiving  side  to  follow  symlinks, such as symlinks to directories.  In a modern rsync such as
#              this one, you’ll need to specify --keep-dirlinks (-K) to get this extra behavior.  The only excep‐
#              tion  is  when  sending files to an rsync that is too old to understand -K -- in that case, the -L
#              option will still have the side-effect of -K on that older receiving rsync.

reset_rsync_test_local
rsync -avPRKL $REMOTE_URI/$TEST_BASE/./root $LOCAL_DPATH/rsync_test-link  
ls -al $LOCAL_DPATH/
ls -al $LOCAL_DPATH/rsync_test-link/
tree $LOCAL_DPATH/link-dest2

# Method 2: with  -Kk --copy-unsafe-links
# Alternatively using -k --copy-unsafe-links will get almost everything 
# links inside the relative directory are copied as links, links outside
# the relative dir are copied as files, except relative outside files for
# whatever reason. 

#       -K, --keep-dirlinks
#              This option causes the receiving side to treat a symlink to a directory as though it were  a  real
#              directory,  but  only  if  it  matches a real directory from the sender.  Without this option, the
#              receiver’s symlink would be deleted and replaced with a real directory.

#       --copy-unsafe-links
#              This tells rsync to copy the referent of symbolic links that point outside the copied tree.  Abso‐
#              lute  symlinks  are  also  treated like ordinary files, and so are any symlinks in the source path
#              itself when --relative is used.  This option has no additional effect  if  --copy-links  was  also
#              specified.

#       -k, --copy-dirlinks
#              This option causes the sending side to treat a symlink to a directory as though  it  were  a  real
#              directory.   This  is useful if you don’t want symlinks to non-directories to be affected, as they
#              would be using --copy-links.

# Method 2: with  -Kk --copy-unsafe-links
# Alternatively using -k --copy-unsafe-links will get almost everything 
# links inside the relative directory are copied as links, links outside
# the relative dir are copied as files, except relative outside files for
# whatever reason. 

# Method 2: with  -Kk --copy-unsafe-links
# Alternatively using -k --copy-unsafe-links will get almost everything 
# links inside the relative directory are copied as links, links outside
# the relative dir are copied as files, except relative outside files for
# whatever reason. 
reset_rsync_test_local
rsync -avPRKk --copy-unsafe-links $REMOTE_URI/$TEST_BASE/./root $LOCAL_DPATH/rsync_test-link  
ls -al $LOCAL_DPATH/
ls -al $LOCAL_DPATH/rsync_test-link/
tree $LOCAL_DPATH/link-dest2
