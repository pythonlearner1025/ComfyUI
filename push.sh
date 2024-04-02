#!/bin/bash

sudo docker build -t deploy-comfy . 

sudo docker tag deploy-comfy invocation02/memetic-2024:build-comfy-v1

sudo docker push invocation02/memetic-2024:build-comfy-v1