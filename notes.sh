cd ~/code/VIAME/plugins/camtrawl/python
export PYTHONPATH=$(pwd):$PYTHONPATH


workon_py2
export KWIVER_PLUGIN_PATH=""
export SPROKIT_MODULE_PATH=""
source ~/code/VIAME/build-py2/install/setup_viame.sh
export KWIVER_PYTHON_DEFAULT_LOG_LEVEL=debug
export KWIVER_DEFAULT_LOG_LEVEL=debug
export KWIVER_DEFAULT_LOG_LEVEL=info

export KWIVER_PYTHON_COLOREDLOGS=1

#SeeAlso: ~/code/kwiver/examples/tracking_pipelines/README.md

processopedia


cd ~/code/VIAME/examples/tracking_pipelines
pipeline_runner -p ~/code/VIAME/examples/tracking_pipelines/simple_tracker.pipe


cd ~/code/VIAME/examples/detector_pipelines
#pipeline_runner -p ~/code/VIAME/examples/detector_pipelines/yolo_v2_detector.pipe
pipeline_runner -p ~/code/VIAME/examples/detector_pipelines/scallop_tk_detector.pipe


cd ~/code/VIAME/examples/hello_world_pipeline
pipeline_runner -p ~/code/VIAME/examples/hello_world_pipeline/hello_world_detector.pipe
pipeline_runner -p ~/code/VIAME/examples/hello_world_pipeline/hello_world_python.pipe


#python ~/code/VIAME/plugins/camtrawl/python/run_camtrawl.py
#python run_camtrawl.py
#pipeline_runner -p ~/.cache/sprokit/temp_pipelines/temp_pipeline_file.pipe
#pipeline_runner -p camtrawl.pipe -S pythread_per_process


Tracking related files:

~/code/VIAME/packages/kwiver/

git diff --name-status master..HEAD | grep ^

git diff --name-status dev/segnet..HEAD | grep ^A
git diff --name-status dev/tracking-framework..HEAD | grep ^A
#git merge-base dev/tracking-framework master
#git diff --name-status dev/tracking-framework..1ea4cd274487928c9617f8c26b03fb43369f6ff9 | grep ^A

pypipe()
{
    COMMAND=$1
    #python -c "import sys; [sys.stdout.write(line.replace('$1', '$2')) for line in sys.stdin.readlines()]"
    python -c "import sys; from os.path import *; [sys.stdout.write($1) for line in sys.stdin.readlines()]"
}

replace()
{
    pypipe "line.replace('$1', '$2')"
    #python -c "import sys; [sys.stdout.write(x.replace('$1', '$2')) for x in sys.stdin.readlines()]"
}

abspath()
{
    pypipe "abspath(line)"
    #python -c "import os, sys; [sys.stdout.write(os.path.abspath(x)) for x in sys.stdin.readlines()]"
}

filter-file-diff()
{
    grep ^$1 | replace "$1\t" "" | abspath | pypipe "'$1 ' + line" 
}


git-new-files(){
    BRANCH=$1
    MASTER=$2
    MERGE_BASE=$(git merge-base $MASTER $BRANCH)
    git diff --name-status $MERGE_BASE..$BRANCH | filter-file-diff A
    #git diff --name-status $MERGE_BASE..$BRANCH | filter-file-diff D
    #python -c "import os, sys; [sys.stdout.write(os.path.abspath(x.replace('A\t', ''))) for x in sys.stdin.readlines()]"
}

BRANCH=dev/tracking-framework 
BASE=master

git-new-files dev/tracking-framework master
git-new-files dev/tracking-framework HEAD


NOTE TO PIP INSTALL SMQTK with psycopg2 we need the postgres dev libs
sudo apt-get install libpq-dev

source ~/code/VIAME/build/install/setup_viame.sh
cd /home/joncrall/code/VIAME/examples/tracking_pipelines
~/code/VIAME/build/install/bin/pipe_to_dot -p simple_tracker.pipe -o g.dot
dot -Tpng g.dot > g.png


github query-wip
github dev/tracking-framework
kwgitlab dev/obj_tracking
 
gitk master jon/viame/master jon/viame/next viame/master viame/query-wip viame/tracking-work viame/master-w-pytorch viame/master-no-pybind viame/add-descriptor-pipeline


gitk master dev/tracking-framework
gitk master viame/tracking-work

git merge-base --independent viame/tracking-work dev/tracking-framework
echo $?
git merge-base --is-ancestor dev/tracking-framework viame/tracking-work 
echo $?

git merge-base --is-ancestor dev/tracking-framework jon/viame/next
git merge-base --is-ancestor jon/viame/next dev/tracking-framework 
echo $?


