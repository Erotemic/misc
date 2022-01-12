def main():
    """
    Is it faster to use a dtype as a string or by accessing np.float64

    Turns out the getattr of np. adds enough overhead to make it worse than
    string, but when you import then use, you skip that and do slightly better.

    This is all contrived though. This is never the bottleneck.
    """

    import xarray
    import numpy as np
    from numpy import float64
    import timerit
    data = xarray.DataArray(np.empty(1, dtype=np.int16))

    ti = timerit.Timerit(30000, bestof=10, verbose=2)

    for timer in ti.reset('str-dtype'):
        with timer:
            data.astype('float64')

    for timer in ti.reset('access-raw-dtype'):
        with timer:
            data.astype(np.float64)

    for timer in ti.reset('no-access-raw-dtype'):
        with timer:
            data.astype(float64)
