"""
Definition of concepts from Wildberger's Foundations of Mathematics

References:
    [MF 123] Affine one-dimensional geometry and the Triple Quad Formula
    https://www.youtube.com/watch?v=8rjxOFAzBa4


    [MF 123] Heron's formula, Archimedes' function, and the TQF
    https://www.youtube.com/watch?v=iMWEiPuFhBQ

    [MF 125] Brahmaguptas Forumla & QQF #1

    [MF 126] Brahmagupta's formula and the Quadruple Quad Formula (II) | Rational Geometry Math Foundations 126

"""


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
