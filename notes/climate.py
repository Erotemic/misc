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

reg = pint.UnitRegistry()

reg.define('CO2 = []')
reg.define('dollar = []')

billion = 1_000_000_000
million = 1_000_000

CO2_ton = reg.CO2 * reg.metric_ton
CO2_pound = reg.CO2 * reg.pound
kwh = reg.Unit('kilowatt/hour')

cents = 0.01 * reg.dollar

us_emissions_2018 = 5.27 * billion * reg.metric_ton * reg.CO2
us_population_2018 = 327.2 * million

us_person_anual_footprint = 16 * reg.metric_ton

# Different estimates for this number
us_person_anual_footprint_candidates = {
    'nature.org': 16 * CO2_ton,
    'terrapass': (63_934 * CO2_pound).to(CO2_ton),
}
us_person_anual_footprint = us_person_anual_footprint_candidates['terrapass']


offsets = {
    'terrapass': (100.75 * reg.dollars) / (20_191 * CO2_pound).to(CO2_ton),
    'cotap': (75 * reg.dollars) / (5 * CO2_ton),
}
dollar_per_co2ton = offsets['terrapass']


us_person_anual_offset_cost = us_person_anual_footprint * dollar_per_co2ton
print('us_person_anual_offset_cost = {!r}'.format(us_person_anual_offset_cost))

us_cost_to_offset_2018 = us_emissions_2018 * dollar_per_co2ton
print('us_cost_to_offset_2018 = {!r}'.format(us_cost_to_offset_2018))

us_cost_to_offset_2018_percapita = us_cost_to_offset_2018 / us_population_2018
print('us_cost_to_offset_2018_percapita = {!r}'.format(us_cost_to_offset_2018_percapita))


coal_2019_energy = 947_891 * million * kwh
coal_2019_footprint = 952 * million * CO2_ton
coal_2019_co2_per_kwh = coal_2019_footprint / coal_2019_energy

# How much energy compaines charge per killowatt hour
paid_cost_per_kwh = (10.42 * cents) / kwh
print('paid_cost_per_kwh  = {!r}'.format(paid_cost_per_kwh))

# What is the carbon cost of each coal kwh?
extra_cost_per_kwh = dollar_per_co2ton * coal_2019_co2_per_kwh
print('extra_cost_per_kwh = {!r}'.format(extra_cost_per_kwh))
