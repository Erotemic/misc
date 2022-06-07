#!/bin/bash
__doc__="
Demonstrate how to modify branch state

References:
https://stackoverflow.com/questions/72536295/how-to-modify-deeper-git-history-and-keep-recent-commit-structures
"

setup_toy_repo(){
    mkdir -p "$HOME/tmp/tmprepo"
    rm -rf   "$HOME/tmp/tmprepo"
    mkdir -p "$HOME/tmp/tmprepo"


    cd "$HOME"/tmp/tmprepo
    git init 

    git checkout -b main
    echo "state01" > state && git add state && git commit -m "Initial commit"
    echo "state02" > state && git add state && git commit -m "Modify state"

    git checkout -b branch1
    echo "state03" > state && git add state && git commit -m "Modify state"
    echo "state04" > state && git add state && git commit -m "Modify state"
    echo "state05" > state && git add state && git commit -m "Modify state"

    git checkout main
    git checkout -b branch2
    echo "state06" > state && git add state && git commit -m "Modify state"
    echo "state07" > state && git add state && git commit -m "Modify state"
    echo "state08" > state && git add state && git commit -m "Modify state"

    git checkout main
    git merge branch2 --no-ff -m "merge commit" 
    git merge branch1 -s ours --commit --no-edit --no-ff -m "merge commit" 

    git checkout -b branch3
    echo "state09" > state && git add state && git commit -m "Modify state - WANT TO SQUASH"
    git tag "Point1"
    echo "state10" > state && git add state && git commit -m "Modify state - WANT TO SQUASH"
    git checkout main
    git merge --no-ff -m "merge commit - WANT TO SQUASH" branch3
    git tag "Point2"

    git checkout main
    git checkout -b branch4
    echo "state11" > state && git add state && git commit -m "Modify state"
    echo "state12" > state && git add state && git commit -m "Modify state"
    echo "state13" > state && git add state && git commit -m "Modify state"

    git checkout main
    git checkout -b branch5
    echo "state14" > state && git add state && git commit -m "Modify state"
    echo "state15" > state && git add state && git commit -m "Modify state"
    echo "state16" > state && git add state && git commit -m "Modify state"

    git checkout main
    git checkout -b branch6
    echo "state17" > state && git add state && git commit -m "Modify state"
    echo "state18" > state && git add state && git commit -m "Modify state"
    echo "state19" > state && git add state && git commit -m "Modify state"

    git checkout branch5
    git merge branch6 -s ours --commit --no-edit --no-ff -m "merge commit" 

    git checkout main
    git merge branch5 -s ours --commit --no-edit --no-ff -m "merge commit" 
    git merge branch4 -s ours --commit --no-edit --no-ff -m "merge commit" 
}


attempted_solutions(){

    # Squash all information between point1 and point2
    git checkout Point1
    git reset --hard Point2
    git reset --soft Point1^
    git commit -am "all changes between point1 and point2"

    # The state is now guarenteed to be the same as Point2, but the history has
    # been modified to our liking. Now we need to replay all the other commits
    # on top of this.

    # Based on answers in this SO post:
    # https://stackoverflow.com/questions/1994463/how-to-cherry-pick-a-range-of-commits-and-merge-them-into-another-branch

    COMMIT_A=$(git rev-list -n 1 Point2)
    COMMIT_B=$(git rev-list -n 1 main)
    echo "COMMIT_A = $COMMIT_A"
    echo "COMMIT_B = $COMMIT_B"

    # I've tried the following, but they do not seem to work.

    # Try with cherry pick
    git cherry-pick "${COMMIT_A}..${COMMIT_B}" 

    # Try with rebase onto
    git rebase "$COMMIT_A" "$COMMIT_B"~0 --onto HEAD
    
}
