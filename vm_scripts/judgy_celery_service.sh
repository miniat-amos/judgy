#!/bin/bash
# Script - judgy_celery_service.sh
# Author - Slava Borysyuk
# Date - 10/11/2025
# Description - The purpose of this script is to
# set up celery as a daemon service in order 
# to run certain actions as background processes


judgycelery() {

sudo tee /etc/systemd/system/judgycelery.service > /dev/null <<'EOF'
[Unit]
Description=celery daemon for Django judgy project
After=network.target

[Service]
Type=simple
User=celery
Group=celery
WorkingDirectory=/home/admin/judgy/django_project
ExecStart=/home/admin/judgy/env/bin/celery -A progcomp worker --loglevel=info

[Install]                                                                                                               
WantedBy=multi-user.target 
EOF


    sudo systemctl daemon-reload
    sudo systemctl enable --now /etc/systemd/system/judgycelery.service
}

judgycelery