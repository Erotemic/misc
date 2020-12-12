
delete_remote_tags(){
    # https://stackoverflow.com/questions/5480258/how-to-delete-a-remote-tag
    git push --delete origin test-tag4
    git tag --delete test-tag4

}


#prep_next_version(){
#    MODNAME=$(python -c "import setup; print(setup.NAME)")
#    VERSION=$(python -c "import setup; print(setup.VERSION)")
#    TAG_NAME="${VERSION}"
#    NEXT_VERSION=$(python -c "print('.'.join('$VERSION'.split('.')[0:2]) + '.' + str(int('$VERSION'.split('.')[2]) + 1))")
#    echo "MODNAME = $MODNAME"
#    echo "VERSION = $VERSION"
#    echo "NEXT_VERSION = $NEXT_VERSION"

#    echo "NEXT_VERSION = $NEXT_VERSION"
#    git co -b dev/$NEXT_VERSION


#    rob sedr "'$VERSION'" "'$NEXT_VERSION'" True
#    echo "" >> CHANGELOG.md

#    source $HOME/local/init/utils.sh


#    # New code to insert the new line in the right spot 
#    pyblock "
#    with open('CHANGELOG.md') as file:
#        text = file.read()
#    lines = text.split(chr(10))
#    for ix, line in enumerate(lines):
#        if '## Version' in line:
#            break
#    newline = '## Version $NEXT_VERSION - Unreleased'
#    newlines = lines[:ix] + [newline, '', ''] + lines[ix:]
#    new_text = chr(10).join(newlines)
#    with open('CHANGELOG.md', 'w') as file:
#        file.write(new_text)
#    "
#    # Old code to insert the new line in a bad spot
#    #echo "## Version $NEXT_VERSION - Unreleased" >> CHANGELOG.md

#    git commit -am "Start branch for $NEXT_VERSION"
#}


accept_latest_dev_mr(){
    __doc__='
    Accepts an MR if the pipeline is passing.

    Requires that you have loaded a loaded secret

    load_secrets
    MODNAME=kwimage
    DEPLOY_REMOTE=origin
    '
    MODNAME=$1
    DEPLOY_REMOTE=$2

    cd $HOME/code/$MODNAME
    MERGE_BRANCH=$(git branch --show-current)
    GROUP_NAME=$(git remote get-url $DEPLOY_REMOTE | cut -d ":" -f 2 | cut -d "/" -f 1)
    HOST=https://$(git remote get-url $DEPLOY_REMOTE | cut -d "/" -f 1 | cut -d "@" -f 2 | cut -d ":" -f 1)

    echo "
        MODNAME=$MODNAME
        DEPLOY_REMOTE=$DEPLOY_REMOTE
        HOST=$HOST
        GROUP_NAME=$GROUP_NAME
        MERGE_BRANCH=$MERGE_BRANCH
        "

    if [[ "$HOST" != *"gitlab"* ]]; then
      echo "This function only supports the Gitlab Restful API at the moment"
      return 1
    fi

    # You must have a way of loading an authentication token here
    # The function ``git_token_for`` should map a hostname to the 
    # authentication token used for that hostname
    PRIVATE_GITLAB_TOKEN=$(git_token_for $HOST)

    if [[ "$PRIVATE_GITLAB_TOKEN" == "ERROR" ]]; then
        echo "Failed to load authentication key"
        return 1
    fi

    TMP_DIR=$(mktemp -d -t ci-XXXXXXXXXX)

    curl --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/groups" > $TMP_DIR/all_group_info
    GROUP_ID=$(cat $TMP_DIR/all_group_info | jq ". | map(select(.name==\"$GROUP_NAME\")) | .[0].id")
    echo "GROUP_ID = $GROUP_ID"

    curl --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/groups/$GROUP_ID" > $TMP_DIR/group_info
    PROJ_ID=$(cat $TMP_DIR/group_info | jq ".projects | map(select(.name==\"$MODNAME\")) | .[0].id")
    echo "PROJ_ID = $PROJ_ID"

    curl --request GET --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/projects/$PROJ_ID/merge_requests/?state=opened" > $TMP_DIR/open_mr_info
    MERGE_IID=$(cat $TMP_DIR/open_mr_info | jq ". | map(select(.source_branch==\"$MERGE_BRANCH\")) | .[0].iid")
    echo "MERGE_IID = $MERGE_IID"

    curl --request GET --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/projects/$PROJ_ID/merge_requests/$MERGE_IID" > $TMP_DIR/merge_info
    cat $TMP_DIR/merge_info| jq .
    CAN_MERGE=$(cat $TMP_DIR/merge_info| jq .user.can_merge | sed -e 's/^"//' -e 's/"$//')
    MERGE_STATUS=$(cat $TMP_DIR/merge_info| jq .head_pipeline.status | sed -e 's/^"//' -e 's/"$//')
    echo "CAN_MERGE = $CAN_MERGE"
    echo "MERGE_STATUS = $MERGE_STATUS"

    if [[ "$CAN_MERGE" == "true" &&  "$MERGE_STATUS" == "success" ]]; then
        echo "MR is mergable and the pipelines has passed"
    else
        echo "The MR is not in a mergable state"
        return 1
    fi

    DRAFT_STATUS=$(cat $TMP_DIR/merge_info| jq .work_in_progress | sed -e 's/^"//' -e 's/"$//')
    echo "DRAFT_STATUS = $DRAFT_STATUS"

    # TODO: Figure out how to resolve draft status via the API
    #if [[ "$DRAFT_STATUS" == "true" ]]; then
    #    # https://docs.gitlab.com/ee/user/project/quick_actions.html#quick-actions-for-issues-merge-requests-and-epics
    #    curl --request PUT --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/projects/$PROJ_ID/merge_requests/$MERGE_IID/merge/work_in_progress" > $TMP_DIR/toggle_status
    #    cat toggle_status | jq .
    #fi

    # Click the accept button
    curl --request PUT --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/projects/$PROJ_ID/merge_requests/$MERGE_IID/merge" > $TMP_DIR/status
    cat $TMP_DIR/status | jq .
    cat $TMP_DIR/status | jq .message

    echo "accept_latest_dev_mr finished."
    rm -rf $TMP_DIR

}


