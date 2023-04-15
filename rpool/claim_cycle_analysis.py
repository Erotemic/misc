"""
I'm curious if there is existing guidance on calculating the optimal number of
ntervals to wait before claiming rewards. I imagine this depends on several
factors like:
    * number of minipools,
    * smoothing pool status,
    * gas prices,
    * how much of your rewards you will restake,
    * current collateral level etc...

I was wondering if someone's written a tool that lets you specify your
assumptions and calculate how often someone in that circumstance should be
claiming rewards in order to maximize returns?

Can we write such a scripts? Here is an attempt.

URL:
    https://github.com/Erotemic/misc/blob/main/rpool/claim_cycle_analysis.py

Requirements:
    pip install ubelt scriptconfig pandas rich pint numpy

Optional Requirements:
    pip install kwplot


References:
    # We likely have too many oversimplified assumptions here.
    https://www.rocketpooltool.com/
    https://docs.rocketpool.net/guides/node/responsibilities.html#rewards
    https://docs.rocketpool.net/guides/node/rewards.html#rewards-and-checkpoints
    https://github.com/rocket-pool/rocketpool-research/blob/master/Merkle%20Rewards%20System/rewards-calculation-spec.md
    https://www.reddit.com/r/rocketpool/comments/o3rovh/rpl_rewards_estimate/
    https://docs.google.com/spreadsheets/d/1Wl3EukDALcd8nBQQkMhzXr5WfwmEj264YPfch9AJN30/edit#gid=0


TODO:
    - [ ] Handle converting ETH rewards into restaked RPL, requires estimating how much that transaction costs.

    - [ ] Ensure RPL reward rate is corret

    - [ ] Ensure smoothing pool ETH rewards is correct

    - [ ] Handle fractional restaking
"""
import scriptconfig as scfg
import ubelt as ub
import pint
import rich
import pandas as pd
import numpy as np


class ConversionRates(scfg.DataConfig):
    """
    Base class representing unit conversions
    """
    eth_to_dollar = scfg.Value(2000, help='current value of 1ETH in dollars')
    rpl_to_eth = scfg.Value(0.024404, help='current value of 1RPL in ETH')

    def __post_init__(conversions):
        conversions._ureg = pint.UnitRegistry()
        conversions._ureg.define('dollar = []')
        conversions._ureg.define(f'ETH = {conversions.eth_to_dollar} dollar')
        conversions._ureg.define(f'RPL = {conversions.rpl_to_eth} ETH')


class UnhandledAssumptions(ConversionRates):
    # TODO: these numbers are important but unhandled. They should
    # be folded into assumptions and used in calculations.
    average_rpl_collateral_fraction = scfg.Value(1.4438, help=ub.paragraph(
        '''
        The average collateral level over all minipools on the network.
        (Default from 2023-04-15)
        '''))

    total_rocketpool_minipools = scfg.Value(6847, help=ub.paragraph(
        '''
        Total number of active minipools. (Default from 2023-04-15)
        '''))

    eth_supply_staked_fraction = scfg.Value(0.0777, help=ub.paragraph(
        '''
        Percent of the ETH supply that is staked
        '''))


