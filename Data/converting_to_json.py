#converting csv to json format
import pandas as pd

# Load the CSV file
df = pd.read_csv('/Users/ayushirajpoot/Documents/GitHub/CS-4675-Team-12/Data/only_rows_with_zipcodes.csv')  # change to your actual CSV filename

# Convert to JSON and save to file
df.to_json('dataset_zipcodes.json', orient='records', lines=True) 