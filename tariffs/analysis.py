#%%
import json
from fredapi import Fred
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
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
fred_df['inflation_rate'] = fred_df['cpi'].pct_change() * 100
fred_df['gdp_growth'] = fred_df['gdp'].pct_change()*100
fred_df['consumer_confidence_growth'] = fred_df['consumer_confidence'].pct_change()*100
fred_df['unemployment_rate_growth'] = fred_df['unemployment_rate'].pct_change()*100
fred_df['cpi_growth'] = fred_df['cpi'].pct_change()*100
fred_df['r3_gdp_growth'] = fred_df['gdp_growth'].rolling(3).mean()
fred_df['r5_gdp_growth'] = fred_df['gdp_growth'].rolling(5).mean()
fred_df['r10_gdp_growth'] = fred_df['gdp_growth'].rolling(10).mean()
tariffs = pd.read_csv('data-2dFbJ.csv')
tariffs.columns =  [col.lower() for col in tariffs.columns]
joined = fred_df.merge(tariffs,on='year',how='inner').set_index('year')
main = joined.copy()
main['tariff_diff'] = main['tariff_rate'].pct_change() * 100
main['r3_tariffs'] = main['tariff_rate'].rolling(3).mean()
main['r5_tariffs'] = main['tariff_rate'].rolling(5).mean()
main['r10_tariffs'] = main['tariff_rate'].rolling(10).mean()
#main = main.drop(columns=['index'])
# %%

go.Figure(data=[go.Table(header=dict(values=joined.columns),
                 cells=dict(values=[joined[f'{col}'] for col in joined.columns]))
                     ])
#%%
px.imshow(main.drop(columns=['index','month']).corr(),text_auto=True,aspect='auto')
# %%
independents = [col for col in main.columns if 'tariff' in col and 'diff' not in col and 'ieepa' not in col]
dependents = [col for col in main.columns if 'gdp' in col or col in ['cpi_growth', 'unemployment_rate_growth', 'consumer_confidence_growth'] and col!='gdp']
model_df = main.dropna()
for dep in dependents:
    for ind in independents:
        mod = sm.OLS(model_df[dep], model_df[ind],hasconst=False)
        res = mod.fit()
        print(res.summary()) 
# %%
