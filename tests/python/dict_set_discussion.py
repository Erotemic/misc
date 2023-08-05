from collections import defaultdict
from collections.abc import Mapping
from typing import Iterable
import random


class CandidateOperations:
    """
    Container to organize candidate implementations we will test
    """

    def __and_v1__(self: dict, other: Iterable):
        """
        Intersection-like method for dictionaries based on existing key
        intersection

        Baseline __and__ implementation.

        Example:
            >>> self = {'a': 1, 'b': 2}
            >>> other = {'b': 1, 'c': 3}
            >>> __and_v1__(self, other)
        """
        chosen = self.keys() & other
        return self.__class__((k, self[k]) for k in chosen)

    def __and_v2__(self, other):
        """
        Alternative __and__ that preserves LHS order
        """
        chosen = set(self.keys())
        chosen.intersection_update(other)
        new = self.__class__((k, self[k]) for k in self if k in chosen)
        return new

    def __and_v3__(self, other):
        """
        Alternative __and__ that preserves RHS order
        """
        new = self.__class__((k, self[k]) for k in other if k in self)
        return new

    def __and_v4__(self, other):
        """
        Alternative __and__ that preserves LHS order and ID
        """
        chosen = set(self.keys())
        chosen.intersection_update(other)
        new = self.__class__((k, self[k]) for k in self if k in chosen)
        return new

    # ----

    def __sub_v1__(self: dict, other: Iterable):
        """
        Difference-like method for dictionaries based on existing key
        difference.

        Baseline __sub__ implementation.

        Example:
            >>> self = {'a': 1, 'b': 2}
            >>> other = {'b': 1, 'c': 3}
            >>> __sub_v1__(self, other)
        """
        chosen = self.keys() - other
        return self.__class__((k, self[k]) for k in chosen)

    def __sub_v2__(self, other):
        """
        Alternative __sub__ that preserves LHS order
        """
        chosen = set(self.keys())
        chosen.difference_update(other)
        new = self.__class__((k, self[k]) for k in self if k in chosen)
        return new

    def __sub_v3__(self, other):
        """
        Alternative __sub__ that preserves LHS order
        """
        _other = set(other)
        new = self.__class__((k, self[k]) for k, v in self.items() if k not in _other)
        return new


class mydefaultdict(defaultdict):
    """
    Example:
        >>> print(dict(mydefaultdict()))
        >>> print(dict(mydefaultdict(a=1, b=2)))
        >>> print(dict(mydefaultdict({'a': 1, 'b': 2})))
        >>> print(dict(mydefaultdict({})))
    """
    def __init__(self, *args, **kwargs):
        super().__init__(lambda: 'default', *args, **kwargs)


def choice_without_replacement(rng, candidates, k):
    chosen = []
    while len(chosen) != k:
        c = rng.choice(candidates)
        if c not in chosen:
            chosen.append(c)
    return chosen


def has_common_order(items1, items2):
    """
    Check to see if items1 are in the same relative order as items2

    Example:
        >>> has_common_order([2, 3, 5], [1, 2, 3, 4, 5])
        True
        >>> has_common_order([2, 3, 5], [5, 4, 3, 2, 1])
        False
    """
    order_lut1 = {k: idx for idx, k in enumerate(items1)}
    order2 = [order_lut1[k] for k in items2 if k in order_lut1]
    return sorted(order2) == order2


class TestCaseGenerator:
    """
    Generates random data for RHS and LHS of proposed dictionary operation
    """
    def __init__(self, max_size, rng, niter):
        # Get a list of items that are equal but non-identical
        key_alternatives = []
        for k in range(0, max_size):
            alts = [float(k), int(k)]
            if k in {0, 1}:
                alts.append(bool(k))
            key_alternatives.append(alts)
        self.key_alternatives = key_alternatives
        self.rng = rng
        self.niter = niter

    def _random_keys(self):
        rng = self.rng
        # Randomize the number of keys in the RHS and LHS
        size = rng.randint(0, len(self.key_alternatives))
        # Randomize the values of the keys in the RHS and LHS
        alts = choice_without_replacement(rng, self.key_alternatives, k=size)
        keys = [rng.choice(ks) for ks in alts]
        # Randomize the order of the keys in the RHS and LHS
        rng.shuffle(keys)
        return keys

    def random_lhs(self):
        keys1 = self._random_keys()
        # Make a random LHS dictionary
        lhs = {k: idx for idx, k in enumerate(keys1)}
        return lhs

    def random_rhs(self):
        keys2 = self._random_keys()
        # The RHS can be anything iterable, here are some common choices
        # rhs_types = [set, list, dict, tuple, mydefaultdict]
        rhs_types = [set, list, dict, tuple]

        # Make a random RHS iterable
        # Choose some iterable type for the "other" argument
        rhs_type = self.rng.choice(rhs_types)
        if issubclass(rhs_type, Mapping):
            rhs = rhs_type((k, idx) for idx, k in enumerate(keys2))
        else:
            rhs = rhs_type(keys2)
        return rhs

    def next_case(self):
        lhs = self.random_lhs()
        rhs = self.random_rhs()
        return {'lhs': lhs, 'rhs': rhs}

    def __iter__(self):
        for _ in range(self.niter):
            yield  self.next_case()


