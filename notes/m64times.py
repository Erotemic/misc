"""
Mario64 Speedrun Routing
Parse spreadsheet with best times, per stage and compute optimal runs.
Look at differences when taking into account constraints.
"""
import ubelt as ub
# import networkx as nx
import pandas as pd
# https://docs.google.com/spreadsheets/d/1_cOIEnuKIQ-3LA_U0ygpiL87PTSBPlHmKDId0vC7alo/edit#gid=1471905853
sheet_id = "1_cOIEnuKIQ-3LA_U0ygpiL87PTSBPlHmKDId0vC7alo"
sheet_name = "Singlestar"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
raw_df = pd.read_csv(url)


mapping = {
    'Unnamed: 4': 'in_game_time',
    'Real Time / IGT': 'real_time',
}
df = raw_df.copy()
ignore = [
    'Singlestar Rules',
]
df = df.rename({c: c.strip() for c in df.columns}, axis=1)
df = df.drop(ignore, axis=1)
df = df.rename(mapping, axis=1)


def parse_time(t):
    if pd.isnull(t):
        return t
    if t.strip() == '---':
        return float('nan')
    import datetime as datetime_mod
    rest = t
    minutes = 0
    seconds = 0
    milliseconds = 0
    if "'" in t:
        front, rest = rest.split("'", 1)
        minutes = int(front)
    if '"' in t:
        front, rest = rest.split('"', 1)
        seconds = int(front)
        milliseconds = int(rest)
    else:
        return t
    delta = datetime_mod.timedelta(seconds=seconds, milliseconds=milliseconds, minutes=minutes)
    return delta.total_seconds()

df['in_game_time'] = df['in_game_time'].map(parse_time)
df['real_time'] = df['real_time'].map(parse_time)

# Parse stages and stars

curr_stage = None
curr_star = None
rows = []
for _, old_row in df.iterrows():
    name = old_row['Stage / Star']
    try:
        int(name.split(' ')[0].strip('.'))
    except Exception:
        is_header = False
    else:
        is_header = True

    if is_header:
        curr_stage = name
    else:
        if not pd.isnull(name):
            curr_star = name
        if curr_star == 'Through the Jet Stream':
            if 'Jolly' in curr_stage:
                curr_star = 'Through the Jet Stream - JRB'
            else:
                curr_star = 'Through the Jet Stream - DDD'
        new_row = ub.udict({
            'stage': curr_stage,
            'coarse': curr_star,
        }) | (ub.udict(old_row) - {
            'Stage / Star',
            'Notes',
            'Singlestar WR Counter',
            'Unnamed: 11',
            'Unnamed: 10',
        })
        rows.append(new_row)

new_df = pd.DataFrame(rows)
stage_mapping = {
    '1. Bob-omb Battlefield': 'BoB',
    "2. Whomp's Fortress": "WF",
    '3. Jolly Roger Bay': 'JRB',
    '4. Cool, Cool Mountain': 'CCM',
    "5. Big Boo's Haunt": "BBH",
    '6. Hazy Maze Cave': 'HMC',
    '7. Lethal Lava Land': 'LLL',
    '8. Shifting Sand Land': 'SSL',
    '9. Dire, Dire Docks': 'DDD',
    "10. Snowman's Land": 'SML',
    '11. Wet-Dry World': 'WDW',
    '12. Tall, Tall Mountain': 'TTM',
    '13. Tiny-Huge Island': 'THI',
    '14. Tick Tock Clock': 'TTC',
    '15. Rainbow Ride': 'RR',
    '16. Secret Stars': 'secret',
    '17. Bowser Stages': 'bowser_stages',
    '18. Bowser Battles': 'bowser_battles',
}
new_df['stage'] = new_df['stage'].apply(stage_mapping.__getitem__)

secret_rows = []

row = new_df[new_df['coarse'] == 'Tower of the Wing Cap Red Coins'].iloc[0]
row['stage'] = 'WC'
row['reward'] = 'star;wing_cap'
secret_rows.append(row)
row = new_df[new_df['coarse'] == 'Vanish Cap under the Moat Red Coins'].iloc[0]
row['stage'] = 'VC'
row['reward'] = 'star;vanish_cap'
secret_rows.append(row)
row = new_df[new_df['coarse'] == 'Cavern of the Metal Cap Red Coins'].iloc[0]
row['stage'] = 'HMC'
row['reward'] = 'star;metal_cap'
secret_rows.append(row)
row = new_df[new_df['coarse'] == 'The Secret Aquarium Red Coins'].iloc[0]
row['stage'] = 'SA'
row['reward'] = 'star'
secret_rows.append(row)
row = new_df[new_df['coarse'] == 'Wing Mario over the Rainbow Red Coins'].iloc[0]
row['stage'] = 'WMotR'
row['reward'] = 'star'
secret_rows.append(row)
row = new_df[new_df['coarse'] == "The Princess's Secret Slide Box Star"].iloc[0]
row['stage'] = 'SS'
row['reward'] = 'star'
secret_rows.append(row)
row = new_df[new_df['coarse'] == """The Princess's Secret Slide Under 21"0"""].iloc[0]
row['stage'] = 'SS'
row['reward'] = 'star'
secret_rows.append(row)

