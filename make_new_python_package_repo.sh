make_pypkg(){
    REPO_NAME=$1
    REPO_DPATH=$HOME/code/$REPO_NAME
    echo "INITIALIZING $REPO_NAME in $REPO_DPATH"

    echo "MOVING TEMPLATE FILES FROM UBELT"
    cp ~/code/ubelt/pytest.ini $REPO_DPATH
    cp ~/code/ubelt/.travis.yml $REPO_DPATH
    cp ~/code/ubelt/.coveragerc $REPO_DPATH
    cp ~/code/ubelt/appveyor.yml $REPO_DPATH
    cp ~/code/ubelt/run_tests.py $REPO_DPATH
    cp ~/code/ubelt/setup.py $REPO_DPATH
    cp ~/code/ubelt/.gitignore $REPO_DPATH

    source $HOME/local/init/utils.sh
    echo "$(codeblock "
    pytest >= 3.3.1
    coverage >= 4.3.4
    xdoctest >= 0.3.0
    pytest-cov
    ")" >  $REPO_DPATH/requirements.txt
    

    echo "CREATING PACKAGE STRUCTURE"
    touch $REPO_DPATH/whatsnew.txt
    mkdir -p $REPO_DPATH/$REPO_NAME
    touch $REPO_DPATH/$REPO_NAME/__init__.py

    echo "SETTING BASELINE VERSION NUMBER"
    echo "__version__ = '0.0.1.dev0'" > $REPO_DPATH/$REPO_NAME/__init__.py

    cd $REPO_DPATH

    echo "REPLACING PACKAGE NAME REFERENCES"
    find . -iname '*.yml' | xargs sed -i "s/ubelt/$REPO_NAME/g"
    find . -iname '*.py' | xargs sed -i "s/ubelt/$REPO_NAME/g"
    find . -iname '*.ini' | xargs sed -i "s/ubelt/$REPO_NAME/g"
    find . -iname '*.coveragerc' | xargs sed -i "s/ubelt/$REPO_NAME/g"
    echo "FINISHED"
}

echo "
source ~/misc/make_new_python_package_repo.sh
REPO_NAME=timerit
make_pypkg $REPO_NAME
" > /dev/null
