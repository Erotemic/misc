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
import seaborn as sbn
import ubelt as ub
import io
import pandas as pd
kwplot.autompl()

url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
file = io.BytesIO()
ub.download(url, fpath=file)
file.seek(0)
data = pd.read_csv(file)


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


ax = sbn.barplot(x='state', y='since_mortality', ci='since_mortality_std', data=stats_df)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

# stats_df = stats_df.sort_values('mortality_rate')
# print(stats_df)

# data = json.loads(text)
