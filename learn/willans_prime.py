"""
https://www.youtube.com/watch?v=j5s0h42GfvM

A formula for prime numbers
"""
import math
import sympy
from functools import cache

def willans_naive(n):
    p = 1 + sum(
        math.floor(
            (n / (
                sum(
                    math.floor(
                        math.cos(
                            math.pi * (math.factorial(j - 1) + 1) / j
                        ) ** 2
                    )
                    for j in range(1, i + 1)
                )
            )) ** (1 / n)
        )
        for i in range(1, (2 ** n) + 1)
    )
    return p


def wilsons_prime_detector(j):
    return (math.factorial(j - 1) + 1) / j

@cache
def j_term(j):
    j_part = wilsons_prime_detector(j)
    cos_part = math.cos(math.pi * j_part)
    return math.floor(cos_part ** 2)

@cache
def i_denom(i):
    return sum(j_term(j) for j in range(1, i + 1))

@cache
def i_term(i, n):
    return math.floor((n / i_denom(i)) ** (1 / n))

def willans_naive_memo(n):
    return 1 + sum(i_term(i, n) for i in range(1, (2 ** n) + 1))


for n in [1, 2, 3, 4, 5]:
    p = willans_naive_v2(n)
    print(f'{n=} {p=}')
    p = willans_naive_memo(n)
    print(f'{n=} {p=}')



import timerit
ti = timerit.Timerit(100, bestof=10, verbose=2)
for timer in ti.reset('willans_naive'):
    with timer:
        willans_naive(n)

for timer in ti.reset('willans_naive_memo'):
    with timer:
        willans_naive_memo(n)


import sympy as sym



@cache
def j_term_sym(j):
    fact_part = sym.factorial(j - 1)
    cos_part = sym.cos(sym.pi * (fact_part + 1) / j)
    return sym.floor(cos_part ** 2)

@cache
def i_denom_sym(i):
    j = sympy.symbols('j')
    return sym.Sum(j_term_sym(j), (j, 1, i))

@cache
def i_term_sym(i, n):
    return sym.floor((n / i_denom_sym(i)) ** (1 / n))

def willans_naive_symbolic(n):
    i = sympy.symbols('i')
    return 1 + sympy.Sum(i_term_sym(i, n), (i, 1, 2 ** n))

nexpr = sympy.symbols('n')
pexpr = willans_naive_symbolic(nexpr)

pexpr.subs({nexpr: 2})

for n in range(1, 9):
    p = (pexpr.subs({nexpr: n})).doit()
    print(f'p={p}')


def is_prime(n):
    """
    Check if the number "n" is prime, with n > 1.

    Returns a boolean, True if n is prime.
    """
    max_val = n ** 0.5
    stop = int(max_val + 1)
    for i in range(2, stop):
        if n % i == 0:
            return False
    return True
