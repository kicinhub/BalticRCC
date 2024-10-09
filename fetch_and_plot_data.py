import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates

# Set plotting parameters
mpl.rcParams['figure.dpi'] = 200
mpl.rcParams.update({'figure.autolayout': True})
plt.style.use('seaborn-darkgrid')

# API URL
url = 'https://api-baltic.transparency-dashboard.eu/api/v1/export'


def fetch_timeseries_data(params, value_columns):
    """Fetch timeseries data from the API and return a DataFrame."""
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        timeseries = data['data']['timeseries']
        df = pd.DataFrame(timeseries)
        df['_from'] = pd.to_datetime(df['_from'])
        # Expand the 'values' list into separate columns
        values = pd.DataFrame(df['values'].tolist())
        df = pd.concat([df['_from'], values], axis=1)
        columns_mapping = {i: name for i, name in enumerate(value_columns)}
        df.rename(columns=columns_mapping, inplace=True)
        return df
    else:
        print(f'Failed to fetch data, status code: {response.status_code}')
        return pd.DataFrame()

# Parameters for imbalance volumes
params_imbalance = {
    'id': 'imbalance_volumes',
    'start_date': '2024-09-23T00:00',
    'end_date': '2024-09-29T00:00',
    'output_time_zone': 'EET',
    'output_format': 'json',
    'json_header_groups': 1,
    'download': 0
}

# Fetch imbalance volumes data
df_imbalance = fetch_timeseries_data(params_imbalance, 
                                     ['Imbalance_Baltics'])
df_imbalance.rename(columns={'_from': 'Timestamp'}, inplace=True)

# Parameters for activations
params_activations = {
    'id': 'normal_activations_total',
    'start_date': '2024-09-23T00:00',
    'end_date': '2024-09-29T00:00',
    'output_time_zone': 'EET',
    'output_format': 'json',
    'json_header_groups': 1,
    'download': 0
}

# Fetch activations data
df_activations = fetch_timeseries_data(params_activations, 
                                       ['Upward_Baltics', 'Downward_Baltics'])
df_activations.rename(columns={'_from': 'Timestamp'}, inplace=True)


# Masks for non-zero activations
Upward_mask = df_activations['Upward_Baltics'] != 0
Downward_mask = df_activations['Downward_Baltics'] != 0

# Plotting
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(df_imbalance['Timestamp'], df_imbalance['Imbalance_Baltics'],
        c='black', label='Imbalance')

ax.plot(df_activations['Timestamp'], -df_activations['Upward_Baltics'],
        label='Upward Activation', c='blue', alpha=0.5)
ax.scatter(df_activations.loc[Upward_mask, 'Timestamp'], 
           -df_activations.loc[Upward_mask, 'Upward_Baltics'], 
           marker='^', s=10, c='blue', alpha=0.7)

ax.plot(df_activations['Timestamp'], df_activations['Downward_Baltics'], 
        label='Downward Activation', c='red', alpha=0.5)
ax.scatter(df_activations.loc[Downward_mask, 'Timestamp'], 
           df_activations.loc[Downward_mask, 'Downward_Baltics'], 
           marker='v', s=10, c='red', alpha=0.7)

# Format x-axis with dates
ax.xaxis.set_major_locator(mdates.DayLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)

ax.set_xlabel('Timestamp')
ax.set_ylabel('Energy (MWh)')
ax.set_title('Imbalance and Adjustments for Baltics')
ax.legend(fontsize='small')
plt.tight_layout()

plt.savefig('BalticRCC_task2.png')
plt.show()