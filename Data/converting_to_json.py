#converting csv to json format
import pandas as pd

# Load the CSV file
df = pd.read_csv('AB_US_2023.csv')  # change to your actual CSV filename

# Convert to JSON and save to file
df.to_json('AB_US_2023.json', orient='records', lines=True) 