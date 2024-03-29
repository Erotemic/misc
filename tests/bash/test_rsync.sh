__heredoc__="""
Inspection and demonstration of rsync behaviors so I don't forget them


Notes:
    Putting a '/' at the end of a directory means look inside the directory,
    and compare its contents to the destination.
    /home/joncrall/misc/tests/bash/test_rsync.sh


    Using --stats with -n will report differences
    
    rsync -avrcn --stats $HOME/data/public_data_registry/.dvc/cache hermes:/data/shared/dvc-cache/public_data_registry
"""


TEST_BASE=rsync_test
#REMOTE_DPATH=$HOME/remote/$REMOTE
REMOTE_DPATH=$HOME/tmp/rsync-test/remote
LOCAL_DPATH=$HOME/tmp/rsync-test/local


# CASE 1:
# Use a non-local remote
REMOTE=namek
#mount-remotes.sh $REMOTE
REMOTE_MOUNT=$HOME/remote/$REMOTE/tmp/rsync-test/remote
REMOTE_URI=namek:tmp/rsync-test/remote


# CASE 2:
# Use a local remote
REMOTE_URI=$REMOTE_DPATH
REMOTE_MOUNT=$REMOTE_DPATH


reset_rsync_test_remote()
{

    # In the case of a non-local setup this must be run on the real server to
    # get correct symlink

    # Clean
    if [ -d "$REMOTE_DPATH" ]; then
        rm -rf "$REMOTE_DPATH"
    fi

    mkdir -p "$REMOTE_DPATH"


    # Setup remote data
    mkdir -p "$REMOTE_DPATH"/$TEST_BASE/root/dir_L0_X0_A
    mkdir -p "$REMOTE_DPATH"/$TEST_BASE/root/dir_L0_X0_A/dir_L1_X0_B
    mkdir -p "$REMOTE_DPATH"/$TEST_BASE/root/dir_L0_X0_A/dir_L1_X0_B2
    mkdir -p "$REMOTE_DPATH"/$TEST_BASE/root/dir_L0_X1_C
    mkdir -p "$REMOTE_DPATH"/$TEST_BASE/root/inside_dir
    mkdir -p "$REMOTE_DPATH"/$TEST_BASE/root/links
    mkdir -p "$REMOTE_DPATH"/$TEST_BASE/outside_dir/

    touch "$REMOTE_DPATH"/$TEST_BASE/root/file_L0_X0_a.txt
    touch "$REMOTE_DPATH"/$TEST_BASE/root/dir_L0_X0_A/file_L1_X0_b.txt
    touch "$REMOTE_DPATH"/$TEST_BASE/root/dir_L0_X0_A/file1.txt
    touch "$REMOTE_DPATH"/$TEST_BASE/root/dir_L0_X0_A/file2.txt
    touch "$REMOTE_DPATH"/$TEST_BASE/root/dir_L0_X0_A/file1.json
    touch "$REMOTE_DPATH"/$TEST_BASE/root/dir_L0_X0_A/file2.json
    touch "$REMOTE_DPATH"/$TEST_BASE/root/dir_L0_X0_A/dir_L1_X0_B2/file1.txt
    touch "$REMOTE_DPATH"/$TEST_BASE/root/dir_L0_X0_A/dir_L1_X0_B2/file2.json
    touch "$REMOTE_DPATH"/$TEST_BASE/root/dir_L0_X1_C/file_L1_X0_c.txt

    touch "$REMOTE_DPATH"/$TEST_BASE/root/inside_dir/inside_file.txt
    touch "$REMOTE_DPATH"/$TEST_BASE/outside_dir/outside_file.txt

    # Create links to inside and outside the sync root
    ln -s "$REMOTE_DPATH"/$TEST_BASE/root/inside_dir/inside_file.txt "$REMOTE_DPATH"/$TEST_BASE/root/links/inside_flink.txt
    ln -s "$REMOTE_DPATH"/$TEST_BASE/outside_dir/outside_file.txt "$REMOTE_DPATH"/$TEST_BASE/root/links/outside_flink.txt
    ln -s "$REMOTE_DPATH"/$TEST_BASE/outside_dir "$REMOTE_DPATH"/$TEST_BASE/root/links/outside_dlink
    ln -s "$REMOTE_DPATH"/$TEST_BASE/root/inside_dir "$REMOTE_DPATH"/$TEST_BASE/root/links/inside_dlink

    ln -sr "$REMOTE_DPATH"/$TEST_BASE/root/inside_dir/inside_file.txt "$REMOTE_DPATH"/$TEST_BASE/root/links/rel_inside_flink.txt
    ln -sr "$REMOTE_DPATH"/$TEST_BASE/outside_dir/outside_file.txt "$REMOTE_DPATH"/$TEST_BASE/root/links/rel_outside_flink.txt
    ln -sr "$REMOTE_DPATH"/$TEST_BASE/outside_dir "$REMOTE_DPATH"/$TEST_BASE/root/links/rel_outside_dlink
    ln -sr "$REMOTE_DPATH"/$TEST_BASE/root/inside_dir "$REMOTE_DPATH"/$TEST_BASE/root/links/rel_inside_dlink

    tree "$REMOTE_DPATH"/

    _checks="
    cd $REMOTE_DPATH/$TEST_BASE
    "
}

