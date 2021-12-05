"""
A fact that I like is that base-exp(1) is the most efficient base for encoding
in terms of the number of total distinct states you have to have access to.

To see this, we simply consider the number of nodes in a tree with branching
factor b needed to encode all states at the leaves.

References:
    https://en.m.wikipedia.org/wiki/Radix_economy
    https://en.wikipedia.org/wiki/Ternary_computer
    https://en.wikipedia.org/wiki/Decimal_computer
"""
import numpy as np
import kwplot
import pandas as pd

# amount_of_information = np.arange(10)

amount_of_information = 1_000_000  # we have 1_000_000 bits


base = np.arange(2, 16)

min_base = 2
max_base = 16
base = np.linspace(min_base, max_base, min(100, min_base * (max_base - 2) + 1)).round()
base = np.unique(np.hstack([base, [0.1, 0.2, 0.3, 0.5, 0.8, 0.9, 1.1, 1.5, 1.9, 2.0, 3.0, 8, 10, 16, np.exp(1), np.pi, np.pi * 2]]))
# It doesn't make much sense to have a base < 2, and the analysis of the
# function in this case is out of scope of this tutorial
base = base[base >= 2]
base.sort()

# First let's consider the integer case (as that is what we can actually
# realize with bits)
df = pd.DataFrame({'base': base})
df['tree_height'] = np.log(amount_of_information) / np.log(df['base'])
df['number_of_nodes'] = df['tree_height'] * df['base']


sns = kwplot.autosns()
ax = sns.lineplot(data=df, x='base', y='number_of_nodes', marker='o')
ax.set_title('Nodes in a decision tree with base-b')
