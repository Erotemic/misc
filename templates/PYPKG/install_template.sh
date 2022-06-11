#!/bin/bash
__doc__="""
TODO: Port logic from ~/misc/make_new_python_package_repo.sh
"""

update_pypkg(){
    __doc__="
    REPO_NAME=pyflann_ibeis
    "
    REPO_NAME=$1
    #
    REPO_DPATH=$HOME/code/$REPO_NAME

    TEMPLATE_DPATH=$HOME/misc/templates/PYPKG/

    source "$HOME/local/init/utils.sh"

    cd "$REPO_DPATH"
    #cp -r "$TEMPLATE_DPATH"/.circleci .
    cp -rv "$TEMPLATE_DPATH"/.github .
    cp -rv "$TEMPLATE_DPATH"/dev/ .
    #find . -iname '*.yml' | xargs sed -i "s/PYPKG/$REPO_NAME/g"

    chmod +x ./setup.py
    chmod +x ./run_developer_setup.sh
    chmod +x ./run_doctests.py
    chmod +x ./run_tests.py

    git add .github
    git add dev/setup_secrets.sh
    git add dev/make_strict_req.sh

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
    #(git checkout -b "first" "$(git rev-list --max-parents=0 HEAD)" ; git push) && git checkout - 

    #>> $REPO_DPATH/docs/source/conf.py
}

