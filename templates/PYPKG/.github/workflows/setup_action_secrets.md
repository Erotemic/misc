==========================
GITHUB ACTION INSTRUCTIONS
==========================

This file is a reference script for setting up secrets for github actions
(because currently we can't add heredocs to github yaml files like we can with
other CI tools)

This file was designed to be used as a template. You can adapt it to
new projects with a few simple changes.  Namely perform the following
search and replaces.


# TODO: re-setup template

```bash
cat .github/workflows/setup_action_secrets.md | \
    sed 's|GITHUB_USER|<YOUR-GITHUB-USERNAME>|g' | \
    sed 's|PYPKG|<YOUR-REPO>|g' | \
    sed 's|GPG_ID|<YOUR-GPG-ID>|g' | \
    sed 's|PKG_CI_SECRET|<YOUR_CI_SECRET>|g' 
> /tmp/repl 

# Check the diff
colordiff .github/workflows/setup_action_secrets.md /tmp/repl

# overwrite if you like the diff
cp /tmp/repl .github/workflows/setup_action_secrets.md
```

For example, xdoctest may use:

```bash
cat .github/workflows/setup_action_secrets.md | \
    sed 's|GITHUB_USER|Erotemic|g' | \
    sed 's|PYPKG|xdoctest|g' | \
    sed 's|GPG_ID|travis-ci-Erotemic|g' | \
    sed 's|PKG_CI_SECRET|CI_SECRET|g' | \
tee /tmp/repl && colordiff .github/workflows/setup_action_secrets.md /tmp/repl
# overwrite if you like the diff
cp /tmp/repl .github/workflow/setup_action_secrets.md
```


To use this script you need the following configurations on your CI account.

NOTES
-----

* This script will require maintenance for new releases of Python


CI SECRETS
----------

Almost all of the stages in this pipeline can be performed on a local machine
(making it much easier to debug) as well as the CI machine. However, there are
a handful of required environment variables which will contain sensitive
information. These variables are

* `TWINE_USERNAME` - this is your pypi username
    twine info is only needed if you want to automatically publish to pypi

* `TWINE_PASSWORD` - this is your pypi password 

* `PKG_CI_SECRET` - We will use this as a secret key to encrypt/decrypt gpg secrets 
    This is only needed if you want to automatically sign published
    wheels with a gpg key.

* `PERSONAL_GITHUB_PUSH_TOKEN` - 
    This is only needed if you want to automatically git-tag release branches.

    To make a API token go to:
        https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/creating-a-personal-access-token

Instructions:

    Browse to: 
        https://github.com/GITHUB_USER/PYPKG/settings/secrets/actions

    Do whatever you need to locally access the values of these variables

    echo $TWINE_USERNAME
    echo $PERSONAL_GITHUB_PUSH_TOKEN
    echo $PKG_CI_SECRET
    echo $TWINE_PASSWORD

    For each one, click "Add Environment Variable" and enter the name
    and value. Unfortunately this is a manual process.

WARNING: 

Ensure that your project settings do not allow Forks to view environment
variables.

TODO: Can you protect branches on GithubActions? Is that the default?

TODO: Look into secrethub

WARNING: If an untrusted actor gains the ability to write to a
protected branch, then they will be able to exfiltrate your secrets.

WARNING: These variables contain secret information. Ensure that these
the protected and masked settings are enabled when you create them.


ENCRYPTING GPG SECRETS
----------------------

The following script demonstrates how to securely encrypt a secret GPG key. It
is assumed that you have a file `secret_loader.sh` that looks like this

```bash
    source secretfile
```

and then a secret file that looks like this

```bash
    #!/bin/bash
    echo /some/secret/file 

    export TWINE_USERNAME=<pypi-username>
    export TWINE_PASSWORD=<pypi-password>
    export PKG_CI_SECRET="<a-very-long-secret-string>"
    export PERSONAL_GITHUB_PUSH_TOKEN="git-push-token:<token-password>"
```

You should also make a `secret_unloader.sh` that points to a script that
unloads these secret variables from the environment.

