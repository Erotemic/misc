import numpy as np

def check_ttest():
    import scipy
    import scipy.stats  # NOQA
    from benchmarker.benchmarker import stats_dict
    import numpy as np
    metric_vals1 = np.random.randn(10000) + 0.01
    metric_vals2 = np.random.randn(1000)

    stats1 = stats_dict(metric_vals1)
    stats2 = stats_dict(metric_vals2)

    ind_kw = dict(
        equal_var=0,
        # alternative='two-sided'
        alternative='less' if stats1['mean'] < stats2['mean'] else 'greater'
    )

    # Not sure why these are slightly different
    res1 = scipy.stats.ttest_ind(metric_vals1, metric_vals2, **ind_kw)

    res2 = scipy.stats.ttest_ind_from_stats(
        stats1['mean'], stats1['std'], stats1['n'],
        stats2['mean'], stats2['std'], stats2['n'],
        **ind_kw
    )
    print('res1 = {!r}'.format(res1))
    print('res2 = {!r}'.format(res2))


def stats_dict(data):
    stats = {
        'nobs': len(data),
        'mean': data.mean(),
        'std': data.std(),
        'min': data.min(),
        'max': data.max(),
    }
    return stats


def combine_stats(s1, s2):
    """
    Helper for combining mean and standard deviation of multiple measurements

    Args:
        s1 (dict): stats dict containing mean, std, and n
        s2 (dict): stats dict containing mean, std, and n

    Example:
        >>> basis = {
        >>>     'nobs1': [1, 10, 100, 10000],
        >>>     'nobs2': [1, 10, 100, 10000],
        >>> }
        >>> for params in ub.named_product(basis):
        >>>     data1 = np.random.rand(params['nobs1'])
        >>>     data2 = np.random.rand(params['nobs2'])
        >>>     data3 = np.hstack([data1, data2])
        >>>     s1 = stats_dict(data1)
        >>>     s2 = stats_dict(data2)
        >>>     s3 = stats_dict(data3)
        >>>     # Check that our combo works
        >>>     combo_s3 = combine_stats(s1, s2)
        >>>     compare = pd.DataFrame({'raw': s3, 'combo': combo_s3})
        >>>     print(compare)
        >>>     assert np.allclose(compare.raw, compare.combo)

    References:
        https://stackoverflow.com/questions/7753002/adding-combining-standard-deviations
        https://math.stackexchange.com/questions/2971315/how-do-i-combine-standard-deviations-of-two-groups
    """
    stats = [s1, s2]
    sizes = np.array([s['nobs'] for s in stats])
    means = np.array([s['mean'] for s in stats])
    stds = np.array([s['std'] for s in stats])
    mins = np.array([s['min'] for s in stats])
    maxs = np.array([s['max'] for s in stats])
    varis = stds * stds

    combo_size = sizes.sum()
    combo_mean = (sizes * means).sum() / combo_size

    mean_diff = (means - combo_mean)
    mean_squared_diff = mean_diff * mean_diff

    sv = (sizes * varis).sum()
    smd = (sizes * mean_squared_diff).sum()
    combo_var = (sv + smd) / combo_size
    combo_std = np.sqrt(combo_var)

    """
    Let n = number of observations 1, i.e. len(X)
    Let m = number of observations 2, i.e. len(Y)

    Let mX = mean(X)
    Let mY = mean(Y)
    Let vX = var(X)
    Let vY = var(Y)

    # The combined mean is easy
    mZ = ((mX * n) + (mY * m)) / (n + m)

    # The combined population variance is
    vZ = (
        ((n * vX) + (m * vY)) +
        ((n * (mX - mZ) ** 2) + (m * (mY - mZ) ** 2))
    ) / (m + n)

    # The combined sample variance is
    sample_vZ = (
        (((n - 1) * sample_vX) + ((m - 1) * sample_vY)) +
        ((n * (mX - mZ) ** 2) + (m * (mY - mZ) ** 2))
    ) / (m + n - 1)

    """

    combo_stats = {
        'nobs': combo_size,
        'mean': combo_mean,
        'std': combo_std,
        'min': mins.min(),
        'max': maxs.max(),
    }
    return combo_stats