reset_rsync_test_local(){
    # Setup home data
    echo "LOCAL_DPATH = $LOCAL_DPATH"
    if [ -d "$LOCAL_DPATH" ]; then
        rm -rf "$LOCAL_DPATH"
    fi
    mkdir -p "$LOCAL_DPATH"
    mkdir -p "$LOCAL_DPATH"/$TEST_BASE

    # Make an existing link on the destination that we will sync to
    mkdir -p "$LOCAL_DPATH"/link-dest1
    mkdir -p "$LOCAL_DPATH"/link-dest2
    ln -s "$LOCAL_DPATH"/link-dest1 "$LOCAL_DPATH"/rsync_test-link
    ln -s "$LOCAL_DPATH"/link-dest2 "$LOCAL_DPATH"/rsync_test-link/root

    tree "$LOCAL_DPATH"
}


incorrect_rsync_invoke(){
    reset_rsync_test_remote
    reset_rsync_test_local

    rsync -avrP "$REMOTE_DPATH"/$TEST_BASE "$LOCAL_DPATH"/$TEST_BASE
    if [ -d "$LOCAL_DPATH/$TEST_BASE/rsync_test" ]; then
        echo "WE NESTED RSYNC_TEST INSIDE RSYNC_TEST. NOT WANTED"
    fi

    # Incorrect way to invoke part 3
    rsync -avrP "$REMOTE_DPATH"/$TEST_BASE/./root/dir_L0_X2_D "$LOCAL_DPATH"/$TEST_BASE

    # Incorrect way to sync to a linked dir
    rsync -avrPR "$REMOTE_URI"/$TEST_BASE/./root "$LOCAL_DPATH"/rsync_test-link  
    ls -al "$LOCAL_DPATH"/
    ls -al "$LOCAL_DPATH"/rsync_test-link/
    if [ ! -L "$LOCAL_DPATH/rsync_test-link/root" ]; then
        echo "
        We got the expected error
        this displays how the previous root (which was a link) was clobbered.
        "
    else
        echo "We did not get the expected error"
    fi
}


