# https://engineeredlabs.com/collections/frontpage/products/heritage-periodic-table-collectors-edition-85-elements

# https://www.nrc.gov/about-nrc/radiation/around-us/doses-daily-lives.html
import pint
ureg = pint.UnitRegistry()

# https://openoregon.pressbooks.pub/radsafety130/chapter/inverse-square-law/
# Inverse Square law: The radiation Intensity is inversely proportional to the
# square of the distance.  Notice in the diagram that as the distance doubles,
# the area quadruples and thus, the initial radiation amount is spread over
# that entire area and is therefore reduced, proportionately.


# sun, food, radon, and the environment
ave_american_radiation = 0.034 * ureg.parse_units('mrem') / ureg.hour


Autunite_2mm = 0.01 * ureg.parse_units('mrem') / ureg.hour


# Threshold for special training
special_training = 100 * ureg.parse_units('mrem') / ureg.year
special_training.to('mrem/hour')

dose_limit = (5_000 * ureg.parse_units('mrem/year')).to('mrem/hour')


def radiation_measurement_analysis():
    """
    The folks at EngineeredLabs provided me with Geiger counter measurements
    of their products. This code uses them to analyze radiation falloff.

    In each entry:

        * vid is the id of the video the measurements are transcribed from.

        * "distance" is an estimated distance from the radiation source.

        * "rad" is the measured radiation

        * capture_time is the relative time delta of when the Geiger counter
          reading changed with resepct to the video start tiem.

    Requirements:
        pip install pint pandas statsmodels ubelt
    """
    import pint
    ureg = pint.UnitRegistry()

    mrem_h = ureg.parse_units('mrem') / ureg.hour
    m = ureg.parse_units('meters')
    s = ureg.parse_units('seconds')

    # Measurements of background radiation
    bg_dist = ureg.parse_expression('3 m')  # estimate of how far away we are wrt background
    background_rows = [
        dict(vid=1, distance=bg_dist, rad=0.023 * mrem_h, capture_time=0.0 * s),
        dict(vid=1, distance=bg_dist, rad=0.022 * mrem_h, capture_time=0.0 * s),
        dict(vid=1, distance=bg_dist, rad=0.023 * mrem_h, capture_time=4.0 * s),
        dict(vid=1, distance=bg_dist, rad=0.021 * mrem_h, capture_time=5.0 * s),
        dict(vid=1, distance=bg_dist, rad=0.023 * mrem_h, capture_time=11.0 * s),
        dict(vid=1, distance=bg_dist, rad=0.023 * mrem_h, capture_time=16.0 * s),
        dict(vid=1, distance=bg_dist, rad=0.024 * mrem_h, capture_time=20.0 * s),
    ]

    # Measurements of sample radiation
    esp_dist = ureg.parse_expression('1 inch').to(m) / 2  # estimate of how far we are from the sample when very close
    dist0_rows = [
        dict(vid=2, distance=esp_dist, rad=0.060 * mrem_h, capture_time=0.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.061 * mrem_h, capture_time=3.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.060 * mrem_h, capture_time=5.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.059 * mrem_h, capture_time=9.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.060 * mrem_h, capture_time=10.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.059 * mrem_h, capture_time=11.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.057 * mrem_h, capture_time=12.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.058 * mrem_h, capture_time=13.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.059 * mrem_h, capture_time=14.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.060 * mrem_h, capture_time=15.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.061 * mrem_h, capture_time=16.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.062 * mrem_h, capture_time=18.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.062 * mrem_h, capture_time=18.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.064 * mrem_h, capture_time=20.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.065 * mrem_h, capture_time=22.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.066 * mrem_h, capture_time=23.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.065 * mrem_h, capture_time=24.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.063 * mrem_h, capture_time=25.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.065 * mrem_h, capture_time=26.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.064 * mrem_h, capture_time=27.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.064 * mrem_h, capture_time=27.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.065 * mrem_h, capture_time=28.0 * s),
        dict(vid=2, distance=esp_dist, rad=0.063 * mrem_h, capture_time=30.0 * s),
    ]

    guess_dist = ureg.parse_expression('0.3 m')  # estimate of how far away we are wrt background
    guess_rows = [
        dict(vid=3, distance=guess_dist, rad=0.030 * mrem_h, capture_time=0.0 * s),
        dict(vid=3, distance=guess_dist, rad=0.041 * mrem_h, capture_time=2.0 * s),
        dict(vid=3, distance=guess_dist, rad=0.051 * mrem_h, capture_time=3.0 * s),
    ]

    rows = dist0_rows + background_rows
    rows += guess_rows

    import pandas as pd
    import numpy as np
    table = pd.DataFrame(rows)

    # Ensure comparable units
    units = {
        'rad': mrem_h,
        'distance': m,
        'capture_time': s,
    }
    for key, unit in units.items():
        table[key] = table[key].apply(lambda c: c.to(unit).m)
    table['rad'] = table['rad'].astype(float)
    table['distance'] = table['distance'].astype(float)

    # Weight each measurement based on the amount of time the measurement was
    # sustained in the video.
    average_rad_rows = []
    for vid, group in table.groupby('vid'):
        from statsmodels.stats.weightstats import DescrStatsW
        weights = (-1 * group['capture_time'].diff(periods=-1).fillna(0)) / group['capture_time'].iloc[-1]
        table.loc[group.index, 'weight'] = weights
        values = group['rad']
        weighted_stats = DescrStatsW(values, weights=weights, ddof=0)
        dists = group['distance'].unique()
        assert len(dists) == 1
        average_rad_rows.append({
            'vid': vid,
            'distance': dists[0],
            'rad_mean': weighted_stats.mean,
            'rad_std': weighted_stats.std,
        })
    stats_table = pd.DataFrame(average_rad_rows)

    # -------------------
    ADD_DUMMY_VALUES = 0
    if ADD_DUMMY_VALUES:
        # Hack: because we don't have enough samples we can fudge the value
        # knowning that the value should be the background radiation in the
        # limit.

        bg_row = stats_table.loc[stats_table['distance'].argmax()]
        fg_row = stats_table.loc[stats_table['distance'].argmin()]

        dummy_measurements = []
        extra_support = 1
        for idx in range(3, 3 + extra_support):
            dummy_row = {
                'vid': -idx,
                'distance': bg_row['distance'] + idx,
                'rad_mean': bg_row['rad_mean'],
                'rad_std': 0.01,
            }
            dummy_measurements.append(dummy_row)

        # also add an extra value close to the sample
        rad_bg = bg_row['rad_mean']
        rad_above_bg = fg_row['rad_mean'] - rad_bg
        dummy_row = {
            'vid': -1,
            'distance': fg_row['distance'] / 2,
            'rad_mean': rad_bg + (rad_above_bg * 4),
            'rad_std': 0.5,
        }
        dummy_measurements.append(dummy_row)

        # dummy_row = {
        #     'vid': -2,
        #     'distance': fg_row['distance'] / 4,
        #     'rad_mean': rad_bg + (rad_above_bg * 16),
        # }
        # dummy_measurements.append(dummy_row)

        dummy_stats = pd.DataFrame(dummy_measurements)
        dummy_stats['weight'] = 0.5
        stats_table['weight'] = 1.0
        stats_table2 = pd.concat([stats_table, dummy_stats]).reset_index(drop=True).sort_values('distance')
    else:
        stats_table2 = stats_table
    # -------------------

    import scipy
    scipy.optimize.curve_fit

    # Because we know the radiation should follow an inverse square law wrt to
    # distance, we can fit a polynomial of degree 2 (parabola) to interpolate /
    # extrapolate the **inverse** values.
    x = stats_table2['distance'].values
    y = stats_table2['rad_mean'].values
    s = stats_table2['rad_std'].values

    # Model the squared falloff directly
    def invsquare(x, a):
        return a * (1 / (0.01 + x ** 2)) + bg_row['rad_mean']
    # Use curve_fit to constrain the first coefficient to be zero
    coef = scipy.optimize.curve_fit(invsquare, x, y, sigma=s, method='trf')[0]

    # Also fit one to the raw weighted points as a sanity check
    # inv_poly2 = Polynomial.fit(table['distance'], 1 / table['rad'], w=table['weight'], deg=2)

    import kwplot
    sns = kwplot.autosns()
    plt = kwplot.autoplt()
    # ax = sns.boxplot(data=table, x='distance', y='rad', width=0.1)

    # Add in points to show each observation
    ax = sns.relplot(x="distance", y="rad", data=table, size=4, color=".3",
                     linewidth=0, alpha=0.5, palette='deep')

    ax = plt.gca()
    ax.set_xlabel('distance from sample ({})'.format(str(units['distance'])))
    ax.set_ylabel('radiation dosage ({})'.format(str(units['rad'])))

    max_meters = 10

    extrap_x = np.linspace(0, max_meters, 1000)
    extrap_y1 = invsquare(extrap_x, *coef)
    # extrap_y2 = 1 / inv_poly2(extrap_x)

    ax.plot(stats_table2['distance'].values, stats_table2['rad_mean'].values, 'rx')
    ax.plot(stats_table['distance'].values, stats_table['rad_mean'].values, 'bo')
    ax.plot(extrap_x, extrap_y1, '--')
    ax.set_ylim(0.001, 0.1)
    ax.set_yscale('log')
    # ax.plot(extrap_x, extrap_y2, '--')
