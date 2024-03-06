import pandas as pd
import re
import json

# Load the player database CSV file
file_path = 'baseball.csv'
df = pd.read_csv(file_path)

# Load the OPS+ data
ops_file_path = 'baseballOPS.csv'
df_ops_plus = pd.read_csv(ops_file_path)

# Load the WAA and RAA data
waa_raa_file_path = 'baseballAA.csv'
df_waa_raa = pd.read_csv(waa_raa_file_path)

df_players = df[df['G'] >= 81].copy()
# Function to refine names for matching
def refine_name_for_matching(name):
    # Remove non-alphanumeric characters, convert to lowercase, and strip spaces
    refined_name = re.sub(r'[^a-zA-Z0-9]', '', name).lower().strip()
    return refined_name

# Apply the refined normalization function to DataFrames
df_players['Refined Name'] = df_players['Name'].apply(refine_name_for_matching)
df_ops_plus['Refined Name'] = df_ops_plus['Name'].apply(refine_name_for_matching)
df_waa_raa['Refined Name'] = df_waa_raa['Name'].apply(refine_name_for_matching)

# Fill NaN values in the Salary column with 720,000
df_players['Salary'] = df_players['Salary'].fillna(720000)

# Merge the OPS+ data with the player database
df_merged = pd.merge(df_players, df_ops_plus[['Refined Name', 'OPS+']], 
                     left_on='Refined Name', right_on='Refined Name', how='left')

# Merge the WAA and RAA data with the merged player database
df_final_merged = pd.merge(df_merged, df_waa_raa[['Refined Name', 'RAA']], 
                           left_on='Refined Name', right_on='Refined Name', how='left')

# Drop the 'Refined Name' column as it's no longer needed
df_final_merged.drop(columns=['Refined Name'], inplace=True)

# Display the first few rows of the final merged DataFrame
df_final_merged.head()


# Display the first few rows of the final merged DataFrame
merged_players_json = df_final_merged.to_dict(orient='records')

# Convert the list of dictionaries to a JSON string
json_data = json.dumps(merged_players_json, indent=4)

# Write the JSON data to a file
json_file_path = 'baseballDB.json'
with open(json_file_path, 'w') as file:
    file.write(json_data)
