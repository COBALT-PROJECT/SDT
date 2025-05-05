from sseclient import SSEClient
import json

# Direct URL authentication
url = 'http://devops:foobar@127.0.0.1:8080/api/2/things'
print(f"Connecting to: {url}")

try:
    # Connect directly with credentials in URL
    messages = SSEClient(url)
    
    print("Connection established, waiting for events...")
    for msg in messages:
        print(f"Raw message: {msg.data}")
        if msg.data and isinstance(msg.data, str):
            try:
                data = json.loads(msg.data)
                print(f"Parsed data: {data}")
            except:
                print("Not valid JSON")
except Exception as e:
    print(f"Error: {e}")