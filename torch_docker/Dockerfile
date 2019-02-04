#FROM centos6
FROM nvidia/cuda:9.2-cudnn7-devel-ubuntu18.04
ENV TERM linux

# Fixes display issues when we write out utf-8 text
ENV PYTHONIOENCODING UTF-8
ENV LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl git bzip2 openssh-client make \
        gcc g++ gfortran build-essential \
        imagemagick \
        libglib2.0-0 libsm6 libice6 libsm6 libxt6 libxrender1 libfontconfig1 libcups2 libxext6 
       
# Tell docker that we want to use bash as our default shell
SHELL ["/bin/bash", "-c"]  

# Download miniconda
RUN mkdir -p /root/tmp
WORKDIR /root/tmp
ENV CONDA_INSTALL_SCRIPT=Miniconda3-latest-Linux-x86_64.sh
RUN curl https://repo.continuum.io/miniconda/$CONDA_INSTALL_SCRIPT > $CONDA_INSTALL_SCRIPT
RUN chmod +x $CONDA_INSTALL_SCRIPT 

# Install miniconda to user local directory
ENV _CONDA_ROOT=/root/.local/conda
RUN mkdir -p $HOME/.local
RUN ./$CONDA_INSTALL_SCRIPT -b -p $_CONDA_ROOT

# Setup the conda virtual environment
RUN source $_CONDA_ROOT/etc/profile.d/conda.sh  && \
    conda create -y -n py36 python=3.6 && \
    conda activate py36

# Write the script to activate conda
RUN echo '_CONDA_ROOT=$HOME/.local/conda' >> $HOME/conda_bashrc.sh && \
    echo 'source $_CONDA_ROOT/etc/profile.d/conda.sh' >> $HOME/conda_bashrc.sh && \
    echo 'conda activate py36' >> $HOME/conda_bashrc.sh

# Source script in bashrc to activate conda on login
RUN echo 'source $HOME/conda_bashrc.sh' >> $HOME/.bashrc 
RUN cat $HOME/conda_bashrc.sh

# Setup a few packages before installing our libs
RUN source $HOME/conda_bashrc.sh && pip install --upgrade pip
RUN source $HOME/conda_bashrc.sh && pip install ipython ipdb
RUN source $HOME/conda_bashrc.sh && pip install xdoctest 

RUN source $HOME/conda_bashrc.sh && conda install numpy pyyaml mkl mkl-include setuptools cmake cffi typing six Cython scipy -y

# Note: we cannot use $HOME in docker commands other than RUN.
# Note that the default home directory is /root
WORKDIR /root
RUN mkdir -p $HOME/code
RUN git clone --recursive https://github.com/pytorch/pytorch $HOME/code/pytorch
WORKDIR /root/code/pytorch

# FORGOT TO INSTALL VIM!
RUN apt install vim -y

RUN source $HOME/conda_bashrc.sh && \
    git remote add Erotemic https://github.com/Erotemic/pytorch && \
    git fetch --all && \
    git checkout dev/integrate_xdoctest 
RUN source $HOME/conda_bashrc.sh && python setup.py develop

#RUN git clone --branch dev/integrate_xdoctest --recursive https://github.com/Erotemic/pytorch $HOME/code/pytorch
#WORKDIR /root/code/pytorch
#RUN source $HOME/conda_bashrc.sh && python setup.py develop

#RUN source $HOME/conda_bashrc.sh && \
#    ./tools/run_doctests.sh

#git remote add Erotemic https://github.com/Erotemic/pytorch &&

RUN __DUMMY_COMMANDS_="
    cd ~/misc/torch_docker
    docker build -f ./Dockerfile --tag torch_dev_env .

    docker run --runtime=nvidia --rm -it torch_dev_env bash
"
