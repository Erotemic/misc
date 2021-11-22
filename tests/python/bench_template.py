

def benchmark_template():
    import ubelt as ub
    import pandas as pd
    import timerit

    def method1(x):
        ret = []
        for i in range(x):
            ret.append(i)
        return ret

    def method2(x):
        ret = [i for i in range(x)]
        return ret

    method_lut = locals()  # can populate this some other way

    ti = timerit.Timerit(100, bestof=10, verbose=2)

    basis = {
        'method': ['method1', 'method2'],
        'x': list(range(7)),
        # 'param_name': [param values],
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
        ax.set_title('Benchmark')
        ax.set_xlabel('A better x-variable description')
        ax.set_ylabel('A better y-variable description')
