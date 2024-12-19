

import requests
import pandas as pd
import json
import os

API_KEY = "7cabf1af16684543bd085162d6b415f7"
BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
SERIES_IDS = [
    "CES0000000001",
    "CES0500000002",
    "LNS14000000",
    "LNS13000000"
]

def fetch_bls_data(series_ids, start_year, end_year):
    headers = {'Content-type': 'application/json'}
    data = json.dumps({
        "seriesid": series_ids,
        "startyear": start_year,
        "endyear": end_year,
        "registrationkey": API_KEY
    })
    response = requests.post(BASE_URL, headers=headers, data=data)
    return response.json()

def save_data(json_data, output_file="data/bls_data.csv"):
    # Ensure the directory exists
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_series = []
    for series in json_data['Results']['series']:
        series_id = series['seriesID']
        series_data = series['data']
        df = pd.DataFrame(series_data)
        df['seriesID'] = series_id
        all_series.append(df)

    final_df = pd.concat(all_series)
    final_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    data = fetch_bls_data(SERIES_IDS, start_year="2022", end_year="2024")
    save_data(data)

import pandas as pd

def process_data(input_file="C:/Users/Reshmi/OneDrive/Documents/GitHub/Job-Statistics/data/bls_data.csv", output_file="C:/Users/Reshmi/OneDrive/Documents/GitHub/Job-Statistics/data/bls_cleaned_data.csv"):
    df = pd.read_csv(input_file)
    df['date'] = pd.to_datetime(df['year'].astype(str) + df['periodName'], format='%Y%B')
    df = df[['date', 'seriesID', 'value']]
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    process_data()



