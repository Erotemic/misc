
git-remote-co()
{
#REMOTE=origin
#BRANCH=viame/master
REMOTE=$1
BRANCH=$2
git co -b $BRANCH
git reset --hard $REMOTE/$BRANCH
git branch --set-upstream-to=$REMOTE/$BRANCH $BRANCH
}

git-remote-co origin viame/master
git-remote-co origin viame/query-wip
git-remote-co origin viame/tracking-work
git-remote-co origin viame/master-no-pybind
git-remote-co origin viame/master-w-pytorch
git-remote-co origin viame/add-descriptor-pipeline
git-remote-co origin dev/tracking-work

