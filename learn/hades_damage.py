"""
https://docs.google.com/spreadsheets/d/1aHdIl8mx6wB1fysJOtQDEuSlEzL4eD9W50O4XjxxL9o/edit#gid=0
https://docs.google.com/spreadsheets/d/1Py-bKw-IYzFqmsWvN1beBF4YEqU_vkVvB9F4OcVOdg8/edit?usp=sharing
https://www.reddit.com/r/HadesTheGame/comments/jrx6d8/a_spreadsheet_with_updated_values_for_all_boon/
"""
import pint
import ubelt as ub

attack_boons = [
    dict(
        god='Artimis',
        rarity='common',
        crit_chance=0.15,
        extra_damage=0.20,
    ),

    dict(
        god='Artimis',
        rarity='rare',
        crit_chance=0.15,
        extra_damage=0.30,
    ),

    dict(
        god='Artimis',
        rarity='epic',
        crit_chance=0.15,
        extra_damage=0.40,
    ),

    dict(
        god='Artimis',
        rarity='heroic',
        crit_chance=0.15,
        extra_damage=0.50,
    ),

    dict(
        god='Aphrodite',
        rarity='common',
        crit_chance=0.0,
        extra_damage=0.5,
    ),

    dict(
        god='Aphrodite',
        rarity='rare',
        crit_chance=0.0,
        extra_damage=0.75,
    ),

    dict(
        god='Aphrodite',
        rarity='epic',
        crit_chance=0.0,
        extra_damage=1.00,
    ),

    dict(
        god='Aphrodite',
        rarity='heroic',
        crit_chance=0.0,
        extra_damage=1.25,
    ),
]

base = dict(god='Demeter', crit_chance=0)
attack_boons.append(dict(**base, rarity='common', extra_damage=.4))
attack_boons.append(dict(**base, rarity='rare', extra_damage=.6))
attack_boons.append(dict(**base, rarity='epic', extra_damage=.8))
attack_boons.append(dict(**base, rarity='heroic', extra_damage=1.0))


base = dict(god='Poseidon', crit_chance=0)
attack_boons.append(dict(**base, rarity='common', extra_damage=.3))
attack_boons.append(dict(**base, rarity='rare', extra_damage=.45))
attack_boons.append(dict(**base, rarity='epic', extra_damage=.50))
attack_boons.append(dict(**base, rarity='heroic', extra_damage=0.75))

base = dict(god='Athena', crit_chance=0)
attack_boons.append(dict(**base, rarity='common', extra_damage=.3))
attack_boons.append(dict(**base, rarity='rare', extra_damage=.45))
attack_boons.append(dict(**base, rarity='epic', extra_damage=.50))
attack_boons.append(dict(**base, rarity='heroic', extra_damage=0.75))

ureg = pint.UnitRegistry()


def check_sim():
    pp = 0.00
    heart_rend = 1
    base_damage = 150
    # Simulate
    num_attacks = 10000
    import kwarray
    rng = kwarray.ensure_rng(0)

    row = []
    for attack in attack_boons:

        crit_chance = attack['crit_chance']
        crit_chance = crit_chance + pp

        total_damage = 0
        for _ in range(num_attacks):
            crit_flag = rng.rand() < crit_chance
            current_damage = float(base_damage)
            current_damage += current_damage * attack['extra_damage']
            if crit_flag:
                current_damage *= 3
                if heart_rend:
                    current_damage += current_damage * 1.5

            total_damage += int(current_damage)
        average_sim_damage = total_damage / num_attacks

        # Should converge to expected value
        regular_expected = base_damage + base_damage * attack['extra_damage']
        if heart_rend:
            crit_expected = (regular_expected * 3)
            crit_expected = crit_expected + crit_expected * 1.5
        else:
            crit_expected = regular_expected * 3
        expected_damage = (1 - crit_chance) * regular_expected + (crit_chance) * crit_expected

        row.append({
            'god': attack['god'],
            'rarity': attack['rarity'],
            'average_sim_damage': average_sim_damage,
            'expected_damage': expected_damage,
        })

    import pandas as pd
    df = pd.DataFrame(row)
    df = df.sort_values('expected_damage')
    print(df)
    piv = df.pivot(index='god', columns='rarity', values='expected_damage')
    import rich
    piv = piv[['common', 'rare', 'epic', 'heroic']]
    rich.print(piv)

    duration = 5 * ureg.seconds
    damage = 11
    rate = 1 / (0.2 * ureg.seconds)
    pp = 0.02

    ev1 = crit_ev(damage, pp) * rate * duration
    ev2 = crit_ev(damage, pp + 0.01) * rate * duration
    ev3 = crit_ev(damage + 1, pp) * rate * duration
    ev4 = crit_ev(damage, pp + 0.04) * rate * duration
    print(f'ev1={ev1}')
    print(f'ev2={ev2}')
    print(f'ev3={ev3}')
    print(f'ev4={ev4}')


