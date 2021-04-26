"""
pip install pypokedex

TODO:
    - [ ] Implement ranges for unknown properties
"""
import json
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


def normalize(n):
    return n.upper().replace(' ', '_')


class PogoAPI(ub.NiceRepr):
    """
    Object to help with access to data from pogoapi.net
    """
    def __init__(api):
        api.base = 'https://pogoapi.net/api/v1/'
        api.routes = {
            'pokemon_stats': api.base + 'pokemon_stats.json',
            'current_pokemon_moves': api.base + 'current_pokemon_moves.json',
            'pokemon_evolutions': api.base + 'pokemon_evolutions.json',
            'cp_multiplier': api.base + 'cp_multiplier.json',
        }
        api.data = {}
        for key, url in api.routes.items():
            data_fpath = ub.grabdata(url, verbose=1)
            with open(data_fpath, 'r') as file:
                data = json.load(file)
            api.data[key] = data

        # Make the API global for now
        pokemon_stats = api.data['pokemon_stats']
        _name_to_stats = ub.group_items(pokemon_stats, lambda item: item['pokemon_name'].lower())
        _name_to_stats = dict(_name_to_stats)
        api.name_to_stats = _name_to_stats

        _name_to_items = ub.group_items(
            api.data['current_pokemon_moves'],
            lambda item: item['pokemon_name'].lower())
        _name_to_items.default_factory = None
        _name_to_items = dict(_name_to_items)

        # base = 'http://pokeapi.co/api/v2/pokemon/'
        api.name_to_moves = _name_to_items

        evolutions = api.data['pokemon_evolutions']
        _name_to_evolutions = ub.group_items(evolutions, lambda item: item['pokemon_name'].lower())
        _name_to_evolutions = dict(_name_to_evolutions)

        for key, form_stats in api.name_to_stats.items():
            if key not in _name_to_evolutions:
                noevos = []
                for s in form_stats:
                    empty = ub.dict_isect(s, {'form', 'pokemon_name', 'pokemon_id'})
                    empty['evolutions'] = []
                    noevos.append(empty)
                _name_to_evolutions[key] = noevos

        import networkx as nx
        evo_graph = nx.DiGraph()
        for name, form_evo_list in _name_to_evolutions.items():
            for form_evo in form_evo_list:
                u = form_evo['pokemon_name'].lower()
                evo_graph.add_node(u)
                for evo in form_evo['evolutions']:
                    v = evo['pokemon_name'].lower()
                    evo_graph.add_edge(u, v)

        # if 0:
        #     print(forest_str(evo_graph))

        api.name_to_family = {}
        api.name_to_base = {}
        evo_graph.remove_edges_from(nx.selfloop_edges(evo_graph))
        api.evo_graph = evo_graph
        for cc in list(nx.connected_components(api.evo_graph.to_undirected())):
            bases = [n for n in cc if len(evo_graph.pred[n]) == 0]
            base = bases[0]
            for n in cc:
                api.name_to_family[n] = cc
                api.name_to_base[n] = base

        # base_pokmeon = [n for n in evo_graph.nodes if len(evo_graph.pred[n]) == 0]
        api.name_to_evolutions = _name_to_evolutions

        # api.name_to_family = {}
        # for base in base_pokmeon:
        #     family = list(nx.dfs_postorder_nodes(evo_graph, base))
        #     for name in family:
        #         api.name_to_family[name] = family
        #         evos = api.name_to_evolutions[name]
        #         for evo in evos:
        #             evo['base'] = base

        #     for evo in evos['evolutions']:
        #         evo['base']

        api.learnable = {
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

    def __nice__(self):
        return str(list(api.routes.keys()))

    def normalize_name_and_form(api, name, form=None):
        if name.endswith('-shadow'):
            if form is None:
                form = 'Shadow'
            else:
                assert form == 'Shadow', f'{api}, {name}'
            name = name.split('-shadow')[0]

        if name.endswith('galarian'):
            if form is None:
                form = 'Galarian'
            if form == 'Normal':
                form = 'Galarian'  # hack
            # else:
            #     assert form == 'Galarian', f'{api}, {name}'
            name = name.split('_galarian')[0]

        if name == 'farfetchd':
            name = "farfetch\u2019d"

        if form is None:
            form = 'Normal'

        return name, form

    def get_info(api, name, form=None):
        """
        api = PogoAPI()
        name = 'machamp-shadow'
        print(ub.repr2(api.get_info(name)))
        form = None
        name = 'beedrill'
        print(ub.repr2(api.get_info(name)))
        name = 'farfetchd_galarian'
        print(ub.repr2(api.get_info(name)))
        name = 'stunfisk_galarian'
        print(ub.repr2(api.get_info(name)))
        """
        try:
            name_, form_ = api.normalize_name_and_form(name, form)
        except Exception:
            raise Exception(f'name={name}, form={form}')

        try:
            infos = [
                api.name_to_stats[name_],
                api.name_to_moves[name_],
                api.name_to_evolutions[name_],
            ]
        except Exception:
            raise Exception(f'name={name}, form={form}, name_={name_}, form_={form_}')

        info = {}
        for all_infos in infos:
            part = None
            for _info in all_infos:
                if _info['form'] == form_:
                    part = _info
            if part is None:
                raise KeyError
            info.update(part)

        if 1:
            fast_moves = set()
            charge_moves = set()

            for move in info['fast_moves']:
                fast_moves.add(normalize(move))
            for move in info['elite_fast_moves']:
                fast_moves.add(normalize(move))
            for move in info['charged_moves']:
                charge_moves.add(normalize(move))
            for move in info['elite_charged_moves']:
                charge_moves.add(normalize(move))

            if form_ == 'Normal':
                if info['form'] == 'Shadow':
                    charge_moves.add('FRUSTRATION')
                    charge_moves.add('RETURN')

            if name_ not in api.learnable:
                api.learnable[name_] = {}
            api.learnable[name_]['fast'] = sorted(fast_moves)
            api.learnable[name_]['charge'] = sorted(charge_moves)
        return info


api = PogoAPI()


def calc_cp(attack, defense, stamina, level):
    """
    References:
        https://www.dragonflycave.com/pokemon-go/stats
    """
    # cpm_step_lut = {
    #     0: 0.009426125469,
    #     10: 0.008919025675,
    #     20: 0.008924905903,
    #     30: 0.00445946079,
    # }
    cmp_lut = {
        1: 0.09399999678134918, 1.5: 0.1351374313235283, 2.0: 0.16639786958694458,
        2.5: 0.1926509141921997, 3.0: 0.21573247015476227, 3.5: 0.23657265305519104,
        4.0: 0.2557200491428375, 4.5: 0.27353037893772125, 5.0: 0.29024988412857056,
        5.5: 0.3060573786497116, 6.0: 0.3210875988006592, 6.5: 0.33544503152370453,
        7.0: 0.3492126762866974, 7.5: 0.362457737326622, 8.0: 0.37523558735847473,
        8.5: 0.38759241108516856, 9.0: 0.39956727623939514, 9.5: 0.4111935495172506,
        10.0: 0.4225000143051148, 10.5: 0.4329264134104144, 11.0: 0.443107545375824,
        11.5: 0.4530599538719858, 12.0: 0.46279838681221, 12.5: 0.4723360780626535,
        13.0: 0.4816849529743195, 13.5: 0.4908558102324605, 14.0: 0.4998584389686584,
        14.5: 0.5087017565965652, 15.0: 0.517393946647644, 15.5: 0.5259425118565559,
        16.0: 0.5343543291091919, 16.5: 0.5426357612013817, 17.0: 0.5507926940917969,
        17.5: 0.5588305993005633, 18.0: 0.5667545199394226, 18.5: 0.574569147080183,
        19.0: 0.5822789072990417, 19.5: 0.5898879119195044, 20.0: 0.5974000096321106,
        20.5: 0.6048236563801765, 21.0: 0.6121572852134705, 21.5: 0.6194041110575199,
        22.0: 0.6265671253204346, 22.5: 0.633649181574583, 23.0: 0.6406529545783997,
        23.5: 0.6475809663534164, 24.0: 0.654435634613037, 24.5: 0.6612192690372467,
        25.0: 0.667934000492096, 25.5: 0.6745819002389908, 26.0: 0.6811649203300476,
        26.5: 0.6876849085092545, 27.0: 0.6941436529159546, 27.5: 0.7005428969860077,
        28.0: 0.7068842053413391, 28.5: 0.7131690979003906, 29.0: 0.719399094581604,
        29.5: 0.7255756109952927, 30.0: 0.7317000031471252, 30.5: 0.7347410172224045,
        31.0: 0.7377694845199585, 31.5: 0.740785576403141, 32.0: 0.7437894344329834,
        32.5: 0.7467812150716782, 33.0: 0.7497610449790955, 33.5: 0.7527291029691696,
        34.0: 0.7556855082511902, 34.5: 0.7586303651332855, 35.0: 0.7615638375282288,
        35.5: 0.7644860669970512, 36.0: 0.7673971652984619, 36.5: 0.7702972739934921,
        37.0: 0.7731865048408508, 37.5: 0.7760649472475052, 38.0: 0.7789327502250671,
        38.5: 0.78179006, 39.0: 0.78463697, 39.5: 0.78747358,
        40.0: 0.79030001, 40.5: 0.79280001, 41.0: 0.79530001,
        41.5: 0.79780001, 42.0: 0.8003, 42.5: 0.8028,
        43.0: 0.8053, 43.5: 0.8078, 44.0: 0.81029999,
        44.5: 0.81279999, 45.0: 0.81529999,
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
        self = Pokemon('weedle')

        list(self.family())

    """
    def __init__(self, name, ivs=None, level=None, moves=None, shadow=False,
                 form='Normal', cp=None, autobuild=True, shiny=False,
                 adjusted=None):
        self.name = name.lower()
        self.level = level
        self.ivs = ivs
        self.moves = moves
        self.shadow = shadow
        self.shiny = shiny
        if shadow:
            form = 'Shadow'
        self.form = form
        self.api = api
        self.cp = cp
        self.adjusted = adjusted

        self.populate_stats()

        if cp is None:
            if level is not None and self.ivs is not None:
                if autobuild:
                    self.populate_cp()
        else:
            # If CP is specified, get the one that is closest
            # TODO: handle unknown ivs
            if level is None and self.ivs is not None:
                self.populate_level()

    def __json__(self):
        return {
            'name': self.name,
            'ivs': self.ivs,
            'level': self.level,
            'form': self.form,
            'shadow': self.shadow,
            'shiny': self.shiny,
            'moves': self.moves,
            # Depends on other properties
            'cp': self.cp,
            'adjusted': self.adjusted,
        }

    def copy(self, **overwrite):
        """
        Create a copy of this pokemon with possibly different attributes
        """
        kw = self.__json__()
        # Invalidate depenencies
        if 'ivs' in overwrite:
            if overwrite['ivs'] != kw['ivs']:
                kw.pop('cp', None)
                kw.pop('adjusted', None)

        if 'level' in overwrite:
            if overwrite['level'] != kw['level']:
                kw.pop('cp', None)
                kw.pop('adjusted', None)

        if 'cp' in overwrite:
            if overwrite['cp'] != kw['cp']:
                kw.pop('level', None)

        kw.update(overwrite)
        new = Pokemon(**kw)
        return new

    def display_name(self):
        parts = [self.name]
        if self.shadow:
            shadow_glyph = '😈'
            parts.append(shadow_glyph)

        elif self.form not in {'Normal', 'Shadow', 'Purified'}:
            parts.append('({})'.format(self.form))

        if self.form == 'Purified':
            purified_glyph = '👼'
            parts.append(purified_glyph)

        if self.shiny:
            shiny_glpyh = '✨'
            parts.append(shiny_glpyh)
        disp_name = ''.join(parts)
        return disp_name

    def __nice__(self):
        disp_name = self.display_name()
        info = '{}, {}, {}, {}, {}'.format(disp_name, self.cp, self.level, self.ivs, self.moves)
        return info
        # return str([self.name] + self.moves + [self.level] + self.ivs)

    def lookup_moves(self):
        possible_moves = api.name_to_moves[self.name]
        return possible_moves

    def populate_level(self, max_level=45):
        """ Try and find the level given the info """
        import numpy as np
        # hacky, could be more elegant
        target_cp = self.cp
        iva, ivd, ivs = self.ivs
        attack = self.info['base_attack'] + iva
        defense = self.info['base_defense'] + ivd
        stamina = self.info['base_stamina'] + ivs

        found_level = None

        for cand_level in np.arange(1, max_level + 0.5, 0.5):
            # TODO: could binary search
            cp, adjusted = calc_cp(attack, defense, stamina, cand_level)
            if cp == target_cp:
                found_level = cand_level
            elif cp > target_cp:
                break

        if found_level is None:
            raise Exception('cp does not match ivs')
        else:
            self.level = found_level

    def populate_stats(self):
        info = api.get_info(name=self.name, form=self.form)
        self.learnable = api.learnable[self.name]
        self.info = info
        # self.items = items

    def evolved(self):
        """
        Ignore:
            self = Pokemon('gastly', ivs=[6, 13, 15], cp=400)
            self.evolved()

            self = Pokemon('eevee', ivs=[6, 13, 15], cp=400)
            self.evolved()

            self = Pokemon('mew', ivs=[6, 13, 15], cp=400)
            self.evolved()
        """
        possibilities = []
        for other in self.family(onlyadj=True):
            # other.populate_cp()
            possibilities.append(other)
        return possibilities

    def purify(self):
        """
        Example:
            >>> self = Pokemon('ralts', ivs=[6, 13, 15], level=20,
            >>>                 shadow=True, shiny=True)
            >>> new = self.purify()
            >>> print('self = {!r}'.format(self))
            >>> print('new  = {!r}'.format(new))
        """
        if not self.shadow:
            raise Exception('Only can purify shadow pokemon')

        overwrite = {}
        if self.ivs is not None:
            new_ivs = tuple([min(15, s + 2) for s in self.ivs])
            overwrite['ivs'] = new_ivs
        overwrite['form'] = 'Purified'
        overwrite['shadow'] = False
        # TODO: replace frustration with return
        new = self.copy(**overwrite)
        return new

    def family(self, ancestors=True, node=False, onlyadj=False):
        """
        Get other members of this pokemon family

        Yields:
            Pokemon: other members of this family

        Ignore:
            self = Pokemon('gastly', ivs=[6, 13, 15])
            self = Pokemon('haunter', ivs=[6, 13, 15])
            self = Pokemon('gengar', ivs=[6, 13, 15])
            list(self.family())

            self = Pokemon('magikarp', ivs=[6, 13, 15])
            list(self.family())

            self = Pokemon('eevee', ivs=[6, 13, 15])
            list(self.family(onlyadj=True))

            self = Pokemon('ralts', ivs=[6, 13, 15], shadow=True)
            list(self.family(onlyadj=True))
            list(self.family())
        """
        import networkx as nx
        blocklist = set()
        if not node:
            blocklist.add(self.name)

        if not ancestors:
            toadd = set(nx.ancestors(api.evo_graph, self.name))
            blocklist.update(toadd)

        cc = api.name_to_family[self.name]
        if onlyadj:
            keeplist = set(api.evo_graph.adj[self.name])
            blocklist = set(cc) - keeplist

        kw = {
            'level': self.level,
            'form': self.form,
            'ivs': self.ivs,
            'shadow': self.shadow,
            'shiny': self.shiny,
        }
        for name in cc:
            if name not in blocklist:
                if name == self.name:
                    other = Pokemon(name, cp=self.cp, **kw)
                else:
                    other = Pokemon(name, **kw)
                yield other

                if other.shadow:
                    yield other.purify()

    def populate_cp(self):
        level = self.level
        iva, ivd, ivs = self.ivs
        attack = self.info['base_attack'] + iva
        defense = self.info['base_defense'] + ivd
        stamina = self.info['base_stamina'] + ivs
        cp, adjusted = calc_cp(attack, defense, stamina, level)
        self.cp = cp
        self.adjusted = adjusted
        return cp, adjusted

    def check_evolution_cps(self, max_cp=1500, max_level=45):
        """
        self = Pokemon('gastly', ivs=[6, 13, 15])
        self.check_evolution_cps()

        self = Pokemon('gyarados', ivs=[6, 13, 15])
        self.check_evolution_cps()

        self = Pokemon('magikarp', ivs=[6, 13, 15])
        self.check_evolution_cps()
        """
        import numpy as np
        evos = list(self.family(ancestors=False))

        if len(evos) == 0:
            print('no evolutions available')

        for evo in evos:
            other = evo

            best_level = None
            for level in list(np.arange(1, max_level + 0.5, 0.5)):
                # TODO: could binary search
                other.level = level
                other.populate_cp()
                if other.cp <= max_cp:
                    best_level = level
                else:
                    break
            other.level = best_level
            other.populate_cp()

            print('To achieve other = {!r}'.format(other))
            self.level = best_level
            cp, adjusted = self.populate_cp()
            print('self = {!r}'.format(self))
            print('Pokemon CP must be less than this to be used in league')
            print('cp = {!r}'.format(cp))

    def leage_rankings_for(self, have_ivs, max_cp=1500, max_level=45):
        """
        Given a set of IVs for this pokemon compute the leage rankings
        """
        leage_df = self.find_leage_rankings(max_cp=max_cp, max_level=max_level)
        leage_df = leage_df.set_index(['iva', 'ivd', 'ivs'])

        if abs(min(leage_df['cp'].max() - min(3000, max_cp), 0)) > 200:
            print('Out of this leage {}'.format(max_cp))
        else:
            rows = []
            for haves in have_ivs:
                # ultra_row = ultra_df.loc[haves]
                leage_row = leage_df.loc[haves]
                rows.append({
                    'iva': haves[0],
                    'ivd': haves[1],
                    'ivs': haves[2],
                    'rank': leage_row['rank'],
                    'level': leage_row['level'],
                    'cp': leage_row['cp'],
                    'stat_product': leage_row['stat_product'],
                    'attack': leage_row['attack'],
                    'defense': leage_row['defense'],
                    'stamina': leage_row['stamina'],
                    'percent': leage_row['percent'],
                })
            import pandas as pd
            rankings = pd.DataFrame.from_dict(rows)
            #
            print('')
            print('Leage {} Rankings'.format(max_cp))
            print('self = {!r}'.format(self))
            print(rankings.sort_values('rank'))

    def find_leage_rankings(self, max_cp=1500, max_level=45):
        """
        Calculate the leage rankings for this pokemon's IVs, based on the
        adjusted stat product heuristic.

        Ignore:
            >>> import sys, ubelt
            >>> sys.path.append(ubelt.expandpath('~/misc/pkmn'))
            >>> from query_team_builder import *  # NOQA
            >>> self = Pokemon('beedrill')
            >>> beedrill_df = self.find_leage_rankings(max_cp=1500)

            >>> # Find the best IVs that we have for PVP
            >>> self = Pokemon('empoleon')
            >>> have_ivs = [
            >>>     (0, 10, 14),
            >>>     (1, 11, 5),
            >>>     (1, 5, 7),
            >>>     (1, 9, 13),
            >>>     (2, 15, 13),
            >>>     (2, 2, 10),
            >>>     (2, 6, 9),
            >>>     (3, 13, 11),
            >>>     (3, 3, 2),
            >>>     (4, 13, 13),
            >>>     (5, 13, 14),
            >>>     (4, 14, 14),
            >>>     (7, 13, 3),
            >>>     (13, 14, 14),
            >>>     (15, 14, 14),
            >>> ]

            >>> self = Pokemon('beedrill')
            >>> have_ivs = [
            >>>     (0, 8, 14),
            >>>     (0, 12, 14),
            >>>     (1,  3, 10),
            >>>     (1, 13, 6),
            >>>     (4, 11, 13),
            >>>     (4, 14, 13),
            >>>     (1, 13, 7),
            >>>     (1, 10, 8),
            >>>     (4, 13, 13),
            >>>     (4, 14, 14),
            >>>     (4, 15, 12),
            >>>     (5, 14, 11),
            >>>     (11, 15, 14),
            >>>     (15, 15, 15),
            >>>     (12, 15, 15),
            >>> ]
            >>> self.leage_rankings_for(have_ivs)

            >>> have_ivs = [
            >>>     (4, 13, 10),
            >>>     (5, 11, 14),
            >>>     (4, 13, 11),
            >>>     (6, 13, 15),
            >>>     (7, 12, 13),
            >>>     (7, 14, 14),
            >>>     (7, 15, 15),
            >>>     (7, 2, 9),
            >>>     (10, 15, 11),
            >>>     (15, 15, 15),
            >>>     (7, 15, 15),
            >>> ]
            >>> self = Pokemon('gengar')
            >>> print('self.info = {}'.format(ub.repr2(self.info, nl=2)))
            >>> self.leage_rankings_for(have_ivs)

            >>> self = Pokemon('haunter')
            >>> print('self.info = {}'.format(ub.repr2(self.info, nl=2)))
            >>> self.leage_rankings_for(have_ivs)

            >>> have_ivs = [
            >>>     (12, 11, 14),
            >>>     (12, 15, 15),
            >>>     (15, 15, 15),
            >>> ]
            >>> Pokemon('blaziken').leage_rankings_for(have_ivs, max_cp=1500)
            >>> Pokemon('blaziken').leage_rankings_for(have_ivs, max_cp=2500)
            >>> Pokemon('blaziken').leage_rankings_for(have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (0, 2, 14),
            >>>     (4, 2, 13),
            >>>     (11, 13, 12),
            >>>     (4, 13, 9),
            >>>     (15, 12, 13),
            >>>     (13, 14, 13),
            >>>     (13, 14, 13),
            >>>     (14, 14, 10),
            >>>     (6, 15, 11),  # purified
            >>>     (13, 15, 14),  # purified
            >>> ]
            >>> Pokemon('swampert').leage_rankings_for(have_ivs, max_cp=1500)
            >>> Pokemon('swampert').leage_rankings_for(have_ivs, max_cp=2500)
            >>> Pokemon('swampert').leage_rankings_for(have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (1, 2, 15),
            >>>     (12, 15, 14),
            >>>     (14, 15, 14),
            >>>     (14, 14, 14),
            >>>     (14, 13, 15),
            >>>     (15, 15, 10),
            >>> ]
            >>> Pokemon('sceptile').leage_rankings_for(have_ivs, max_cp=1500)
            >>> Pokemon('sceptile').leage_rankings_for(have_ivs, max_cp=2500)

            >>> have_ivs = [
            >>>     (0, 10, 15),
            >>>     (1, 14, 11),
            >>>     (11, 14, 13),
            >>>     (12, 12, 13),
            >>>     (14, 13, 13),
            >>>     (2, 13, 12),
            >>>     (2, 13, 15),
            >>>     (2, 14, 14),
            >>>     (2, 15, 14),
            >>>     (3, 12, 11),
            >>>     (3, 4, 15),
            >>>     (3, 13, 14),
            >>>     (3, 5, 2),
            >>>     (4, 10, 13),
            >>>     (4, 12, 15), # shadow
            >>>     (5, 15, 12),
            >>>     (7, 13, 15),
            >>>     (7, 15, 8),
            >>>     (15, 13, 15),
            >>> ]
            >>> Pokemon('gyarados').leage_rankings_for(have_ivs, max_cp=np.inf)
            >>> Pokemon('gyarados').leage_rankings_for(have_ivs, max_cp=2500)
            >>> Pokemon('gyarados').leage_rankings_for(have_ivs, max_cp=1500)


            >>> have_ivs = [
            >>>     (14, 14, 15),
            >>>     (10, 14, 15),
            >>>     (15, 15, 15),
            >>>     (15, 15, 15),
            >>> ]
            >>> Pokemon('rhyperior').leage_rankings_for(have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (14, 14, 14),
            >>>     (12, 13, 14),
            >>>     (13, 14, 14),
            >>>     (15, 13, 14),
            >>>     (8, 6, 8),
            >>> ]
            >>> Pokemon('vigoroth').leage_rankings_for(have_ivs, max_cp=1500)


            >>> have_ivs = [
            >>>     (6, 15, 13),
            >>>     (3, 4, 14),
            >>>     (2, 9, 15),
            >>>     (6, 14, 15),
            >>>     (7, 15, 15),
            >>>     (10, 15, 15),
            >>> ]
            >>> Pokemon('shiftry').leage_rankings_for(have_ivs, max_cp=1500)
            >>> Pokemon('shiftry').leage_rankings_for(have_ivs, max_cp=2500)

            >>> have_ivs = [
            >>>     (15, 15, 14),
            >>>     (0, 7, 8),
            >>>     (3, 12, 14),
            >>>     (5, 5, 15),
            >>>     (4, 7, 12),
            >>>     (15, 14, 14),
            >>>     (10, 14, 15),
            >>> ]
            >>> Pokemon('alakazam').leage_rankings_for(have_ivs, max_cp=1500)
            >>> Pokemon('alakazam').leage_rankings_for(have_ivs, max_cp=2500)

            >>> have_ivs = [
            >>>     (0, 15, 6),
            >>>     (11, 10, 10),
            >>>     (12, 12, 11),
            >>>     (15, 10, 12),
            >>> ]
            >>> Pokemon('salamence').leage_rankings_for(have_ivs, max_cp=1500)
            >>> Pokemon('salamence').leage_rankings_for(have_ivs, max_cp=2500)
            >>> Pokemon('salamence').leage_rankings_for(have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (6, 10, 10),
            >>>     (11, 9, 14),
            >>>     (13, 12, 14),
            >>>     (15, 15, 15),
            >>>     (15, 15, 5),
            >>> ]
            >>> Pokemon('flygon').leage_rankings_for(have_ivs, max_cp=1500)
            >>> Pokemon('flygon').leage_rankings_for(have_ivs, max_cp=2500)
            >>> Pokemon('flygon').leage_rankings_for(have_ivs, max_cp=np.inf)

            >>> have_ivs = [
            >>>     (6, 11, 11),
            >>>     (10, 11, 10),
            >>>     (10, 11, 12),
            >>>     (6, 14, 4),
            >>>     (15, 12, 15),
            >>>     (15, 7, 15),
            >>> ]
            >>> Pokemon('mamoswine').leage_rankings_for(have_ivs, max_cp=1500)
            >>> Pokemon('mamoswine').leage_rankings_for(have_ivs, max_cp=2500)
            >>> Pokemon('mamoswine').leage_rankings_for(have_ivs, max_cp=np.inf)


        """
        rows = []
        import itertools as it
        import numpy as np

        for iva, ivd, ivs in it.product(range(16), range(16), range(16)):
            attack = self.info['base_attack'] + iva
            defense = self.info['base_defense'] + ivd
            stamina = self.info['base_stamina'] + ivs

            best_level = None
            best_cp = None
            best_adjusted = None
            for level in list(np.arange(1, max_level + 0.5, 0.5)):
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
        df = df.set_index('rank', drop=False)
        min_ = df['stat_product'].min()
        max_ = df['stat_product'].max()
        df['percent'] = ((df['stat_product'] - min_) / (max_ - min_)) * 100
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
                attack = self.info['base_attack'] + iva
                defense = self.info['base_defense'] + ivd
                stamina = self.info['base_stamina'] + ivs
                cand_cp = calc_cp(attack, defense, stamina, level)
                if cand_cp > 1500:
                    break
                best_cp = cand_cp
                best_level = level
                print('best_cp = {!r}'.format(best_cp))
                print('best_level = {!r}'.format(best_level))

        level = self.level
        iva, ivd, ivs = self.ivs
        attack = self.info['base_attack'] + iva
        defense = self.info['base_defense'] + ivd
        stamina = self.info['base_stamina'] + ivs
        cp, adjusted = calc_cp(attack, defense, stamina, level)
        return cp

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

            fm_idx = api.learnable[self.name]['fast'].index(fm)
            cm1_idx = api.learnable[self.name]['charge'].index(cm1) + 1
            parts.append(str(fm_idx))
            parts.append(str(cm1_idx))
            if cm2 is not None:
                if cm2.lower() == 'frustration':
                    # hack for frustration
                    cm2_idx = 0
                else:
                    cm2_idx = api.learnable[self.name]['charge'].index(cm2) + 1
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


def pvp_inventory():
    """
    The idea is you put info about your candidates here and we find good mons
    to power up.
    """
    inventory = [
        Pokemon('Magnezone', (14, 14, 14), cp=1815, form='Normal'),
        Pokemon('Magnemite', (7, 14, 9), cp=792),
        Pokemon('Magnemite', (10, 14, 13), cp=747),
        Pokemon('Magnemite', (13, 9, 15), cp=602),
        Pokemon('Magneton', (13, 14, 13), cp=550, form='Shadow'),
        Pokemon('Magnemite', (15, 13, 7), cp=293, form='Shadow'),
        Pokemon('Magnemite', (2, 14, 15), cp=283, form='Shadow'),
    ]

    inventory = [
        Pokemon('sirfetch’d', (4, 11, 12), cp=1924, form='Galarian'),
        Pokemon('farfetch’d', (12, 15, 15), cp=1495, form='Galarian'),
        Pokemon('farfetch’d', (14, 14, 15), cp=948, form='Galarian'),
    ]

    inventory = [
        Pokemon('bulbasaur', (7, 13, 12), cp=382, form='Shadow'),
        Pokemon('bulbasaur', (4, 8, 13), cp=366, form='Shadow'),
        Pokemon('bulbasaur', (7, 12, 8), cp=227, form='Shadow'),
    ]

    inventory = [
        Pokemon('Clefable', (12, 13, 12), cp=1828),
        Pokemon('Clefairy', (4, 2, 7), cp=389),
    ]

    inventory = [
        Pokemon('Jigglypuff', (10, 14, 15), cp=631),
        Pokemon('Jigglypuff', (10, 12, 15), cp=286),
    ]

    inventory = [
        Pokemon('poliwag', (10, 13, 14), cp=335),
        Pokemon('poliwag', (10, 14, 13), cp=335),
    ]

    inventory = [
        Pokemon('drifloon', (15, 15, 1), cp=695),
        Pokemon('drifloon', (0, 9, 14), cp=527),
        Pokemon('drifloon', (15, 15, 12), cp=509),
        Pokemon('drifloon', (14, 15, 14), cp=508),
        Pokemon('drifloon', (14, 11, 14), cp=497),
        Pokemon('drifloon', (11, 13, 12), cp=489, shiny=True),
        Pokemon('drifloon', (0, 4, 8), cp=336),
        Pokemon('drifloon', (12, 10, 12), cp=118),
    ]

    inventory = [
        Pokemon('shelmet', (10, 15, 8), cp=351),
        Pokemon('shelmet', (0, 13, 0), cp=166),
        Pokemon('shelmet', (15, 10, 12), cp=158),
    ]

    inventory = [
        Pokemon('Karrablast', (10, 4, 12), cp=824),
        Pokemon('Karrablast', (13, 13, 13), cp=655),
        Pokemon('Karrablast', (13, 14, 15), cp=16),
    ]

    inventory = [
        Pokemon('Ralts', (14, 14, 13)),
        Pokemon('Ralts', (14, 11, 12)),
        Pokemon('Ralts', (0, 11, 0), shadow=True),
        Pokemon('Ralts', (1, 14, 2), shadow=True),
        Pokemon('Ralts', (12, 12, 6), shadow=True),
        Pokemon('Ralts', (5, 14, 14)),
        Pokemon('Ralts', (7, 11, 11)),
    ]

    inventory = [
        Pokemon('Toxicroak', (11, 13, 14)),
        Pokemon('Croagunk', (9, 11, 13), cp=794),
        Pokemon('Croagunk', (8, 6, 8), cp=429),
    ]

    inventory = [
        Pokemon('Snorlax', (7, 6, 13), shadow=True),
        Pokemon('Snorlax', (0, 0, 13), shadow=0),
        Pokemon('Snorlax', (8, 15, 14), shadow=0, cp=1155),
        Pokemon('Snorlax', (8, 12, 11), shadow=0, cp=2106),
        Pokemon('Snorlax', (9, 15, 10), shadow=0, cp=2487),
        Pokemon('Snorlax', (1, 15, 14), shadow=0, cp=1372),
        Pokemon('Snorlax', (7, 11, 15), shadow=0, cp=3044),
        Pokemon('Snorlax', (2, 15, 1), shadow=1),
        Pokemon('Munchlax', (14, 11, 14), shadow=0, cp=1056),
    ]

    inventory = [
        Pokemon('Obstagoon', (11, 15, 13), cp=1478, form='Galarian'),
        Pokemon('zigzagoon', (10, 14, 14), cp=268, form='Galarian'),
        Pokemon('zigzagoon', (11, 12, 13), cp=268, form='Galarian'),
        Pokemon('zigzagoon', (11, 12, 15), cp=270, form='Galarian'),
        Pokemon('zigzagoon', (12, 11, 15), cp=272, form='Galarian'),
    ]

    inventory = [
        Pokemon('Meditite', (5, 12, 4), cp=25),
        Pokemon('Medicham', (14, 12, 12), cp=1116),
        Pokemon('Medicham', (15, 15, 10), cp=966),
    ]

    for self in inventory:
        list(self.family())

    candidates = list(ub.flatten(list(pkmn.family(ancestors=False)) for pkmn in inventory)) + inventory

    groups = ub.group_items(candidates, key=lambda p: p.name)

    leages = {
        'master': {'max_cp': float('inf')},
        'ultra': {'max_cp': 2500},
        'great': {'max_cp': 1500},
        'little': {'max_cp': 500},
    }

    max_level = 45  # for XL candy
    max_level = 40  # normal

    for name, group in groups.items():
        print('\n\n------------\n\n')
        print('name = {!r}'.format(name))
        for leage_name, leage_filters in leages.items():
            max_cp = leage_filters['max_cp']
            print('')
            print(' ========== ')
            print(' --- {} in {} --- '.format(name, leage_name))
            not_eligible = [p for p in group if p.cp is not None and p.cp > max_cp]
            print('not_eligible = {!r}'.format(not_eligible))
            have_ivs = [p.ivs for p in group if p.cp is None or p.cp <= max_cp]
            if len(have_ivs) > 0:
                first = ub.peek(group)
                first.leage_rankings_for(have_ivs, max_cp=max_cp,
                                         max_level=max_level)
            else:
                print('none eligable')


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

    # for self in candidates:
    #     self.populate_stats()

    # for self in candidates:
    #     print('self = {!r}'.format(self))
    #     print(self.calc_cp())

    print(ub.repr2(api.learnable))

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
