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

"
