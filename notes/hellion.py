import math
rnd = int

max_hellion = 90
max_hellbat = 135


def trunc_float(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


def to_hellion(start_hellbat):
    frac = (start_hellbat / max_hellbat)
    frac = trunc_float(frac, 3)
    curr_hellion_f = frac * max_hellion
    curr_hellion = rnd(curr_hellion_f)
    return curr_hellion, curr_hellion_f, frac


def to_hellbat(start_hellion):
    frac = (start_hellion / max_hellion)
    frac = trunc_float(frac, 3)
    curr_hellbat_f = frac * max_hellbat
    curr_hellbat = rnd(curr_hellbat_f)
    return curr_hellbat, curr_hellbat_f, frac


start_hellbat1 = 125
curr_hellion1, curr_hellion_f1, frac1_1 = to_hellion(start_hellbat1)
curr_hellbat1, curr_hellbat_f1, frac2_1 = to_hellbat(curr_hellion1)
print('\n--- case 1 ---')
print('start_hellbat1 = {}'.format(start_hellbat1))
print('curr_hellion1 = {} -> {}'.format(curr_hellion_f1, curr_hellion1))
print('curr_hellbat1 = {} -> {}'.format(curr_hellbat_f1, curr_hellbat1))


start_hellion2 = 80
curr_hellbat2, curr_hellbat_f2, frac1_2 = to_hellbat(start_hellion2)
curr_hellion2, curr_hellion_f2, frac2_2 = to_hellion(curr_hellbat2)
print('\n--- case 2 ---')
print('start_hellion2 = {!r}'.format(start_hellion2))
print('curr_hellbat2 = {} -> {}'.format(curr_hellbat_f2, curr_hellbat2))
print('curr_hellion2 = {} -> {}'.format(curr_hellion_f2, curr_hellion2))
