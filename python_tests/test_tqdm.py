import ubelt as ub
import tqdm
from time import sleep


def test1():
    for i in tqdm.trange(10, desc='1st loop'):
        for j in tqdm.trange(5, desc='2nd loop', leave=False):
            for k in tqdm.trange(100, desc='3nd loop'):
                sleep(0.01)

    d = {'1': 2, '3': 4, '5': 7}
    for key, val in tqdm.tqdm(d.items(), desc='foobar'):
        for i in tqdm.trange(1000, desc='inner loop'):
            sleep(0.01)


def test_partial_nest1():
    # https://github.com/tqdm/tqdm/issues/312
    from tqdm import trange
    from time import sleep
    import sys

    long_msg = ub.codeblock(
        '''
        HELLO WORLD
              -jon
        ''')

    prog = trange(10, desc='1st loop', leave=True, position=1, mininterval=1)

    for i in prog:
        # prog.set_description(long_msg)
        for l in long_msg.split('\n'):
            tqdm.tqdm.write(l, file=sys.stdout)
        # tqdm.tqdm.write(long_msg, file=sys.stdout)
        for j in trange(100, desc='2nd loop', leave=True, position=2, mininterval=.2):
            sleep(0.01)
        for k in trange(100, desc='3nd loop', leave=True, position=3, mininterval=.2):
            sleep(0.01)
    print('\n\n\n\n')


def test_partial_nest2():

    p1 = tqdm.tqdm(total=100, desc='loop 1', leave=True, position=1)

    for _ in range(p1.total):
        p2 = tqdm.tqdm(total=1000, desc='loop 2', leave=True, position=2)
        for _ in range(p2.total):
            sleep(0.001)
            p2.update(1)
        p2.close()

        p3 = tqdm.tqdm(total=1000, desc='loop 3', leave=True, position=3)
        for _ in range(p3.total):
            sleep(0.001)
            p3.update(1)
        p3.close()

        p1.update(1)


if __name__ == '__main__':
    r"""
    CommandLine:
        export PYTHONPATH=$PYTHONPATH:/home/joncrall/misc/python_tests
        python ~/misc/python_tests/test_tqdm.py test_partial_nest1
        python ~/misc/python_tests/test_tqdm.py test_partial_nest2
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
    # test_partial_nest1()
    # test_write()
