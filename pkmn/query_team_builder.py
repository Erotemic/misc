
"""
pip install pypokedex
"""

import ubelt as ub
import re

# azumarill,BUBBLE,ICE_BEAM,PLAY_ROUGH,38,12,15,13

# https://pvpoke.com/custom-rankings/
great_meta = """
abomasnow,POWDER_SNOW,WEATHER_BALL_ICE,ENERGY_BALL
altaria,DRAGON_BREATH,SKY_ATTACK,DRAGON_PULSE
azumarill,BUBBLE,ICE_BEAM,HYDRO_PUMP
bastiodon,SMACK_DOWN,STONE_EDGE,FLAMETHROWER
clefable,CHARM,METEOR_MASH,PSYCHIC
cresselia,PSYCHO_CUT,GRASS_KNOT,MOONBLAST
deoxys_defense,COUNTER,THUNDERBOLT,ROCK_SLIDE
drifblim,HEX,ICY_WIND,SHADOW_BALL
ferrothorn,BULLET_SEED,POWER_WHIP,THUNDER
galvantula,VOLT_SWITCH,DISCHARGE,LUNGE
haunter,SHADOW_CLAW,SHADOW_PUNCH,SHADOW_BALL
hypno,CONFUSION,THUNDER_PUNCH,SHADOW_BALL
hypno_shadow-shadow,CONFUSION,ICE_PUNCH,THUNDER_PUNCH
lapras,ICE_SHARD,SURF,SKULL_BASH
machamp_shadow-shadow,COUNTER,CROSS_CHOP,ROCK_SLIDE
marowak_alolan,FIRE_SPIN,SHADOW_BALL,BONE_CLUB
melmetal,THUNDER_SHOCK,ROCK_SLIDE,SUPER_POWER
munchlax,LICK,BODY_SLAM,BULLDOZE
raichu_alolan,VOLT_SWITCH,THUNDER_PUNCH,WILD_CHARGE
registeel,LOCK_ON,FLASH_CANNON,FOCUS_BLAST
sableye,SHADOW_CLAW,FOUL_PLAY,POWER_GEM
scrafty,COUNTER,POWER_UP_PUNCH,FOUL_PLAY
shiftry,SNARL,LEAF_BLADE,FOUL_PLAY
skarmory,AIR_SLASH,SKY_ATTACK,BRAVE_BIRD
stunfisk,THUNDER_SHOCK,MUD_BOMB,DISCHARGE
stunfisk_galarian,MUD_SHOT,ROCK_SLIDE,EARTHQUAKE
swampert,MUD_SHOT,HYDRO_CANNON,SLUDGE_WAVE
swampert,MUD_SHOT,HYDRO_CANNON,EARTHQUAKE
toxicroak,COUNTER,MUD_BOMB,SLUDGE_BOMB
umbreon,SNARL,FOUL_PLAY,LAST_RESORT
venusaur,VINE_WHIP,FRENZY_PLANT,SLUDGE_BOMB
victreebel_shadow-shadow,RAZOR_LEAF,LEAF_BLADE,SLUDGE_BOMB
vigoroth,COUNTER,BODY_SLAM,BULLDOZE
whiscash,MUD_SHOT,MUD_BOMB,BLIZZARD
wigglytuff,CHARM,ICE_BEAM,PLAY_ROUGH
"""

less_encountered = """
dewgong,ICE_SHARD,ICY_WIND,WATER_PULSE
froslass,POWDER_SNOW,AVALANCHE,SHADOW_BALL
mantine,BUBBLE,BUBBLE_BEAM,ICE_BEAM
medicham,COUNTER,DYNAMIC_PUNCH,ICE_PUNCH
meganium,VINE_WHIP,FRENZY_PLANT,EARTHQUAKE
pelipper,WING_ATTACK,WEATHER_BALL_WATER,HURRICANE
tropius,AIR_SLASH,LEAF_BLADE,AERIAL_ACE
tropius,RAZOR_LEAF,LEAF_BLADE,AERIAL_ACE
zweilous,DRAGON_BREATH,BODY_SLAM,DARK_PULSE
"""


# def pokeapi_query():
#     'https://pogoapi.net/'
#     '/api/v1/current_pokemon_moves.json'