import enum  # NOQA


def crit_ev(damage, crit_chance):
    p = crit_chance
    return (damage * (1 - p)) + (p * damage * 3)


class Rarity(enum.Enum):
    COMMON = 1
    RARE = 2
    EPIC = 3
    HEROIC = 4

    @classmethod
    def coerce(Rarity, data):
        if isinstance(data, str):
            self = Rarity._member_map_[data.upper()]
        elif isinstance(data, Rarity):
            self = data
        else:
            raise TypeError
        return self


class Boon:
    rarity_to_value = {
        Rarity.COMMON: NotImplemented,
        Rarity.RARE: NotImplemented,
        Rarity.EPIC: NotImplemented,
        Rarity.HEROIC: NotImplemented,
    }
    pom_scaling = NotImplemented
    god = NotImplemented

    def __init__(self, rarity='common', augmenters=None, level=0, luck=0):
        self.level = level
        self.rarity = Rarity.coerce(rarity)
        self.augmenters = augmenters
        self.luck = luck

    @property
    def extra_crit(self):
        total = 0
        if not self.augmenters:
            return total
        for aug in self.augmenters:
            if aug.value_type == 'crit_chance':
                total += aug.value
        return total

    @property
    def extra_duration(self):
        total = 0
        if not self.augmenters:
            return total
        for aug in self.augmenters:
            if aug.value_type == 'duration':
                total += aug.value
        return total

    @property
    def base_value(self):
        value = self.rarity_to_value[self.rarity]
        if isinstance(value, tuple):
            lo, hi = value
            value = lo * (1 - self.luck) + hi * self.luck
        return value

    @property
    def pom_value(self):
        last_idx = len(self.pom_scaling) - 2
        stop_idx = self.level
        clipped_stop_idx = min(stop_idx, last_idx)
        remain = stop_idx - clipped_stop_idx
        part1 = sum(self.pom_scaling[:clipped_stop_idx])
        part2 = (self.pom_scaling[last_idx] * remain)
        pom_extra = part1 + part2
        return pom_extra

    @property
    def value(self):
        return self.base_value + self.pom_value


class AttackBoon(Boon):
    base_crit_chance = 0


class SpecialBoon(Boon):
    base_crit_chance = 0


class CastBoon(Boon):
    base_crit_chance = 0


class GlacialGlare(Boon):
    rarity_to_value = {
        Rarity.COMMON: 2.0 * ureg.seconds,
        Rarity.RARE: 2.4 * ureg.seconds,
        Rarity.EPIC: 2.8 * ureg.seconds,
        Rarity.HEROIC: 3.2 * ureg.seconds,
    }
    pom_scaling = [1 * ureg.seconds, ...]
    value_type = 'duration'

    @property
    def duration(self):
        return self.base_value + self.pom_value


class ColdEmbrace(Boon):
    value_type = None

    @property
    def extra_duration(self):
        return 4 * ureg.seconds

    @property
    def extra_damage_percent(self):
        return 0.30


