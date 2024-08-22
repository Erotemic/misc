"""
https://www.reddit.com/r/mathmemes/comments/18p86nt/one_can_imagine_sisyphus_happy/

The Taylor series of `sin(x)` about `x=0` is:

```

def term(x, n):
    return (x ^ (2 * n + 1)) * (-1 ** n) / factorial(2n + 1)

sin(x) := ∑ _ {n → ∞} (term(x, n))

```

def McLaurenTerm x:ℝ n:ℕ  :=
    (x ^ (2 * n + 1)) * (-1 ^ n) / (factorial (2n + 1))

theorem sin_x_mclauren x:ℝ:
    Filter.Tendsto
     (fun (k : ℕ) => ∑ n in (range k), McLaurenTerm x n)
     Filter.atTop
     (sin x): by sorry


"""
import sympy
from sympy import factorial
from sympy import sin
from sympy import symbols


def taylor_term(f, x, a, n, evaluate=True):
    """
    The taylor `n`-th series term of function
    `f` with argument `x` about point `a`.
    """
    nth_deriv_of_f = f.diff((x, n))
    numer = nth_deriv_of_f * (x - a) ** n
    with sympy.evaluate(False):
        denom = factorial(n)
    return numer / denom


x = symbols('x')
f = sin(x)
# a = symbols('a')
a = 0

terms = [
    taylor_term(f, x, a, n)
    for n in range(7)
]

approx_f = sum(terms)
sympy.pprint(approx_f)

# with sympy.evaluate(False):
#     sympy.pprint(approx_f.subs({x: 0}))


# Notes
# from sympy import Derivative
# Derivative(f, evaluate=evaluate).subs({x: a})

x = symbols('x')
f = sympy.Function('f')
a = symbols('a')
n = symbols('n')
f_of_x = f(x)
term = taylor_term(f_of_x, x, a, n)
sympy.pprint(term)
taylor_expr = sympy.Sum(term, (n, 0, float('inf')))
sympy.pprint(taylor_expr)

taylor_sin_x = taylor_expr.subs({f_of_x: sin(x)})
sympy.pprint(taylor_sin_x)

taylor_sin_x_at_0 = taylor_expr.subs({f_of_x: sin(x)}).subs({a: 0})
sympy.pprint(taylor_sin_x_at_0)
