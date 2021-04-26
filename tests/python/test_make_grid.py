
def time_grid_create_methods():
    import numpy as np
    import ubelt
    N = 10
    K = 1001
    for timer in ubelt.Timerit(100, bestof=10, label='hv-stack'):
        with timer:
            ns = np.hstack([np.arange(N)[:, None]] * K).ravel()
            ks = np.vstack([np.arange(K)[None, :]] * N).ravel()

    for timer in ubelt.Timerit(100, bestof=10, label='tile'):
        with timer:
            ns = np.tile(np.arange(N)[:, None], (1, K)).ravel()
            ks = np.tile(np.arange(K), (N, 1)).ravel()

    for timer in ubelt.Timerit(100, bestof=10, label='repeat+arange'):
        with timer:
            ns = np.repeat(np.arange(N), K, axis=0).ravel()
            ks = np.repeat(np.arange(K)[None, :], N, axis=0).ravel()

    for timer in ubelt.Timerit(100, bestof=10, label='mgrid'):
        with timer:
            ns, ks = np.mgrid[0:N, 0:K]
            ns = ns.ravel()
            ks = ks.ravel()

    for timer in ubelt.Timerit(100, bestof=10, label='meshgrid'):
        with timer:
            ks, ns = np.meshgrid(np.arange(K), np.arange(N))
            ns = ns.ravel()
            ks = ks.ravel()

    for timer in ubelt.Timerit(100, bestof=10, label='ogrid+repeat'):
        with timer:
            ns_basis, ks_basis = np.ogrid[0:N, 0:K]
            ns = np.repeat(ns_basis, K, axis=0).ravel()
            ks = np.repeat(ks_basis, N, axis=0).ravel()
