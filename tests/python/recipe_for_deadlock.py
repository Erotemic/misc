#!/usr/bin/env python3
# coding:utf8
"""
References:
    https://pybay.com/site_media/slides/raymond2017-keynote/combo.html
"""
# import sys
import multiprocessing
# import subprocess
from concurrent.futures import ThreadPoolExecutor


def run(arg):
    # print('Start')
    print("starting %s" % arg)
    p = multiprocessing.Process(target=print, args=("running", arg))
    # p = multiprocessing.Process(target=print, args=("running",))
    p.start()
    p.join()
    # print('Finish')
    print("finished %s" % arg)


def recipie1():
    n = 16
    tests = range(n)
    with ThreadPoolExecutor(n) as pool:
        for r in pool.map(run, tests):
            pass


def run_popen(arg):
    # print('Start')
    print("starting %s" % arg)
    import ubelt as ub

    # Blocking variant
    info = ub.cmd('python -c "import sys; print(sys.argv[1])" "{}"'.format(arg), verbose=1)

    # Non blocking
    info = ub.cmd('python -c "import sys; print(sys.argv[1])" "{}"'.format(arg), verbose=1, detach=True)
    proc = info['proc']
    proc.communicate()

    print("finished %s" % arg)


def recipie2():
    n = 16
    tests = range(n)
    import ubelt as ub
    with ub.JobPool(mode='thread', max_workers=10) as pool:
        for arg in tests:
            pool.submit(run_popen, arg)

        for f in pool.as_completed():
            f.result()


if __name__ == "__main__":
    """
    python ~/misc/tests/python/recipe_for_deadlock.py
    """
    recipie2()
