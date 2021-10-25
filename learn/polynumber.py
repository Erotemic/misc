"""
TODO:
    Translation, Derivatives, and Subdevatives
    Translating polynumbers and the Derivative | Arithmetic and Geometry Math Foundations 69 | https://www.youtube.com/watch?v=vyRFz8J4Y_M&list=PL5A714C94D40392AB&index=72



L_beta(p) = p(beta + alpha) = p(alpha + beta)
"""
import numpy as np
import fractions
import numbers


class Rational(fractions.Fraction):
    """
    Extension of the Fraction class, mostly to make printing nicer

    >>> 3 * -(Rational(3) / 2)
    """
    def __str__(self):
        if self.denominator == 1:
            return str(self.numerator)
        else:
            return '({}/{})'.format(self.numerator, self.denominator)

    def __repr__(self):
        return str(self)

    def __neg__(self):
        return Rational(super().__neg__())

    def __add__(self, other):
        return Rational(super().__add__(other))

    def __radd__(self, other):
        return Rational(super().__radd__(other))

    def __sub__(self, other):
        return Rational(super().__sub__(other))

    def __mul__(self, other):
        return Rational(super().__mul__(other))

    def __rmul__(self, other):
        return Rational(super().__rmul__(other))

    def __truediv__(self, other):
        return Rational(super().__truediv__(other))

    def __floordiv__(self, other):
        return Rational(super().__floordiv__(other))


def rationalize(data):
    """
    Takes an ndarray and ensures its members are rational

    Example:
        >>> data = ((np.random.rand(3, 5)) * 100)
        >>> rationalize(data)
    """
    if isinstance(data, np.ndarray):
        data = np.vectorize(Rational)(data)
    elif isinstance(data, numbers.Number):
        data = Rational(data)
    else:
        raise TypeError(type(data))
    return data


class PolyNumberV1:
    """
    A PolyNumberV1 as defined by Norman Wildberger

    Coefficients are stored in ascending order of degree, i.e.
    ``c = self.coeff[2]`` is the term for ``c * alpha ** 2``

    References:
        https://www.youtube.com/channel/UCXl0Zbk8_rvjyLwAR-Xh9pQ
    """
    def __init__(self, coeff):
        self.coeff = np.asarray(coeff)

    def __str__(self):
        return 'PolyNumberV1({})'.format(str(self.coeff))

    def __repr__(self):
        return repr(self.coeff).replace('array', 'PolyNumberV1')

    @classmethod
    def coerce(cls, data):
        return cls(np.atleast_1d(np.asarray(data)))

    @classmethod
    def from_degree(cls, degree):
        """ construct the "unary?" polynomial of a certain degree """
        # not sure what to call this
        if degree < 0:
            return cls([0])
        else:
            return cls(([0] * (degree) + [1]))

    def __lshift__(self, places):
        return PolyNumberV1(self.coeff[places:])

    def __rshift__(self, places):
        """
        import timerit
        ti = timerit.Timerit()
        ti.reset('pad').call(lambda: np.pad(self.coeff, (n, 0))).print()
        ti.reset('stack').call(lambda: np.hstack([np.zeros_like(self.coeff, shape=(n)), self.coeff])).print()

        self = PolyNumberV1([1])
        places = 3
        self >> 5
        self << places
        """
        return self.lower_pad(places)

    def lower_pad(self, places):
        left_pad = np.zeros_like(self.coeff, shape=places)
        new_coeff = np.hstack([left_pad, self.coeff])
        return PolyNumberV1(new_coeff)

    def upper_pad(self, places):
        right_pad = np.zeros_like(self.coeff, shape=places)
        new_coeff = np.hstack([self.coeff, right_pad])
        return PolyNumberV1(new_coeff)

    @classmethod
    def random(cls, num_coeff=3, min_coeff=0, max_coeff=21):
        coeff = np.random.randint(min_coeff, max_coeff, size=num_coeff)
        self = cls(coeff)
        return self

    def as_rational(self):
        return PolyNumberV1(np.array(list(map(Rational, self.coeff)), dtype=object))

    def drop_lead_zeros(self):
        nonzero_idxs = np.nonzero(self.coeff)[0]
        if len(nonzero_idxs) > 0:
            d = nonzero_idxs.max() + 1
        else:
            d = 0
        return PolyNumberV1(self.coeff[0:d])

    def copy(self):
        return PolyNumberV1(self.coeff.copy())

    def lead(self):
        """
        Return leading (highest power) coefficient
        """
        if len(self.coeff) > 0:
            return self.coeff[-1]
        else:
            return 0

    def __eq__(self, other):
        p = self.coeff
        q = other.coeff
        n = min(len(p), len(q))
        return np.all(p[0:n] == q[0:n]) and np.all(p[n:] == 0) and np.all(q[n:] == 0)

    def degree(self):
        """
        Number of coefficients

        References:
            https://en.wikipedia.org/wiki/Degree_of_a_polynomial#Degree_of_the_zero_polynomial
        """
        if len(self.coeff) == 0:
            return -float('inf')
        elif self.coeff[-1] != 0:
            return len(self.coeff) - 1
        else:
            return len(self.drop_lead_zeros().coeff) - 1

    def __neg__(self):
        return PolyNumberV1(-self.coeff)

    def __add__(self, other):
        p = self.coeff
        q = other.coeff
        if len(p) > len(q):
            p, q = q, p
        dtype = np.result_type(p, q)
        r = q.copy().astype(dtype)
        r[0:len(p)] += p
        return PolyNumberV1(r)

    def __sub__(self, other):
        return self + (-other)

    def as_polynomial(self):
        """
        Returns the numpy polynomial representation
        """
        return np.polynomial.Polynomial(self.coeff)

    def __mul__(self, other):
        """
        Example:
            self = PolyNumberV1([2, 7, 2, -3]).as_rational()
            other = PolyNumberV1([1, 3]).as_rational()
            result = self * other
            print('result = {!r}'.format(result))

            p1 = self.as_polynomial()
            p2 = other.as_polynomial()
            p3 = p1 * p2
            print('p3 = {!r}'.format(p3))

            divmod(p1, p2)
            divmod(self, other)
        """
        if 0:
            # More efficient
            return PolyNumberV1(np.polymul(self.coeff, other.coeff))
        else:
            # Reasonably efficient
            p = self.coeff
            q = other.coeff

            len_p = len(p)
            len_q = len(q)

            p_basis_idxs = np.arange(len_p)[:, None]
            q_basis_idxs = np.arange(len_q)[None, :]

            r_idxs = (q_basis_idxs + p_basis_idxs).ravel()
            raveled_r_idxs = np.arange(len_p * len_q)
            p_idxs, q_idxs = np.unravel_index(raveled_r_idxs, (len_p, len_q))

            terms = p[p_idxs] * q[q_idxs]

            len_r = (len_p + len_q) - 1
            r = np.zeros(len_r, dtype=terms.dtype)
            np.add.at(r, r_idxs, terms)
            result = PolyNumberV1(r)
            return result

    def __divmod__(self, other):
        """
        Not efficient
        """
        n = self
        d = other
        # https://en.wikipedia.org/wiki/Polynomial_greatest_common_divisor#Euclidean_division
        # https://en.wikipedia.org/wiki/Polynomial_long_division
        zero = PolyNumberV1.coerce(0)
        r = n            # init remainder
        q = zero.copy()  # init quotient (div result)
        shift = r.degree() - d.degree()
        while r != zero and shift >= 0:
            t = PolyNumberV1([(r.lead() / d.lead())]).lower_pad(shift)
            q = q + t
            r = (r - (d * t)).drop_lead_zeros()
            shift = r.degree() - d.degree()
        return (q, r)

    def __truediv__(self, other):
        return divmod(self, other)[0]

    def __mod__(self, other):
        return divmod(self, other)[1]