Given this file-structure setup, you can then run the following
commands verbatim. Alternatively just populate the environment
variables and run line-by-line without creating the secret
loader/unloader scripts.

```bash
# THIS IS NOT EXECUTE ON THE CI, THIS IS FOR DEVELOPER REFERENCE
# ON HOW THE ENCRYPTED GPG KEYS ARE SETUP.

# Load or generate secrets
source $(secret_loader.sh)
echo $PKG_CI_SECRET
echo $TWINE_USERNAME

# ADD RELEVANT VARIABLES TO CIRCLECI SECRET VARIABLES
# https://app.circleci.com/settings/project/github/Erotemic/xdoctest/environment-variables
# See previous CIRCLE_CI section for more details

# HOW TO ENCRYPT YOUR SECRET GPG KEY
IDENTIFIER="travis-ci-Erotemic"
GPG_KEYID=$(gpg --list-keys --keyid-format LONG "$IDENTIFIER" | head -n 2 | tail -n 1 | awk '{print $1}' | tail -c 9)
echo "GPG_KEYID = $GPG_KEYID"

# Export plaintext gpg public keys, private keys, and trust info
mkdir -p dev
gpg --armor --export-secret-keys $GPG_KEYID > dev/ci_secret_gpg_key.pgp
gpg --armor --export $GPG_KEYID > dev/ci_public_gpg_key.pgp
gpg --export-ownertrust > dev/gpg_owner_trust

# Encrypt gpg keys and trust with CI secret
GLKWS=$PKG_CI_SECRET openssl enc -aes-256-cbc -pbkdf2 -md SHA512 -pass env:GLKWS -e -a -in dev/ci_public_gpg_key.pgp > dev/ci_public_gpg_key.pgp.enc
GLKWS=$PKG_CI_SECRET openssl enc -aes-256-cbc -pbkdf2 -md SHA512 -pass env:GLKWS -e -a -in dev/ci_secret_gpg_key.pgp > dev/ci_secret_gpg_key.pgp.enc
GLKWS=$PKG_CI_SECRET openssl enc -aes-256-cbc -pbkdf2 -md SHA512 -pass env:GLKWS -e -a -in dev/gpg_owner_trust > dev/gpg_owner_trust.enc
echo $GPG_KEYID > dev/public_gpg_key

# Test decrpyt
cat dev/public_gpg_key
GLKWS=$PKG_CI_SECRET openssl enc -aes-256-cbc -pbkdf2 -md SHA512 -pass env:GLKWS -d -a -in dev/ci_public_gpg_key.pgp.enc 
GLKWS=$PKG_CI_SECRET openssl enc -aes-256-cbc -pbkdf2 -md SHA512 -pass env:GLKWS -d -a -in dev/gpg_owner_trust.enc 
GLKWS=$PKG_CI_SECRET openssl enc -aes-256-cbc -pbkdf2 -md SHA512 -pass env:GLKWS -d -a -in dev/ci_secret_gpg_key.pgp.enc 

source $(secret_unloader.sh)

# Look at what we did, clean up, and add it to git
ls dev/*.enc
rm dev/gpg_owner_trust dev/*.pgp
git status
git add dev/*.enc
git add dev/public_gpg_key
```


Test Github Push Token 
----------------------

The following script tests if your `PERSONAL_GITHUB_PUSH_TOKEN` environment variable is correctly setup.

```bash
docker run -it ubuntu
apt update -y && apt install git -y
git clone https://github.com/Erotemic/xdoctest.git
cd xdoctest
# do sed twice to handle the case of https clone with and without a read token
git config user.email "ci@circleci.com"
git config user.name "CircleCI-User"
URL_HOST=$(git remote get-url origin | sed -e 's|https\?://.*@||g' | sed -e 's|https\?://||g')
echo "URL_HOST = $URL_HOST"
git tag "test-tag4"
git push --tags "https://${PERSONAL_GITHUB_PUSH_TOKEN}@${URL_HOST}"

# Cleanup after you verify the tags shows up on the remote
git push --delete origin test-tag4
git tag --delete test-tag4

