def main():
    args = [1, 2, 3]

    func_types = {}

    funcs = func_types['wrong_way_lambda'] = []
    for a in args:
        funcs.append(lambda: a)

    funcs = func_types['wrong_way_comprehension_lambda'] = [
        lambda: a
        for a in args
    ]

    funcs = func_types['wrong_way_def'] = []
    for a in args:
        def _():
            return a
        funcs.append(_)

    funcs = func_types['right_way'] = []
    def mkfunc(a):
        def _():
            return a
        return _

    for a in args:
        _ = mkfunc(a)
        funcs.append(_)

    funcs = func_types['right_way_comprehension'] = [
        mkfunc(a)
        for a in args
    ]

    import rich
    import ubelt as ub

    for key, funcs in func_types.items():
        rich.print('----')
        rich.print(f'key={key}')
        rich.print('funcs = {}'.format(ub.urepr(funcs, nl=1)))
        results = [f() for f in funcs]
        rich.print(f'results={results}')


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/priority.py
    """
    main()
