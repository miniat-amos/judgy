#!/bin/bash

echo "Starting Judgy Competition Platform..."

# Build and start Docker containers
echo "Building and starting Docker containers..."
docker-compose -f ../docker-compose.web.yml up --build -d

# Start the Django application
# Gunicorn server
start_server() {
    echo "Starting Gunicorn server"
    pkill gunicorn || true  # Kill any existing Gunicorn processes
    mkdir -p ./logs
    nohup gunicorn --timeout 300 progcomp.wsgi:application --bind 0.0.0.0:8000 --workers 17 > logs/server_$(date +%F_%T).log 2>&1 & # Starts Django server
}

# Wait for containers to be ready
echo "Waiting for containers to initialize..."
sleep 10

# Run migrations and collect static files
echo "Running migrations and collecting static files..."
cd ../django_project
docker exec judgy_web python manage.py makemigrations
docker exec judgy_web python manage.py migrate
docker exec judgy_web python manage.py collectstatic --noinput

# Create superuser (if not exists)
echo "Creating superuser if not exists..."
docker exec -it judgy_web python make_superuser.py

cd ../QuickStart

# Start Redis server (if not already running)
if ! pgrep redis-server > /dev/null; then
    echo "Starting Redis server..."
    redis-server &
    sleep 2
fi

# Start Celery worker
echo "Starting Celery worker..."
cd ../django_project
docker exec -d judgy_web celery -A progcomp worker -l info
cd ../QuickStart

echo "Judgy Platform is up and running!"
echo "Access the site at http://localhost:8000"
