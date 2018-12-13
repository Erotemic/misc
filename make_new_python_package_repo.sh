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
    cp -r ~/code/ubelt/.circleci $REPO_DPATH

    source $HOME/local/init/utils.sh
    echo "$(codeblock "
    pytest >= 3.3.1
    coverage >= 4.3.4
    xdoctest >= 0.3.0
    pytest-cov
    ")" >  $REPO_DPATH/requirements.txt

    
    echo "$(codeblock "
    # Install dependency packages
    pip install -r requirements.txt

    # Install irharn in developer mode
    pip install -e .

    # Compile C extensions to improve runtime
    #python setup.py build_ext --inplace

    cat README.md
    ")" >  $REPO_DPATH/run_developer_setup.py
    chmod +x $REPO_DPATH/run_developer_setup.py


    echo "$(codeblock "
    [build-system]
    requires = [\"setuptools\", \"wheel\", \"scikit-build\", \"cmake\", \"cython\", \"ninja\", \"ubelt\"]
    ")" >  $REPO_DPATH/pyproject.toml


    echo "$(codeblock "
    mkinit $REPO_NAME
    ")" >  $REPO_DPATH/_autogen_init.py
    chmod +x $REPO_DPATH/_autogen_init.py
    

    echo "CREATING PACKAGE STRUCTURE"
    touch $REPO_DPATH/whatsnew.txt
    touch $PKG_DPATH/__init__.py

    echo "SETTING BASELINE VERSION NUMBER"
    echo "__version__ = '0.0.1.dev0'" > $REPO_DPATH/$REPO_NAME/__init__.py

    cd $REPO_DPATH

    echo "REPLACING PACKAGE NAME REFERENCES"
    find . -iname '*.yml' | xargs sed -i "s/ubelt/$REPO_NAME/g"
    find . -iname '*.sh' | xargs sed -i "s/ubelt/$REPO_NAME/g"
    find . -iname '*.py' | xargs sed -i "s/ubelt/$REPO_NAME/g"
    find . -iname '*.ini' | xargs sed -i "s/ubelt/$REPO_NAME/g"
    find . -iname '*.coveragerc' | xargs sed -i "s/ubelt/$REPO_NAME/g"

    echo "REPLACING THINGS IN SETUP.PY"
            '',
            'Topic :: Software Development :: Libraries :: Python Modules',
    
    sed -i "s/'Development Status :: 4 - Beta'/'Development Status :: 3 - Alpha'/g" setup.py

    sed -i "s/'Intended Audience :: Developers'/#'Intended Audience :: <?TODO: Developers>'/g" setup.py
    sed -i "s/'Topic :: Software Development :: Libraries :: Python Modules'/#'Topic :: <?TODO: Software Development :: Libraries :: Python Modules>'/g" setup.py
    sed -i "s/'Topic :: Utilities/#'Topic :: <?TODO: Utilities>'/g" setup.py

    #sed -i "s/'Intended Audience :: Developers'.*\\n*//g" setup.py
    #sed -i "s/'Topic :: Software Development :: Libraries :: Python Modules'.*\\n*//g" setup.py
    #sed -i "s/'Topic :: Utilities.*\\n*',//g" setup.py

    #sed -i "s/'Programming Language :: Python :: 2.7//g" setup.py


    echo "FIXING PERMISSIONS"
    chmod +x $REPO_DPATH/setup.py
    chmod +x $REPO_DPATH/run_developer_setup.py
    chmod +x $REPO_DPATH/run_doctests.py
    chmod +x $REPO_DPATH/run_tests.py
    chmod +x $REPO_DPATH/_autogen_init.py


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
    #REPO_NAME=kwel

    REPO_NAME=ndsampler
    echo "REPO_NAME = $REPO_NAME"
    source ~/misc/make_new_python_package_repo.sh && make_pypkg $REPO_NAME
" > /dev/null
