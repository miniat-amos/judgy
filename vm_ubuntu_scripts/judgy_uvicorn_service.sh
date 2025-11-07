#!/bin/bash
# Script - judgy_gunicorn_service.sh,
# Author - Slava Borysyuk,
# Date - 11/07/2025,
# Description - The purpose of this script is to,
# set up uvicorn as a daemon service in order,
# to start the judgy django web app.,
judgyuvicorn() {

sudo tee /etc/systemd/system/judgyuvicorn.service > /dev/null <<'EOF'
[Unit]
Description=uvicorn daemon for Django judgy project
After=network.target

[Service]
User=webmaster
Group=webmaster
WorkingDirectory=/home/webmaster/judgy/django_project
ExecStart=/home/webmaster/judgy/env/bin/uvicorn progcomp.asgi:application \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 9 \
    --log-level info \
    --proxy-headers

[Install]
WantedBy=multi-user.target 
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable --now /etc/systemd/system/judgyuvicorn.service
}

judgyuvicorn