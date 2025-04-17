import pandas as pd
import requests
import time
import numpy as np

# Load your CSV data
df = pd.read_csv('/Users/ayushirajpoot/Documents/GitHub/CS-4675-Team-12/Data/AB_US_2023.csv')
df['zipcode'] = None

# Nominatim reverse geocode function
def get_zipcode_osm(lat, lon):
    url = f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json'
    headers = {'User-Agent': 'YourAppName/1.0 (your.email@example.com)'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if 'address' in data and 'postcode' in data['address']:
            return data['address']['postcode']
    return None

# Get 1000 evenly spaced row indices
sample_indices = np.linspace(0, len(df) - 1, 1000, dtype=int)

# Loop through only the sampled rows
for count, idx in enumerate(sample_indices):
    lat, lon = df.at[idx, 'latitude'], df.at[idx, 'longitude']
    try:
        zipcode = get_zipcode_osm(lat, lon)
        df.at[idx, 'zipcode'] = zipcode
        print(f"[{count+1}/1000] Row {idx} - Zipcode: {zipcode}")
        time.sleep(1.1)  # Respect Nominatim rate limits
    except Exception as e:
        print(f"Error on row {idx}: {e}")

# Save updated dataset
df.to_csv('dataset_with_zipcodes_osm.csv', index=False)

