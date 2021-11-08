__doc__='
Requirements:
    pip install sphinx sphinx_rtd_theme

Usage:
    source ~/misc/make_new_python_package_repo.sh

    REPO_NAME=supersetup
    echo "REPO_NAME = $REPO_NAME"
    source ~/misc/make_new_python_package_repo.sh && make_pypkg $REPO_NAME
'


update_pypkg(){
    REPO_DPATH=$HOME/code/kwarray


    cd $REPO_DPATH
    cp -r ~/misc/templates/PYPKG/.circleci .

    cp -rv ~/misc/templates/PYPKG/dev .
    cp -rv ~/misc/templates/PYPKG/.github .
    find . -iname '*.yml' | xargs sed -i "s/PYPKG/$REPO_NAME/g"

    chmod +x ./setup.py
    chmod +x ./run_developer_setup.sh
    chmod +x ./run_doctests.py
    chmod +x ./run_tests.py

    # <FIXME>
    TEXT="$(codeblock "
    Update Requirments:
        # Requirements are broken down by type in the requirements folder, and
        # requirments.txt lists them all. Thus we autogenerate via:
        cat requirements/*.txt > requirements.txt
        
    ")" 
    echo "TEXT = $TEXT"
    sed "s/Pypi:/${TEXT}Pypi:/g" setup.py
    # </FIXME>

    git tag -a "first" "$(git rev-list --max-parents=0 HEAD)" -m "first commit"
    git push --tags
    (git checkout -b "first" "$(git rev-list --max-parents=0 HEAD)" ; git push) && git checkout - 

    #>> $REPO_DPATH/docs/source/conf.py
}

make_pypkg(){
    REPO_NAME=$1

    REPO_DPATH=$HOME/code/$REPO_NAME
    PKG_DPATH=$REPO_DPATH/$REPO_NAME

    echo "INITIALIZING $REPO_NAME in $REPO_DPATH"
    mkdir -p $REPO_DPATH
    mkdir -p $PKG_DPATH

    echo "MOVING TEMPLATE FILES"

    cp ~/misc/templates/PYPKG/setup.py $REPO_DPATH
    cp ~/misc/templates/PYPKG/.gitignore $REPO_DPATH

    cp -r ~/misc/templates/PYPKG/publish.sh $REPO_DPATH
    cp ~/misc/templates/PYPKG/pytest.ini $REPO_DPATH

    cp ~/misc/templates/PYPKG/.travis.yml $REPO_DPATH
    cp ~/misc/templates/PYPKG/.gitlab-ci.yml $REPO_DPATH
    cp ~/misc/templates/PYPKG/appveyor.yml $REPO_DPATH
    cp -r ~/misc/templates/PYPKG/.circleci $REPO_DPATH

    cp ~/misc/templates/PYPKG/.coveragerc $REPO_DPATH
    cp ~/misc/templates/PYPKG/run_tests.py $REPO_DPATH
    cp ~/misc/templates/PYPKG/run_doctests.sh $REPO_DPATH

    cp ~/misc/templates/PYPKG/README.rst $REPO_DPATH

    source $HOME/local/init/utils.sh

    mkdir -p $REPO_DPATH/requirements
    echo "$(codeblock "
    pytest >= 3.3.1
    coverage >= 4.3.4
    xdoctest >= 0.3.0
    pytest-cov
    ")" >  $REPO_DPATH/requirements/tests.txt

    echo "$(codeblock "
    ubelt
    ")" >  $REPO_DPATH/requirements/runtime.txt
    
    echo "$(codeblock "
    numpy
    ")" >  $REPO_DPATH/requirements/optional.txt

    #echo "$(codeblock "
    #scikit-build
    #cmake
    #numpy
    #ninja
    #cython
    #")" >  $REPO_DPATH/requirements/optional.txt

    echo "$(codeblock "
    -r requirements/runtime.txt
    -r requirements/optional.txt
    -r requirements/tests.txt
    ")" >  $REPO_DPATH/requirements.txt
    #-r requirements/build.txt

    
    echo "$(codeblock "
    #!/bin/bash 

    # Install all dependency packages
    pip install -r requirements.txt

    # Install in developer mode
    pip install -e .
    ")" >  $REPO_DPATH/run_developer_setup.sh
    chmod +x $REPO_DPATH/run_developer_setup.sh


    echo "$(codeblock "
    [build-system]
    requires = [\"setuptools\", \"wheel\"]
    ")" >  $REPO_DPATH/pyproject.toml

    
    echo "CREATING PACKAGE STRUCTURE"
    echo "$(codeblock "
    # Changelog

    We are currently working on porting this changelog to the specifications in
    [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
    This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

    ## [Version 0.0.1] - 
     
    ### Added
    * Initial version
    ")" >  $REPO_DPATH/CHANGELOG.md

    echo "__version__ = '0.0.1'" > $PKG_DPATH/__init__.py

    cd $REPO_DPATH

    echo "REPLACING PACKAGE NAME REFERENCES"
    find . -iname '*.yml' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    find . -iname '*.sh' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    find . -iname '*.py' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    find . -iname '*.ini' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    find . -iname '*.coveragerc' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    find . -iname '*.py' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    find . -iname '*' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    find . -iname '*.rst' | xargs sed -i "s/PYPKG/$REPO_NAME/g"

    echo "REPLACING THINGS IN SETUP.PY"

    AUTHOR=$(git config --global user.name)
    AUTHOR_EMAIL=$(git config --global user.email)
    sed -i "s/<AUTHOR>/${AUTHOR}/g" setup.py
    sed -i "s/<AUTHOR_EMAIL>/${AUTHOR_EMAIL}/g" setup.py

    echo "FIXING PERMISSIONS"
    chmod +x $REPO_DPATH/setup.py
    chmod +x $REPO_DPATH/run_developer_setup.sh
    chmod +x $REPO_DPATH/run_doctests.py
    chmod +x $REPO_DPATH/run_tests.py


    init_pypkg_docs $REPO_NAME
    
    
    echo "FINISHED"
}


init_pypkg_docs(){
    REPO_NAME=$1
    echo "REPO_NAME = $REPO_NAME"

    REPO_DPATH=$HOME/code/$REPO_NAME
    PKG_DPATH=$REPO_DPATH/$REPO_NAME

    echo "MAKING DOCS"
    rm -rf $REPO_DPATH/docs

    mkdir -p $REPO_DPATH/docs

    echo "$(codeblock "
    sphinx
    sphinx-autobuild 
    sphinx_rtd_theme 
    sphinxcontrib-napoleon
    sphinx-autoapi
    six
    Pygments
    ubelt
    ")" >  $REPO_DPATH/docs/requirements.txt

    pip install -r $REPO_DPATH/docs/requirements.txt

    AUTHOR=$(git config --global user.name)
    sphinx-quickstart -q --sep \
        --project=$REPO_NAME \
        --author="$AUTHOR" \
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


    # NOTE: this still isnt working 100% with read-the-docs. 
    # I dont like having to run this manually. It can create stale files and
    # it is difficult to clean / redo.
    sphinx-apidoc -f -o $REPO_DPATH/docs/source $PKG_DPATH --separate

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

    master_doc = 'index' 
    
    ")" >> $REPO_DPATH/docs/source/conf.py

    REPO_URL=$(cd $REPO_DPATH && git remote -v | grep origin | cut  -f2 | cut -d' ' -f1)
    echo "REPO_URL = $REPO_URL"
    
    (cd $REPO_DPATH/docs && PYTHONPATH="$REPO_DPATH:$PYTHONPATH" make html)

    echo "You will likely need to manually edit: $REPO_DPATH/docs/source/index.rst"


    echo "A Good template for what should be in there is:

    :gitlab_url: $REPO_URL

    Welcome to $REPO_NAME's documentation!
    ==================================

    .. The __init__ files contains the top-level documentation overview
    .. automodule:: kwcoco.__init__
       :show-inheritance:

    .. toctree::

       $REPO_NAME

    Indices and tables
    ==================

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`

    "

    cp ~/misc/templates/PYPKG/.readthedocs.yml $REPO_DPATH

    echo "

    To enable the read-the-docs go to https://readthedocs.org/dashboard/ and login

    Make sure you have a .readthedocs.yml file

    Click import project: (for github you can select, but gitlab you need to import manually)


    Set the Repository NAME: $REPO_NAME
    Set the Repository URL: $REPO_URL

    For gitlab you also need to setup an integrations and add gitlab incoming webhook

    Then go to $REPO_URL/hooks and add the URL



    "
}