class PolyNumberNd(PolyNumberV1):
    """
    Generalization of PolyNumbers, BiPolyNumbers, TriPolyNumbers, etc...
    """
    def __init__(self, coeff):
        """
        Args:
            coeff (ndarray): each dimension corresponds to a different poly
                number "variable", i.e. alpha, beta, etc...

        Example:
            >>> import sys, ubelt
            >>> sys.path.append(ubelt.expandpath('~/misc/learn'))
            >>> from polynumber import *  # NOQA
            >>> coeff = rationalize(np.array([
            >>>     [1,   7, 10],
            >>>     [7,  20,  0],
            >>>     [10,  0,  0],
            >>> ]))
            >>> self = PolyNumberNd(coeff)
        """
        self.coeff = coeff


def demo():
    p = PolyNumberV1([2, 7, 2, -3]).as_rational()
    q = PolyNumberV1([1, 3]).as_rational()
    p = PolyNumberV1.random(23).as_rational()
    q = PolyNumberV1.random(20).as_rational()
    self, other = p, q  # NOQA
    r_sum = p + q
    r_sub = p - q
    r_mul = p * q
    r_div, r_rem = divmod(p, q)
    print('r_sub = {!r}'.format(r_sub))
    print('r_sum = {!r}'.format(r_sum))
    print('r_mul = {!r}'.format(r_mul))
    print('r_div = {!r}'.format(r_div))
    print('r_rem = {!r}'.format(r_rem))
    assert (r_div * q + r_rem) == p


def symcheck():
    import sympy as sym
    x = sym.symbols('x')

    a_coeff = sym.symbols(', '.join(['a' + str(i) for i in range(4)]))
    b_coeff = sym.symbols(', '.join(['b' + str(i) for i in range(4)]))

    poly_a = sum(a_i * (x ** i) for i, a_i in enumerate(a_coeff))
    poly_b = sum(b_i * (x ** i) for i, b_i in enumerate(b_coeff))

    poly_c = (poly_a * poly_b).expand().collect(x)

    z = sym.Poly(poly_a) * sym.Poly(poly_b)

    terms = poly_c.as_ordered_terms()
    print(sum(sorted(terms, key=lambda term: term.as_powers_dict().get(x, 0))))


class PolyNumber(np.polynomial.Polynomial):
    """
    Inherit capabilities from numpy Polynomial
    """

    # def __init__(self, coeff):
    #     super().__init__(coeff)
    #     self.coeff = np.asarray(coeff)

    def __str__(self):
        return 'PolyNumber({})'.format(str(self.coef))

    def __repr__(self):
        return repr(self.coef).replace('array', 'PolyNumber')

    @classmethod
    def coerce(cls, data):
        return cls(np.atleast_1d(np.asarray(data)))

    @classmethod
    def random(cls, num_coeff=3, min_coeff=0, max_coeff=21):
        coef = np.random.randint(min_coeff, max_coeff, size=num_coeff)
        self = cls(coef)
        return self

    def as_rational(self):
        return PolyNumber(np.array(list(map(Rational, self.coef)), dtype=object))


def numpy_polynomials():

    # Numpy does not seem to have a polynomial class for N dimensions
    poly_a = PolyNumber([2, 7, 2, -3]).as_rational()
    poly_b = PolyNumber([1, 3]).as_rational()

    prod = poly_a * poly_b
    div, rem = divmod(poly_a, poly_b)

    bipoly_b = PolyNumber(np.array([[1, 0, 1], [0, 0, 0], [1, 0, 0]]))