bowser_rows = []
row = new_df[new_df['coarse'] == "Bowser in the Dark World Course"].iloc[0]
row['stage'] = 'BitDW'
row['reward'] = ''
bowser_rows.append(row)
row = new_df[new_df['coarse'] == "Bowser in the Dark World Red Coins"].iloc[0]
row['stage'] = 'BitDW'
row['reward'] = 'star'
row = bowser_rows.append(row)
row = new_df[new_df['coarse'] == "Bowser in the Dark World Battle"].iloc[0]
row['stage'] = 'BitDW'
row['reward'] = 'basement_key'
bowser_rows.append(row)

row = new_df[new_df['coarse'] == "Bowser in the Fire Sea Course"].iloc[0]
row['stage'] = 'BitFS'
row['reward'] = ''
bowser_rows.append(row)
row = new_df[new_df['coarse'] == "Bowser in the Fire Sea Red Coins"].iloc[0]
row['stage'] = 'BitFS'
row['reward'] = 'star'
bowser_rows.append(row)
row = new_df[new_df['coarse'] == "Bowser in the Fire Sea Battle"].iloc[0]
row['stage'] = 'BitFS'
row['reward'] = 'tower_key'
bowser_rows.append(row)

row = new_df[new_df['coarse'] == "Bowser in the Sky Course"].iloc[0]
row['stage'] = 'BitS'
row['reward'] = ''
bowser_rows.append(row)
row = new_df[new_df['coarse'] == "Bowser in the Sky Red Coins"].iloc[0]
row['stage'] = 'BitS'
row['reward'] = 'star'
bowser_rows.append(row)
row = new_df[new_df['coarse'] == "Bowser in the Sky Battle"].iloc[0]
row['stage'] = 'BitS'
row['reward'] = 'jumbo_star'
bowser_rows.append(row)

special = pd.DataFrame(secret_rows)
bowser = pd.DataFrame(bowser_rows)


# Build a new smaller table
table_rows = []
stage_mapping = {}
for stage, group in dict(list(new_df.groupby('stage'))).items():
    if stage not in {'secret', 'bowser_battles', 'bowser_stages'}:
        # Select one time per star
        for _, g in group.groupby('coarse'):
            row = g.loc[g['in_game_time'].idxmin()]
            row = row.to_dict()
            row['reward'] = 'star'
            table_rows.append(row)

table_rows.extend(bowser_rows)
table_rows.extend(secret_rows)


# table = table.sort_values('stage')
# table = table.sort_values('in_game_time')
table = pd.DataFrame(table_rows)
print(table.to_string())
table = table.set_index('coarse', drop=0)
table.loc[:, 'requires'] = ''

table.loc["Board Bowser's Sub", 'reward'] = 'sub'
table.loc[table['stage'] == 'DDD', 'requires'] = '15 stars'
table.loc[table['stage'] == 'WF', 'requires'] = '1 stars'
table.loc[table['stage'] == 'CCM', 'requires'] = '3 stars'
table.loc[table['stage'] == 'JRB', 'requires'] = '3 stars'
table.loc[table['stage'] == 'SS', 'requires'] = '1 stars'
table.loc[table['stage'] == 'BBH', 'requires'] = '12 stars'
table.loc[table['stage'] == 'BBH', 'requires'] = '12 stars'
table.loc[table['stage'] == 'SSL', 'requires'] = 'basement_key'
table.loc[table['stage'] == 'LLL', 'requires'] = 'basement_key'
table.loc[table['stage'] == 'HMC', 'requires'] = 'basement_key'
table.loc[table['stage'] == 'TTC', 'requires'] = 'tower_key'
table.loc[table['stage'] == 'SML', 'requires'] = 'tower_key'
table.loc[table['stage'] == 'THI', 'requires'] = 'tower_key'
table.loc[table['stage'] == 'TTM', 'requires'] = 'tower_key'
table.loc[table['stage'] == 'WDW', 'requires'] = 'tower_key'
table.loc[table['stage'] == 'RR', 'requires'] = 'tower_key'
table.loc[table['stage'] == 'BitS', 'requires'] = 'tower_key'
table.loc[table['stage'] == 'BitDW', 'requires'] = '8 stars'
table.loc[table['stage'] == 'BitFS', 'requires'] = 'sub'
table.loc[table['stage'] == 'SA', 'requires'] = '3 stars'
table.loc[table['stage'] == 'WMotR', 'requires'] = 'tower_key'
table.loc[table['stage'] == 'WC', 'requires'] = '10 stars'
table.loc[table['stage'] == 'VC', 'requires'] = 'basement_key'

table.loc['Red-Hot Log Rolling', 'requires'] += ';wing_cap'
table.loc['Shoot to the Island in the Sky', 'requires'] += ';wing_cap'
table.loc['Quick Race Through Downtown!', 'requires'] += ';vanish_cap'
table.loc['Eye to Eye in the Secret Room', 'requires'] += ';vanish_cap'
table.loc['Wing Mario over the Rainbow Red Coins', 'requires'] += ';wing_cap'