class Assumptions(ConversionRates):
    """
    Main configuration class representing assumptions about cost to claim,
    initial amount staked, reward rates, etc...
    """

    num_8eth_minipools = scfg.Value(0.0, help='number of 8 eth minipools')

    num_16eth_minipools = scfg.Value(1.0, help='number of 16 eth minipools')

    cost_per_claim = scfg.Value(
        "0.015 ETH", help=ub.paragraph(
            '''
            The expected cost of claiming and restaking rewards, which depends
            on the current gas rate
            '''))

    rpl_staked = scfg.Value(
        "300.00 RPL", help='Initial amount of RPL collateral staked')

    node_eth_reward = scfg.Value(
        None,
        # "0.024 ETH",
        help=ub.paragraph(
            '''
            Expected ETH reward earned by all minipools in the node for an
            interval. Specifying this ignores num minipools.
            '''))

    reward_per_validator = scfg.Value(
        '0.04 ETH', help=ub.paragraph(
            '''
            The average reward per full validator per interval.
            This can be variable. Used if you specify number of minipools.
            Only used if node_eth_reward is unspecified.
            '''))

    rpl_reward_rate = scfg.Value(
        0.00653, help=ub.paragraph(
            '''
            percent of current staked RPL rewarded each month
            # FIXME: is this correct? How do we determine this?
            '''))

    rpl_restake_rate = scfg.Value(1.0, help=ub.paragraph(
        '''
        fraction of RPL to restake
        # TODO: handle non-1.0 values
        '''))

    def __post_init__(assumptions):
        super().__post_init__()
        assumptions.cost_per_claim = coerce_unit(assumptions.cost_per_claim, 'ETH', assumptions._ureg)
        assumptions.rpl_staked = coerce_unit(assumptions.rpl_staked, 'RPL', assumptions._ureg)
        assumptions.node_eth_reward = coerce_unit(assumptions.node_eth_reward, 'ETH', assumptions._ureg)
        assumptions.reward_per_validator = coerce_unit(assumptions.reward_per_validator, 'ETH', assumptions._ureg)
        if assumptions.reward_per_validator is None:
            assert assumptions.node_eth_reward, 'mutex'
        if assumptions.node_eth_reward is None:
            assert assumptions.reward_per_validator, 'mutex'
        assert assumptions.rpl_restake_rate == 1, 'only full restake implemented'
        assumptions._compute_unspecified()

    def _compute_unspecified(assumptions):
        """
        Ignore:
            >>> from claim_cycle_analysis import *  # NOQA
            >>> assumptions = Assumptions(
            >>>     num_8eth_minipools=0,
            >>>     num_16eth_minipools=1,
            >>>     reward_per_validator=None,
            >>>     node_eth_reward='0.024 ETH'
            >>> )
            >>> print(f'assumptions.reward_per_validator={assumptions.reward_per_validator}')
            >>> assumptions = Assumptions(
            >>>     num_8eth_minipools=0,
            >>>     num_16eth_minipools=1,
            >>>     reward_per_validator='0.04 ETH',
            >>> )
            >>> print(f'assumptions.node_eth_reward={assumptions.node_eth_reward}')
            >>> assumptions = Assumptions(
            >>>     num_8eth_minipools=2,
            >>>     num_16eth_minipools=0,
            >>>     reward_per_validator='0.04 ETH',
            >>> )
            >>> print(f'assumptions.node_eth_reward={assumptions.node_eth_reward}')
        """
        min_collateral_frac = 0.1  # 10 %
        max_collateral_frac = 1.5  # 150 %
        eth_per_validator = 32  # constant

        commision_types = {
            8: 0.14,  # 14% for 8-ETH minipools
            16: 0.20,  # 20% for 16-ETH minipools
        }
        num_pool_types = {
            8: assumptions.num_8eth_minipools,
            16: assumptions.num_16eth_minipools,
        }

        ureg = assumptions._ureg

        total_staked_eth = 0
        total_borrowed_eth = 0

        for pool_size, num in num_pool_types.items():
            pool_borrow = eth_per_validator - pool_size
            total_staked_eth += num * pool_size * ureg.ETH
            total_borrowed_eth += num * pool_borrow * ureg.ETH

        rpl_stake_min = (total_borrowed_eth * min_collateral_frac).to('RPL')
        rpl_stake_max = (total_staked_eth * max_collateral_frac).to('RPL')

        assumptions._rpl_stake_max = rpl_stake_max

        if assumptions.rpl_staked < rpl_stake_min:
            raise AssertionError(f'under min amount {assumptions.rpl_staked} < {rpl_stake_min}')

        if assumptions.reward_per_validator is None:
            # See _symbolic_reward_rates for derivation
            assumptions.reward_per_validator = (
                eth_per_validator * assumptions.node_eth_reward / (
                    # 16 part
                    commision_types[16] * eth_per_validator * num_pool_types[16] -
                    16 * commision_types[16] * num_pool_types[16] +
                    16 * num_pool_types[16] +
                    # 8 part
                    commision_types[8] * eth_per_validator * num_pool_types[8] -
                    8 * commision_types[8] * num_pool_types[8] +
                    8 * num_pool_types[8])
            )

        if assumptions.node_eth_reward is None:
            # See _symbolic_reward_rates for derivation
            assumptions.node_eth_reward = (
                # 16 part
                commision_types[16] * num_pool_types[16] * assumptions.reward_per_validator * (1 - 16 / eth_per_validator) +
                16 * num_pool_types[16] * assumptions.reward_per_validator / eth_per_validator +
                # 8 part
                commision_types[8] * num_pool_types[8] * assumptions.reward_per_validator * (1 - 8 / eth_per_validator) +
                8 * num_pool_types[8] * assumptions.reward_per_validator / eth_per_validator
            )

    def expected_rewards(assumptions, total_intervals, intervals_per_claim):
        """
        Simulate a claim strategy and return the result

        Example:
            >>> from claim_cycle_analysis import *  # NOQA
            >>> assumptions = Assumptions()
            >>> total_intervals = 4
            >>> intervals_per_claim = 2
            >>> state1 = assumptions.expected_rewards(120, 1)
            >>> state2 = assumptions.expected_rewards(120, 6)
            >>> rich.print('state1 = {}'.format(ub.urepr(state1, nl=1, align=':', precision=2)))
            >>> rich.print('state2 = {}'.format(ub.urepr(state2, nl=1, align=':', precision=2)))
        """
        from dataclasses import dataclass

        @dataclass
        class Agent:
            """
            Helper to keep track of state in the simulation
            """
            total_rpl_stake = assumptions.rpl_staked
            total_claimed_rpl_reward = 0
            total_claimed_eth_reward = 0
            total_unclaimed_rpl = 0
            total_unclaimed_eth = 0
            total_claim_cost = 0
            total_rpl_income = 0
            total_eth_income = 0
            net_gain = 0
            num_claims = 0

            def execute_claim(agent):
                agent.total_claimed_rpl_reward += agent.total_unclaimed_rpl
                agent.total_claimed_eth_reward += agent.total_unclaimed_eth

                # Add some amount of the RPL back to your stake.
                rpl_gain = agent.total_unclaimed_rpl
                eth_gain = agent.total_unclaimed_eth
                agent.total_unclaimed_eth = 0
                agent.total_unclaimed_rpl = 0

                CAN_CONVERT_ETH_TO_RPL = 0

                if CAN_CONVERT_ETH_TO_RPL:
                    # FIXME: this should actually be lossy
                    rpl_gain += eth_gain.to('RPL')
                    eth_gain = 0

                rpl_restake = (rpl_gain * assumptions.rpl_restake_rate)
                agent.total_rpl_stake += rpl_restake

                agent.net_gain += (
                    rpl_gain + eth_gain - assumptions.cost_per_claim
                ).to('ETH')
                agent.total_rpl_income += rpl_gain
                agent.total_eth_income += eth_gain
                agent.total_claim_cost += assumptions.cost_per_claim
                agent.num_claims += 1

        agent = Agent()
        initial_rpl = assumptions.rpl_staked
        inital_eth = (
            assumptions.num_8eth_minipools * 8 * assumptions._ureg.ETH +
            assumptions.num_16eth_minipools * 16 * assumptions._ureg.ETH
        )
        initial_value = (inital_eth + initial_rpl).to('ETH')

        for interval_idx in range(1, total_intervals + 1):
            # Calculate rewards for this interval
            rpl_reward = min(assumptions._rpl_stake_max, agent.total_rpl_stake) * assumptions.rpl_reward_rate
            eth_reward = assumptions.node_eth_reward

            agent.total_unclaimed_rpl += rpl_reward
            agent.total_unclaimed_eth += eth_reward

            if (interval_idx % intervals_per_claim) == 0:
                # Execute a claim after this interval
                agent.execute_claim()

            # print('agent.__dict__ = {}'.format(ub.urepr(agent.__dict__, nl=1, precision=2)))

        if agent.total_unclaimed_rpl > 0:
            # Final claim
            agent.execute_claim()

        report_unit = 'ETH'

        state = {
            'total_years': total_intervals / 12,
            'initial_stake': assumptions.rpl_staked.m,
            'num_claims': agent.num_claims,
            'intervals_per_claim': intervals_per_claim,
            'total_claim_cost': agent.total_claim_cost,
            'total_claimed_rpl_reward': agent.total_claimed_rpl_reward,
            'total_claimed_eth_reward': agent.total_claimed_eth_reward,
            # 'total_unclaimed_rpl': agent.total_unclaimed_rpl,
            # 'total_unclaimed_eth': agent.total_unclaimed_eth,
            'net_gain': agent.net_gain.to(report_unit),
            'net_value': (initial_value + agent.net_gain).to(report_unit),
            'initial_value': initial_value.to(report_unit),
        }
        return state


