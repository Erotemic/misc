import numpy as np
import ubelt as ub
from scipy import integrate


class CouponCollector(object):
    """
    Non-uniform coupon collector problem

    Calculate statistics about the number of samples before a ``target``
    fraction of unique events are observed.

    Attributes:
        probs (ndarray): probability mass for each unique item

    Setup:
        Given a finite list of items each with probability p[i], we take S
        samples from sample items without replacement according to the
        probabilities p.

    Questions:
        (1) what is the probability that we sample all items in S samples?

        (2) what is the probability that we sample X% of all items in S
            samples?

        (3) what is the expected value for number of samples S we must take
            before we have sampled X% of all items?

        (4) what is the number of samples S we must draw before there is a p%
            chance that we have sampled X% of all items?

    References:
        https://math.stackexchange.com/questions/489772/probability-of-sampling-with-and-without-replacement
        https://math.stackexchange.com/questions/2735842/expected-samples-to-observe-all-unique-observations
        https://en.wikipedia.org/wiki/Coupon_collector%27s_problem
        https://math.stackexchange.com/questions/699194/non-uniform-coupon-collector
        https://www.combinatorics.org/ojs/index.php/eljc/article/view/v20i2p33/pdf
        https://kainwen.com/2019/08/20/coupon-collectors-problem-a-infinite-series-perspective/
        https://stackoverflow.com/questions/54539128/compute-an-integral-using-scipy-where-the-integrand-is-a-product-with-parameters

        https://math.stackexchange.com/questions/1176813/coupon-collector-problem-for-non-uniform-coupons-on-the-number-of-missed-coupon
        https://mathoverflow.net/questions/198857/coupon-collector-problem-for-non-uniform-coupons-bound-on-the-number-of-missed/198988#198988


    Example:
        >>> # https://www.reddit.com/r/TheSilphRoad/comments/lr5opy/mew_and_the_coupon_collectors_problem/
        >>> num_fast_moves = 14
        >>> num_charge_moves = 25

        >>> self = CouponCollector(np.ones(num_charge_moves) / num_charge_moves)
        >>> self.expected_samples(1.0, method='exact')

        >>> n = num_fast_moves - 1
        >>> self = CouponCollector(np.ones(n) / n)
        >>> p1 = self.expected_samples(1.0, method='exact')
        >>> # Special case for uniform probabilities
        >>> p2 = nth_harmonic(13) * 13
        >>> assert np.isclose(p1, p2)
    """

    def __init__(self, probs):
        self.probs = probs

    def prob_sampled_in(self, target, num_samples, method='approx'):
        """
        Probability of drawing a ``target`` fraction of events in
        ``num_samples``.

        Args:
            target (float): between 0 and 1
            num_samples (int): number of samples drawn

        Returns:
            float : probability

        Example:
            >>> probs = np.ones(4)
            >>> probs = probs / probs.sum()
            >>> self = CouponCollector(probs)
            >>> target = 1.0
            >>> self.prob_sampled_in(target, 8)
        """
        if method == 'approx':
            if target != 1.0:
                raise NotImplementedError('approx method only implemented for target=1')
            import numpy as np
            # Compute the probability that each item was drawn independent of other
            # items.
            t = num_samples
            p_item_drawn = (1 - (1 - self.probs) ** t)
            # Approximate by (incorrectly) assuming independence between these
            # probs.
            p_target_items_drawn = np.prod(p_item_drawn)
        else:
            raise NotImplementedError(method)
        return p_target_items_drawn

    def expected_samples(self, target, method='approx'):
        """
        Args:
            target (float): fraction of events between 0 and 1
            method (str): can be 'approx' or 'montecarlo'.

        Example:
            >>> probs = np.ones(4)
            >>> probs = np.random.rand(int(10000))
            >>> probs = probs / probs.sum()
            >>> self = CouponCollector(probs)
            >>> ev_exact = self.expected_samples(target=1.0, method='exact')
            >>> print('ev_exact = {!r}'.format(ev_exact))
            >>> ev_approx = self.expected_samples(target=1.0, method='approx')
            >>> print('ev_approx = {!r}'.format(ev_approx))
            >>> ev_monte = self.expected_samples(target=1.0, method='montecarlo')
            >>> print('ev_monte = {!r}'.format(ev_monte))
        """
        probs = self.probs

        if method == 'exact':
            if target != 1.0:
                raise NotImplementedError('exact method only implemented for target=1')
            ev = coupon_collector_expected_samples(self.probs)

        if method == 'approx':
            # Theoretical approximation (this is not exactly right)
            def _integrand(t):
                return self.prob_sampled_in(target, t, method=method)
            ev, abserr = integrate.quad(
                func=_integrand,
                a=len(self.probs),  # These bounds are dubious
                b=len(self.probs) ** 2)
            # def func(t):
            #     return (self.prob_sampled_in(target, t) - 0.5) ** 2
            # x0 = len(probs) * np.log(len(probs))
            # import scipy
            # scipy.optimize.newton(func, x0)

        elif method == 'montecarlo':
            ntrials = 100
            timeout = 30
            trails = []
            with ub.Timer() as timer:
                for _ in range(ntrials):
                    remain = set(range(len(probs)))
                    all_items = np.arange(len(probs))
                    n_seen = 0
                    while len(remain):
                        got = np.random.choice(all_items, p=probs)
                        if got in remain:
                            remain.remove(got)
                        n_seen += 1
                        if timer.toc() > timeout:
                            # Limit attempts
                            break
                    trails.append(n_seen)
                    if timer.toc() > 2:
                        # Limit attempts
                        break
            expected_number_samples = np.mean(trails)
            ev = expected_number_samples
        return ev


