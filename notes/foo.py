import scipy.stats
# According to [1] There is a ~1.45% chance of a drive failing each year
# .. [1] https://www.backblaze.com/blog/backblaze-hard-drive-stats-q2-2020/

# We can model a Poisson distribution to ask some questions
λ = 1.45 / 100   # probability of failure within a year
y = 1            # number of years
k = 1            # number of events (failures)


def probabilities_for_y_years(y):
    ##
    ##
    # The PMF is the probability that exactly k failures occur in y years
    print('\nIn y={} years we can expect'.format(y))

    rv = scipy.stats.poisson(mu=λ * y)

    k = 1
    p_one_fail = rv.pmf(k)
    print('p_one_fail = {:.4f}%'.format(p_one_fail * 100))
    k = 2
    p_two_fail = rv.pmf(k)
    print('p_two_fail = {:.4f}%'.format(p_two_fail * 100))

    # The CDF(k) is the probability the k or fewer failures occur in y years.
    # So, the probability k or more events occur is 1 - CDF(k - 1)
    # k or fewer, so 1 - CDF is the probability more than k events occur
    k = 1
    p_atleast_one_fail = 1 - rv.cdf(k - 1)
    print('p_atleast_one_fail = {:.4f}%'.format(p_atleast_one_fail * 100))

    k = 2
    p_atleast_two_fail = 1 - rv.cdf(k - 1)
    print('p_atleast_two_fail = {:.4f}%'.format(p_atleast_two_fail * 100))

probabilities_for_y_years(y=1)
probabilities_for_y_years(y=5)
probabilities_for_y_years(y=10)
probabilities_for_y_years(y=15)
