import requests
import os
import json

# Define the API endpoint
url = "http://127.0.0.1:8001/api/SDT/create/"


def get_json_file_paths(base_dir):
    """
    Gets the paths of all JSON files in the given directory and its subdirectories.

    Args:
        base_dir (str): The base directory to search for JSON files.
    """
    json_file_paths = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, base_dir)
                json_file_paths.append(relative_path)
    return json_file_paths

if __name__ == "__main__":
    base_dir = 'test_files/CCM-Output-v2'
    json_file_paths = []
    if not os.path.exists(base_dir):
        print(f"Directory {base_dir} does not exist.")
    else:
        json_file_paths = get_json_file_paths(base_dir)
    if not json_file_paths:
        print("No JSON files found.")
    else:
        for path in json_file_paths:
            print(f"File: {path}")


# Function to extract the name from the file path
def extract_name(file_path):
    parts = file_path.split(os.sep)
    first = parts[0]  # Extract the first part of the path
    return first

# Iterate over each file path
# for file_path in json_file_paths:  # Limit to one iteration
#     file_path = file_path.strip()  # Remove any leading/trailing whitespace
if json_file_paths:  # Ensure the file path is not empty
    # Read the JSON file
    with open(json_file_paths, 'r') as file:
        json_payload = file.read()

    # Extract the name from the file path
    name = extract_name(json_file_paths)

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
    print(f"Response for {json_file_paths}: {response.json()}")