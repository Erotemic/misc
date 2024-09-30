# syntax=docker/dockerfile:1.5.0

# **************************************************
# Builds a docker image to make it easy to send a
# particular person a GPG message.
# **************************************************

FROM ubuntu

## Install Prerequisites 
RUN <<EOF
#!/bin/bash
apt update -q
DEBIAN_FRONTEND=noninteractive apt install -q -y --no-install-recommends \
        gnupg2 
apt-get clean 
rm -rf /var/lib/apt/lists/*
EOF

env RECIPIENT_FINGERPRINT=4AC8B478335ED6ED667715F3622BE571405441B4

RUN <<EOF
#!/bin/bash
gpg --recv-keys --keyserver hkp://keyserver.ubuntu.com $RECIPIENT_FINGERPRINT
EOF


RUN <<EOF
#!/bin/bash
gpg --list-keys --fingerprint --with-colons "$RECIPIENT_FINGERPRINT" | \
    sed -E -n -e 's/^fpr:::::::::([0-9A-F]+):$/\1:6:/p' | \
    gpg --import-ownertrust
EOF


ENTRYPOINT gpg --encrypt --armor --recipient $RECIPIENT_FINGERPRINT


################
### __DOCS__ ###
################
RUN <<EOF
echo '
# https://www.docker.com/blog/introduction-to-heredocs-in-dockerfiles/

# docker login
# docker pull docker/dockerfile:1.3.0-labs

cd ~/misc/learn/

SeeAlso:
~/misc/learn/send_me_a_gpg_message.sh

LATEST_TAG=20240930
DOCKER_BUILDKIT=1 docker build --progress=plain \
    -t erotemic/send-erotemic-a-gpg-message:$LATEST_TAG \
    -f send_me_a_gpg_message.dockerfile .
docker image tag erotemic/send-erotemic-a-gpg-message:$LATEST_TAG erotemic/send-erotemic-a-gpg-message:latest 
docker push erotemic/send-erotemic-a-gpg-message:$LATEST_TAG 
docker push erotemic/send-erotemic-a-gpg-message:latest 

# Main usage looks like this:
echo "
--- START YOUR MESSAGE ---
Hello world,
This is a super secret message, encrypted using docker.
--- END YOUR MESSAGE ---
" | docker run -i erotemic/send-erotemic-a-gpg-message


'
EOF

