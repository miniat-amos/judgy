#!/bin/bash
# Script - judgy_gunicorn_service.sh
# Author - Slava Borysyuk
# Date - 10/11/2025
# Description - The purpose of this script is to
# set up gunicorn as a daemon service in order 
# to start the judgy django web app. 


judgygunicorn() {

sudo tee /etc/systemd/system/judgygunicorn.service > /dev/null <<'EOF'
[Unit]
Description=gunicorn daemon for Django judgy project
After=network.target

[Service]
User=admin
Group=admin
WorkingDirectory=/home/admin/judgy/django_project
ExecStart=/home/admin/judgy/env/bin/gunicorn --config gunicorn_config.py progcomp.wsgi:application

[Install]                                                                                                               
WantedBy=multi-user.target 
EOF


    sudo systemctl daemon-reload
    sudo systemctl enable --now /etc/systemd/system/judgygunicorn.service
}

judgygunicorn