def symbolic_population_combo_stats():
    import sympy as sym

    class Constraints(list):
        def __setitem__(self, key, val):
            if not isinstance(key, tuple):
                key = (key, '')
            self.append((key, val))

        def __getitem__(self, key):
            if isinstance(key, tuple):
                found = [v for k, v in self if k == key][0]
            else:
                found = [v for (a, lbl), v in self if a == key]
            return found

        def get_subs(self, *args):
            found = []
            for k in args:
                vs = self[k]
                for v in vs:
                    found.append((k, v))
            return found

    constraints = Constraints()

    # First indexed object
    n = sym.symbols('n', integer=True, negative=False)
    X = sym.IndexedBase('X')
    i = sym.Idx('i', n)
    mX, vX = sym.symbols('mX, vX')  # symbolic mean / variance
    res_mX_Xi  = sym.IndexedBase('res_mX_X')[i]   # symbolic mean residual
    qres_mX_Xi = sym.IndexedBase('qres_mX_X')[i]  # symbolic squared mean residual
    constraints[res_mX_Xi]  = (X[i] - mX)       # mean residual
    constraints[qres_mX_Xi] = (X[i] - mX) ** 2  # mean residual squared
    # Definition of mean and variance
    constraints[mX] = sym.summation(X[i], i) / n
    constraints[vX] = sym.summation((X[i] - mX) ** 2, i) / n

    # Second indexed object
    m = sym.symbols('m', integer=True, negative=False)
    Y = sym.IndexedBase('Y')
    j = sym.Idx('j', (0, m - 1))
    mY, vY = sym.symbols('mY, vY')
    vY = sym.symbols('vY')
    res_mY_Yj = sym.IndexedBase('res_mY_Y')[j]
    qres_mY_Yj = sym.IndexedBase('qres_mY_Y')[j]
    constraints[res_mY_Yj] = (Y[j] - mY)
    constraints[qres_mY_Yj] = (Y[j] - mY) ** 2
    constraints[mY] = sym.summation(Y[j], j) / m
    constraints[vY] = sym.summation((Y[j] - mY) ** 2, j) / m

    # We now want to find the stats of the combined Z = concat([X, Y])
    k = sym.Idx('k', m + n)
    mZ = sym.symbols('mZ')
    vZ = sym.symbols('vZ')

    # Let t be the total items in Z. This is the sum of the size of its parts.
    t = n + m

    # Define the mean of Z in terms of original sets X and Y
    # We don't know these, but we will use these to verify the general formula
    constraints[mZ, 'terms_X_Y'] = (
        sym.summation(X[i], i) +
        sym.summation(Y[j], j)
    ) / t

    # The expression for mZ in terms of mX and mY is not hard to see
    # The mean of the combined set is easy to compute
    constraints[mZ, 'terms_mX_mY'] = (n * mX + m * mY) / (n + m)

    if 1:
        # Demonstrate equality
        lhs = constraints[mZ, 'terms_X_Y']
        rhs = constraints[mZ, 'terms_mX_mY'].subs(
            constraints.get_subs(mX, mY)
        )
        assert (rhs - lhs).simplify() == 0

    # Define variance of Z in terms of X and Y.
    # The squared residuals are wrt to mZ this time.
    qres_mZ_Xi = sym.IndexedBase('qres_mZ_X')[i]
    qres_mZ_Yj = sym.IndexedBase('qres_mZ_Y')[j]
    constraints[qres_mZ_Xi, 'raw1'] = (X[i] - mZ) ** 2
    constraints[qres_mZ_Yj, 'raw1'] = (Y[j] - mZ) ** 2
    constraints[vZ] = (
        sym.summation(constraints[qres_mZ_Xi, 'raw1'], i) +
        sym.summation(constraints[qres_mZ_Yj, 'raw1'], j)
    ) / t

    # Define symbols for the residual terms of Z
    # res_mZ_Zk = sym.IndexedBase('qres_mZ_Z')[k]
    qres_mZ_Zk = sym.IndexedBase('qres_mZ_Z')[k]
    constraints[qres_mZ_Zk] = sym.Piecewise(
        (qres_mZ_Xi.base[k], k < n),
        (qres_mZ_Yj.base[k - n], k >= n)
    )
    constraints[qres_mZ_Xi, 'alt1'] = qres_mZ_Zk.subs(k, i)
    constraints[qres_mZ_Yj, 'alt1'] = qres_mZ_Zk.subs(k, n + j)
    constraints[vZ] = (sym.summation(qres_mZ_Zk, k)) / t

    # The variance is tricker to get in terms of mX, mY, vX, and vY.
    # We can note that:
    # (X[i] - mZ) ** 2 =
    # (X[i] - mX + mX - mZ) ** 2 =
    # (This is the step I want to encode symbolically... it can be seen by
    #  considering
    #     ((a + b + c + d) ** 2).expand() =
    #     a**2 + 2*a*b + 2*a*c + 2*a*d + b**2 + 2*b*c + 2*b*d + c**2 + 2*c*d + d**2
    #  but I'd like to make it more clear so the sympy code does not rely on
    #  comments
    # )
    # (X[i] - mX) ** 2 + 2 * (X[i] - mX) * (mX - mZ) + (mX - mZ) ** 2
    if 0:
        # This shows the above step for X
        a, b, c, d = sym.symbols('a, b, c, d')
        let = {a: X[i], b: mX, c: mX, d: mZ}
        expr = ((a - b + c - d) ** 2).expand()
        term = (a - b) ** 2
        rest = (expr - term.expand())
        adjust = rest.subs(let).factor()
        adjust = sym.collect(adjust.expand(), [X[i]], func=sym.factor)
        sym.collect(adjust.expand(), [X[i]], func=sym.factor)
        expected_adjust = 2 * (X[i] - mX) * (mX - mZ) + (mX - mZ) ** 2
        assert expected_adjust.expand().simplify() == adjust.expand().simplify()
        final = adjust + term.subs(let)
        print('final = {!r}'.format(final))

    constraints[qres_mZ_Xi, 'alt2'] = (
        (X[i] - mX) ** 2 + 2 * (X[i] - mX) * (mX - mZ) + (mX - mZ) ** 2
    )
    constraints[qres_mZ_Xi, 'alt3'] = (
        # qres_mX_Xi       + 2 * res_mX_Xi   * (mX - mZ) + (mX - mZ) ** 2
        qres_mX_Xi       + 2 * (X[i] - mX) * (mX - mZ) + (mX - mZ) ** 2
    )

    # And likewise:
    # (Y[j] - mZ) ** 2 =
    # (Y[j] - mY + mY - mZ) ** 2 =
    # (Y[j] - mY) ** 2 + 2 * (Y[j] - mY) * (mY - mZ) + (mY - mZ) ** 2
    constraints[qres_mZ_Yj, 'alt2'] = (
        (Y[j] - mY) ** 2 + 2 * (Y[j] - mY) * (mY - mZ) + (mY - mZ) ** 2
    )
    constraints[qres_mZ_Yj, 'alt3'] = (
        qres_mY_Yj       + 2 * (Y[j] - mY) * (mY - mZ) + (mY - mZ) ** 2
        # qres_mY_Yj       + 2 * res_mY_Yj   * (mY - mZ) + (mY - mZ) ** 2
    )

    constraints[vZ, 'alt3'] = (
        sym.summation(constraints[qres_mZ_Xi, 'alt3'], i) +
        sym.summation(constraints[qres_mZ_Yj, 'alt3'], j)
    ) / t

    def hack_simplify_sum(expr):
        # https://stackoverflow.com/questions/62679575/why-cant-sympy-simplify-these-sum-expressions-of-indexed-variables
        # https://github.com/sympy/sympy/issues/19685

        if expr.func is sym.concrete.summations.Sum:
            body, (idx, lower, upper) = expr.args
            if idx not in body.free_symbols:
                factor = (upper + 1) - lower
                return factor * body
            else:
                if body.func is sym.Mul:
                    factor_out = []
                    factor_in = []
                    for sub_arg in body.args:
                        if idx in sub_arg.free_symbols:
                            factor_in.append(sub_arg)
                        else:
                            factor_out.append(sub_arg)
                    outer = sym.Mul(*factor_out)
                    return outer * sym.summation(sym.Mul(*factor_in), (idx, lower, upper))
        return expr

    def distribute(func, expr):
        assert expr.func in [sym.Add, sym.Mul]
        new_args = [func(a) for a in expr.args]
        return expr.func(*new_args)

    # We will use these facts
    constraints[sym.summation(X[i], i)] = mX * n,
    constraints[sym.summation(qres_mX_Xi, i)] = vX * n
    constraints[sym.summation(Y[j], j)] = mY * m
    constraints[sym.summation(qres_mY_Yj, j)] = vY * m

    # Now that we have established the relation between the each squared
    # residual term wrt mZ in terms of mX, we need to establish an expression
    # for the sum of the squared residual terms wrt mZ.
    # The goal is to find a way to cancel any remaining references to X[i]
    qrsum_part1 = sym.summation(constraints[qres_mZ_Xi, 'alt3'], i)
    qrsum_part1 = distribute(hack_simplify_sum, qrsum_part1.expand())
    # We can replace the sum of X with mX * n, because the sum of all items
    # in X will be equal to the mean of X added together n times.
    # similar thing with the sum of the qres
    qrsum_part1 = qrsum_part1.subs({
        sym.summation(X[i], i): mX * n,
        sym.summation(qres_mX_Xi, i): vX * n
    })

    qrsum_part2 = sym.summation(constraints[qres_mZ_Yj, 'alt3'], j)
    qrsum_part2 = distribute(hack_simplify_sum, qrsum_part2.expand())
    qrsum_part2 = qrsum_part2.subs({
        sym.summation(Y[j], j): mY * m,
        sym.summation(qres_mY_Yj, j): vY * m
    })

    constraints[vZ, 'alt4'] = (
        qrsum_part1 +
        qrsum_part2
    ) / t

    print(sym.pprint(constraints[vZ, 'alt4']))

    # sym.summation(constraints[qres_mZ_Xi, 'alt3'].subs(constraints.get_subs(res_mX_Xi, qres_mX_Xi)), i).simplify().factor()
    # part1.subs(constraints.get_subs(res_mX_Xi, qres_mX_Xi))

    for a, b in constraints:
        print('\n---\n')
        sym.pprint(a)
        print('=')
        sym.pprint(b)