import json
pokemon_stats_fpath = ub.grabdata('https://pogoapi.net/api/v1/pokemon_stats.json')
with open(pokemon_stats_fpath, 'r') as file:
    pokemon_stats_db = json.load(file)
name_to_stats = ub.group_items(pokemon_stats_db, lambda item: item['pokemon_name'].lower())
name_to_stats = dict(name_to_stats)

moves_json_fpath = ub.grabdata('https://pogoapi.net/api/v1/current_pokemon_moves.json')
with open(moves_json_fpath, 'r') as file:
    moves_db = json.load(file)
# name_to_item = {item['pokemon_name'].lower(): item for item in moves_db}
name_to_items = ub.group_items(moves_db, lambda item: item['pokemon_name'].lower())
name_to_items.default_factory = None
name_to_items = dict(name_to_items)
# base = 'http://pokeapi.co/api/v2/pokemon/'


learnable = {
    'stunfisk_galarian': {
        'fast': [
            'MUD_SHOT',
            'METAL_CLAW',
        ],
        'charge': [
            'EARTHQUAKE',
            'FLASH_CANNON',
            'MUDDY_WATER',
            'ROCK_SLIDE',
        ]
    }
}


def calc_cp(attack, defense, stamina, level):
    """
    References:
        https://www.dragonflycave.com/pokemon-go/stats
    """
    cpm_step_lut = {
        0: 0.009426125469,
        10: 0.008919025675,
        20: 0.008924905903,
        30: 0.00445946079,
    }
    cmp_lut = {
        1: 0.094, 1.5: 0.1351374318, 2: 0.16639787, 2.5: 0.192650919, 3: 0.21573247,
        3.5: 0.2365726613, 4: 0.25572005, 4.5: 0.2735303812, 5: 0.29024988, 5.5: 0.3060573775,
        6: 0.3210876, 6.5: 0.3354450362, 7: 0.34921268, 7.5: 0.3624577511, 8: 0.3752356,
        8.5: 0.387592416, 9: 0.39956728, 9.5: 0.4111935514, 10: 0.4225, 10.5: 0.4329264091,
        11: 0.44310755, 11.5: 0.4530599591, 12: 0.4627984, 12.5: 0.472336093, 13: 0.48168495, 13.5: 0.4908558003,
        14: 0.49985844, 14.5: 0.508701765, 15: 0.51739395, 15.5: 0.5259425113, 16: 0.5343543, 16.5: 0.5426357375,
        17: 0.5507927, 17.5: 0.5588305862, 18: 0.5667545, 18.5: 0.5745691333, 19: 0.5822789, 19.5: 0.5898879072,
        20: 0.5974, 20.5: 0.6048236651, 21: 0.6121573, 21.5: 0.6194041216, 22: 0.6265671, 22.5: 0.6336491432,
        23: 0.64065295, 23.5: 0.6475809666, 24: 0.65443563, 24.5: 0.6612192524, 25: 0.667934, 25.5: 0.6745818959,
        26: 0.6811649, 26.5: 0.6876849038, 27: 0.69414365, 27.5: 0.70054287, 28: 0.7068842, 28.5: 0.7131691091,
        29: 0.7193991, 29.5: 0.7255756136, 30: 0.7317, 30.5: 0.7347410093, 31: 0.7377695,
        31.5: 0.7407855938, 32: 0.74378943, 32.5: 0.7467812109, 33: 0.74976104, 33.5: 0.7527290867,
        34: 0.7556855, 34.5: 0.7586303683, 35: 0.76156384, 35.5: 0.7644860647, 36: 0.76739717,
        36.5: 0.7702972656, 37: 0.7731865, 37.5: 0.7760649616, 38: 0.77893275, 38.5: 0.7817900548,
        39: 0.784637, 39.5: 0.7874736075, 40: 0.7903, 41: 0.79530001, 42: 0.8003, 43: 0.8053,
        44: 0.81029999, 45: 0.81529999,
    }
    # cpm_step = cpm_step_lut[(level // 10) * 10]
    # cpm_step
    cp_multiplier = cmp_lut[level]

    # https://gamepress.gg/pokemongo/cp-multiplier
    # https://gamepress.gg/pokemongo/pokemon-stats-advanced#:~:text=Calculating%20CP,*%20CP_Multiplier%5E2)%20%2F%2010
    a, d, s = attack, defense, stamina

    adjusted = {
        'attack': a * cp_multiplier,
        'defense': d * cp_multiplier,
        'stamina': int(s * cp_multiplier),
    }
    cp = int(a * (d ** 0.5) * (s ** 0.5) * (cp_multiplier ** 2) / 10)
    return cp, adjusted


