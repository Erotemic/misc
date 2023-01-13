__heredoc__(){ NOOP=; }  # define a __heredoc__ function that does nothing

codeblock()
{
    # Prevents python indentation errors in bash
    echo "$1" | python -c "import sys; from textwrap import dedent; print(dedent(sys.stdin.read()).strip('\n'))"
}



__heredoc__ '''
VIAME Detection Challenge - Baseline 

This script outlines a baseline solution to the 2018 VIAME Detection Challenge
using the algorithms provided by Detectron system (developed by Facebook
Research).

Challenge Website:
    http://www.viametoolkit.org/cvpr-2018-workshop-data-challenge/
'''

# The instructions in this script rely on a few predefined directories. 
# You may overwrite these to fit your personal workflow. 
CODE_DIR=$HOME/code
DATA_DIR=$HOME/data
WORK_DIR=$HOME/work


extract_viame_challenge_data(){
    __heredoc__ '''
    Challenge Download Data:
        https://challenge.kitware.com/girder#collection/5a722b2c56357d621cd46c22/folder/5a9028a256357d0cb633ce20
        * Groundtruth: phase0-annotations.tar.gz
        * Images: phase0-imagery.tar.gz
    '''
    # After downloading the data from challenge.kitware.com, extract it to your data directory 
    mkdir -p $DATA_DIR/viame-challenge-2018
    tar xvzf $HOME/Downloads/phase0-annotations.tar.gz -C $DATA_DIR/viame-challenge-2018
    tar xvzf $HOME/Downloads/phase0-imagery.tar.gz -C $DATA_DIR/viame-challenge-2018
}


install_detectron_docker_image(){
    __heredoc__ '''
    setup a docker container with caffe2 and detectron installed

    Detectron Install Docs:
        https://github.com/facebookresearch/Detectron/blob/master/INSTALL.md 
    '''
    DETECTRON=$CODE_DIR/Detectron
    if [ ! -d "$DETECTRON" ]; then
        git clone https://github.com/facebookresearch/Detectron.git $DETECTRON
    fi
    # Build the docker container with caffe2 and detectron (which must use python2 ☹)
    cd $DETECTRON/docker
    docker build -t detectron:c2-cuda9-cudnn7 .
    # test the image to make sure it works
    nvidia-docker run -v ~/data:/data --rm -it detectron:c2-cuda9-cudnn7 python2 tests/test_batch_permutation_op.py 
}

train_detectron_model(){
    # startup the detectron docker image and mount your data and work directory
    nvidia-docker run -v $WORK_DIR:/work $DATA_DIR:/data -it detectron:c2-cuda9-cudnn7 bash

    codeblock "
    MODEL:
      TYPE: generalized_rcnn
      CONV_BODY: ResNet.add_ResNet50_conv4_body
      NUM_CLASSES: 81
      FASTER_RCNN: True
    NUM_GPUS: 1
    SOLVER:
      WEIGHT_DECAY: 0.0001
      LR_POLICY: steps_with_decay
      BASE_LR: 0.01
      GAMMA: 0.1
      # 1x schedule (note TRAIN.IMS_PER_BATCH: 1)
      MAX_ITER: 180000
      STEPS: [0, 120000, 160000]
    RPN:
      SIZES: (32, 64, 128, 256, 512)
    FAST_RCNN:
      ROI_BOX_HEAD: ResNet.add_ResNet_roi_conv5_head
      ROI_XFORM_METHOD: RoIAlign
    TRAIN:
      WEIGHTS: https://s3-us-west-2.amazonaws.com/detectron/ImageNetPretrained/MSRA/R-50.pkl
      DATASETS: ('coco_2014_train', 'coco_2014_valminusminival')
      SCALES: (800,)
      MAX_SIZE: 1333
      IMS_PER_BATCH: 1
      BATCH_SIZE_PER_IM: 512
    TEST:
      DATASETS: ('coco_2014_minival',)
      SCALES: (800,)
      MAX_SIZE: 1333
      NMS: 0.5
      RPN_PRE_NMS_TOP_N: 6000
      RPN_POST_NMS_TOP_N: 1000
    OUTPUT_DIR: $WORK_DIR/viame-challenge-2018/output
    " > $WORK_DIR/viame-challenge-2018/viame_baseline_faster_rcnn.yaml
    

    python2 tools/train_net.py \
        --cfg $WORK_DIR/viame-challenge-2018/viame_baseline_faster_rcnn.yaml \
        OUTPUT_DIR $WORK_DIR/viame-challenge-2018/output
}


# Setup the challenge data
extract_viame_challenge_data

# Checkout, install, and test the Detectron docker image
install_detectron_docker_image
