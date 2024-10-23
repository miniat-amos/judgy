#!/bin/bash
# Author - Slava Borysyuk
# Date Created - 10/23/2024
# Creates Docker images based on the competition
# code passed in by Admin. It will create images
# with all of the problems associated with that
# competition code. All images will come preloaded
# with judging programs and test files.

# Check if they passed in competition code
if [ $# -ne 1 ]; then
    echo "Usage $0 COMP_CODE"
    exit 1
fi

# Assign variable from first argument
COMP_CODE=$1

# Export as env variable to allow docker compose to use it
export COMP_CODE

# Run docker compose build with the COMP_CODE argument
docker compose build --build-arg COMP_CODE=$COMP_CODE