demo_stats_command(){

    reset_rsync_test_remote
    reset_rsync_test_local

    rsync -avrPLn --stats "$REMOTE_URI"/$TEST_BASE/root/links/ "$LOCAL_DPATH"/$TEST_BASE/links

    # Create links folder on the destination and copy the hard (K) contents of the links folder from the remote
    rsync -avrPL --stats "$REMOTE_URI"/$TEST_BASE/root/links/ "$LOCAL_DPATH"/$TEST_BASE/links
    rsync -avrPL --stats "$REMOTE_URI"/$TEST_BASE/root/links/ "$LOCAL_DPATH"/$TEST_BASE/links

    tree "$REMOTE_URI"/$TEST_BASE/./root
    tree "$LOCAL_DPATH"/$TEST_BASE

    # First invocation will show:
    #Number of files: 13 (reg: 8, dir: 5)
    #Number of created files: 13 (reg: 8, dir: 5)
    #Number of deleted files: 0
    #Number of regular files transferred: 8

    # Second invocation will show:
    #Number of files: 13 (reg: 8, dir: 5)
    #Number of created files: 0
    #Number of deleted files: 0
    #Number of regular files transferred: 0
    

    # Test sync of the rest of the data
    rsync -avrPLn --stats "$REMOTE_URI"/$TEST_BASE/root/ "$LOCAL_DPATH"/$TEST_BASE/ 
    #Number of files: 22 (reg: 12, dir: 10)
    #Number of created files: 8 (reg: 4, dir: 4)
    #Number of deleted files: 0
    #Number of regular files transferred: 4

    # And actually do it
    rsync -avrPL --stats "$REMOTE_URI"/$TEST_BASE/root/ "$LOCAL_DPATH"/$TEST_BASE/ 
    

    ls "$REMOTE_URI"/$TEST_BASE/./root
    ls "$LOCAL_DPATH"/$TEST_BASE

    tree "$REMOTE_URI"/$TEST_BASE/./root
    tree "$LOCAL_DPATH"/$TEST_BASE

}


correct_rsync_invoke(){

    reset_rsync_test_remote
    reset_rsync_test_local

    # TEST THAT THIS WILL WORK IF WE TRY TO SYNC TO A SYMLINK
    # The -K is important when syncing to a destination dir that is a symlink
    # The -L will resolve any symlinks
    #     this grabs everything however, all files will be copied over as hard files

    # Alternatively using -k --copy-unsafe-links will get almost everything 
    # links inside the relative directory are copied as links, links outside
    # the relative dir are copied as files, except relative outside files for
    # whatever reason. 

    # Remember -a / --archive == -rlptgoD (no -H,-A,-X)

    reset_rsync_test_local
    # It seems -KL is the safest thing if you want to ensure all the files are moved
    # might take extra space though. 
    #rsync -avrPRKk --copy-unsafe-links $REMOTE_URI/$TEST_BASE/./root $LOCAL_DPATH/rsync_test-link  
    rsync -avPRKL "$REMOTE_URI"/$TEST_BASE/./root "$LOCAL_DPATH"/rsync_test-link  
    ls -al "$LOCAL_DPATH"/
    ls -al "$LOCAL_DPATH"/rsync_test-link/
    tree "$LOCAL_DPATH"/link-dest2

    # Rsync to empty directory (make sure the "." is in the right place)
    #rsync -avrP $REMOTE_DPATH/$TEST_BASE/./root $LOCAL_DPATH/$TEST_BASE  # This works

    # NOTE: THIS DOES NOT PRESERVER LINKS
    rsync -avrPR "$REMOTE_URI"/$TEST_BASE/./root "$LOCAL_DPATH"/$TEST_BASE 
    tree "$REMOTE_MOUNT"/$TEST_BASE
    tree "$LOCAL_DPATH"/$TEST_BASE

    if [ -d "$LOCAL_DPATH/$TEST_BASE/rsync_test" ]; then
        echo "WE NESTED RSYNC_TEST INSIDE RSYNC_TEST. NOT WANTED"
    else
        echo "Invoked RSYNC correctly"
    fi

    # Second invoke should be idenpotent
    #rsync -avrP $REMOTE_URI/$TEST_BASE/./root $LOCAL_DPATH/$TEST_BASE  # This works
    rsync -avrPR "$REMOTE_URI"/$TEST_BASE/./root "$LOCAL_DPATH"/$TEST_BASE  # This also works, probably safer

    tree "$REMOTE_MOUNT"/$TEST_BASE
    tree "$LOCAL_DPATH"/$TEST_BASE

    # Make a new file and resync
    touch "$REMOTE_MOUNT"/$TEST_BASE/root/dir_L0_X0_A/file_L1_X1_d.txt
    rsync -avrPR "$REMOTE_URI"/$TEST_BASE/./root "$LOCAL_DPATH"/$TEST_BASE

    tree "$REMOTE_MOUNT"/$TEST_BASE
    tree "$LOCAL_DPATH"/$TEST_BASE

    # Create a new root level directory and file, but only send the directory
    mkdir -p "$REMOTE_MOUNT"/$TEST_BASE/root/dir_L0_X2_D
    touch "$REMOTE_MOUNT"/$TEST_BASE/root/dir_L0_X2_D/file_L1_X0_e.txt
    touch "$REMOTE_MOUNT"/$TEST_BASE/root/file_L0_X1_f.txt

    # need to use R for relative when doing this
    rsync -avrRP "$REMOTE_URI"/$TEST_BASE/./root/dir_L0_X2_D "$LOCAL_DPATH"/$TEST_BASE
    tree "$REMOTE_MOUNT"/$TEST_BASE
    tree "$REMOTE_MOUNT"/$TEST_BASE

    if [ -f "$LOCAL_DPATH/$TEST_BASE/root/file_L0_X1_f.txt" ]; then
        echo "We should not have synced the file yet"
    else
        echo "Invoked RSYNC correctly"
    fi

    rsync -avrPR "$REMOTE_URI"/$TEST_BASE/./root/file_L0_X1_f.txt "$LOCAL_DPATH"/$TEST_BASE
    if [ -f "$LOCAL_DPATH/$TEST_BASE/root/file_L0_X1_f.txt" ]; then
        echo "We correctly synced the file now"
    else
        echo "We should have synced the file yet"
    fi
}

