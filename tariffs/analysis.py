#%%
import json
from fredapi import Fred
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "notebook"
#%%
with open("fred_api.json",'r') as fred_api:
    file_contents = fred_api.read()
    data = json.loads(file_contents)
    api_key = data['fred_api'] # requires api key
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
df.columns = ['cpi', 'unemployment_rate', 'consumer_confidence', 'gdp']
df.dropna(inplace=True)

# Calculate monthly inflation rate from CPI
fred_df = df.dropna().reset_index() # remove first row with NaN inflation
fred_df['month'] = fred_df['index'].dt.month
fred_df['year'] = fred_df['index'].dt.year
fred_df = fred_df[fred_df.month==12]
fred_df = fred_df.sort_values(['year'],ascending=True)
tariffs = pd.read_csv('data-2dFbJ.csv')
tariffs.columns =  [col.lower() for col in tariffs.columns]
joined = fred_df.merge(tariffs,on='year',how='inner').set_index('year')
main = joined.copy()
main = main.drop(columns=['tariff_rate_no_ieepa'])
# go.Figure(data=[go.Table(header=dict(values=main[['cpi', 'unemployment_rate', 'consumer_confidence', 'gdp']]),
#                  cells=dict(values=[main[f'{col}'] for col in [['cpi', 'unemployment_rate', 'consumer_confidence', 'gdp']]]))
#                      ])#%%

#%%
px.imshow(main.drop(columns=['index','month']).corr(),text_auto=True,aspect='auto')
# %%
independents = [col for col in main.columns if 'tariff' in col and 'diff' not in col and 'ieepa' not in col]
dependents = [col for col in main.columns if col in ['cpi', 'unemployment_rate', 'consumer_confidence','gdp']]
model_df = main.dropna()
model_df[dependents].describe()
for dep in dependents:
    for ind in independents:
        px.scatter(model_df,ind,dep,trendline='ols').show()
# %%
