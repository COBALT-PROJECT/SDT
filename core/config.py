# Configuration variables for the SDT service
import socket
import os

# Get local IP address
def get_local_ip():
    try:
        # Create a socket connection to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't actually connect but gets local routing info
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"  # Fallback to localhost

# Eclipse Ditto configuration
Ditto_IP = os.getenv("DITTO_HOST", "ditto")
Ditto_PORT = "80"

# Local MQTT broker configuration
LOCAL_IP = get_local_ip()
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST")# Use this for your MQTT connections

# Clouditor configuration
Clouditor_IP = os.getenv("CLOUDITOR_HOST")
Clouditor_PORT = "8080"

# Other global configuration parameters can be added here
LOG_LEVEL = "INFO"
OUTPUT_DIR = "/home/abdul/DigitalTwin/Cobalt/SDT/sdt_output"
