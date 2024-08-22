# https://math.stackexchange.com/questions/1678205/derivative-of-a-function-divided-by-the-same-function
from sympy import diff, symbols, Function, log, exp, Derivative
x = symbols('x')
b = symbols('b')
e = exp(1)
f = Function('f')
g = Function('g')

# It is true that
# ∂/∂x ln(x) == 1 / x
assert diff(log(x, e)) == 1 / x
assert diff(log(x, b), x) == 1 / (x * log(b, e))

# The chain rule is
# ((∂ f(g(x))) / (∂x)) == ((∂ f(g(x))) / (∂g(x))) * ((∂ g(x)) / (∂x))
# OR less formally
# given h = f(g(x))
# h'(x) = f'(g(x)) * g'(x)
assert diff(f(g(x)), x) == Derivative(f(g(x)), g(x)) * Derivative(g(x), x)


# We want to prove that
# ((∂f(x))/(∂x)) / f(x) == ((∂log(f(x)))/(∂x))
# The identity is True
lhs = diff(f(x), x) / f(x)
rhs = diff(log(f(x)), x)
assert lhs == rhs

"""
To see this, consider the rhs:

    diff(log(f(x)), x)

Expand this using the chain rule

    diff(log(f(x)), f(x)) * diff(f(x), x)

The left hand part of this simplifies to (1 / f(x))

    1 / f(x) * diff(f(x), x)

Rearrange to

    diff(f(x), x) / f(x)

This is the LHS, thus the LHS is equal to the RHS. QED.
"""
