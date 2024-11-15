#!/bin/bash

echo "Entrypoint script is running"


echo "Starting mysql container"

docker compose -f ./docker-compose.web.yml up --build db -d 

until mysqladmin ping -h "127.0.0.1" -P "${MYSQL_PORT}" -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" --silent; do
    echo "Waiting for MySQL..."
    sleep 2
done

python manage.py makemigrations judgy --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input

export DJANGO_SUPERUSER_EMAIL=$SUPER_USER_EMAIL
export DJANGO_SUPERUSER_PASSWORD=$SUPER_USER_PASSWORD
export DJANGO_SUPERUSER_FIRSTNAME=$SUPER_USER_FIRST_NAME
export DJANGO_SUPERUSER_LASTNAME=$SUPER_USER_LAST_NAME

python manage.py createsuperuser --noinput

chmod +x ./django-project/docker_setup.sh ./django-project/docker_delete.sh

gunicorn progcomp.wsgi:application --bind 0.0.0.0:8000

docker compose -f ./docker-compose.web.yml up --build nginx -d




