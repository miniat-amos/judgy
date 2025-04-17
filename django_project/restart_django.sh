#!/bin/bash


restart_server() {
    echo "Restart Gunicorn server"
    pkill gunicorn || true  # Kill any existing Gunicorn processes
    mkdir -p ./logs
    nohup gunicorn --timeout 300 progcomp.wsgi:application --bind 0.0.0.0:8000 --workers 17 > logs/server_$(date +%F_%T).log 2>&1 &
}

echo "Activating python virtual env"
source ./env/bin/activate

pip3 install -r requirements.txt

echo "Entering django project directory"
cd ./django_project

restart_server