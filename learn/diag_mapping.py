
import sympy as sym
n, t = sym.symbols('n, t')
nth_triangular_number = (n * (n + 1)) / 2
z = sym.Eq(nth_triangular_number, t)
sym.solve(z, n)[1]


n = np.arange(10)
(n * (n + 1)) / 2

t = np.arange(10, dtype=np.float32)
np.floor((np.sqrt(8 * (t - 1) + 1) / 2 - 1 / 2))



import numpy as np

x = np.arange(0, 20)
t = (x * (x + 1)) / 2

t * 2 = x ** 2 + x

x ** 2 + x = t * 2

x * (x + 1) = t * 2


np.sqrt(x).astype(int)

np.tril_indices(10, 2)

i = np.arange(0, 20)
j = np.arange(0, 20)

from itertools import product
N = 10
sorted(product(range(N), range(N)))




N = 5
M = np.zeros((N, N), dtype=int)
i, j = np.triu_indices(N)
x = np.arange(1, len(i) + 1)
M[i, j] = x[::-1]
M = np.fliplr(M)



M = np.zeros((N, N), dtype=int)
p_basis_idxs = np.arange(N)[:, None]
q_basis_idxs = np.arange(N)[None, :]

r_idxs = (q_basis_idxs + p_basis_idxs).ravel()
raveled_r_idxs = np.arange(N * N)
p_idxs, q_idxs = np.unravel_index(raveled_r_idxs, (N, N))
M.ravel()[raveled_r_idxs] = np.arange(len(raveled_r_idxs))



 0,  2,  5,  9, 14,
 1,  4,  8, 13,
 3,  7, 12,
 6, 11,
10,
