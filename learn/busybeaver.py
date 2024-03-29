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
    def enumerate(cls, all_states, alphabet_symbols, accept_states=None):
        for next_state in all_states:
            for write_symbol in alphabet_symbols:
                for direction in {L, R}:
                    yield cls(write_symbol, direction, next_state)


class TransitionTable(Dict[State, Dict[Symbol, Action]]):
    """
    A table that has an entry for every state, and maps it to another mapping
    typically from either a 0 to an action or 1 to a potentially different
    action.

    This is what defines execution flow
    """
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
            possible_actions = list(Action.enumerate(all_states, alphabet_symbols, accept_states))
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

    Example:
        list(TuringMachine.enumerate(2))[37]
    """

    # Interesting: all states a program can occupy
    Q: set[State]              # non-empty, all states

    # Boring, these just say we can either have 0 or 1 on the tape
    Γ: set[Symbol]             # non-empty, tape alphabet symbols
    b: Symbol                  # blank symbol
    Σ: set[Symbol]             # input symbols, subset of Γ - {b}

    # Interesting: this defines how you move between states.
    # THIS IS YOUR PROGRAM!
    δ: TransitionTable         # transition function

    # Boring, just pick one. This is the entry point to the program.
    # e.g. the main function or bootstrap function.
    q0: State                  # initial state, element of Q

    # Boring, just use HALT
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
        """
        Example:
            self = TuringMachine.random()
        """
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
                    curr = 'BREAK'
                    break
        logs.append(curr)
        return logs

    @classmethod
    def random(cls, n=1, rng=None):
        """
        n = 1
        cls = TuringMachine
        """
        import random
        try:
            import kwarray
            rng = kwarray.ensure_rng(rng)
        except ImportError:
            if rng is None:
                rng = random.Random(random.randint(0, 10000000000))
            else:
                rng = random.Random(rng)

        rng.randint
        possible  = cls.numberof(n)

        all_tms = list(cls.enumerate(n))  # todo: make an api with enumerage
        import random
        tm = random.choice(all_tms)
        return tm
        ...

    @classmethod
    def numberof(cls, num_states, num_symbols=2):
        """
        Number of turing machines with num_states and num_symbols

        CommandLine:
            xdoctest -m /home/joncrall/misc/learn/busybeaver.py TuringMachine.numberof

        Example:
            >>> print(TuringMachine.numberof(1))
            >>> print(len(list(TuringMachine.enumerate(1))))
            >>> #
            >>> print(TuringMachine.numberof(2))
            >>> print(len(list(TuringMachine.enumerate(2))))
            >>> if 0:
            >>>     print(TuringMachine.numberof(3))
            >>>     print(len(list(TuringMachine.enumerate(3))))
        """
        num_directions = 2
        return (num_symbols * num_directions * (num_states + 1)) ** (num_symbols * num_states)

    @classmethod
    def enumerate(cls, num_states : int, num_symbols=2):
        """
        Enumerate all turning machines of size n.
        There is no guarantee any generated TM will halt if you run them.

        Example:
            >>> import sys, ubelt
            >>> sys.path.append(ubelt.expandpath('~/misc/learn'))
            >>> from busybeaver import *  # NOQA
            >>> import itertools as it
            >>> for n in range(1, 5):
            >>>     first_five = list(it.islice(TuringMachine.enumerate(n), 0, 10))
            >>>     print('first_five({}) = {}'.format(n, ub.urepr([m._asdict() for m in first_five], nl=-1)))
        """
        # I'm confused by the wiki saying input symbols cannot have the blank
        # symbol, but blank 0, input is {1} and the initial tape is all 0?
        # isn't that not allowed? Whatever, moving forward, the results are
        # mostly correct.
        blank_symbol = Symbol(0)
        input_symbols = {Symbol(s) for s in range(1, num_symbols)}
        alphabet_symbols = input_symbols | {blank_symbol}

        num_digits = int(floor(log(max(1, num_states))))
        transition_states = {State(f'S{i:0{num_digits}d}') for i in range(num_states)}

        # I think multi-accept states reduce to a single final state, so no
        # need to generate them all?
        accept_states = {State('HALT')}
        all_states = accept_states | transition_states

        initial_state = min(transition_states)

        for transition in TransitionTable.enumerate(all_states, accept_states, alphabet_symbols):
            machine = cls(
                all_states, alphabet_symbols, blank_symbol, input_symbols,
                transition, initial_state, accept_states)
            yield machine

    @classmethod
    def busybeaver3(cls):
        """
        Hard coded defenition of a TM for busybeaver(3)

        CommandLine:
            xdoctest -m /home/joncrall/misc/learn/busybeaver.py TuringMachine.busybeaver3

        Example:
            >>> import sys, ubelt
            >>> sys.path.append(ubelt.expandpath('~/misc/learn'))
            >>> from busybeaver import *  # NOQA
            >>> import ubelt as ub
            >>> machine = TuringMachine.busybeaver3()
            >>> print('machine = {}'.format(ub.urepr(machine._asdict(), nl=-1)))
            >>> tape = InfiniteTape(machine.blank_symbol)
            >>> machine.run(tape)
            >>> print(f'tape={tape}')
            >>> assert sum(v == '1' for v in tape.values()) == 6
        """
        A, B, C = map(State, ['A', 'B', 'C'])
        HALT = State('HALT')
        _0, _1 = map(Symbol, ['0', '1'])
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
                _0: Action(_1, L, B),
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


def busybeaver(n, max_steps=None):
    """
    Initialize an output number to zero. For each n-state Turing Machine
    initialize a tape of all zeros for it to run on.  Run each n-state Turing
    Machine in parallel on its tape. When a machine halts, count the number of
    1's that appear on that machines tape. Update the output to be the maximum
    of itself and the count of 1's. After all machines that will halt finish,
    the output is the n-th busy beaver number.

    In other words, it is the maximum number of ones written by any halting
    n-state turing machine.

    This function is not computable in general.

    Known values:
        n=1 -> 1
        n=2 -> 4
        n=3 -> 6
        n=4 -> 13
        n=5 -> ??

    Ignore:
        >>> busybeaver(1, max_steps=100)
        >>> busybeaver(1)
        >>> busybeaver(2, max_steps=100)
        >>> busybeaver(3, max_steps=100)
        >>> import pytest
        >>> with pytest.raises(Undecidable):
        >>>     busybeaver(3)
    """
    if max_steps is None:
        # For certain n, we can make this a computable function
        if n == 1:
            max_steps = 10

    output = 0
    tm_iter = TuringMachine.enumerate(n)
    # import ubelt as ub
    from progiter.manager import ProgressManager
    pman = ProgressManager()
    with pman:
        prog = pman.progiter(tm_iter, total=TuringMachine.numberof(n), verbose=3)
        # prog = ub.ProgIter(tm_iter, total=TuringMachine.numberof(n), verbose=3)
        for machine in prog:
            tape = InfiniteTape(machine.blank_symbol)
            if max_steps is not None or machine.halts():
                logs = machine.run(tape, max_steps)
                if logs[-1] != 'BREAK':
                    num_ones = sum(v == '1' for v in tape.values())
                    output = max(output, num_ones)
            prog.set_extra(f'output={output}')
    return output


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/learn/busybeaver.py
    """
    busybeaver(3, max_steps=100)