git_checkeven(){
    # https://stackoverflow.com/questions/31982954/how-can-i-check-whether-two-branches-are-even
    if [ $# -ne 2 ]; then
        printf "usage: git checkeven <revA> <revB>\n\n"
        return 3
    fi

    revA=$1
    revB=$2

    nA2B="$(git rev-list --count $revA..$revB)"
    nB2A="$(git rev-list --count $revB..$revA)"

    if [ "$nA2B" -eq 0 -a "$nB2A" -eq 0 ]; then
      printf "$revA is even with $revB\n"
      return 0
    elif [ "$nA2B" -gt 0 ]; then
      printf "$revA is $nA2B commits behind $revB\n"
      return 1
    else
      printf "$revA is $nB2A commits ahead of $revB\n"
      return 2
    fi
}

update_master(){
    MODNAME=$1
    DEPLOY_REMOTE=$2
    # -----
    echo "
    Ensure you've merged the topic-branch into master

    MODNAME = $MODNAME
    DEPLOY_REMOTE = $DEPLOY_REMOTE
    "

    cd $HOME/code/$MODNAME
    VERSION=$(python -c "import $MODNAME; print($MODNAME.__version__)")
    NEXT_VERSION=$(python -c "print('.'.join('$VERSION'.split('.')[0:2]) + '.' + str(int('$VERSION'.split('.')[2]) + 1))")
    echo "
    VERSION = $VERSION
    NEXT_VERSION = $NEXT_VERSION
    "

    git fetch $DEPLOY_REMOTE
    git_checkeven $DEPLOY_REMOTE/release $DEPLOY_REMOTE/master
    RES=$?
    if [ "$RES" == "0" ]; then
        echo "WARNING: master is up to date with release, did you forget to merge the topic branch?"
    else
        echo "master is different than release, that is expected"
    fi

    git checkout master || git checkout $DEPLOY_REMOTE/master -b master
    git pull $DEPLOY_REMOTE master

}


finish_deployment(){
    MODNAME=$1
    DEPLOY_REMOTE=$2
    DEPLOY_BRANCH=$3
    # -----
    echo "
    Ensure you've merged the topic-branch into master

    TODO: assert the version doesnt already exist (if we forgot to bump the version var)

    MODNAME = $MODNAME
    DEPLOY_REMOTE = $DEPLOY_REMOTE
    DEPLOY_BRANCH = $DEPLOY_BRANCH
    "


    cd $HOME/code/$MODNAME
    VERSION=$(python -c "import $MODNAME; print($MODNAME.__version__)")
    #TAG_NAME="${VERSION}"
    NEXT_VERSION=$(python -c "print('.'.join('$VERSION'.split('.')[0:2]) + '.' + str(int('$VERSION'.split('.')[2]) + 1))")
    echo "
    VERSION = $VERSION
    NEXT_VERSION = $NEXT_VERSION
    "
    git checkout master || git checkout $DEPLOY_REMOTE/master -b master
    git fetch $DEPLOY_REMOTE
    git pull $DEPLOY_REMOTE master
    git push $DEPLOY_REMOTE master:release
    #git tag "${TAG_NAME}" "${TAG_NAME}"^{} -f -m "tarball tag ${VERSION}"
    #git tag "${TAG_NAME}" -f -m "tarball tag ${VERSION}"
    #git push --tags $DEPLOY_REMOTE 

    echo "NEXT_VERSION = $NEXT_VERSION"
    git co -b dev/$NEXT_VERSION

    rob sedr "'$VERSION'" "'$NEXT_VERSION'" True
    rob sedr "'dev/$VERSION'" "'dev/$NEXT_VERSION'" True

    DATE_STR=$(date +'%Y-%m-%d')
    sed -i "s|Unreleased|Released $DATE_STR|g" CHANGELOG.md

    # Old code to insert the new line in a bad spot
    #echo "## Version $NEXT_VERSION - Unreleased" >> CHANGELOG.md
    # New code to insert the new line in the right spot 
    pyblock "
    with open('CHANGELOG.md') as file:
        text = file.read()
    lines = text.split(chr(10))
    for ix, line in enumerate(lines):
        if 'Version ' in line:
            break
    newline = '## Version $NEXT_VERSION - Unreleased'
    newlines = lines[:ix] + [newline, '', ''] + lines[ix:]
    new_text = chr(10).join(newlines)
    with open('CHANGELOG.md', 'w') as file:
        file.write(new_text)
    "

    git commit -am "Start branch for $NEXT_VERSION"
    git push $DEPLOY_REMOTE


    # Hack for netharn
    sed -i "s|'name': '$MODNAME', 'branch': 'dev/$VERSION'|'name': '$MODNAME', 'branch': 'dev/$NEXT_VERSION'|g" $HOME/code/netharn/super_setup.py
}


mypkgs(){
    source ~/misc/bump_versions.sh

    MODNAME=bioharn
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=torch_liberator
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    accept_latest_dev_mr $MODNAME $DEPLOY_REMOTE
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    MODNAME=liberator
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    source ~/misc/bump_versions.sh
    MODNAME=scriptconfig
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=kwcoco
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    accept_latest_dev_mr $MODNAME $DEPLOY_REMOTE
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=kwarray
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
    accept_latest_dev_mr $MODNAME $DEPLOY_REMOTE
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=kwimage
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
    accept_latest_dev_mr $MODNAME $DEPLOY_REMOTE
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    source ~/misc/bump_versions.sh
    MODNAME=kwplot
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    source ~/misc/bump_versions.sh
    MODNAME=ndsampler
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=netharn
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
    accept_latest_dev_mr $MODNAME $DEPLOY_REMOTE
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH


    source ~/misc/bump_versions.sh
    MODNAME=ubelt
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH


    source ~/misc/bump_versions.sh
    MODNAME=xdoctest
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH


    source ~/misc/bump_versions.sh
    MODNAME=line_profiler
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH


}
