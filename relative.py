import pint
ureg = pint.UnitRegistry()


def percent_faster(new, old):
    """
    `new` is `percent`% faster than `old`

    Args:
        new (float): measure of time
        old (float): measure of time (with same units as new)

    Returns:
        percent: how much faster `new` is as a percentage of `old`

    References:
        https://stackoverflow.com/questions/8127862/how-do-you-calculate-how-much-faster-time-x-is-from-time-y-in-terms-of
        https://math.stackexchange.com/questions/716767/how-to-calculate-the-percentage-of-increase-decrease-with-negative-numbers/716770#716770

    Notes:
        Equivalent to percent_smaller_than

        new =
        (1 - percent / 100) * old

    Example:
        >>> new = 8.59755
        >>> old = 8.72848
        >>> print('{:.3f}% faster'.format(percent_faster(new, old)))
        1.500% faster
        >>> new = 0.6053
        >>> old = 1.3477
        >>> percent_faster(new, old)
        >>> print('{:.3f}% faster'.format(percent_faster(new, old)))
        55.086% faster
    """
    return percent_smaller_than(new, old)


def percent_smaller_than(new, old):
    """
    `new` is `percent`% smaller than `old`
    """
    percent = percent_decrease(new, old)
    return percent


def percent_decrease(new, old):
    """
    `new` is `percent`% smaller than `old`

    >>> percent_decrease(1, 5)
    80
    >>> percent_decrease(8.6, 8.7)
    1.14
    """
    assert new <= old
    percent = percent_change(new, old)
    return percent


def percent_increase(new, old):
    """
    `new` is `percent`% larger than `old`

    Example:
        >>> percent_increase(5, 1)
        400.0
        >>> percent_increase(8.6, 8.5)
        1.17
    """
    assert new >= old
    percent = -percent_change(new, old)
    return percent


def percent_change(new, old):
    """
    `new` is `old` changed by `percent`

    Notes:
        negative numbers are percent increases
        positive numbers are percent decreases

    Example:
        >>> percent_change(5, 1)
        -400.0
        >>> percent_change(1, 5)
        80.0
    """
    decrease = (old - new)
    frac = decrease / old
    percent = frac * 100.0
    return percent


def percent_slower(new, old):
    """
    `new` is X percent slower than `old`

    Args:
        new (float): measure of time
        old (float): measure of time (with same units as new)

    Returns:
        precent_slower: how much slower `new` is as a percentage of `old`

    Example:
        >>> new = 8.59755
        >>> old = 8.72848
        >>> print('{:.3f}% slower'.format(percent_slower(new, old)))
        1.500% slower
        >>> new = 0.6053
        >>> old = 1.3477
        >>> percent_slower(new, old)
        >>> print('{:.3f}% slower'.format(percent_slower(new, old)))
        55.086% slower
    """
    assert new >= old
    precent_slower = (old - new) / old * 100
    return precent_slower
