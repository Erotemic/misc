import numpy as np

# Truncated Gaussian Case
# -----------------------

# Compute the a / b paramters for a Truncated Normal such that all values will be between [low, high]
# Truncated normal curves can have asymetric distances to the left / right of the mean
from scipy.stats import truncnorm
low = -4
high = 20
# Mean and std can be whatever we want
mean = 4.1
std = 3.5
# Convert high and low values to be wrt the standard normal range
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.truncnorm.html
a = (low - mean) / std
b = (high - mean) / std
rv = truncnorm(a=a, b=b, loc=mean, scale=std)


# Show the truncated normal curve we computed
x = np.linspace(-30, 30, 1000)
y = rv.pdf(x)
import kwplot
kwplot.plt.plot(x, y)
ax = kwplot.plt.gca()
ax.set_title('Truncated Normal')


# Pure Gaussian Case
# ------------------

# Pure gaussian derivation
# In this case distances away from the mean must be symmetric

from sympy import symbols, exp, sqrt, pi
sigma, x, eps = symbols('sigma, x, eps')

C = 1 / sqrt(2 * pi)
norm_expr = C * exp(-(x ** 2) / (2 * sigma ** 2))

"""
Derive the formula to compute ``sigma`` given that we want the probability to
drop less than ``epsilon`` after we are ``x`` units away from the mean.

from sympy import symbols, exp, sqrt, pi, ln
C * exp(-(x ** 2) / (2 * sigma ** 2)) < eps

ln(C * exp(-(x ** 2) / (2 * sigma ** 2))) < ln(eps)
ln(C) + ln(exp(-(x ** 2) / (2 * sigma ** 2))) < ln(eps)
ln(C) + -(x ** 2) / (2 * sigma ** 2) < ln(eps)

(ln(C) * (2 * sigma ** 2)) + -(x ** 2) < (ln(eps) * (2 * sigma ** 2))
-(x ** 2) < (ln(eps) * (2 * sigma ** 2)) - (ln(C) * (2 * sigma ** 2))
-(x ** 2) < ((ln(eps) - ln(C)) * (2 * sigma ** 2))
-(x ** 2) < (2 * (ln(eps) - ln(C)) * (sigma ** 2))
-(x ** 2) < 2 * ln(eps / C) * (sigma ** 2)
-(x ** 2) < ln((eps / C) ** 2) * (sigma ** 2)

-(x ** 2) / ln((eps / C) ** 2) < (sigma ** 2)
sqrt(-(x ** 2) / ln((eps / C) ** 2)) < sigma

expr = sympy.simplify(sqrt(-(x ** 2) / ln((eps / C) ** 2)))
print(expr)
rows = []
for eps_ in [0.1, 0.01, 1e-5, 1e-8]:
    for x_ in [1, 3, 5, 9, 20]:
        sigma_ = float(expr.subs({eps: eps_, x: x_}))
        rows.append({'sigma': sigma_, 'x': x_, 'eps': eps_})
import pandas as pd
df = pd.DataFrame(rows)
piv = df.pivot(index='eps', columns='x', values='sigma')
print(piv)

import math
x = 5
eps = 1e-9
math.sqrt(-(x ** 2) / math.log(math.tau * eps ** 2))
"""

norm_expr

from scipy.stats import norm
import math
mean = 4.1

# 5 units from the mean we want the probability to be less than epsilon
distance_from_mean = 20
eps = 1e-17
x = distance_from_mean
std = math.sqrt(-(x ** 2) / math.log(math.tau * eps ** 2))

rv = norm(mean, std)
x = np.linspace(-30, 30, 1000)
y = rv.pdf(x)
import kwplot
kwplot.plt.plot(x, y, label=f'drop<eps at {distance_from_mean} units')
ax = kwplot.plt.gca()
ax.set_title('Normal')

eps = 1e-17
x = distance_from_mean = 5
std = math.sqrt(-(x ** 2) / math.log(math.tau * eps ** 2))
rv = norm(mean, std)
x = np.linspace(-30, 30, 1000)
y = rv.pdf(x)
kwplot.plt.plot(x, y, label=f'drop<eps at {distance_from_mean} units')
ax.legend()
