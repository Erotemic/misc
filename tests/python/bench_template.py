

def benchmark_template():
    import ubelt as ub
    import pandas as pd
    import timerit

    def method1(x, y, z):
        ret = []
        for i in range((x + y) * z):
            ret.append(i)
        return ret

    def method2(x, y, z):
        ret = [i for i in range((x + y) * z)]
        return ret

    method_lut = locals()  # can populate this some other way

    ti = timerit.Timerit(100, bestof=10, verbose=2)

    basis = {
        'method': ['method1', 'method2'],
        'x': list(range(7)),
        'y': [0, 100],
        'z': [2, 3]
        # 'param_name': [param values],
    }
    xlabel = 'x'
    kw_labels = ['x', 'y', 'z']
    group_labels = {
        'style': ['y'],
        'size': ['z'],
    }
    group_labels['hue'] = list(
        (ub.oset(basis) - {xlabel}) - set.union(*map(set, group_labels.values())))
    grid_iter = list(ub.named_product(basis))

    # For each variation of your experiment, create a row.
    rows = []
    for params in grid_iter:
        group_keys = {}
        for gname, labels in group_labels.items():
            group_keys[gname + '_key'] = ub.repr2(
                ub.dict_isect(params, labels), compact=1, si=1)
        key = ub.repr2(params, compact=1, si=1)
        kwargs = ub.dict_isect(params.copy(),  kw_labels)
        method = method_lut[params['method']]
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
            **group_keys,
            **params,
        }
        rows.append(row)

    # The rows define a long-form pandas data array.
    # Data in long-form makes it very easy to use seaborn.
    data = pd.DataFrame(rows)
    data = data.sort_values('min')
    print(data)

    plot = True
    if plot:
        # import seaborn as sns
        # kwplot autosns works well for IPython and script execution.
        # not sure about notebooks.
        import kwplot
        sns = kwplot.autosns()

        plotkw = {}
        for gname, labels in group_labels.items():
            if labels:
                plotkw[gname] = gname + '_key'

        # Your variables may change
        ax = kwplot.figure(fnum=1, doclf=True).gca()
        sns.lineplot(data=data, x=xlabel, y='min', marker='o', ax=ax, **plotkw)
        ax.set_title('Benchmark')
        ax.set_xlabel('A better x-variable description')
        ax.set_ylabel('A better y-variable description')
