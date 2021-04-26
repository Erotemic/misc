def hard_drive_failure_analysis():
    """
    References:
        https://www.backblaze.com/blog/backblaze-hard-drive-stats-q2-2020/

       https://f001.backblazeb2.com/file/Backblaze_Blog/Q2_2020_Drive_Stats_Chart_Data.zip
       https://f001.backblazeb2.com/file/Backblaze_Blog/Q2_2019_Drive_Stats_Chart_Data.zip

    """
    import ubelt as ub
    import random
    import time

    url_template = 'https://f001.backblazeb2.com/file/Backblaze_Blog/{}_{}_Drive_Stats_Chart_Data.zip'
    success_urls = []
    failed_urls = []
    got_fpaths = []
    for year in range(2017, 2021):
        for q in [1, 2, 3, 4]:
            try:
                url = url_template.format('Q' + str(q), year)
                print('url = {!r}'.format(url))
                # Play nice, don't crash their servers
                fpath = ub.grabdata(url)
                print('Got fpath = {!r}'.format(fpath))
                success_urls.append(url)
                got_fpaths.append(fpath)
                if 0:
                    # only need to do this the first time
                    time.sleep(1 + random.random())
            except Exception:
                print('Failed to grab url = {!r}'.format(url))
                failed_urls.append(url)
                pass

    got_fpaths = [
        '/home/joncrall/.cache/ubelt/Q3_2017_Drive_Stats_Chart_Data.zip',
        '/home/joncrall/.cache/ubelt/Q1_2018_Drive_Stats_Chart_Data.zip',
        '/home/joncrall/.cache/ubelt/Q2_2018_Drive_Stats_Chart_Data.zip',
        '/home/joncrall/.cache/ubelt/Q3_2018_Drive_Stats_Chart_Data.zip',
        '/home/joncrall/.cache/ubelt/Q1_2019_Drive_Stats_Chart_Data.zip',
        '/home/joncrall/.cache/ubelt/Q2_2019_Drive_Stats_Chart_Data.zip',
        '/home/joncrall/.cache/ubelt/Q2_2020_Drive_Stats_Chart_Data.zip'
    ]

    from torch_liberator.util.util_zip import zopen, split_archive
    split_archive(fpath)

    import zipfile

    import pandas as pd

    rates = []

    for fpath in got_fpaths:
        myzip = zipfile.ZipFile(fpath, 'r')
        name = ub.peek([name for name in myzip.namelist() if not name.startswith('_')])
        internal_fpath = fpath + '/' + name

        internal_file = zopen(internal_fpath, mode='rb')
        table = pd.read_excel(internal_file)

        found = None
        class BreakException(Exception):
            pass
        try:
            for rx, row in table.iterrows():
                for cx, col in enumerate(row):
                    if isinstance(col, str):
                        col = col.replace('\n', '').replace(' ', '').lower()
                        print('col = {!r}'.format(col))
                        if col in {'afr', 'annualizedfailurerate', 'failurerate'}:
                            found = (rx, cx)
                            raise BreakException

        except BreakException:
            pass

        if found is None:
            raise Exception

        rx, cx = found
        print('table = {!r}'.format(table))

        final_rate = table.iloc[-1].iloc[cx]
        rates.append(final_rate)

        drive_fails = table.iloc[-1].iloc[-2]
        drive_days = table.iloc[-1].iloc[-3]
        drive_count = table.iloc[-1].iloc[-4]
        print('final_rate = {!r}'.format(final_rate))

    # Lets say just overall every year your HDD has a 1.45% chance of failing

    annualize_fail_rate = 0.0145

    """

    rate = expected # events in 1 time period

    P(k events in t timesteps) = exp(- rate * t) * ((rate * time) ** k) / k!


    The probability we wait more than t for an event is

    P(T > t) = exp(-rate * t)

    The probability that the even will happen before time t is:

    P(T <= t) = 1 - exp(-rate * t)
    """

    import scipy.stats
    import numpy as np
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


    ##
    ##
    # The PMF is the probability that exactly k failures occur in y years
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




    # Probability k disks fail after y years
    k = 1
    p_one_fail = ((λ * y) ** k) * np.exp(-λ * y) / (scipy.special.factorial(k))
    print('p_one_fail = {:.4f}%'.format(p_one_fail * 100))

    k = 2
    p_two_fail = ((λ * y) ** k) * np.exp(-λ * y) / (scipy.special.factorial(k))
    print('p_two_fail = {:.4f}%'.format(p_two_fail * 100))
