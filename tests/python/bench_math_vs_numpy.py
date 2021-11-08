

def benchmark_math_vs_numpy():
    import math
    import numpy as np
    import timerit

    ti = timerit.Timerit(100000, bestof=100, verbose=2)
    for timer in ti.reset('np.isclose'):
        x = np.random.rand() * 1000
        with timer:
            np.isclose(x, 0)

    for timer in ti.reset('math.isclose'):
        x = np.random.rand() * 1000
        with timer:
            math.isclose(x, 0)

    ti = timerit.Timerit(100000, bestof=100, verbose=2)
    for timer in ti.reset('multiple np.sqrt'):
        x = np.random.rand(2) * 1000
        with timer:
            np.sqrt(x)

    for timer in ti.reset('multiple math.sqrt'):
        x = np.random.rand(2) * 1000
        with timer:
            [math.sqrt(item) for item in x]

    import ubelt as ub
    import math
    import numpy as np
    import timerit
    operations = {
        'math.sin': math.sin,
        'np.sin': np.sin,
        'math.sqrt': math.sqrt,
        'np.sqrt': np.sqrt,
        'np.exp': np.exp,
        'math.exp': math.exp,
        'math.asin': math.asin,
        'np.arcsin': np.arcsin,
        'math.isclose-0': lambda x: math.isclose(x, 0),
        'np.isclose-0': lambda x: np.isclose(x, 0),
        'math.atan2-1': lambda x: math.atan2(x, 1),
        'np.atan2-1': lambda x: np.arctan2(x, 1),
    }
    ti = timerit.Timerit(100000, bestof=100, verbose=2)
    for opkey, op in operations.items():
        for timer in ti.reset(opkey):
            x = np.random.rand()
            with timer:
                op(x)

    print('ti.rankings = {}'.format(ub.repr2(ti.rankings['mean'], nl=1, precision=9, align=':')))