#correct_rsync_invoke
#rsync -avrP $REMOTE_URI/$TEST_BASE/root/dir_L0_X2_D $LOCAL_DPATH/$TEST_BASE/root/dir_L0_X2_D
#tree $LOCAL_DPATH/$TEST_BASE


#correct_rsync_invoke
#rsync -avrP $REMOTE_URI/$TEST_BASE/root/dir_L0_X2_D $LOCAL_DPATH/$TEST_BASE/root/dir_L0_X2_D
#tree $LOCAL_DPATH/$TEST_BASE


reset_rsync_test_local_move(){
    LOCAL_DPATH=$HOME/tmp/rsync-test/local
    MOVE_TEST_ROOT=$LOCAL_DPATH/rsync_move_test
    # Setup home data
    echo "LOCAL_DPATH = $LOCAL_DPATH"
    if [ -d "$LOCAL_DPATH" ]; then
        rm -rf "$LOCAL_DPATH"
    fi
    mkdir -p "$LOCAL_DPATH"
    mkdir -p "$MOVE_TEST_ROOT"
    # Pretend that we accidently botched a move and have a repo inside of a repo
    # so the goal is merge all files from repo/repo into repo
    mkdir -p "$MOVE_TEST_ROOT"/repo/
    mkdir -p "$MOVE_TEST_ROOT"/repo/primes/
    mkdir -p "$MOVE_TEST_ROOT"/repo/perfect/
    mkdir -p "$MOVE_TEST_ROOT"/repo/nat/

    mkdir -p "$MOVE_TEST_ROOT"/repo/repo
    mkdir -p "$MOVE_TEST_ROOT"/repo/repo/primes/
    mkdir -p "$MOVE_TEST_ROOT"/repo/repo/perfect/
    mkdir -p "$MOVE_TEST_ROOT"/repo/repo/nat/

    # Some of the primes ended up in the correct and the botched repo
    touch "$MOVE_TEST_ROOT"/repo/primes/prime02
    touch "$MOVE_TEST_ROOT"/repo/primes/prime05
    touch "$MOVE_TEST_ROOT"/repo/primes/prime13
    touch "$MOVE_TEST_ROOT"/repo/repo/primes/prime03
    touch "$MOVE_TEST_ROOT"/repo/repo/primes/prime11
    # For prime7, lets say there is a conflict in the data contained in the file
    echo "correct data" > "$MOVE_TEST_ROOT"/repo/primes/prime07
    echo "botched data" > "$MOVE_TEST_ROOT"/repo/repo/primes/prime07

    # All of the perfects ended up in the botched repo
    touch "$MOVE_TEST_ROOT"/repo/repo/perfect/perfect006
    touch "$MOVE_TEST_ROOT"/repo/repo/perfect/perfect028
    touch "$MOVE_TEST_ROOT"/repo/repo/perfect/perfect496

    # The naturals have some symlinks, so we need to be careful there
    touch "$MOVE_TEST_ROOT"/repo/nat/nat04
    touch "$MOVE_TEST_ROOT"/repo/nat/nat06

    # basedir nats
    touch "$MOVE_TEST_ROOT"/repo/nat/nat01
    ln -s "$MOVE_TEST_ROOT"/repo/primes/prime02 "$MOVE_TEST_ROOT"/repo/nat/nat02
    (cd "$MOVE_TEST_ROOT"/repo/nat/ && ln -s ../primes/prime05 nat05)
    ln -s "$MOVE_TEST_ROOT"/repo/primes/prime11 "$MOVE_TEST_ROOT"/repo/nat/nat11

    # Botched nats
    touch  "$MOVE_TEST_ROOT"/repo/repo/nat/nat08
    ln -s "$MOVE_TEST_ROOT"/repo/primes/prime07  "$MOVE_TEST_ROOT"/repo/repo/nat/nat07 
    (cd "$MOVE_TEST_ROOT"/repo/repo/nat/ && ln -s  ../primes/prime03 nat03)
    ln -s "$MOVE_TEST_ROOT"/repo/repo/primes/prime11 "$MOVE_TEST_ROOT"/repo/repo/nat/nat11

    tree "$MOVE_TEST_ROOT"
}