git merge-base master viame/master
#git merge-base --is-ancestor <commit> <commit>
#git merge-base --independent <commit>…​
#git merge-base --fork-point <ref> [<commit>]


make_diva_kwiver(){
    git co master
    git co -b jon/diva/master
    git merge dev/tracking-framework
    git merge viame/query-wip

    git log --name-only master..dev/tracking-framework
}

# Note viame/next kwiver sha 7a9285a83f8fe1f814fb71e4d69d0ec110fe916b
# Note viame/master kwiver sha edd8fb851103ede39c235bc44bf8b1ce62c080e7

python ~/misc/git-branch-relationships.py "
    jon/viame/master
    jon/viame/next
    master
    dev/tracking-framework
    viame/master
    viame/query-wip
    viame/tracking-work
    viame/master-no-pybind
    viame/master-w-pytorch
    dev/obj_tracking
    7a9285a83f8fe
    edd8fb851103e
"


gitk viame/query-wip viame/master dev/tracking-framework


merging_query_wip(){
    git co viame/query-wip
    git co -b jon/viame/query-wip

    #gitk ab450923532ed904035939d123bf15e8fc8c5127

    git cherry-pick df4813f971ce7c123152ee44d7fde1a765ab05b8
    git cherry-pick 1c1b7365f691dd9bafaf6e45f38248845f22820c
    git cherry-pick eab3b29a912484043378046afd114416da6f7e17

    git co jon/diva/master
    git merge jon/viame/query-wip

}

# list all branches that have commit as an ancestor
gitk --all --ancestry-path viame/query-wip..


#Required classes:

CLASSES=(compute_track_descriptors
compute_association_matrix
associate_detections_to_tracks 
initialize_object_tracks 
write_object_track 
image_object_detector 
detected_object_output 
frame_list_input)
     

for i in ${CLASSES[@]}; do
    echo class: $i
    cgrep --files-with-matches --exclude "*.dot*" --exclude "*.rst*" --exclude "*.pipe*" $i
    #fzfind $i
done

    cgrep --files-with-matches --exclude "*.dot*" --exclude "*.rst*" --exclude "*.pipe*" compute_track_descriptors




As far as I can tell there are a few things that need to be done:

* dev/tracking-framework needs to be merged into KWIVER master, however there are issues preventing that from happening. The PR is too big and lacks tests. I believe Matt P is working on this front, but progress is slow. How should we proceed? Perhaps we make a diva/master branch and work off of that?

* There are parts of the tracking pipeline that depend on burnout, smqtk, vivia, etc...
What are these parts? In other words, what functionality from VIAME needs to be ported other than the dev/tracking-framework branch?

* kwiver has an enable_burnout option, but all it does is `find_package( vidtk REQUIRED )`.

For reference the following classes referenced in the tracker pipeline are not currently in kwiver master. However, I believe they are in dev/tracking-framework
class: compute_association_matrix
class: associate_detections_to_tracks
class: initialize_object_tracks
class: write_object_track




python -c "from kwiver.util.vital_type_converters import ctypes; print(ctypes)"

# Runs kwiver standalone simple example
(cd ~/code/kwiver/build-py2/examples/pipelines && pipeline_runner -p number_flow.pipe)


# Find libraries loaded on runtime 
# https://stackoverflow.com/questions/5103443/how-to-check-what-shared-libraries-are-loaded-at-run-time-for-a-given-process
python ~/misc/ldd_graph.py processopedia
strace processopedia 2>&1 | grep '^open(".*\.so"' | grep -v "= -1"
strace processopedia 2>&1 | grep '^open(".*\.so"' | grep -v "= -1" | grep python -A 10000 -B 10000



 git diff --name-only jon/diva/master jon/viame/master

 

README.rst
gitk jon/diva/master jon/viame/master arrows/core/handle_descriptor_request_core.cxx
gitk jon/diva/master jon/viame/master arrows/darknet/darknet_detector.cxx

arrows/ocv/refine_detections_write_to_disk.cxx
arrows/uuid/tests/CMakeLists.txt
arrows/uuid/tests/test_uuid_factory.cxx
doc/manuals/_images/cmake/cmake_step_2.png
doc/manuals/_images/cmake/cmake_step_3.png
examples/external/darknet.zip.sha512
sprokit/CMakeLists.txt
sprokit/conf/sprokit-macro-python-tests.cmake
sprokit/processes/vxl/kw_archive_writer_process.cxx
sprokit/src/bindings/python/modules/loaders.py
sprokit/src/bindings/python/sprokit/pipeline/process.cxx
sprokit/src/bindings/python/sprokit/pipeline/process_factory.cxx
sprokit/src/bindings/python/sprokit/pipeline/scheduler_factory.cxx
sprokit/src/sprokit/pipeline/CMakeLists.txt
sprokit/src/sprokit/pipeline/process.h
sprokit/src/sprokit/pipeline/process_factory.cxx
sprokit/src/sprokit/pipeline/process_factory.h
sprokit/src/sprokit/pipeline/scheduler_factory.cxx
sprokit/src/sprokit/pipeline/scheduler_factory.h
sprokit/tests/bindings/python/CMakeLists.txt
tests/test_gtest.h
 