def symbolic_combo_stats():
    import sympy as sym  # NQOA

    def indexed_samples(var_name, idx_name, nobs_name):
        nobs = sym.symbols(nobs_name, integer=True, negative=False)
        var = sym.IndexedBase(var_name)
        idx = sym.Idx(idx_name, (0, nobs - 1))  # an index ranging from 0 to nobs-1
        return var, idx, nobs

    def indexed_stats(X, i, n):
        # Represents sum(var[i] for i in range(0, nobs))
        sum_X = sym.summation(X[i], (i, 0, n - 1))
        mean_X = sum_X / n

        # The variance is the average squared distance to the mean.
        var_X = sym.summation((X[i] - mean_X) ** 2, (i, 0, n - 1)) / n
        std_X = sym.sqrt(var_X)

        # Note that when using a sample to estimate the value for a population, the
        # computed variance will be an underestimate (via Jensen's inequality).
        # This is accounted for by dividing by (n - 1) instead of n, which is
        # known as Bessel's correction, and this works for variance only.
        # https://en.wikipedia.org/wiki/Bessel%27s_correction
        # https://www.youtube.com/watch?v=bHVPpomkUYs
        # https://www.youtube.com/watch?v=bVB4X5CUWTg
        unbiased_var_X = sym.summation((X[i] - mean_X) ** 2, (i, 0, n - 1)) / (n - 1)

        # There is no way to do this for the standard deviation in general
        # https://en.wikipedia.org/wiki/Standard_deviation#Unbiased_sample_standard_deviation
        # https://en.wikipedia.org/wiki/Unbiased_estimation_of_standard_deviation
        # Different distributions will have different correction factors, although
        # using n-1 is a decent rule of thumb?
        unbiased_std_X = sym.sqrt(unbiased_var_X)

        stats = {
            'mean': mean_X,
            'var': var_X,
            'std': std_X,
            'unbiased_var': unbiased_var_X,
            'unbiased_std': unbiased_std_X,
        }
        return stats

    X, i, n = indexed_samples('X', 'i', 'n')
    Y, j, m = indexed_samples('Y', 'j', 'm')
    stats_X = indexed_stats(X, i, n)
    stats_Y = indexed_stats(Y, j, m)

    # Let Z be the concat of X and Y
    Z = sym.IndexedBase('Z')

    # Let these represent the means of X and Y and Z
    mX = sym.symbols('mX')
    mY = sym.symbols('mY')
    mZ = sym.symbols('mZ')

    # To compute new var wrt to Z we need to be able to express A in [X, Y]
    # Let's do it with X (works the same with Y) without loss of generatity
    '''
    (X[i] - mZ) ** 2
    ((X[i] - mX + mX - mZ) ** 2)
    a = ((X[i] - u + v - mZ) ** 2).expand()
    with sym.evaluate(False):
        b = a.subs({u: mX, v: mX})
    # mX**2 + mX**2 - 2*mX*mZ + 2*mX*mZ - 2*mX*X[i] + 2*mX*X[i] - 2*mX*mX + mZ**2 - 2*mZ*X[i] + X[i]**2

    # We want to get the previous expresion wrt to this term
    term = (X[i] - mX) ** 2
    offset = (b - term).simplify()
    # -mX**2 + 2*mX*X[i] + mZ**2 - 2*mZ*X[i]

    # Re-add to get
    offset + term

    # On SE this is expressed as
    offset_SE = 2 * (X[i] - mX) * (mX - mZ) + (mX - mZ) ** 2

    -mX**2 + mZ**2 + 2 (mX*X[i] - 2*mZ*X[i]) + (-mX + X[i])**2


    # To rewrite heropop's answer for population variance we get:
    '''


    example = {
        n: 5,
        m: 7,
    }

    x = stats_X['mean'].subs(example)

    def concat_indexed(X, Y):
        pass


