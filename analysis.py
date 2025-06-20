#%%
import json
from fredapi import Fred
import pandas as pd
from get_tariffs import AnnualTariffs
#%%

with open("fred_api.json",'r') as fred_api:
    file_contents = fred_api.read()
    data = json.loads(file_contents)
    api_key = data['fred_api']
fred = Fred(api_key=api_key)

# Retrieve monthly data
cpi = fred.get_series('CPIAUCSL')  # Consumer Price Index
unemp = fred.get_series('UNRATE')  # Unemployment rate
conf = fred.get_series('UMCSENT')  # Consumer confidence

# Retrieve and interpolate GDP (quarterly → monthly)
gdp_q = fred.get_series('GDPC1')  # Real GDP, chained 2012 dollars
gdp_m = gdp_q.resample('MS').interpolate('linear')  # monthly frequency

# Align to common date range
df = pd.concat([cpi, unemp, conf, gdp_m], axis=1)
df.columns = ['CPI', 'Unemployment_Rate', 'Consumer_Confidence', 'GDP']
df.dropna(inplace=True)

# Calculate monthly inflation rate from CPI
df['Inflation_Rate'] = df['CPI'].pct_change() * 100
df.dropna(inplace=True)  # remove first row with NaN inflation

# Reset index and format
fred_df = df.reset_index(inplace=True)
#%%
tariffs = AnnualTariffs(interpolate_monthly=True)
tarrif_df = tariffs.get_tarrif_data()
# %%
