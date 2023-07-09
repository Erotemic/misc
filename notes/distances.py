# https://en.wikipedia.org/wiki/Solar_System
import pint

reg = pint.UnitRegistry()
billion = 1_000_000_000


milky_way_diameter   = 105_700 * reg.light_year
heliosphere_diameter = (287_46 * billion * reg.km).to(reg.light_year)
sun_to_earth         = (1 * reg.au).to(reg.light_year)
earth_diameter       = (12_742.5 * reg.km).to(reg.light_year)

a_billion_light_years = 1 * billion * reg.light_year


r = dict()
r['number_milkyways_in_abillionlightyears'] = a_billion_light_years / milky_way_diameter
r['num_solarsystems_in_milkyway'] = milky_way_diameter / heliosphere_diameter
r['num_au_in_solarsystem'] = heliosphere_diameter / sun_to_earth
r['num_earths_in_au'] = sun_to_earth / earth_diameter

import ubelt as ub
print('r = {}'.format(ub.repr2(ub.map_vals(float, r), nl=1, precision=0, align=':', sort=0, si=1)))


def named_large_number(num, prefix='auto', precision=2):
    """
    https://en.wikipedia.org/wiki/Names_of_large_numbers

    Example:
        >>> import sys, ubelt
        >>> sys.path.append(ubelt.expandpath('~/misc/notes'))
        >>> from password_model import *  # NOQA
        >>> import random
        >>> rng = random.Random(0)
        >>> lines = []
        >>> test_mags = (list(range(-10, 3 * 22)) + [3 * 100, 3 * 101, 3 * 102])
        >>> # test_mags = list(range(-1, 3 * 5))
        >>> for mag in test_mags:
        >>>     coef = rng.random()
        >>>     for coef in [1.0, 1.1]:
        >>>         num = coef * (10 ** mag)
        >>>         text = named_large_number(num)
        >>>         line = 'text@{:3d}: {}'.format(mag, text)
        >>>         lines.append(line)
        >>> print('lines = {}'.format(ub.repr2(lines, nl=1), align=' '))
    """
    magnitude_to_prefix = {
        3 *  0: '',
        3 *  1: 'thousand',
        3 *  2: 'million',
        3 *  3: 'billion',
        3 *  4: 'trillion',
        3 *  5: 'quadrillion',
        3 *  6: 'quintillion',
        3 *  7: 'sextillion',
        3 *  8: 'septillion',
        3 *  9: 'octillion',
        3 * 10: 'nonillion',
        3 * 11: 'decillion',
        3 * 12: 'undecillion',
        3 * 13: 'duodectillion',
        3 * 14: 'tredecillion',
        3 * 15: 'quattuor-decillion',
        3 * 16: 'quindecillion',
        3 * 17: 'sexdecillion',
        3 * 18: 'septendecillion',
        3 * 19: 'octodecillion',
        3 * 20: 'novemdecillion',
        3 * 21: 'vigintillion',
        3 * 101: 'centillion',
    }
    prefix_to_magintude = ub.invert_dict(magnitude_to_prefix)
    import math

    num_mag = math.log(abs(float(num) + 1), 10)
    if prefix == 'auto':
        chosen_prefix = ''
        for cand_mag, cand_prefix in magnitude_to_prefix.items():
            if num_mag >= (cand_mag):
                chosen_prefix = cand_prefix
        prefix = chosen_prefix
    mag = prefix_to_magintude[prefix]

    coeff = num / (10 ** mag)
    coef_repr = ub.repr2(float(coeff), precision=precision)
    text = coef_repr + ' ' + prefix
    return text
