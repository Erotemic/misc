REPO_NAME=somepackage

REPO_DPATH=$HOME/code/$REPO_NAME
cp ~/code/ubelt/pytest.ini
cp ~/code/ubelt/requirements.txt $REPO_DPATH
cp ~/code/ubelt/optional-requirements.txt $REPO_DPATH
cp ~/code/ubelt/.travis.yml $REPO_DPATH
cp ~/code/ubelt/.coveragerc $REPO_DPATH
cp ~/code/ubelt/appveyor.yml $REPO_DPATH
cp ~/code/ubelt/run_tests.py $REPO_DPATH
cp ~/code/ubelt/setup.py $REPO_DPATH
cp ~/code/ubelt/.gitignore $REPO_DPATH

touch $REPO_DPATH/whatsnew.txt
mkdir -p $REPO_DPATH/$REPO_NAME
touch $REPO_DPATH/$REPO_NAME/__init__.py

echo "__version__ = '0.0.1.dev0'" > $REPO_DPATH/$REPO_NAME/__init__.py

cd $REPO_DPATH
sed ubelt $REPO_NAME

find . -iname '*.yml' | xargs sed -i "s/ubelt/$REPO_NAME/g"
find . -iname '*.py' | xargs sed -i "s/ubelt/$REPO_NAME/g"
find . -iname '*.ini' | xargs sed -i "s/ubelt/$REPO_NAME/g"
find . -iname '*.coveragerc' | xargs sed -i "s/ubelt/$REPO_NAME/g"
