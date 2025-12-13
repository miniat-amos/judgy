#!/bin/bash
# Script - judgy_celery_service.sh
# Author - Slava Borysyuk
# Date - 10/11/2025
# Description - Creates a rootless systemd --user service for Celery

set -e

SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SYSTEMD_USER_DIR/judgycelery.service"

echo "Creating Celery systemd user service..."

# Create systemd user directory
mkdir -p "$SYSTEMD_USER_DIR"

# Write service file
tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Celery worker for Django Judgy project
After=network.target

[Service]
Type=simple
WorkingDirectory=$HOME/judgy/django_project
ExecStart=$HOME/judgy/env/bin/celery -A progcomp worker --loglevel=info --concurrency=8
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

# Reload and enable service
systemctl --user daemon-reload
systemctl --user enable --now judgycelery.service

