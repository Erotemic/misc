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
