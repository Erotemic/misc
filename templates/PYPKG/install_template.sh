#!/bin/bash
__doc__="""
TODO: Port logic from ~/misc/make_new_python_package_repo.sh
"""

update_pypkg(){
    __doc__="
    source ~/misc/templates/PYPKG/install_template.sh
    REPO_NAME=pyflann_ibeis
    print_pullreq_url
    update_pypkg $REPO_NAME
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

    cp -rv "$TEMPLATE_DPATH"/publish.sh .
    #find . -iname '*.yml' | xargs sed -i "s/PYPKG/$REPO_NAME/g"

    chmod +x ./setup.py
    chmod +x ./publish.sh
    chmod +x ./run_developer_setup.sh
    chmod +x ./run_doctests.py
    chmod +x ./run_tests.py

    IS_BINARY="1"
    if [[ "$IS_BINARY" == "1" ]]; then
        sed -i 's|="pure"|="binary|g' publish.sh
    else
        ecoh "TOTO: Can do setup magic here"
    fi

    git add .github
    git add dev/setup_secrets.sh
    git add dev/make_strict_req.sh

    echo "REPLACING PACKAGE NAME REFERENCES"
    # shellcheck disable=SC2038
    find . -iname '*.yml' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    # shellcheck disable=SC2038
    find . -iname '*.sh' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    # shellcheck disable=SC2038
    find . -iname '*.py' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    # shellcheck disable=SC2038
    find . -iname '*.ini' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    # shellcheck disable=SC2038
    find . -iname '*.coveragerc' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    # shellcheck disable=SC2038
    find . -iname '*.py' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    # shellcheck disable=SC2038
    find . -iname '*' | xargs sed -i "s/PYPKG/$REPO_NAME/g"
    # shellcheck disable=SC2038
    find . -iname '*.rst' | xargs sed -i "s/PYPKG/$REPO_NAME/g"


    # Do setup
    echo "
    Need to run one of

    source dev/setup_secrets.sh
    setup_package_environs_github_erotemic
    #setup_package_environs_gitlab_kitware
    #setup_package_environs_github_pyutils

    load_secrets
    upload_github_secrets
    #upload_gitlab_group_secrets
    #upload_gitlab_repo_secrets

    export_encrypted_code_signing_keys
    "

    # <FIXME>
    #TEXT="$(codeblock "
    #Update Requirments:
    #    # Requirements are broken down by type in the requirements folder, and
    #    # requirments.txt lists them all. Thus we autogenerate via:
    #    cat requirements/*.txt > requirements.txt
        
    #")" 
    #echo "TEXT = $TEXT"
    #sed "s/Pypi:/${TEXT}Pypi:/g" setup.py
    # </FIXME>

    #git tag -a "first" "$(git rev-list --max-parents=0 HEAD)" -m "first commit"
    #git push --tags
    #(git checkout -b "first" "$(git rev-list --max-parents=0 HEAD)" ; git push) && git checkout - 

    #>> $REPO_DPATH/docs/source/conf.py
}
