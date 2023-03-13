"""
some numbers on climate change

References:
    https://www.statista.com/statistics/276629/global-co2-emissions/
    https://ourworldindata.org/co2-emissions
    https://www.nature.org/en-us/get-involved/how-to-help/carbon-footprint-calculator/#:~:text=The%20average%20carbon%20footprint%20for,under%202%20tons%20by%202050.
    https://www.energybot.com/electricity-rates-by-state.html
    https://secondnature.org/climate-action-guidance/purchasing-carbon-offsets-faqs/#:~:text=How%20much%20do%20carbon%20offsets,project%2C%20and%20the%20vintage%20year.
    https://www.eia.gov/tools/faqs/faq.php?id=74&t=11#:~:text=In%202019%2C%20total%20U.S.%20electricity,of%20CO2%20emissions%20per%20kWh.
"""

import pint
import ubelt as ub
from dateutil import parser
import datetime
import json
import numpy as np
import pandas as pd


@ub.util_format._FORMATTER_EXTENSIONS.register(pint.Unit)
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


@ub.util_format._FORMATTER_EXTENSIONS.register(pint.Quantity)
def format_quantity(data, _return_info=None, **kwargs):
    return ub.repr2(data.magnitude, **kwargs) + ' ' + ub.repr2(data.u)

reg = pint.UnitRegistry()

reg.define('CO2 = []')
reg.define('dollar = []')

reg.define('dollar_2011 = []')
reg.define('us_person = []')
reg.define('year_2018 = []')

billion = 1_000_000_000
million = 1_000_000

CO2_ton = reg.CO2 * reg.metric_ton
CO2_pound = reg.CO2 * reg.pound
kwh = reg.Unit('kilowatt/hour')
twh = reg.Unit('terawatt/hour')

cents = 0.01 * reg.dollar

ONLINE_MODE = 0

if ONLINE_MODE:
    columns_of_interest = [
        'co2',
        'year',
        'total_ghg',
        'population',
        'gdp',
        'primary_energy_consumption',
        'consumption_co2',
    ]

    # header_info_fpath = ub.grabdata('https://github.com/owid/co2-data/raw/master/owid-co2-codebook.csv')
    from datetime import timedelta
    header_info_fpath = ub.grabdata('https://github.com/owid/co2-data/blob/master/owid-co2-codebook.csv', expires=timedelta(days=30))
    # header_info_fpath = ub.grabdata('https://nyc3.digitaloceanspaces.com/owid-public/data/co2/owid-co2-data.csv')
    header_info = pd.read_csv(header_info_fpath).set_index('column').drop('source', axis=1)
    column_descriptions = header_info.loc[columns_of_interest]

    key_to_description = {}
    for key, row in column_descriptions.iterrows():
        key_to_description[key] = ub.paragraph(row['description']).split('. ')
    print('key_to_description = {}'.format(ub.repr2(key_to_description, nl=2)))
    print(column_descriptions.to_string())

    # Download carbon emission dataset
    # https://github.com/owid/co2-data
    # https://github.com/owid/co2-data/blob/master/owid-co2-codebook.csv
    # Annual production-based emissions of carbon dioxide (CO2), measured in
    # million tonnes. This is based on territorial emissions, which do not
    # account for emissions embedded in traded goods.
    # owid_co2_data_fpath = ub.grabdata('https://github.com/owid/co2-data/raw/master/owid-co2-data.json')
    owid_co2_data_fpath = ub.grabdata('https://nyc3.digitaloceanspaces.com/owid-public/data/co2/owid-co2-data.json', expires=timedelta(days=30))
    with open(owid_co2_data_fpath, 'r') as file:
        co2_data = json.load(file)
    us_co2_data = co2_data['United States']['data']

    _raw_us_data = pd.DataFrame(us_co2_data).set_index('year', drop=0)
    us_data = _raw_us_data.loc[1980:][columns_of_interest]
    us_data = us_data.assign(year=_raw_us_data['year'].apply(lambda x: x * reg.year))
    us_data = us_data.assign(co2=_raw_us_data['co2'].apply(lambda x: x * million * CO2_ton))
    us_data = us_data.assign(population=_raw_us_data['population'].apply(lambda x: x * reg.us_person))
    us_data = us_data.assign(primary_energy_consumption=_raw_us_data['primary_energy_consumption'].apply(lambda x: x * twh / reg.year))
    us_data = us_data.assign(gdp=_raw_us_data['gdp'].apply(lambda x: x * reg.dollar_2011))

    if 0:
        import kwplot
        sns = kwplot.autosns()
        sns.lineplot(data=_raw_us_data, x='year', y='co2')

    us_emissions_2018 = us_data['co2'].loc[2018]
    us_population_2018 = us_data['population'].loc[2018]
    us_person_anual_footprint = us_emissions_2018 / us_population_2018
    us_data['co2_per_capita'] = us_data['co2'] / us_data['population']
