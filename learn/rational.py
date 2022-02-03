"""
Definition of concepts from Wildberger's Foundations of Mathematics


References:
    [MF PlayList] https://www.youtube.com/watch?v=91c5Ti6Ddio&list=PL5A714C94D40392AB

    [MF 103] & [MF 104] Extend rational numbers to include infinity

    [MF 123] Affine one-dimensional geometry and the Triple Quad Formula
    https://www.youtube.com/watch?v=8rjxOFAzBa4


    [MF 123] Heron's formula, Archimedes' function, and the TQF
    https://www.youtube.com/watch?v=iMWEiPuFhBQ

    [MF 125] Brahmaguptas Forumla & QQF #1

    [MF 126] Brahmagupta's formula and the Quadruple Quad Formula (II) | Rational Geometry Math Foundations 126

    [MF 108] - Limits to Infinity
    [MF 109] - Logical difficulties with the modern theory of limits


TODO:
    [MF 130] - Has that rotation + scaling thing I was interested in

"""
import fractions
import math
import numpy as np
import sympy as sym  # NOQA
from kwarray import ensure_rng
import itertools as it


def MF_122_Notes():
    """
    In MF 122 NJW defines:

    Points in an Affine geometry
        A 1-point A = [a] is of type [Rat] or A¹
        A 2-point A = [a1, a2] is of type [Rat²] or A²
        A N-point A = [a1, a2, ..., an] is of type [Ratⁿ] or Aⁿ

    Points in an Projective geometry:
        A 2-proporation is an expression of the form a:b where a and b are
        numbers, not both zero, with the convention that

        a:b = λa:λb, for any non-zero λ

        A projective 1-point is an expression p = [a, b] where
            a:b is a 2-proportion of rational numbers

        We visualize such a projective 1-point as the line 2-dim space through
        the origin and [a,b]

    There is a natural association A=[a] <--> p=[a:1]

    The projective 1-point [1:0] does not correspond to any Affine point, which
    in some sense can play the role of infinity in an extended affine space.

    In other words, let:
        P1 be the set of projective 1 points
        A1 be the set of affine 1 points
        The projective 1 point be ∞ in an affine sense

        P1 = A1 ∪ ∞
    """


def sqrt(data):
    if isinstance(data, np.ndarray):
        return np.sqrt(data)
    elif isinstance(data, sym.Symbol):
        return sym.sqrt(data)
    else:
        return math.sqrt(data)


def distance(p1, p2):
    """
    The distance between two points
    """
    sqrt(quadrence(p1, p2))


def quadrence(p1, p2):
    """
    The squared distance between two points.

    This is a fully rational analog if distance.

    Example:
        >>> p1, p2 = Rational.symbols('a1:3')
        >>> q12 = quadrence(p1, p2)
        >>> print('q12 = {!r}'.format(q12))
        >>> p1, p2 = Rational.random(2)
        >>> q12 = quadrence(p1, p2)
        >>> print('q12 = {!r}'.format(q12))
    """
    return (p1 - p2) ** 2


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
    TODO:
        What is a good structure that automatically

        - [ ] Defines the theorem
        - [ ] Visualizes it
        - [ ] Communicates it
        - [ ] Proves it
        - [ ] Gives examples

    References:
        https://brilliant.org/wiki/triple-quad-formula/

    [MF 123]

    The relationship between the quadrances between three Rational 1-points.

    Note:
        NJW introduces this in terms of affine 1-Points. In this context
        the TQF is true for any 3 rational 1-points. For rational N-points,
        this statement is true iff all 3 N-points are co-linear.

    Example:
        a1, a2, a3 = sorted(Rational.random(3))
        self = TripleQuadForumla()
        self.given(a1, a2, a3)
        claim = self.claim()
        assert sym.simplify(claim)

        import kwplot
        plt = kwplot.autoplt()
        ax = kwplot.figure().gca()
        ax.plot(a1, 0, 'o')
        ax.annotate('a1', (a1, 0))
        ax.plot(a2, 0, 'o')
        ax.annotate('a2', (a2, 0))
        ax.plot(a3, 0, 'o')
        ax.annotate('a3', (a3, 0))

        plt.eventplot(np.array([a1, a2, a3]).astype(float))

        a1, a2, a3 = Rational.symbols('a1:4')
        self = TripleQuadForumla()
        self.given(a1, a2, a3)
        claim = self.claim()
        assert sym.simplify(claim)
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
        rhs = 2 * (q1 ** 2 + q2 ** 2 + q3 ** 2)
        return sym.Eq(lhs, rhs)


