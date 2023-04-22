#!/bin/bash
__notes__="
TODO:

Need to fix CI such that we cache docker images better.

ERROR: Preparation failed: Error response from daemon: toomanyrequests: You
have reached your pull rate limit. You may increase the limit by authenticating
and upgrading: https://www.docker.com/increase-rate-limit (docker.go:142:0s)

"
delete_remote_tags(){
    # https://stackoverflow.com/questions/5480258/how-to-delete-a-remote-tag
    git push --delete origin test-tag4
    git tag --delete test-tag4

}


delete_merged_branches(){
    # https://stackoverflow.com/questions/6127328/how-do-i-delete-all-git-branches-which-have-been-merged

    # Delete merged dev branches
    TO_DELETE_LOCAL=$(git branch --merged main | grep -Ev "(^\*|master|main|release)" | grep "dev/")
    TO_DELETE_REMOTE=$(git branch -r --merged main | grep -Ev "(^\*|master|main|release)" | grep "origin/dev/")
    echo "TO_DELETE_REMOTE = $TO_DELETE_REMOTE"
    echo "TO_DELETE_LOCAL = $TO_DELETE_LOCAL"
    for branchname in $TO_DELETE; do
      echo "branchname = $branchname"
    done

    for branchname in $TO_DELETE_LOCAL; do
      echo "branchname = $branchname"
      git branch -d "$branchname"
    done

    for full_branchname in $TO_DELETE_REMOTE; do
      echo "full_branchname = $full_branchname"
      branchname=$(echo "$full_branchname" | cut -d"/" -f2-)
      echo "branchname = $branchname"
    done


    for full_branchname in $TO_DELETE_REMOTE; do
      echo "full_branchname = $full_branchname"
      branchname=$(echo "$full_branchname" | cut -d"/" -f2-)
      remote=$(echo "$full_branchname" | cut -d"/" -f1)
      echo "remote = $remote"
      echo "branchname = $branchname"
      git push --delete "$remote" "$branchname"
    done
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

#    source "$HOME"/local/init/utils.sh


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


accept_latest_gitlab_dev_mr(){
    __doc__='
    Accepts an MR if the pipeline is passing.

    The current branch you are on must corespond to the merge request you would
    like to accept.

    Requires that you have loaded a loaded secret

    load_secrets
    MODNAME=kwimage
    DEPLOY_REMOTE=origin
    '
    MODNAME=$1
    DEPLOY_REMOTE=$2

    cd "$HOME/code/$MODNAME"
    MERGE_BRANCH=$(git branch --show-current)
    GROUP_NAME=$(git remote get-url "$DEPLOY_REMOTE" | cut -d ":" -f 2 | cut -d "/" -f 1)
    HOST=https://$(git remote get-url "$DEPLOY_REMOTE" | cut -d "/" -f 1 | cut -d "@" -f 2 | cut -d ":" -f 1)

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
    PRIVATE_GITLAB_TOKEN=$(git_token_for "$HOST")

    export MODNAME
    export HOST
    export GROUP_NAME
    export MERGE_BRANCH
    export DEPLOY_REMOTE
    export PRIVATE_GITLAB_TOKEN

    if [[ "$PRIVATE_GITLAB_TOKEN" == "ERROR" ]]; then
        echo "Failed to load authentication key"
        return 1
    fi

    # use python logic instead of bash.
    python -c "if 1:
    '''
    Requires:
        pip install python-gitlab
    '''
    import gitlab
    from xcookie.vcs_remotes import GitlabRemote
    import os
    proj_name = os.environ['MODNAME']
    proj_group = os.environ['GROUP_NAME']
    proj_host = os.environ['HOST']
    remote = GitlabRemote(proj_name, proj_group, proj_host)
    project = remote.project
    remote.gitlab.auth()

    mrs = project.mergerequests.list(iterator=True)
    open_mrs = []
    for cand_mr in mrs:
        if cand_mr.state == 'opened':
            open_mrs.append(cand_mr)

    mergable_mrs = []
    for mr in open_mrs:
        if mr.draft:
            print('mr is a draft')
        elif 'do not merge' in mr.title:
            ...
        elif mr.merge_status == 'can_be_merged':
            mergable_mrs.append(mr)

    assert len(mergable_mrs) == 1, 'expected only one mergable branch'
    mr = mergable_mrs[0]
    status = mr.merge()
    assert status['merge_error'] is None
    "
    echo "accept_latest_gitlab_dev_mr finished."

    #TMP_DIR=$(mktemp -d -t ci-XXXXXXXXXX)

    #curl --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/groups" > "$TMP_DIR/all_group_info"
    #GROUP_ID=$(cat "$TMP_DIR/all_group_info" | jq ". | map(select(.name==\"$GROUP_NAME\")) | .[0].id")
    #echo "GROUP_ID = $GROUP_ID"

    #curl --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/groups/$GROUP_ID" > "$TMP_DIR/group_info"
    #PROJ_ID=$(cat "$TMP_DIR/group_info" | jq ".projects | map(select(.name==\"$MODNAME\")) | .[0].id")
    #echo "PROJ_ID = $PROJ_ID"

    #curl --request GET --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/projects/$PROJ_ID/merge_requests/?state=opened" > "$TMP_DIR/open_mr_info"
    #MERGE_IID=$(cat "$TMP_DIR/open_mr_info" | jq ". | map(select(.source_branch==\"$MERGE_BRANCH\")) | .[0].iid")
    #echo "MERGE_IID = $MERGE_IID"

    #curl --request GET --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/projects/$PROJ_ID/merge_requests/$MERGE_IID" > "$TMP_DIR/merge_info"
    #cat "$TMP_DIR/merge_info"| jq .
    #CAN_MERGE=$(cat "$TMP_DIR/merge_info"| jq .user.can_merge | sed -e 's/^"//' -e 's/"$//')
    #MERGE_STATUS=$(cat "$TMP_DIR/merge_info"| jq .head_pipeline.status | sed -e 's/^"//' -e 's/"$//')
    #echo "CAN_MERGE = $CAN_MERGE"
    #echo "MERGE_STATUS = $MERGE_STATUS"

    #if [[ "$CAN_MERGE" == "true" &&  "$MERGE_STATUS" == "success" ]]; then
    #    echo "MR is mergable and the pipelines has passed"
    #else
    #    echo "The MR is not in an auto-mergable state. Manually inspect, and merge if everything seems ok"
    #    return 1
    #fi

    #DRAFT_STATUS=$(cat "$TMP_DIR/merge_info"| jq .work_in_progress | sed -e 's/^"//' -e 's/"$//')
    #echo "DRAFT_STATUS = $DRAFT_STATUS"

    #if [[ "$DRAFT_STATUS" == "true" ]]; then
    #    # NOTE: QUICK ACTIONS ARE NOT REST API ACTIONS
    #    # https://docs.gitlab.com/ee/user/project/quick_actions.html#quick-actions-for-issues-merge-requests-and-epics

    #    curl --request GET --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/projects/$PROJ_ID/merge_requests/$MERGE_IID" > "$TMP_DIR/merge_info"
    #    OLD_TITLE=$(cat "$TMP_DIR/merge_info"| jq .title | sed -e 's/^"//' -e 's/"$//')
    #    # shellcheck disable=SC2001
    #    NEW_TITLE=$(echo "$OLD_TITLE" | sed 's|Draft *:* *||gi')
    #    #NEW_TITLE=${OLD_TITLE//s/Draft *:* */}
    #    echo "OLD_TITLE = $OLD_TITLE"
    #    echo "NEW_TITLE = $NEW_TITLE"

    #    # We can get rid of draft status by changing the title
    #    # https://docs.gitlab.com/13.7/ee/api/merge_requests.html#update-mr
    #    curl --request PUT \
    #        --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" \
    #        --data-urlencode "title=$NEW_TITLE" \
    #        "$HOST/api/v4/projects/$PROJ_ID/merge_requests/$MERGE_IID" > "$TMP_DIR/toggle_status"
    #    cat "$TMP_DIR/toggle_status" | jq .
    #fi

    ## Click the accept button
    #curl --request PUT --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/projects/$PROJ_ID/merge_requests/$MERGE_IID/merge" > "$TMP_DIR/status"
    #cat "$TMP_DIR/status" | jq .
    #cat "$TMP_DIR/status" | jq .message

    #echo "accept_latest_gitlab_dev_mr finished."
    #rm -rf "$TMP_DIR"

}


create_new_gitlab_dev_mr(){
    MODNAME=$1
    DEPLOY_REMOTE=$2

    cd "$HOME/code/$MODNAME"
    MERGE_BRANCH=$(git branch --show-current)
    DEFAULT_BRANCH=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)
    GROUP_NAME=$(git remote get-url "$DEPLOY_REMOTE" | cut -d ":" -f 2 | cut -d "/" -f 1)
    HOST=https://$(git remote get-url "$DEPLOY_REMOTE" | cut -d "/" -f 1 | cut -d "@" -f 2 | cut -d ":" -f 1)

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
    export PRIVATE_GITLAB_TOKEN=$(git_token_for "$HOST")

    if [[ "$PRIVATE_GITLAB_TOKEN" == "ERROR" ]]; then
        echo "Failed to load authentication key"
        return 1
    fi

    export MODNAME
    export HOST
    export GROUP_NAME
    export MERGE_BRANCH
    export DEPLOY_REMOTE
    export DEFAULT_BRANCH

    # TODO: use python logic instead of bash.
    python -c "if 1:
    from xcookie.vcs_remotes import GitlabRemote
    import os
    proj_name = os.environ['MODNAME']
    proj_group = os.environ['GROUP_NAME']
    proj_host = os.environ['HOST']
    remote = GitlabRemote(proj_name, proj_group, proj_host)
    remote.gitlab.auth()
    project = remote.project

    merge_branch = os.environ['MERGE_BRANCH']
    default_branch = os.environ['DEFAULT_BRANCH']

    title = 'Start branch for ' + merge_branch
    print(title)

    user = remote.gitlab.user

    status = project.mergerequests.create({
        'title': title,
        'source_branch': merge_branch,
        'target_branch': default_branch,
        'description': 'auto created MR',
        'assignee_id': user.id,
    })

    assert status.state == 'opened'
    print(status.web_url)
    "

    #TMP_DIR=$(mktemp -d -t ci-XXXXXXXXXX)

    #curl --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/groups" > "$TMP_DIR/all_group_info"
    #GROUP_ID=$(cat "$TMP_DIR/all_group_info" | jq ". | map(select(.path==\"$GROUP_NAME\")) | .[0].id")
    #echo "GROUP_ID = $GROUP_ID"

    #curl --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/groups/$GROUP_ID" > "$TMP_DIR/group_info"
    #PROJ_ID=$(cat "$TMP_DIR/group_info" | jq ".projects | map(select(.path==\"$MODNAME\")) | .[0].id")
    #echo "PROJ_ID = $PROJ_ID"

    #curl --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/user" > "$TMP_DIR/user_info"
    #cat "$TMP_DIR/user_info" | jq .
    #SELF_USER_ID=$(cat "$TMP_DIR/user_info"| jq .id)
    #echo "SELF_USER_ID = $SELF_USER_ID"

    ## Create the new gitlab MR and assign yourself

    #TITLE="Start branch for $MERGE_BRANCH"
    #echo "MERGE_BRANCH = $MERGE_BRANCH"
    #echo "DEFAULT_BRANCH = $DEFAULT_BRANCH"

    #curl --request POST \
    #    --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" \
    #    --data-urlencode "title=$TITLE" \
    #    --data-urlencode "source_branch=$MERGE_BRANCH" \
    #    --data-urlencode "target_branch=$DEFAULT_BRANCH" \
    #    --data-urlencode "description=auto created mr" \
    #    --data-urlencode "assignee_id=$SELF_USER_ID" \
    #    "$HOST/api/v4/projects/$PROJ_ID/merge_requests" > "$TMP_DIR/new_mr"
    #cat "$TMP_DIR/new_mr" | jq .
    #MR_URL=$(cat "$TMP_DIR/new_mr" | jq -r .web_url)
    #echo "MR_URL = $MR_URL"

    ## shellcheck disable=SC2050
    #if [[ "false" == "true" ]]; then
    #    # Assign myself
    #    # shouldnt need to do this if we created the MR correctly
    #    curl --request GET --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" "$HOST/api/v4/projects/$PROJ_ID/merge_requests/?state=opened" > "$TMP_DIR/open_mr_info"
    #    MERGE_IID=$(cat "$TMP_DIR/new_mr" | jq ".iid")
    #    echo "MERGE_IID = $MERGE_IID"
    #    curl --request PUT \
    #        --header "PRIVATE-TOKEN: $PRIVATE_GITLAB_TOKEN" \
    #        --data-urlencode "assignee_id=$SELF_USER_ID" \
    #        "$HOST/api/v4/projects/$PROJ_ID/merge_requests/$MERGE_IID" > "$TMP_DIR/update_mr"
    #    cat "$TMP_DIR/update_mr" | jq .
    #fi
}


