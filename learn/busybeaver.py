"""
https://www.youtube.com/watch?v=kmAc1nDizu0
https://python-course.eu/applications-python/turing-machine.php


Busy beaver for a general n is not computable, because it relies on counting
the number of turning machines that halt. This number requires a function that
can compute or be used to compute if any turning machine with n states halts.
For some n this is possible, but in general it is not.

Example:
    >>> import sys, ubelt
    >>> sys.path.append(ubelt.expandpath('~/misc/learn'))
    >>> from busybeaver import *  # NOQA
    >>> one_state_machines = list(TuringMachine.enumerate(1))
    >>> print('one_state_machines = {}'.format(ub.urepr(one_state_machines, nl=1)))
    >>> two_state_machines = list(TuringMachine.enumerate(2))
    >>> print('two_state_machines = {}'.format(ub.urepr(two_state_machines, nl=1)))
    >>> print(len(one_state_machines))
    >>> print(len(two_state_machines))
"""
from typing import NamedTuple
from typing import Dict
from math import floor, log
from itertools import product, combinations, tee, count


class Undecidable(Exception):
    ...


class Shift(int):
    ...


L = LEFT = Shift(-1)
R = RIGHT = Shift(1)


class State(str):
    ...


class Symbol(str):
    ...


class Action(NamedTuple):
    write_symbol: Symbol
    direction: Shift
    next_state: State

    @classmethod
    def enumerate(cls, all_states, alphabet_symbols):
        for next_state in all_states:
            for write_symbol in alphabet_symbols:
                for direction in {L, R}:
                    yield cls(write_symbol, direction, next_state)


class TransitionTable(Dict[State, Dict[Symbol, Action]]):
    @classmethod
    def enumerate(cls, all_states, accept_states, alphabet_symbols):
        """
        For each state consider all possible actions it could perform.
        Enumerate each distinct mapping from input to output

        Example:
            >>> nonleaf_states = set(map(State, {0, 1}))
            >>> accept_states = {State('HALT')}
            >>> all_states = nonleaf_states | accept_states
            >>> alphabet_symbols = {'0', '1'}
            >>> list(TransitionTable.enumerate(all_states, accept_states, alphabet_symbols))
            >>> len(list(TransitionTable.enumerate(all_states, accept_states, alphabet_symbols)))
        """
        nonleaf_states = all_states - accept_states

        def possible_symbol_to_actions():
            # Create an object that will enumerate possible actions for each state
            # and for each possible symbol that could be read.
            possible_actions = list(Action.enumerate(all_states, alphabet_symbols))
            for action_tup in product(*tee(possible_actions, len(alphabet_symbols))):
                yield dict(zip(alphabet_symbols, action_tup))

        # Create a copy of this enumerable for each possible "current symbol/state"
        possible_symbol_to_actions_per_nonleaf = tee(possible_symbol_to_actions(), len(nonleaf_states))
        # Generate possible ways to transition for each state
        for transition_values in product(*possible_symbol_to_actions_per_nonleaf):
            transition = dict(zip(nonleaf_states, transition_values))
            yield transition


class InfiniteTape(dict):
    def __init__(self, blank=0):
        self.blank = blank
        self.position = 0

    def shift(self, direction):
        self.position += direction

    def read(self):
        return self.get(self.position, self.blank)

    def write(self, symbol):
        self[self.position] = symbol