def semi_symbolic_stats():
    import sympy as sym
    X = sym.IndexedBase('X')
    Y = sym.IndexedBase('Y')

    n_ = 5
    m_ = 3
    n, m = sym.symbols('n, m')
    Xs = [X[i] for i in range(n_)]
    Ys = [Y[j] for j in range(m_)]
    Zs = Xs + Ys

    mX = sym.symbols('mX')
    mY = sym.symbols('mY')
    vX = sym.symbols('vX')
    vY = sym.symbols('vY')

    mean_X = sum(Xs) / n
    mean_Y = sum(Ys) / m
    mean_Z = sum(Zs) / (m + n)

    mZ = ((mX * n) + (mY * m)) / (m + n)
    sym.pprint(mZ)
    sym.pprint(mZ.subs({mX: mean_X, mY: mean_Y}))

    var_X = sum((x - mX) ** 2 for x in Xs) / n
    var_Y = sum((y - mY) ** 2 for y in Ys) / m
    var_Z = sum((z - mZ) ** 2 for z in Zs) / (m + n)

    vZ = (
        ((n * vX) + (m * vY)) +
        ((n * (mX - mZ) ** 2) + (m * (mY - mZ) ** 2))
    ) / (m + n)
    sym.pprint(vZ)
    sym.pprint(vZ.simplify())
    sym.pprint(vZ.factor())

    # sym.pprint(var_Z.subs({mZ: mean_Z}))
    sym.pprint(var_X)
    sym.pprint(var_Y)
    sym.pprint(var_Z)

    std_X = sym.sqrt(var_X)
    std_Y = sym.sqrt(var_Y)

    mean_Z = ((mean_X * n) + (mean_Y * m)) / (n + m)


    pass


