#!/bin/bash
# ==============================================
# Script Name  : entrypoint.sh
# Author       : Slava Borysyuk
# Date Created : 11/15/2024
# Description  : Initializes the Judgy Programming Competition environment
#                by setting up a MySQL Docker container, migrating Django models,
#                starting the Django application, and configuring Nginx as a reverse proxy.
# Usage        : bash ./django-project/entrypoint.sh
# Dependencies : Requires Docker, Docker Compose, and Python 3.12.
# Environment  : Ensure a `.env` file is present with necessary environment variables:
#                - SUPER_USER_EMAIL
#                - SUPER_USER_PASSWORD
#                - SUPER_USER_FIRST_NAME
#                - SUPER_USER_LAST_NAME
#                - MYSQL_PORT
#                - MYSQL_USER
#                - MYSQL_PASSWORD
# Notes        :
#  - This script assumes Ubuntu or Debian-based systems.
#  - The Python virtual environment will be created in the current directory.
# ==============================================


echo "Entrypoint script is running"

create_virtualenv() {

    sudo apt update
    sudo apt install -y software-properties-common
    sudo add-apt-repository ppa:deadsnakes/ppa

    sudo apt update
    sudo apt install -y python3.12 python3.12-venv python3.12-dev

    echo "Creating virtual env"

    # Create the python virtual env (USING VERSION 3.12)
    python3.12 -m venv env

    # Activate the environment
    source ./env/bin/activate

    # Install requirements.txt
    pip install --upgrade pip
    pip install -r requirements.txt

}

python_commands() {
    echo "Running python commands"

    # Get all models from judgy app
    python manage.py makemigrations judgy --no-input
    # Migrate models to db
    python manage.py migrate --no-input
    # Get all static files
    python manage.py collectstatic --no-input

    DJANGO_SUPERUSER_EMAIL=$SUPER_USER_EMAIL
    DJANGO_SUPERUSER_PASSWORD=$SUPER_USER_PASSWORD
    DJANGO_SUPERUSER_FIRSTNAME=$SUPER_USER_FIRST_NAME
    DJANGO_SUPERUSER_LASTNAME=$SUPER_USER_LAST_NAME

    # Create the super user from .env
    python manage.py createsuperuser --noinput
}

# Run virtual env function
create_virtualenv

echo "Exporting .env variables"

export $(grep -v '^#' .env | xargs)

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

echo "Starting django web app in the background on port 8000"
# Run the django web app on port 8000
nohup gunicorn progcomp.wsgi:application --bind 0.0.0.0:8000 > nohup.out 2>&1 &

echo "Starting nginx"
# Create the nginx container to start web server
docker compose -f ../docker-compose.web.yml up --build nginx -d