class TuringMachine(NamedTuple):
    """
    References:
        https://en.wikipedia.org/wiki/Turing_machine
    """
    Q: set[State]              # non-empty, all states
    Γ: set[Symbol]             # non-empty, tape alphabet symbols
    b: Symbol                  # blank symbol
    Σ: set[Symbol]             # input symbols, subset of Γ - {b}
    δ: TransitionTable         # transition function
    q0: State                  # initial state, element of Q
    F: State                   # final state, subset of Q

    @property
    def all_states(self):
        return self.Q

    @property
    def alphabet_symbols(self):
        return self.Γ

    @property
    def blank_symbol(self):
        return self.b

    @property
    def input_symbols(self):
        return self.Σ

    @property
    def transition(self):
        return self.δ

    @property
    def initial_state(self):
        return self.q0

    @property
    def accept_states(self):
        return self.F

    def halts(self):
        raise Undecidable

    def run(self, tape: InfiniteTape = None, max_steps: int = None):
        """
        Execute a machine on a tape

        Ignore:
            >>> from busybeaver import *  # NOQA
            >>> for m in TuringMachine.enumerate(2):
            >>>     if m.initial_state in m.accept_states:
            >>>         continue
            >>>     self = m
            >>>     print('---')
            >>>     print(f'self={self}')
            >>>     tape = InfiniteTape(self.blank_symbol)
            >>>     logs = self.run(tape, max_steps=100)
            >>>     print(f'logs={logs}')
            >>>     print(f'tape={tape}')
        """
        if tape is None:
            tape = InfiniteTape(self.blank_symbol)

        logs = []
        curr = self.initial_state
        if curr not in self.accept_states:
            for step_num in count():
                symbol_to_action = self.transition[curr]
                symbol = tape.read()
                action = symbol_to_action[symbol]
                # Write overwrites current state (i.e. happens before the shift)
                tape.write(action.write_symbol)
                tape.shift(action.direction)
                curr = action.next_state
                logs.append(curr)
                if curr in self.accept_states:
                    break
                if max_steps is not None and step_num > max_steps:
                    logs.append('BREAK')
                    break

        return logs

    @classmethod
    def enumerate(cls, num_states : int, num_symbols=2):
        """
        Enumerate all turning machines of size n. There is no guarentee if they
        will halt if you run them or not.

        Example:
            >>> import sys, ubelt
            >>> sys.path.append(ubelt.expandpath('~/misc/learn'))
            >>> from busybeaver import *  # NOQA
            >>> import itertools as it
            >>> for n in range(0, 5):
            >>>     first_five = list(it.islice(TuringMachine.enumerate(n), 0, 10))
            >>>     print('first_five({}) = {}'.format(n, ub.urepr([m._asdict() for m in first_five], nl=-1)))
        """
        # I'm confused by the wiki saying input symbols cannot have the blank
        # symbol, but blank 0, input is {1} and the initial tape is all 0?
        # isn't that not allowed? Whatever, moving forward
        blank_symbol = Symbol(0)
        input_symbols = {Symbol(s) for s in range(1, num_symbols)}
        alphabet_symbols = input_symbols | {blank_symbol}

        num_digits = int(floor(log(max(1, num_states))))
        transition_states = {State(f'S{i:0{num_digits}d}') for i in range(num_states)}

        # I think multi-accept states reduce to a single final state, so no
        # need to generate them all?
        accept_states = {State('HALT')}
        all_states = accept_states | transition_states

        for initial_state in all_states:
            for transition in TransitionTable.enumerate(all_states, accept_states, alphabet_symbols):
                machine = cls(
                    all_states, alphabet_symbols, blank_symbol, input_symbols,
                    transition, initial_state, accept_states)
                yield machine

    @classmethod
    def busybeaver3(cls):
        """
        Hard coded defenition of the TM for busybeaver(3)

        Ignore:
            machine = TuringMachine.busybeaver3()
            tape = InfiniteTape(machine.blank_symbol)
            machine.run(tape)
            list(tape.values())
        """
        A, B, C = map(State, ['A', 'B', 'C'])
        HALT = State('HALT')
        _0, _1 = map(Symbol, [0, 1])
        transition = TransitionTable({
            A: {
                _0: Action(_1, R, B),
                _1: Action(_1, L, C),
            },
            B: {
                _0: Action(_1, L, A),
                _1: Action(_1, R, B),
            },
            C: {
                _0: Action(_1, R, B),
                _1: Action(_1, R, HALT),
            },
        })
        initial_state = A
        all_states = {A, B, C, HALT}
        alphabet_symbols = {_0, _1}
        blank_symbol = _0
        input_symbols = {_1}
        accept_states = {HALT}
        machine = TuringMachine(
            all_states, alphabet_symbols, blank_symbol, input_symbols,
            transition, initial_state, accept_states
        )
        return machine


def possible_accept_states(all_states):
    """
    Example:
        >>> all_states = set(map(State, {0, 1}))
        >>> list(possible_accept_states(all_states))
    """
    for num_accept_states in range(0, len(all_states) + 1):
        for accept_states in map(set, combinations(all_states, num_accept_states)):
            yield accept_states


def busy_beaver(n):
    for machine in TuringMachine.enumerate(n):
        if machine.halts():
            ...
        ...
