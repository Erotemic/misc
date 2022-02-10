

def benchmark_template():
    import ubelt as ub
    import pandas as pd
    import timerit

    from functools import reduce
    import operator as op
    import itertools as it

    def method_mul_raw(n):
        return eval('lambda v: ' + ' * '.join(['v'] * n))

    def method_mul_for(v, n):
        ret = v
        for _ in range(1, n):
            ret = ret * v
        return ret

    def method_mul_reduce(v, n):
        return reduce(op.mul, it.repeat(v, n))

    def method_pow(v, n):
        return v ** n

    method_lut = locals()  # can populate this some other way

    ti = timerit.Timerit(500000, bestof=200, verbose=2)

    basis = {
        'method': ['method_mul_raw', 'method_mul_reduce', 'method_pow'],
        'n': list(range(1, 20)),
        'v': ['random'],
        # 'param_name': [param values],
    }
    xlabel = 'n'
    kw_labels = ['v', 'n']
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
        method = method_lut[params['method']]
        # Timerit will run some user-specified number of loops.
        # and compute time stats with similar methodology to timeit

        if params['method'] == 'method_mul_raw':
            method = method(kwargs.pop('n'))

        for timer in ti.reset(key):
            # Put any setup logic you dont want to time here.
            # ...
            import random
            if kwargs['v'] == 'random':
                kwargs['v'] = random.randint(1, 31000) if random.random() > 0.5 else random.random()
            with timer:
                # Put the logic you want to time here
                method(**kwargs)
        for time in map(min, ub.chunks(ti.times, ti.bestof)):
            row = {
                # 'mean': ti.mean(),
                'time': time,
                'key': key,
                **group_keys,
                **params,
            }
            rows.append(row)

    # The rows define a long-form pandas data array.
    # Data in long-form makes it very easy to use seaborn.
    data = pd.DataFrame(rows)
    # data = data.sort_values('time')
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
        sns.lineplot(data=data, x=xlabel, y='time', marker='o', ax=ax, **plotkw)
        ax.set_title('Benchmark')
        ax.set_xlabel('N')
        ax.set_ylabel('Time')
        ax.set_yscale('log')
