from os.path import join, basename, exists
import ubelt as ub
import random
import string


def _demodata_files(dpath=None, num_files=10, pool_size=3, size_pool=None):

    def _random_data(rng, num):
        return ''.join([rng.choice(string.hexdigits) for _ in range(num)])

    def _write_random_file(dpath, part_pool, size_pool, rng):
        namesize = 16
        # Choose 1, 4, or 16 parts of data
        num_parts = rng.choice(size_pool)
        chunks = [rng.choice(part_pool) for _ in range(num_parts)]
        contents = ''.join(chunks)
        fname_noext = _random_data(rng, namesize)
        ext = ub.hash_data(contents)[0:4]
        fname = '{}.{}'.format(fname_noext, ext)
        fpath = join(dpath, fname)
        with open(fpath, 'w') as file:
            file.write(contents)
        return fpath

    if size_pool is None:
        size_pool = [1, 4, 16]

    dpath = ub.ensure_app_cache_dir('pfile/random')
    rng = random.Random(0)
    # Create a pool of random chunks of data
    chunksize = 65536
    part_pool = [_random_data(rng, chunksize) for _ in range(pool_size)]
    # Write 100 random files that have a reasonable collision probability
    fpaths = [_write_random_file(dpath, part_pool, size_pool, rng)
              for _ in ub.ProgIter(range(num_files), desc='write files')]

    for fpath in fpaths:
        assert exists(fpath)
    return fpaths


def benchmark():
    import timerit
    import ubelt as ub
    from kwcoco.util.util_futures import JobPool  # NOQA
    ti = timerit.Timerit(3, bestof=1, verbose=2)

    max_workers = 4

    # Choose a path to an HDD
    dpath = ub.ensuredir('/raid/data/tmp')

    fpath_demodata = _demodata_files(dpath=dpath, num_files=1000,
                                     size_pool=[10, 20, 50], pool_size=8)

    for timer in ti.reset('hash_file(hasher=xx64)'):
        with timer:
            for fpath in fpath_demodata:
                ub.hash_file(fpath, hasher='xx64')

    for timer in ti.reset('hash_file(hasher=xxhash) - serial'):
        # jobs = JobPool(mode='thread', max_workers=2)
        jobs = JobPool(mode='serial', max_workers=max_workers)
        with timer:
            for fpath in fpath_demodata:
                jobs.submit(ub.hash_file, fpath, hasher='xxhash')
            results = [job.result() for job in jobs.jobs]

    for timer in ti.reset('hash_file(hasher=xxhash) - thread'):
        # jobs = JobPool(mode='thread', max_workers=2)
        jobs = JobPool(mode='thread', max_workers=max_workers)
        with timer:
            for fpath in fpath_demodata:
                jobs.submit(ub.hash_file, fpath, hasher='xx64')
            results = [job.result() for job in jobs.jobs]

    for timer in ti.reset('hash_file(hasher=xxhash) - process'):
        # jobs = JobPool(mode='thread', max_workers=2)
        jobs = JobPool(mode='process', max_workers=max_workers)
        with timer:
            for fpath in fpath_demodata:
                jobs.submit(ub.hash_file, fpath, hasher='xx64')
            results = [job.result() for job in jobs.jobs]


if __name__ == '__main__':
    benchmark()