===============


git co jon/master


python ~/misc/git/git_xadd.py \
    vital/CMakeLists.txt \
    vital/tests/test_image_container_set.cxx \
    vital/types/image_container_set.h \
    vital/tests/CMakeLists.txt \
    --branch=dev/add_vital_type_image_container_set \
    --base=master \ 
    -m "add vital type: image_container_set"

git merge dev/add_vital_type_image_container_set


python ~/misc/git/git_xadd.py \
    vital/CMakeLists.txt \
    sprokit/processes/core/extract_image_descriptor_process.cxx \
    sprokit/processes/core/extract_image_descriptor_process.h \
    vital/algo/extract_image_descriptor.cxx \
    vital/algo/extract_image_descriptor.h \
    --branch=dev/image_desc_proc \
    --base=master \
    -m "add process/algo: image_desc_proc"

git merge dev/image_desc_proc

git co -b dev/hog_desc_arrow



python ~/misc/git/git_xadd.py \
    vital/algo/detected_object_set_output.h \
    --branch=dev/doc_fixes \
    -m "made param rst doc consistent"

git-xadd sprokit/processes/kwiver_type_traits.h --branch=dev/add_vital_type_image_container_set -m "fixed type trait"





FLETCH_BUILD_ERRORS(){
    __heredoc__ "
    [ 97%] Linking CXX executable ../../bin/opencv_traincascade
    //usr/lib/liblapack.so.3: undefined reference to `gotoblas`
    collect2: error: ld returned 1 exit status
    apps/traincascade/CMakeFiles/opencv_traincascade.dir/build.make:392: recipe for target 'bin/opencv_traincascade' failed

    https://github.com/opencv/opencv/issues/7970

    problem may be multiple cblas.h

    locate cblas.h

    Workaround is to disable lapack
    
    OPENCV_ENABLE_LAPACK=False, there should be a better solution though
    "


    # VIAME CMAKE HAD ERROR WHEN CUDA WAS IN LOCAL DIRECTORY
    # FOUND CUDA_rt_LIBRARY in the wrong place.
    # Found /usr/lib/x86_64-linux-gnu/librt.so isntead of
    # ~/.local/cuda/lib64/libcudart.so


[  2%] Building NVCC (Device) object src/caffe/CMakeFiles/cuda_compile.dir/layers/cuda_compile_generated_relu_layer.cu.o
nvcc warning : The 'compute_20', 'sm_20', and 'sm_21' architectures are deprecated, and may be removed in a future release (Use -Wno-deprecated-gpu-targets to suppress warning).
nvcc warning : The 'compute_20', 'sm_20', and 'sm_21' architectures are deprecated, and may be removed in a future release (Use -Wno-deprecated-gpu-targets to suppress warning).
/home/joncrall/code/fletch/build-py3.5/build/src/Caffe/include/caffe/util/cudnn.hpp(112): error: too few arguments in function call

1 error detected in the compilation of "/tmp/tmpxft_00000524_00000000-5_relu_layer.cpp4.ii".
CMake Error at cuda_compile_generated_relu_layer.cu.o.cmake:266 (message):
  Error generating file
  /home/joncrall/code/fletch/build-py3.5/build/src/Caffe-build/src/caffe/CMakeFiles/cuda_compile.dir/layers/./cuda_compile_generated_relu_layer.cu.o


src/caffe/CMakeFiles/caffe.dir/build.make:483: recipe for target 'src/caffe/CMakeFiles/cuda_compile.dir/layers/cuda_compile_generated_relu_layer.cu.o' failed
make[2]: *** [src/caffe/CMakeFiles/cuda_compile.dir/layers/cuda_compile_generated_relu_layer.cu.o] Error 1
CMakeFiles/Makefile2:272: recipe for target 'src/caffe/CMakeFiles/caffe.dir/all' failed
make[1]: *** [src/caffe/CMakeFiles/caffe.dir/all] Error 2
Makefile:127: recipe for target 'all' failed
make: *** [all] Error 2



}
