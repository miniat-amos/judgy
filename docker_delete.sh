#!/bin/bash
# Author - Slava Borysyuk
# Date Created - 10/25/2024
# Creates Docker images based on the competition
# code passed in by Admin. It will create images
# with all of the problems associated with that
# competition code. All images will come preloaded
# with judging programs and test files.

#!/bin/bash

#!/bin/bash

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