# class Moves():
#     def __init__(moves):
#         pass
#     pass


class Pokemon(ub.NiceRepr):
    """

    Example:
        import sys, ubelt
        sys.path.append(ubelt.expandpath('~/misc/pkmn'))
        from query_team_builder import *  # NOQA
        self = Pokemon('beedrill')

    """
    def __init__(self, name, level=None, ivs=None, moves=None, shadow=False,
                 form='Normal'):
        self.name = name
        self.level = level
        self.ivs = ivs
        self.moves = moves
        self.shadow = shadow
        if shadow:
            form = 'Shadow'
        self.form = form

    def lookup_moves(self):
        possible_moves = name_to_items[self.name]
        return possible_moves

    def populate_stats(self):
        self.form
        try:
            items = name_to_items[self.name]
            all_stats = name_to_stats[self.name]
            form = 'Normal'
        except Exception:
            if self.name.endswith('galarian'):
                form = 'Galarian'
                name = self.name.split('_galarian')[0]
                if name == 'farfetchd':
                    name = "farfetch\u2019d"
                all_stats = name_to_stats[name]
                items = name_to_items[name]
            else:
                raise
        for _stats in all_stats:
            if _stats['form'] == form:
                stats = _stats

        fast_moves = set()
        charge_moves = set()

        def normalize(n):
            return n.upper().replace(' ', '_')

        for item in items:
            if form == 'Galarian':
                if item['form'] != form:
                    continue

            for move in item['fast_moves']:
                fast_moves.add(normalize(move))
            for move in item['elite_fast_moves']:
                fast_moves.add(normalize(move))
            for move in item['charged_moves']:
                charge_moves.add(normalize(move))
            for move in item['elite_charged_moves']:
                charge_moves.add(normalize(move))

            if form == 'Normal':
                if item['form'] == 'Shadow':
                    charge_moves.add('FRUSTRATION')
                    charge_moves.add('RETURN')

            # if item['form'] == form:
            #     found = item
        if self.name not in learnable:
            learnable[self.name] = {}

        learnable[self.name]['fast'] = sorted(fast_moves)
        learnable[self.name]['charge'] = sorted(charge_moves)

        self.learnable = learnable[self.name]
        self.stats = stats
        # self.items = items

    def find_leage_rankings(self, max_cp=1500):
        """
        Calculate the leage rankings for this pokemon's IVs, based on the
        adjusted stat product heuristic.

        Ignore:
            >>> import sys, ubelt
            >>> sys.path.append(ubelt.expandpath('~/misc/pkmn'))
            >>> from query_team_builder import *  # NOQA
            >>> self = Pokemon('beedrill')
            >>> self.populate_stats()
            >>> beedrill_df = self.find_leage_rankings(max_cp=1500)

            >>> self = Pokemon('empoleon')
            >>> self.populate_stats()
            >>> empoleon_ultra_df = self.find_leage_rankings(max_cp=2500)
            >>> empoleon_greak_df = self.find_leage_rankings(max_cp=1500)

        """
        rows = []
        import itertools as it
        import numpy as np

        for iva, ivd, ivs in it.product(range(16), range(16), range(16)):
            attack = self.stats['base_attack'] + iva
            defense = self.stats['base_defense'] + ivd
            stamina = self.stats['base_stamina'] + ivs

            best_level = None
            best_cp = None
            best_adjusted = None
            for level in np.arange(1, 45, 0.5):
                cand_cp, adjusted = calc_cp(attack, defense, stamina, level)
                if cand_cp <= max_cp:
                    best_cp = cand_cp
                    best_level = level
                    best_adjusted = adjusted
                else:
                    break

            row = {
                'iva': iva,
                'ivd': ivd,
                'ivs': ivs,
                'cp': best_cp,
                'level': best_level,
                'attack': best_adjusted['attack'],
                'defense': best_adjusted['defense'],
                'stamina': best_adjusted['stamina'],
            }
            rows.append(row)

        import kwarray
        df = kwarray.DataFrameArray.from_dict(rows)
        df = df.pandas()
        df['stat_product'] = (df['attack'] * df['defense'] * df['stamina']) / 1000
        df = df.sort_values('stat_product', ascending=False)
        df['rank'] = np.arange(1, len(df) + 1)
        df = df.set_index('rank')
        return df

    def calc_cp(self):
        if self.level is None:
            best_cp = 0
            best_level = 0
            # levels = [y + x for x in range(1, 45) for y in [0, 0.5]]
            for level in range(1, 45):
                iva, ivd, ivs = self.ivs
                if iva is None:
                    iva = 10
                if ivd is None:
                    ivd = 10
                if ivs is None:
                    ivs = 10
                attack = self.stats['base_attack'] + iva
                defense = self.stats['base_defense'] + ivd
                stamina = self.stats['base_stamina'] + ivs
                cand_cp = calc_cp(attack, defense, stamina, level)
                if cand_cp > 1500:
                    break
                best_cp = cand_cp
                best_level = level
                print('best_cp = {!r}'.format(best_cp))
                print('best_level = {!r}'.format(best_level))

        level = self.level
        iva, ivd, ivs = self.ivs
        attack = self.stats['base_attack'] + iva
        defense = self.stats['base_defense'] + ivd
        stamina = self.stats['base_stamina'] + ivs
        cp, adjusted = calc_cp(attack, defense, stamina, level)
        return cp

    def __nice__(self):
        info = '{}, {}, {}, {}'.format(self.name, self.moves, self.level, self.ivs)
        return info
        # return str([self.name] + self.moves + [self.level] + self.ivs)

    @classmethod
    def from_pvpoke_row(cls, row):
        """
        Example:
            from query_team_builder import *  # NOQA
            row = 'victreebel_shadow-shadow,RAZOR_LEAF,LEAF_BLADE,FRUSTRATION,22.5,4,14,14'
            self = Pokemon.from_pvpoke_row(row)
        """
        name = row[0]
        shadow = False
        if name.endswith('-shadow'):
            name = name.split('-shadow')[0]
            # weird case for victreebel
            if name.endswith('_shadow'):
                name = name.split('_shadow')[0]
            shadow = True
        level = None
        ivs = [None, None, None]

        moves = []
        idx = 0
        for idx in range(1, 4):
            if idx >= len(row):
                break
            if not re.match('[a-z]+', row[idx].lower()):
                break
            moves.append(row[idx])
        idx += 1
        if idx < len(row):
            level = float(row[idx])
        idx += 1
        if idx < len(row):
            ivs = list(map(int, row[idx:]))
        self = cls(name, level, ivs, moves, shadow=shadow)
        return self

    def to_pvpoke_url(self):
        parts = []
        parts.append(self.name)
        if self.level is not None:
            parts.append(str(self.level))

        needs_441 = False

        if self.ivs and all(v is not None for v in self.ivs):
            parts.extend(list(map(str, self.ivs)))
            needs_441 = True
        if self.shadow:
            parts.append('shadow')
            needs_441 = True

        if needs_441:
            parts.append('4-4-1')  # no idea what this is

        if self.moves:
            parts.append('m')
            moves = self.moves + ([None] * max(0, 3 - len(self.moves)))
            fm, cm1, cm2 = moves

            fixup = {
                'FUTURE_SIGHT': 'FUTURESIGHT',
            }
            cm1 = fixup.get(cm1, cm1)
            cm2 = fixup.get(cm2, cm2)

            fm_idx = learnable[self.name]['fast'].index(fm)
            cm1_idx = learnable[self.name]['charge'].index(cm1) + 1
            parts.append(str(fm_idx))
            parts.append(str(cm1_idx))
            if cm2 is not None:
                if cm2.lower() == 'frustration':
                    # hack for frustration
                    cm2_idx = 0
                else:
                    cm2_idx = learnable[self.name]['charge'].index(cm2) + 1
                parts.append(str(cm2_idx))
        else:
            parts.append('m-1-1-2')

        # parts.append(self.moves[0])
        # parts.append(self.moves[1])
        # parts.append('0')
        # parts.append(self.moves[2])
        # parts.append('1')
        # need a lut
        # for move in self.moves:
        #     pass
        code = '-'.join(parts)
        return code


