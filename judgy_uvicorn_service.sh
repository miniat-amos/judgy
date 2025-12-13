#!/bin/bash
# Script - judgy_uvicorn_service.sh
# Author - Slava Borysyuk
# Date - 11/07/2025
# Description - Creates a rootless systemd --user service for Uvicorn

set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <port>"
    exit 1
fi

PORT="$1"

SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SYSTEMD_USER_DIR/judgyuvicorn.service"

echo "Creating Uvicorn systemd user service on port $PORT..."

# Create systemd user directory
mkdir -p "$SYSTEMD_USER_DIR"

# Write service file
tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Uvicorn ASGI server for Django Judgy project
After=network.target

[Service]
Type=simple
WorkingDirectory=$HOME/judgy/django_project
ExecStart=$HOME/judgy/env/bin/uvicorn progcomp.asgi:application \\
    --host 0.0.0.0 \\
    --port $PORT \\
    --workers 9 \\
    --log-level info \\
    --proxy-headers \\
    --lifespan off
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

# Reload and enable service
systemctl --user daemon-reload
systemctl --user enable --now judgyuvicorn.service

