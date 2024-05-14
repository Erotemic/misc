"""
Demo the relationship between different ways to define a context manager
"""
import rich
from contextlib import contextmanager


class ClassContext:
    def __init__(self, *args, **kwargs):
        rich.print('[green]ClassContextManager.__init__')
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        rich.print('[green]ClassContextManager.__enter__')
        return 'class-as-enter-obj'

    def __exit__(self, ex_type, ex_value, ex_traceback):
        rich.print('[green]ClassContextManager.__exit__')


@contextmanager
def func_context():
    # In a function there is no analog of __init__
    # This part corresponds to __enter__
    rich.print('[green]func_context: Before yield')
    try:
        # The yield value corresponds to the return of __enter__
        yield 'func-as-enter-obj'
    finally:
        # This part corresponds to __exit__
        rich.print('[green]func_context: After yield')


def main():
    print('\n\n')
    rich.print('[white] --- Test Class ---')
    rich.print('1. About to make context ')
    context = ClassContext()
    rich.print('2. About to enter context')
    with context as enter_obj:
        rich.print(f'2. Inside Context enter_obj={enter_obj}')
    rich.print('3. Outside Context')

    print('\n\n')
    rich.print('[white] --- Test Func ---')
    rich.print('1. About to make context ')
    context = func_context()
    rich.print('2. About to enter context')
    with context as enter_obj:
        rich.print(f'2. Inside Context enter_obj={enter_obj}')
    rich.print('3. Outside Context')

    print('\n\n')
    rich.print('[white] --- Test Class With Error ---')
    rich.print('1. About to make context ')
    context = ClassContext()
    rich.print('2. About to enter context')
    try:
        with context as enter_obj:
            rich.print(f'2. Inside Context enter_obj={enter_obj}')
            raise Exception('Error happened')
    except Exception:
        print('Caught the error')
    else:
        raise AssertionError('Should have caught an error')
    rich.print('3. Outside Context')

    print('\n\n')
    rich.print('[white] --- Test Func With Error ---')
    rich.print('1. About to make context ')
    context = func_context()
    rich.print('2. About to enter context')
    try:
        with context as enter_obj:
            rich.print(f'2. Inside Context enter_obj={enter_obj}')
            raise Exception('Error happened')
    except Exception:
        print('Caught the error')
    else:
        raise AssertionError('Should have caught an error')
    rich.print('3. Outside Context')

if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/context_manager.py
    """
    main()
