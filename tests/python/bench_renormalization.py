

def run_benchmark_renormalization():
    """
    See if we can renormalize probabilities after update with a faster method
    that maintains memory a bit better

    Example:
        >>> import sys, ubelt
        >>> sys.path.append(ubelt.expandpath('~/misc/tests/python'))
        >>> from bench_renormalization import *  # NOQA
        >>> run_benchmark_renormalization()
    """
    import ubelt as ub
    import xdev
    import pathlib
    import timerit

    fpath = pathlib.Path('~/misc/tests/python/renormalize_cython.pyx').expanduser()
    renormalize_cython = xdev.import_module_from_pyx(fpath, annotate=True,
                                                     verbose=3, recompile=True)

    xdev.profile_now(renormalize_demo_v1)(1000, 100)
    xdev.profile_now(renormalize_demo_v2)(1000, 100)
    xdev.profile_now(renormalize_demo_v3)(1000, 100)
    xdev.profile_now(renormalize_demo_v4)(1000, 100)

    func_list = [
        # renormalize_demo_v1,
        renormalize_demo_v2,
        # renormalize_demo_v3,
        # renormalize_demo_v4,
        renormalize_cython.renormalize_demo_cython_v1,
        renormalize_cython.renormalize_demo_cython_v2,
        renormalize_cython.renormalize_demo_cython_v3,
    ]
    methods = {f.__name__: f for f in func_list}
    for key, method in methods.items():
        with timerit.Timer(label=key, verbose=0) as t:
            method(1000, 100)
        print(f'{key:<30} {t.toc():0.6f}')

    arg_basis = {
        'T': [10, 20,  30,  50],
        'D': [10, 50, 100, 300],
    }
    args_grid = []
    for argkw in list(ub.named_product(arg_basis)):
        if argkw['T'] <= argkw['D']:
            arg_basis['size'] = argkw['T'] * argkw['D']
            args_grid.append(argkw)

    ti = timerit.Timerit(100, bestof=10, verbose=2)

    measures = []

    for method_name, method in methods.items():
        for argkw in args_grid:
            row = ub.dict_union({'method': method_name}, argkw)
            key = ub.repr2(row, compact=1)
            argkey = ub.repr2(argkw, compact=1)

            kwargs = ub.dict_subset(argkw, ['T', 'D'])
            for timer in ti.reset('time'):
                with timer:
                    method(**kwargs)

            row['mean'] = ti.mean()
            row['min'] = ti.min()
            row['key'] = key
            row['argkey'] = argkey
            measures.append(row)

    import pandas as pd
    df = pd.DataFrame(measures)
    import kwplot
    sns = kwplot.autosns()

    kwplot.figure(fnum=1, pnum=(1, 2, 1), docla=True)
    sns.lineplot(data=df, x='D', y='min', hue='method', style='method')
    kwplot.figure(fnum=1, pnum=(1, 2, 2), docla=True)
    sns.lineplot(data=df, x='T', y='min', hue='method', style='method')

    p = (df.pivot(['method'], ['argkey'], ['mean']))
    print(p.mean(axis=1).sort_values())


def renormalize_demo_v1(D, T):
    import numpy as np
    energy = np.random.rand(D)
    for _ in range(T):
        probs = energy / energy.sum()
        # Do something with probs
        # Get probabilities for the next state and update
        updates = np.random.rand(D)
        energy = energy * updates


def renormalize_demo_v2(D, T):
    import numpy as np
    energy = np.random.rand(D)
    probs = np.empty_like(energy)
    for _ in range(T):
        probs[:] = energy
        probs /= energy.sum()
        # Do something with probs
        # Get probabilities for the next state and update
        updates = np.random.rand(D)
        energy *= updates


def renormalize_demo_v3(D, T):
    import numpy as np
    energy = np.random.rand(D)
    probs = np.empty_like(energy)
    for _ in range(T):
        probs = np.divide(energy, energy.sum(), out=probs)
        probs /= energy.sum()
        # Do something with probs
        # Get probabilities for the next state and update
        updates = np.random.rand(D)
        energy *= updates


def renormalize_demo_v4(D, T):
    import numpy as np
    import kwarray
    energy = kwarray.fast_rand.uniform32(size=D)
    probs = np.empty_like(energy)
    for _ in range(T):
        probs[:] = energy
        probs /= energy.sum()
        # Do something with probs
        # Get probabilities for the next state and update
        updates = kwarray.fast_rand.uniform32(size=D)
        energy *= updates


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/bench_renormalization.py
    """
    import kwplot
    plt = kwplot.autoplt()
    run_benchmark_renormalization()
    plt.show()
