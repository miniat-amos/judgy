#!/bin/bash
# ==============================================
# Script Name  : docker_delete.sh
# Author       : Slava Borysyuk
# Date Created : 10/25/2024
# Description  : Deletes Docker images for a specific competition code.
#                Images are identified by the prefix `judgy-<COMP_CODE>-`.
# Usage        : ./docker_delete.sh COMP_CODE
# Arguments    : 
#                - COMP_CODE: The competition code used to identify images for deletion.
# Notes        : 
#  - Ensure Docker is installed and running before executing this script.
#  - This script forcibly removes images (`docker rmi -f`), so use with caution.
# ==============================================


if [ $# -ne 1 ]; then
    echo "Usage: $0 COMP_CODE"
    exit 1
fi

COMP_CODE=$1
echo "Deleting images with prefix: judgy-$COMP_CODE-"

# List all images with the prefix and delete them individually
for image_id in $(docker images --format "{{.Repository}}:{{.Tag}}" | grep "^judgy-${COMP_CODE}-"); do
    docker rmi -f "$image_id" || true
done
