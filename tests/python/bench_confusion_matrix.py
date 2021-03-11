import numpy as np
import xdev

if 0:
    from sklearn.metrics.classification import (unique_labels, _check_targets,
                                                check_consistent_length,
                                                coo_matrix)

else:
    from sklearn.metrics._classification import (unique_labels, _check_targets,
                                                 check_consistent_length,
                                                 coo_matrix)


@xdev.profile
def confusion_matrix_2017(y_true, y_pred, labels=None, sample_weight=None):
    y_type, y_true, y_pred = _check_targets(y_true, y_pred)
    if y_type not in ("binary", "multiclass"):
        raise ValueError("%s is not supported" % y_type)

    if labels is None:
        labels = unique_labels(y_true, y_pred)
    else:
        labels = np.asarray(labels)
        if np.all([l not in y_true for l in labels]):
            raise ValueError("At least one label specified must be in y_true")

    if sample_weight is None:
        sample_weight = np.ones(y_true.shape[0], dtype=np.int64)
    else:
        sample_weight = np.asarray(sample_weight)

    check_consistent_length(sample_weight, y_true, y_pred)

    n_labels = labels.size
    label_to_ind = dict((y, x) for x, y in enumerate(labels))
    y_pred = np.array([label_to_ind.get(x, n_labels + 1) for x in y_pred])
    y_true = np.array([label_to_ind.get(x, n_labels + 1) for x in y_true])

    # eliminate items in y_true, y_pred not in labels
    isvalid = np.logical_and(y_pred < n_labels, y_true < n_labels)
    y_pred = y_pred[isvalid]
    y_true = y_true[isvalid]
    # also eliminate weights of eliminated items
    sample_weight = sample_weight[isvalid]

    # Choose the accumulator dtype to always have high precision
    if sample_weight.dtype.kind in {'i', 'u', 'b'}:
        dtype = np.int64
    else:
        dtype = np.float64

    CM = coo_matrix((sample_weight, (y_true, y_pred)),
                    shape=(n_labels, n_labels), dtype=dtype,
                    ).toarray()

    return CM


@xdev.profile
def confusion_matrix_2021(y_true, y_pred, *, labels=None, sample_weight=None,
                     normalize=None):
    y_type, y_true, y_pred = _check_targets(y_true, y_pred)
    if y_type not in ("binary", "multiclass"):
        raise ValueError("%s is not supported" % y_type)

    if labels is None:
        labels = unique_labels(y_true, y_pred)
    else:
        labels = np.asarray(labels)
        n_labels = labels.size
        if n_labels == 0:
            raise ValueError("'labels' should contains at least one label.")
        elif y_true.size == 0:
            return np.zeros((n_labels, n_labels), dtype=int)
        elif np.all([l not in y_true for l in labels]):
            raise ValueError("At least one label specified must be in y_true")

    if sample_weight is None:
        sample_weight = np.ones(y_true.shape[0], dtype=np.int64)
    else:
        sample_weight = np.asarray(sample_weight)

    check_consistent_length(y_true, y_pred, sample_weight)

    if normalize not in ['true', 'pred', 'all', None]:
        raise ValueError("normalize must be one of {'true', 'pred', "
                         "'all', None}")

    n_labels = labels.size
    label_to_ind = {y: x for x, y in enumerate(labels)}
    # convert yt, yp into index
    y_pred = np.array([label_to_ind.get(x, n_labels + 1) for x in y_pred])
    y_true = np.array([label_to_ind.get(x, n_labels + 1) for x in y_true])

    # intersect y_pred, y_true with labels, eliminate items not in labels
    ind = np.logical_and(y_pred < n_labels, y_true < n_labels)
    y_pred = y_pred[ind]
    y_true = y_true[ind]
    # also eliminate weights of eliminated items
    sample_weight = sample_weight[ind]

    # Choose the accumulator dtype to always have high precision
    if sample_weight.dtype.kind in {'i', 'u', 'b'}:
        dtype = np.int64
    else:
        dtype = np.float64

    cm = coo_matrix((sample_weight, (y_true, y_pred)),
                    shape=(n_labels, n_labels), dtype=dtype,
                    ).toarray()

    with np.errstate(all='ignore'):
        if normalize == 'true':
            cm = cm / cm.sum(axis=1, keepdims=True)
        elif normalize == 'pred':
            cm = cm / cm.sum(axis=0, keepdims=True)
        elif normalize == 'all':
            cm = cm / cm.sum()
        cm = np.nan_to_num(cm)

    return cm