def archimedes(q1, q2, q3):
    """
    This is the difference between the lhs and the rhs of the
    TripleQuadForumula.  [MF 124 @ 2:23].

    The TQF is satisfied when this is zero.

    Given:
        TQF: ((q1 + q2 + q3) ** 2) == (2 * (q1 ** 2 + q2 ** 2 + q3 ** 3))

    Define:
        A(q1, q2, q3) = ((q1 + q2 + q3) ** 2) - (2 * (q1 ** 2 + q2 ** 2 + q3 ** 3))

    Claim:
        A(q1, q2, q3) = 4 * q1 * q2 - (q1 + q2 - q3) ** 2
    """
    return 4 * q1 * q2 - (q1 + q2 - q3) ** 2


def herons_forumla(a, b, c):
    """
    Given the side lengths of a triangle, this computes the area of the
    triangle. [MF 124]

    Example:
        >>> triangle = kwimage.Polygon.random(n=3).to_shapely()
        >>> p1, p2, p3 = list(map(shapely.geometry.Point, list(triangle.exterior.coords)[0:3]))
        >>> a = p1.distance(p2)
        >>> b = p1.distance(p3)
        >>> c = p2.distance(p3)
        >>> area = float(herons_forumla(a, b, c))
        >>> assert np.isclose(triangle.area, area)
    """
    s = (a + b + c) / 2  # semi-perimeter
    area = sym.sqrt(s * (s - a) * (s - b) * (s - c))
    return area


