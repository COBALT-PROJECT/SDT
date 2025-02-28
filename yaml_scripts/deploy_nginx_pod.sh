#!/bin/bash

# Variables
POD_NAME="nginx-pull-test"
IMAGE="nginx:1.27-alpine"

# Step 1: Create a Pod YAML dynamically
cat <<EOF > ${POD_NAME}.yaml
apiVersion: v1
kind: Pod
metadata:
  name: ${POD_NAME}
spec:
  containers:
  - name: nginx-container
    image: ${IMAGE}
    imagePullPolicy: Always
    port:
    - containerPort:80
      hostPort:5000
EOF

echo "Created YAML file for ${POD_NAME}."

# Step 2: Apply the Pod YAML
echo "Applying Pod configuration..."
sudo kubectl apply -f ${POD_NAME}.yaml

# Step 3: Wait for the Pod to be created and check its status
echo "Waiting for the Pod to start..."
for i in {1..10}; do
    STATUS=$(sudo kubectl get pod ${POD_NAME} -o jsonpath='{.status.phase}' 2>/dev/null)
    if [[ "$STATUS" == "Running" ]]; then
        echo "Pod ${POD_NAME} is running."
        break
    elif [[ "$STATUS" == "Pending" ]]; then
        echo "Pod ${POD_NAME} is pending... retrying ($i/10)."
        sleep 5
    else
        echo "Pod ${POD_NAME} status: ${STATUS}"
        break
    fi
done

# Step 4: Cleanup (optional)
read -p "Do you want to delete the pod? [y/N] " DELETE_CONFIRM
if [[ "$DELETE_CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Deleting Pod and YAML file..."
    sudo kubectl delete pod ${POD_NAME}
    #rm -f ${POD_NAME}.yaml
    echo "Cleanup complete."
else
    echo "Pod and YAML file retained for inspection."
fi
