# http://torch.ch/docs/getting-started.html

apt_install_docker(){
    # FIXME: 
    # Doesn't work on Ooo.
    # Worked on Namek.

    # Create a docker group if one does not exist
    if [[ $(groups | grep docker) == "" ]]; then
        sudo groupadd docker
    fi
    # Add current $USER to docker group if not in it already
    if [[ $(groups $USER | grep docker) == "" ]]; then
        sudo usermod -aG docker $USER
        # NEED TO LOGOUT / LOGIN to revaluate groups
        su - $USER  # or we can do this
    fi

    if [ $(which nvidia-docker) == "" ]; then
        # Install the apt sources for nvidia-docker2
        curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
        curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
          sudo tee /etc/apt/sources.list.d/nvidia-docker.list
        sudo apt-get update

        sudo apt-get install nvidia-docker2
        sudo pkill -SIGHUP dockerd
    fi

    # https://github.com/moby/moby/issues/3127
    # ENSURE ALL DOCKER PROCS ARE CLOSED
    docker ps -q | xargs docker kill


    # MOVE DOCKER DATA DIRECTORY TO EXTERNAL DRIVE
    if [$(grep '^DOCKER.*g /data/docker' /etc/default/docker) != "" ]; then
        # Shutdown docker while we make configuration changes
        sudo service docker stop
        #Ubuntu/Debian: edit your /etc/default/docker file with the -g option: 
        # NOTE: only do this if you don't want the docker cache directory somewhere else
        sudo sed -ie 's|^#* *DOCKER_OPTS.*|DOCKER_OPTS="-g /data/docker"|g' /etc/default/docker
        sudo sed -ie 's|^#* *export DOCKER_TMPDIR.*|export DOCKER_TMPDIR=/data/docker-tmp|g' /etc/default/docker
        cat /etc/default/docker
        sudo service docker start
    fi

    if [ -f "/etc/systemd/system/docker.service.d/override.conf" ]; then
        # https://github.com/nvidia/nvidia-container-runtime#docker-engine-setup
        # We need to point the systemctl docker serivce to this file
        cat /lib/systemd/system/docker.service

        # the proper way to edit systemd service file is to create a file in
        # /etc/systemd/system/docker.service.d/<something>.conf and only override
        # the directives you need. The file in /lib/systemd/system/docker.service
        # is "reserved" for the package vendor.
        sudo mkdir -p /etc/systemd/system/docker.service.d

        source ~/local/init/utils.sh

        sudo rm /etc/systemd/system/docker.service.d/override.conf
        sudo_writeto /etc/systemd/system/docker.service.d/override.conf '
            [Service]
            ExecStart=
            ExecStart=/usr/bin/dockerd --host=fd:// --add-runtime=nvidia=/usr/bin/nvidia-container-runtime \$DOCKER_OPTS
            '
        cat /etc/systemd/system/docker.service.d/override.conf
        echo ""
        echo "Updated the docker configuration"
        sudo systemctl daemon-reload
        sudo service docker restart

        sudo systemctl restart docker
    fi
}

test_install_worked(){
    #docker run --runtime=nvidia --rm python:3.6
    #docker run --runtime=nvidia --rm python:3.6 bash -it
    docker run --runtime=nvidia --rm -it nvidia/cuda:9.2-cudnn7-runtime-ubuntu16.04 bash
}

build_torch_dockerfile(){ 
    cd ~/misc/torch_docker
    docker build -f ./Dockerfile --tag torch_dev_env .
    docker run --runtime=nvidia --rm -it torch_dev_env bash
    docker run --rm -it torch_dev_env bash
}
