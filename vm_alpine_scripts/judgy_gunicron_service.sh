#!/bin/bash
# Script - judgy_gunicorn_service.sh
# Author - Slava Borysyuk
# Date - 10/15/2025
# Description - The purpose of this script is to
# set up gunicorn as a daemon service in order 
# to start the judgy django web app. 


judgygunicorn() {

doas tee /etc/init.d/gunicorn > /dev/null <<'EOF'
#!/sbin/openrc-run
name="Judgy Gunicorn"
description="Gunicorn daemon for Django Judgy project"

pidfile="/run/gunicorn/gunicorn.pid"
command="/home/admin/judgy/env/bin/gunicorn"
directory="/home/admin/judgy/django_project"
user="admin"
group="admin"
gunicorn_config="/home/admin/judgy/django_project/gunicorn_config.py"
wsgi_module="progcomp.wsgi:application"

depend() {
    need net
}

start_pre() {
    checkpath --directory --owner ${user}:${group} /run/gunicorn
}

start() {
    ebegin "Starting ${name}"
    start-stop-daemon --start --quiet \
        --chdir "${directory}" \
        --user "${user}" --group "${group}" \
        --background --make-pidfile --pidfile "${pidfile}" \
        --exec "${command}" -- \
        --config "${gunicorn_config}" "${wsgi_module}" 
    eend $?
}

stop() {
    ebegin "Stopping ${name}"
    start-stop-daemon --stop --quiet --pidfile "${pidfile}"
    eend $?
}


EOF


  doas chmod +x /etc/init.d/gunicorn
  doas rc-update add gunicorn default
  doas rc-service gunicorn start

}

judgygunicorn