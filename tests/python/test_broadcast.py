
# An odd broadcast behavior
import nprime
import numpy as np
import ubelt as ub
primes = list(nprime.generate_primes(100))


# Shapes of [X, 1, Y] and [X, Y] broadcast to [X, X, Y]
a = np.array(primes[0:6]).reshape(3, 1, 2)
b = np.array(primes[6:12]).reshape(3, 2)

c = a * b

c_str = ('c \n{!r}'.format(c))
a_str = ('a \n{!r}'.format(a))
b_str = ('b \n{!r}'.format(b))
print(ub.hzcat([c_str, ' = ', a_str, ' * ', b_str]))
print('c.shape = {!r}'.format(c.shape))
print('a.shape = {!r}'.format(a.shape))
print('b.shape = {!r}'.format(b.shape))

print('\n ---- \n Look at components \n')

# look at components
b_comp = c / a
a_comp = c / b
a_comp_str = ('a_comp \n{!r}'.format(a_comp))
b_comp_str = ('b_comp \n{!r}'.format(b_comp))
print(ub.hzcat([c_str, ' = ', a_comp_str, ' * ', b_comp_str]))

print('c.shape = {!r}'.format(c.shape))
print('b_comp.shape = {!r}'.format(b_comp.shape))
print('a_comp.shape = {!r}'.format(a_comp.shape))


print('\n ---- \n Also Valid and IMO more clear \n')
b_bcast = b[None, :]
c_bcast = a * b_bcast
c_bcast.shape


c_bcast_str = ('c_bcast \n{!r}'.format(c))
b_bcast_str = ('b_bcast \n{!r}'.format(b_bcast))
print(ub.hzcat([c_bcast_str, ' = ', a_str, ' * ', b_bcast_str]))

print('c_bcast.shape = {!r}'.format(c_bcast.shape))
print('a.shape       = {!r}'.format(a.shape))
print('b_bcast.shape = {!r}'.format(b_bcast.shape))

assert np.all(c_bcast == c)
