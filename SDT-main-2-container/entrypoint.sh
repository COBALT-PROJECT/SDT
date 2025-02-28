#!/bin/bash

#install all the pre-requisite packages by running setup.py? (i already install them when running dockerfile)
# Start the FastAPI app for api-adapter
echo "Starting api-adapter..."
uvicorn api-adapter:app --host=0.0.0.0 --port=8000 &
PID1=$!

# Wait for the API Adapter to be ready
echo "Waiting for api-adapter to be ready..."
#the while loop ensures the next process wont run until this one is completed. and same for the other processes as well.
while ! curl -s http://127.0.0.1:8000 > /dev/null; do
    sleep 1
done
echo "api-adapter is ready!"

# Start the api-controller
echo "Starting api-controller..."
python3 api-controller.py &
PID2=$!

# Wait for the API Controller to be ready
echo "Waiting for api-controller to be ready..."
while ! curl -s http://127.0.0.1:8005 > /dev/null; do
    sleep 1
done
echo "api-controller is ready!"

#run the command to create the toe with complete realistic network
echo "Creating the toe..."
python3 /app/tests/create_toe.py &
PID3=$!

# Wait for all processes
wait $PID1 $PID2 $PID3
