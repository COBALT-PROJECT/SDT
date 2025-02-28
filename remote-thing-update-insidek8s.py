import json
import requests

# Define the SDT Service URL inside Kubernetes
# Use this if the script is running from inside Kubernetes
SDT_API_URL = "http://sdt-service.default.svc.cluster.local:8000/api/clouditor2dt/"

# If the script runs **outside Kubernetes**, use the NodePort service
# Uncomment and replace <NODE_IP> with your actual node IP
# SDT_API_URL = "http://<NODE_IP>:30008/api/clouditor2dt/"

# Define files to process
files = ['test_files/storageraw.json', 'test_files/vmraw.json']

# List to store API responses
dts = []

for f in files:
    try:
        # Read JSON data from the file
        with open(f, 'r', encoding='utf-8') as json_data:
            payload = json.load(json_data)

        # Perform PUT request
        response = requests.put(
            SDT_API_URL,
            json=payload,  # Use json parameter instead of data
            headers={'Content-Type': 'application/json'}
        )

        # Check if the request was successful
        if response.status_code in [200, 201, 204]:  # Success status codes
            response_data = response.json() if response.text else {}
            dts.append(response_data)
            print(f"✅ Successfully updated {f}")
        else:
            print(f"❌ Failed to update {f}: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"⚠️ Error processing {f}: {str(e)}")

# Save the responses to a JSON file
output_file = 'things-updated.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dts, f, ensure_ascii=False, indent=4)

# Print the result
print("\nUpdated Things:")
print(json.dumps(dts, indent=4))
