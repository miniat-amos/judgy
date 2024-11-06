#!/bin/sh

echo "Entrypoint script is running"


until mysqladmin ping -h "judgy_mysql_prod" -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" --silent; do
    echo "Waiting for MySQL..."
    sleep 2
done

python manage.py makemigrations judgy --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input

# DJANGO_SUPERUSER_PASSWORD=$SUPER_USER_PASSWORD python manage.py createsuperuser --username $SUPER_USER_NAME --email $SUPER_USER_EMAIL --noinput

gunicorn progcomp.wsgi:application --bind 0.0.0.0:8000