class AchimedesForumla:
    """
    [MF 124]
    Rational version of Heron's formula

    The area of a planar triangle with side-quadrances q1, q2, q3 is given by
    16 * (area ** 2) = A(q1, q2, q3). Where A is :func:`archimedes`.

    A(q1, q2, q3) = 4 * q1 * q2 - (q1 + q2 - q3) ** 2

    [MF 124 @ 37:00]

    Example:
        >>> triangle = kwimage.Polygon.random(n=3).to_shapely()
        >>> flt_pts = np.array(list(triangle.exterior.coords)[0:3])
        >>> p1, p2, p3 = np.array(list(map(Rational.coerce, flt_pts.ravel()))).reshape(3, 2)
        >>> q12 = ((p1 - p2) ** 2).sum()
        >>> q13 = ((p1 - p3) ** 2).sum()
        >>> q23 = ((p2 - p3) ** 2).sum()
        >>> triangle_quadrea = archimedes(q12, q13, q23)
        >>> approx_quadrea = 16 * (triangle.area ** 2)
        >>> assert np.isclose(float(approx_quadrea), float(triangle_quadrea))
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


def ptolemys_theorem():
    """
    [MF 131]

    References:
        https://en.wikipedia.org/wiki/Group_of_rational_points_on_the_unit_circle
        https://math.stackexchange.com/questions/845426/rational-points-on-a-surface

    Example:
        >>> # Generate random rational points on a circle - how to?
        >>>
    """


def pythagorean_triples():
    # Pythagorean triples
    _ratiter = Rational.members(negative=False, zero=False)
    for rat in _ratiter:
        m = rat.numerator
        n = rat.denominator
        a = 2 * m * n
        b = m * m - n * n
        c = m * m + n * n
        if a > 0 and b > 0 and c > 0:
            yield a, b, c


def rational_circle_points(num, mode='stereographic', rng=None):
    """
    References:
        https://en.wikipedia.org/wiki/Pythagorean_triple

    Example:
        >>> import kwplot
        >>> plt = kwplot.autoplt()
        >>> points1 = rational_circle_points(16, mode='stereographic')
        >>> points2 = rational_circle_points(16, mode='parametric')
        >>> ax = kwplot.figure(fnum=1, doclf=True).gca()
        >>> ax.plot(points2.T[0], points2.T[1], 'ro', label='parametric')
        >>> ax.plot(points1.T[0], points1.T[1], 'bx', label='stereographic')
        >>> ax.legend()
        >>> ax.set_aspect('equal')
        >>> ax.set_xlim(-1, 1)
        >>> ax.set_ylim(-1, 1)
    """
    import itertools as it
    if mode == 'stereographic':
        points = []
        # Stereographic approach
        _ratiter = Rational.members()
        for rat in it.islice(_ratiter, num):
            m = rat.numerator
            n = rat.denominator
            x = Rational(2 * m * n, m * m + n * n)
            y = Rational(m * m - n * n, m * m + n * n)
            assert (x * x + y * y) == 1
            points.append((x, y))
    elif mode == 'parametric':
        # parametric
        points = []
        for t in it.islice(Integer.members(), num):
            x = Rational((1 - t * t), (1 + t * t))
            y = Rational((2 * t), (1 + t * t))
            assert (x * x + y * y) == 1
            points.append((x, y))
    else:
        raise KeyError(mode)

    def _order_vertices(verts):
        """
        References:
            https://stackoverflow.com/questions/1709283/how-can-i-sort-a-coordinate-list-for-a-rectangle-counterclockwise

        Ignore:
            verts = poly.data['exterior'].data[::-1]
        """
        mean_x = verts.T[0].sum() / len(verts)
        mean_y = verts.T[1].sum() / len(verts)

        delta_x = mean_x - verts.T[0]
        delta_y = verts.T[1] - mean_y

        tau = np.pi * 2
        # Is there a rational version of this?
        angle = (np.arctan2(delta_x.astype(float), delta_y.astype(float)) + tau) % tau
        sortx = angle.argsort()
        verts = verts.take(sortx, axis=0)
        return verts
    points = np.array(points)
    points = _order_vertices(points)
    return points


class Integer(int):

    @classmethod
    def members(cls, zero=True, positive=True, negative=True):
        """
        Example:
            >>> list(it.islice(Integer.members(), 10))
        """
        if zero:
            yield 0
        for index in it.count(1):
            if positive:
                yield index
            if negative:
                yield -index


class Rational(fractions.Fraction):
    """
    Extension of the Fraction class, mostly to make printing nicer

    Example:
        >>> r = 3 * -(Rational(3) / 2)
        >>> Rational.random()
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
        elif isinstance(data, float):
            n, d = data.as_integer_ratio()
            return cls(n, d)
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
        try:
            return Rational(super().__sub__(other))
        except TypeError:
            if isinstance(other, np.ndarray):
                return np.array(self) - other
            else:
                raise

    # def __rsub__(self, other):
    #     return Rational(super().__sub__(other))

    def __mul__(self, other):
        return Rational(super().__mul__(other))

    def __mod__(self, other):
        return Rational(super().__mod__(other))

    def __pow__(self, other):
        return Rational(super().__pow__(other))

    def __rmul__(self, other):
        return Rational(super().__rmul__(other))

    def __truediv__(self, other):
        return Rational(super().__truediv__(other))

    def __floordiv__(self, other):
        return Rational(super().__floordiv__(other))

    # def arctan2(self, other):
    #     return math.atan2(float(self), float(other))

    @classmethod
    def random(cls, size=None, min=None, max=None, rng=None):
        min = np.iinfo(int).min if min is None else min
        max = np.iinfo(int).max if max is None else max
        rng = ensure_rng(rng)
        if size is None:
            n, d = map(int, rng.randint(min, max, size=2))
            return cls(n, d)
        else:
            items = np.empty(size, dtype=Rational)
            ns, ds = rng.randint(min, max, size=(2, items.size))
            items.ravel()[:] = [Rational(int(n), int(d)) for n, d in zip(ns, ds)]
            return items

    @classmethod
    def symbols(cls, names, **kwargs):
        kwargs['rational'] = True
        return sym.symbols(names, **kwargs)

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


def farey_sequence(minval, maxval):
    """
    """
    # def gen_farey_level(prev_level):
    #     pass
    # rat1 = Rational(0)
    # rat2 = Rational(1)
    zero = Rational(minval)
    one = Rational(maxval)
    level = []
    while True:
        new_middle = [a.mediant(b) for a, b in zip(level[0:-1], level[1:])]
        level = [zero] + new_middle + [one]
        yield from level


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


