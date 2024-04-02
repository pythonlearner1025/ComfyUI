#!/bin/bash

# Set the output log file path

exec python3 main.py --listen &

# Start the training script
exec python3 runpod_handler.py &

wait -n

exit $?