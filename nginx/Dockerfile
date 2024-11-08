FROM nginx:stable

RUN apt-get update && \
    apt-get install -y certbot python3-certbot-nginx && \
    rm -rf /var/lib/apt/lists/*

COPY ./entrypoint.sh /

RUN chmod +x /entrypoint.sh
