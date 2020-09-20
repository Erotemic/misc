
"""
pip install pypokedex
"""

import ubelt as ub
import re

candidate_csv_text = ub.codeblock(
    '''
    hypno,CONFUSION,SHADOW_BALL,FOCUS_BLAST,22.5,13,15,14
    farfetchd_galarian,FURY_CUTTER,LEAF_BLADE,BRAVE_BIRD,33.5,12,15,15
    altaria,DRAGON_BREATH,SKY_ATTACK,DRAGON_PULSE,26.5,14,12,13
    skarmory,AIR_SLASH,SKY_ATTACK,FLASH_CANNON,26,11,13,10
    azumarill,BUBBLE,ICE_BEAM,HYDRO_PUMP,38,12,15,13
    registeel,LOCK_ON,FLASH_CANNON,FOCUS_BLAST,22,10,14,15
    stunfisk_galarian,MUD_SHOT,ROCK_SLIDE,EARTHQUAKE,25,11,14,14
    ''')


# azumarill,BUBBLE,ICE_BEAM,PLAY_ROUGH,38,12,15,13
# umbreon,SNARL,FOUL_PLAY,LAST_RESORT
# dewgong,ICE_SHARD,ICY_WIND,WATER_PULSE


# def pokeapi_query():
#     'https://pogoapi.net/'
#     '/api/v1/current_pokemon_moves.json'

import json
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


class Pokemon(ub.NiceRepr):
    def __init__(self, name, level, ivs, moves, shadow=False):
        self.name = name
        self.level = level
        self.ivs = ivs
        self.moves = moves
        self.shadow = shadow

    def __nice__(self):
        return str([self.name] + self.moves + [self.level] + self.ivs)

    @classmethod
    def from_pvpoke_row(cls, row):
        name = row[0]
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
        self = cls(name, level, ivs, moves)
        return self

    def to_pvpoke_url(self):
        parts = []
        parts.append(self.name)
        if self.level is not None:
            parts.append(str(self.level))
        if self.ivs and all(v is not None for v in self.ivs):
            parts.extend(list(map(str, self.ivs)))
        if self.shadow:
            parts.append('shadow')

        parts.append('4-4-1')  # no idea what this is

        if self.moves:
            parts.append('m')
            moves = self.moves + ([None] * max(0, 3 - len(self.moves)))
            fm, cm1, cm2 = moves
            fm_idx = learnable[self.name]['fast'].index(fm)
            cm1_idx = learnable[self.name]['charge'].index(cm1) + 1
            parts.append(str(fm_idx))
            parts.append(str(cm1_idx))
            if cm2 is not None:
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
    candidates = []
    for line in candidate_csv_text.split('\n'):
        if line:
            row = line.split(',')
            cand = Pokemon.from_pvpoke_row(row)
            candidates.append(cand)

    for self in candidates:
        try:
            items = name_to_items[self.name]
            form = 'Normal'
        except Exception:
            if self.name.endswith('galarian'):
                form = 'Galarian'
                name = self.name.split('_galarian')[0]
                if name == 'farfetchd':
                    name = "farfetch\u2019d"
                items = name_to_items[name]
            else:
                raise

        self.form = form
        assert len(items)
        found = None

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
                    charge_moves.add('RETURN')

            # if item['form'] == form:
            #     found = item
        if self.name not in learnable:
            learnable[self.name] = {}

        learnable[self.name]['fast'] = sorted(fast_moves)
        learnable[self.name]['charge'] = sorted(charge_moves)

    print(ub.repr2(learnable))

    great_base = 'https://pvpoke.com/team-builder/all/1500'
    sep = '%2C'
    import itertools as it
    for team in it.combinations(candidates, 3):
        if len(set(p.name for p in team)) != 3:
            continue
        suffix = sep.join([p.to_pvpoke_url() for p in team])
        url = great_base + '/' + suffix
        print(url)

    # altaria-26.5-14-12-13-4-4-1-m-0-3-2%2Cskarmory-26-11-13-10-4-4-1-m-0-3-2%2Cazumarill-38-12-15-13-4-4-1-m-0-2-1

    # !pip install beautifulsoup4

    from bs4 import BeautifulSoup
    import requests
    got = requests.request('get', url)
    print(got.text)

    soup = BeautifulSoup(got.text, 'html.parser')
    for div in soup.find_all(name='div'):
        if 'grade' in div.attrs:
            print('div = {!r}'.format(div))
