"""
Make plots for birthday style hash collisions

There are a lot of floating point and precision issues here that make it tricky
to get these numbers exactly.

References:
    https://stackoverflow.com/questions/18134627/how-much-of-a-git-sha-is-generally-considered-necessary-to-uniquely-identify-a
    https://en.wikipedia.org/wiki/Birthday_problem
    https://www.johndcook.com/blog/2016/01/30/general-birthday-problem/
    https://gist.github.com/benhoyt/b59c00fc47361b67bfdedc92e86b03eb
    https://en.wikipedia.org/wiki/Birthday_attack
"""
#!/usr/bin/env python3
import scriptconfig as scfg
import ubelt as ub
import numpy as np


class BirthdayProblemConfig(scfg.DataConfig):
    # src = scfg.Value(None, position=1, help='input')
    ...


def main(cmdline=1, **kwargs):
    """
    Example:
        >>> # xdoctest: +SKIP
        >>> import sys, ubelt
        >>> sys.path.append(ubelt.expandpath('~/misc/learn'))
        >>> from birthday_problem import *  # NOQA
        >>> cmdline = 0
        >>> kwargs = dict(
        >>> )
        >>> main(cmdline=cmdline, **kwargs)
    """
    config = BirthdayProblemConfig.legacy(cmdline=cmdline, data=kwargs)
    print('config = ' + ub.urepr(dict(config), nl=1))

    # alphabet size
    # base = 16
    base = 26
    state_sizes = [365, base ** 7, base ** 8, base ** 12, base ** 16, base ** 32][0:4]

    import ubelt as ub
    executor = ub.Executor(mode='thread', max_workers=2)

    impls = {k: v for k, v in Birthday.__dict__.items() if not k.startswith('_')}
    import numpy as np
    from concurrent.futures import TimeoutError
    rows = []
    for N in np.array(state_sizes).astype(float):
        num_chars = np.log(N) / np.log(base)
        M = N // 4
        M = min(1_000_000_000_000, N)
        # num_samples = np.unique(np.linspace(10, M, 1000).round().astype(int)).astype(float)
        num_samples = np.unique((10 ** np.linspace(1, np.log10(M), 3000)).round().astype(int)).astype(float)
        for r in ub.ProgIter(num_samples, desc='compute', homogeneous=False, freq=1, adjust=False):
            for key, func in impls.items():
                ...
                job = executor.submit(func, N, r)
                try:
                    p = job.result(timeout=1)
                except TimeoutError:
                    job.cancel()
                except AssertionError:
                    job.cancel()
                else:
                    p = float(p)
                    rows.append({'num_chars': num_chars, 'N': N, 'r': r, 'p': p, 'method': key})

    import pandas as pd
    import kwplot
    sns = kwplot.autosns()
    df = pd.DataFrame(rows)
    df = df[np.isfinite(df['p'])]
    N_to_group = dict(list(df.groupby('N')))
    pnum_ = kwplot.PlotNums(nSubplots=len(N_to_group))
    for N, group in N_to_group.items():
        fig = kwplot.figure(fnum=1, pnum=pnum_())
        ax = fig.gca()
        sns.lineplot(data=group, x='r', y='p', ax=ax, hue='method')
        num_chars = group['num_chars'].iloc[0]
        ax.set_title(f'symbols {base} ** {num_chars} = {N}')
        ax.set_xlabel('r (num samples)')
        ax.set_xscale('log')
        ax.set_yscale('log', base=2)
        ax.plot([0, group['r'].max()], [.5, .5])
        ax.plot([0, group['r'].max()], [.001, .001])
        ax.plot([0, group['r'].max()], [.01, .01])
        ymin, ymax = ax.get_ylim()
        ax.set_ylim(ymin, 1.1)


