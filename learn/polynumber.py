import numpy as np
import fractions


class PrettyFraction(fractions.Fraction):
    """
    >>> 3 * -(PrettyFraction(3) / 2)
    """
    def __str__(self):
        if self.denominator == 1:
            return str(self.numerator)
        else:
            return '({}/{})'.format(self.numerator, self.denominator)

    def __repr__(self):
        return str(self)

    def __neg__(self):
        return PrettyFraction(super().__neg__())

    def __add__(self, other):
        return PrettyFraction(super().__add__(other))

    def __radd__(self, other):
        return PrettyFraction(super().__radd__(other))

    def __sub__(self, other):
        return PrettyFraction(super().__sub__(other))

    def __mul__(self, other):
        return PrettyFraction(super().__mul__(other))

    def __rmul__(self, other):
        return PrettyFraction(super().__rmul__(other))

    def __truediv__(self, other):
        return PrettyFraction(super().__truediv__(other))

    def __floordiv__(self, other):
        return PrettyFraction(super().__floordiv__(other))


class PolyNumber:
    """
    A PolyNumber as defined by Norman Wildberger

    Coefficients are stored in ascending order of degree, i.e.
    ``c = self.coeff[2]`` is the term for ``c * alpha ** 2``

    References:
        https://www.youtube.com/channel/UCXl0Zbk8_rvjyLwAR-Xh9pQ
    """
    def __init__(self, coeff):
        self.coeff = np.asarray(coeff)

    def __str__(self):
        return 'PolyNumber({})'.format(str(self.coeff))

    def __repr__(self):
        return repr(self.coeff).replace('array', 'PolyNumber')

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

    @classmethod
    def random(cls, num_coeff=3, min_coeff=0, max_coeff=21):
        coeff = np.random.randint(min_coeff, max_coeff, size=num_coeff)
        self = cls(coeff)
        return self

    def as_rational(self):
        return PolyNumber(np.array(list(map(PrettyFraction, self.coeff)), dtype=object))

    def drop_lead_zeros(self):
        nonzero_idxs = np.nonzero(self.coeff)[0]
        if len(nonzero_idxs) > 0:
            d = nonzero_idxs.max() + 1
        else:
            d = 0
        return PolyNumber(self.coeff[0:d])

    def copy(self):
        return PolyNumber(self.coeff.copy())

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
        return PolyNumber(-self.coeff)

    def __add__(self, other):
        p = self.coeff
        q = other.coeff
        if len(p) > len(q):
            p, q = q, p
        dtype = np.result_type(p, q)
        r = q.copy().astype(dtype)
        r[0:len(p)] += p
        return PolyNumber(r)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        """
        Reasonably efficient
        """
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
        result = PolyNumber(r)
        return result

    def __divmod__(self, other):
        """
        Not efficient
        """
        n = self
        d = other
        # https://en.wikipedia.org/wiki/Polynomial_greatest_common_divisor#Euclidean_division
        # https://en.wikipedia.org/wiki/Polynomial_long_division
        zero = PolyNumber.coerce(0)
        r = n            # init remainder
        q = zero.copy()  # init quotient (div result)
        shift = r.degree() - d.degree()
        while r != zero and shift >= 0:
            y = PolyNumber([(r.lead() / d.lead())])
            t = PolyNumber.from_degree(shift) * y
            q = q + t
            r = (r - (d * t)).drop_lead_zeros()
            shift = r.degree() - d.degree()
        return (q, r)

    def __truediv__(self, other):
        return divmod(self, other)[0]

    def __mod__(self, other):
        return divmod(self, other)[1]


def demo():
    p = PolyNumber([2, 7, 2, -3]).as_rational()
    q = PolyNumber([1, 3]).as_rational()
    p = PolyNumber.random(23).as_rational()
    q = PolyNumber.random(20).as_rational()
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