def main():
    """
    Simulate multiple strategies over a range of conditions and report results
    """
    REQUIRE_CLAIM_DIVIDES_TOTAL = 0

    # Loop over several assumptions to determine what the result of a claim
    # strategy is.
    # conversions = ConversionRates()
    # min_initial_rpl = (conversions._ureg.parse_expression('24 ETH') * 0.1).to('RPL').m
    # max_initial_rpl = (conversions._ureg.parse_expression('16 ETH') * 1.5).to('RPL').m
    main_config = Assumptions.cli(strict=True)

    # Hack to allow basis
    rpl_staked_basis = [main_config.rpl_staked] if not ub.iterable(main_config.rpl_staked) else main_config.rpl_staked
    total_intervals_basis = np.array([1, 3, 5, 10]) * 12

    states = []
    for rpl_staked in rpl_staked_basis:
        assumptions = Assumptions(rpl_staked=rpl_staked)
        for total_intervals in total_intervals_basis:
            for n in range(1, total_intervals):
                # For simplicity, only simulate a strategy if the number of
                # claims divides the number of intervals tested.
                if (total_intervals % n) == 0 or not REQUIRE_CLAIM_DIVIDES_TOTAL:
                    state = assumptions.expected_rewards(total_intervals, intervals_per_claim=n)
                    rich.print('state = {}'.format(ub.urepr(state, nl=1, align=':', precision=2)))
                    states.append(state)

    # Analyze claim strategy results
    df = pd.DataFrame(states)
    df = df.applymap(lambda x: x.m if hasattr(x, 'm') else x)

    # Determine the efficiency of a claim strategy
    groups = df.groupby(['initial_stake', 'total_years'])
    norm_groups = []
    maximized_rows = []
    for _, group in groups:
        group['normalized_net_gain'] = group['net_gain'] / group['net_gain'].max()
        norm_groups.append(group)
        maxrow = group.loc[group['net_gain'].idxmax()]
        maximized_rows.append(maxrow)
    norm_df = pd.concat(norm_groups)

    # Create a table of the most efficient strategies per assumption condition
    maximized_df = pd.DataFrame(maximized_rows)
    piv_result = maximized_df.pivot(
        index=['initial_stake'],
        columns=['total_years'],
        values=['intervals_per_claim'])

    # Print tables
    rich.print(norm_df.to_string(float_format='%0.2f'))
    rich.print(piv_result)

    plotkw = {}
    if len(rpl_staked_basis) > 1:
        plotkw['hue'] = 'initial_stake'
    if len(total_intervals_basis) > 1:
        plotkw['size'] = 'total_years'

    # Plot tables
    PLOT = 1
    if PLOT:
        import kwplot
        sns = kwplot.autosns()
        plt = kwplot.autoplt()

        fig = kwplot.figure(fnum=1)
        ax2 = fig.gca()
        annot = piv_result.applymap(str)
        sns.heatmap(
            piv_result,
            annot=annot,
            ax=ax2, fmt='s',
            annot_kws={'size': 10},
            cbar_kws={'label': 'optimal-intervals-per-claim', 'pad': 0.001}
        )
        fig.subplots_adjust(bottom=0.2)

        # plt.ion()
        fig = kwplot.figure(fnum=2)
        ax = fig.gca()
        sns.lineplot(
            data=norm_df,
            x='intervals_per_claim',
            y='normalized_net_gain',
            **plotkw,
            ax=ax)
        ax.set_title('Interval per Claim Efficiency')

        fig = kwplot.figure(fnum=3)
        ax = fig.gca()
        sns.lineplot(
            data=norm_df,
            x='intervals_per_claim',
            y='net_gain',
            **plotkw,
            ax=ax)
        ax.set_title('Interval per Claim Gain')

        fig = kwplot.figure(fnum=4)
        ax = fig.gca()
        sns.lineplot(
            data=norm_df,
            x='intervals_per_claim',
            y='net_value',
            **plotkw,
            ax=ax)
        ax.set_title('Interval per Claim Net Value')
        plt.show()


