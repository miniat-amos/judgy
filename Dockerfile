# This argument will be passed from the compose file
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

WORKDIR /usr/app

RUN mkdir outputs && touch ./outputs/output.txt



