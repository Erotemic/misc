

def benchmark_reversed_range():
    import ubelt as ub
    import pandas as pd
    import timerit
    import itertools as it

    methods = []

    def custom_reversed_range_v1(start, stop):
        final = stop - 1
        for idx in range(stop - start):
            yield final - idx

    def custom_reversed_range_v2(start, stop):
        yield from it.islice(it.count(stop - 1, step=-1), stop - start)

    @methods.append
    def reversed_builtin(x):
        start = 10
        stop = x + start
        ret = list(reversed(range(start, stop)))
        return ret

    @methods.append
    def negative_range(x):
        start = 10
        stop = x + start
        ret = list(range(stop - 1, start - 1, -1))
        return ret

    # @methods.append
    # def custom_v1(x):
    #     start = 10
    #     stop = x + start
    #     ret = list(custom_reversed_range_v1(start, stop))
    #     return ret

    # @methods.append
    # def custom_v2(x):
    #     start = 10
    #     stop = x + start
    #     ret = list(custom_reversed_range_v2(start, stop))
    #     return ret

    method_lut = {f.__name__: f for f in methods}

    results = {k: func(10) for k, func in method_lut.items()}
    print('results = {}'.format(ub.repr2(results, nl=1, align=':')))
    if not ub.allsame(results.values()):
        raise AssertionError('Failed consistency check')

    ti = timerit.Timerit(1000, bestof=10, verbose=2)

    basis = {
        'method': list(method_lut.keys()),
        'x': [2 ** i for i in range(14)],
    }
    grid_iter = ub.named_product(basis)

    # For each variation of your experiment, create a row.
    rows = []
    for params in grid_iter:
        key = ub.repr2(params, compact=1, si=1)
        kwargs = params.copy()
        method_key = kwargs.pop('method')
        method = method_lut[method_key]
        # Timerit will run some user-specified number of loops.
        # and compute time stats with similar methodology to timeit
        for timer in ti.reset(key):
            # Put any setup logic you dont want to time here.
            # ...
            with timer:
                # Put the logic you want to time here
                method(**kwargs)
        row = {
            'mean': ti.mean(),
            'min': ti.min(),
            'key': key,
            **params,
        }
        rows.append(row)

    # The rows define a long-form pandas data array.
    # Data in long-form makes it very easy to use seaborn.
    data = pd.DataFrame(rows)
    print(data)

    plot = True
    if plot:
        # import seaborn as sns
        # kwplot autosns works well for IPython and script execution.
        # not sure about notebooks.
        import kwplot
        sns = kwplot.autosns()

        # Your variables may change
        ax = kwplot.figure(fnum=1, doclf=True).gca()
        sns.lineplot(data=data, x='x', y='min', hue='method', marker='o', ax=ax)
        # ax.set_xscale('log')
        ax.set_title('Benchmark Reveral Methods ')
        ax.set_xlabel('A better x-variable description')
        ax.set_ylabel('A better y-variable description')