else:
    us_emissions_2018 = 5.27 * billion * CO2_ton / reg.year_2018
    us_population_2018 = 327.2 * million * reg.us_person
    us_person_anual_footprint = us_emissions_2018 / us_population_2018

# Different estimates for this number
us_person_anual_footprint_candidates = {
    'nature.org': 16 * CO2_ton / (reg.year * reg.us_person),
    'terrapass': (63_934 * CO2_pound).to(CO2_ton) / (reg.year * reg.us_person),
}
co2_offset_costs = {
    'terrapass': (100.75 * reg.dollars) / (20_191 * CO2_pound).to(CO2_ton),
    # 'cotap': (75 * reg.dollars) / (5 * CO2_ton),
    'cotap': (15 * reg.dollars) / (1 * CO2_ton),
    'wren': (25) / (1 * CO2_ton),
}
print('us_person_anual_footprint_candidates = {}'.format(ub.repr2(us_person_anual_footprint_candidates, precision=2, nl=1, align=':', sort=0)))
print('co2_offset_costs = {}'.format(ub.repr2(co2_offset_costs, precision=2, nl=1, align=':', sort=0)))

us_person_anual_footprint = us_person_anual_footprint_candidates['nature.org']
dollar_per_co2ton = co2_offset_costs['cotap']


person_offset_costs = {}
person_offset_costs['us_person_anual_offset_cost'] = us_person_anual_offset_cost = us_person_anual_footprint * dollar_per_co2ton
person_offset_costs['us_cost_to_offset_2018'] = us_cost_to_offset_2018 = us_emissions_2018 * dollar_per_co2ton
person_offset_costs['us_cost_to_offset_2018_percapita'] = us_cost_to_offset_2018 / us_population_2018
print('person_offset_costs = {}'.format(ub.repr2(person_offset_costs, precision=2, nl=1, align=':', sort=0)))


coal_2019_energy = 947_891 * million * kwh
coal_2019_footprint = 952 * million * CO2_ton
coal_2019_co2_per_kwh = coal_2019_footprint / coal_2019_energy

# How much energy compaines charge per killowatt hour
paid_cost_per_kwh = (10.42 * cents) / kwh
print('paid_cost_per_kwh  = {!r}'.format(paid_cost_per_kwh))

# What is the carbon cost of each coal kwh?
extra_cost_per_kwh = dollar_per_co2ton * coal_2019_co2_per_kwh
print('extra_cost_per_kwh = {!r}'.format(extra_cost_per_kwh))


# Figure out where my balance is
# import dateutil
# dateutil.relativedelta

life_start = parser.parse('1989')
current_date = datetime.datetime.now().date()


