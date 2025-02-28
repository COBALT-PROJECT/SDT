#run this file from the SDT-main directory, this is a remote update of a thing in ditto from outside the k8s cluster

import json
import requests

# Define files to process
files = ['test_files/storageraw.json', 'test_files/vmraw.json']

NODE_IP = "127.0.0.1"  # Replace with your actual Kubernetes node IP
NODE_PORT = "30008"  # SDT Service NodePort as defined in the sdt-service.yaml file
#API endpoint URL
SDT_API_URL = f"http://{NODE_IP}:{NODE_PORT}/api/clouditor2dt/"

# List to store API responses
dts = []

for f in files:
    try:
        # Read JSON data from the file
        with open(f, 'r', encoding='utf-8') as json_data:
            payload = json.load(json_data)

        # Perform PUT request instead of POST
        response = requests.post(
            SDT_API_URL,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )

        # Check if the request was successful
        if response.status_code in [200, 201, 204]:  # Success status codes
            response_data = response.json() if response.text else {}
            dts.append(response_data)
        else:
            print(f"Failed to update {f}: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error processing {f}: {str(e)}")

# Save the responses to a JSON file
output_file = 'things-updated.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dts, f, ensure_ascii=False, indent=4)

# Print the result
print(json.dumps(dts, indent=4))
