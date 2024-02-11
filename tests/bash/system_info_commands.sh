#!/usr/bin/env bash

# Get amd64, arm64, etc arch info
dpkg --print-architecture

lsb_release -a

# Codename (e.g. impish)
lsb_release -cs

# Lots of info
cat /proc/cpuinfo

# arch type in x86_64 format
# x86_64
uname -m

# Kernel info
# Linux toothbrush 5.13.0-40-generic #45-Ubuntu SMP Tue Mar 29 14:48:14 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux
uname -a


# More OS Name stuff
cat /etc/issue

cat /etc/os-release

hostnamectl


# Bash config files:
# https://unix.stackexchange.com/questions/175648/use-config-file-for-my-shell-script
INST_ARCH=$(uname -m)
NAME=$( (source /etc/os-release && echo "$NAME") | tr '[:upper:]' '[:lower:]' )
VER=$( (source /etc/os-release && echo "$VERSION_ID") | sed 's/\.//g' )
NVIDIA_DISTRO=${NAME}${VER}
NVIDIA_DISTRO_ARCH=${NVIDIA_DISTRO}/${INST_ARCH}
echo "NVIDIA_DISTRO_ARCH = $NVIDIA_DISTRO_ARCH"
apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/"$NVIDIA_DISTRO_ARCH"/3bf863cc.pub


#wget "https://developer.download.nvidia.com/compute/cuda/repos/${NVIDIA_DISTRO_ARCH}/cuda-keyring_1.0-1_all.deb"

# https://forums.developer.nvidia.com/t/notice-cuda-linux-repository-key-rotation/212772
sudo apt-key del 7fa2af80
sudo dpkg -i cuda-keyring_1.0-1_all.deb
