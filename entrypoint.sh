#!/bin/bash

echo "Entrypoint script is running"

python_commands() {
    echo "Running python commands"

    # Get all models from judgy app
    python3 manage.py makemigrations --no-input
    # Migrate models to db
    python3 manage.py migrate --no-input
    # Get all static files
    python3 manage.py collectstatic --no-input
}

echo "Exporting .env variables"

# Export the .env vars so script has them
export $(grep -v '^#' .env | xargs)

chmod +x ./judgy_celery_service.sh ./judgy_uvicorn_service.sh

echo "Setting up uvicorn service"
./judgy_uvicorn_service.sh ${SERVER_PORT}

echo "Setting up celery service"
./judgy_celery_service.sh

sudo loginctl enable-linger $USER

echo "Entering django project directory"

cd ./django_project

echo "Starting mysql container"

# Create the mySQL container
docker compose -f ../docker-compose.web.yml up --build db -d 

until mysqladmin ping -h "127.0.0.1" -P "${MYSQL_PORT}" -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" --silent; do
    echo "Waiting for MySQL before migrating..."
    sleep 2
done

# Run python commands function
python_commands

# Give permissions to docker scripts
chmod +x ./docker_setup.sh ./docker_delete.sh

echo "Starting nginx"
# Create the nginx container to start web server
docker compose -f ../docker-compose.web.yml up --build nginx -d




