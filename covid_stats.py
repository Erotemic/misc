import numpy as np


# curl --location --request GET 'https://api.covid19api.com/'


# curl --location --request GET 'https://api.covid19api.com/total/country/south-africa/status/confirmed'


# curl --location --request GET 'https://api.covid19api.com/total/country/united-states/status/confirmed'


# curl --location --request GET 'https://api.covid19api.com/countries' | jq


# curl --location --request GET 'https://api.covid19api.com/total/country/united-states/status/confirmed' | jq


# # import ubelt

# import io
# file = io.BytesIO()
# ub.download('https://covidtracking.com/api/v1/states/info.json', fpath=file)

import kwplot
import seaborn as sns
import ubelt as ub
import io
import pandas as pd
from dateutil import parser
import datetime
import pathlib
sns = kwplot.autosns()

repo_fpath = pathlib.Path('/data/joncrall/COVID-19/csse_covid_19_data')


data = pd.read_csv('/home/joncrall/Downloads/Provisional_COVID-19_Deaths_by_Sex_and_Age.csv')

# data[data['Province_State'] == 'Florida']


url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
file = io.BytesIO()
ub.download(url, fpath=file)
file.seek(0)
data = pd.read_csv(file)


sub = data[['Start Date', 'End Date', 'Age Group', 'COVID-19 Deaths', 'State', 'Sex']]
flags1 = (sub['State'] == 'Florida') | (sub['State'] == 'New York')
flags1 &= sub['Sex'] == 'All Sexes'
sub2 = sub[flags1]

flags3 = (
    (sub2['Age Group'] != 'All Ages') &
    (sub2['Age Group'] != 'Under 1 year') &
    (sub2['Age Group'] != '1-4 years') &
    (sub2['Age Group'] != '5-14 years') &
    (sub2['Age Group'] != '15-24 years') &
    (sub2['Age Group'] != '0-17 years') &

    (sub2['Age Group'] != '25-34 years') &
    (sub2['Age Group'] != '30-39 years') &
    (sub2['Age Group'] != '40-49 years') &

    (sub2['Age Group'] != '30-35 years') &
    (sub2['Age Group'] != '35-44 years') &
    (sub2['Age Group'] != '45-54 years') &
    (sub2['Age Group'] != '55-64 years') &
    (sub2['Age Group'] != '18-29 years')
)
sub3 = sub2[flags3]

start_datetimes = [parser.parse(d) for d in sub3['Start Date'].tolist()]
end_datetimes = [parser.parse(d) for d in sub3['End Date'].tolist()]
start_dates = np.array([d.date() for d in start_datetimes])
end_dates = np.array([d.date() for d in end_datetimes])

is_valids = []
for start, possible_ends in ub.group_items(end_dates, start_dates).items():
    idx = np.abs(start - np.array(possible_ends)).argmin()
    best_end = possible_ends[idx]
    is_valid = (start_dates == start) & (end_dates == best_end)
    is_valids.append(is_valid)

flags4 = np.logical_or.reduce(is_valids)

# flag = (end_dates - start_dates) <= datetime.timedelta(days=7)
# sub2 = sub1[flag]
sub4 = sub3[flags4]
sub4['start_dt'] = start_dates[flags4]

for k, g in sub4.groupby('Age Group'):
    for r, q in g.groupby('State'):
        pass
    pass



ax = sns.lineplot(data=sub4, x='start_dt', y='COVID-19 Deaths', hue='State', style='Age Group')
ax.set_yscale('symlog')


fl = sub2[sub2['State'] == 'Florida']
ny = sub2[sub2['State'] == 'New York']


sub['Start Date'] = pd.to_datetime().date
sub['End Date'] = [parser.parse(d) for d in sub['End Date'].tolist()]


# for k, d in fl.groupby('Age Group'):
#     pass

# fl.groupby
# fl['COVID-19 Deaths']


data['date'] = data['date'].astype('datetime64[ns]')

import datetime

# cutoff = datetime.datetime(2020, 6, 1)
cutoff = datetime.datetime(2020, 7, 15)

state_to_data = dict(list(data.groupby('state')))
state_to_data['New York']
state_to_data['New Jersey']

data['mortality'] = data['deaths'] / data['cases'] * 100

stats = []
for state, group in state_to_data.items():

    total = group.iloc[-1]
    baseline = group[group['date'] < cutoff].iloc[-1]
    since = group[group['date'] >= cutoff]

    group['day_cases'] = np.r_[[0], np.diff(group['cases'].values)]
    group['day_deaths'] = np.r_[[0], np.diff(group['deaths'].values)]
    group['day_mortality'] = group['day_deaths'] / (group['day_cases'] + 1e-9)

    row = {
        'state': state,
        'total_cases': total['cases'],
        'total_deaths': total['deaths'],
        'since_cases': total['cases'] - baseline['cases'],
        'since_deaths': total['deaths'] - baseline['deaths'],

        'mortality': total['mortality'],
        'mortality_std': group['mortality'].std(),
    }

    row['since_mortality'] = row['since_deaths'] / row['since_cases'] * 100
    row['since_mortality_std'] = since['mortality'].std()
    stats.append(row)


stats_df = pd.DataFrame(stats)

pd.options.display.max_rows = 1000

stats_df = stats_df.sort_values('total_cases', ascending=False)
print(stats_df)


ax = sns.barplot(x='state', y='since_mortality', ci='since_mortality_std', data=stats_df)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

# stats_df = stats_df.sort_values('mortality_rate')
# print(stats_df)

# data = json.loads(text)
