

def benchmark_template():
    import ubelt as ub
    import pandas as pd
    import timerit
    import random
    import re

    def method_finditer(string, sub):
        return [m.span()[0] for m in re.finditer(sub, string)]

    def method_forloop(string, sub):
        found = []
        remain = string
        sublen = len(sub)
        offset = 0
        try:
            while remain:
                remain = string[offset:]
                remain_start_idx = remain.index(sub)
                full_idx = offset + remain_start_idx
                offset = full_idx + sublen
                found.append(full_idx)
        except ValueError:
            pass
        return found

    def method_awky(string, sub):
        s = string
        res = []
        ind = 0
        while (ind := s.find(sub, ind)) != -1:
            res.append(ind)
            ind += len(sub)
        return res

    method_lut = locals()  # can populate this some other way

    ti = timerit.Timerit(100, bestof=10, verbose=2)

    def generate_data(size, subsize=None):
        assert size > 0
        if subsize is None:
            a, b = sorted(random.randint(0, size) for _ in range(2))
        else:
            size = max(size, subsize)
            a = random.randint(0, size - subsize)
            b = a  + subsize
        string = ''.join(random.choices('01', k=size))
        sub = string[a:b]
        data = {'string': string, 'sub': sub}
        return data

    """
    """

    if __debug__:
        sub = '01'
        string = '0101010100000111'
        found1 = method_finditer(string, sub)
        found2 = method_forloop(string, sub)
        print('found1 = {!r}'.format(found1))
        print('found2 = {!r}'.format(found2))
        size = 10
        subsize = 2
        func_kwargs = generate_data(size=10, subsize=2)
        print('func_kwargs = {!r}'.format(func_kwargs))
        string = func_kwargs['string']
        sub = func_kwargs['sub']
        found1 = method_finditer(string, sub)
        found2 = method_forloop(string, sub)
        print('found1 = {!r}'.format(found1))
        print('found2 = {!r}'.format(found2))
        assert found1 == found2

    basis = {
        'method': ['method_finditer', 'method_forloop', 'method_awky'],
        'size': [1, 10, 100, 200, 200, 500, 1000, 2000, 10000],
        'subsize': [2, 64],
    }
    xlabel = 'size'
    data_kwkeys = ub.compatible(basis, generate_data)
    func_kwkeys = ub.compatible(basis, method_lut[basis['method'][0]])
    group_labels = {
        'style': ['subsize'],
    }
    hue_labels = ub.oset(basis) - {xlabel}
    if group_labels:
        hue_labels = hue_labels - set.union(*map(set, group_labels.values()))
    group_labels['hue'] = list(hue_labels)
    grid_iter = list(ub.named_product(basis))

    # For each variation of your experiment, create a row.
    rows = []
    for params in grid_iter:
        group_keys = {}
        for gname, labels in group_labels.items():
            group_keys[gname + '_key'] = ub.repr2(
                ub.dict_isect(params, labels), compact=1, si=1)
        key = ub.repr2(params, compact=1, si=1)

        data_kwargs = ub.dict_isect(params.copy(),  data_kwkeys)
        func_kwargs = generate_data(**data_kwargs)
        method = method_lut[params['method']]
        # Timerit will run some user-specified number of loops.
        # and compute time stats with similar methodology to timeit
        for timer in ti.reset(key):
            with timer:
                # MAIN LOGIC
                method(**func_kwargs)
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
        ax.set_xlabel('Substring size')
        ax.set_ylabel('Minimum execution time')
        ax.set_xscale('log')
        ax.set_yscale('log')
