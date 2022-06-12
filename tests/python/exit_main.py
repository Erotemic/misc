#!/bin/env python
import sys
import ubelt as ub


def main():
    if ub.argflag('--fail'):
        raise Exception

if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/exit_main.py --fail
        RET_VAL=$?
        echo "RET_VAL=$RET_VAL"
        python ~/misc/tests/python/exit_main.py
        RET_VAL=$?
        echo "RET_VAL=$RET_VAL"
    """
    sys.exit(main())
