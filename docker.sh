#!/bin/bash

# Build the Docker image
sudo docker build -t comfy .

# Check and remove existing containers
if sudo docker ps -a | grep -q comfyct; then
  sudo docker remove comfyct -f
fi

default_fs="--rm --gpus all"

sudo docker run $default_fs -p 127.0.0.1:8188:8188 --env-file .deploy-envs --name comfyct comfy &