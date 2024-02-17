#!/bin/bash

# Check if an image name is provided
if [ -z "$1" ]; then
    echo "Usage: ./start.sh transaction-fraud-api"
    exit 1
fi

IMAGE_NAME=$1

# Build the Docker image
docker build -t $IMAGE_NAME .

# Run the container, mounting the volume and exposing the port
docker run -p 5000:5000 