@xdev.profile
def confusion_matrix_2017_new(y_true, y_pred, labels=None, sample_weight=None):
    y_type, y_true, y_pred = _check_targets(y_true, y_pred)
    if y_type not in ("binary", "multiclass"):
        raise ValueError("%s is not supported" % y_type)

    if labels is None:
        labels = unique_labels(y_true, y_pred)
    else:
        labels = np.asarray(labels)
        if np.all([l not in y_true for l in labels]):
            raise ValueError("At least one label specified must be in y_true")

    if sample_weight is None:
        sample_weight = np.ones(y_true.shape[0], dtype=np.int64)
    else:
        sample_weight = np.asarray(sample_weight)

    check_consistent_length(sample_weight, y_true, y_pred)

    n_labels = labels.size
    # If labels are not consecitive integers starting from zero, then
    # yt, yp must be converted into index form
    need_index_conversion = not (
        labels.dtype.kind in {'i', 'u', 'b'} and
        labels.min() == 0 and np.all(np.diff(labels) == 1) and
        y_true.min() >= 0 and y_pred.min() >= 0
    )
    if need_index_conversion:
        label_to_ind = dict((y, x) for x, y in enumerate(labels))
        y_pred = np.array([label_to_ind.get(x, n_labels + 1) for x in y_pred])
        y_true = np.array([label_to_ind.get(x, n_labels + 1) for x in y_true])

    # eliminate items in y_true, y_pred not in labels
    isvalid = np.logical_and(y_pred < n_labels, y_true < n_labels)
    if not np.all(isvalid):
        y_pred = y_pred[isvalid]
        y_true = y_true[isvalid]
        # also eliminate weights of eliminated items
        sample_weight = sample_weight[isvalid]

    # Choose the accumulator dtype to always have high precision
    if sample_weight.dtype.kind in {'i', 'u', 'b'}:
        dtype = np.int64
    else:
        dtype = np.float64

    CM = coo_matrix((sample_weight, (y_true, y_pred)),
                    shape=(n_labels, n_labels), dtype=dtype,
                    ).toarray()

    return CM


@xdev.profile
def confusion_matrix_2021_new(y_true, y_pred, *, labels=None,
                              sample_weight=None, normalize=None):
    y_type, y_true, y_pred = _check_targets(y_true, y_pred)
    if y_type not in ("binary", "multiclass"):
        raise ValueError("%s is not supported" % y_type)

    if labels is None:
        labels = unique_labels(y_true, y_pred)
    else:
        labels = np.asarray(labels)
        n_labels = labels.size
        if n_labels == 0:
            raise ValueError("'labels' should contains at least one label.")
        elif y_true.size == 0:
            return np.zeros((n_labels, n_labels), dtype=int)
        elif len(np.intersect1d(y_true, labels)) == 0:
            raise ValueError("At least one label specified must be in y_true")

    if sample_weight is None:
        sample_weight = np.ones(y_true.shape[0], dtype=np.int64)
    else:
        sample_weight = np.asarray(sample_weight)

    check_consistent_length(y_true, y_pred, sample_weight)

    if normalize not in ['true', 'pred', 'all', None]:
        raise ValueError("normalize must be one of {'true', 'pred', "
                         "'all', None}")

    n_labels = labels.size
    # If labels are not consecutive integers starting from zero, then
    # y_true and y_pred must be converted into index form
    need_index_conversion = not (
        labels.dtype.kind in {'i', 'u', 'b'} and
        np.all(labels == np.arange(n_labels)) and
        y_true.min() >= 0 and y_pred.min() >= 0
    )
    if need_index_conversion:
        label_to_ind = {y: x for x, y in enumerate(labels)}
        y_pred = np.array([label_to_ind.get(x, n_labels + 1) for x in y_pred])
        y_true = np.array([label_to_ind.get(x, n_labels + 1) for x in y_true])

    # intersect y_pred, y_true with labels, eliminate items not in labels
    ind = np.logical_and(y_pred < n_labels, y_true < n_labels)
    if not np.all(ind):
        y_pred = y_pred[ind]
        y_true = y_true[ind]
        # also eliminate weights of eliminated items
        sample_weight = sample_weight[ind]

    # Choose the accumulator dtype to always have high precision
    if sample_weight.dtype.kind in {'i', 'u', 'b'}:
        dtype = np.int64
    else:
        dtype = np.float64

    cm = coo_matrix((sample_weight, (y_true, y_pred)),
                    shape=(n_labels, n_labels), dtype=dtype,
                    ).toarray()

    with np.errstate(all='ignore'):
        if normalize == 'true':
            cm = cm / cm.sum(axis=1, keepdims=True)
        elif normalize == 'pred':
            cm = cm / cm.sum(axis=0, keepdims=True)
        elif normalize == 'all':
            cm = cm / cm.sum()
        cm = np.nan_to_num(cm)

    return cm


def make_inputs(n_input, n_classes, labelkw=None, weightkw=None, dtype=np.uint8, rng=np.random):
    y_true = (rng.rand(n_input) * n_classes).astype(dtype)
    y_pred = (rng.rand(n_input) * n_classes).astype(dtype)

    if labelkw is None:
        labels = None
    else:
        if labelkw == 'int-consec':
            labels = np.arange(n_classes, dtype=np.int)
        elif labelkw == 'int-nonconsec':
            labels = np.arange(n_classes, dtype=np.int)[::-1]
        elif labelkw == 'str':
            labels = np.array(list(map(str, np.arange(n_classes, dtype=np.int))))
        else:
            raise KeyError(labelkw)
        y_true = labels[y_true]
        y_pred = labels[y_pred]

    if weightkw is None:
        sample_weight = None
    else:
        if weightkw == 'float':
            sample_weight = rng.rand(n_input)
        elif weightkw == 'int':
            sample_weight = np.ones(n_input, dtype=np.int)
        else:
            raise KeyError(weightkw)

    kwargs = dict(
        y_true=y_true,
        y_pred=y_pred,
        labels=labels,
        sample_weight=sample_weight)
    return kwargs


