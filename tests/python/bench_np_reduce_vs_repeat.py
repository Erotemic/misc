import numpy as np


def simple_bench():
    """
    a = np.random.rand(10000)
    b = np.random.rand(10000)
    c = np.random.rand(10000)
    d = np.random.rand(10000)

    arrs = [a, b, c, d]

    ret1 = a * b * c * d
    ret2 = np.multiply.reduce([a, b, c, d])

    %timeit np.multiply.reduce([a, b, c, d])
    %timeit a * b * c * d
    """


def benchmark_repeat_vs_reduce_mul():
    import ubelt as ub
    import pandas as pd
    import timerit

    def method_repeat(arrs):
        """
        helper code:
            arr_names = ['a{:02d}'.format(idx) for idx in range(1, 32 + 1)]
            lhs = ', '.join(arr_names)
            rhs = ' * '.join(arr_names)
            print(f'{lhs} = arrs')
            print(f'ret = {rhs}')
        """
        # Hard coded pure python syntax for multiplying
        if len(arrs) == 4:
            a01, a02, a03, a04 = arrs
            ret = a01 * a02 * a03 * a04
        elif len(arrs) == 8:
            a01, a02, a03, a04, a05, a06, a07, a08 = arrs
            ret = a01 * a02 * a03 * a04 * a05 * a06 * a07 * a08
        elif len(arrs) == 32:
            a01, a02, a03, a04, a05, a06, a07, a08, a09, a10, a11, a12, a13, a14, a15, a16, a17, a18, a19, a20, a21, a22, a23, a24, a25, a26, a27, a28, a29, a30, a31, a32 = arrs
            ret = a01 * a02 * a03 * a04 * a05 * a06 * a07 * a08 * a09 * a10 * a11 * a12 * a13 * a14 * a15 * a16 * a17 * a18 * a19 * a20 * a21 * a22 * a23 * a24 * a25 * a26 * a27 * a28 * a29 * a30 * a31 * a32
        return ret

    def method_reduce(arrs):
        ret = np.multiply.reduce(arrs)
        return ret

    def method_stack(arrs):
        stacked = np.stack(arrs)
        ret = stacked.prod(axis=0)
        return ret

    method_lut = locals()  # can populate this some other way

    ti = timerit.Timerit(10000, bestof=10, verbose=2)

    basis = {
        'method': ['method_repeat', 'method_reduce', 'method_stack'],
        'arr_size': [10, 100, 1000, 10000],
        'num_arrs': [4, 8, 32],
    }
    xlabel = 'arr_size'
    kw_labels = []
    group_labels = {
        'style': ['num_arrs'],
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

        arr_size = params['arr_size']
        num_arrs = params['num_arrs']

        arrs = []
        for _ in range(num_arrs):
            arr = np.random.rand(arr_size)
            arrs.append(arr)
        kwargs['arrs'] = arrs
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
        ax.set_ylabel('Array Size')
