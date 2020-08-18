__heredoc__="""
Inspection and demonstration of rsync behaviors so I don't forget them


Notes:
    Putting a '/' at the end of a directory means look inside the directory,
    and compare its contents to the destination.


"""


TEST_BASE=rsync_test

#REMOTE_DPATH=$HOME/remote/$REMOTE

REMOTE_DPATH=$HOME/tmp/test-remote
LOCAL_DPATH=$HOME/tmp/test-local


# CASE 1:
# Use a non-local remote
REMOTE=namek
#mount-remotes.sh $REMOTE
REMOTE_MOUNT=$HOME/remote/$REMOTE/tmp/test-remote
REMOTE_URI=namek:tmp/test-remote


# CASE 2:
# Use a local remote
REMOTE_URI=$REMOTE_DPATH
REMOTE_MOUNT=$REMOTE_DPATH


reset_rsync_test_setup()
{

    # In the case of a non-local setup this must be run on the real server to
    # get correct symlink

    # Clean
    if [ -d "$REMOTE_DPATH/$TEST_BASE" ]; then
        rm -rf $REMOTE_DPATH/$TEST_BASE 
    fi

    mkdir -p $REMOTE_DPATH/$TEST_BASE 


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

    tree $REMOTE_DPATH/$TEST_BASE

    _checks="
    cd $REMOTE_DPATH/$TEST_BASE
    "


    # Setup home data
    if [ -d "$LOCAL_DPATH/$TEST_BASE" ]; then
        rm -rf $LOCAL_DPATH/$TEST_BASE 
    fi
    mkdir -p $LOCAL_DPATH/$TEST_BASE 
    tree $LOCAL_DPATH/$TEST_BASE
    _checks="
    cd $LOCAL_DPATH/$TEST_BASE
    "
}


incorrect_rsync_invoke(){
    reset_rsync_test_setup
    rsync -avrP $REMOTE_DPATH/$TEST_BASE $LOCAL_DPATH/$TEST_BASE
    if [ -d "$LOCAL_DPATH/$TEST_BASE/rsync_test" ]; then
        echo "WE NESTED RSYNC_TEST INSIDE RSYNC_TEST. NOT WANTED"
    fi

    # Incorrect way to invoke part 3
    rsync -avrP $REMOTE_DPATH/$TEST_BASE/./root/dir_L0_X2_D $LOCAL_DPATH/$TEST_BASE
}


correct_rsync_invoke(){

    reset_rsync_test_setup

    # Rsync to empty directory (make sure the "." is in the right place)
    #rsync -avrP $REMOTE_DPATH/$TEST_BASE/./root $LOCAL_DPATH/$TEST_BASE  # This works

    rsync -avrPR $REMOTE_URI/$TEST_BASE/./root $LOCAL_DPATH/$TEST_BASE  # This also works, probably safer

    tree $REMOTE_MOUNT/$TEST_BASE
    tree $LOCAL_DPATH/$TEST_BASE

    if [ -d "$LOCAL_DPATH/$TEST_BASE/rsync_test" ]; then
        echo "WE NESTED RSYNC_TEST INSIDE RSYNC_TEST. NOT WANTED"
    else
        echo "Invoked RSYNC correctly"
    fi

    # Second invoke should be idenpotent
    #rsync -avrP $REMOTE_URI/$TEST_BASE/./root $LOCAL_DPATH/$TEST_BASE  # This works
    rsync -avrPR $REMOTE_URI/$TEST_BASE/./root $LOCAL_DPATH/$TEST_BASE  # This also works, probably safer

    tree $REMOTE_MOUNT/$TEST_BASE
    tree $LOCAL_DPATH/$TEST_BASE

    # Make a new file and resync
    touch $REMOTE_MOUNT/$TEST_BASE/root/dir_L0_X0_A/file_L1_X1_d.txt
    rsync -avrPR $REMOTE_URI/$TEST_BASE/./root $LOCAL_DPATH/$TEST_BASE

    tree $REMOTE_MOUNT/$TEST_BASE
    tree $LOCAL_DPATH/$TEST_BASE

    # Create a new root level directory and file, but only send the directory
    mkdir -p $REMOTE_MOUNT/$TEST_BASE/root/dir_L0_X2_D
    touch $REMOTE_MOUNT/$TEST_BASE/root/dir_L0_X2_D/file_L1_X0_e.txt
    touch $REMOTE_MOUNT/$TEST_BASE/root/file_L0_X1_f.txt

    # need to use R for relative when doing this
    rsync -avrRP $REMOTE_URI/$TEST_BASE/./root/dir_L0_X2_D $LOCAL_DPATH/$TEST_BASE
    tree $REMOTE_MOUNT/$TEST_BASE
    tree $REMOTE_MOUNT/$TEST_BASE

    if [ -f "$LOCAL_DPATH/$TEST_BASE/root/file_L0_X1_f.txt" ]; then
        echo "We should not have synced the file yet"
    else
        echo "Invoked RSYNC correctly"
    fi

    rsync -avrPR $REMOTE_URI/$TEST_BASE/./root/file_L0_X1_f.txt $LOCAL_DPATH/$TEST_BASE
    if [ -f "$LOCAL_DPATH/$TEST_BASE/root/file_L0_X1_f.txt" ]; then
        echo "We correctly synced the file now"
    else
        echo "We should have synced the file yet"
    fi
}

correct_rsync_invoke



rsync -avrP $REMOTE_URI/$TEST_BASE/root/dir_L0_X2_D $LOCAL_DPATH/$TEST_BASE/root/dir_L0_X2_D
tree $LOCAL_DPATH/$TEST_BASE
