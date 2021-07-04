"""
SeeAlso:
    https://github.com/Legrandin/pycryptodome
    https://github.com/xkortex/passcrux
    https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing
    https://pypi.org/project/pyfinite/
    https://en.wikipedia.org/wiki/Field_(mathematics)
    http://subdevise.com/2018/01/22/Implementing-Shamir-s-Secret-Sharing-in-Python/
    http://www.math.usm.edu/lambers/mat772/fall10/lecture5.pdf
    http://terpconnect.umd.edu/~petersd/666/BarycentricLagrange1.pdf


Ignore:
    pip install pyfinite


Notes:

    A field is a set F, where operations +, -, *, and / are defined, and
        * (F, +) is an abelian group
        * (F - {0}, *) is an abelian group

    A finite field is a field where F has a finite number of elements.

    A basic example of a finite field is the integers module a prime number.
"""


def check_with_pyfinite():
    from pyfinite import ffield
    F = ffield.FField(5)  # create the field GF(2^5)
    a = 7    # field elements are denoted as integers from 0 to 2^5-1
    b = 15
    F.ShowPolynomial(a)  # show the polynomial representation of a


from random import randint
from numpy.polynomial.polynomial import Polynomial, polyval


class LagrangePolynomial(object):
    """
    Given a set of k + 1 unique data points:

    Reference:
        https://en.wikipedia.org/wiki/Lagrange_polynomial

    Example:

        x = [-1,  0, 1, 2]
        y = [ 3, -4, 5, 6]
    """

    @classmethod
    def fit(cls, x, y):

        if 0:
            # scipy version, numerically unstable
            from scipy.interpolate import lagrange
            final = lagrange(x, y)
        if 0:
            # numpy version
            import numpy as np
            x_ = np.array(x)
            x_[:, None] - x_[None, :]
            js, ms = np.triu_indices(len(x), 1)
            x_[js] - x_[ms]
        else:
            import operator as op
            from functools import reduce
            basis_polys = []
            for j, x_j in enumerate(x):
                parts_j = []
                for m, x_m in enumerate(x):
                    if m != j:
                        part_m_j = Polynomial([-1 * x_m, 1]) / (x_j - x_m)
                        parts_j.append(part_m_j)
                basis_j = reduce(op.mul, parts_j, 1)
                basis_polys.append(basis_j)
            final = sum(y_j * basis_j for y_j, basis_j in zip(y, basis_polys))

            if __debug__:
                # Final lagrance polynomial must have this property
                for j in range(len(x)):
                    assert final(x[j]) == y[j]


class FFieldPolynomial(Polynomial):
    """
    A polynomial over a finite integer field (Z mod p)
    """
    def __init__(self, coeff, p):
        super().__init__(coeff)
        self.p = p

    def __call__(self, x):
        accum = 0
        for c in reversed(self.coef):
            accum *= x
            accum += c
            accum %= self.p
        return accum


def _extended_gcd2(a, b):
    """
    Division in integers modulus p means finding the inverse of the
    denominator modulo p and then multiplying the numerator by this
    inverse (Note: inverse of A is B such that A*B % p == 1) this can
    be computed via extended Euclidean algorithm
    http://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Computation

    Example:
        a = 4324
        b = 44
        bezout_x, bezout_y = _extended_gcd2(a, b)

        import math
        math.gcd(a, b)
        a * bezout_x + b * bezout_y

    Returns:
        Bezout coefficients (x, y)
    """
    (old_r, r) = (a, b)
    (old_s, s) = (1, 0)
    (old_t, t) = (0, 1)

    while r != 0:
        quotient = old_r // r
        (old_r, r) = (r, old_r - quotient * r)
        (old_s, s) = (s, old_s - quotient * s)
        (old_t, t) = (t, old_t - quotient * t)

    bezout_x, bezout_y = old_s, old_t
    # gcd_value = old_r
    # import math
    # a_div_gcd = math.copysign(t, a)
    # b_div_gcd = math.copysign(s, a)
    return bezout_x, bezout_y


def _extended_gcd1(a, b):
    curr_numer = a
    curr_denom = b
    curr_x, prev_x = 0, 1
    curr_y, prev_y = 0, 0
    while curr_denom != 0:
        quotient, remainder = divmod(curr_numer, curr_denom)
        curr_numer, curr_denom = curr_denom, remainder
        next_x = (prev_x - quotient * curr_x)
        next_y = (prev_y - quotient * curr_y)
        curr_x, prev_x = next_x, curr_x
        curr_y, prev_y = next_y, curr_y

    # ab_gcd = curr_numer
    bezout_x, bezout_y = prev_x, prev_y
    return bezout_x, bezout_y


def divmod_p(a, b, p):
    """
    Args:
        a (int): numerator
        b (int): denominator
        p (int): prime number of finite-field

    Returns:
        int: c, such that (b * c) % p = a

    Example:
        >>> a = 802
        >>> b = 83
        >>> p = int(2 ** 19 - 1)
        >>> divmod_p(a, b, p)

    """
    # _extended_gcd2(b, p)[0] * a
    # _extended_gcd1(b, p)[0] * a
    inv, _ = _extended_gcd2(b, p)
    return inv * a
    # _extended_gcd()


