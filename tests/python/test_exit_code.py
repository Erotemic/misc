r"""
Tests python exit code in various circumstances


Script Commands:
    python ~/misc/tests/python/test_exit_code.py --exit-mode=sys  --exit-val=0 ; \
    echo $? ; \
    python ~/misc/tests/python/test_exit_code.py --exit-mode=sys  --exit-val=1 ; \
    echo $? ; \
    python ~/misc/tests/python/test_exit_code.py --exit-mode=sys  --exit-val=None ; \
    echo $? ; \
    python ~/misc/tests/python/test_exit_code.py --exit-mode=sys  --exit-val=err ; \
    echo $?

    python ~/misc/tests/python/test_exit_code.py --exit-mode=None --exit-val=0 ; \
    echo $? ; \
    python ~/misc/tests/python/test_exit_code.py --exit-mode=None --exit-val=1 ; \
    echo $? ; \
    python ~/misc/tests/python/test_exit_code.py --exit-mode=None --exit-val=None ; \
    echo $? ; \
    python ~/misc/tests/python/test_exit_code.py --exit-mode=None --exit-val=err ; \
    echo $?

Results:
    (py38) joncrall@Ooo:~/misc/tests/python$     python ~/misc/tests/python/test_exit_code.py --exit-mode=sys  --exit-val=0 ; \
    >     echo $? ; \
    >     python ~/misc/tests/python/test_exit_code.py --exit-mode=sys  --exit-val=1 ; \
    >     echo $? ; \
    >     python ~/misc/tests/python/test_exit_code.py --exit-mode=sys  --exit-val=None ; \
    >     echo $? ; \
    >     python ~/misc/tests/python/test_exit_code.py --exit-mode=sys  --exit-val=err ; \
    >     echo $?
    0
    1
    0
    Traceback (most recent call last):
      File "/home/joncrall/misc/tests/python/test_exit_code.py", line 46, in <module>
        sys.exit(main())
      File "/home/joncrall/misc/tests/python/test_exit_code.py", line 36, in main
        raise Exception
    Exception
    1
    (py38) joncrall@Ooo:~/misc/tests/python$
    (py38) joncrall@Ooo:~/misc/tests/python$     python ~/misc/tests/python/test_exit_code.py --exit-mode=None --exit-val=0 ; \
    >     echo $? ; \
    >     python ~/misc/tests/python/test_exit_code.py --exit-mode=None --exit-val=1 ; \
    >     echo $? ; \
    >     python ~/misc/tests/python/test_exit_code.py --exit-mode=None --exit-val=None ; \
    >     echo $? ; \
    >     python ~/misc/tests/python/test_exit_code.py --exit-mode=None --exit-val=err ; \
    >     echo $?
    0
    0
    0
"""
import sys
import ubelt as ub


def main():
    val = ub.argval('--exit-val', default=None)

    if val == 'None':
        val = None

    if val == 'err':
        raise Exception

    if val is not None:
        val = int(val)
    return val


if __name__ == '__main__':
    mode = ub.argval('--exit-mode', default='sys')
    if mode == 'sys':
        sys.exit(main())
    else:
        main()
