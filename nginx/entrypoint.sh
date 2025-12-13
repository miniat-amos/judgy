#!/bin/bash

envsubst '${SERVER_NAME} ${SERVER_PORT}' < /etc/nginx/templates/default.template.conf > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'