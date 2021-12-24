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
reg.define('us_person = []')

billion = 1_000_000_000
million = 1_000_000

CO2_ton = reg.CO2 * reg.metric_ton
CO2_pound = reg.CO2 * reg.pound
kwh = reg.Unit('kilowatt/hour')

cents = 0.01 * reg.dollar

us_emissions_2018 = 5.27 * billion * reg.metric_ton * reg.CO2 / reg.year
us_population_2018 = 327.2 * million * reg.us_person

us_person_anual_footprint = 16 * reg.metric_ton / (reg.year * reg.us_person)

# Different estimates for this number
us_person_anual_footprint_candidates = {
    'nature.org': 16 * CO2_ton / (reg.year * reg.us_person),
    'terrapass': (63_934 * CO2_pound).to(CO2_ton) / (reg.year * reg.us_person),
}
co2_offset_costs = {
    'terrapass': (100.75 * reg.dollars) / (20_191 * CO2_pound).to(CO2_ton),
    'cotap': (75 * reg.dollars) / (5 * CO2_ton),
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


# I started offsetting yearly when I was 30, so I have 30 years of backlog
backlog = 30 * reg.year * reg.us_person * us_person_anual_offset_cost
print('backlog = {!r}'.format(backlog))


coal_2019_energy = 947_891 * million * kwh
coal_2019_footprint = 952 * million * CO2_ton
coal_2019_co2_per_kwh = coal_2019_footprint / coal_2019_energy

# How much energy compaines charge per killowatt hour
paid_cost_per_kwh = (10.42 * cents) / kwh
print('paid_cost_per_kwh  = {!r}'.format(paid_cost_per_kwh))

# What is the carbon cost of each coal kwh?
extra_cost_per_kwh = dollar_per_co2ton * coal_2019_co2_per_kwh
print('extra_cost_per_kwh = {!r}'.format(extra_cost_per_kwh))