print(table.to_string())

table[table['stage'] == 'BoB']
table[table['stage'] == 'WF']
table[table['stage'] == 'CCM']
table[table['stage'] == 'JRB']
table[table['stage'] == 'BitDW']
table[table['stage'] == 'SSL']
table[table['stage'] == 'LLL']

# Formulate the pathing as an integer program
# Idea:
# WF requires 1 star
# BitDW requires 8 stars
# basement stars require basement key
# BitFS requires 15 stars (really should encode mips)
# tower stars require tower key


def norm_name(n):
    return n.replace(' ', '_').replace("'", '').replace('"', '').replace('!', '').replace('.', '').lower()

ptable = table.copy()
ptable['name'] = ptable['coarse'].apply(norm_name)
ptable = ptable.set_index('name', drop=0)


if 0:
    # Simplify the problem
    ptable = ptable[(ptable['stage'] == 'BoB') |
                    (ptable['stage'] == 'WF') |
                    (ptable['stage'] == 'CCM') |
                    (ptable['stage'] == 'BitDW')]

    small = {
        'behind_chain_chomps_gate',
        'blast_away_the_wall',
        'chip_off_whomps_block',
        'fall_onto_the_caged_island',
        'red_coins_on_the_floating_isle',
        'shoot_into_the_wild_blue',
        'to_the_top_of_the_fortress',
        'lil_penguin_lost',
        'wall_kicks_will_work',
        'bowser_in_the_dark_world_course',
        'bowser_in_the_dark_world_red_coins',
        'bowser_in_the_dark_world_battle',
    }
    # ptable = ptable[[n in small for n in ptable['name']]]

star_stages = [s for s in ptable[ptable['reward'] == 'star']['name']]

# times = pulp.LpVariable.dicts(name='times', indices=ptable['name'],
#                               lowBound=0, upBound=1, cat=pulp.LpInteger)

import pulp  # NOQA
prob = pulp.LpProblem("M64", pulp.LpMinimize)

# Make a variable indicating if we complete_flags a stage
complete_flags = pulp.LpVariable.dicts(name='got', indices=ptable['name'],
                                       lowBound=0, upBound=1, cat=pulp.LpInteger)

# Make a variable indicating if we can get to the start of a stage
can_get_to = pulp.LpVariable.dicts(name='can_get', indices=ptable['name'],
                                     upBound=1, cat=pulp.LpInteger)

# Make a variable indicating how many stars we are missing to get to a stage
num_missing = pulp.LpVariable.dicts(name='num_missing', indices=ptable['name'],
                                    lowBound=0, upBound=1, cat=pulp.LpInteger)

# A subset of complete_flags stages give stars
star_flags = ub.udict(complete_flags) & star_stages

time_cost_parts = []

# Indicates how many stars we have
num_stars = sum(star_flags.values())

# For every stage we could complete
for name in complete_flags:
    # It costs time to complete a coarse
    time_cost_parts.append(
        ptable.loc[name]['in_game_time'] * complete_flags[name]
    )

    # You can only get the star if requirements are met
    row = ptable.loc[name]
    reqcode = row['requires'].split(';')
    requires = [r for r in reqcode if r]
    for r in requires:
        if 'star' in r:
            required_stars = int(r.split(' ')[0])

            # We want to say
            # can_get_to = (num_stars >= required_stars)
            # i.e. is 1 when the constraint is satisfied and 0 otherwise
            # But that's not a valid phrasing...
            #
            # But when that would be 0, then num_stars - required_stars is
            # negative. So when num_stars - required_stars is negative, we
            # need to force the varaiable to be 0 or less.
            # Use a temporary variable that can be negative, 0 or 1
            num_missing[name] = required_stars - num_stars
            # We can complete a stage when num missing is 0 or less
            # Negate, so we can see how many extra stars we have (abundence)
            abundence = -num_missing[name]
            # Add 1, so when the abundence is 0 or more we know we can complete
            prob.add(can_get_to[name] <= abundence + 1)
            prob.add(can_get_to[name] >= 0)

    # Can only complete a coarse if you are able to get to it.
    prob.add(complete_flags[name] <= can_get_to[name])

# We must do these levels
# TODO: jumbo star constraint instead
prob.add(complete_flags['bowser_in_the_dark_world_battle'] >= 1)
prob.add(complete_flags['bowser_in_the_fire_sea_battle'] >= 1)
prob.add(complete_flags['bowser_in_the_sky_battle'] >= 1)

# Minimize total time
total_time = sum(time_cost_parts)
prob.objective = total_time

#pulp.CPLEX().solve(prob)
pulp.PULP_CBC_CMD().solve(prob)

# Read solution
solution = {k: v.value() for k, v in complete_flags.items()}
print('solution = {}'.format(ub.urepr(solution, nl=1, align=':')))
print([k for k, v in solution.items() if v > 0])
