from collections import defaultdict
from collections.abc import Mapping
from typing import Iterable
import random


def __and__(self: dict, other: Iterable):
    """
    Proposed new "intersection-like" method for dictionaries

    Example:
        >>> self = {'a': 1, 'b': 2}
        >>> other = {'b': 1, 'c': 3}
        >>> __and__(self, other)
    """
    common = self.keys() & other
    return self.__class__((k, self[k]) for k in common)


def __sub__(self: dict, other: Iterable):
    """
    Proposed new "difference-like" method for dictionaries

    Example:
        >>> self = {'a': 1, 'b': 2}
        >>> other = {'b': 1, 'c': 3}
        >>> __sub__(self, other)
    """
    common = self.keys() - other
    return self.__class__((k, self[k]) for k in common)


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
    def __init__(testgen, max_size, rng):
        # Get a list of items that are equal but non-identical
        key_alternatives = []
        for k in range(0, max_size):
            alts = [float(k), int(k)]
            if k in {0, 1}:
                alts.append(bool(k))
            key_alternatives.append(alts)
        testgen.key_alternatives = key_alternatives
        testgen.rng = rng

    def _random_keys(testgen):
        rng = testgen.rng
        # Randomize the number of keys in the RHS and LHS
        size = rng.randint(0, len(testgen.key_alternatives))
        # Randomize the values of the keys in the RHS and LHS
        alts = choice_without_replacement(rng, testgen.key_alternatives, k=size)
        keys = [rng.choice(ks) for ks in alts]
        # Randomize the order of the keys in the RHS and LHS
        rng.shuffle(keys)
        return keys

    def random_lhs(testgen):
        keys1 = testgen._random_keys()
        # Make a random LHS dictionary
        lhs = {k: idx for idx, k in enumerate(keys1)}
        return lhs

    def random_rhs(testgen):
        keys2 = testgen._random_keys()
        # The RHS can be anything iterable, here are some common choices
        rhs_types = [set, list, dict, tuple, mydefaultdict]

        # Make a random RHS iterable
        # Choose some iterable type for the "other" argument
        rhs_type = testgen.rng.choice(rhs_types)
        if issubclass(rhs_type, Mapping):
            rhs = rhs_type((k, idx) for idx, k in enumerate(keys2))
        else:
            rhs = rhs_type(keys2)
        return rhs


def compare_keys(keys, keys_result):
    keys_common = [k for k in keys if k in keys_result]
    is_identical = [k1 is kc for k1, kc in zip(keys, keys_common)]
    is_all_identical = all(is_identical)
    has_order = has_common_order(keys, keys_result)
    status = {
        'size': len(keys),
        'order': has_order,
        'id': is_all_identical,
    }
    return status


def run_test_case(testgen):

    lhs = testgen.random_lhs()
    rhs = testgen.random_rhs()

    # Execute the candidate implementation
    result = __and__(lhs, rhs)

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
        'type_LHS': type(lhs).__name__,
        'type_RHS': type(rhs).__name__,
    }
    return row


def main():
    # Initialize a seeded random number generator
    rng = random.Random(3300082100142)
    max_size = 5
    testgen = TestCaseGenerator(max_size, rng)

    niter = 100
    rows = []
    for _ in range(niter):
        row = run_test_case(testgen)
        rows.append(row)

    import pandas as pd
    df = pd.DataFrame(rows)
    import rich
    rich.print(df.to_string())


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/tests/python/dict_set_discussion.py
    """
    main()
