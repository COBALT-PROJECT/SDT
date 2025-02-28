import requests
import os
import json
# Define the API endpoint
url = "http://127.0.0.1:8001/api/SDT/create/"

# Define the path to the file containing the JSON file paths
bom_json_paths_file = "/home/abdul/DigitalTwin/Cobalt/SDT/SDT/tests/bom_json_paths.txt"

# Read the file paths from bom_json_paths.txt
with open(bom_json_paths_file, 'r') as paths_file:
    file_paths = paths_file.readlines()

# Function to extract the name from the file path
def extract_name(file_path):
    parts = file_path.split(os.sep)
    for i, part in enumerate(parts):
        if part == "bom-examples-master":
            first= parts[i + 1]
        elif part == "bom.json":
            second = parts[i - 1]
            return f"{first}_{second}"
    return None

# Iterate over each file path
for file_path in file_paths[:1]:  # Limit to one iteration
    file_path = file_path.strip()  # Remove any leading/trailing whitespace
    if file_path:  # Ensure the file path is not empty
        # Read the JSON file
        with open(file_path, 'r') as file:
            json_payload = file.read()

        # Extract the name from the file path
        name = extract_name(file_path)

        # Prepare the data to be sent in the request
        data = {
            "name": name,
            "payload": json_payload
        }

        # # Convert the data to JSON
        # data = json.dumps(data)
        
        print(name)
        # Make the API call
        response = requests.post(url, json=data)

        # Print the response
        print(f"Response for {file_path}: {response.json()}")