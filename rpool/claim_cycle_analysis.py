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
"""
import scriptconfig as scfg
import ubelt as ub
import pint
import rich
import pandas as pd


class ConversionRates(scfg.DataConfig):
    """
    Base class representing unit conversions
    """
    eth_to_dollar = 2000
    rpl_to_eth = 0.024404

    def __post_init__(conversions):
        conversions._ureg = pint.UnitRegistry()
        conversions._ureg.define('dollar = []')
        conversions._ureg.define(f'ETH = {conversions.eth_to_dollar} dollar')
        conversions._ureg.define(f'RPL = {conversions.rpl_to_eth} ETH')


def coerce_unit(data, unit, ureg):
    """
    Helper to convert input into a proper unit
    """
    import numbers
    if isinstance(data, str):
        value = ureg.parse_expression(data)
    elif isinstance(data, numbers.Number):
        value = ureg.parse_expression(f'{data} {unit}')
    elif isinstance(data, pint.Quantity):
        value = data
    else:
        raise TypeError(type(data))
    return value


class Assumptions(ConversionRates):
    """
    Main configuration class representing assumptions about cost to claim,
    initial amount staked, reward rates, etc...

    Current hard coded assumptions (fixme!):
        * 1 16ETH minipool
    """

    cost_per_claim = scfg.Value(
        "0.015 ETH", help='The expected cost of claiming and restaking rewards')

    rpl_staked = scfg.Value(
        "300.00 RPL", help='Initial amount of RPL collateral staked')

    smoothing_pool_reward = scfg.Value(
        "0.024 ETH", help="Expected rewards each month from the smoothing pool per minipool")

    rpl_reward_rate = scfg.Value(
        0.006, help="percent of current staked RPL rewarded each month")

    rpl_restake_rate = scfg.Value(1.0, help='fraction of RPL to restake')

    def __post_init__(assumptions):
        super().__post_init__()
        assumptions.cost_per_claim = coerce_unit(assumptions.cost_per_claim, 'ETH', assumptions._ureg)
        assumptions.rpl_staked = coerce_unit(assumptions.rpl_staked, 'RPL', assumptions._ureg)
        assumptions.smoothing_pool_reward = coerce_unit(assumptions.smoothing_pool_reward, 'ETH', assumptions._ureg)
        assert assumptions.rpl_restake_rate == 1, 'only full restake implemented'

    def expected_rewards(assumptions, total_intervals, intervals_per_claim):
        """
        Simulate a claim strategy and return the result
        """
        from dataclasses import dataclass

        # FIXME: handle 8ETH minipools
        rpl_stake_limit = (assumptions._ureg.parse_expression('16 ETH') * 1.5).to('RPL')

        @dataclass
        class Agent:
            total_rpl_stake = assumptions.rpl_staked
            total_claim_cost = 0
            total_claimed_rpl_reward = 0
            total_claimed_eth_reward = 0
            total_unclaimed_rpl = 0
            total_unclaimed_eth = 0
            num_claims = 0

            def execute_claim(agent):
                agent.total_claimed_rpl_reward += agent.total_unclaimed_rpl
                agent.total_claimed_eth_reward += agent.total_unclaimed_eth
                agent.total_claim_cost += assumptions.cost_per_claim

                # Add some amount of the RPL back to your stake.
                agent.total_rpl_stake += (agent.total_unclaimed_rpl * assumptions.rpl_restake_rate)

                agent.total_unclaimed_eth = 0
                agent.total_unclaimed_rpl = 0
                agent.num_claims += 1

        agent = Agent()

        for interval_idx in range(1, total_intervals + 1):
            # Calculate rewards for this interval
            rpl_reward = min(rpl_stake_limit, agent.total_rpl_stake) * assumptions.rpl_reward_rate
            eth_reward = assumptions.smoothing_pool_reward

            agent.total_unclaimed_rpl += rpl_reward
            agent.total_unclaimed_eth += eth_reward

            if (interval_idx % intervals_per_claim) == 0:
                # Execute a claim after this interval
                agent.execute_claim()

        if agent.total_unclaimed_rpl > 0:
            # Final claim
            agent.execute_claim()

        net_value = (
            agent.total_claimed_eth_reward +
            agent.total_rpl_stake - agent.total_claim_cost
        ).to('ETH').m

        state = {
            'total_years': total_intervals / 12,
            'initial_stake': assumptions.rpl_staked.m,
            'num_claims': agent.num_claims,
            'intervals_per_claim': intervals_per_claim,
            'total_claim_cost': agent.total_claim_cost,
            'total_claimed_rpl_reward': agent.total_claimed_rpl_reward,
            'total_claimed_eth_reward': agent.total_claimed_eth_reward,
            'total_unclaimed_rpl': agent.total_unclaimed_rpl,
            'total_unclaimed_eth': agent.total_unclaimed_eth,
            'net_value': net_value,
        }
        return state


def main():
    """
    Simulate multiple strategies over a range of conditions and report results
    """
    import numpy as np

    conversions = ConversionRates()
    min_initial_rpl = (conversions._ureg.parse_expression('16 ETH') * 0.1).to('RPL').m
    max_initial_rpl = (conversions._ureg.parse_expression('16 ETH') * 1.0).to('RPL').m

    # Loop over several assumptions to determine what the result of a claim
    # strategy is.
    states = []
    rpl_staked_basis = np.linspace(min_initial_rpl, max_initial_rpl, 10)
    total_intervals_basis = np.arange(1, 10) * 12   # 1-10 years
    for rpl_staked in rpl_staked_basis:
        assumptions = Assumptions(rpl_staked=rpl_staked)
        for total_intervals in total_intervals_basis:
            for n in range(1, total_intervals):
                # For simplicity, only simulate a strategy if the number of
                # claims divides the number of intervals tested.
                if (total_intervals % n) == 0:
                    state = assumptions.expected_rewards(total_intervals, intervals_per_claim=n)
                    rich.print('state = {}'.format(ub.urepr(state, nl=1, align=':')))
                    states.append(state)

    # Analyze claim strategy results
    df = pd.DataFrame(states)

    # Determine the efficiency of a claim strategy
    groups = df.groupby(['initial_stake', 'total_years'])
    norm_groups = []
    maximized_rows = []
    for _, group in groups:
        group['normalized_net_value'] = group['net_value'] / group['net_value'].max()
        norm_groups.append(group)
        maxrow = group.loc[group['net_value'].idxmax()]
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

    # Plot tables
    PLOT = 1
    if PLOT:
        import kwplot
        sns = kwplot.autosns()
        plt = kwplot.autoplt()

        plt.ion()
        fig = kwplot.figure(fnum=1)
        ax = fig.gca()

        sns.lineplot(data=norm_df, x='intervals_per_claim',
                     y='normalized_net_value', size='total_years',
                     hue='initial_stake', ax=ax)

        ax.set_title('Interval per Claim Efficiency')

        fig = kwplot.figure(fnum=2)
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


if __name__ == '__main__':
    """
    CommandLine:
        python ~/misc/rpool/claim_cycle_analysis.py
    """
    main()
