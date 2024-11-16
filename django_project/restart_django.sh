restart_server() {
    echo "Restart Gunicorn server"
    pkill gunicorn || true  # Kill any existing Gunicorn processes
    mkdir ./logs
    nohup gunicorn progcomp.wsgi:application --bind 0.0.0.0:8000 --workers 17 > logs/server_$(date +%F_%T).log 2>&1 &
}

source ./env/bin/activate

cd ./django_project

restart_server