class ExemplarCaseGenerator:

    def __init__(self):
        self.exemplars = [
            {'rhs': {}, 'lhs': {3.0: 0}},
            {'rhs': [2.0, 0, 4.0, True, 3.0], 'lhs': {False: 0, 3: 1, 2.0: 2, 1.0: 3, 4: 4}},
            {'rhs': (), 'lhs': {}},
            {'rhs': (0,), 'lhs': {4.0: 0}},
            {'rhs': {False, 1, 3}, 'lhs': {False: 0, 1: 1, 2.0: 2, 4: 3, 3.0: 4}},
            {'rhs': {2.0: 0, 4: 1, 1: 2, 0: 3, 3: 4}, 'lhs': {3.0: 0, 4.0: 1, 2: 2, 0.0: 3, True: 4}},
            {'rhs': [4, 2, 0], 'lhs': {0: 0, 2.0: 1, 3: 2, 1: 3, 4: 4}},
            {'rhs': (3, 4, 1.0, 0, 2.0), 'lhs': {0: 0, 3: 1, 4: 2}},
            {'rhs': [2], 'lhs': {}},
            {'rhs': {0, True, 2.0, 3.0, 4}, 'lhs': {True: 0, 3: 1, 2.0: 2, 0: 3, 4: 4}},
            {'rhs': [False, 4, 1.0, 3.0], 'lhs': {2.0: 0, 4: 1, 3.0: 2}},
            {'rhs': {False, 1.0, 2, 3, 4}, 'lhs': {1.0: 0, 2: 1, 4: 2, 3: 3, 0.0: 4}},
            {'rhs': (1.0, 3.0, 4.0, 2.0, False), 'lhs': {False: 0, 4.0: 1, 1.0: 2, 2.0: 3}},
            {'rhs': [3, False, 4.0], 'lhs': {4.0: 0, 1.0: 1, 3: 2}},
            {'rhs': {0, True, 4}, 'lhs': {0: 0, 4.0: 1, 2: 2}},
            {'rhs': (0, 1, 2, 4.0), 'lhs': {0.0: 0, 3.0: 1, 2.0: 2, 4.0: 3}},
            {'rhs': [0, 1.0, 4], 'lhs': {3: 0, 4: 1, 1: 2}},
            {'rhs': {1, 2.0, 3}, 'lhs': {4: 0, 1: 1, 3.0: 2, False: 3, 2.0: 4}},
            {'rhs': (2, 1, False), 'lhs': {1.0: 0, 4.0: 1, 3.0: 2, 2: 3}},
            {'rhs': (2,), 'lhs': {2.0: 0}},
            {'rhs': [0, 4, 2], 'lhs': {2: 0, 3.0: 1, 0: 2}},
            {'rhs': {0.0, 1.0, 2, 3}, 'lhs': {4.0: 0, True: 1, 3.0: 2}},
            {'rhs': {2.0: 0, 3: 1, 1: 2}, 'lhs': {4.0: 0, 1: 1, 2.0: 2, 0: 3}},
            {'rhs': (False, 2.0, 1), 'lhs': {3: 0, False: 1, 4.0: 2, 1: 3}},
            {'rhs': [False, 2, 3], 'lhs': {False: 0, True: 1, 4: 2}},
            {'rhs': {2}, 'lhs': {2.0: 0}},
            {'rhs': {}, 'lhs': {3.0: 0}},
            {'rhs': [2.0, 0, 4.0, True, 3.0], 'lhs': {False: 0, 3: 1, 2.0: 2, 1.0: 3, 4: 4}},
            {'rhs': (), 'lhs': {}},
            {'rhs': (0,), 'lhs': {4.0: 0}},
            {'rhs': {False, 1, 3}, 'lhs': {False: 0, 1: 1, 2.0: 2, 4: 3, 3.0: 4}},
            {'rhs': {2.0: 0, 4: 1, 1: 2, 0: 3, 3: 4}, 'lhs': {3.0: 0, 4.0: 1, 2: 2, 0.0: 3, True: 4}},
            {'rhs': (3, 4, 1.0, 0, 2.0), 'lhs': {0: 0, 3: 1, 4: 2}},
            {'rhs': [2], 'lhs': {}},
            {'rhs': [False, 4, 1.0, 3.0], 'lhs': {2.0: 0, 4: 1, 3.0: 2}},
            {'rhs': (1.0, 3.0, 4.0, 2.0, False), 'lhs': {False: 0, 4.0: 1, 1.0: 2, 2.0: 3}},
            {'rhs': {0, True, 4}, 'lhs': {0: 0, 4.0: 1, 2: 2}},
            {'rhs': (2,), 'lhs': {2.0: 0}},
            {'rhs': (False, 2.0, 1), 'lhs': {3: 0, False: 1, 4.0: 2, 1: 3}},
            {'rhs': {}, 'lhs': {3.0: 0}},
            {'rhs': [2.0, 0, 4.0, True, 3.0], 'lhs': {False: 0, 3: 1, 2.0: 2, 1.0: 3, 4: 4}},
            {'rhs': (), 'lhs': {}},
            {'rhs': (0,), 'lhs': {4.0: 0}},
            {'rhs': {False, 1, 3}, 'lhs': {False: 0, 1: 1, 2.0: 2, 4: 3, 3.0: 4}},
            {'rhs': [4, 2, 0], 'lhs': {0: 0, 2.0: 1, 3: 2, 1: 3, 4: 4}},
            {'rhs': [2], 'lhs': {}},
            {'rhs': {1, 2.0, 3}, 'lhs': {4: 0, 1: 1, 3.0: 2, False: 3, 2.0: 4}},
            {'rhs': {}, 'lhs': {3.0: 0}},
            {'rhs': [2.0, 0, 4.0, True, 3.0], 'lhs': {False: 0, 3: 1, 2.0: 2, 1.0: 3, 4: 4}},
            {'rhs': (), 'lhs': {}},
            {'rhs': (0,), 'lhs': {4.0: 0}},
            {'rhs': {False, 1, 3}, 'lhs': {False: 0, 1: 1, 2.0: 2, 4: 3, 3.0: 4}},
            {'rhs': [2], 'lhs': {}},
        ]

    def __iter__(self):
        yield from iter(self.exemplars)