class Birthday:
    """
    Different implementations / approximations of the birthday problem

    1 - N! / (N ** r * (N - r)!)

    All functions have the signature

    Args:
        N (int): number of possible states (e.g. 365 days, or 2 ** bits in a hash function)
        r (int): the number of samples (i.e. 23 students)

    Returns:
        float: the probability that at least two people in the ``r`` samples
            share a birthday.

    Example:
        >>> import sys, ubelt
        >>> sys.path.append(ubelt.expandpath('~/misc/learn'))
        >>> from birthday_problem import *  # NOQA
        >>> impls = {k: v for k, v in Birthday.__dict__.items() if not k.startswith('_')}
        >>> # Can only go so big with direct methods
        >>> N, r = 7, 3
        >>> results = {}
        >>> for key, func in impls.items():
        >>>     results[key] = float(func(N=N, r=r))
        >>> print('results = {}'.format(ub.urepr(results, nl=1, align=':')))
        >>> # Can go bigger with logspace
        >>> N, r = 365, 23
        >>> results = {}
        >>> for key, func in impls.items():
        >>>     results[key] = float(func(N=N, r=r))
        >>> print('results = {}'.format(ub.urepr(results, nl=1, align=':')))
    """

    # @staticmethod
    # def exact_direct(N, r):
    #     from scipy.special import factorial
    #     return ((factorial(N) / (N ** r)) / factorial(N - r))

    def exact_series(N, r):
        max_size = 16_000_000
        num_parts, remain = map(int, divmod(r, max_size))

        if r > 600000:
            raise AssertionError

        def generate():
            if num_parts > 0:
                arr = np.arange(1, max_size)
                yield arr

                for i in range(1, num_parts):
                    a = i * max_size
                    b = (i + 1) * max_size
                    arr = np.arange(a, b)
                    yield arr

                if remain:
                    final = int(num_parts * max_size)
                    arr = np.arange(final, final + remain)
                    yield arr
            else:
                arr = np.arange(1, remain)
                yield arr

        total = 0
        # import scipy.special
        size = num_parts + 1
        for arr in ub.ProgIter(generate(), total=size, desc='series', enabled=size > 2):
            body = 1 - (np.arange(1, r) / N)
            total += np.log(body).sum()
        p = 1 - np.exp(total)
        return p

    @staticmethod
    def exact_logspace(N, r):
        from numpy import exp, log
        from scipy.special import loggamma
        return np.clip(1 - exp(loggamma(N + 1) - loggamma(N - r + 1) - r * log(N)), 0, 1)

    # @staticmethod
    # def exact_symbolic_direct(N, r):
    #     """
    #     """
    #     from sympy import factorial, Pow
    #     return (factorial(N) / Pow(N, r)) / (factorial(N - r))

    @staticmethod
    def exact_symbolic_logspace(N, r):
        from sympy import loggamma
        from sympy import exp, log
        return np.clip(1 - exp(loggamma(N + 1) - loggamma(N - r + 1) - r * log(N)), 0, 1)

    # def approx_poisson(N, r):
    #     from numpy import exp
    #     from scipy.special import comb
    #     return exp(-comb(r, 2) / N)

    # def approx_square(N, r):
    #     return np.clip(1 - (r ** 2) / (2 * N), 0, 1)

    def approx_wiki_genshared_v1(N, r):
        # https://en.wikipedia.org/wiki/Birthday_problem#Probability_of_a_shared_birthday_(collision)
        return 1 - np.exp((-r * (r - 1)) / (2 * N))

    def approx_wiki_sympy_genshared_v1(N, r):
        import sympy
        r = sympy.Float(r)
        N = sympy.Float(N)
        p = 1 - sympy.exp(-(r * (r - 1)) / (2 * N))
        return p

    # def approx_wiki_genshared_v2(N, r):
    #     # https://en.wikipedia.org/wiki/Birthday_problem#Probability_of_a_shared_birthday_(collision)
    #     return ((N - 1) / N) ** (r * (r - 1) / 2)

    def rule_of_thumb(N, r):
        return np.clip(((r * r) / (2 * N)), 0, 1)

    # def lower_bound(N, r):
    #     """
    #     https://crypto.stackexchange.com/questions/64584/on-a-lower-bound-for-the-birthday-problem
    #     """
    #     # if r < np.sqrt(2 * N):
    #     #     numer = (r - 1) ** 2
    #     #     denom = 4 * N
    #     # else:

    #     p = (r * (r - 1)) / (2 * N)
    #     # p = (1 - np.exp(-1)) * r * (r - 1) / (2 * N)
    #     # numer = (r - 1) * r
    #     # denom = 2 * N
    #     # p = 1 - (numer / denom)
    #     p = np.clip(p, 0, 1)
    #     return p

def symbolic_work():
    import sympy
    from sympy import loggamma
    from sympy import factorial, Pow
    from sympy import exp, log
    import sympy as sym
    N, r = sym.symbols('N, r')
    a, b, c = sym.symbols('a, b, c')
    assert (a / (b * c)) == ((a / b) / c)
    expr = factorial(N) / (Pow(N, r) * factorial(N - r))
    print(sym.pretty(expr))

    k = sym.symbols('k')
    expr_v1 = sym.Product(1 - k / N, (k, 1, (r - 1)))
    print(sympy.pretty(expr_v1))

    bound_v1 = sym.Product(sympy.exp(-k / N), (k, 1, (r - 1)))
    print(sympy.pretty(bound_v1))

    bound_v1 = sym.Product(sympy.exp(-k / N), (k, 1, (r - 1)))
    bound_v2 = sym.exp(-r * (r - 1) / (2 * N))
    print(sympy.pretty(bound_v1))
    print(sympy.pretty(bound_v2))

    subber = {N: 365, r: 23}
    print(expr_v1.subs(subber).evalf())
    print(bound_v1.subs(subber).evalf())
    print(bound_v2.subs(subber).evalf())

    import scipy.special
    N = (16 ** 8)
    # N = (26 ** 12)
    #N = (32 ** 12)
    # r = 10000
    r = 5000
    # N = 365
    # r = 23
    body = 1 - (np.arange(1, r) / N)
    np.prod(body)
    1 - np.exp(np.log(body).sum())
    # np.log(body)
    # scipy.special.logsumexp(body)


if __name__ == '__main__':
    """

    CommandLine:
        python ~/misc/learn/birthday_problem.py
        python -m birthday_problem
    """
    main()
