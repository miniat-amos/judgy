# This argument will be passed from the compose file
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG COMP_CODE

WORKDIR /usr/ap

COPY ./${COMP_CODE}/problems/*/*judging_program/ .
COPY ./${COMP_CODE}/problems/*/*test_files/ .

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    mkdir outputs && \
    touch ./outputs/output.txt && \
    touch ./outputs/score.txt && \
    rm -rf /var/lib/apt/lists/*