git_checkeven(){
    __doc__="
    Check if two branches are equal (i.e. even)
    "
    # https://stackoverflow.com/questions/31982954/how-can-i-check-whether-two-branches-are-even
    if [ $# -ne 2 ]; then
        printf "usage: git checkeven <revA> <revB>\n\n"
        return 3
    fi

    revA=$1
    revB=$2

    # TODO: verify that the remote exists
    #if ! git rev-parse --quiet --verify "$revA" ; then
    #    echo "revA = $revA does not exist"
    #fi
    #if ! git rev-parse --quiet --verify "$revB" ; then
    #    echo "revB = $revB does not exist"
    #fi

    # shellcheck disable=SC2086
    nA2B="$(git rev-list --count $revA..$revB -- )"
    # shellcheck disable=SC2086
    nB2A="$(git rev-list --count $revB..$revA)"

    if [ "$nA2B" -eq 0 ] && [ "$nB2A" -eq 0 ]; then
      echo "$revA is even with $revB"
      return 0
    elif [ "$nA2B" -gt 0 ]; then
      echo "$revA is $nA2B commits behind $revB"
      return 1
    else
      echo "$revA is $nB2A commits ahead of $revB"
      return 2
    fi
}


gitlab_update_master_to_main(){
    __doc__="
    # https://boleary.dev/blog/2020-06-11-change-your-default-branch.html
    "
    # Locally
    git branch -m master main
    git push -u origin main

    # Remotely, go to settings
    REMOTE=origin
    GROUP_NAME=$(git remote get-url $REMOTE | cut -d ":" -f 2 | cut -d "/" -f 1)
    PROJECT_NAME=$(git remote get-url $REMOTE | cut -d ":" -f 2 | cut -d "/" -f 2 | cut -d "." -f 1)
    HOST=https://$(git remote get-url $REMOTE | cut -d "/" -f 1 | cut -d "@" -f 2 | cut -d ":" -f 1)
    REPO_URL=$HOST/$GROUP_NAME/$PROJECT_NAME
    SETTINGS_URL=$REPO_URL/-/settings/repository
    echo "SETTINGS_URL = $SETTINGS_URL"
    # https://gitlab.kitware.com/computer-vision/ndsampler/-/settings/repository
    # Update the default branch
    # Update protected branches

}

update_default_branch(){
    MODNAME=$1
    DEPLOY_REMOTE=$2
    # -----
    echo "
    Ensure you've merged the topic-branch into the default branch (main/master)

    MODNAME = $MODNAME
    DEPLOY_REMOTE = $DEPLOY_REMOTE
    "

    cd "$HOME/code/$MODNAME"
    VERSION=$(python -c "import $MODNAME; print($MODNAME.__version__)")
    NEXT_VERSION=$(python -c "print('.'.join('$VERSION'.split('.')[0:2]) + '.' + str(int('$VERSION'.split('.')[2]) + 1))")
    DEFAULT_BRANCH=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)
    echo "
    VERSION = $VERSION
    NEXT_VERSION = $NEXT_VERSION
    DEFAULT_BRANCH = $DEFAULT_BRANCH
    "

    git fetch "$DEPLOY_REMOTE"
    git_checkeven "$DEPLOY_REMOTE/release" "$DEPLOY_REMOTE/$DEFAULT_BRANCH"
    RES=$?
    if [ "$RES" == "0" ]; then
        echo "WARNING: $DEFAULT_BRANCH is up to date with release, did you forget to merge the topic branch?"
    else
        echo "$DEFAULT_BRANCH is different than release, that is expected"
    fi

    git checkout "$DEFAULT_BRANCH" || git checkout "$DEPLOY_REMOTE/$DEFAULT_BRANCH" -b "$DEFAULT_BRANCH"
    git pull "$DEPLOY_REMOTE" "$DEFAULT_BRANCH"

}


