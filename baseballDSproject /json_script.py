import json

# Load the JSON file
json_file_path = 'final_merged_db.json'  # Replace with your JSON file path
with open(json_file_path, 'r') as file:
    data = json.load(file)

# Remove the 'RAA' key from each JSON object
for obj in data:
    if 'xwOBA' in obj:
        del obj['xwOBA']

# Save the modified data back to a JSON file
output_file_path = 'final_merged_db.json'  # Replace with your desired output file path
with open(output_file_path, 'w') as file:
    json.dump(data, file, indent=4)

print("Key removed from all JSON objects and saved to:", output_file_path)
