#!/bin/bash
# ==============================================
# Script Name  : docker_setup.sh
# Author       : Slava Borysyuk
# Date Created : 10/23/2024
# Description  : Builds Docker images for a specific competition using the provided 
#                competition code. The images include judging programs and other files 
#                for all problems associated with the competition.
# Usage        : ./docker_setup.sh COMP_CODE
# Arguments    : 
#                - COMP_CODE: The unique competition code used for identifying the problems.
# Dependencies : 
#                - Requires Docker and Docker Compose to be installed and functional.
# Environment  :
#                - Exports `COMP_CODE` as an environment variable for Docker Compose.
# Notes        :
#  - Ensure `docker-compose.languages.yml` is correctly configured for this process.
#  - COMP_CODE is passed as a build argument during the Docker image creation process.
# ==============================================


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
docker compose -f docker-compose.languages.yml build --build-arg COMP_CODE=$COMP_CODE