def compare_keys(keys, keys_result):
    """
    Compare if the input and output keys have the same order and item identity

    Example:
        >>> compare_keys([True], [1])
        {'size': 1, 'order': True, 'id': False}
        >>> compare_keys([1.0, 2.0], [2.0])
        {'size': 2, 'order': True, 'id': True}
        >>> compare_keys([1.0, 2.0, 3.0], [3, 2.0])
        {'size': 3, 'order': False, 'id': False}
    """
    keys_lut1 = dict(zip(keys, keys))
    is_identical = [keys_lut1[k2] is k2 for k2 in keys_result if k2 in keys_lut1]
    is_all_identical = all(is_identical)
    has_order = has_common_order(keys, keys_result)
    status = {
        'size': len(keys),
        'order': has_order,
        'id': is_all_identical,
    }
    return status


def analyze_result(lhs, rhs, result):
    """
    Get information about how the operation output relates to its inputs.
    """
    # Analyze the result
    keys_lhs = list(lhs)
    keys_rhs = list(rhs)
    keys_result = list(result)

    _lhs_comp = compare_keys(keys_lhs, keys_result)
    _rhs_comp = compare_keys(keys_rhs, keys_result)
    lhs_comp = {'LHS_' + k: v for k, v in _lhs_comp.items()}
    rhs_comp = {'RHS_' + k: v for k, v in _rhs_comp.items()}

    row = lhs_comp | rhs_comp | {
        'lhs_keys': keys_lhs,
        'rhs_keys': keys_rhs,
        'result_keys': keys_result,
        'LHS_type': type(lhs).__name__,
        'RHS_type': type(rhs).__name__,
        'rhs': rhs,
        'lhs': lhs,
        'result': result,
    }
    return row


