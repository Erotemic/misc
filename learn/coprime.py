import nprime
import pandas as pd
import itertools as it
import math
import kwplot
sns = kwplot.sns


def is_coprime(a, b):
    return math.gcd(a, b) == 1


rows = []


N = 50
for i, j in it.product(range(N), range(N)):
    if i >= j:
        _num_prime = nprime.is_prime(i) + nprime.is_prime(j)
        _coprime = is_coprime(i, j)

        if _coprime:
            if _num_prime >= 1:
                label = 'coprime_anyprime'
            else:
                label = 'coprime_composite'
        else:
            label = 'boring'

        rows.append({
            'x': i,
            'y': j,
            'label': label,
        })

df = pd.DataFrame(rows)

sub_df = df[df['label'] == 'coprime_composite']
print(sub_df)
np.unique(sub_df[['x', 'y']].values.ravel())

sns.scatterplot(data=sub_df, x='x', y='y', hue='label')
