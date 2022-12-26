"""
Mario64 Speedrun Routing
Parse spreadsheet with best times, per stage and compute optimal runs.
Look at differences when taking into account constraints.
"""
import ubelt as ub
import pandas as pd
# https://docs.google.com/spreadsheets/d/1_cOIEnuKIQ-3LA_U0ygpiL87PTSBPlHmKDId0vC7alo/edit#gid=1471905853
sheet_id = "1_cOIEnuKIQ-3LA_U0ygpiL87PTSBPlHmKDId0vC7alo"
sheet_name = "Singlestar"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
fpath = ub.grabdata(url)
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

prows = []
for row in table.to_dict('records'):
    row = ub.udict(row) - {'Region', 'Version', 'Runner'}
    row['name'] = norm_name(row['coarse'])
    reqcode = row['requires'].split(';')
    requires = [r for r in reqcode if r]
    for r in requires:
        if 'star' in r:
            requires_stars = int(r.split(' ')[0])
            row['requires_star'] = requires_stars
        if 'basement_key' == r:
            row['requires_basement_key'] = 1
        if 'tower_key' == r:
            row['requires_tower_key'] = 1
        if 'sub' == r:
            row['requires_sub'] = 1
    rewcode = row['reward'].split(';')
    rewards = [r for r in rewcode if r]
    for r in rewards:
        if r == 'star':
            row['rewards_star'] = 1
        if r == 'basement_key':
            row['rewards_basement_key'] = 1
        if r == 'tower_key':
            row['rewards_tower_key'] = 1
        if r == 'wing_cap':
            row['rewards_wing_cap'] = 1
        if r == 'jumbo_star':
            row['rewards_jumbo_star'] = 1
    prows.append(row)
ptable = pd.DataFrame(prows)
ptable = ptable.set_index('name', drop=0)

SIMPLE = 0
if SIMPLE:
    # Simplify the problem
    ptable = ptable[
        (ptable['stage'] == 'BoB') |
        (ptable['stage'] == 'WF') |
        (ptable['stage'] == 'CCM') |
        (ptable['stage'] == 'WC') |
        (ptable['stage'] == 'SS') |
        (ptable['stage'] == 'BitDW')
    ]


def threshold_constraint_(var, thresh):
    r"""
    https://en.wikipedia.org/wiki/Big_M_method

    References:
        .. [1] https://or.stackexchange.com/questions/33/in-an-integer-program-how-i-can-force-a-binary-variable-to-equal-1-if-some-cond
        https://stackoverflow.com/questions/28395992/mixed-integer-programming-variable-assignment-per-condition-if-then-else

    Is the formulation in the first reference wrong?

    Ignore:
        import kwplot
        kwplot.autosns()

        XLB, XRB = -70, 70

        x = np.linspace(XLB, XRB, 100)
        b = 0.0

        plt = kwplot.autoplt()
        M = 140

        '''

        According to [1]

        To enforce (x < b) => (y == 1):

            b - x <= My

        To enforce (x > b) => (y == 1):

            x - b <= My

        M is a large constant used for numerical stability, but you want
        it to be as small as possible, while still producing correct result
        '''

        LB = -3
        UB = 3

        kwplot.figure(doclf=1, pnum=(1, 2, 1))
        y = (b - x) / M
        plt.fill_between(x, y, UB, alpha=0.5, label='yM')

        plt.plot([b, b], [LB, UB])
        ax = plt.gca()
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_xlim(XLB, XRB)
        ax.set_ylim(LB, UB)
        ax.set_title(f'Check for less than a threshold\nb - x <= My  <--> ((x < b) --> (y == 1))\nb = {b}')
        ax.legend()

        kwplot.figure(doclf=0, pnum=(1, 2, 2))
        y = (x - b) / M
        plt.fill_between(x, y, UB, alpha=0.5, label='y')

        plt.plot([b, b], [LB, UB])
        ax = plt.gca()
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_xlim(XLB, XRB)
        ax.set_ylim(LB, UB)
        ax.set_title(f'Check for greater than a threshold\nx - b <= My  <--> ((x > b) --> (y == 1))\nb = {b}')
        ax.legend()
    """

import pulp  # NOQA

# Make a variable indicating if we complete_flags a stage
complete_flags = pulp.LpVariable.dicts(name='got', indices=ptable['name'],
                                       lowBound=0, upBound=1, cat=pulp.LpInteger)

# Make a variable indicating if we can get to the start of a stage
can_enter = pulp.LpVariable.dicts(name='can_enter', indices=ptable['name'],
                                   lowBound=0, upBound=1, cat=pulp.LpInteger)

# Make a variable indicating how many stars we are missing to get to a stage
star_deficit = pulp.LpVariable.dicts(name='star_deficit', indices=ptable['name'],
                                       lowBound=0, upBound=1, cat=pulp.LpInteger)

# Get the subset of coarses that give each type of reward
reward_cols = [c for c in ptable.columns if c.startswith('rewards_')]
reward_flags = {}
for c in reward_cols:
    key = c.split('_', 1)[1]
    subset = ptable[ptable[c] > 0]
    reward_flags[key] = ub.udict(complete_flags) & (subset['name'].tolist())

# Indicates how many stars we have
num_stars = pulp.lpSum(reward_flags['star'].values())