class PressurePoints(Boon):
    rarity_to_value = {
        Rarity.COMMON: 0.02,
        Rarity.RARE: 0.03,
        Rarity.EPIC: 0.04,
        Rarity.HEROIC: 0.05,
    }
    pom_scaling = [0.01, ...]
    value_type = 'crit_chance'
    god = 'Artimis'

    @property
    def crit_chance(self):
        return self.base_value + self.pom_value


class CrystalBeam(CastBoon):
    god = 'Demeter'
    name = 'CrystalBeam'
    rarity_to_value = {
        Rarity.COMMON: 8,
        Rarity.RARE: 9.2,
        Rarity.EPIC: 11.6,
        Rarity.HEROIC: 11.6,
    }
    pom_scaling = [2, 1, ...]

    def __init__(self, rarity=Rarity.COMMON, augmenters=None):
        super().__init__(rarity=rarity, augmenters=augmenters)
        self.base_duration =  5 * ureg.seconds
        self.damage_rate = 1 / (0.2 * ureg.seconds)
        self.rarity = rarity
        self.base_crit_chance = 0

    @property
    def crit_chance(self):
        return self.base_crit_chance + self.extra_crit

    @property
    def base_damage(self):
        return self.base_value

    @property
    def damage(self):
        return self.base_damage + self.pom_value

    @property
    def duration(self):
        return self.base_duration + self.extra_duration

    @property
    def total_damage(self):
        return self.damage * self.damage_rate * self.duration

    @property
    def ev_damage(self):
        p = self.crit_chance
        noncrit_damage = self.damage * (1 - p)
        crit_damage = self.damage * 3
        return  noncrit_damage * (1 - p) + crit_damage * (p)

    @property
    def ev_total_damage(self):
        return (self.ev_damage * self.damage_rate * self.duration).m


def check_crystal_beam():
    pp = PressurePoints(rarity=Rarity.COMMON)
    gg = GlacialGlare(rarity=Rarity.COMMON)
    augmenters = [gg, pp, ColdEmbrace()]
    self = beam = CrystalBeam(rarity=Rarity.EPIC, augmenters=augmenters)
    rows = []

    boons = {
        'beam': beam,
        'gg': gg,
        'pp': pp,
    }

    base_levels = {
        'beam': 1,
        'pp': 0,
        'gg': 0,
    }

    num_poms = 10

    for boon_key in boons.keys():
        boon = boons[boon_key]
        base_level = base_levels[boon_key]
        boon.level = base_level

    for boon_key in boons.keys():
        boon = boons[boon_key]
        base_level = base_levels[boon_key]
        boon.level = base_level

        for level in range(base_level, base_level + num_poms):
            boon.level = level
            rows.append({
                'ev_total_damage': self.ev_total_damage,
                'beam_rarity': beam.rarity,
                'beam_level': beam.level,
                'gg_level': gg.level,
                'gg_rarity': gg.rarity,
                'pp_rarity': pp.rarity,
                'pp_level': pp.level,
                'varied': boon_key,
                'level': level,
            })

        # Reset
        boon.level = base_level

    import pandas as pd
    df = pd.DataFrame(rows)
    import kwplot
    sns = kwplot.autosns()
    sns.lineplot(data=df, x='level', y='ev_total_damage', hue='varied')
    # ax.invert_yaxis()


class PlusMultipler(ub.NiceRepr):
    """
    Represents +X%, which is really the same as *(1+X/100)

    Example:
        self = PlusMultipler(10)
        self * self

    """
    def __init__(self, percent):
        self.percent = percent

    @property
    def factor(self):
        return 1 + (self.percent / 100)

    def __nice__(self):
        return f'+{self.percent}%'

    def _combine(self, other):
        if 1:
            # Optimized calculation
            percent1 = self.percent
            percent2 = other.percent
            new_percent = percent1 * percent2 / 100 + percent1 + percent2
        else:
            # Easier to follow calculation
            factor1 = self.factor
            factor2 = other.factor
            new_factor = (factor1 * factor2)
            new_percent = (new_factor - 1) * 100
        return PlusMultipler(new_percent)

    def __mul__(self, other):
        if isinstance(other, PlusMultipler):
            self._combine(other)
        else:
            return other * self.factor


