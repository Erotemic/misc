__doc__="
A script that demonstrates pros and cons of rebase versus merge
"


setup_repo_with_features(){
    __doc__='
    source ~/misc/tests/git/git_feature_branch_strats.sh
    setup_repo_with_features
    gitk --all
    '
    mkdir -p $HOME/tmp/tmprepo
    rm -rf   $HOME/tmp/tmprepo
    mkdir -p $HOME/tmp/tmprepo

    cd $HOME/tmp/tmprepo
    git init 
    git checkout -b main

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

    echo "
    main branch boilerplate1
    " >> setupfile.py
    git add setupfile.py
    git commit -m "main branch boilerplate1"

    echo "
    main branch boilerplate2
    " >> setupfile.py
    git add setupfile.py
    git commit -m "main branch boilerplate2"


    ### Feature 2
    git checkout main
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
    git checkout main
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
    git checkout main
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
    local fpath=$1
    grep -v -e'^<<<<<<<' -e '^>>>>>>>' -e'=======' $fpath > $fpath.next 
    mv $fpath.next $fpath
}


test_partial_dependant_feature_mergers(){
    __doc__='
    In this test development of feature 4 will depend on the first part of feature 3.

    We will merge an initial version of feature3 into feature4, continue
    development on feature4 and feature3, and then try to get them both into
    main nicely.

    Unfortunately, there seems to be a lot of conflict resolution that is still
    required.
    '
    # Restart with a fresh base repo + feature branches
    setup_repo_with_features

    git co main
    
    # Add some main branch development
    echo "
    main branch boilerplate3
    " >> setupfile.py
    git add setupfile.py
    git commit -m "main branch boilerplate3"

    echo "
    main branch boilerplate4
    " >> setupfile.py
    git add setupfile.py
    git commit -m "main branch boilerplate4"
    

    # Let's pretend feature 4 depends on  feature 4
    git checkout dev/feature4

    git merge dev/feature3

    # Resolve conflicts (take both)
    union_conflict_resolve mainfile.py 
    union_conflict_resolve setupfile.py
    git add mainfile.py setupfile.py
    git commit -m "merge start of feature3 into feature4"

    echo "
    continue feature4 development
    " >> feature4.py
    git add feature4.py 
    git commit -am "continue feature4 development"

    git checkout dev/feature3
    echo "
    continue feature3 development
    " >> feature3.py
    git add feature3.py 
    git commit -am "continue feature3 development"

    # Merge feature 3 into main
    git checkout main
    git merge dev/feature3
    union_conflict_resolve setupfile.py
    git add setupfile.py
    git commit -m "resolved conflicts between main and feature3"

    # Rebase feature 4 onto main
    git checkout dev/feature4
    git rebase main

    # Have to resolve conflict again :(
    union_conflict_resolve setupfile.py
    git add setupfile.py
    git rebase --continue

    union_conflict_resolve mainfile.py
    git add mainfile.py
    git rebase --continue

    # Merge the rebased feature4 into main
    git checkout main
    git merge dev/feature4

}


### Merging
merge_strategy_via_merging(){
    __doc__='
    source ~/misc/tests/git/git_feature_branch_strats.sh
    '
    # Restart with a fresh base repo + feature branches
    setup_repo_with_features

    # Merge feature 4
    git checkout dev/feature4
    git merge main
    git checkout main
    git merge dev/feature4

    ##### Merge feature 3
    git checkout dev/feature3
    git merge main

    # Resolve conflicts on the feature branch
    union_conflict_resolve mainfile.py 
    union_conflict_resolve setupfile.py
    git add mainfile.py setupfile.py
    git commit -m "merged main into feature3"

    git checkout main
    git merge dev/feature3

    ##### Merge feature 2
    git checkout dev/feature2
    git merge main

    # Resolve conflicts on the feature branch
    union_conflict_resolve mainfile.py 
    union_conflict_resolve setupfile.py
    git add mainfile.py setupfile.py
    git commit -m "merged main into feature2"

    git checkout main
    git merge dev/feature2

}

### Merging
merge_strategy_via_rebase(){

    # Restart with a fresh base repo + feature branches
    setup_repo_with_features

    # Merge feature 4
    git checkout dev/feature4
    git rebase main
    git checkout main
    git merge dev/feature4

    ##### Merge feature 3
    git checkout dev/feature3
    git rebase main

    # Resolve conflicts in the rebase
    union_conflict_resolve setupfile.py
    git add setupfile.py
    git rebase --continue

    union_conflict_resolve mainfile.py
    git add mainfile.py
    git rebase --continue

    git checkout main
    git merge dev/feature3

    ##### Merge feature 2
    git checkout dev/feature2
    git rebase main

    # Resolve conflicts in the rebase
    union_conflict_resolve setupfile.py
    git add setupfile.py
    git rebase --continue

    union_conflict_resolve mainfile.py
    git add mainfile.py
    git rebase --continue

    git checkout main
    git merge dev/feature2


}
