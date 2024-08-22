def main():
    import numpy as np
    import timerit

    class MyClass:
        ...

    from numpy import ndarray
    instance = MyClass()

    types_to_check = [
        int,
        float,
        str,
        list,
        set,
        ndarray,
        MyClass,
    ]
    if 1:
        code_lines = []
        for t in types_to_check:
            code_lines.append(f'elif isinstance(instance, {t.__name__}):')
            code_lines.append(f'    value = "{t.__name__}"')
        code_lines.append('else:')
        code_lines.append('    value = "else"')
        text = '\n'.join(code_lines)[2:]
        print(text)

        code_lines = ['match instance:']
        for t in types_to_check:
            code_lines.append(f'    case {t.__name__}():')
            code_lines.append(f'        value = "{t.__name__}"')
        code_lines.append('    case _:')
        code_lines.append('        value = "_"')
        text = '\n'.join(code_lines)
        print(text)

    ti = timerit.Timerit(100, bestof=10, verbose=1)
    for timer in ti.reset('single correct isinstance'):
        with timer:
            isinstance(instance, MyClass)
    for timer in ti.reset('single incorrect isinstance'):
        with timer:
            isinstance(instance, str)
    ti.print()

    ti = timerit.Timerit(10000, bestof=10, verbose=3)
    for timer in ti.reset('cascaded if statements'):
        with timer:
            if isinstance(instance, int):
                value = "int"
            elif isinstance(instance, float):
                value = "float"
            elif isinstance(instance, str):
                value = "str"
            elif isinstance(instance, list):
                value = "list"
            elif isinstance(instance, set):
                value = "set"
            elif isinstance(instance, ndarray):
                value = "ndarray"
            elif isinstance(instance, MyClass):
                value = "MyClass"
            else:
                value = "else"
    del value
    for timer in ti.reset('match case statement'):
        with timer:
            match instance:
                case int():
                    value = "int"
                case float():
                    value = "float"
                case str():
                    value = "str"
                case list():
                    value = "list"
                case set():
                    value = "set"
                case ndarray():
                    value = "ndarray"
                case MyClass():
                    value = "MyClass"
                case _:
                    value = "_"
    del value
    import ubelt as ub
    print(f'ti.rankings = {ub.urepr(ti.rankings, nl=2)}')


def simple_statements():
    import timeit
    """
    %timeit isinstance(instance, MyClass)
    %timeit isinstance(instance, str)
    """
    print(timeit.timeit('isinstance(instance, MyClass)', globals=locals()))
    print(timeit.timeit('isinstance(instance, str)', globals=locals()))
    timeit.main(['--setup', 'instance = 1', 'isinstance(instance, str)'])
    timeit.main(['--setup', 'instance = 1', 'isinstance(instance, int)'])

    import timerit
    ti = timerit.Timerit(10000000, bestof=5, verbose=2)
    instance = 1
    for timer in ti.reset('single correct isinstance'):
        with timer:
            isinstance(instance, int)
    for timer in ti.reset('single incorrect isinstance'):
        with timer:
            isinstance(instance, str)
