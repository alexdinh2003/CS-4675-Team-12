import pandas as pd

# Load your full dataset
df = pd.read_csv('/Users/ayushirajpoot/Documents/GitHub/CS-4675-Team-12/Data/dataset_with_zipcodes_osm.csv')

# Filter rows where zipcode is not null / not empty
df_with_zip = df[df['zipcode'].notnull() & (df['zipcode'] != '')]

# Save to a new CSV
df_with_zip.to_csv('only_rows_with_zipcodes.csv', index=False)

print(f"Saved {len(df_with_zip)} rows with zipcodes.")