class HeartbreakFlourish(SpecialBoon):
    rarity_to_value = {
        Rarity.COMMON: 80,
        Rarity.RARE: (104, 120),
        Rarity.EPIC: (144, 160),
        Rarity.HEROIC: (184, 200),
    }
    pom_scaling = [32, 22, 16, 11, 8, ...]
    god = 'Aphrodite'


class HeartbreakStrike(AttackBoon):
    rarity_to_value = {
        Rarity.COMMON: 50,
        Rarity.RARE: (65, 75),
        Rarity.EPIC: (90, 100),
        Rarity.HEROIC: (115, 125),
    }
    pom_scaling = [20, 14, 10, 7, 5, ...]
    god = 'Aphrodite'


class DeadlyStrike(AttackBoon):
    rarity_to_value = {
        Rarity.COMMON: 20,
        Rarity.RARE: (26, 30),
        Rarity.EPIC: (36, 40),
        Rarity.HEROIC: (46, 50),
    }
    base_crit_chance = 0.15
    pom_scaling = [8, 6, 4, 3, 2, ...]
    god = 'Artemis'


def check_rocket_bomb():
    """
    When is worth pomming PP or the Special?
    """
    base_damage = 80
    aphro_lvl4 = PlusMultipler(214)
    aphro_lvl5 = PlusMultipler(225)

    chaos1 = PlusMultipler(52)
    chaos2 = PlusMultipler(45)
    bouldy = PlusMultipler(2)

    pp_lvl1 = PressurePoints(rarity=Rarity.EPIC, level=0)
    pp_lvl2 = PressurePoints(rarity=Rarity.EPIC, level=1)

    (chaos2 * (chaos1 * (aphro_lvl4 * base_damage)))
    (chaos2 * chaos1 * aphro_lvl4 * base_damage)

    option0 = crit_ev(bouldy * (chaos2 * (chaos1 * (aphro_lvl4 * base_damage))), pp_lvl1.crit_chance)
    option1 = crit_ev(bouldy * (chaos2 * (chaos1 * (aphro_lvl5 * base_damage))), pp_lvl1.crit_chance)
    option2 = crit_ev(bouldy * (chaos2 * (chaos1 * (aphro_lvl4 * base_damage))), pp_lvl2.crit_chance)
    print(f'option0={option0}')
    print(f'option1={option1}')
    print(f'option2={option2}')


class Weapon:
    ...


class StygianBlade(Weapon):
    strike = 20
    chop = 25
    thrust = 30
    nova = 50


def check_nemesis_sword():
    """
    Is Aphro or Artemis Higher EV damage on nemesis?
    """
    base_damage = StygianBlade.strike
    crit_chance = 0.30

    rows = []
    for rarity in ['common', 'rare', 'epic']:
        for level in range(0, 10):
            attack1 = DeadlyStrike(rarity, luck=1, level=level)
            attack2 = HeartbreakStrike(rarity, luck=1, level=level)

            mul1 = PlusMultipler(attack1.value)
            mul2 = PlusMultipler(attack2.value)

            value1 = crit_ev(mul1 * base_damage, crit_chance + attack1.base_crit_chance)
            value2 = crit_ev(mul2 * base_damage, crit_chance)
            rows.append({
                'god': attack1.god,
                'rarity': attack1.rarity.name,
                'level': attack1.level,
                'value': value1,
            })
            rows.append({
                'god': attack2.god,
                'rarity': attack2.rarity.name,
                'level': attack2.level,
                'value': value2,
            })
    import pandas as pd
    import rich
    df = pd.DataFrame(rows)

    piv = df.pivot(index=['rarity', 'god'], columns=['level'], values=['value'])
    rich.print(piv)
    import kwplot
    sns = kwplot.autosns()
    sns.lineplot(data=df, x='level', y='value', hue='god', size='rarity')
