#!/bin/bash
# Script - judgy_uvicorn_service.sh
# Author - Slava Borysyuk
# Date - 11/07/2025
# Description - Creates a rootless systemd --user service for Uvicorn

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <username> <port>"
    exit 1
fi

USER_NAME="$1"
PORT="$2"

USER_HOME="/home/$USER_NAME"
SYSTEMD_USER_DIR="$USER_HOME/.config/systemd/user"
SERVICE_FILE="$SYSTEMD_USER_DIR/judgyuvicorn.service"


# Ensure user exists
if ! id "$USER_NAME" &>/dev/null; then
    echo "User '$USER_NAME' does not exist"
    exit 1
fi

echo "Creating Uvicorn systemd user service for $USER_NAME on port $PORT..."

# Create systemd user directory
sudo -u "$USER_NAME" mkdir -p "$SYSTEMD_USER_DIR"

# Write service file as the user
sudo -u "$USER_NAME" tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Uvicorn ASGI server for Django Judgy project
After=network.target

[Service]
Type=simple
WorkingDirectory=$USER_HOME/judgy/django_project
ExecStart=$USER_HOME/judgy/env/bin/uvicorn progcomp.asgi:application \\
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

# Allow service to run without interactive login
loginctl enable-linger "$USER_NAME"

# Reload and enable service
systemctl --user daemon-reload
systemctl --user enable --now judgyuvicorn.service

echo "Uvicorn service for $USER_NAME has been created and started."