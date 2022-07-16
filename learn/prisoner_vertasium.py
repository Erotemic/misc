"""
Monte Carlo version of Veritasium riddle

100 prisoners numbered 0-99

Slips with their numbers are randomply palced in 100 boxes in a room

Each priosner may enter the room one at a time and check 50 boxes

They leave the room exactly as they found it. They cannot communicate after the
game starts. They can communicate before the game starts.

If all 100 prisoners find their number they all go free, otherwise they all are
executed.

There is a strategy with a 1/3 chance of success.
"""

import numpy as np
import ubelt as ub
import kwarray
num_players = 100
allowed_chances = num_players // 2
rng = np.random.RandomState(33213210)


def run_iteration(strategy=0):
    boxes = np.arange(num_players)
    rng.shuffle(boxes)
    num_success = 0
    for player_index in range(num_players):
        if strategy == 'random':
            chosen_indexes = np.arange(num_players)
            rng.shuffle(chosen_indexes)
            chosen_indexes = chosen_indexes[:allowed_chances]
        elif strategy == 'shift':
            chosen_indexes = np.arange(player_index, player_index + allowed_chances) % num_players
        elif strategy == 'loop':
            chosen_indexes = []
            next_choice = player_index
            for chance_index in range(allowed_chances):
                chosen_indexes.append(next_choice)
                result = boxes[next_choice]
                next_choice = result
        else:
            raise NotImplementedError
        selected = boxes[chosen_indexes]
        success = player_index in selected
        num_success += success
    return num_success

num_monte_carlo_trials = 1000
results = [run_iteration(strategy='random') for _ in range(num_monte_carlo_trials)]
print(ub.repr2(kwarray.stats_dict(results, n_extreme=True), nl=0))

results = [run_iteration(strategy='shift') for _ in range(num_monte_carlo_trials)]
print(ub.repr2(kwarray.stats_dict(results, n_extreme=True), nl=0))

results = [run_iteration(strategy='loop') for _ in range(num_monte_carlo_trials)]
print(ub.repr2(kwarray.stats_dict(results, n_extreme=True), nl=0))