def mwe_check_before_select():
    import ubelt as ub
    import numpy as np
    results = []
    ns = np.logspace(1, 7, 100).astype(np.int)
    for n in ub.ProgIter(ns, desc='time-tradeoff', verbose=3):
        print('n = {!r}'.format(n))
        y_true = np.random.randint(0, 100, n).astype(np.int64)
        y_pred = np.random.randint(0, 100, n).astype(np.int64)
        sample_weight = np.random.rand(n)

        isvalid = np.random.rand(n) > 0.5

        import timerit
        ti = timerit.Timerit(9, bestof=3, verbose=2)
        for timer in ti.reset('all-check'):
            with timer:
                np.all(isvalid)
        results.append({
            'n': n,
            'label': ti.label,
            'time': ti.mean(),
        })

        for timer in ti.reset('all-index'):
            with timer:
                y_true[isvalid]
                y_pred[isvalid]
                sample_weight[isvalid]
        results.append({
            'n': n,
            'label': ti.label,
            'time': ti.mean(),
        })

    df = pd.DataFrame(results)

    import kwplot
    import seaborn as sns
    kwplot.autoplt()
    sns.set()
    ax = sns.lineplot(data=df, x='n', y='time', hue='label')
    ax.set_yscale('log')
    ax.set_xscale('log')

    pass


def main():
    import itertools as it
    import ubelt as ub

    basis1 = {
        'n_input': [10, 1000, 10000, 200000],
        'n_classes': [2, 10, 100, 1000],
        'dtype': ['uint8', 'int64'],
        # 'n_input': [10, 1000],
        # 'n_classes': [2, 10],
    }

    basis2 = {
        'labelkw': [None, 'int-consec', 'int-nonconsec', 'str'],
        # 'weightkw': (None, 'float', 'int'),
        'weightkw': (None, 'float'),
    }

    if True:
        basis1 = {
            'n_input': [10, 1000, 10000],
            # 'n_input': [10000, 100000],
            'n_classes': [2, 10, 100],
            'dtype': ['uint8', 'int64'],
            # 'n_input': [10, 1000],
            # 'n_classes': [2, 10],
        }

        basis2 = {
            'labelkw': [None, 'int-consec', 'int-nonconsec'],
            # 'weightkw': (None, 'float', 'int'),
            'weightkw': (None, 'float'),
        }

    if False:
        basis1 = {
            'n_input': [10, 1000, 10000],
            'n_classes': [2, 10, 100],
            'dtype': ['int64'],
        }
        # Lets just look at the consecutive int case
        basis2 = {
            'labelkw': ['int-consec'],
            # 'weightkw': (None, 'float', 'int'),
            'weightkw': ('float',),
        }

    def gridsearch(basis):
        return it.product(*([(k, v) for v in vs] for k, vs in basis.items()))

    import pandas as pd

    import warnings

    all_results = {}

    n_iters = 3
    for kw2 in gridsearch(basis2):
        results = pd.DataFrame()
        print('\n-------')
        print(kw2)
        for kw1 in gridsearch(basis1):
            kw = kw2 + kw1
            key = ub.repr2(dict(kw1), nl=0, si=True, itemsep='', explicit=True, nobr=True)

            kwargs = make_inputs(**dict(kw))

            funcs = {
                '2017_old': confusion_matrix_2017,
                '2017_new': confusion_matrix_2017_new,
                '2021_old': confusion_matrix_2021,
                '2021_new': confusion_matrix_2021_new,
            }

            warnings.filterwarnings('ignore')
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', '.*deprecated.*', category=DeprecationWarning)
                for ver, func in funcs.items():
                    ti = ub.Timerit(n_iters, verbose=0, label=ver)
                    for timer in ti:
                        with timer:
                            func(**kwargs)
                    results.loc[key, ver] = ti.mean()

        results['speedup_2017_wrt_2017'] = results['2017_old'] / results['2017_new']
        results['speedup_2021_wrt_2017'] = results['2017_old'] / results['2021_new']
        results['speedup_2021_wrt_2021'] = results['2021_old'] / results['2021_new']

        kw2_key = ub.repr2(kw2, nl=0, sep='', nobr=True, explit=1)
        all_results[kw2_key] = results
        print(results)

    means = {key: val.mean(axis=0) for key, val in all_results.items()}
    average_results = sum(means.values()) / len(means)
    print('average_results = {}'.format(ub.repr2(average_results, nl=1)))


if __name__ == '__main__':
    """
    python ~/misc/tests/python/bench_confusion_matrix.py
    python ~/misc/tests/python/bench_confusion_matrix.py --profile
    """
    main()