def can_i_concat_indexed_objects():
    import sympy as sym

    # First indexed object
    n = sym.symbols('n', integer=True, negative=False)
    X = sym.IndexedBase('X')
    i = sym.Idx('i', (0, n - 1))

    # Second indexed object
    m = sym.symbols('m', integer=True, negative=False)
    Y = sym.IndexedBase('Y')
    j = sym.Idx('j', (0, m - 1))

    # I would like to create a third object, Z that concatentates X and Y, s.t.
    Z = sym.IndexedBase('Z')
    k = sym.Idx('k', (0, n + m - 1))

    # It should satisfy
    sym.Eq(Z[i], X[i])  # the first elements are from X
    sym.Eq(Z[j + n], Y[j])  # the last elements are from Y

    # which means, given
    sum_X = sym.summation(X[i], (i, 0, n - 1))
    sum_Y = sym.summation(Y[j], (j, 0, m - 1))

    sum_Z = sym.summation(Z[k], (k, 0, n - 1))
    sum_Z_part1 = sym.summation(Z[k], (k, 0, n - 1))
    sum_Z_part2 = sym.summation(Z[k], (k, n, n + m - 1))

    sym.Eq(sum_Z, sum_X + sum_Y)
    sym.Eq(sum_Z_part1, sum_X)
    sym.Eq(sum_Z_part2, sum_Y)

    # One way to do this is
    Z_k = sym.Piecewise(
        (X[k], k < n),
        (Y[k - n], k >= n)
    )
    sum_Z = sym.summation(Z_k, (k, 0, n - 1))

    # But this is not subscriptable
    (sum_Z - sum_X - sum_Y).simplify()