test_rsync_merge_folders(){
    __doc__="
    source ~/misc/tests/bash/test_rsync.sh
    "
    reset_rsync_test_local_move

    # Does not work
    #mv $MOVE_TEST_ROOT/repo/repo/* $MOVE_TEST_ROOT/repo
    rsync -avrRP "$MOVE_TEST_ROOT"/repo/./repo "$MOVE_TEST_ROOT"

    tree "$MOVE_TEST_ROOT"

    # Check the content of prime7 to see if it was overwritten or not
    # Ans: the data is not overwritten, only disjoint files are merged in
    cat "$MOVE_TEST_ROOT"/repo/primes/prime07

    # Remove the botched repo
    rm -rf "$MOVE_TEST_ROOT"/repo/repo

    # Note that the broken (nat11) link is overwritten
    tree "$MOVE_TEST_ROOT"

}


test_rsync_files_only(){
    __doc__="
    Demonstrate an invocation that only moves files matching a specific pattern.

    source ~/misc/tests/bash/test_rsync.sh
    "
    reset_rsync_test_remote

    # Test moving selected files from a specific directy
    TEST_FILE_ROOT=$LOCAL_DPATH/rsync_include_file_test
    echo "REMOTE_DPATH = $REMOTE_DPATH"
    echo "TEST_FILE_ROOT = $TEST_FILE_ROOT"
    [ -d "$TEST_FILE_ROOT" ] || rm -rf "$TEST_FILE_ROOT"
    mkdir -p "$TEST_FILE_ROOT"

    tree "$REMOTE_DPATH"
    tree "$TEST_FILE_ROOT"

    # Include only removes list from an existing exclude list, so you must specify --exclude
    rsync -avn --include="/*.txt" --exclude="*" "$REMOTE_DPATH/rsync_test/root/dir_L0_X0_A/" "$TEST_FILE_ROOT"
    rsync -avn --include="/*.json" --exclude="*" "$REMOTE_DPATH/rsync_test/root/dir_L0_X0_A/" "$TEST_FILE_ROOT"

    rsync -avprPRn --include="/*.json" --exclude="*" "$REMOTE_DPATH/rsync_test/root/dir_L0_X0_A/" "$TEST_FILE_ROOT"


}
