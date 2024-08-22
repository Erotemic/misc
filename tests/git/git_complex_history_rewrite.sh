#!/usr/bin/env bash
__doc__="
Demonstrate how to modify branch state

References:
    .. [PartialRewwrite] https://htmlpreview.github.io/?https://github.com/newren/git-filter-repo/blob/docs/html/git-filter-repo.html#_parent_rewriting_2
    .. [MainSoQuestion] https://stackoverflow.com/questions/72536295/how-to-modify-deeper-git-history-and-keep-recent-commit-structures
    .. [HowRebaseOntoWorks] https://medium.com/swiftblade/how-git-rebase-onto-works-71ff00e3f88c
    .. [SoRebaseOnto] https://stackoverflow.com/questions/1994463/how-to-cherry-pick-a-range-of-commits-and-merge-them-into-another-branch
    .. [GitFilterRepo] https://htmlpreview.github.io/?https://github.com/newren/git-filter-repo/blob/docs/html/git-filter-repo.html
"

GLOBAL_COUNTER=0


next_state_change(){
    GLOBAL_COUNTER=$((GLOBAL_COUNTER + 1))
    THIS_FPATH=subdir/file_$GLOBAL_COUNTER
    echo "state-$GLOBAL_COUNTER" > state
    mkdir -p subdir
    echo "state-$GLOBAL_COUNTER" > $THIS_FPATH
    git add state $THIS_FPATH
    git commit -am "Modify State $GLOBAL_COUNTER"
}

setup_toy_repo(){
    mkdir -p "$HOME/tmp/git-demos/messy-origin"
    rm -rf   "$HOME/tmp/git-demos/messy-origin"
    rm -rf   "$HOME/tmp/git-demos/messy-clone"
    mkdir -p "$HOME/tmp/git-demos/messy-origin"

    GLOBAL_COUNTER=0

    cd "$HOME/tmp/git-demos/messy-origin"
    git init 

    git checkout -b main
    next_state_change
    next_state_change

    git checkout -b branch1
    next_state_change
    next_state_change
    next_state_change

    git checkout -b branch2 main
    next_state_change
    next_state_change
    next_state_change

    git checkout main
    git merge branch2 --no-ff -m "merge commit 1" 
    git merge branch1 --no-ff -m "merge commit 2" 
    # Resolve conflict
    echo "state-8-5" > state
    git add state && git commit -m "Resolved 8-5 merge"

    git checkout -b branch3
    next_state_change
    git tag "Point1"
    next_state_change
    next_state_change
    next_state_change
    next_state_change

    git checkout main
    git merge --no-ff -m "merge commit 3 - WANT TO SQUASH" branch3
    git tag "Point2"

    git checkout -b branch4 main
    next_state_change
    next_state_change
    next_state_change

    git checkout -b branch5 main
    next_state_change
    next_state_change
    next_state_change

    git checkout -b branch6 main
    next_state_change
    next_state_change
    next_state_change

    git checkout branch5
    git merge branch6 --no-ff -m "merge commit 4" 
    echo "state-19-22" > state
    git add state && git commit -m "Resolved 19-22 merge"

    git checkout main
    git merge branch5 --no-ff -m "merge commit 5" 
    git merge branch4 --no-ff -m "merge commit 6" 
    echo "state-19-22-4" > state
    git add state && git commit -m "Resolved 19-22-4 merge"

    git clone "$HOME/tmp/git-demos/messy-origin/.git" "$HOME/tmp/git-demos/messy-clone"
    cd "$HOME/tmp/git-demos/messy-clone"
}


make_squashed_head(){
    COMMIT_A="$1"
    COMMIT_B="$2"
    MESSAGE="$3"
    #
    git checkout "$COMMIT_B"
    git reset --hard "$COMMIT_B"
    git reset --soft "$COMMIT_A"^
    #git reset --mixed "$COMMIT_A"^
    git commit -m "$MESSAGE"
}


squash_between(){
    COMMIT_A="$1"
    COMMIT_B="$2"
    MESSAGE="$3"

    CURR_HEAD=$(git rev-list -n 1 HEAD)
    make_squashed_head "$COMMIT_A" "$COMMIT_B" "$MESSAGE"
    COMMIT_B_PRIME=$(git rev-list -n 1 HEAD)
    git replace "$COMMIT_B" "$COMMIT_B_PRIME"
    git checkout "$CURR_HEAD"
    #git filter-repo --partial --refs "${COMMIT_B}^..${CURR_HEAD}"  --force
    #git filter-repo --partial --refs "${COMMIT_B}^..${CURR_HEAD}"  --force
    git filter-repo --partial --refs "${COMMIT_B}^..HEAD"  --force
}