if ONLINE_MODE:
    per_cap_extrap = us_data[['co2_per_capita', 'year']]
    num_missing_years = current_date.year - per_cap_extrap.year.max().m
    rolling_mean = us_data.co2_per_capita.apply(lambda x: x.m).rolling(5).mean()
    extrap_value = rolling_mean.iloc[-1] * us_data.co2_per_capita.iloc[-1].u

    extrap_rows = []
    for extrap_year in range(per_cap_extrap.year.max().m + 1, per_cap_extrap.year.max().m + num_missing_years + 1):
        row = {}
        row['year'] = extrap_year
        row['co2_per_capita'] = extrap_value
        extrap_rows.append(row)

    extrap_df = pd.DataFrame(extrap_rows).set_index('year', drop=0)
    extrap_df['is_extrap'] = True
    per_cap_extrap = pd.concat([per_cap_extrap, extrap_df])

    personal_timeline = per_cap_extrap.loc[life_start.year:]
    personal_carbon_used = personal_timeline['co2_per_capita'].sum()

    if 0:
        import kwplot
        sns = kwplot.autosns()
        magnitudes = personal_timeline.applymap(lambda x: x.m if hasattr(x, 'm') else x)
        ax = sns.lineplot(data=magnitudes, x='year', y='co2_per_capita')
        ax.set_title('Personal estimated emissions each year')
else:
    years_alive = (current_date.year - life_start.year) * reg.year
    personal_carbon_used = us_person_anual_footprint * years_alive * reg.us_person

    offline_rows = [
        {'co2_per_capita': us_person_anual_footprint * reg.year, 'year': year * reg.year, 'is_extrap': True}
        for year in range(life_start.year, current_date.year + 1)]
    personal_timeline = pd.DataFrame(offline_rows).set_index('year', drop=False)

personal_timeline = personal_timeline.sort_index()

rows = [
    {'date': '2023-03-13', 'amount':  250.00 * reg.dollars, 'organization': 'wren'},
    {'date': '2023-03-13', 'amount':  272.15 * reg.dollars, 'organization': 'wren'},
    {'date': '2022-11-23', 'amount':  300.00 * reg.dollars, 'organization': 'cotap'},
    {'date': '2022-07-05', 'amount':  300.00 * reg.dollars, 'organization': 'cotap'},
    {'date': '2022-07-05', 'amount':   40.00 * reg.dollars, 'organization': 'cotap', 'towards': 'flight&vacation'},
    {'date': '2021-12-27', 'amount': 2000.00 * reg.dollars, 'organization': 'cotap'},
    {'date': '2021-12-27', 'amount':  340.00 * reg.dollars, 'organization': 'cotap'},
    {'date': '2021-07-05', 'amount':   99.80 * reg.dollars, 'organization': 'terrapass'},
    {'date': '2020-01-11', 'amount':  179.64 * reg.dollars, 'organization': 'terrapass'},
]
for row in rows:
    tonnes_offset = row['amount'] / co2_offset_costs[row['organization']]
    row['offset'] = tonnes_offset
    if 'towards' not in row:
        row['towards'] = 'general'

# Skip any dontation that is directly offsetting a direct emission
all_offsets = pd.DataFrame(rows)
print(all_offsets)

general_offsets = all_offsets[all_offsets['towards'] == 'general']

personal_carbon_offset = general_offsets.offset.sum()
personal_carbon_footprint = personal_carbon_used - personal_carbon_offset

unaccounted_for = np.maximum(personal_timeline['co2_per_capita'][::-1].cumsum()[::-1] - (personal_carbon_offset / reg.us_person), 0)
unaccounted_for = np.minimum(unaccounted_for, personal_timeline['co2_per_capita'].apply(lambda x: x.m))

personal_timeline['unaccounted'] = unaccounted_for
print(personal_timeline)

print('personal_carbon_used      = {!r}'.format(ub.repr2(personal_carbon_used, precision=2)))
print('personal_carbon_offset    = {!r}'.format(ub.repr2(personal_carbon_offset, precision=2)))
print('personal_carbon_footprint = {!r}'.format(ub.repr2(personal_carbon_footprint, precision=2)))


backlog_cost = personal_carbon_footprint * dollar_per_co2ton
print('backlog_cost = {}'.format(ub.repr2(backlog_cost, nl=1, precision=2)))
