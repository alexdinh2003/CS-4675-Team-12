import pandas as pd
import sys

# Clean newly downloaded data from insideairbnb.com.
def clean_csv(file_path):
    df = pd.read_csv(file_path, low_memory=False)
    
    df = df.apply(lambda col: col.str.replace('\n', '').str.strip() if col.dtype == 'object' else col)
    df.columns = df.columns.str.strip()

    new_file_path = file_path.replace('.csv', '_cleaned.csv')
    df.to_csv(new_file_path, index=False)
    
    print(f"Cleaned data saved to {new_file_path}")

#Create an object for a listing of a certain id.
def create_listing_object(path, listing_id):
    df = pd.read_csv(path, low_memory=False)
    listing_row = df[df.iloc[:, 0] == int(listing_id)]
    
    if listing_row.empty:
        print(f"No listing found with id {listing_id}")
        return None
    
    listing_dict = listing_row.to_dict(orient='records')[0]
    return(listing_dict)

# Turn dictionary of listing data into a string.
def stringify_listing_data(listing_dict):
    listing_str = ', '.join(f"{key}: {value.replace(',', '~')}" if isinstance(value, str) else f"{key}: {value}" for key, value in listing_dict.items())
    return listing_str

# Turn stringified listing data back into a dictionary.
def parse_listing_data(listing_str):
    listing_dict = dict(item.split(": ", 1) for item in listing_str.split(", "))
    listing_dict = {key: value.replace('~', ',') if isinstance(value, str) else value for key, value in listing_dict.items()}
    return listing_dict

#This is just for testing.
if __name__ == "__main__":
    file_path = sys.argv[1]
    if len(sys.argv) < 3:
        clean_csv(file_path)
    else:
        listing_id = sys.argv[2]
        create_listing_object(file_path, listing_id)