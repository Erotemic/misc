import numpy as np
import ubelt as ub
from os.path import join
import h5py
import pandas as pd
import utool as ut  # NOQA


def test_array_io():
    """
    References:
        http://tdeboissiere.github.io/h5py-vs-npz.html
    """

    # Setup Test Data
    dpath = ub.ensure_app_cache_dir('misc')
    dpath = '.'

    N_ARRS = 100
    N_ITERS = 1

    arrs = [np.random.rand(480, 360, 4) for i in range(N_ARRS)]
    # arrs = [np.random.rand(2048, 2048, 4).astype(np.float32) for i in range(N_ARRS)]

    class Store(object):
        """
        Base class helper for defining IO storage strategies
        """

        def name(self):
            return self.__class__.__name__

        def n_bytes(self):
            return sum(map(ut.file_bytes, self.paths()))

        def test_disk_io(self):
            # Function that runs different strategies
            key = self.name()

            print('\n# --- {} ---'.format(key))
            write_ti = ub.Timerit(N_ITERS, label='{} write time'.format(self.ext))
            for timer in write_ti:
                with timer:
                    self.write()

            read_ti = ub.Timerit(N_ITERS, label='{} read time'.format(self.ext))
            for timer in read_ti:
                with timer:
                    for _ in self.read():
                        pass

            record.loc[key, 'write'] = write_ti.ave_secs
            record.loc[key, 'read'] = read_ti.ave_secs
            record.loc[key, 'MB'] = self.n_bytes() * 1e-6
            print('\n')
            print(record)
            print('-------')

    class MultiFileStore(Store):
        def paths(self):
            for i in range(N_ARRS):
                fpath_fmt = join(dpath, 'arr{}' + self.ext)
                fpath = fpath_fmt.format(i)
                yield fpath

    class SingleFileStore(Store):
        def paths(self):
            fpath = join(dpath, 'arrs' + self.ext)
            yield fpath

    record = pd.DataFrame(columns=['write', 'read', 'MB'])

    # === Storage Strategy Definitions ===

    # Multi File (file-per-item) Stores

    class NPY(MultiFileStore):
        ext = '.npy'
        def __init__(self, readkw={}, writekw={}):
            self.readkw = readkw
            self.writekw = writekw

        def read(self):
            for fpath in self.paths():
                yield np.load(fpath, **self.readkw)[...]

        def write(self):
            for fpath, arr in zip(self.paths(), arrs):
                np.save(fpath, arr, **self.writekw)

        def name(self):
            read_id = ub.repr2(self.readkw, nl=0, sep='', si=True)
            write_id = ub.repr2(self.writekw, nl=0, sep='', si=True)
            return super().name() + '(' + read_id + ', ' + write_id + ')'

    class NPZ(MultiFileStore):
        ext = '.npz'
        def read(self):
            for fpath in self.paths():
                yield np.load(fpath)['arr_0'][...]

        def write(self):
            for fpath, arr in zip(self.paths(), arrs):
                np.savez(fpath, arr)

    class H5PY(MultiFileStore):
        ext = '.h5'
        def read(self):
            for fpath in self.paths():
                with h5py.File(fpath, 'r') as hf:
                    yield hf['arr_0'][...]

        def write(self):
            for fpath, arr in zip(self.paths(), arrs):
                with h5py.File(fpath, 'w') as hf:
                    hf.create_dataset('arr_0', data=arr)

    # Single File Database Stores

    class NPZ_DB(SingleFileStore):
        ext = '.npz'
        def read(self):
            fpath, = self.paths()
            file_ = np.load(fpath)
            for i in range(N_ARRS):
                yield file_['arr_{}'.format(i)][...]

        def write(self):
            fpath, = self.paths()
            np.savez(fpath, *arrs)

    class H5PY_DB(SingleFileStore):
        ext = '.h5'
        def read(self):
            fpath, = self.paths()
            with h5py.File(fpath, 'r') as hf:
                for i in range(N_ARRS):
                    key = 'arr_%d' % (i,)
                    yield hf[key][...]

        def write(self):
            fpath, = self.paths()
            with h5py.File(fpath, 'w') as hf:
                for i, arr in enumerate(arrs):
                    key = 'arr_%d' % i
                    hf.create_dataset(key, data=arr)
                    # hf.create_dataset(key, data=arr, chunks=True,
                    #                   compression='lzf')

    # Execute tests

    NPY().test_disk_io()
    NPY(dict(allow_pickle=False)).test_disk_io()
    NPY(dict(allow_pickle=False, fix_imports=False), dict(allow_pickle=False, fix_imports=False)).test_disk_io()

    NPY().test_disk_io()

    H5PY_DB().test_disk_io()
    NPZ_DB().test_disk_io()

    H5PY().test_disk_io()
    NPZ().test_disk_io()

    print('\n----')
    print(record.sort_values('write'))

    print('\n----')
    print(record.sort_values('read'))

    print('\n----')
    print(record.sort_values('MB'))
