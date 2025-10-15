#!/bin/bash
# Script - judgy_gunicorn_service.sh
# Author - Slava Borysyuk
# Date - 10/15/2025
# Description - The purpose of this script is to
# set up gunicorn as a daemon service in order 
# to start the judgy django web app. 


judgygunicorn() {

sudo tee /etc/init.d/gunicorn > /dev/null <<'EOF'
#!/sbin/openrc-run
name="Judgy Gunicorn Service"
description="Gunicorn daemon for Django Judgy project"

command="/home/admin/judgy/env/bin/gunicorn"
command_args="--config /home/admin/judgy/django_project/gunicorn_config.py progcomp.wsgi:application"
command_user="admin:admin"
command_background="yes"
directory="/home/admin/judgy/django_project"
pidfile="/run/gunicorn.pid"

depend() {
    need net
}

EOF


  doas chmod +x /etc/init.d/gunicorn
  doas rc-update add gunicorn default
  doas rc-service gunicorn start

}

judgygunicorn