def _group_results(df):
    # Used to generate static examples that cover the main cases.
    import rich
    import pandas as pd
    # Breakup the rows into groups of cases with similar behavior
    # Choose a subset of them as exemplars
    grouper = ['LHS_order', 'LHS_id', 'RHS_order', 'RHS_id']

    FIND_EXEMPLARS = 1
    SHOW_ROWS = 0
    SHOW_KEYS = 0

    if FIND_EXEMPLARS:
        chosen = []

    drop_cols = ['rhs', 'lhs', 'result', 'min', 'mean', 'std']

    if not SHOW_KEYS:
        drop_cols += ['rhs_keys', 'lhs_keys', 'result_keys']

    ave_times = df.groupby('op')[['min', 'mean', 'std']].mean().sort_values('min')

    pd.options.display.multi_sparse = False

    for op, opgroup in df.groupby(['op']):
        parts = []
        print(f'--- {op} ---')
        times = ave_times.loc[[op]]
        rich.print(times)
        grouped = opgroup.groupby(grouper)

        for _, group in grouped:
            to_show = group.drop(drop_cols, axis=1)
            parts.append(to_show)

            if FIND_EXEMPLARS:
                flags = (group['RHS_size'] > 2) & (group['LHS_size'] > 2)
                chosen.extend(flags[flags].index[0:2])
                flags = (group['RHS_size'] == 0) & (group['LHS_size'] == 0)
                chosen.extend(flags[flags].index[0:1])
                flags = (group['RHS_size'] == 0) & (group['LHS_size'] == 1)
                chosen.extend(flags[flags].index[0:1])
                flags = (group['RHS_size'] == 1) & (group['LHS_size'] == 0)
                chosen.extend(flags[flags].index[0:1])
                flags = (group['RHS_size'] == 1) & (group['LHS_size'] == 1)
                chosen.extend(flags[flags].index[0:1])
        if parts:
            rich.print(grouped.size().to_string())
            if SHOW_ROWS:
                combo = pd.concat(parts)
                rich.print(combo.to_string())

    if FIND_EXEMPLARS:
        import ubelt as ub
        chosen = sorted(set(chosen))
        chosen_df = df.loc[chosen]
        # Here is a common case where having & would be really nice!
        __and__ = CandidateOperations.__and_v1__
        exemplars = [__and__(row, {'lhs', 'rhs'})
                     for row in chosen_df.to_dict('records')]
        print('exemplars = {}'.format(ub.urepr(exemplars, nl=1)))
        # list(chosen_df['lhs'].values)
        # list(chosen_df['rhs'].values)

    print('Times:')
    rich.print(ave_times)


def main():
    # Initialize a seeded random number generator

    RANDOMIZE = 1
    if RANDOMIZE:
        # Randonly generate cases
        # rng = random.Random(3300082100142)
        rng = random
        max_size = 100
        niter = 10000
        casegen = TestCaseGenerator(max_size, rng, niter)
        casegen.next_case()
    else:
        # Use pre-defined cases
        casegen = ExemplarCaseGenerator()

    operations = [
        CandidateOperations.__and_v1__,
        CandidateOperations.__and_v2__,
        # CandidateOperations.__and_v3__,
        CandidateOperations.__sub_v1__,
        CandidateOperations.__sub_v2__,
        # CandidateOperations.__sub_v3__,
    ]
    # operations = [v for k, v in CandidateOperations.__dict__.items() if '_v' in k]

    # Test ubelt implementations
    if 0:
        import ubelt as ub
        operations.append(ub.SetDict.intersection)
        operations.append(ub.SetDict.difference)

    # Get the same cases so we can test the same ones for each operation
    fixed_cases = list(casegen)

    # fixed_cases = [
    #     {'lhs': {4: 0, 2.0: 1, False: 2}, 'rhs': {0, True, 3.0, 4}},
    # ]

    import timerit
    ti = timerit.Timerit(100, bestof=10, verbose=0)

    rows = []
    for operation in operations:
        for case in fixed_cases:
            lhs, rhs = case['lhs'], case['rhs']

            time_inst = operation.__name__ + str(case)
            # Execute the candidate implementation
            for timer in ti.reset(time_inst):
                with timer:
                    result = operation(lhs, rhs)

            row = analyze_result(lhs, rhs, result)
            row['op'] = operation.__name__
            row['min'] = ti.min()
            row['mean'] = ti.mean()
            row['std'] = ti.std()
            rows.append(row)

    import pandas as pd
    df = pd.DataFrame(rows)
    _group_results(df)


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/dict_set_discussion.py
    """
    main()
