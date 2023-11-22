"""
https://docs.google.com/spreadsheets/d/1aHdIl8mx6wB1fysJOtQDEuSlEzL4eD9W50O4XjxxL9o/edit#gid=0
"""

pp = 0.0

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


base_damage = 150


if 1:
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
            total_damage += int(current_damage)
        average_sim_damage = total_damage / num_attacks

        # Should converge to expected value
        regular_expected = base_damage + base_damage * attack['extra_damage']
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
