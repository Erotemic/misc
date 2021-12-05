"""
Definition of concepts from Wildberger's Foundations of Mathematics



References:
    [MF PlayList] https://www.youtube.com/watch?v=91c5Ti6Ddio&list=PL5A714C94D40392AB

    [MF 123] Affine one-dimensional geometry and the Triple Quad Formula
    https://www.youtube.com/watch?v=8rjxOFAzBa4


    [MF 123] Heron's formula, Archimedes' function, and the TQF
    https://www.youtube.com/watch?v=iMWEiPuFhBQ

    [MF 125] Brahmaguptas Forumla & QQF #1

    [MF 126] Brahmagupta's formula and the Quadruple Quad Formula (II) | Rational Geometry Math Foundations 126

"""
import fractions


def quadrence(p1, p2):
    """
    The squared distance between two points.

    This is a fully rational analog if distance.
    """
    return ((p1 - p2) ** 2).sum()


def quadrea(geom):
    """
    The squared area times 16 the squared area.

    Defined in [MF 126] @ 36:30

    The 16 is included for some "hand-wavy" reason due to relations in related
    to [MF 124] @ 37:00 and archimedes/herons formula.
    """
    return 16 * (geom.area ** 2)


def displacement(a, b):
    """

    References:
        [MF 123 @ 9:58]
    """
    return b - a


class Theorem:
    """
    Can this be a nice API?
    """
    pass


class Eq:
    pass


class TripleQuadForumla(Theorem):
    """
    [MF 123]
    """

    def given(self, a1, a2, a3):
        self.q1 = quadrence(a2, a3)
        self.q2 = quadrence(a1, a3)
        self.q3 = quadrence(a1, a2)

    def claim(self):
        """
        MF 123 @ 18:39
        """
        q1 = self.q1
        q2 = self.q2
        q3 = self.q3
        lhs = (q1 + q2 + q3) ** 2
        rhs = 2 * (q1 ** 2 + q2 ** 2 + q3 ** 3)
        return Eq(lhs, rhs)


def archimedes(q1, q2, q3):
    """
    This is the difference between the lhs and the rhs of the
    TripleQuadForumula.  [MF 124 @ 2:23]

    Given:
        TQF: ((q1 + q2 + q3) ** 2) == (2 * (q1 ** 2 + q2 ** 2 + q3 ** 3))

    Define:
        A(q1, q2, q3) = ((q1 + q2 + q3) ** 2) - (2 * (q1 ** 2 + q2 ** 2 + q3 ** 3))

    Claim:
        A(q1, q2, q3) = 4 * q1 * q2 - (q1 + q2 - q3) ** 2
    """
    return 4 * q1 * q2 - (q1 + q2 - q3) ** 2


class AchimedesForumla:
    """
    [MF 124]
    Rational version of Heron's formula


    The area of a planar triangel with quadrances q1, q2, q3 is given by
    16 * (area ** 2) = A(q1, q2, q3). Where A is :func:`archimedes`.

    A(q1, q2, q3) = 4 * q1 * q2 - (q1 + q2 - q3) ** 2

    [MF 124 @ 37:00]

    """

    def claim(self):
        pass


def quadruple_quad_function(a, b, c, d):
    """
    [MF 125 @ 25:04]
    """
    p1 = ((a + b + c + d) ** 2 - 2 * (a ** 2 + b ** 2 + c ** 2 + d ** 2)) ** 2
    p2 = 64 * a * b * c * d
    return p1 - p2


def quadruple_quad_forumla(a1, a2, a3, a4):
    """
    [MF 125 @ 35:04]
    """
    q = quadrence
    q12 = q(a1, a2)
    q14 = q(a1, a4)
    q23 = q(a2, a3)
    q34 = q(a3, a4)

    # q13 = q(a1, a3)
    # q24 = q(a2, a4)

    q13_numer = (q12 - q23) ** 2 - (q34 - q14) ** 2
    q13_denom = 2 * (q12 + q23 - q34 - q14)
    q13 = q13_numer / q13_denom

    q24_numer = (q23 - q34) ** 2 - (q12 - q14) ** 2
    q24_denom = 2 * (q23 + q34 - q12 - q14)
    q24 = q24_numer / q24_denom

    q13, q24  # if we know 4 quadrences between points we know the other 2


