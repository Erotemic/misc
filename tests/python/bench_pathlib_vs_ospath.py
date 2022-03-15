

def benchmark_pathlib_vs_fspath():
    import ubelt as ub
    import pathlib
    import pandas as pd
    import random
    import timerit
    import os

    def method_pathlib(inputs):
        p = pathlib.Path(*inputs)

    def method_ospath(inputs):
        p = os.path.join(*inputs)

    method_lut = locals()  # can populate this some other way

    ti = timerit.Timerit(10000, bestof=10, verbose=2)

    basis = {
        'method': ['method_pathlib', 'method_ospath'],
        'num_parts': [2, 4, 8, 12, 16],
    }
    xlabel = 'num_parts'
    kw_labels = []
    group_labels = {
        'style': [],
        'size': [],
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

        n = params['num_parts']
        inputs = [chr(random.randint(97, 120)) for _ in range(n)]
        kwargs['inputs'] = inputs
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
        ax.set_xlabel('Time')
        ax.set_ylabel('Number of parts')