# def float_members(num, min_val=0, max_val=1):
#     # probably dont want to do this like this
#     import numpy as np
#     members = np.linspace(min_val, max_val, limit)
#     yield from members


def ford_circles():
    """
    Draw Ford Circles

    This is a Ford Circle diagram of the Rationals and Float32 numbers.
    Only 163 of the 32608 rationals I generated can be exactly represented by a float32.

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
    import matplotlib as mpl
    plt = kwplot.autoplt()
    sns = kwplot.autosns()  # NOQA

    limit = 256 * 256
    print('limit = {!r}'.format(limit))
    rats_to_plot = set()

    maxx = 1
    _iter = Rational.members(limit=limit)
    _genrat = set(ub.ProgIter(_iter, total=limit, desc='gen rats'))
    rats_to_plot |= _genrat
    rats_to_plot2 = sorted({Rational(r % maxx) for r in rats_to_plot} | {maxx})

    floats = sorted(ub.unique(map(float, rats_to_plot2), key=lambda f: f.as_integer_ratio()))
    print(f'{len(rats_to_plot)  = }')
    print(f'{len(rats_to_plot2) = }')
    print(f'{len(floats)        = }')
    import numpy as np

    ax = kwplot.figure(fnum=1, doclf=True).gca()
    prog = ub.ProgIter(sorted(rats_to_plot2), verbose=1)
    dtype = np.float32
    patches = ub.ddict(list)
    errors = []
    for rat in prog:
        denominator = rat.denominator
        radius = 1 / (2 * (denominator * denominator))
        point = (rat, radius)
        flt = dtype(rat)
        a, b = flt.as_integer_ratio()
        flt_as_rat = Rational(a, b)
        error = abs(rat - flt_as_rat)
        if error == 0:
            new_circle = plt.Circle(point, radius, facecolor='dodgerblue', edgecolor='none', linewidth=0, alpha=0.5)
            patches['good'].append(new_circle)
        else:
            errors.append(error)
            # Plot a line for error
            new_circle = plt.Circle(point, radius, facecolor='orangered', edgecolor='none', linewidth=0, alpha=0.5)
            patches['bad'].append(new_circle)
            ax.plot((rat - error, rat + error), (radius, radius), 'x-', color='darkgray')

    print(ub.map_vals(len, patches))
    total = float(sum(errors))
    print('total = {!r}'.format(total))
    print(max(errors))
    print(min(errors))

    for v in patches.values():
        first = ub.peek(v)
        prop = ub.dict_isect(first.properties(), ['facecolor', 'linewidth', 'alpha', 'edgecolor'])
        col = mpl.collections.PatchCollection(v, **prop)
        ax.add_collection(col)

    # Lets look for the holes in IEEE float
    # for flt in ub.ProgIter(sorted(floats), verbose=1):

    kwplot.phantom_legend({
        f'rationals without a {dtype}': 'orangered',
        f'rationals with a {dtype}': 'dodgerblue',
        f'x-x indicates {dtype} approximation error': 'darkgray',
    })

    ax.set_title('Holes in IEEE 754 Float64')
    ax.set_xlabel('A rational number')
    ax.set_ylabel('The squared rational denominator')

    # import numpy as np
    # points = np.array([c.center for c in _circles])
    # maxx, maxy = points.max(axis=0)
    # print('maxx = {!r}'.format(maxx))
    # print('maxy = {!r}'.format(maxy))
    # maxx, maxy = maxx // 2, maxy // 2
    # ax.set_xlim(0, np.sqrt(int(maxx)))
    # ax.set_ylim(0, np.sqrt(int(maxy)))
    # ax.set_aspect('equal')
    # ax.set_xlim(0.2, 0.22)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 0.1)


def limits_to_infinity():
    r"""
    Limits of rational PolyNumber on-sequences

    If [p(n)> is a rational poly on-seq, and A \in Rat then

    lim(n -> inf)(p(n)) = A  is equivalent to

    we can find k, m \in Nat such that if m <= n then

    (-k / n) <= p(n) - A <= (k / n)

    The above definition is only for infinity,
    https://www.reddit.com/r/mathmemes/comments/sh72iw/its_all_good_until_we_had_to_prove_limits/
    """
