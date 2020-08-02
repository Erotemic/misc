__heredoc__="""
Inspection and demonstration of rsync behaviors so I don't forget them


Notes:
    Putting a '/' at the end of a directory means look inside the directory,
    and compare its contents to the destination.


"""

REMOTE=namek
mount-remotes.sh $REMOTE

TEST_BASE=tmp/rsync_test
REMOTE_MOUNT=$HOME/remote/$REMOTE
REMOTE_BASE=$HOME/remote/

reset_rsync_test_setup()
{
    # Clean
    if [ -d "$REMOTE_MOUNT/$TEST_BASE" ]; then
        rm -rf $REMOTE_MOUNT/$TEST_BASE 
    fi

    if [ -d "$HOME/$TEST_BASE" ]; then
        rm -rf $HOME/$TEST_BASE 
    fi

    mkdir -p $REMOTE_MOUNT/$TEST_BASE 
    mkdir -p $HOME/$TEST_BASE 


    # Setup remote data
    mkdir -p $REMOTE_MOUNT/$TEST_BASE/root/dir_L0_X0_A
    mkdir -p $REMOTE_MOUNT/$TEST_BASE/root/dir_L0_X0_A/dir_L1_X0_B
    mkdir -p $REMOTE_MOUNT/$TEST_BASE/root/dir_L0_X1_C

    touch $REMOTE_MOUNT/$TEST_BASE/root/file_L0_X0_a.txt
    touch $REMOTE_MOUNT/$TEST_BASE/root/dir_L0_X0_A/file_L1_X0_b.txt
    touch $REMOTE_MOUNT/$TEST_BASE/root/dir_L0_X1_C/file_L1_X0_c.txt


    tree $REMOTE_MOUNT/$TEST_BASE
    tree $HOME/$TEST_BASE
}


incorrect_rsync_invoke(){
    reset_rsync_test_setup
    rsync -avrP $REMOTE_MOUNT/$TEST_BASE $HOME/$TEST_BASE
    if [ -d "$HOME/$TEST_BASE/rsync_test" ]; then
        echo "WE NESTED RSYNC_TEST INSIDE RSYNC_TEST. NOT WANTED"
    fi

    # Incorrect way to invoke part 3
    rsync -avrP $REMOTE_MOUNT/$TEST_BASE/./root/dir_L0_X2_D $HOME/$TEST_BASE
}


correct_rsync_invoke(){

    reset_rsync_test_setup

    # Rsync to empty directory (make sure the "." is in the right place)
    #rsync -avrP $REMOTE_MOUNT/$TEST_BASE/./root $HOME/$TEST_BASE  # This works

    rsync -avrPR $REMOTE_MOUNT/$TEST_BASE/./root $HOME/$TEST_BASE  # This also works, probably safer

    tree $REMOTE_MOUNT/$TEST_BASE
    tree $HOME/$TEST_BASE

    if [ -d "$HOME/$TEST_BASE/rsync_test" ]; then
        echo "WE NESTED RSYNC_TEST INSIDE RSYNC_TEST. NOT WANTED"
    else
        echo "Invoked RSYNC correctly"
    fi

    # Second invoke should be idenpotent
    #rsync -avrP $REMOTE_MOUNT/$TEST_BASE/./root $HOME/$TEST_BASE  # This works
    rsync -avrPR $REMOTE_MOUNT/$TEST_BASE/./root $HOME/$TEST_BASE  # This also works, probably safer

    tree $REMOTE_MOUNT/$TEST_BASE
    tree $HOME/$TEST_BASE

    # Make a new file and resync
    touch $REMOTE_MOUNT/$TEST_BASE/root/dir_L0_X0_A/file_L1_X1_d.txt
    rsync -avrPR $REMOTE_MOUNT/$TEST_BASE/./root $HOME/$TEST_BASE

    tree $REMOTE_MOUNT/$TEST_BASE
    tree $HOME/$TEST_BASE

    # Create a new root level directory and file, but only send the directory
    mkdir -p $REMOTE_MOUNT/$TEST_BASE/root/dir_L0_X2_D
    touch $REMOTE_MOUNT/$TEST_BASE/root/dir_L0_X2_D/file_L1_X0_e.txt
    touch $REMOTE_MOUNT/$TEST_BASE/root/file_L0_X1_f.txt

    # need to use R for relative when doing this
    rsync -avrRP $REMOTE_MOUNT/$TEST_BASE/./root/dir_L0_X2_D $HOME/$TEST_BASE
    tree $REMOTE_MOUNT/$TEST_BASE
    tree $HOME/$TEST_BASE

    if [ -f "$HOME/$TEST_BASE/root/file_L0_X1_f.txt" ]; then
        echo "We should not have synced the file yet"
    else
        echo "Invoked RSYNC correctly"
    fi

    rsync -avrPR $REMOTE_MOUNT/$TEST_BASE/./root/file_L0_X1_f.txt $HOME/$TEST_BASE
    if [ -f "$HOME/$TEST_BASE/root/file_L0_X1_f.txt" ]; then
        echo "We correctly synced the file now"
    else
        echo "We should have synced the file yet"
    fi
}

correct_rsync_invoke



rsync -avrP $REMOTE_MOUNT/$TEST_BASE/root/dir_L0_X2_D $HOME/$TEST_BASE/root/dir_L0_X2_D
tree $HOME/$TEST_BASE