working_solution(){
    source ~/misc/tests/git/git_complex_history_rewrite.sh
    setup_toy_repo
    COMMIT_A=Point1
    COMMIT_B=Point2
    MESSAGE="Squash Point1-Point2"
    squash_between  "$COMMIT_A" "$COMMIT_B" "$MESSAGE"

    # Test other commit ranges
    COMMIT_A=$(git log --fixed-strings --grep "Modify State 20"  --format=format:%H)
    COMMIT_B=$(git log --fixed-strings --grep "Modify State 22"  --format=format:%H)
    MESSAGE="Squash-20-22"
    squash_between  "$COMMIT_A" "$COMMIT_B" "$MESSAGE"

    COMMIT_A=$(git log --fixed-strings --grep "Modify State 6"  --format=format:%H)
    COMMIT_B=$(git log --fixed-strings --grep "Modify State 8"  --format=format:%H)
    MESSAGE="Squash-6-8"
    squash_between  "$COMMIT_A" "$COMMIT_B" "$MESSAGE"

    COMMIT_A=$(git log --fixed-strings --grep "Modify State 3"  --format=format:%H)
    COMMIT_B=$(git log --fixed-strings --grep "Modify State 5"  --format=format:%H)
    MESSAGE="Squash-3-5"
    squash_between  "$COMMIT_A" "$COMMIT_B" "$MESSAGE"

    COMMIT_A=$(git log --fixed-strings --grep "Modify State 17"  --format=format:%H)
    COMMIT_B=$(git log --fixed-strings --grep "merge commit 5"  --format=format:%H)
    MESSAGE="Squash-17-m5"
    squash_between  "$COMMIT_A" "$COMMIT_B" "$MESSAGE"
}


attempted_solutions(){
    source ~/misc/tests/git/git_complex_history_rewrite.sh
    setup_toy_repo

    make_squashed_head Point1 Point2 "make squashed commits"
    git tag "Point2_prime"

    git replace Point2 Point2_prime
    # Because the modification is in-place, we need to rewrite all the commits
    # between these points to we don't muck up the remote
    # you can instruct filter-branch to ignore commits before Point1:
    #if type git-filter-repo; then
    git filter-repo --partial --refs Point2^..main  --force
    #else
    #    echo "dont use filter-branch, use filter-repo"
    #    FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --tag-name-filter cat Point2 main
    #fi
    git co -b new_main
    git push origin
}


 failed_solutions(){
    # This seems to work
    #git replace Point2 Point2_prime
    #git filter-repo --force

    # The state is now guarenteed to be the same as Point2, but the history has
    # been modified to our liking. Now we need to replay all the other commits
    # on top of this.

    # Based on answers in this SO post:
    # https://stackoverflow.com/questions/1994463/how-to-cherry-pick-a-range-of-commits-and-merge-them-into-another-branch

    #COMMIT_A=$(git rev-list -n 1 Point2)
    #COMMIT_B=$(git rev-list -n 1 main)
    #echo "COMMIT_A = $COMMIT_A"
    #echo "COMMIT_B = $COMMIT_B"
    ## I've tried the following, but they do not seem to work.
    ## Try with cherry pick
    #git cherry-pick "${COMMIT_A}..${COMMIT_B}" 
    ## Try with rebase onto
    #git rebase "$COMMIT_A" "$COMMIT_B"~0 --onto HEAD
    #git rebase Point2 main --onto HEAD --rebase-merges

    #git config rerere.enabled true --local
    #git config rerere.autoupdate true  --local
    git rebase 85a82de143af360419a3fdccc22ab30491b4d17c Point2 --onto Point2_prime --rebase-merges=rebase-cousins -s ours  -v --no-ff
    git rebase Point2 new_main --onto Point2_prime --rebase-merges=rebase-cousins --rerere-autoupdate  -m -s theirs --no-ff -v

    git co main
    git rebase -r --onto Point2_prime Point2 -s ours
}
