

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

    # Change params here to modify number of trials
    ti = timerit.Timerit(100, bestof=10, verbose=1)

    # if True, record every trail run and show variance in seaborn
    # if False, use the standard timerit min/mean measures
    RECORD_ALL = True

    # These are the parameters that we benchmark over
    basis = {
        'method': ['method1', 'method2'],
        'x': list(range(7)),
        'y': [0, 100],
        'z': [2, 3]
        # 'param_name': [param values],
    }
    xlabel = 'x'
    # Set these to param labels that directly transfer to method kwargs
    kw_labels = ['x', 'y', 'z']
    # Set these to empty lists if they are not used
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
        # Make any modifications you need to compute input kwargs for each
        # method here.
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

        if RECORD_ALL:
            # Seaborn will show the variance if this is enabled, otherwise
            # use the robust timerit mean / min times
            chunk_iter = ub.chunks(ti.times, ti.bestof)
            times = list(map(min, chunk_iter))  # TODO: timerit method for this
            for time in times:
                row = {
                    # 'mean': ti.mean(),
                    'time': time,
                    'key': key,
                    **group_keys,
                    **params,
                }
                rows.append(row)
        else:
            row = {
                'mean': ti.mean(),
                'min': ti.min(),
                'key': key,
                **group_keys,
                **params,
            }
            rows.append(row)

    time_key = 'time' if RECORD_ALL else 'min'

    # The rows define a long-form pandas data array.
    # Data in long-form makes it very easy to use seaborn.
    data = pd.DataFrame(rows)
    data = data.sort_values(time_key)
    print(data)

    if RECORD_ALL:
        # Show the min / mean if we record all
        min_times = data.groupby('key').min().rename({'time': 'min'}, axis=1)
        mean_times = data.groupby('key')[['time']].mean().rename({'time': 'mean'}, axis=1)
        stats_data = pd.concat([min_times, mean_times], axis=1)
        stats_data = stats_data.sort_values('min')
        print('Statistics:')
        print(stats_data)

    plot = True
    if plot:
        # import seaborn as sns
        # kwplot autosns works well for IPython and script execution.
        # not sure about notebooks.
        import kwplot
        sns = kwplot.autosns()
        plt = kwplot.autoplt()

        plotkw = {}
        for gname, labels in group_labels.items():
            if labels:
                plotkw[gname] = gname + '_key'

        # Your variables may change
        ax = kwplot.figure(fnum=1, doclf=True).gca()
        sns.lineplot(data=data, x=xlabel, y=time_key, marker='o', ax=ax, **plotkw)
        ax.set_title('Benchmark Name')
        ax.set_xlabel('Size (todo: A better x-variable description)')
        ax.set_ylabel('Time (todo: A better y-variable description)')
        # ax.set_xscale('log')
        # ax.set_yscale('log')

        try:
            __IPYTHON__
        except NameError:
            plt.show()


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/bench_template.py
    """
    benchmark_template()