def ff_lagrange_fit(xs, ys, p):
    """
    Numerically stable lagrange interpolation over finite field (Z mod p)

    Args:
        xs (List[int]): points on the x-axis
        ys (List[int]): corresponding points on the y-axis

    Returns:
        callable: polynomial such that F(xs[i]) == ys[i]

    Given points
    Find the y-value for the given x, given n (x, y) points;
    k points will define a polynomial of up to kth order.

    Example:
        xs = [0, 32, 64]
        ys = [0, 32, 64]
        p = int(2 ** 19 - 1)

        import sympy
        z = sympy.symbols('z')

        lagrange_poly = ff_lagrange_fit(xs, ys, p)
        symbolic = lagrange_poly(z)
    """
    import operator as op
    from functools import reduce

    def prod(vals):
        return reduce(op.mul, vals, 1)

    def eval_lagrange_poly(z):
        """
        Evaluates a lagrange polynomial F, at F(z)
        """
        k = len(xs)
        numers = []
        denoms = []
        for i in range(k):
            others = list(xs)
            x_i = others.pop(i)
            numers.append(prod(z - o for o in others))
            denoms.append(prod(x_i - o for o in others))

        denom_prod = prod(denoms)
        numer_sum = sum(
            divmod_p(y_i * n_i * denom_prod % p, d_i, p)
            for y_i, n_i, d_i in zip(ys, numers, denoms)
        )
        val = divmod_p(numer_sum, denom_prod, p)
        val = (val + p) % p
        return val

    if 0:
        # TODO: it would be nice to have a set of nice pythonic classes
        # for fit lagrange polynomials over (integers mod p)

        def eval_at(z):
            ws = []
            for j, x_j in enumerate(xs):
                left = [x_j - x_k for x_k in xs[:j]]
                right = [x_j - x_k for x_k in xs[j + 1:]]
                winv_j = prod(right) * prod(left)
                # w_j = 1 / winv_j
                w_j = divmod_p(1, winv_j, p)
                ws.append(w_j)
            wys = [w_j * y_j for w_j, y_j in zip(ws, ys)]
            ds = [z - x_j for x_j in xs]

            numer_parts = [
                wy_j / d_j
                for wy_j, d_j in zip(wys, ds)
            ]

            denom_parts = [
                w_j / d_j
                for w_j, d_j in zip(ws, ds)
            ]

            numer = sum(numer_parts)
            denom = sum(denom_parts)

            val = (numer / denom) % p
            print('val = {!r}'.format(val))
            return val

        return eval_at

    return eval_lagrange_poly


class ShamirSecretSpliter(object):
    """
    This class serves as an implementation of Shamir's Secret Sharing scheme,
    which provides methods for managing shared secrets
    """

    def __init__(self, secret, num_shares, min_thresh, prime=None, rng=None):
        """
        secret: secret
        num_shares: total number of shares
        min_thresh: recovery threshold
        prime: prime, where prime > secret and prime > num_shares

        Example:
            secret = 'this is my super secret message'
            num_shares = 6
            min_thresh = 3
            prime = int(2 ** 19 - 1)
            prime = int(2 ** 127 - 1)
            prime = int(2 ** 521 - 1)

        """
        if prime is None:
            prime = int(2 ** 19 - 1)
            prime = int(2 ** 31 - 1)
            prime = int(2 ** 61 - 1)
            prime = int(2 ** 89 - 1)
            prime = int(2 ** 107 - 1)
            prime = int(2 ** 127 - 1)
            prime = int(2 ** 521 - 1)

        import kwarray
        rng = kwarray.ensure_rng(rng, api='python')

        # import nprime
        # nprime.is_prime(prime)

        # Create random tail coefficients and combine with the secret
        # to make the secret polynomial

        secret_int = int.from_bytes(secret.encode(), 'big')

        if secret_int > prime:
            raise ValueError('Must choose a prime bigger than the message')

        tail_coeffs = [rng.randint(1, prime - 1) for _ in range(min_thresh - 1)]
        assert len(set(tail_coeffs)) == len(tail_coeffs), 'must be unique'
        secret_coeffs = [secret_int] + tail_coeffs
        secret_poly1 = Polynomial(secret_coeffs)
        secret_poly2 = FFieldPolynomial(secret_coeffs, prime)

        # Points on this polynomial are the secret shares
        shares1 = [(x, int(secret_poly1(x) % prime)) for x in range(1, num_shares + 1)]
        shares2 = [(x, int(secret_poly2(x) % prime)) for x in range(1, num_shares + 1)]

        # Randomly sample subshares to demo decryption
        shares = shares2
        subshares = rng.sample(shares, k=3)
        xs, ys = list(zip(*subshares))

        recon_poly = ff_lagrange_fit(xs, ys, prime)
        recon = recon_poly(0)
        print('recon = {!r}'.format(recon))

        import math
        length = int((math.log(recon) / math.log(256))) + 1
        recon_bytes = recon.to_bytes(length, 'big')
        recon_text = recon_bytes.decode('utf8')
        print('recon_text = {!r}'.format(recon_text))

        # recon_poly(xs[0])
        # recon_poly(xs[1])

        # Doesn't work, numerically unstable
        # from scipy.interpolate import lagrange
        # recon_poly = lagrange(xs, ys)
        # recon_poly(xs)
        # recon = recon_poly(0)
        # print('recon = {!r}'.format(recon))
        # recon_poly.coeffs[0] % prime
