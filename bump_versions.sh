
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
    TAG_NAME="${VERSION}"
    NEXT_VERSION=$(python -c "print('.'.join('$VERSION'.split('.')[0:2]) + '.' + str(int('$VERSION'.split('.')[2]) + 1))")
    echo "VERSION = $VERSION"
    echo "NEXT_VERSION = $NEXT_VERSION"
    git checkout master || git checkout $DEPLOY_REMOTE/master -b master
    git fetch $DEPLOY_REMOTE
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
    TAG_NAME="${VERSION}"
    NEXT_VERSION=$(python -c "print('.'.join('$VERSION'.split('.')[0:2]) + '.' + str(int('$VERSION'.split('.')[2]) + 1))")
    echo "
    VERSION = $VERSION
    NEXT_VERSION = $NEXT_VERSION
    TAG_NAME = $TAG_NAME
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
    sed -i "s|Unreleased|$DATE_STR|g" CHANGELOG.md

    # Old code to insert the new line in a bad spot
    #echo "## Version $NEXT_VERSION - Unreleased" >> CHANGELOG.md
    # New code to insert the new line in the right spot 
    pyblock "
    with open('CHANGELOG.md') as file:
        text = file.read()
    lines = text.split(chr(10))
    for ix, line in enumerate(lines):
        if '## Version' in line:
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
    MODNAME=torch_liberator
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
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
    MODNAME=kwcoco
    DEPLOY_REMOTE=origin
    DEPLOY_BRANCH=release
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    MODNAME=kwarray
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    source ~/misc/bump_versions.sh
    MODNAME=kwimage
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
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
    MODNAME=netharn
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
    update_master $MODNAME $DEPLOY_REMOTE
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
}