# The total time is the sum of the time associated with each coarse we
# completed
total_time = sum(
    ptable.loc[k]['in_game_time'] * v
    for k, v in complete_flags.items()
)

prob = pulp.LpProblem("M64", pulp.LpMinimize)

# Subject to the following constraints

# Get subset of coarses that have requirements
require_cols = [c for c in ptable.columns if c.startswith('requires_')]
require_flags = {}

deficit_values = ub.ddict(dict)
deficit_flags = ub.ddict(dict)


# Gah this doesn't quite work, because we need to encode that
# we need 8 stars BEFORE we get the basement key.

for c in require_cols:
    key = c.split('_', 1)[1]
    subset = ptable[ptable[c] > 0]
    # Now many do we have of this reward type?
    num_have = sum(reward_flags.get(key, {}).values())

    def_accum = []
    for _, row in subset.iterrows():
        ...
        name = row['name']
        # For each stage with this particular requirement, we can only enter if
        # the requirement is satisfied.
        is_satisfied = can_enter[row['name']]

        # For this coarse, how many of this reward type are required?
        num_required = row[c]

        """
        We want to encode:
            is_satisfied = 1 if (num_required >= num_have) else 0

        But that specific expression isn't in normal form. Instead we can make
        a variable equal to our deficit of the resource wrt to this constraint.
        And then use another variable to encode if we have a deficit or not.

        num_deficit | have_deficit |
        ----------- | ------------ |
                 +2 |            1 |
                 +1 |            1 |
                  0 |            0 |
                 -1 |            0 |
                 -2 |            0 |

        This is encoded via

            have_deficit >= num_deficit
            have_deficit

        Our goal then becomes:

            is_satisfied = 1 if num_deficit <= 0 else 0

        Which I think we need to encode with an M-method, which means
        we need to ensure M is a constant larger than the maximum number of
        items.

            is_satisfied
        """
        deficit_key = f'deficit_{key}_{name}'
        # num_deficit = pulp.LpVariable(deficit_key)
        has_deficit = pulp.LpVariable(deficit_key, lowBound=0, upBound=1)
        M = len(ptable) * 2
        deficit_flags[name][key] = has_deficit
        num_deficit = num_required - num_have
        deficit_values[name][key] = num_deficit
        # prob.add(num_deficit == (num_required - num_have))
        #
        # prob.add(num_deficit - 1 <= M * has_deficit)
        # prob.add(num_deficit - 1 <= M * has_deficit)
        prob.add(num_deficit <= M * (1 - has_deficit))

        # Encode we can only enter if there is no deficit
        prob.add((-num_deficit) + 2 >= is_satisfied)


# For each coarse, we can only complete it if we can enter it.
for name in complete_flags.keys():
    prob.add(complete_flags[name] <= can_enter[name])


# Hack:
    prob.add(complete_flags['bowser_in_the_dark_world_battle'] <= complete_flags['bowser_in_the_dark_world_red_coins'])

# We get the keys when we complete bowser
if SIMPLE:
    # We must get the basement key
    prob.add(sum(reward_flags['basement_key'].values()) >= 1)
    ...
else:
    # We must get the jumbo star
    prob.add(sum(reward_flags['jumbo_star'].values()) >= 1)


# Minimize total time (and also bias towards not doing things)
prob.setObjective(total_time * 1000 + sum(can_enter.values()) )

# Not sure what is broken ...

#pulp.CPLEX().solve(prob)
pulp.PULP_CBC_CMD().solve(prob)


class emtpy_var():
    def value(self):
        return None

# Read solution
soln_rows = []
for name in complete_flags.keys():
    row = {
        'name': name,
        'time': ptable.loc[name]['in_game_time'],
        'complete': complete_flags[name].value(),
        'can_enter': can_enter[name].value(),
        'reward_star': reward_flags['star'].get(name, emtpy_var()).value(),
        'reward_basement_key': reward_flags['basement_key'].get(name, emtpy_var()).value()
        # 'deficit': complete_flags[name].value(),
    }
    # for key, defs in deficit_flags[name].items():
    #     deficit_col = f'has_deficit_{key}'
    #     row[deficit_col] = defs.value()
    for key, defs in deficit_values[name].items():
        deficit_col = f'deficit_{key}'
        try:
            row[deficit_col] = defs.value()
        except Exception:
            ...
    soln_rows.append(row)

import rich
soln_table = pd.DataFrame(soln_rows)
soln_table = soln_table.sort_values('time')
soln_table['complete'] = soln_table['complete'].apply(bool)
rich.print(soln_table.to_string())

# can_get_to_soln = {k: v.value() for k, v in can_enter.items()}
# deficit_soln = {k: v.value() for k, v in star_deficit.items()}
# print('can_get_to_soln = {}'.format(ub.repr2(can_get_to_soln, nl=1)))
# print('deficit_soln = {}'.format(ub.repr2(deficit_soln, nl=1)))

# solution = {k: v.value() for k, v in complete_flags.items()}
# print('solution = {}'.format(ub.urepr(solution, nl=1, align=':')))
# print([k for k, v in solution.items() if v > 0])

num_stars_soln = num_stars.value()
print(f'num_stars_soln={num_stars_soln}')

total_time_soln = total_time.value()
print(f'total_time_soln={total_time_soln}')
