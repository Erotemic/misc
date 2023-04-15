

def benchmark_unpack():
    """
    What is faster unpacking items with slice syntax or tuple-unpacking

    Slice unpacking seems to be a tad faster.
    """
    import ubelt as ub
    import random
    import pandas as pd
    import timerit
    import string
    import itertools as it

    def tuple_unpack(items):
        *prefix, key = items
        return prefix, key

    def slice_unpack(items):
        prefix, key = items[:-1], items[-1]
        return prefix, key

    def islice_unpack(items):
        last_idx = len(items) - 1
        prefix = list(it.islice(items, 0, last_idx))
        key = items[last_idx]
        return prefix, key

    method_lut = locals()  # can populate this some other way

    ti = timerit.Timerit(5000, bestof=3, verbose=2)

    basis = {
        'method': ['tuple_unpack', 'slice_unpack', 'islice_unpack'],
        'size': list(range(1, 64 + 1)),
        'type': ['string', 'float'],
    }
    xlabel = 'size'
    kw_labels = []
    group_labels = {
        'style': ['type'],
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
        size = params['size']
        method = method_lut[params['method']]
        # Timerit will run some user-specified number of loops.
        # and compute time stats with similar methodology to timeit
        for timer in ti.reset(key):
            if params['type'] == 'string':
                items = [''.join(random.choices(string.printable, k=5)) for _ in range(size)]
            elif params['type'] == 'float':
                items = [random.random() for _ in range(size)]
            else:
                raise NotImplementedError(params['type'])
            with timer:
                method(items)
        for time in ti.times:
            row = {
                'time': time,
                'key': key,
                **group_keys,
                **params,
            }
            rows.append(row)

    # The rows define a long-form pandas data array.
    # Data in long-form makes it very easy to use seaborn.
    data = pd.DataFrame(rows)
    data = data.sort_values('time')
    summary_rows = []
    for method, group in data.groupby('method'):
        row = {}
        row['method'] = method
        row['mean'] = group['time'].mean()
        row['std'] = group['time'].std()
        row['min'] = group['time'].min()
        row['max'] = group['time'].max()
        summary_rows.append(row)
    print(pd.DataFrame(summary_rows).sort_values('mean'))

    plot = True
    if plot:
        # import seaborn as sns
        # kwplot autosns works well for IPython and script execution.
        # not sure about notebooks.
        import kwplot
        sns = kwplot.autosns()
        plt = kwplot.autoplt()
        plt.ion()

        plotkw = {}
        for gname, labels in group_labels.items():
            if labels:
                plotkw[gname] = gname + '_key'

        # Your variables may change
        ax = kwplot.figure(fnum=1, doclf=True).gca()
        sns.lineplot(data=data, x=xlabel, y='time', marker='o', ax=ax, **plotkw)
        ax.set_title('Benchmark')
        ax.set_xlabel('Execution time')
        ax.set_ylabel('Size of slices')
        plt.show()

if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/bench_unpack.py
    """
    benchmark_unpack()
