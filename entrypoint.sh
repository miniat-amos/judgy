#!/bin/bash

echo "Entrypoint script is running"

until mysqladmin ping -h "judgy_mysql_prod" -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" --silent; do
    echo "Waiting for MySQL..."
    sleep 2
done


python manage.py makemigrations judgy --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input

export DJANGO_SUPERUSER_USERNAME=$SUPER_USER_NAME
export DJANGO_SUPERUSER_EMAIL=$SUPER_USER_EMAIL
export DJANGO_SUPERUSER_PASSWORD=$SUPER_USER_PASSWORD

python manage.py createsuperuser --noinput

chmod +x /app/docker_setup.sh /app/docker_delete.sh

gunicorn progcomp.wsgi:application --bind 0.0.0.0:8000