finish_deployment(){
    MODNAME=$1
    DEPLOY_REMOTE=$2
    DEPLOY_BRANCH=$3
    # -----
    echo "
    Ensure you've merged the topic-branch into teh default branch (main/master)

    TODO: assert the version doesnt already exist (if we forgot to bump the version var)

    MODNAME = $MODNAME
    DEPLOY_REMOTE = $DEPLOY_REMOTE
    DEPLOY_BRANCH = $DEPLOY_BRANCH
    "


    cd "$HOME/code/$MODNAME"
    VERSION=$(python -c "import $MODNAME; print($MODNAME.__version__)")
    #TAG_NAME="${VERSION}"
    NEXT_VERSION=$(python -c "print('.'.join('$VERSION'.split('.')[0:2]) + '.' + str(int('$VERSION'.split('.')[2]) + 1))")
    echo "
    VERSION = $VERSION
    NEXT_VERSION = $NEXT_VERSION
    "

    # Get default branch name (master/main)
    DEFAULT_BRANCH=$(git remote show origin | grep 'HEAD branch' | cut -d' ' -f5)
    echo "DEFAULT_BRANCH = $DEFAULT_BRANCH"
    git checkout "$DEFAULT_BRANCH" || git checkout "$DEPLOY_REMOTE/$DEFAULT_BRANCH" -b "$DEFAULT_BRANCH"
    git fetch "$DEPLOY_REMOTE"
    git pull "$DEPLOY_REMOTE" "$DEFAULT_BRANCH"
    git push "$DEPLOY_REMOTE" "$DEFAULT_BRANCH:release"
    #git tag "${TAG_NAME}" "${TAG_NAME}"^{} -f -m "tarball tag ${VERSION}"
    #git tag "${TAG_NAME}" -f -m "tarball tag ${VERSION}"
    #git push --tags $DEPLOY_REMOTE

    echo "NEXT_VERSION = $NEXT_VERSION"
    git checkout -b "dev/$NEXT_VERSION"

    REPO_DPATH="$HOME/code/$MODNAME"
    xdev sed --regexpr="'$VERSION'" --repl="'$NEXT_VERSION'" --dpath="$REPO_DPATH" --include=__init__.py --dry=False
    #xdev sed --regexpr="'dev/$VERSION'" --repl="'dev/$NEXT_VERSION'" --dpath="$REPO_DPATH" --dry=False

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
    git push "$DEPLOY_REMOTE"

}


