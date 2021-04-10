cd ~/misc/tests/python/pkg_req_test/

pip install -e ~/misc/tests/python/pkg_req_test/dummy_pkg2
pip install -e ~/misc/tests/python/pkg_req_test/dummy_pkg1


dummy_pkg1

python -c "import dummy_pkg2"
python -c "import dummy_pkg1"



__doc__="
#### opencv-requirements problem 

I'm having an issue with my requirements.txt

My library depends on the `cv2` module, and there are two main ways of
obtaining this with pip. Either `opencv-python` or `opencv-python-headless`.

The issue is that `opencv-python` contains libraries that can conflict with
`pyqt5`, which I often see when I'm using `matplotlib`.  Using
`opencv-python-headless` works around this issue.


The problem is that pip has gotten too smart for its own good. 
It throws some requirements not satisfied error, but I can't figure out how
to reproduce that reliably.



I got the error to happen again, but again, I don't know what caused it. The traceback is:
"

#ERROR ex = DistributionNotFound(Requirement.parse('opencv-python'), {'kwimage'})
#Traceback (most recent call last):
#  File "/home/joncrall/.pyenv/versions/3.8.5/envs/py385/bin/kwcoco", line 33, in <module>
#    sys.exit(load_entry_point('kwcoco', 'console_scripts', 'kwcoco')())
#  File "/home/joncrall/code/kwcoco/kwcoco/cli/__main__.py", line 112, in main
#    ret = main(cmdline=False, **kw)
#  File "/home/joncrall/code/kwcoco/kwcoco/cli/coco_validate.py", line 81, in main
#    result = dset.validate(**config_)
#  File "/home/joncrall/code/kwcoco/kwcoco/coco_dataset.py", line 2670, in validate
#    from kwcoco.coco_schema import COCO_SCHEMA
#  File "/home/joncrall/code/kwcoco/kwcoco/coco_schema.py", line 42, in <module>
#    from kwcoco.util.jsonschema_elements import SchemaElements
#  File "/home/joncrall/code/kwcoco/kwcoco/util/__init__.py", line 6, in <module>
#    from kwcoco.util import util_sklearn
#  File "/home/joncrall/code/kwcoco/kwcoco/util/util_sklearn.py", line 6, in <module>
#    from sklearn.utils.validation import check_array
#  File "/home/joncrall/.pyenv/versions/3.8.5/envs/py385/lib/python3.8/site-packages/sklearn/__init__.py", line 82, in <module>
#    from .base import clone
#  File "/home/joncrall/.pyenv/versions/3.8.5/envs/py385/lib/python3.8/site-packages/sklearn/base.py", line 17, in <module>
#    from .utils import _IS_32BIT
#  File "/home/joncrall/.pyenv/versions/3.8.5/envs/py385/lib/python3.8/site-packages/sklearn/utils/__init__.py", line 23, in <module>
#    from .class_weight import compute_class_weight, compute_sample_weight
#  File "/home/joncrall/.pyenv/versions/3.8.5/envs/py385/lib/python3.8/site-packages/sklearn/utils/class_weight.py", line 7, in <module>
#    from .validation import _deprecate_positional_args
#  File "/home/joncrall/.pyenv/versions/3.8.5/envs/py385/lib/python3.8/site-packages/sklearn/utils/validation.py", line 26, in <module>
#    from .fixes import _object_dtype_isnan, parse_version
#  File "/home/joncrall/.pyenv/versions/3.8.5/envs/py385/lib/python3.8/site-packages/sklearn/utils/fixes.py", line 28, in <module>
#    from pkg_resources import parse_version  # type: ignore
#  File "/home/joncrall/.pyenv/versions/3.8.5/envs/py385/lib/python3.8/site-packages/pkg_resources/__init__.py", line 3262, in <module>
#    def _initialize_master_working_set():
#  File "/home/joncrall/.pyenv/versions/3.8.5/envs/py385/lib/python3.8/site-packages/pkg_resources/__init__.py", line 3245, in _call_aside
#    f(*args, **kwargs)
#  File "/home/joncrall/.pyenv/versions/3.8.5/envs/py385/lib/python3.8/site-packages/pkg_resources/__init__.py", line 3274, in _initialize_master_working_set
#    working_set = WorkingSet._build_master()
#  File "/home/joncrall/.pyenv/versions/3.8.5/envs/py385/lib/python3.8/site-packages/pkg_resources/__init__.py", line 584, in _build_master
#    ws.require(__requires__)
#  File "/home/joncrall/.pyenv/versions/3.8.5/envs/py385/lib/python3.8/site-packages/pkg_resources/__init__.py", line 901, in require
#    needed = self.resolve(parse_requirements(requirements))
#  File "/home/joncrall/.pyenv/versions/3.8.5/envs/py385/lib/python3.8/site-packages/pkg_resources/__init__.py", line 787, in resolve
#    raise DistributionNotFound(req, requirers)
#pkg_resources.DistributionNotFound: The 'opencv-python' distribution was not found and is required by kwimage

