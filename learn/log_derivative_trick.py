"""
Understanding the log-derivative trick

https://medium.com/@aminamollaysa/policy-gradients-and-log-derivative-trick-4aad962e43e0
https://andrewcharlesjones.github.io/posts/2020/02/log-derivative/
"""


def demo_log_derivative():
    import sympy
    from sympy import log
    from sympy import Derivative as d
    f = sympy.Function("f", real=True)
    x = sympy.symbols('x')

    # We want to show the equivalence between these cases
    lhs = d(log(f(x)), x)
    rhs = d(f(x), x) / f(x)
    print('lhs = {}'.format(lhs))
    print('rhs = {}'.format(rhs))
    lhs2 = sympy.simplify(lhs)
    rhs2 = sympy.simplify(rhs)
    print('lhs2 = {!r}'.format(lhs2))
    print('rhs2 = {!r}'.format(rhs2))


def demo_derivative_of_log():
    import sympy
    from sympy import log
    from sympy import Derivative as d
    x = sympy.symbols('x')
    # REMEMBER: Derivative of the log function is
    # (d(log(x, b), d)) = (1 / ln(b) * x)
    # (d(log(x, e), d)) = (1 / x)
    lhs = d(log(x))
    rhs = sympy.simplify(lhs)
    print('lhs = {!r}'.format(lhs))
    print('rhs = {!r}'.format(rhs))


def demo_chain_rule():
    import sympy
    x = sympy.symbols('x')
    f = sympy.Function('f')
    g = sympy.Function('g')

    # Derivative of composed functions:
    lhs = sympy.Derivative(f(g(x)), x)

    # Manual expansion of chain rule:
    u = g(x)
    rhs = sympy.Derivative(f(u), u) * sympy.Derivative(g(x), x)

    # Simplification should demonstrate equality
    rhs2 = sympy.simplify(rhs)
    lhs2 = sympy.simplify(lhs)

    print('rhs = {!r}'.format(rhs))
    print('lhs = {!r}'.format(lhs))
    print('rhs2 = {!r}'.format(rhs2))
    print('lhs2 = {!r}'.format(lhs2))
    assert rhs2 == lhs2