def coupon_collector_expected_samples(probs):
    """
    Find the expected number of samples before all "coupons" (with a
    non-uniform probability mass) are "collected".

    Args:
        probs (ndarray): probability mass for each unique item

    Returns:
        float : expected number of samples before all events have occurred.

    References:
        https://en.wikipedia.org/wiki/Coupon_collector%27s_problem
        https://www.combinatorics.org/ojs/index.php/eljc/article/view/v20i2p33/pdf
        https://stackoverflow.com/questions/54539128/scipy-integrand-is-product

    Example:
        >>> # Check EV of samples for a non-uniform distribution
        >>> probs = [0.38, 0.05, 0.36, 0.16, 0.05]
        >>> ev = coupon_collector_expected_samples(probs)
        >>> print('ev = {}'.format(ub.repr2(ev, precision=4)))
        ev = 30.6537

        >>> # Use general solution on a uniform distribution
        >>> probs = np.ones(4) / 4
        >>> ev = coupon_collector_expected_samples(probs)
        >>> print('ev = {}'.format(ub.repr2(ev, precision=4)))
        ev = 8.3333

        >>> # Check that this is the same as the solution for the uniform case
        >>> import sympy
        >>> n = len(probs)
        >>> uniform_ev = float(sympy.harmonic(n) * n)
        >>> assert np.isclose(ev, uniform_ev)
    """
    probs = np.asarray(probs)
    # Philippe Flajolet's generalized expected value integral
    def _integrand(t):
        return 1 - np.product(1 - np.exp(-probs * t))
    ev, abserr = integrate.quad(func=_integrand, a=0, b=np.inf)
    return ev


def nth_harmonic(n):
    """
    Example:
        >>> n = 10
        >>> want = float(sympy.harmonic(n))
        >>> got = nth_harmonic(n)
        >>> np.isclose(want, got)
    """
    return np.sum(1 / np.arange(1, n + 1))


def uniform_coupon_ev(n):
    ev = n * nth_harmonic(n)
    return ev


def uniform_coupon_ev_to_collect_k(n, k):
    i = np.arange(n)
    prob_new = (n - i + 1) / n
    ev_new = 1 / prob_new
    ev = np.sum(ev_new[0:k])
    return ev


def bound_ev_coupons_seen(probs, num_samples):
    """
    This seems incorrect, but probably works as a bound

    Args:
        probs: non-uniform probability for each coupon

    References:
        https://math.stackexchange.com/questions/1176813/coupon-collector-problem-for-non-uniform-coupons-on-the-number-of-missed-coupon

    Example:
        >>> probs = np.random.rand(1000)
        >>> probs /= probs.sum()
        >>> num_samples = len(probs)
        >>> bound_ev_coupons_seen(probs, num_samples)
    """
    ev_notseen = ((1 - probs) ** num_samples).sum()
    ev_seen = len(probs) - ev_notseen
    return ev_seen