mypkgs(){
    source ~/misc/bump_versions.sh

    MODNAME=bioharn
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=torch_liberator
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    accept_latest_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
    create_new_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=liberator
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    accept_latest_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
    create_new_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=scriptconfig
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    accept_latest_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
    create_new_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=kwcoco
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    accept_latest_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
    create_new_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=kwarray
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    accept_latest_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
    create_new_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=kwimage
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    accept_latest_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
    create_new_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=kwimage_ext
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    accept_latest_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
    create_new_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE

    source ~/misc/bump_versions.sh
    MODNAME=kwplot
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    load_secrets
    accept_latest_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
    create_new_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=ndsampler
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    accept_latest_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
    create_new_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=netharn
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    accept_latest_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
    create_new_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=cmd_queue
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    accept_latest_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
    create_new_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=delayed_image
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    accept_latest_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
    create_new_gitlab_dev_mr $MODNAME $DEPLOY_REMOTE


    ### GITHUB PROJECTS

    # Currently need to manually merge PRs


    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=ubelt
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=progiter
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    source ~/misc/bump_versions.sh
    load_secrets
    MODNAME=mkinit
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH


    source ~/misc/bump_versions.sh
    MODNAME=xdoctest
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH


    source ~/misc/bump_versions.sh
    MODNAME=line_profiler
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    update_default_branch $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH


}


