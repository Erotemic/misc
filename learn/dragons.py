import pandas as pd
import numpy as np

# Define the pool of creatures
# Pandas DataFrames are like SpreadSheets for Python
pool1 = pd.DataFrame([
    {'odds': 0.0281, 'breed_time': 4 * 60, 'hatch_time': 4 * 60},
    {'odds': 0.0281, 'breed_time': 72 * 60, 'hatch_time': 96 * 60},
    {'odds': 0.0281, 'breed_time': 72 * 60, 'hatch_time': 96 * 60},
    {'odds': 0.0281, 'breed_time': 72 * 60, 'hatch_time': 72 * 60},
    {'odds': 0.0225, 'breed_time': 72 * 60, 'hatch_time': 96 * 60},
    {'odds': 0.0281, 'breed_time': 120 * 60, 'hatch_time': 144 * 60},
    {'odds': 0.0225, 'breed_time': 120 * 60, 'hatch_time': 144 * 60},
    {'odds': 0.0225, 'breed_time': 120 * 60, 'hatch_time': 144 * 60},
    {'odds': 0.0281, 'breed_time': 120 * 60, 'hatch_time': 144 * 60},
    {'odds': 0.0281, 'breed_time': 120 * 60, 'hatch_time': 144 * 60},
])


# This is another pool, we will use montecarlo to determine if pool1 or pool2
# is better. Note there are only minor differences.
pool2 = pd.DataFrame([
    {'odds': 0.0281, 'breed_time': 4 * 60, 'hatch_time': 4 * 60},
    {'odds': 0.0281, 'breed_time': 1 * 60, 'hatch_time': 96 * 60},
    {'odds': 0.0281, 'breed_time': 72 * 60, 'hatch_time': 96 * 60},
    {'odds': 0.0281, 'breed_time': 72 * 60, 'hatch_time': 72 * 60},
    {'odds': 0.0225, 'breed_time': 72 * 60, 'hatch_time': 96 * 60},
    {'odds': 0.0281, 'breed_time': 120 * 60, 'hatch_time': 144 * 60},
    {'odds': 0.0225, 'breed_time': 120 * 60, 'hatch_time': 144 * 60},
    {'odds': 0.0225, 'breed_time': 120 * 60, 'hatch_time': 144 * 60},
    {'odds': 0.0281, 'breed_time': 120 * 60, 'hatch_time': 144 * 60},
    {'odds': 0.0281, 'breed_time': 620 * 60, 'hatch_time': 144 * 60},
])


def normalize_pool(pool):
    pool['prob'] = pool['odds'] / pool['odds'].sum()
    return pool

# Ensure the probabilities in the rows of each pool sum to 1.0!
pool1 = normalize_pool(pool1)
pool2 = normalize_pool(pool2)


def simulate_roll(pool):
    """
    Returns the best hatch time from a simulation of 1 trial.
    """
    # Randomly choose two from the pool without replacement
    chosen_indices = np.random.choice(
        pool.index, size=2, replace=False, p=pool['prob'])
    # Lookup pool at the chosen locations
    chosen_rows = pool.iloc[chosen_indices]

    # we always choose the minimum breed time of our available selection
    chosen_time = chosen_rows['breed_time'].min()
    return chosen_time


def approximate_expected_chosen_time(pool):
    """
    Run a Monte-Carlo simulation to get the statistically expected result from
    a pool. Of course you might get lucky or unlucky, but this is this returns
    the statistics that will maximize your results in the long run.
    """
    # Choose a big number to get a good approximation
    num_trials = 10000
    trials_results = []
    for trial_index in range(num_trials):
        trial_result = simulate_roll(pool)
        trials_results.append(trial_result)

    # Return the expected breed time for a pool
    expected_breed_time = np.mean(trials_results)
    return expected_breed_time


approx_pool1_ev = approximate_expected_chosen_time(pool1)
approx_pool2_ev = approximate_expected_chosen_time(pool1)
print('approx_pool1_ev = {!r}'.format(approx_pool1_ev))
print('approx_pool2_ev = {!r}'.format(approx_pool2_ev))

if approx_pool1_ev > approx_pool2_ev:
    print('Choose pool1, you will get better results in the long-run')
else:
    print('Choose pool2, you will get better results in the long-run')
