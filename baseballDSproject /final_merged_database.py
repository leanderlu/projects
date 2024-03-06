import pandas as pd
import json

# Read the CSV file
csv_file = 'baseballwOBA.csv'  # Replace with your CSV file path
csv_data = pd.read_csv(csv_file)

# Read the JSON file
json_file = 'final_merged_db.json'  # Replace with your JSON file path
with open(json_file, 'r') as file:
    json_data = json.load(file)

# Convert JSON data to a DataFrame
json_df = pd.DataFrame(json_data)

# Merge CSV data with JSON data
# Replace 'common_key' with the actual key you're using for merging
merged_df = pd.merge(json_df, csv_data, on='Name', how='left')

# Convert merged DataFrame back to JSON format
updated_json = merged_df.to_dict(orient='records')

# Save the updated JSON data to a file
output_file = 'final_merged_db.json'  # Replace with your desired output file path
with open(output_file, 'w') as file:
    json.dump(updated_json, file, indent=4)
