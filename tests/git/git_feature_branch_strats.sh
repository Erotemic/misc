__doc__="
A script that demonstrates pros and cons of rebase versus merge
"


setup_repo_with_features(){
    mkdir -p $HOME/tmp/tmprepo
    rm -rf   $HOME/tmp/tmprepo
    mkdir -p $HOME/tmp/tmprepo

    cd $HOME/tmp/tmprepo
    git init

    echo "
    download dependency 1
    install dependency 1
    " > setupfile.py
    echo "do something" > feature1.py
    echo "
    import feature1
    use feature1
    " > mainfile.py

    git add setupfile.py 
    git add feature1.py 
    git add mainfile.py
    git commit -m "initial commit"


    ### Feature 2
    git checkout master
    git checkout -b dev/feature2

    echo "
    download dependency 2
    install dependency 2
    " >> setupfile.py
    git add setupfile.py 
    git commit -am "add dependency for feature2"

    echo "do something" > feature2.py
    git add feature2.py 
    git commit -am "add feature2"

    echo "
    import feature2
    use feature2
    " >> mainfile.py
    git add mainfile.py
    git commit -am "integrate feature2"

    ### Feature 3
    git checkout master
    git checkout -b dev/feature3

    echo "
    download dependency 3
    install dependency 3
    " >> setupfile.py
    git add setupfile.py 
    git commit -am "add dependency for feature3"

    echo "do something" > feature3.py
    git add feature3.py 
    git commit -am "add feature3"

    echo "
    import feature3
    use feature3
    " >> mainfile.py
    git add mainfile.py
    git commit -am "integrate feature3"

    ### Feature 4
    git checkout master
    git checkout -b dev/feature4

    echo "
    download dependency 4
    install dependency 4
    " >> setupfile.py
    git add setupfile.py 
    git commit -am "add dependency for feature4"

    echo "do something" > feature4.py
    git add feature4.py 
    git commit -am "add feature4"

    echo "
    import feature4
    use feature4
    " >> mainfile.py
    git add mainfile.py
    git commit -am "integrate feature4"

    # gitk --all
}


union_conflict_resolve(){
    __doc__="
    both changes are important, take both
    "
    fpath=$1
    grep -v -e'^<<<<<<<' -e '^>>>>>>>' -e'=======' $fpath > $fpath.next 
    mv $fpath.next $fpath
}


### Merging
merge_strategy_via_merging(){

    # Merge feature 4
    git checkout dev/feature4
    git merge master
    git checkout master
    git merge dev/feature4

    ##### Merge feature 3
    git checkout dev/feature3
    git merge master

    # Resolve conflicts on the feature branch
    union_conflict_resolve mainfile.py 
    union_conflict_resolve setupfile.py
    git add mainfile.py setupfile.py
    git commit -m "merged master into feature3"

    git checkout master
    git merge dev/feature3

    ##### Merge feature 2
    git checkout dev/feature2
    git merge master

    # Resolve conflicts on the feature branch
    union_conflict_resolve mainfile.py 
    union_conflict_resolve setupfile.py
    git add mainfile.py setupfile.py
    git commit -m "merged master into feature2"

    git checkout master
    git merge dev/feature2

}

### Merging
merge_strategy_via_rebase(){

    # Merge feature 4
    git checkout dev/feature4
    git rebase master
    git checkout master
    git merge dev/feature4

    ##### Merge feature 3
    git checkout dev/feature3
    git rebase master

    # Resolve conflicts in the rebase
    union_conflict_resolve setupfile.py
    git add setupfile.py
    git rebase --continue

    union_conflict_resolve mainfile.py
    git add mainfile.py
    git rebase --continue

    git checkout master
    git merge dev/feature3

    ##### Merge feature 2
    git checkout dev/feature2
    git rebase master

    # Resolve conflicts in the rebase
    union_conflict_resolve setupfile.py
    git add setupfile.py
    git rebase --continue

    union_conflict_resolve mainfile.py
    git add mainfile.py
    git rebase --continue

    git checkout master
    git merge dev/feature2


}
