#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage $0 COMP_CODE"
    exit 1
fi

COMP_CODE=$1

export COMP_CODE

docker compose build --build-arg COMP_CODE=$COMP_CODE
