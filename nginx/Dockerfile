FROM nginx:stable

RUN apt-get update && \
    rm -rf /var/lib/apt/lists/*

COPY ./entrypoint.sh /

RUN chmod +x /entrypoint.sh
