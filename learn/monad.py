"""
Banging my head against monads again. Attacking it by trying to fully
understand that:

    "a monad is a monoid in the category of endofunctors"


A Category has:
    * Objects (typically sets, but any mathematical object)
    * One or more Morphism (typically associative functions)

    * Can think of as a labeled directed graph where nodes are objects and
      edges are morphisms


Morphism:
    * a morphism associates two objects X and Y
    * they are composable and associative
    * can be thought of as a mapping, or assignment, or drawing an "arrow" or
      "directed edge" between X and Y. Maps elements in X to elements in Y.


Functor (F):

    * Mapping from category C to category D
    * associates object X in C to object F(X) of D
    * associates each morphism f: X -> Y in C to a morphism F(f): F(X) -> F(Y) in Dsuch that
        * F(id_{X}) = id_{F(X)} for X in C                                     # must preserve identity morphisms
        * F(g * f) = F(g) * F(f) for all morphisms f: X -> Y and g: Y -Z in C  # must preserve composition


Endofunctor (F):
    * Functor but C and D are the same category. So...

    * associate objects X in C to F(X) in C.
    * associate morphism f in C to F(f) in C.



Monoid:
    * A set (of at least one identity element) endowed with:

    * exactly one associative binary operation that has an identity

    * the binary op not have an inverse

    * It is a category with one object X and the morphisms from
    # X to X are the elements of the


Any monoid (any algebraic structure with a single associative binary operation
and an identity element)
forms a small category with a single object x. (Here, x is any fixed set.)
The morphisms from x to x are precisely the elements of the monoid,
the identity morphism of x is the identity of the monoid, and the categorical composition of morphisms is given by the monoid operation.



Monad:
    * Is a monoid


Monad (alterantive):
    * a Klesis Tripple (equivalent to the math definition)

    * type consttructor M
    * Type convertor (unit) that embeds an object x in the monad
    * A conninator called bind that unrwaps the object, applies a function (and rewraps the result?)


Adjunction:
    * a pair of functors F and G between categories C and D such that:
    * F: D -> C
    * G: C -> D


Functors F and G are adjoint if:

    F: D -> C
    G: C -> D


Functor category:
    https://en.wikipedia.org/wiki/Functor_category


Class:
    https://en.wikipedia.org/wiki/Class_(set_theory)

    * a class is a collection of sets (or sometimes other mathematical objects)
    that can be unambiguously defined by a property that all its members share

    * Assuming ZFC, then a class is a set of unambiguously definable sets.
      Outside of ZFC, classes may not be sets.

    * A class that is not a set (informally in Zermelo–Fraenkel) is called a proper class


"""


class Category:
    def __init__(self, objects, morphisms):
        self.objects = objects
        self.morphisms = morphisms