def _pint_repr_extensions():
    """
    Add pint formating to ubelt.urepr
    """
    REPR_EXTENSIONS = ub.util_repr._REPR_EXTENSIONS

    @REPR_EXTENSIONS.register(pint.Unit)
    def format_unit(data, **kwargs):
        numer = [k for k, v in data._units.items() if v > 0]
        denom = [k for k, v in data._units.items() if v < 0]
        numer_str = ' * '.join(numer)
        if len(denom) == 0:
            return '* ' + numer_str
        elif len(denom) > 1:
            denom_str = '({})'.format(' * '.join(denom))
        elif len(denom) == 1:
            denom_str = ' * '.join(denom)
        else:
            raise AssertionError
        if len(numer) == 0:
            return '/ ' + denom_str
        else:
            return '* ' + numer_str + ' / ' + denom_str

    @REPR_EXTENSIONS.register(pint.Quantity)
    def format_quantity(data, _return_info=None, **kwargs):
        return ub.repr2(data.magnitude, **kwargs) + ' ' + ub.repr2(data.u)


def coerce_unit(data, unit, ureg):
    """
    Helper to convert input into a proper unit
    """
    import numbers
    if data is None:
        value = None
    elif isinstance(data, str):
        value = ureg.parse_expression(data)
    elif isinstance(data, numbers.Number):
        value = ureg.parse_expression(f'{data} {unit}')
    elif isinstance(data, pint.Quantity):
        value = ureg.parse_expression(f'{data.m} {data.u}')
    else:
        raise TypeError(type(data))
    return value


