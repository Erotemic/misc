"""
Inner Product: scalar similarity measure between two vectors based on angle
Outer Product:

References:
    https://en.wikipedia.org/wiki/Inner_product_space
    https://en.wikipedia.org/wiki/Outer_product
    https://math.stackexchange.com/questions/4183973/intuitive-explanation-of-outer-product

Properties:
    The dot product is the trace of the outer product
"""

import numpy as np
u = np.array([1, 2])[:, None]
v = np.array([3, 4])[:, None]
x = np.array([5, 6])[:, None]

inner = u.T @  v
outer = u @ v.T

# Consider the way the outer product acts on a vector
outer @ x

# Without computing the full outer product, you can
# compute the way it acts on a vector
(u @ v.T) @ x
u @ (v.T @ x)
u * (v.T @ x)

assert np.all(u.T @  v == u.ravel().dot(v.ravel()))
assert np.all(u @  v.T == np.outer(u, v))

# Note: cross product only makes sense in 2 or 3 dimensions
np.cross(np.random.rand(3), np.random.rand(2))
# def project(vec, onto):
#     return (vec.T @ onto) / (onto ** 2).sum() * onto
# project(v, w)