class Rational(fractions.Fraction):
    """
    Extension of the Fraction class, mostly to make printing nicer

    >>> 3 * -(Rational(3) / 2)
    """
    def __str__(self):
        if self.denominator == 1:
            return str(self.numerator)
        else:
            return '{}'.format(self.numerator / self.denominator)
            # return '({}/{})'.format(self.numerator, self.denominator)

    def __json__(self):
        return {
            'type': 'rational',
            'numerator': self.numerator,
            'denominator': self.denominator,
        }

    def __smalljson__(self):
        return '{:d}/{:d}'.format(self.numerator, self.denominator)

    @classmethod
    def coerce(cls, data):
        if isinstance(data, dict):
            return cls.from_json(data)
        elif isinstance(data, int):
            return cls(data, 1)
        elif isinstance(data, str):
            return cls(*map(int, data.split('/')))
        else:
            from PIL.TiffImagePlugin import IFDRational
            if isinstance(data, IFDRational):
                return cls(data.numerator, data.denominator)
            else:
                raise TypeError

    @classmethod
    def from_json(cls, data):
        return cls(data['numerator'], data['denominator'])

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

    @classmethod
    def members(cls, limit=None, zero=True, positive=True, negative=True, maxnumer=None):
        """
        Generate "all" of the rational numbers

        Python implementation of the Gibbons-Lester-Bird algorithm[1] for enumerating
        the positive rationals.

        James Tauber 2004-07-01
        http://jtauber.com/


        Example:
            >>> import sys, ubelt
            >>> sys.path.append(ubelt.expandpath('~/misc/learn'))
            >>> from rational import *  # NOQA
            >>> import itertools as it
            >>> rats = list(it.islice(Rational.members(), 100))
            >>> print('rats = {!r}'.format(rats))
            >>> rats = list(Rational.members(limit=10))
            >>> print('rats = {!r}'.format(rats))

        References:
            [1] http://web.comlab.ox.ac.uk/oucl/work/jeremy.gibbons/publications/rationals.pdf
            [2] https://jtauber.com/blog/2004/07/01/enumerating_the_rationals_in_python/
        """
        import itertools as it
        # generates the positive rationals with no duplicates.
        # ANNOTATED VERSION
        #
        # def proper_fraction((n, d)):
        #     return (n // d, (n % d, d))
        #
        # def reciprocal((n, d)):
        #     return (d, n)
        #
        # def one_take((n, d)):
        #     return (d - n, d)
        #
        # def improper_fraction(i, (n, d)):
        #     return ((d * i) + n, d)
        #
        # def rationals():
        #     r = (0,1)
        #     while True:
        #         n, y = proper_fraction(r)
        #         z = improper_fraction(n, one_take(y))
        #         r = reciprocal(z)
        #         yield r
        if zero:
            yield cls(0, 1)
        numer = 0
        denom = 1
        for _index in it.islice(it.count(0), limit):
            numer, denom = (
                denom,
                ((denom * (numer // denom)) + (denom - (numer % denom)))
            )
            yield cls(numer, denom)

            if negative:
                yield cls(-numer, denom)

    def mediant(self, other):
        return Rational(self.numerator + other.numerator, self.denominator + other.denominator)


def ford_circles():
    """
    Draw Ford Circles

    [MF 14]
    [MF 95]

    [MF 14] https://www.youtube.com/watch?v=83ZjYvkdzYI&list=PL5A714C94D40392AB&index=14
    [MF 95] https://www.youtube.com/watch?v=gATEJ3f3FBM&list=PL5A714C94D40392AB&index=95

    Examples:
        import kwplot
        kwplot.autompl()
    """
    import kwplot
    import ubelt as ub
    plt = kwplot.autoplt()
    sns = kwplot.autosns()  # NOQA

    limit = 256 * 256
    _circles = []
    rationals = []
    rats_to_plot = set()

    def Stern_Brocot(n):
        """
        Another way to iterate over rationals

        References:
            https://stackoverflow.com/questions/24997970/iterating-over-parts-of-the-stern-brocot-tree-in-python
        """
        states = [(0, 1, 1, 1)]
        result = []
        while len(states) != 0:
            a, b, c, d = states.pop()
            if a + b + c + d <= n:
                result.append((a + c, b + d))
                states.append((a, b, a + c, b + d))
                states.append((a + c, b + d, c, d))
        return result

    # import itertools as it  # NOQA
    # _stern_rats = set()
    # for item in Stern_Brocot(limit):
    #     _stern_rats.add(Rational(*item))
    # rats_to_plot |= _stern_rats

    maxx = 1
    _iter = Rational.members(limit=limit)
    _genrat = set(ub.ProgIter(_iter, total=limit, desc='gen rats'))
    rats_to_plot |= _genrat
    rats_to_plot2 = {Rational(r % maxx) for r in rats_to_plot} | {maxx}
    print(f'{len(rats_to_plot)  = }')
    print(f'{len(rats_to_plot2) = }')

    # def stern_brocot(n):
    #     """
    #     References:
    #         https://stackoverflow.com/questions/24997970/iterating-over-parts-of-the-stern-brocot-tree-in-python
    #     """
    #     states = [(0, 1, 1, 1)]
    #     while len(states) != 0:
    #         a, b, c, d = states.pop()
    #         if a + b + c + d <= n:
    #             yield (a + c, b + d)
    #             states.append((a, b, a + c, b + d))
    #             states.append((a + c, b + d, c, d))

    # _iter = Rational.members(limit=limit, maxnumer=8)
    # _genrat = set(ub.ProgIter(_iter, total=limit, desc='gen rats'))

    # def farey_sequence(minval, maxval):
    #     """
    #     """
    #     # def gen_farey_level(prev_level):
    #     #     pass
    #     # rat1 = Rational(0)
    #     # rat2 = Rational(1)
    #     zero = Rational(minval)
    #     one = Rational(maxval)
    #     level = []
    #     while True:
    #         new_middle = [a.mediant(b) for a, b in zip(level[0:-1], level[1:])]
    #         level = [zero] + new_middle + [one]
    #         yield from level

    # # rats_to_plot = _genrat2 | _genrat
    # rats_to_plot = _genrat

    ax = kwplot.figure(fnum=1, doclf=True).gca()
    prog = ub.ProgIter(sorted(rats_to_plot2), verbose=1)
    for rat in prog:
        rationals.append(rat)
        diameter = 1 / (rat.denominator ** 2)
        radius = diameter / 2
        point = (rat, radius)
        # prog.set_extra(f'{rat} {diameter}')
        new_circle = plt.Circle(point, radius, facecolor='none', edgecolor='black', linewidth=1)
        _circles.append(new_circle)
        ax.add_patch(new_circle)

    print(f'{len(rats_to_plot)  = }')
    print(f'{len(rats_to_plot2) = }')

    # import numpy as np
    # points = np.array([c.center for c in _circles])
    # maxx, maxy = points.max(axis=0)
    # print('maxx = {!r}'.format(maxx))
    # print('maxy = {!r}'.format(maxy))
    # maxx, maxy = maxx // 2, maxy // 2
    # ax.set_xlim(0, np.sqrt(int(maxx)))
    # ax.set_ylim(0, np.sqrt(int(maxy)))
    ax.set_aspect('equal')
    ax.set_xlim(0, maxx)
    ax.set_ylim(0, 1)
