#!/bin/bash

# Related to:
# https://github.com/pypa/cibuildwheel/pull/966#discussion_r906712059

# Create a podman container with "-w"
podman create --name=foobar-podman-test --interactive -w "/createme-dir" python:3.7 /bin/bash
# Running the exec here will fail because the container is not started
podman exec -i foobar-podman-test mkdir -p "/createme-dir"
# But starting the container raises an error when create was used with "-w"
podman start foobar-podman-test
# Cleanup
podman rm --force -v foobar-podman-test



# Demo where this sequence works with docker
docker create --name=foobar-docker-test --interactive -w "/createme-dir"  python:3.7 /bin/bash
docker start foobar-docker-test
docker exec -i foobar-docker-test mkdir -p "/createme-dir"
docker rm --force -v foobar-docker-test
