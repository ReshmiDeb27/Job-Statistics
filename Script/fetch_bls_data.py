import os
import requests
import pandas as pd
from datetime import datetime

# BLS API URL and API key
BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
API_KEY = "7cabf1af16684543bd085162d6b415f7"

# Series IDs to fetch
series_ids = [
    "CES0000000001",
    "CES0500000002", 
    "LNS14000000",
    "LNS13000000"
]

# File to store the dataset
OUTPUT_FILE = "C:/Users/Reshmi/OneDrive/Documents/GitHub/Job-Statistics/data/bls_cleaned_data.csv"


def load_existing_data(file_path):
    """Load existing data from a CSV file."""
    if os.path.exists(file_path):
        print(f"Loading existing data from {file_path}...")
        return pd.read_csv(file_path)
    else:
        print(f"No existing data found at {file_path}. Creating a new dataset.")
        return pd.DataFrame(columns=["seriesID", "date", "value"])


def fetch_series_data(series_id, start_year):
    """Fetch data for a single series from the BLS API."""
    print(f"Fetching data for series: {series_id}")
    payload = {
        "seriesid": [series_id],
        "startyear": start_year,
        "endyear": str(datetime.now().year),
        "registrationkey": API_KEY,
    }
    response = requests.post(BLS_API_URL, json=payload)
    if response.status_code == 200:
        data = response.json()
        if "Results" in data:
            return data["Results"]["series"][0]["data"]
        else:
            print(f"No data found for series: {series_id}")
            return []
    else:
        print(f"Error fetching data for series {series_id}: {response.status_code}")
        return []


def fetch_and_update_data(output_file):
    """Fetch new data, append to existing data, and save."""
    # Load existing data
    existing_data = load_existing_data(output_file)
    existing_data['date'] = pd.to_datetime(existing_data['date'], errors='coerce')

    # Determine the earliest year in the existing data
    if not existing_data.empty:
        start_year = existing_data['date'].dt.year.min()
    else:
        start_year = 2022  # Default start year if no data exists

    # Prepare to collect new data
    new_data = []

    for series_id in series_ids:
        series_data = fetch_series_data(series_id, str(start_year))
        for item in series_data:
            new_data.append({
                "seriesID": series_id,
                "date": f"{item['year']}-{item['period'][1:]}-01",  # Convert 'M01' to '01'
                "value": float(item['value'].replace(",", "")),
            })

    # Convert new data to DataFrame
    new_data_df = pd.DataFrame(new_data)
    new_data_df['date'] = pd.to_datetime(new_data_df['date'], errors='coerce')
    new_data_df.dropna(subset=['date'], inplace=True)

    # Concatenate with existing data
    updated_data = pd.concat([existing_data, new_data_df], ignore_index=True)
    updated_data.drop_duplicates(subset=["seriesID", "date"], inplace=True)  # Remove duplicates
    updated_data.sort_values(by=["seriesID", "date"], inplace=True)

    # Save updated data to CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    updated_data.to_csv(output_file, index=False)
    print(f"Data successfully updated and saved to {output_file}")


if __name__ == "__main__":
    fetch_and_update_data(OUTPUT_FILE)