def _symbolic_reward_rates():
    """
    Symbolic math developer notes
    """
    import sympy
    num_8pools = sympy.symbols('num_8pools')
    num_16pools = sympy.symbols('num_16pools')

    rewards_per_validator = sympy.symbols('rewards_per_validator')
    node_rewards = sympy.symbols('node_rewards')

    comission_8eth = sympy.symbols('comission_8eth')
    comission_16eth = sympy.symbols('comission_16eth')

    eth_per_validator = sympy.symbols('eth_per_validator')
    commision_types = {
        8: comission_8eth,  # 14% for 8-ETH minipools
        16: comission_16eth,  # 20% for 16-ETH minipools
    }
    num_pool_types = {
        8: num_8pools,
        16: num_16pools,
    }
    num_validators = 0

    equations = []
    total_nodeop_rewards = 0
    total_rewards = 0
    total_validators = 0
    for pool_size, num in num_pool_types.items():
        commision_rate = commision_types[pool_size]
        num_validators += num

        nodeop_frac = pool_size / eth_per_validator
        reth_frac = 1 - nodeop_frac
        reth_share0 = (reth_frac * rewards_per_validator * num)
        nodeop_share0 = (nodeop_frac * rewards_per_validator * num)
        commision = reth_share0 * commision_rate
        reth_share = reth_share0 - commision
        nodeop_share = nodeop_share0 + commision

        total_nodeop_rewards += nodeop_share
        total_validators += num
        total_rewards += (reth_share + nodeop_share)

    equations = []
    equations += [sympy.Eq((total_rewards / total_validators), rewards_per_validator)]
    equations += [sympy.Eq(total_nodeop_rewards, node_rewards)]

    print(sympy.solve(equations, rewards_per_validator))
    print(total_nodeop_rewards)
    # print(sympy.solve(equations, node_rewards))

    # Formula expressions
    # See _symbolic_reward_rates for derivation
    expr_rewards_per_validator = (
        eth_per_validator * node_rewards / (
            # 16 part
            comission_16eth * eth_per_validator * num_16pools -
            16 * comission_16eth * num_16pools +
            16 * num_16pools +
            # 8 part
            comission_8eth * eth_per_validator * num_8pools -
            8 * comission_8eth * num_8pools +
            8 * num_8pools)
    )

    expr_node_rewards = (
        # 16 part
        comission_16eth * num_16pools * rewards_per_validator * (1 - 16 / eth_per_validator) +
        16 * num_16pools * rewards_per_validator / eth_per_validator +
        # 8 part
        comission_8eth * num_8pools * rewards_per_validator * (1 - 8 / eth_per_validator) +
        8 * num_8pools * rewards_per_validator / eth_per_validator
    )

    common = ub.udict({
        num_16pools: 1,
        num_8pools: 1,
        eth_per_validator: 32,
        comission_8eth: 0.14,
        comission_16eth: 0.16,
    })
    import math
    for x in np.linspace(0.1, 1.0, 10):
        assume_rewards_per_validator = x
        node_rewards_calc = expr_node_rewards.subs(common | {
            rewards_per_validator: assume_rewards_per_validator,
        })
        rewards_per_validator_calc = expr_rewards_per_validator.subs(common | {
            node_rewards: node_rewards_calc,
        })
        assert math.isclose(rewards_per_validator_calc, assume_rewards_per_validator)

        assume_node_rewards = x
        rewards_per_validator_calc = expr_rewards_per_validator.subs(common | {
            node_rewards: assume_node_rewards,
        })
        node_rewards_calc = expr_node_rewards.subs(common | {
            rewards_per_validator: rewards_per_validator_calc,
        })
        assert math.isclose(assume_node_rewards, node_rewards_calc)


_pint_repr_extensions()


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/rpool/claim_cycle_analysis.py
    """
    main()
