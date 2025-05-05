import requests
import os
import json
import time
import sys

# Define the API endpoint
url = "http://127.0.0.1:8000/api/SDT/create/"
# Set a reasonable timeout for requests (in seconds)
REQUEST_TIMEOUT = 30


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
        for path in json_file_paths[:1]:
            print(f"Processing file: {path}")
            try:
                # Read the JSON file
                with open(os.path.join(base_dir, path), 'r') as file:
                    json_payload = file.read()

                # Extract the name from the file path
                name = path.split(os.sep)[0]
                filename = path.split(os.sep)[1]
                if not filename.startswith("output"):
                    # Prepare the data to be sent in the request
                    data = {
                        "name": name,
                        "payload": json.loads(json_payload)  # Parse to ensure valid JSON
                    }

                    print(f"Sending request for {name}...")
                    
                    # Make the API call with a timeout
                    start_time = time.time()
                    response = requests.post(url, json=data, timeout=REQUEST_TIMEOUT)
                    
                    print(f"Request completed in {time.time() - start_time:.2f} seconds")
                    print(f"Response status: {response.status_code}")
                    
                    # Print the response
                    try:
                        response_data = response.json()
                        print(f"Response for {path}: {response_data}")
                    except json.JSONDecodeError:
                        print(f"Response for {path} is not a valid JSON: {response.text[:500]}...")
                    
                    # Optional: Add a delay between requests to prevent overloading the server
                    time.sleep(1)
            except requests.Timeout:
                print(f"Request for {path} timed out after {REQUEST_TIMEOUT} seconds")
                continue
            except requests.RequestException as e:
                print(f"Request error for {path}: {str(e)}")
                continue
            except Exception as e:
                print(f"Error processing {path}: {str(e)}")
                continue
            
            print(f"Completed processing {path}\n" + "-"*50)