open_common_paths_multi_repos(){
    # Check if we can make it easier to maintain several similar changes across github repos

    ~/code/vtool_ibeis/CHANGELOG.md

    python -c "if 1:
    import ubelt as ub
    import os
    dpath = ub.Path.appdir('vimtk/tmp').ensuredir()
    fpath = dpath / 'helper_init_script.vim'

    home = ub.Path.home()

    lines = []

    modnames = [
        'plottool_ibeis',
        'guitool_ibeis',
        'dtool_ibeis',
        'vtool_ibeis',
        'vtool_ibeis_ext',
        'utool',
        'ibeis',
        'pyhesaff',
        'pyflann_ibeis',
    ]

    for idx, modname in enumerate(modnames):
        common_paths = [
            home / 'code' / modname / 'CHANGELOG.md',
            home / 'code' / modname / 'requirements/tests.txt',
            home / 'code' / modname / modname / '__init__.py',
        ]
        if idx == 0:
            lines.append(';e ' + os.fspath(common_paths[0]))
        else:
            lines.append(';tabe ' + os.fspath(common_paths[0]))

        for p in common_paths[1:]:
            lines.append(';sp '  + os.fspath(p))
    text = chr(10).join(lines)
    fpath.write_text(text)
    print(fpath)
    "
    gvim -s "$HOME"/.cache/vimtk/tmp/helper_init_script.vim
}
