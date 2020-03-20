

finish_deployment(){
    MODNAME=$1
    DEPLOY_REMOTE=$2
    DEPLOY_BRANCH=$3
    echo "
    Ensure you've merged the release into master

    MODNAME = $MODNAME
    DEPLOY_REMOTE = $DEPLOY_REMOTE
    DEPLOY_BRANCH = $DEPLOY_BRANCH
    "

    cd $HOME/code/$MODNAME
    VERSION=$(python -c "import $MODNAME; print($MODNAME.__version__)")
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
    TAG_NAME="${VERSION}"
    NEXT_VERSION=$(python -c "print('.'.join('$VERSION'.split('.')[0:2]) + '.' + str(int('$VERSION'.split('.')[2]) + 1))")
    echo "VERSION = $VERSION"
    echo "NEXT_VERSION = $NEXT_VERSION"
    git checkout master
    git fetch $DEPLOY_REMOTE
    git pull $DEPLOY_REMOTE
    git push $DEPLOY_REMOTE master:release
    #git tag "${TAG_NAME}" "${TAG_NAME}"^{} -f -m "tarball tag ${VERSION}"
    git tag "${TAG_NAME}" -f -m "tarball tag ${VERSION}"
    git push --tags $DEPLOY_REMOTE 

    echo "NEXT_VERSION = $NEXT_VERSION"
    git co -b dev/$NEXT_VERSION

    rob sedr "'$VERSION'" "'$NEXT_VERSION'" True
    echo "" >> CHANGELOG.md
    echo "## Version $NEXT_VERSION - Unreleased" >> CHANGELOG.md

    git commit -am "Start branch for $NEXT_VERSION"
    git push $DEPLOY_REMOTE
}


mypkgs(){
    source ~/misc/bump_versions.sh
    MODNAME=kwarray
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    MODNAME=kwimage
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    MODNAME=kwplot
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    MODNAME=ndsampler
    DEPLOY_REMOTE=public
    DEPLOY_BRANCH=release
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH

    MODNAME=netharn
    finish_deployment $MODNAME $DEPLOY_REMOTE $DEPLOY_BRANCH
}