def main():
    mode = 'great'
    if mode == 'great':
        candidate_csv_text = ub.codeblock(
            '''
            registeel,LOCK_ON,FLASH_CANNON,FOCUS_BLAST,22,10,14,15
            stunfisk_galarian,MUD_SHOT,ROCK_SLIDE,EARTHQUAKE,25,11,14,14
            # altaria,DRAGON_BREATH,SKY_ATTACK,DRAGON_PULSE,26.5,14,12,13

            skarmory,AIR_SLASH,SKY_ATTACK,FLASH_CANNON,26,11,13,10

            azumarill,BUBBLE,ICE_BEAM,HYDRO_PUMP,38,12,15,13
            dewgong,ICE_SHARD,ICY_WIND,WATER_PULSE,26.5,15,08,15

            # umbreon,SNARL,FOUL_PLAY,LAST_RESORT,24.5,15,10,15
            # farfetchd_galarian,FURY_CUTTER,LEAF_BLADE,BRAVE_BIRD,33.5,12,15,15

            hypno,CONFUSION,SHADOW_BALL,THUNDER_PUNCH,25.5,13,15,14
            # hypno,CONFUSION,SHADOW_BALL,FOCUS_BLAST,25.5,13,15,14

            # machamp-shadow,COUNTER,ROCK_SLIDE,CROSS_CHOP,18,5,11,10
            victreebel_shadow-shadow,RAZOR_LEAF,LEAF_BLADE,FRUSTRATION,22.5,4,14,14
            ''')
    elif mode == 'ultra':
        candidate_csv_text = ub.codeblock(
            '''
            cresselia,PSYCHO_CUT,MOONBLAST,FUTURE_SIGHT
            togekiss,CHARM,FLAMETHROWER,ANCIENT_POWER
            articuno,ICE_SHARD,ICY_WIND,HURRICANE
            swampert,MUD_SHOT,MUDDY_WATER,EARTHQUAKE
            venusaur,VINE_WHIP,FRENZY_PLANT,SLUDGE_BOMB
            ''')
    else:
        raise KeyError(mode)

    candidates = []
    for line in candidate_csv_text.split('\n'):
        line = line.strip()
        if line.startswith('#'):
            continue
        if line:
            row = line.split(',')
            cand = Pokemon.from_pvpoke_row(row)
            candidates.append(cand)

    for self in candidates:

        self.populate_stats()

        items = self.items
        form = self.form


    # for self in candidates:
    #     print('self = {!r}'.format(self))
    #     print(self.calc_cp())

    print(ub.repr2(learnable))

    if mode == 'ultra':
        base = 'https://pvpoke.com/team-builder/all/2500'
    elif mode == 'great':
        base = 'https://pvpoke.com/team-builder/all/1500'
    sep = '%2C'
    import itertools as it
    print('candidates = {!r}'.format(candidates))
    for team in it.combinations(candidates, 3):
        # if not any('registeel' in p.name for p in team):
        #     continue
        if not any('victree' in p.name for p in team):
            continue
        if len(set(p.name for p in team)) != 3:
            continue
        suffix = sep.join([p.to_pvpoke_url() for p in team])
        url = base + '/' + suffix
        print(url)

    # altaria-26.5-14-12-13-4-4-1-m-0-3-2%2Cskarmory-26-11-13-10-4-4-1-m-0-3-2%2Cazumarill-38-12-15-13-4-4-1-m-0-2-1

    # !pip install beautifulsoup4

    # from bs4 import BeautifulSoup
    # import requests
    # got = requests.request('get', url)
    # print(got.text)
    # soup = BeautifulSoup(got.text, 'html.parser')
    # for div in soup.find_all(name='div'):
    #     if 'grade' in div.attrs:
    #         print('div = {!r}'.format(div))


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/pkmn/query_team_builder.py
    """
    main()
