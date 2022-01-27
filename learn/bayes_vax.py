pop = 1e6
n_vx = 990e3
n_unvx = 10e3

icu_vx = 50
icu_unvx = 50
icu_num = 100

p_vx = n_vx / pop
p_unvx = n_unvx / pop
p_icu = icu_num / pop

p_vx = 0.99
p_unvx = 0.01
p_icu = 0.0001
p_vx_g_icu = 0.5
p_unvx_g_icu = 0.5
# Good ol' bayes
p_icu_g_vx = p_vx_g_icu * p_icu / p_vx
p_icu_g_unvx = p_unvx_g_icu * p_icu / p_unvx
print(f'p_icu_g_unvx = {100 * p_icu_g_unvx:.6f}%')
print(f'p_icu_g_vx = {100 * p_icu_g_vx:.6f}%')

"""

P(vax) = 0.99
P(unvax) = 0.01

P(icu) = 0.0001

P(vax | icu) = 0.5
P(unvax | icu) = 0.5

# P(A | B) = P(B | A) * P(A) / P(B)

P(icu | vax) = 0.005051%
P(icu | vax) = 0.500000%

"""
