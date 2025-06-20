import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class AnnualTariffs:
    def __init__(self,interpolate_monthly=None):
        self.interpolate_monthly = interpolate_monthly

        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        self.driver.get("https://dataweb.usitc.gov/tariff/annual")
        time.sleep(5)

    def map_data(self):
        """
        read data from usitc.gov, compile in dataframe
        -- interpolate or not based on self.interpolate_monthly
        """
        links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '.zip')]")
        zip_urls = [link.get_attribute("href") for link in links]
        self.driver.quit()
        for url in zip_urls:
            temp_df = pd.read_csv(url)
            yield temp_df

    def get_tarrif_data(self)->pd.DataFrame:
        df = pd.concat(self.map_data())
        annual = df.drop_duplicates().sort_values('Year')
        annual['Date'] = pd.to_datetime(annual['Year'].astype(str) + '-01-01')
        annual = annual.set_index('Date')[['Tariff_Rate']]
        if self.interpolate_monthly:
            monthly = annual.resample('MS').interpolate('linear').reset_index()
            monthly = monthly.rename(columns={'Date': 'Month'})
            return monthly
        else:
            return annual
    
    