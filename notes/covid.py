"""
Moderna Adverse Effects Rate:

https://www.cdc.gov/vaccines/covid-19/info-by-product/moderna/reactogenicity.html

The proportions of participants who reported at least one serious adverse event
were 1% in the vaccine group and 1% in the placebo group. The most common
serious adverse events occurring at higher rates in the vaccine group than the
placebo group were myocardial infarction (5 cases in vaccine group vs. 3 cases
in placebo group), cholecystitis (3 vs. 0), and nephrolithiasis (3 vs. 0).



One side effects:
    https://www.cdc.gov/coronavirus/2019-ncov/vaccines/different-vaccines/Pfizer-BioNTech.html
    https://www.cdc.gov/coronavirus/2019-ncov/vaccines/safety/myocarditis.html
    https://www.usnews.com/news/health-news/articles/2021-08-02/after-nearly-9-million-pfizer-shots-for-us-teens-serious-side-effects-rare-cdc


    https://www.cdc.gov/mmwr/volumes/70/wr/mm7031e1.htm?s_cid=mm7031e1_w
"""
import numpy as np
import pandas as pd
import ubelt as ub

Dose_1_Vaccine_N = 3761
Dose_1_Placebo_N = 3748
Dose_2_Vaccine_N = 3589
Dose_2_Placebo_N = 3549
myocardial       = 5 - 3
cholecystitis    = 3 - 0
nephrolithiasis  = 3 - 0

total_adverse = (myocardial + cholecystitis + nephrolithiasis)
adversity_rate = total_adverse / Dose_2_Vaccine_N

print('adversity_rate = {!r}'.format(adversity_rate))

moderna_hospital_rate_guess = pd.Series(ub.map_vals(lambda x: x / Dose_2_Vaccine_N, {
    '0-4': np.nan,
    '5-17': np.nan,
    '18-49': np.nan,
    '50-64': np.nan,
    '65+': np.nan,
}))

moderna_hospital_rate_guess.loc['total'] = total_adverse / Dose_2_Vaccine_N
df = moderna_hospital_rate_guess.to_frame('moderna_hospital_rate_guess')


"""
Hospitalization rate COVID:
    https://covid.cdc.gov/covid-data-tracker/#covidnet-hospitalization-network
"""

per = 100_000

covid_hospital_rate_per_1p5_years = pd.Series(ub.map_vals(lambda x: x / per, {
    '0-4': 87,
    '5-17': 51.8,
    '18-49': 440.9,
    '50-64': 1020.7,
    '65+': 1977.2,
}))
covid_hospital_rate_per_1p5_years.loc['total'] = covid_hospital_rate_per_1p5_years.sum()

df['covid_hospital_rate_per_1p5_years'] = covid_hospital_rate_per_1p5_years

np.array([70, 30, 10, 1]) / per


covid_adversity_rate = covid_hospital_rate_per_1p5_years.sum()
print('covid_adversity_rate = {!r}'.format(covid_adversity_rate))

df['risk'] = moderna_hospital_rate_guess / covid_hospital_rate_per_1p5_years
df['reward'] =  covid_hospital_rate_per_1p5_years / moderna_hospital_rate_guess


print(df)

print('risk = {!r}'.format(df.risk))


"""
COVID-19 Vaccine Safety in Adolescents Aged 12–17 Years
December 14, 2020–July 16, 2021

https://www.cdc.gov/mmwr/volumes/70/wr/mm7031e1.htm?s_cid=mm7031e1_w

As of July 16, 2021, approximately 8.9 million U.S. adolescents aged 12–17
years had received Pfizer-BioNTech vaccine.* VAERS received 9,246 reports after
Pfizer-BioNTech vaccination in this age group
"""

dose2_teens_N = 8.9e6
teen_death_N = 14
teen_hospital_N = 849 + teen_death_N

vaccine_teens_rate = teen_hospital_N / dose2_teens_N
print('vaccine_teens_rate = {:.8f}'.format(vaccine_teens_rate))

"""
Teen hospital rate
# https://covid.cdc.gov/covid-data-tracker/#covidnet-hospitalization-network
"""
covid_teens_rate = 75.6 / per
print('covid_teens_rate   = {:.5f}'.format(covid_teens_rate))


covid_teens_rate / vaccine_teens_rate

"""
Risk for COVID-19 Infection, Hospitalization, and Death By Age Group

https://www.cdc.gov/coronavirus/2019-ncov/covid-data/investigations-discovery/hospitalization-death-by-age.html

Total COVID deaths 4-17 years: 513-60

"""
