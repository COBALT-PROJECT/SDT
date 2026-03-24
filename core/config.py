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
Ditto_IP = os.getenv("DITTO_HOST", "localhost")
Ditto_PORT = os.getenv("DITTO_PORT", "8080")

# Local MQTT broker configuration
LOCAL_IP = get_local_ip()
# MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")# Use this for your MQTT connections
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")  # Fixed typo
# Clouditor configuration
Clouditor_IP = os.getenv("CLOUDITOR_HOST")
Clouditor_PORT = os.getenv("CLOUDITOR_PORT", "8080")

#IDS Connector configuration

# Other global configuration parameters can be added here
LOG_LEVEL = "INFO"
OUTPUT_DIR = "/home/abdul/DigitalTwin/Cobalt/SDT/sdt_output"


IDS_CONNECTOR_HOST = os.getenv("IDS_CONNECTOR_HOST", "localhost")
IDS_CONNECTOR_PORT = os.getenv("IDS_CONNECTOR_PORT", "8004")