IsMAGE_NAME=mgoltzsche/podman:minimal
docker run --privileged -v "$HOME/.cache/pip:/pip_cache" -it $IMAGE_NAME sh

adduser custom_user -D
su custom_user
cd "$HOME"

# Make a storage.conf and containers.conf file
#
# https://github.com/containers/common/blob/main/docs/containers.conf.5.md
# https://github.com/containers/storage/blob/main/docs/containers-storage.conf.5.md
export CONTAINERS_CONF="$(pwd)/temp_containers.conf"
export CONTAINERS_STORAGE_CONF="$(pwd)/temp_storage.conf"
echo "CONTAINERS_CONF = $CONTAINERS_CONF"
echo "CONTAINERS_STORAGE_CONF = $CONTAINERS_STORAGE_CONF"

# --
echo "
[storage]
driver=\"vfs\"
rootless_storage_path=\"$HOME/.local/share/containers/vfs-rootless-storage\"
graphroot=\"$HOME/.local/share/containers/vfs-storage\"
runroot=\"$HOME/.local/share/containers/vfs-runroot\"
[storage.options.aufs]
mountopt=\"rw\"
[storage.options.vfs]
ignore_chown_errors="true"
" > "$CONTAINERS_STORAGE_CONF"
# --
# For defaults see /usr/share/containers/containers.conf
echo "
[containers]
default_capabilities = [
\"CHOWN\",
\"DAC_OVERRIDE\",
\"FOWNER\",
\"FSETID\",
\"KILL\",
\"NET_BIND_SERVICE\",
\"SETFCAP\",
\"SETGID\",
\"SETPCAP\",
\"SETUID\",
\"SYS_CHROOT\"
]
[engine]
cgroup_manager=\"cgroupfs\"
events_logger=\"file\"
" > "$CONTAINERS_CONF"

#podman run ubi8 mount
#podman run --privileged ubi8 mount
cat "$CONTAINERS_CONF"
cat "$CONTAINERS_STORAGE_CONF"


podman create --name=test_container1 --interactive --volume=/:/host:Z docker.io/library/alpine:3.15 /bin/bash


ls -al $HOME/.local/share/containers/
