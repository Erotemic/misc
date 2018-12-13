import pickle
from os.path import join
import numpy as np
import ubelt as ub
import pandas as pd


class Pickleable(object):
    def __init__(self):
        self.numpy_data = np.random.rand(100, 100, 100).astype(np.float32)
        self.multiple_np_data = [
            np.random.rand(100, 100, 100).astype(np.float32)
            for _ in range(10)
        ]
        self.pandas_data = pd.DataFrame()
        self.pandas_data['data1'] = np.zeros(100)
        self.pandas_data['data2'] = list(range(100))
        self.pandas_data['data3'] = [object() for obj in range(100)]
        self.strings = ['fdsfjkljkfldsjkl', 'fdsafjkdslfjdsklfjdskl']
        self.none1 = None
        self.none2 = None


def benchmark_pickle_protocols():
    data = Pickleable()

    dpaths = {
        'ssd': ub.ensure_app_cache_dir('pickle_benchmark'),
        'ra10': ub.ensuredir('/raid/cache/pickle_bench'),
    }
    protocols = [0, 1, 2, 3, 4]

    def benchmark_write(xxd, proto):
        dpath = dpaths[xxd]
        args = {'proto': proto, 'xxd': xxd}

        fpath = join(dpath, 'test_{}.pkl'.format(proto))
        for timer in ub.Timerit(10, label='save {}'.format(args)):
            ub.delete(fpath)
            ub.writeto(fpath, 'junkdata')
            ub.delete(fpath)
            with timer:
                with open(fpath, 'wb') as file:
                    pickle.dump(data, file, protocol=proto)

        result = args.copy()
        result['write_time'] = timer.ellapsed

        for timer in ub.Timerit(10, label='read {}'.format(args)):
            with timer:
                with open(fpath, 'rb') as file:
                    pickle.load(file)

        result['read_time'] = timer.ellapsed
        return result

    results = []
    for xxd in dpaths.keys():
        for proto in protocols:
            results.append(benchmark_write(xxd, proto))

    df = pd.DataFrame.from_dict(results)
    df = df.sort_values('write_time')
    print(df)

    print('\n')

    df = df.sort_values('read_time')
    print(df)


if __name__ == '__main__':
    r"""
    CommandLine:
        python ~/misc/python_tests/test_pickle_protocols.py benchmark_pickle_protocols
    """
    import xdoctest
    xdoctest.doctest_module(__file__)
