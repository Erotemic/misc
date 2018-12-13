make_pypkg(){
    REPO_NAME=$1

    REPO_DPATH=$HOME/code/$REPO_NAME
    PKG_DPATH=$REPO_DPATH/$REPO_NAME
    echo "INITIALIZING $REPO_NAME in $REPO_DPATH"
    mkdir -p $REPO_DPATH
    mkdir -p $PKG_DPATH

    echo "MOVING TEMPLATE FILES FROM UBELT"
    cp ~/code/ubelt/pytest.ini $REPO_DPATH
    cp ~/code/ubelt/.travis.yml $REPO_DPATH
    cp ~/code/ubelt/.coveragerc $REPO_DPATH
    cp ~/code/ubelt/appveyor.yml $REPO_DPATH
    cp ~/code/ubelt/run_tests.py $REPO_DPATH
    cp ~/code/ubelt/run_doctests.sh $REPO_DPATH
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
    touch $PKG_DPATH/__init__.py

    echo "SETTING BASELINE VERSION NUMBER"
    echo "__version__ = '0.0.1.dev'" > $REPO_DPATH/$REPO_NAME/__init__.py

    cd $REPO_DPATH

    echo "REPLACING PACKAGE NAME REFERENCES"
    find . -iname '*.yml' | xargs sed -i "s/ubelt/$REPO_NAME/g"
    find . -iname '*.sh' | xargs sed -i "s/ubelt/$REPO_NAME/g"
    find . -iname '*.py' | xargs sed -i "s/ubelt/$REPO_NAME/g"
    find . -iname '*.ini' | xargs sed -i "s/ubelt/$REPO_NAME/g"
    find . -iname '*.coveragerc' | xargs sed -i "s/ubelt/$REPO_NAME/g"

    echo "MAKING DOCS"
    rm -rf $REPO_DPATH/docs

    mkdir -p $REPO_DPATH/docs

    echo "$(codeblock "
    sphinx
    -e git://github.com/snide/sphinx_rtd_theme.git#egg=sphinx_rtd_theme
    ")" >  $REPO_DPATH/docs/requirements.txt

    sphinx-quickstart -q --sep \
        --project=$REPO_NAME \
        --author="Jon Crall" \
        --ext-autodoc \
        --ext-viewcode \
        --ext-intersphinx \
        --ext-todo \
        --extensions=sphinx.ext.napoleon,sphinx.ext.autosummary \
        $REPO_DPATH/docs

    # Make conf.py use the read-the-docs theme
    sed -i "s/html_theme = 'alabaster'/import sphinx_rtd_theme  # NOQA\nhtml_theme = 'sphinx_rtd_theme'\nhtml_theme_path = [sphinx_rtd_theme.get_html_theme_path()]/g" $REPO_DPATH/docs/source/conf.py

    # Make conf.py automatically read version info from the package
    sed -i "s/version = ''/import $REPO_NAME\nversion = '.'.join($REPO_NAME.__version__.split('.')[0:2])/g" $REPO_DPATH/docs/source/conf.py

    sphinx-apidoc -f -o $REPO_DPATH/docs/source $PKG_DPATH --separate

    (cd $REPO_DPATH/docs && PYTHONPATH="$REPO_DPATH:$PYTHONPATH" make html)

    echo "$(codeblock "
    todo_include_todos = True
    napoleon_google_docstring = True
    napoleon_use_param = False
    napoleon_use_ivar = True
    autodoc_inherit_docstrings = False
    autodoc_member_order = 'bysource'

    html_theme_options = {
        'collapse_navigation': False,
        'display_version': True,
        # 'logo_only': True,
    }
        
    ")" >> $REPO_DPATH/docs/source/conf.py
    
    
    
    echo "FINISHED"
}

echo "
Requirements:
    pip install sphinx sphinx_rtd_theme

Usage:
    source ~/misc/make_new_python_package_repo.sh
    REPO_NAME=pydir
    REPO_NAME=kwel
    echo "REPO_NAME = $REPO_NAME"
    make_pypkg $REPO_NAME
" > /dev/null
