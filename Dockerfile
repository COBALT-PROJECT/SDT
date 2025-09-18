FROM python:3.9-slim
WORKDIR /app

# Install dependencies: curl, git, and MQTT broker
RUN apt-get update && apt-get install -y \
    curl \
    git \
    mosquitto \
    mosquitto-clients \
    && rm -rf /var/lib/apt/lists/*

# Configure Mosquitto to listen on all interfaces and allow anonymous connections
RUN mkdir -p /etc/mosquitto/conf.d
RUN echo "listener 1883 0.0.0.0" > /etc/mosquitto/conf.d/custom.conf \
    && echo "allow_anonymous true" >> /etc/mosquitto/conf.d/custom.conf

# Copy the application files - fix the copy destination
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p evidence sdt_output logs

# Create startup script to run both Mosquitto and the sdt_interface
RUN echo '#!/bin/bash\n\
# Start Mosquitto in background\n\
mosquitto -c /etc/mosquitto/mosquitto.conf -d\n\
echo "Started Mosquitto MQTT broker on port 1883"\n\
\n\
# Start the SDT interface\n\
cd /app/SDT\n\
exec uvicorn sdt_interface:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh

RUN chmod +x /app/start.sh


# Expose both the API and MQTT ports
EXPOSE 8000 1883

# Change the working directory to match where the app runs
WORKDIR /app/SDT

# Use the correct module path based on the working directory
ENV PYTHONPATH=/app
CMD ["/app/start.sh"]
